use crate::client::{encode_path_segment, Client};
use crate::error::Result;
use crate::operations::validate_json_operation;
use crate::response::{parse_page, ApiResponse, Page};
use serde_json::{json, Value};

pub struct UsageResource<'a> {
    pub(crate) client: &'a Client,
}

impl UsageResource<'_> {
    pub fn get_quota_cycle(&self) -> Result<ApiResponse<Value>> {
        self.client.get_json("/openapi/usage/quota-cycle", &[])
    }

    pub fn get_default_quota(&self) -> Result<ApiResponse<Value>> {
        self.client.get_json("/openapi/usage/default-quota", &[])
    }

    pub fn update_default_quota(&self, body: Value) -> Result<ApiResponse<Value>> {
        validate_json_operation("usage-default-quota-update", &body)?;
        self.client
            .post_json("/openapi/usage/default-quota/update", &[], body)
    }

    pub fn query_members(&self, user_ids: &[&str]) -> Result<ApiResponse<Value>> {
        self.query_members_with_options(Some(user_ids), None, None, None, None, None)
    }

    #[allow(clippy::too_many_arguments)]
    pub fn query_members_with_options(
        &self,
        user_ids: Option<&[&str]>,
        user_names: Option<&[&str]>,
        page_num: Option<i64>,
        page_size: Option<i64>,
        start_time: Option<&str>,
        end_time: Option<&str>,
    ) -> Result<ApiResponse<Value>> {
        let mut body = member_selectors(user_ids, user_names, page_num, page_size);
        if let Some(start_time) = start_time {
            body.insert("startTime".into(), json!(start_time));
        }
        if let Some(end_time) = end_time {
            body.insert("endTime".into(), json!(end_time));
        }
        let body = Value::Object(body);
        validate_json_operation("usage-members-query", &body)?;
        self.client
            .post_json("/openapi/usage/members/query", &[], body)
    }

    pub fn query_member_limits(&self, user_ids: &[&str]) -> Result<ApiResponse<Value>> {
        self.query_member_limits_with_options(Some(user_ids), None, None, None)
    }

    pub fn query_member_limits_with_options(
        &self,
        user_ids: Option<&[&str]>,
        user_names: Option<&[&str]>,
        page_num: Option<i64>,
        page_size: Option<i64>,
    ) -> Result<ApiResponse<Value>> {
        let body = member_selectors(user_ids, user_names, page_num, page_size);
        let body = Value::Object(body);
        validate_json_operation("usage-members-limit-query", &body)?;
        self.client
            .post_json("/openapi/usage/members/limit-query", &[], body)
    }

    pub fn update_member_quota(&self, body: Value) -> Result<ApiResponse<Value>> {
        validate_json_operation("usage-members-quota-update", &body)?;
        self.client
            .post_json("/openapi/usage/members/quota/update", &[], body)
    }

    pub fn update_department_quota(
        &self,
        department_id: &str,
        body: Value,
    ) -> Result<ApiResponse<Value>> {
        validate_json_operation("usage-department-quota-update", &body)?;
        let department_id = encode_path_segment(department_id);
        self.client.post_json(
            &format!("/openapi/usage/departments/{department_id}/quota/update"),
            &[],
            body,
        )
    }

    pub fn query_member_details(&self, body: Value) -> Result<ApiResponse<Page<Value>>> {
        validate_json_operation("usage-members-detail", &body)?;
        let resp = self
            .client
            .post_json("/openapi/usage/members/detail", &[], body)?;
        let page = if resp.data.get("items").is_some() || resp.data.get("nextPageToken").is_some() {
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

fn member_selectors(
    user_ids: Option<&[&str]>,
    user_names: Option<&[&str]>,
    page_num: Option<i64>,
    page_size: Option<i64>,
) -> serde_json::Map<String, Value> {
    let mut body = serde_json::Map::new();
    if let Some(user_ids) = user_ids {
        body.insert("userIds".into(), json!(user_ids));
    }
    if let Some(user_names) = user_names {
        body.insert("userNames".into(), json!(user_names));
    }
    if let Some(page_num) = page_num {
        body.insert("pageNum".into(), json!(page_num));
    }
    if let Some(page_size) = page_size {
        body.insert("pageSize".into(), json!(page_size));
    }
    body
}
