use crate::client::Client;
use crate::error::Result;
use crate::operations::validate_json_operation;
use crate::response::ApiResponse;
use serde_json::{json, Value};

pub struct ExpertCategoriesResource<'a> {
    pub(crate) client: &'a Client,
}

impl ExpertCategoriesResource<'_> {
    pub fn list(&self) -> Result<ApiResponse<crate::response::Page<Value>>> {
        self.client.get_page("/openapi/expert-categories", &[])
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
        let body = Value::Object(body);
        validate_json_operation("expert-categories-create", &body)?;
        self.client
            .post_json("/openapi/expert-categories", &[], body)
    }

    pub fn update(&self, category_id: i64, body: Value) -> Result<ApiResponse<Value>> {
        validate_json_operation("expert-categories-update", &body)?;
        self.client.post_json(
            &format!("/openapi/expert-categories/{category_id}/update"),
            &[],
            body,
        )
    }

    pub fn delete(&self, category_id: i64) -> Result<ApiResponse<Value>> {
        self.client.post_empty(
            &format!("/openapi/expert-categories/{category_id}/delete"),
            &[],
        )
    }

    pub fn reorder(&self, ordered_ids: &[i64]) -> Result<ApiResponse<Value>> {
        let body = json!({ "orderedIds": ordered_ids });
        validate_json_operation("expert-categories-reorder", &body)?;
        self.client
            .post_json("/openapi/expert-categories/reorder", &[], body)
    }
}
