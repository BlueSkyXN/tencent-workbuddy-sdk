use crate::client::{push_q, push_qi, Client};
use crate::error::Result;
use crate::response::ApiResponse;
use serde_json::{json, Value};

pub struct MembersResource<'a> {
    pub(crate) client: &'a Client,
}

impl MembersResource<'_> {
    pub fn list(
        &self,
        page_num: Option<i64>,
        page_size: Option<i64>,
        keyword: Option<&str>,
    ) -> Result<ApiResponse<crate::response::Page<Value>>> {
        let mut q = Vec::new();
        push_qi(&mut q, "pageNum", page_num);
        push_qi(&mut q, "pageSize", page_size);
        push_q(&mut q, "keyword", keyword.map(|s| s.to_string()));
        self.client.get_page("/openapi/members", &q)
    }

    pub fn add_user_ids(&self, user_ids: &[&str]) -> Result<ApiResponse<Value>> {
        self.client
            .post_json("/openapi/members/add", &[], json!({ "userIds": user_ids }))
    }

    pub fn add_raw(&self, body: Value) -> Result<ApiResponse<Value>> {
        self.client.post_json("/openapi/members/add", &[], body)
    }
}
