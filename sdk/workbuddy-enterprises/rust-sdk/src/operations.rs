//! Static Enterprise OpenAPI operation manifest used by the CLI and contract tests.

use crate::error::{Error, Result};
use serde_json::{Map, Value};
use std::collections::HashMap;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum OperationBodyKind {
    None,
    Json,
    Multipart,
}

#[derive(Debug, Clone, Copy)]
pub struct OperationSpec {
    pub name: &'static str,
    pub method: &'static str,
    /// Path suffix after `/enterprises/{enterpriseId}`.
    pub suffix_template: &'static str,
    pub path_params: &'static [&'static str],
    pub required_query: &'static [&'static str],
    pub allowed_query: &'static [&'static str],
    pub body_kind: OperationBodyKind,
    pub required_body_fields: &'static [&'static str],
    /// YAML top-level request-body properties. Nested dashboard structures are
    /// validated separately because their allowed fields vary by option object.
    pub allowed_body_fields: &'static [&'static str],
    pub write: bool,
}

/// Machine-readable METHOD + full OpenAPI path registry for external YAML gates.
/// This is handwritten metadata, not a redistributed copy of the upstream YAML.
#[rustfmt::skip]
pub const OPENAPI_OPERATIONS: &[(&str, &str)] = &[
    ("GET", "/enterprises/{enterpriseId}/users"),
    ("POST", "/enterprises/{enterpriseId}/users/{userId}/update"),
    ("POST", "/enterprises/{enterpriseId}/users/{userId}/delete"),
    ("POST", "/enterprises/{enterpriseId}/users/{userId}/password/update"),
    ("GET", "/enterprises/{enterpriseId}/info"),
    ("GET", "/enterprises/{enterpriseId}/license"),
    ("GET", "/enterprises/{enterpriseId}/metrics/download_url/v2"),
    ("GET", "/enterprises/{enterpriseId}/metrics/download_url"),
    ("GET", "/enterprises/{enterpriseId}/metrics"),
    ("POST", "/enterprises/{enterpriseId}/dashboard/analytics/activity"),
    ("POST", "/enterprises/{enterpriseId}/dashboard/analytics/dialog"),
    ("POST", "/enterprises/{enterpriseId}/dashboard/analytics/completion"),
    ("POST", "/enterprises/{enterpriseId}/dashboard/analytics/generation"),
    ("POST", "/enterprises/{enterpriseId}/dashboard/member/data"),
    ("GET", "/enterprises/{enterpriseId}/openapi/members"),
    ("GET", "/enterprises/{enterpriseId}/openapi/license/overview"),
    ("POST", "/enterprises/{enterpriseId}/openapi/license/members/query"),
    ("POST", "/enterprises/{enterpriseId}/openapi/license/members/grant"),
    ("GET", "/enterprises/{enterpriseId}/openapi/usage/quota-cycle"),
    ("GET", "/enterprises/{enterpriseId}/openapi/usage/default-quota"),
    ("POST", "/enterprises/{enterpriseId}/openapi/usage/default-quota/update"),
    ("POST", "/enterprises/{enterpriseId}/openapi/usage/members/query"),
    ("POST", "/enterprises/{enterpriseId}/openapi/usage/members/limit-query"),
    ("POST", "/enterprises/{enterpriseId}/openapi/usage/members/quota/update"),
    ("POST", "/enterprises/{enterpriseId}/openapi/usage/departments/{departmentId}/quota/update"),
    ("GET", "/enterprises/{enterpriseId}/openapi/models/builtin"),
    ("POST", "/enterprises/{enterpriseId}/openapi/models/builtin/{modelId}/toggle"),
    ("POST", "/enterprises/{enterpriseId}/openapi/models/builtin/{modelId}/visibility"),
    ("GET", "/enterprises/{enterpriseId}/openapi/models/custom"),
    ("POST", "/enterprises/{enterpriseId}/openapi/models/custom"),
    ("GET", "/enterprises/{enterpriseId}/openapi/models/custom/{modelId}"),
    ("POST", "/enterprises/{enterpriseId}/openapi/models/custom/{modelId}/delete"),
    ("POST", "/enterprises/{enterpriseId}/openapi/models/custom/{modelId}/visibility"),
    ("GET", "/enterprises/{enterpriseId}/openapi/models/available"),
    ("GET", "/enterprises/{enterpriseId}/openapi/models"),
    ("GET", "/enterprises/{enterpriseId}/openapi/models/{modelId}"),
    ("POST", "/enterprises/{enterpriseId}/openapi/models/{modelId}/toggle"),
    ("POST", "/enterprises/{enterpriseId}/openapi/models/{modelId}/visibility"),
    ("GET", "/enterprises/{enterpriseId}/openapi/groups"),
    ("GET", "/enterprises/{enterpriseId}/openapi/groups/{groupId}"),
    ("GET", "/enterprises/{enterpriseId}/openapi/groups/{groupId}/members"),
    ("POST", "/enterprises/{enterpriseId}/openapi/groups/{groupId}/members/add"),
    ("POST", "/enterprises/{enterpriseId}/openapi/groups/{groupId}/members/remove"),
    ("POST", "/enterprises/{enterpriseId}/openapi/groups/{groupId}/members/replace"),
    ("POST", "/enterprises/{enterpriseId}/openapi/usage/members/detail"),
    ("POST", "/enterprises/{enterpriseId}/openapi/members/add"),
    ("POST", "/enterprises/{enterpriseId}/openapi/license/members/revoke"),
    ("GET", "/enterprises/{enterpriseId}/openapi/skills"),
    ("POST", "/enterprises/{enterpriseId}/openapi/skills"),
    ("GET", "/enterprises/{enterpriseId}/openapi/skills/{skillRef}"),
    ("POST", "/enterprises/{enterpriseId}/openapi/skills/{skillRef}/update"),
    ("POST", "/enterprises/{enterpriseId}/openapi/skills/{skillRef}/delete"),
    ("POST", "/enterprises/{enterpriseId}/openapi/skills/{skillRef}/toggle"),
    ("GET", "/enterprises/{enterpriseId}/openapi/skills/{skillRef}/visibility"),
    ("POST", "/enterprises/{enterpriseId}/openapi/skills/{skillRef}/visibility"),
    ("GET", "/enterprises/{enterpriseId}/openapi/skill-categories"),
    ("POST", "/enterprises/{enterpriseId}/openapi/skill-categories"),
    ("POST", "/enterprises/{enterpriseId}/openapi/skill-categories/{id}/update"),
    ("POST", "/enterprises/{enterpriseId}/openapi/skill-categories/{id}/delete"),
    ("POST", "/enterprises/{enterpriseId}/openapi/skill-categories/reorder"),
    ("GET", "/enterprises/{enterpriseId}/openapi/experts"),
    ("POST", "/enterprises/{enterpriseId}/openapi/experts"),
    ("GET", "/enterprises/{enterpriseId}/openapi/experts/{expertRef}"),
    ("POST", "/enterprises/{enterpriseId}/openapi/experts/{expertRef}/update"),
    ("POST", "/enterprises/{enterpriseId}/openapi/experts/{expertRef}/delete"),
    ("POST", "/enterprises/{enterpriseId}/openapi/experts/{expertRef}/toggle"),
    ("GET", "/enterprises/{enterpriseId}/openapi/experts/{expertRef}/visibility"),
    ("POST", "/enterprises/{enterpriseId}/openapi/experts/{expertRef}/visibility"),
    ("GET", "/enterprises/{enterpriseId}/openapi/expert-categories"),
    ("POST", "/enterprises/{enterpriseId}/openapi/expert-categories"),
    ("POST", "/enterprises/{enterpriseId}/openapi/expert-categories/{id}/update"),
    ("POST", "/enterprises/{enterpriseId}/openapi/expert-categories/{id}/delete"),
    ("POST", "/enterprises/{enterpriseId}/openapi/expert-categories/reorder"),
];

macro_rules! op {
    ($name:literal, $method:literal, $suffix:literal, [$($path:literal),*], [$($required_query:literal),*], [$($query:literal),*], $body:ident, [$($required_body:literal),*], [$($allowed_body:literal),*], $write:expr) => {
        OperationSpec {
            name: $name,
            method: $method,
            suffix_template: $suffix,
            path_params: &[$($path),*],
            required_query: &[$($required_query),*],
            allowed_query: &[$($query),*],
            body_kind: OperationBodyKind::$body,
            required_body_fields: &[$($required_body),*],
            allowed_body_fields: &[$($allowed_body),*],
            write: $write,
        }
    };
}

/// One manifest entry per operation in `api.yaml` (73 total).
#[rustfmt::skip]
pub const OPERATION_SPECS: &[OperationSpec] = &[
    op!("users-list", "GET", "/users", [], [], ["page", "pageSize", "keyword", "dep", "include_subtree", "is_root", "plugin_enabled", "use_cache", "exact_match"], None, [], [], false),
    op!("users-update", "POST", "/users/{userId}/update", ["userId"], [], [], Json, [], ["userEnterpriseName", "phone", "email"], true),
    op!("users-delete", "POST", "/users/{userId}/delete", ["userId"], [], [], None, [], [], true),
    op!("users-password-update", "POST", "/users/{userId}/password/update", ["userId"], [], [], Json, [], ["password"], true),
    op!("enterprise-info", "GET", "/info", [], [], [], None, [], [], false),
    op!("enterprise-license", "GET", "/license", [], [], [], None, [], [], false),
    op!("metrics-download-url-v2", "GET", "/metrics/download_url/v2", [], ["queries", "range.start", "range.end", "range.step"], ["queries", "range.start", "range.end", "range.step"], None, [], [], false),
    op!("metrics-download-url", "GET", "/metrics/download_url", [], ["queries", "range.start", "range.end", "range.step"], ["queries", "range.start", "range.end", "range.step"], None, [], [], false),
    op!("metrics", "GET", "/metrics", [], ["queries", "range.start", "range.end", "range.step"], ["queries", "range.start", "range.end", "range.step"], None, [], [], false),
    op!("analytics-activity", "POST", "/dashboard/analytics/activity", [], [], [], Json, ["timeRange", "memberFilter", "clientFilter", "pluginFilter", "viewType", "activityOptions"], ["timeRange", "memberFilter", "clientFilter", "pluginFilter", "viewType", "activityOptions"], false),
    op!("analytics-dialog", "POST", "/dashboard/analytics/dialog", [], [], [], Json, ["timeRange", "memberFilter", "clientFilter", "pluginFilter", "viewType"], ["timeRange", "memberFilter", "clientFilter", "pluginFilter", "viewType", "dialogOptions"], false),
    op!("analytics-completion", "POST", "/dashboard/analytics/completion", [], [], [], Json, ["timeRange", "memberFilter", "clientFilter", "pluginFilter", "viewType"], ["timeRange", "memberFilter", "clientFilter", "pluginFilter", "viewType", "completionOptions"], false),
    op!("analytics-generation", "POST", "/dashboard/analytics/generation", [], [], [], Json, ["timeRange", "memberFilter", "clientFilter", "pluginFilter", "viewType"], ["timeRange", "memberFilter", "clientFilter", "pluginFilter", "viewType", "generationOptions"], false),
    op!("analytics-member-data", "POST", "/dashboard/member/data", [], [], [], Json, ["timeRange", "memberFilter", "clientFilter", "pluginFilter", "pagination"], ["timeRange", "memberFilter", "clientFilter", "pluginFilter", "pagination", "memberOptions"], false),
    op!("members-list", "GET", "/openapi/members", [], [], ["pageNum", "pageSize", "keyword"], None, [], [], false),
    op!("licenses-overview", "GET", "/openapi/license/overview", [], [], [], None, [], [], false),
    op!("licenses-members-query", "POST", "/openapi/license/members/query", [], [], [], Json, [], ["userIds", "userNames"], false),
    op!("licenses-members-grant", "POST", "/openapi/license/members/grant", [], [], [], Json, [], ["userIds", "userNames"], true),
    op!("usage-quota-cycle", "GET", "/openapi/usage/quota-cycle", [], [], [], None, [], [], false),
    op!("usage-default-quota", "GET", "/openapi/usage/default-quota", [], [], [], None, [], [], false),
    op!("usage-default-quota-update", "POST", "/openapi/usage/default-quota/update", [], [], [], Json, ["limitType"], ["limitType", "newLimit", "cycleType"], true),
    op!("usage-members-query", "POST", "/openapi/usage/members/query", [], [], [], Json, [], ["userIds", "userNames", "pageNum", "pageSize", "startTime", "endTime"], false),
    op!("usage-members-limit-query", "POST", "/openapi/usage/members/limit-query", [], [], [], Json, [], ["userIds", "userNames", "pageNum", "pageSize"], false),
    op!("usage-members-quota-update", "POST", "/openapi/usage/members/quota/update", [], [], [], Json, ["limitType"], ["userIds", "userNames", "limitType", "newLimit", "cycleType"], true),
    op!("usage-department-quota-update", "POST", "/openapi/usage/departments/{departmentId}/quota/update", ["departmentId"], [], [], Json, ["limitType"], ["limitType", "newLimit", "cycleType"], true),
    op!("models-builtin-list", "GET", "/openapi/models/builtin", [], [], [], None, [], [], false),
    op!("models-builtin-toggle", "POST", "/openapi/models/builtin/{modelId}/toggle", ["modelId"], [], [], Json, ["enabled"], ["enabled"], true),
    op!("models-builtin-visibility", "POST", "/openapi/models/builtin/{modelId}/visibility", ["modelId"], [], [], Json, ["scope"], ["scope", "userIds", "groupIds"], true),
    op!("models-custom-list", "GET", "/openapi/models/custom", [], [], ["pageNum", "pageSize"], None, [], [], false),
    op!("models-custom-create", "POST", "/openapi/models/custom", [], [], [], Json, ["displayName", "provider", "baseUrl", "apiKey", "modelName", "scope"], ["displayName", "provider", "baseUrl", "apiKey", "modelName", "contextLength", "enabled", "scope", "userIds", "groupIds"], true),
    op!("models-custom-get", "GET", "/openapi/models/custom/{modelId}", ["modelId"], [], [], None, [], [], false),
    op!("models-custom-delete", "POST", "/openapi/models/custom/{modelId}/delete", ["modelId"], [], [], None, [], [], true),
    op!("models-custom-visibility", "POST", "/openapi/models/custom/{modelId}/visibility", ["modelId"], [], [], Json, ["scope"], ["scope", "userIds", "groupIds"], true),
    op!("models-available", "GET", "/openapi/models/available", [], ["userId"], ["userId"], None, [], [], false),
    op!("models-list", "GET", "/openapi/models", [], [], ["source", "pageNum", "pageSize", "enabled", "provider"], None, [], [], false),
    op!("models-get", "GET", "/openapi/models/{modelId}", ["modelId"], [], [], None, [], [], false),
    op!("models-toggle", "POST", "/openapi/models/{modelId}/toggle", ["modelId"], [], [], Json, ["enabled"], ["enabled"], true),
    op!("models-visibility", "POST", "/openapi/models/{modelId}/visibility", ["modelId"], [], [], Json, ["scope"], ["scope", "userIds", "groupIds"], true),
    op!("groups-list", "GET", "/openapi/groups", [], [], ["page", "pageSize", "keyword"], None, [], [], false),
    op!("groups-get", "GET", "/openapi/groups/{groupId}", ["groupId"], [], [], None, [], [], false),
    op!("groups-members-list", "GET", "/openapi/groups/{groupId}/members", ["groupId"], [], ["page", "pageSize", "keyword"], None, [], [], false),
    op!("groups-members-add", "POST", "/openapi/groups/{groupId}/members/add", ["groupId"], [], [], Json, [], ["userIds", "orgNodeIds"], true),
    op!("groups-members-remove", "POST", "/openapi/groups/{groupId}/members/remove", ["groupId"], [], [], Json, [], ["userIds", "orgNodeIds"], true),
    op!("groups-members-replace", "POST", "/openapi/groups/{groupId}/members/replace", ["groupId"], [], [], Json, [], ["userIds", "userNames", "clearAll"], true),
    op!("usage-members-detail", "POST", "/openapi/usage/members/detail", [], [], [], Json, ["timeRange"], ["timeRange", "departmentIds", "userIds", "eventTypes", "principalTypes", "pageNum", "pageSize", "groupId", "version", "pageToken"], false),
    op!("members-add", "POST", "/openapi/members/add", [], [], [], Json, ["members"], ["members", "grantLicense"], true),
    op!("licenses-members-revoke", "POST", "/openapi/license/members/revoke", [], [], [], Json, ["userIds"], ["userIds", "reason"], true),
    op!("skills-list", "GET", "/openapi/skills", [], ["source"], ["source", "keyword", "categoryId", "publishStatus", "pageNum", "pageSize"], None, [], [], false),
    op!("skills-create", "POST", "/openapi/skills", [], [], [], Multipart, ["name", "displayName"], ["name", "displayName", "displayNameEn", "descriptionZh", "descriptionEn", "icon", "version", "publishStatus", "categoryId", "package", "expectedMd5", "expectedSha256"], true),
    op!("skills-get", "GET", "/openapi/skills/{skillRef}", ["skillRef"], [], [], None, [], [], false),
    op!("skills-update", "POST", "/openapi/skills/{skillRef}/update", ["skillRef"], [], [], Multipart, [], ["name", "displayName", "displayNameEn", "descriptionZh", "descriptionEn", "icon", "version", "publishStatus", "status", "disabledReason", "categoryId", "package", "expectedMd5", "expectedSha256"], true),
    op!("skills-delete", "POST", "/openapi/skills/{skillRef}/delete", ["skillRef"], [], [], None, [], [], true),
    op!("skills-toggle", "POST", "/openapi/skills/{skillRef}/toggle", ["skillRef"], ["source"], ["source"], Json, ["enabled"], ["enabled", "disabledReason"], true),
    op!("skills-visibility-set", "POST", "/openapi/skills/{skillRef}/visibility", ["skillRef"], ["source"], ["source"], Json, ["type"], ["type", "scopes"], true),
    op!("skills-visibility-get", "GET", "/openapi/skills/{skillRef}/visibility", ["skillRef"], ["source"], ["source"], None, [], [], false),
    op!("skill-categories-list", "GET", "/openapi/skill-categories", [], [], [], None, [], [], false),
    op!("skill-categories-create", "POST", "/openapi/skill-categories", [], [], [], Json, ["name"], ["name", "description", "sortOrder"], true),
    op!("skill-categories-update", "POST", "/openapi/skill-categories/{id}/update", ["id"], [], [], Json, [], ["name", "description", "sortOrder"], true),
    op!("skill-categories-delete", "POST", "/openapi/skill-categories/{id}/delete", ["id"], [], [], None, [], [], true),
    op!("skill-categories-reorder", "POST", "/openapi/skill-categories/reorder", [], [], [], Json, ["orderedIds"], ["orderedIds"], true),
    op!("experts-list", "GET", "/openapi/experts", [], ["source"], ["source", "keyword", "categoryId", "publishStatus", "pageNum", "pageSize"], None, [], [], false),
    op!("experts-create", "POST", "/openapi/experts", [], [], [], Multipart, ["name", "displayName"], ["name", "displayName", "displayNameEn", "professionZh", "professionEn", "agentName", "descriptionZh", "descriptionEn", "icon", "version", "publishStatus", "categoryId", "package", "expectedMd5", "expectedSha256"], true),
    op!("experts-get", "GET", "/openapi/experts/{expertRef}", ["expertRef"], [], [], None, [], [], false),
    op!("experts-update", "POST", "/openapi/experts/{expertRef}/update", ["expertRef"], [], [], Multipart, [], ["name", "displayName", "displayNameEn", "professionZh", "professionEn", "agentName", "descriptionZh", "descriptionEn", "icon", "version", "publishStatus", "status", "disabledReason", "categoryId", "package", "expectedMd5", "expectedSha256"], true),
    op!("experts-delete", "POST", "/openapi/experts/{expertRef}/delete", ["expertRef"], [], [], None, [], [], true),
    op!("experts-toggle", "POST", "/openapi/experts/{expertRef}/toggle", ["expertRef"], ["source"], ["source"], Json, ["enabled"], ["enabled", "disabledReason"], true),
    op!("experts-visibility-set", "POST", "/openapi/experts/{expertRef}/visibility", ["expertRef"], ["source"], ["source"], Json, ["type"], ["type", "scopes"], true),
    op!("experts-visibility-get", "GET", "/openapi/experts/{expertRef}/visibility", ["expertRef"], ["source"], ["source"], None, [], [], false),
    op!("expert-categories-list", "GET", "/openapi/expert-categories", [], [], [], None, [], [], false),
    op!("expert-categories-create", "POST", "/openapi/expert-categories", [], [], [], Json, ["name"], ["name", "description", "sortOrder"], true),
    op!("expert-categories-update", "POST", "/openapi/expert-categories/{id}/update", ["id"], [], [], Json, [], ["name", "description", "sortOrder"], true),
    op!("expert-categories-delete", "POST", "/openapi/expert-categories/{id}/delete", ["id"], [], [], None, [], [], true),
    op!("expert-categories-reorder", "POST", "/openapi/expert-categories/reorder", [], [], [], Json, ["orderedIds"], ["orderedIds"], true),
];

pub fn find_operation(name: &str) -> Option<&'static OperationSpec> {
    OPERATION_SPECS.iter().find(|spec| spec.name == name)
}

pub fn operation_names() -> impl Iterator<Item = &'static str> {
    OPERATION_SPECS.iter().map(|spec| spec.name)
}

/// Validates the manifest-level JSON contract before the generic operation path sends it.
/// Resource methods call this as well when they expose the same raw `Value` payload.
#[rustfmt::skip]
pub fn validate_json_operation(operation: &str, body: &Value) -> Result<()> {
    let spec = find_operation(operation)
        .ok_or_else(|| Error::Config(format!("unknown OpenAPI operation `{operation}`")))?;
    if spec.body_kind != OperationBodyKind::Json {
        return Err(Error::Config(format!("{operation} is not a JSON operation")));
    }
    let object = body
        .as_object()
        .ok_or_else(|| Error::Config(format!("{operation} requires a JSON object body")))?;
    for field in spec.required_body_fields {
        if !object.contains_key(*field) {
            return Err(Error::Config(format!(
                "{operation} body is missing required field `{field}`"
            )));
        }
    }
    for field in object.keys() {
        if !spec.allowed_body_fields.contains(&field.as_str()) {
            return Err(Error::Config(format!(
                "{operation} body does not define field `{field}`"
            )));
        }
    }

    match operation {
        "analytics-activity" | "analytics-dialog" | "analytics-completion"
        | "analytics-generation" | "analytics-member-data" => {
            validate_analytics_body(operation, object)?;
        }
        "members-add" => validate_members_add(object)?,
        "models-custom-create" => validate_enum(object, "scope", &["all", "specified"], operation)?,
        "models-builtin-visibility" | "models-custom-visibility" | "models-visibility" => {
            validate_enum(object, "scope", &["all", "specified"], operation)?;
        }
        "skills-visibility-set" | "experts-visibility-set" => {
            validate_enum(object, "type", &["all", "scope_list"], operation)?;
        }
        "usage-default-quota-update" | "usage-members-quota-update"
        | "usage-department-quota-update" => {
            validate_enum(object, "limitType", &["limited", "unlimited"], operation)?;
        }
        _ => {}
    }
    Ok(())
}

pub fn validate_multipart_operation(
    operation: &str,
    fields: &HashMap<String, String>,
    has_package: bool,
) -> Result<()> {
    let spec = find_operation(operation)
        .ok_or_else(|| Error::Config(format!("unknown OpenAPI operation `{operation}`")))?;
    if spec.body_kind != OperationBodyKind::Multipart {
        return Err(Error::Config(format!("{operation} is not multipart")));
    }
    if fields.contains_key("package") {
        return Err(Error::Config(
            "multipart field `package` must be supplied as a file, not as text".into(),
        ));
    }
    for field in fields.keys() {
        if !spec.allowed_body_fields.contains(&field.as_str()) {
            return Err(Error::Config(format!(
                "{operation} multipart body does not define field `{field}`"
            )));
        }
    }
    for field in spec.required_body_fields {
        if !fields.contains_key(*field) {
            return Err(Error::Config(format!(
                "{operation} multipart body is missing required field `{field}`"
            )));
        }
    }
    if operation.ends_with("-update") && !has_package && fields.is_empty() {
        return Err(Error::Config(format!(
            "{operation} requires package or at least one multipart field"
        )));
    }
    if let Some(value) = fields.get("publishStatus") {
        if !matches!(value.as_str(), "draft" | "published") {
            return Err(Error::Config(
                "multipart field `publishStatus` must be `draft` or `published`".into(),
            ));
        }
    }
    if let Some(value) = fields.get("status") {
        if !matches!(value.as_str(), "enabled" | "disabled") {
            return Err(Error::Config(
                "multipart field `status` must be `enabled` or `disabled`".into(),
            ));
        }
    }
    Ok(())
}

#[rustfmt::skip]
fn validate_members_add(object: &Map<String, Value>) -> Result<()> {
    let members = object
        .get("members")
        .and_then(Value::as_array)
        .ok_or_else(|| Error::Config("members-add body field `members` must be an array".into()))?;
    for (index, member) in members.iter().enumerate() {
        let member = member
            .as_object()
            .ok_or_else(|| Error::Config(format!("members[{index}] must be an object")))?;
        for field in ["username", "email"] {
            if !member.contains_key(field) {
                return Err(Error::Config(format!(
                    "members[{index}] is missing required field `{field}`"
                )));
            }
        }
    }
    Ok(())
}

#[rustfmt::skip]
fn validate_analytics_body(operation: &str, object: &Map<String, Value>) -> Result<()> {
    validate_time_range(operation, object.get("timeRange"))?;
    for field in ["memberFilter", "clientFilter", "pluginFilter"] {
        let filter = object
            .get(field)
            .and_then(Value::as_object)
            .ok_or_else(|| Error::Config(format!("{operation} body field `{field}` must be an object")))?;
        validate_enum(filter, "type", &["all", "selected"], operation)?;
    }
    if operation == "analytics-member-data" {
        let pagination = object
            .get("pagination")
            .and_then(Value::as_object)
            .ok_or_else(|| Error::Config("analytics-member-data `pagination` must be an object".into()))?;
        for field in ["page", "pageSize"] {
            if !pagination.contains_key(field) {
                return Err(Error::Config(format!(
                    "analytics-member-data pagination is missing `{field}`"
                )));
            }
        }
    } else {
        validate_enum(object, "viewType", &["metrics", "trends"], operation)?;
    }
    if operation == "analytics-activity" {
        let options = object
            .get("activityOptions")
            .and_then(Value::as_object)
            .ok_or_else(|| Error::Config("analytics-activity `activityOptions` must be an object".into()))?;
        if !options.contains_key("distributionDimension") {
            return Err(Error::Config(
                "analytics-activity activityOptions is missing `distributionDimension`".into(),
            ));
        }
    }
    Ok(())
}

#[rustfmt::skip]
fn validate_time_range(operation: &str, value: Option<&Value>) -> Result<()> {
    let range = value
        .and_then(Value::as_object)
        .ok_or_else(|| Error::Config(format!("{operation} `timeRange` must be an object")))?;
    for field in ["startTime", "endTime"] {
        if !range.contains_key(field) {
            return Err(Error::Config(format!(
                "{operation} timeRange is missing `{field}`"
            )));
        }
    }
    Ok(())
}

#[rustfmt::skip]
fn validate_enum(
    object: &Map<String, Value>,
    field: &str,
    allowed: &[&str],
    operation: &str,
) -> Result<()> {
    let value = object
        .get(field)
        .and_then(Value::as_str)
        .ok_or_else(|| Error::Config(format!("{operation} `{field}` must be a string")))?;
    if !allowed.contains(&value) {
        return Err(Error::Config(format!(
            "{operation} `{field}` must be one of {}",
            allowed.join(", ")
        )));
    }
    Ok(())
}
