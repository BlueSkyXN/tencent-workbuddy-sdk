
from __future__ import annotations

from typing import Any

from workbuddy_enterprise.resources._base import Resource
from workbuddy_enterprise.response import ApiResponse


class EnterpriseResource(Resource):
    def get_info(self) -> ApiResponse[dict[str, Any]]:
        return self._as_map(self._get("/info"))

    def get_license(self) -> ApiResponse[dict[str, Any]]:
        return self._as_map(self._get("/license"))
