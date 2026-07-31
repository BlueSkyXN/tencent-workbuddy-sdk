use crate::client::Client;
use crate::error::Result;
use crate::response::ApiResponse;
use serde_json::{json, Value};

pub struct LicensesResource<'a> {
    pub(crate) client: &'a Client,
}

impl LicensesResource<'_> {
    pub fn overview(&self) -> Result<ApiResponse<Value>> {
        self.client.get_json("/openapi/license/overview", &[])
    }

    pub fn query_members(&self, user_ids: &[&str]) -> Result<ApiResponse<Value>> {
        self.query_members_with_options(Some(user_ids), None)
    }

    pub fn query_members_with_options(
        &self,
        user_ids: Option<&[&str]>,
        user_names: Option<&[&str]>,
    ) -> Result<ApiResponse<Value>> {
        let body = member_selectors(user_ids, user_names);
        self.client
            .post_json("/openapi/license/members/query", &[], body)
    }

    pub fn grant(&self, user_ids: &[&str]) -> Result<ApiResponse<Value>> {
        self.grant_with_options(Some(user_ids), None)
    }

    pub fn grant_with_options(
        &self,
        user_ids: Option<&[&str]>,
        user_names: Option<&[&str]>,
    ) -> Result<ApiResponse<Value>> {
        let body = member_selectors(user_ids, user_names);
        self.client
            .post_json("/openapi/license/members/grant", &[], body)
    }

    pub fn revoke(&self, user_ids: &[&str]) -> Result<ApiResponse<Value>> {
        self.revoke_with_reason(user_ids, None)
    }

    pub fn revoke_with_reason(
        &self,
        user_ids: &[&str],
        reason: Option<&str>,
    ) -> Result<ApiResponse<Value>> {
        let mut body = serde_json::Map::new();
        body.insert("userIds".into(), json!(user_ids));
        if let Some(reason) = reason {
            body.insert("reason".into(), json!(reason));
        }
        self.client
            .post_json("/openapi/license/members/revoke", &[], Value::Object(body))
    }
}

fn member_selectors(user_ids: Option<&[&str]>, user_names: Option<&[&str]>) -> Value {
    let mut body = serde_json::Map::new();
    if let Some(user_ids) = user_ids {
        body.insert("userIds".into(), json!(user_ids));
    }
    if let Some(user_names) = user_names {
        body.insert("userNames".into(), json!(user_names));
    }
    Value::Object(body)
}
