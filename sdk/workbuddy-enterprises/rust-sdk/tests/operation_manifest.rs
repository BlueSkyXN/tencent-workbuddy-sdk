use serde_json::json;
use std::collections::HashSet;
use workbuddy_enterprise::{
    find_operation, validate_json_operation, OperationBodyKind, OPENAPI_OPERATIONS, OPERATION_SPECS,
};

#[rustfmt::skip]
#[test]
fn cli_operation_specs_cover_the_full_machine_readable_registry() {
    assert_eq!(OPENAPI_OPERATIONS.len(), 73);
    assert_eq!(OPERATION_SPECS.len(), OPENAPI_OPERATIONS.len());

    let mut names = HashSet::new();
    let mut mapped = HashSet::new();
    for spec in OPERATION_SPECS {
        assert!(names.insert(spec.name), "duplicate operation name: {}", spec.name);
        let path = format!("/enterprises/{{enterpriseId}}{}", spec.suffix_template);
        assert!(
            OPENAPI_OPERATIONS.contains(&(spec.method, path.as_str())),
            "{} {} is absent from OPENAPI_OPERATIONS",
            spec.method,
            path
        );
        assert!(mapped.insert((spec.method, path)));
    }
    assert_eq!(mapped.len(), OPENAPI_OPERATIONS.len());
}

#[test]
fn manifest_marks_read_and_write_posts_by_operation_semantics() {
    assert!(!find_operation("analytics-activity").unwrap().write);
    assert!(!find_operation("licenses-members-query").unwrap().write);
    assert!(!find_operation("usage-members-detail").unwrap().write);
    assert!(find_operation("members-add").unwrap().write);
    assert!(find_operation("skills-delete").unwrap().write);
}

#[test]
fn json_contract_validation_enforces_required_nested_and_known_fields() {
    let missing_model_field = json!({
        "displayName": "M",
        "provider": "openai",
        "baseUrl": "https://example.test",
        "apiKey": "secret",
        "scope": "all"
    });
    assert!(validate_json_operation("models-custom-create", &missing_model_field).is_err());

    let invalid_member = json!({"members": [{"username": "alice"}]});
    assert!(validate_json_operation("members-add", &invalid_member).is_err());

    let activity = json!({
        "timeRange": {"startTime": "2026-01-01T00:00:00Z", "endTime": "2026-01-02T00:00:00Z"},
        "memberFilter": {"type": "all"},
        "clientFilter": {"type": "all"},
        "pluginFilter": {"type": "all"},
        "viewType": "metrics",
        "activityOptions": {"distributionDimension": "client"}
    });
    assert!(validate_json_operation("analytics-activity", &activity).is_ok());
    assert!(validate_json_operation("analytics-activity", &json!({"unknown": true})).is_err());
    assert!(validate_json_operation("users-delete", &json!({})).is_err());
    assert!(validate_json_operation("skills-create", &json!({})).is_err());

    assert_eq!(
        find_operation("skills-create").unwrap().body_kind,
        OperationBodyKind::Multipart
    );
}
