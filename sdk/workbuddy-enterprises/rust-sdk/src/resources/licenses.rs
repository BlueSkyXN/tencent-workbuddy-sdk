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
        self.client.post_json(
            "/openapi/license/members/query",
            &[],
            json!({ "userIds": user_ids }),
        )
    }

    pub fn grant(&self, user_ids: &[&str]) -> Result<ApiResponse<Value>> {
        self.client.post_json(
            "/openapi/license/members/grant",
            &[],
            json!({ "userIds": user_ids }),
        )
    }

    pub fn revoke(&self, user_ids: &[&str]) -> Result<ApiResponse<Value>> {
        self.client.post_json(
            "/openapi/license/members/revoke",
            &[],
            json!({ "userIds": user_ids }),
        )
    }
}
