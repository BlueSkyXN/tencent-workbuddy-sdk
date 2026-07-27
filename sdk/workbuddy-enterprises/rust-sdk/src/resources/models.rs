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
        body: Value,
    ) -> Result<ApiResponse<Value>> {
        self.client.post_json(
            &format!("/openapi/models/builtin/{model_id}/visibility"),
            &[],
            body,
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
        self.client.post_json(
            &format!("/openapi/models/custom/{model_id}/delete"),
            &[],
            json!({}),
        )
    }

    pub fn set_custom_visibility(&self, model_id: &str, body: Value) -> Result<ApiResponse<Value>> {
        self.client.post_json(
            &format!("/openapi/models/custom/{model_id}/visibility"),
            &[],
            body,
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

    pub fn set_visibility(&self, model_id: &str, body: Value) -> Result<ApiResponse<Value>> {
        self.client
            .post_json(&format!("/openapi/models/{model_id}/visibility"), &[], body)
    }
}
