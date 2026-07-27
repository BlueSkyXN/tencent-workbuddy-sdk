use crate::client::{push_q, Client};
use crate::error::Result;
use crate::response::{parse_page, ApiResponse, Page};
use serde_json::Value;

pub struct AnalyticsResource<'a> {
    pub(crate) client: &'a Client,
}

impl AnalyticsResource<'_> {
    pub fn metrics_download_url_v2(&self, queries: Option<&str>) -> Result<ApiResponse<Value>> {
        let mut q = Vec::new();
        push_q(&mut q, "queries", queries.map(|s| s.to_string()));
        self.client.get_json("/metrics/download_url/v2", &q)
    }

    pub fn metrics_download_url(&self, queries: Option<&str>) -> Result<ApiResponse<Value>> {
        let mut q = Vec::new();
        push_q(&mut q, "queries", queries.map(|s| s.to_string()));
        self.client.get_json("/metrics/download_url", &q)
    }

    pub fn metrics(&self, queries: Option<&str>) -> Result<ApiResponse<Value>> {
        let mut q = Vec::new();
        push_q(&mut q, "queries", queries.map(|s| s.to_string()));
        self.client.get_json("/metrics", &q)
    }

    pub fn activity(&self, body: Value) -> Result<ApiResponse<Value>> {
        self.client
            .post_json("/dashboard/analytics/activity", &[], body)
    }

    pub fn dialog(&self, body: Value) -> Result<ApiResponse<Value>> {
        self.client
            .post_json("/dashboard/analytics/dialog", &[], body)
    }

    pub fn completion(&self, body: Value) -> Result<ApiResponse<Value>> {
        self.client
            .post_json("/dashboard/analytics/completion", &[], body)
    }

    pub fn generation(&self, body: Value) -> Result<ApiResponse<Value>> {
        self.client
            .post_json("/dashboard/analytics/generation", &[], body)
    }

    pub fn member_data(&self, body: Value) -> Result<ApiResponse<Page<Value>>> {
        let resp = self.client.post_json("/dashboard/member/data", &[], body)?;
        let page = if resp.data.get("items").is_some() || resp.data.get("list").is_some() {
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
