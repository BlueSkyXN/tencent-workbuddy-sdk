use crate::client::Client;
use crate::error::Result;
use crate::response::ApiResponse;
use serde_json::{json, Value};

pub struct SkillCategoriesResource<'a> {
    pub(crate) client: &'a Client,
}

impl SkillCategoriesResource<'_> {
    pub fn list(&self) -> Result<ApiResponse<crate::response::Page<Value>>> {
        self.client.get_page("/openapi/skill-categories", &[])
    }

    pub fn create(
        &self,
        name: &str,
        description: Option<&str>,
        sort_order: Option<i64>,
    ) -> Result<ApiResponse<Value>> {
        let mut body = serde_json::Map::new();
        body.insert("name".into(), json!(name));
        if let Some(d) = description {
            body.insert("description".into(), json!(d));
        }
        if let Some(s) = sort_order {
            body.insert("sortOrder".into(), json!(s));
        }
        self.client
            .post_json("/openapi/skill-categories", &[], Value::Object(body))
    }

    pub fn update(&self, category_id: i64, body: Value) -> Result<ApiResponse<Value>> {
        self.client.post_json(
            &format!("/openapi/skill-categories/{category_id}/update"),
            &[],
            body,
        )
    }

    pub fn delete(&self, category_id: i64) -> Result<ApiResponse<Value>> {
        self.client.post_json(
            &format!("/openapi/skill-categories/{category_id}/delete"),
            &[],
            json!({}),
        )
    }

    pub fn reorder(&self, ordered_ids: &[i64]) -> Result<ApiResponse<Value>> {
        self.client.post_json(
            "/openapi/skill-categories/reorder",
            &[],
            json!({ "orderedIds": ordered_ids }),
        )
    }
}
