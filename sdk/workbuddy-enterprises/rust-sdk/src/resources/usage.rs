
use crate::client::Client;
use crate::error::Result;
use crate::response::{parse_page, ApiResponse, Page};
use serde_json::{json, Value};

pub struct UsageResource<'a> {
    pub(crate) client: &'a Client,
}

impl<'a> UsageResource<'a> {
    pub fn get_quota_cycle(&self) -> Result<ApiResponse<Value>> {
        self.client.get_json("/openapi/usage/quota-cycle", &[])
    }

    pub fn get_default_quota(&self) -> Result<ApiResponse<Value>> {
        self.client.get_json("/openapi/usage/default-quota", &[])
    }

    pub fn update_default_quota(&self, body: Value) -> Result<ApiResponse<Value>> {
        self.client
            .post_json("/openapi/usage/default-quota/update", &[], body)
    }

    pub fn query_members(&self, user_ids: &[&str]) -> Result<ApiResponse<Value>> {
        self.client.post_json(
            "/openapi/usage/members/query",
            &[],
            json!({ "userIds": user_ids }),
        )
    }

    pub fn query_member_limits(&self, user_ids: &[&str]) -> Result<ApiResponse<Value>> {
        self.client.post_json(
            "/openapi/usage/members/limit-query",
            &[],
            json!({ "userIds": user_ids }),
        )
    }

    pub fn update_member_quota(&self, body: Value) -> Result<ApiResponse<Value>> {
        self.client
            .post_json("/openapi/usage/members/quota/update", &[], body)
    }

    pub fn update_department_quota(
        &self,
        department_id: &str,
        body: Value,
    ) -> Result<ApiResponse<Value>> {
        self.client.post_json(
            &format!("/openapi/usage/departments/{department_id}/quota/update"),
            &[],
            body,
        )
    }

    pub fn query_member_details(&self, body: Value) -> Result<ApiResponse<Page<Value>>> {
        let resp = self
            .client
            .post_json("/openapi/usage/members/detail", &[], body)?;
        let page = if resp.data.get("items").is_some() || resp.data.get("nextPageToken").is_some()
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
}
