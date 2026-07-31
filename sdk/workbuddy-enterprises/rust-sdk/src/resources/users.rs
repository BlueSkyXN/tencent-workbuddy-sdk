use crate::client::{encode_path_segment, push_q, push_qb, push_qi, Client};
use crate::error::Result;
use crate::operations::validate_json_operation;
use crate::response::{parse_page_with_keys, ApiResponse, Page};
use serde_json::{json, Value};

pub struct UsersResource<'a> {
    pub(crate) client: &'a Client,
}

impl UsersResource<'_> {
    #[allow(clippy::too_many_arguments)]
    pub fn list(
        &self,
        page: Option<i64>,
        page_size: Option<i64>,
        keyword: Option<&str>,
        dep: Option<&str>,
        include_subtree: Option<bool>,
        is_root: Option<bool>,
        plugin_enabled: Option<i64>,
        use_cache: Option<bool>,
        exact_match: Option<bool>,
    ) -> Result<ApiResponse<Page<Value>>> {
        let mut q = Vec::new();
        push_qi(&mut q, "page", page);
        push_qi(&mut q, "pageSize", page_size);
        push_q(&mut q, "keyword", keyword.map(|s| s.to_string()));
        push_q(&mut q, "dep", dep.map(|s| s.to_string()));
        push_qb(&mut q, "include_subtree", include_subtree);
        push_qb(&mut q, "is_root", is_root);
        push_qi(&mut q, "plugin_enabled", plugin_enabled);
        push_qb(&mut q, "use_cache", use_cache);
        push_qb(&mut q, "exact_match", exact_match);
        let resp = self.client.get_json("/users", &q)?;
        let page = parse_page_with_keys(resp.data, &["users", "items", "list", "records"]);
        Ok(ApiResponse {
            data: page,
            code: resp.code,
            message: resp.message,
            request_id: resp.request_id,
            raw: resp.raw,
        })
    }

    pub fn update(&self, user_id: &str, body: Value) -> Result<ApiResponse<Value>> {
        validate_json_operation("users-update", &body)?;
        let user_id = encode_path_segment(user_id);
        self.client
            .post_json(&format!("/users/{user_id}/update"), &[], body)
    }

    pub fn delete(&self, user_id: &str) -> Result<ApiResponse<Value>> {
        let user_id = encode_path_segment(user_id);
        self.client
            .post_empty(&format!("/users/{user_id}/delete"), &[])
    }

    pub fn update_password(&self, user_id: &str, password: &str) -> Result<ApiResponse<Value>> {
        let user_id = encode_path_segment(user_id);
        self.client.post_json(
            &format!("/users/{user_id}/password/update"),
            &[],
            json!({ "password": password }),
        )
    }
}
