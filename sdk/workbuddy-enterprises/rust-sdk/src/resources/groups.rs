use crate::client::{encode_path_segment, push_q, push_qi, Client};
use crate::error::Result;
use crate::response::ApiResponse;
use serde_json::{json, Value};

pub struct GroupsResource<'a> {
    pub(crate) client: &'a Client,
}

impl GroupsResource<'_> {
    pub fn list(
        &self,
        page: Option<i64>,
        page_size: Option<i64>,
        keyword: Option<&str>,
    ) -> Result<ApiResponse<crate::response::Page<Value>>> {
        let mut q = Vec::new();
        push_qi(&mut q, "page", page);
        push_qi(&mut q, "pageSize", page_size);
        push_q(&mut q, "keyword", keyword.map(|s| s.to_string()));
        self.client.get_page("/openapi/groups", &q)
    }

    pub fn get(&self, group_id: &str) -> Result<ApiResponse<Value>> {
        let group_id = encode_path_segment(group_id);
        self.client
            .get_json(&format!("/openapi/groups/{group_id}"), &[])
    }

    pub fn list_members(
        &self,
        group_id: &str,
        page: Option<i64>,
        page_size: Option<i64>,
        keyword: Option<&str>,
    ) -> Result<ApiResponse<crate::response::Page<Value>>> {
        let group_id = encode_path_segment(group_id);
        let mut q = Vec::new();
        push_qi(&mut q, "page", page);
        push_qi(&mut q, "pageSize", page_size);
        push_q(&mut q, "keyword", keyword.map(|s| s.to_string()));
        self.client
            .get_page(&format!("/openapi/groups/{group_id}/members"), &q)
    }

    pub fn add_members(
        &self,
        group_id: &str,
        user_ids: Option<&[&str]>,
        org_node_ids: Option<&[&str]>,
    ) -> Result<ApiResponse<Value>> {
        let group_id = encode_path_segment(group_id);
        let mut body = serde_json::Map::new();
        if let Some(v) = user_ids {
            body.insert("userIds".into(), json!(v));
        }
        if let Some(v) = org_node_ids {
            body.insert("orgNodeIds".into(), json!(v));
        }
        self.client.post_json(
            &format!("/openapi/groups/{group_id}/members/add"),
            &[],
            Value::Object(body),
        )
    }

    pub fn remove_members(
        &self,
        group_id: &str,
        user_ids: Option<&[&str]>,
        org_node_ids: Option<&[&str]>,
    ) -> Result<ApiResponse<Value>> {
        let group_id = encode_path_segment(group_id);
        let mut body = serde_json::Map::new();
        if let Some(v) = user_ids {
            body.insert("userIds".into(), json!(v));
        }
        if let Some(v) = org_node_ids {
            body.insert("orgNodeIds".into(), json!(v));
        }
        self.client.post_json(
            &format!("/openapi/groups/{group_id}/members/remove"),
            &[],
            Value::Object(body),
        )
    }

    pub fn replace_members(
        &self,
        group_id: &str,
        user_ids: Option<&[&str]>,
        user_names: Option<&[&str]>,
        clear_all: Option<bool>,
    ) -> Result<ApiResponse<Value>> {
        let group_id = encode_path_segment(group_id);
        let mut body = serde_json::Map::new();
        if let Some(v) = user_ids {
            body.insert("userIds".into(), json!(v));
        }
        if let Some(v) = user_names {
            body.insert("userNames".into(), json!(v));
        }
        if let Some(v) = clear_all {
            body.insert("clearAll".into(), json!(v));
        }
        self.client.post_json(
            &format!("/openapi/groups/{group_id}/members/replace"),
            &[],
            Value::Object(body),
        )
    }
}
