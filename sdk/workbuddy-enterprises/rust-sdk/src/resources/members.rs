use crate::client::{push_q, push_qi, Client};
use crate::error::Result;
use crate::operations::validate_json_operation;
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

    /// YAML requires body.members[] with username + email.
    pub fn add(
        &self,
        members: &[Value],
        grant_license: Option<bool>,
    ) -> Result<ApiResponse<Value>> {
        let mut body = serde_json::Map::new();
        body.insert("members".into(), json!(members));
        if let Some(g) = grant_license {
            body.insert("grantLicense".into(), json!(g));
        }
        let body = Value::Object(body);
        validate_json_operation("members-add", &body)?;
        self.client.post_json("/openapi/members/add", &[], body)
    }

    pub fn add_raw(&self, body: Value) -> Result<ApiResponse<Value>> {
        validate_json_operation("members-add", &body)?;
        self.client.post_json("/openapi/members/add", &[], body)
    }
}
