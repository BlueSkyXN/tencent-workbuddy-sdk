
use crate::client::{push_q, push_qb, push_qi, Client};
use crate::error::Result;
use crate::response::{parse_page, ApiResponse, Page};
use serde_json::{json, Value};

pub struct UsersResource<'a> {
    pub(crate) client: &'a Client,
}

impl<'a> UsersResource<'a> {
    pub fn list(
        &self,
        page: Option<i64>,
        page_size: Option<i64>,
        keyword: Option<&str>,
        dep: Option<&str>,
        include_subtree: Option<bool>,
    ) -> Result<ApiResponse<Page<Value>>> {
        let mut q = Vec::new();
        push_qi(&mut q, "page", page);
        push_qi(&mut q, "pageSize", page_size);
        push_q(&mut q, "keyword", keyword.map(|s| s.to_string()));
        push_q(&mut q, "dep", dep.map(|s| s.to_string()));
        push_qb(&mut q, "include_subtree", include_subtree);
        let resp = self.client.get_json("/users", &q)?;
        let page = if resp.data.get("items").is_some()
            || resp.data.get("list").is_some()
            || resp.data.get("totalCount").is_some()
        {
            parse_page(resp.data)
        } else {
            Page {
                items: vec![],
                total_count: None,
                page: None,
                page_num: None,
                page_size: None,
                next_page_token: None,
                extra: resp.data,
            }
        };
        Ok(ApiResponse {
            data: page,
            code: resp.code,
            message: resp.message,
            request_id: resp.request_id,
            raw: resp.raw,
        })
    }

    pub fn update(&self, user_id: &str, body: Value) -> Result<ApiResponse<Value>> {
        self.client
            .post_json(&format!("/users/{user_id}/update"), &[], body)
    }

    pub fn delete(&self, user_id: &str) -> Result<ApiResponse<Value>> {
        self.client
            .post_json(&format!("/users/{user_id}/delete"), &[], json!({}))
    }

    pub fn update_password(&self, user_id: &str, password: &str) -> Result<ApiResponse<Value>> {
        self.client.post_json(
            &format!("/users/{user_id}/password/update"),
            &[],
            json!({ "password": password }),
        )
    }
}
