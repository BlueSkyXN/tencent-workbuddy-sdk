use serde::Deserialize;
use serde_json::Value;

#[derive(Debug, Clone)]
pub struct ApiResponse<T> {
    pub data: T,
    pub code: i64,
    pub message: String,
    pub request_id: Option<String>,
    pub raw: Option<Value>,
}

#[derive(Debug, Clone, Default)]
pub struct Page<T> {
    pub items: Vec<T>,
    pub total_count: Option<i64>,
    pub page: Option<i64>,
    pub page_num: Option<i64>,
    pub page_size: Option<i64>,
    pub next_page_token: Option<String>,
    pub extra: Value,
}

#[derive(Debug, Deserialize)]
pub(crate) struct WireEnvelope {
    pub code: Option<i64>,
    pub msg: Option<String>,
    pub message: Option<String>,
    #[serde(rename = "requestId")]
    pub request_id: Option<String>,
    pub data: Option<Value>,
}

pub fn parse_page(data: Value) -> Page<Value> {
    parse_page_with_keys(data, &["items", "list", "records", "users", "members"])
}

pub fn parse_page_with_keys(data: Value, item_keys: &[&str]) -> Page<Value> {
    let obj = data.as_object().cloned().unwrap_or_default();
    let mut items = Vec::new();
    for key in item_keys {
        if let Some(Value::Array(arr)) = obj.get(*key) {
            items = arr.clone();
            break;
        }
    }

    let mut page = Page {
        items,
        total_count: int_field(&obj, "totalCount").or_else(|| int_field(&obj, "total")),
        page: int_field(&obj, "page"),
        page_num: int_field(&obj, "pageNum"),
        page_size: int_field(&obj, "pageSize"),
        next_page_token: obj
            .get("nextPageToken")
            .and_then(|v| v.as_str())
            .map(|s| s.to_string()),
        extra: Value::Object(obj.clone()),
    };

    if let Some(Value::Object(nested)) = obj.get("pagination") {
        if page.total_count.is_none() {
            page.total_count =
                int_field(nested, "totalCount").or_else(|| int_field(nested, "total"));
        }
        if page.page.is_none() {
            page.page = int_field(nested, "page");
        }
        if page.page_num.is_none() {
            page.page_num = int_field(nested, "pageNum");
        }
        if page.page_size.is_none() {
            page.page_size = int_field(nested, "pageSize");
        }
        if page.next_page_token.is_none() {
            page.next_page_token = nested
                .get("nextPageToken")
                .and_then(|v| v.as_str())
                .map(|s| s.to_string());
        }
    }
    page
}

fn int_field(obj: &serde_json::Map<String, Value>, key: &str) -> Option<i64> {
    obj.get(key).and_then(|v| {
        v.as_i64()
            .or_else(|| v.as_u64().map(|u| u as i64))
            .or_else(|| v.as_f64().map(|f| f as i64))
            .or_else(|| v.as_str().and_then(|s| s.parse().ok()))
    })
}
