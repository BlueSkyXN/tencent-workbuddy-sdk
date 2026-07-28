use crate::client::{push_q, push_qb, push_qi, Client};
use crate::error::Result;
use crate::response::ApiResponse;
use serde_json::{json, Value};

pub struct ModelsResource<'a> {
    pub(crate) client: &'a Client,
}

impl ModelsResource<'_> {
    pub fn list_builtin(&self) -> Result<ApiResponse<crate::response::Page<Value>>> {
        self.client.get_page("/openapi/models/builtin", &[])
    }

    pub fn set_builtin_enabled(&self, model_id: &str, enabled: bool) -> Result<ApiResponse<Value>> {
        self.client.post_json(
            &format!("/openapi/models/builtin/{model_id}/toggle"),
            &[],
            json!({ "enabled": enabled }),
        )
    }

    pub fn set_builtin_visibility(
        &self,
        model_id: &str,
        scope: &str,
        user_ids: Option<&[&str]>,
        group_ids: Option<&[&str]>,
    ) -> Result<ApiResponse<Value>> {
        self.set_model_visibility(
            &format!("/openapi/models/builtin/{model_id}/visibility"),
            scope,
            user_ids,
            group_ids,
        )
    }

    pub fn list_custom(
        &self,
        page_num: Option<i64>,
        page_size: Option<i64>,
    ) -> Result<ApiResponse<crate::response::Page<Value>>> {
        let mut q = Vec::new();
        push_qi(&mut q, "pageNum", page_num);
        push_qi(&mut q, "pageSize", page_size);
        self.client.get_page("/openapi/models/custom", &q)
    }

    pub fn create_custom(&self, body: Value) -> Result<ApiResponse<Value>> {
        self.client.post_json("/openapi/models/custom", &[], body)
    }

    pub fn get_custom(&self, model_id: &str) -> Result<ApiResponse<Value>> {
        self.client
            .get_json(&format!("/openapi/models/custom/{model_id}"), &[])
    }

    pub fn delete_custom(&self, model_id: &str) -> Result<ApiResponse<Value>> {
        // no requestBody in YAML
        self.client
            .post_empty(&format!("/openapi/models/custom/{model_id}/delete"), &[])
    }

    pub fn set_custom_visibility(
        &self,
        model_id: &str,
        scope: &str,
        user_ids: Option<&[&str]>,
        group_ids: Option<&[&str]>,
    ) -> Result<ApiResponse<Value>> {
        self.set_model_visibility(
            &format!("/openapi/models/custom/{model_id}/visibility"),
            scope,
            user_ids,
            group_ids,
        )
    }

    pub fn list_available(&self, user_id: &str) -> Result<ApiResponse<Value>> {
        let q = vec![("userId".into(), user_id.into())];
        self.client.get_json("/openapi/models/available", &q)
    }

    pub fn list(
        &self,
        source: Option<&str>,
        page_num: Option<i64>,
        page_size: Option<i64>,
        enabled: Option<bool>,
        provider: Option<&str>,
    ) -> Result<ApiResponse<crate::response::Page<Value>>> {
        let mut q = Vec::new();
        push_q(&mut q, "source", source.map(|s| s.to_string()));
        push_qi(&mut q, "pageNum", page_num);
        push_qi(&mut q, "pageSize", page_size);
        push_qb(&mut q, "enabled", enabled);
        push_q(&mut q, "provider", provider.map(|s| s.to_string()));
        self.client.get_page("/openapi/models", &q)
    }

    pub fn get(&self, model_id: &str) -> Result<ApiResponse<Value>> {
        self.client
            .get_json(&format!("/openapi/models/{model_id}"), &[])
    }

    pub fn set_enabled(&self, model_id: &str, enabled: bool) -> Result<ApiResponse<Value>> {
        self.client.post_json(
            &format!("/openapi/models/{model_id}/toggle"),
            &[],
            json!({ "enabled": enabled }),
        )
    }

    pub fn set_visibility(
        &self,
        model_id: &str,
        scope: &str,
        user_ids: Option<&[&str]>,
        group_ids: Option<&[&str]>,
    ) -> Result<ApiResponse<Value>> {
        self.set_model_visibility(
            &format!("/openapi/models/{model_id}/visibility"),
            scope,
            user_ids,
            group_ids,
        )
    }

    fn set_model_visibility(
        &self,
        suffix: &str,
        scope: &str,
        user_ids: Option<&[&str]>,
        group_ids: Option<&[&str]>,
    ) -> Result<ApiResponse<Value>> {
        let mut body = serde_json::Map::new();
        body.insert("scope".into(), json!(scope));
        if let Some(v) = user_ids {
            body.insert("userIds".into(), json!(v));
        }
        if let Some(v) = group_ids {
            body.insert("groupIds".into(), json!(v));
        }
        self.client.post_json(suffix, &[], Value::Object(body))
    }
}
