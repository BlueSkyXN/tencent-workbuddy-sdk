use crate::client::{encode_path_segment, push_q, push_qi, Client};
use crate::error::Result;
use crate::response::ApiResponse;
use crate::types::{PublishStatus, SkillSource, VisibilityType};
use serde_json::{json, Value};
use std::collections::HashMap;
use std::path::Path;

pub struct ExpertsResource<'a> {
    pub(crate) client: &'a Client,
}

impl ExpertsResource<'_> {
    /// `category_id` is the decimal OpenAPI category ID serialized as a query value.
    pub fn list(
        &self,
        source: SkillSource,
        keyword: Option<&str>,
        category_id: Option<&str>,
        publish_status: Option<PublishStatus>,
        page_num: Option<i64>,
        page_size: Option<i64>,
    ) -> Result<ApiResponse<crate::response::Page<Value>>> {
        let mut q = Vec::new();
        push_q(&mut q, "source", Some(source.as_str().to_string()));
        push_q(&mut q, "keyword", keyword.map(|s| s.to_string()));
        push_q(&mut q, "categoryId", category_id.map(str::to_string));
        push_q(
            &mut q,
            "publishStatus",
            publish_status.map(|s| s.as_str().to_string()),
        );
        push_qi(&mut q, "pageNum", page_num);
        push_qi(&mut q, "pageSize", page_size);
        self.client.get_page("/openapi/experts", &q)
    }

    pub fn get(&self, expert_ref: &str) -> Result<ApiResponse<Value>> {
        let expert_ref = encode_path_segment(expert_ref);
        self.client
            .get_json(&format!("/openapi/experts/{expert_ref}"), &[])
    }

    pub fn create(
        &self,
        name: &str,
        display_name: &str,
        package: Option<&Path>,
        extra: HashMap<String, String>,
    ) -> Result<ApiResponse<Value>> {
        let mut fields = extra;
        fields.insert("name".into(), name.into());
        fields.insert("displayName".into(), display_name.into());
        self.client
            .post_operation_multipart("experts-create", "/openapi/experts", &fields, package)
    }

    pub fn update(
        &self,
        expert_ref: &str,
        package: Option<&Path>,
        fields: HashMap<String, String>,
    ) -> Result<ApiResponse<Value>> {
        let expert_ref = encode_path_segment(expert_ref);
        self.client.post_operation_multipart(
            "experts-update",
            &format!("/openapi/experts/{expert_ref}/update"),
            &fields,
            package,
        )
    }

    pub fn delete(&self, expert_ref: &str) -> Result<ApiResponse<Value>> {
        let expert_ref = encode_path_segment(expert_ref);
        self.client
            .post_empty(&format!("/openapi/experts/{expert_ref}/delete"), &[])
    }

    pub fn set_enabled(
        &self,
        expert_ref: &str,
        source: SkillSource,
        enabled: bool,
        disabled_reason: Option<&str>,
    ) -> Result<ApiResponse<Value>> {
        let expert_ref = encode_path_segment(expert_ref);
        let q = vec![("source".into(), source.as_str().into())];
        let mut body = serde_json::Map::new();
        body.insert("enabled".into(), json!(enabled));
        if let Some(r) = disabled_reason {
            body.insert("disabledReason".into(), json!(r));
        }
        self.client.post_json(
            &format!("/openapi/experts/{expert_ref}/toggle"),
            &q,
            Value::Object(body),
        )
    }

    pub fn set_visibility(
        &self,
        expert_ref: &str,
        source: SkillSource,
        visibility_type: VisibilityType,
        scopes: Option<Value>,
    ) -> Result<ApiResponse<Value>> {
        let expert_ref = encode_path_segment(expert_ref);
        let q = vec![("source".into(), source.as_str().into())];
        let mut body = serde_json::Map::new();
        body.insert("type".into(), json!(visibility_type.as_str()));
        if let Some(s) = scopes {
            body.insert("scopes".into(), s);
        }
        self.client.post_json(
            &format!("/openapi/experts/{expert_ref}/visibility"),
            &q,
            Value::Object(body),
        )
    }

    pub fn get_visibility(
        &self,
        expert_ref: &str,
        source: SkillSource,
    ) -> Result<ApiResponse<Value>> {
        let expert_ref = encode_path_segment(expert_ref);
        let q = vec![("source".into(), source.as_str().into())];
        self.client
            .get_json(&format!("/openapi/experts/{expert_ref}/visibility"), &q)
    }
}
