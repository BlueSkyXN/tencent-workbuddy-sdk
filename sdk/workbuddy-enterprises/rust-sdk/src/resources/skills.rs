use crate::client::{push_q, push_qi, Client};
use crate::error::Result;
use crate::response::ApiResponse;
use crate::types::{PublishStatus, SkillSource, VisibilityType};
use serde_json::{json, Value};
use std::collections::HashMap;
use std::path::Path;

pub struct SkillsResource<'a> {
    pub(crate) client: &'a Client,
}

impl SkillsResource<'_> {
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
        push_q(&mut q, "categoryId", category_id.map(|s| s.to_string()));
        push_q(
            &mut q,
            "publishStatus",
            publish_status.map(|s| s.as_str().to_string()),
        );
        push_qi(&mut q, "pageNum", page_num);
        push_qi(&mut q, "pageSize", page_size);
        self.client.get_page("/openapi/skills", &q)
    }

    pub fn get(&self, skill_ref: &str) -> Result<ApiResponse<Value>> {
        self.client
            .get_json(&format!("/openapi/skills/{skill_ref}"), &[])
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
            .post_multipart("/openapi/skills", &fields, package)
    }

    pub fn update(
        &self,
        skill_ref: &str,
        package: Option<&Path>,
        fields: HashMap<String, String>,
    ) -> Result<ApiResponse<Value>> {
        self.client.post_multipart(
            &format!("/openapi/skills/{skill_ref}/update"),
            &fields,
            package,
        )
    }

    pub fn delete(&self, skill_ref: &str) -> Result<ApiResponse<Value>> {
        self.client.post_json(
            &format!("/openapi/skills/{skill_ref}/delete"),
            &[],
            json!({}),
        )
    }

    pub fn set_enabled(
        &self,
        skill_ref: &str,
        source: SkillSource,
        enabled: bool,
        disabled_reason: Option<&str>,
    ) -> Result<ApiResponse<Value>> {
        let q = vec![("source".into(), source.as_str().into())];
        let mut body = serde_json::Map::new();
        body.insert("enabled".into(), json!(enabled));
        if let Some(r) = disabled_reason {
            body.insert("disabledReason".into(), json!(r));
        }
        self.client.post_json(
            &format!("/openapi/skills/{skill_ref}/toggle"),
            &q,
            Value::Object(body),
        )
    }

    pub fn set_visibility(
        &self,
        skill_ref: &str,
        source: SkillSource,
        visibility_type: VisibilityType,
        scopes: Option<Value>,
    ) -> Result<ApiResponse<Value>> {
        let q = vec![("source".into(), source.as_str().into())];
        let mut body = serde_json::Map::new();
        body.insert("type".into(), json!(visibility_type.as_str()));
        if let Some(s) = scopes {
            body.insert("scopes".into(), s);
        }
        self.client.post_json(
            &format!("/openapi/skills/{skill_ref}/visibility"),
            &q,
            Value::Object(body),
        )
    }

    pub fn get_visibility(
        &self,
        skill_ref: &str,
        source: SkillSource,
    ) -> Result<ApiResponse<Value>> {
        let q = vec![("source".into(), source.as_str().into())];
        self.client
            .get_json(&format!("/openapi/skills/{skill_ref}/visibility"), &q)
    }
}
