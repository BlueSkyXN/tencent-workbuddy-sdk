use crate::client::{push_q, push_qi, Client};
use crate::error::Result;
use crate::response::{parse_page_with_keys, ApiResponse, Page};
use serde_json::Value;

pub struct AnalyticsResource<'a> {
    pub(crate) client: &'a Client,
}

impl AnalyticsResource<'_> {
    pub fn metrics_download_url_v2(
        &self,
        queries: &str,
        range_start: &str,
        range_end: &str,
        range_step: i64,
    ) -> Result<ApiResponse<Value>> {
        let mut q = Vec::new();
        push_q(&mut q, "queries", Some(queries.to_string()));
        push_q(&mut q, "range.start", Some(range_start.to_string()));
        push_q(&mut q, "range.end", Some(range_end.to_string()));
        push_qi(&mut q, "range.step", Some(range_step));
        self.client.get_json("/metrics/download_url/v2", &q)
    }

    pub fn metrics_download_url(
        &self,
        queries: &str,
        range_start: &str,
        range_end: &str,
        range_step: i64,
    ) -> Result<ApiResponse<Value>> {
        let mut q = Vec::new();
        push_q(&mut q, "queries", Some(queries.to_string()));
        push_q(&mut q, "range.start", Some(range_start.to_string()));
        push_q(&mut q, "range.end", Some(range_end.to_string()));
        push_qi(&mut q, "range.step", Some(range_step));
        self.client.get_json("/metrics/download_url", &q)
    }

    pub fn metrics(
        &self,
        queries: &str,
        range_start: &str,
        range_end: &str,
        range_step: i64,
    ) -> Result<ApiResponse<Value>> {
        let mut q = Vec::new();
        push_q(&mut q, "queries", Some(queries.to_string()));
        push_q(&mut q, "range.start", Some(range_start.to_string()));
        push_q(&mut q, "range.end", Some(range_end.to_string()));
        push_qi(&mut q, "range.step", Some(range_step));
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
        let page = parse_page_with_keys(resp.data, &["members", "items", "list", "records"]);
        Ok(ApiResponse {
            data: page,
            code: resp.code,
            message: resp.message,
            request_id: resp.request_id,
            raw: resp.raw,
        })
    }
}
