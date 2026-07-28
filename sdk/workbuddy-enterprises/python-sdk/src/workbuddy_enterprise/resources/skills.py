
from __future__ import annotations

from pathlib import Path
from typing import Any, BinaryIO, Mapping

from workbuddy_enterprise.pagination import page_query
from workbuddy_enterprise.resources._base import Resource
from workbuddy_enterprise.response import ApiResponse, Page
from workbuddy_enterprise.schemas.common import VisibilityScope, VisibilitySpec
from workbuddy_enterprise.schemas.skills import SkillDetail, SkillSummary
from workbuddy_enterprise.types import PublishStatus, SkillSource, VisibilityType
from workbuddy_enterprise._transport import open_package_file
from workbuddy_enterprise._serialization import clean_dict, dump_value


class SkillsResource(Resource):
    def list(
        self,
        *,
        source: SkillSource | str,
        keyword: str | None = None,
        category_id: int | str | None = None,
        publish_status: PublishStatus | str | None = None,
        page_num: int | None = None,
        page_size: int | None = None,
    ) -> ApiResponse[Page[SkillSummary]]:
        params = {
            "source": dump_value(source),
            "keyword": keyword,
            "categoryId": category_id,
            "publishStatus": dump_value(publish_status) if publish_status is not None else None,
            **page_query(page_num=page_num, page_size=page_size),
        }
        resp = self._get("/openapi/skills", params=params)
        page = self._as_page(resp).data
        typed = Page(
            items=[SkillSummary.from_mapping(i) for i in page.items],
            total_count=page.total_count,
            page=page.page,
            page_num=page.page_num,
            page_size=page.page_size,
            next_page_token=page.next_page_token,
            extra=page.extra,
        )
        return ApiResponse(typed, resp.code, resp.message, resp.request_id, resp.raw)

    def create(
        self,
        *,
        name: str,
        display_name: str,
        package: str | Path | BinaryIO | None = None,
        display_name_en: str | None = None,
        description_zh: str | None = None,
        description_en: str | None = None,
        icon: str | None = None,
        version: str | None = None,
        publish_status: PublishStatus | str | None = None,
        category_id: int | None = None,
        expected_md5: str | None = None,
        expected_sha256: str | None = None,
    ) -> ApiResponse[dict[str, Any]]:
        data = clean_dict(
            {
                "name": name,
                "displayName": display_name,
                "displayNameEn": display_name_en,
                "descriptionZh": description_zh,
                "descriptionEn": description_en,
                "icon": icon,
                "version": version,
                "publishStatus": dump_value(publish_status) if publish_status is not None else None,
                "categoryId": category_id,
                "expectedMd5": expected_md5,
                "expectedSha256": expected_sha256,
            }
        )
        files, closer = open_package_file(package)
        try:
            # httpx requires files or data; if no files, still multipart-compatible form
            if files is None:
                # send as multipart fields without file by using files={} empty? better use data only with multipart forced
                # Use files with a dummy? Spec says multipart. Use httpx files with (None, value) for fields.
                multipart_files = {k: (None, str(v)) for k, v in data.items()}
                resp = self._post_multipart("/openapi/skills", files=multipart_files)
            else:
                resp = self._post_multipart("/openapi/skills", data=data, files=files)
        finally:
            if closer is not None:
                closer.close()
        return self._as_map(resp)

    def get(self, skill_ref: str) -> ApiResponse[SkillDetail]:
        resp = self._get(f"/openapi/skills/{skill_ref}")
        detail = SkillDetail.from_mapping(resp.data or {})
        return ApiResponse(detail, resp.code, resp.message, resp.request_id, resp.raw)

    def update(
        self,
        skill_ref: str,
        *,
        package: str | Path | BinaryIO | None = None,
        name: str | None = None,
        display_name: str | None = None,
        display_name_en: str | None = None,
        description_zh: str | None = None,
        description_en: str | None = None,
        icon: str | None = None,
        version: str | None = None,
        publish_status: PublishStatus | str | None = None,
        status: str | None = None,
        disabled_reason: str | None = None,
        category_id: int | None = None,
        expected_md5: str | None = None,
        expected_sha256: str | None = None,
    ) -> ApiResponse[dict[str, Any]]:
        data = clean_dict(
            {
                "name": name,
                "displayName": display_name,
                "displayNameEn": display_name_en,
                "descriptionZh": description_zh,
                "descriptionEn": description_en,
                "icon": icon,
                "version": version,
                "publishStatus": dump_value(publish_status) if publish_status is not None else None,
                "status": status,
                "disabledReason": disabled_reason,
                "categoryId": category_id,
                "expectedMd5": expected_md5,
                "expectedSha256": expected_sha256,
            }
        )
        files, closer = open_package_file(package)
        try:
            if files is None:
                multipart_files = {k: (None, str(v)) for k, v in data.items()}
                if not multipart_files:
                    multipart_files = {"_": (None, "")}
                resp = self._post_multipart(f"/openapi/skills/{skill_ref}/update", files=multipart_files)
            else:
                resp = self._post_multipart(
                    f"/openapi/skills/{skill_ref}/update", data=data, files=files
                )
        finally:
            if closer is not None:
                closer.close()
        return self._as_map(resp)

    def delete(self, skill_ref: str) -> ApiResponse[dict[str, Any]]:
        resp = self._post_json(f"/openapi/skills/{skill_ref}/delete", body=None, send_json=False)
        return self._as_map(resp)

    def set_enabled(
        self,
        skill_ref: str,
        *,
        source: SkillSource | str,
        enabled: bool,
        disabled_reason: str | None = None,
    ) -> ApiResponse[None]:
        body: dict[str, Any] = {"enabled": enabled}
        if disabled_reason is not None:
            body["disabledReason"] = disabled_reason
        resp = self._post_json(
            f"/openapi/skills/{skill_ref}/toggle",
            params={"source": dump_value(source)},
            body=body,
        )
        return ApiResponse(None, resp.code, resp.message, resp.request_id, resp.raw)

    def set_visibility(
        self,
        skill_ref: str,
        *,
        source: SkillSource | str,
        type: VisibilityType | str,
        scopes: list[VisibilityScope | Mapping[str, Any]] | None = None,
    ) -> ApiResponse[None]:
        scope_objs: list[VisibilityScope] = []
        for s in scopes or []:
            if isinstance(s, VisibilityScope):
                scope_objs.append(s)
            else:
                scope_objs.append(VisibilityScope.from_mapping(s))
        spec = VisibilitySpec(type=dump_value(type), scopes=scope_objs)
        resp = self._post_json(
            f"/openapi/skills/{skill_ref}/visibility",
            params={"source": dump_value(source)},
            body=spec.to_wire(),
        )
        return ApiResponse(None, resp.code, resp.message, resp.request_id, resp.raw)

    def get_visibility(
        self,
        skill_ref: str,
        *,
        source: SkillSource | str,
    ) -> ApiResponse[VisibilitySpec]:
        resp = self._get(
            f"/openapi/skills/{skill_ref}/visibility",
            params={"source": dump_value(source)},
        )
        spec = VisibilitySpec.from_mapping(resp.data or {})
        return ApiResponse(spec, resp.code, resp.message, resp.request_id, resp.raw)
