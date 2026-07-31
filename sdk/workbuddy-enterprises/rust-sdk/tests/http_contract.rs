use serde_json::{json, Value};
use std::collections::HashMap;
use std::io::{Read, Write};
use std::net::{TcpListener, TcpStream};
use std::thread::{self, JoinHandle};
use std::time::Duration;
use workbuddy_enterprise::{Client, ClientConfig, Error, SkillSource};

#[derive(Debug)]
struct CapturedRequest {
    method: String,
    target: String,
    headers: Vec<(String, String)>,
    body: Vec<u8>,
}

impl CapturedRequest {
    fn header(&self, name: &str) -> Option<&str> {
        self.headers
            .iter()
            .find(|(key, _)| key.eq_ignore_ascii_case(name))
            .map(|(_, value)| value.as_str())
    }
}

fn client(base_url: String) -> Client {
    Client::new(ClientConfig {
        enterprise_id: "ent-1".into(),
        client_id: None,
        client_secret: None,
        api_key: Some("test-application-key".into()),
        base_url,
        token_url: "http://127.0.0.1/unused-token-endpoint".into(),
        timeout: Duration::from_secs(3),
    })
    .expect("test client configuration is valid")
}

fn ok_response() -> String {
    r#"{"code":0,"msg":"OK","requestId":"rid","data":{}}"#.into()
}

fn spawn_server(responses: Vec<String>) -> (String, JoinHandle<Vec<CapturedRequest>>) {
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind test listener");
    let base_url = format!(
        "http://{}",
        listener.local_addr().expect("listener address")
    );
    let server = thread::spawn(move || {
        let mut requests = Vec::with_capacity(responses.len());
        for response in responses {
            let (mut stream, _) = listener.accept().expect("accept request");
            let request = read_request(&mut stream);
            write_response(&mut stream, &response);
            requests.push(request);
        }
        requests
    });
    (base_url, server)
}

fn read_request(stream: &mut TcpStream) -> CapturedRequest {
    stream
        .set_read_timeout(Some(Duration::from_secs(3)))
        .expect("set read timeout");
    let mut bytes = Vec::new();
    let header_end = loop {
        let mut chunk = [0_u8; 4096];
        let count = stream.read(&mut chunk).expect("read request");
        assert!(count > 0, "connection closed before HTTP headers");
        bytes.extend_from_slice(&chunk[..count]);
        if let Some(index) = bytes.windows(4).position(|window| window == b"\r\n\r\n") {
            break index + 4;
        }
    };

    let header_text = std::str::from_utf8(&bytes[..header_end]).expect("UTF-8 HTTP headers");
    let mut lines = header_text.split("\r\n");
    let request_line = lines.next().expect("request line");
    let mut request_parts = request_line.split_whitespace();
    let method = request_parts.next().expect("method").to_owned();
    let target = request_parts.next().expect("request target").to_owned();
    let headers: Vec<(String, String)> = lines
        .filter_map(|line| line.split_once(':'))
        .map(|(name, value)| (name.trim().to_owned(), value.trim().to_owned()))
        .collect();
    let content_length = headers
        .iter()
        .find(|(name, _)| name.eq_ignore_ascii_case("content-length"))
        .map(|(_, value)| value.parse::<usize>().expect("numeric content length"))
        .unwrap_or(0);

    while bytes.len() < header_end + content_length {
        let mut chunk = [0_u8; 4096];
        let count = stream.read(&mut chunk).expect("read request body");
        assert!(count > 0, "connection closed before request body");
        bytes.extend_from_slice(&chunk[..count]);
    }

    CapturedRequest {
        method,
        target,
        headers,
        body: bytes[header_end..header_end + content_length].to_vec(),
    }
}

fn write_response(stream: &mut TcpStream, body: &str) {
    let response = format!(
        "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
        body.len(),
        body
    );
    stream
        .write_all(response.as_bytes())
        .expect("write response");
}

#[test]
fn metrics_serializes_all_required_query_parameters() {
    let (base_url, server) = spawn_server(vec![ok_response()]);
    client(base_url)
        .analytics()
        .metrics("activeUserNum", "start", "end", 3600)
        .expect("metrics request succeeds");

    let requests = server.join().expect("server thread");
    assert_eq!(requests[0].method, "GET");
    assert_eq!(
        requests[0].target,
        "/enterprises/ent-1/metrics?queries=activeUserNum&range.start=start&range.end=end&range.step=3600"
    );
}

#[test]
fn category_filters_preserve_the_existing_string_api_and_wire_value() {
    let (base_url, server) = spawn_server(vec![ok_response(); 2]);
    let client = client(base_url);
    client
        .skills()
        .list(SkillSource::Custom, None, Some("10"), None, None, None)
        .expect("skills category query succeeds");
    client
        .experts()
        .list(SkillSource::Custom, None, Some("20"), None, None, None)
        .expect("experts category query succeeds");

    let requests = server.join().expect("server thread");
    assert_eq!(
        requests[0].target,
        "/enterprises/ent-1/openapi/skills?source=custom&categoryId=10"
    );
    assert_eq!(
        requests[1].target,
        "/enterprises/ent-1/openapi/experts?source=custom&categoryId=20"
    );
}

#[test]
fn users_page_reads_users_array() {
    let response = r#"{"code":0,"msg":"OK","data":{"totalCount":1,"users":[{"uid":"u1"}]}}"#.into();
    let (base_url, server) = spawn_server(vec![response]);
    let page = client(base_url)
        .users()
        .list(None, None, None, None, None, None, None, None, None)
        .expect("users request succeeds")
        .data;

    assert_eq!(page.total_count, Some(1));
    assert_eq!(page.items, vec![json!({"uid": "u1"})]);
    server.join().expect("server thread");
}

#[test]
fn dashboard_member_data_reads_members_and_nested_pagination() {
    let response = r#"{"code":0,"msg":"OK","data":{"members":[{"uid":"u1"}],"pagination":{"page":2,"pageSize":20,"total":41}}}"#.into();
    let (base_url, server) = spawn_server(vec![response]);
    let page = client(base_url)
        .analytics()
        .member_data(json!({
            "timeRange": {
                "startTime": "2026-01-01T00:00:00Z",
                "endTime": "2026-01-02T00:00:00Z"
            },
            "memberFilter": {"type": "all"},
            "clientFilter": {"type": "all"},
            "pluginFilter": {"type": "all"},
            "pagination": {"page": 1, "pageSize": 20}
        }))
        .expect("member data request succeeds")
        .data;

    assert_eq!(page.items, vec![json!({"uid": "u1"})]);
    assert_eq!(page.page, Some(2));
    assert_eq!(page.page_size, Some(20));
    assert_eq!(page.total_count, Some(41));
    server.join().expect("server thread");
}

#[test]
fn members_add_serializes_members_contract_body() {
    let (base_url, server) = spawn_server(vec![ok_response()]);
    let members = vec![json!({"username": "alice", "email": "alice@example.com"})];
    client(base_url)
        .members()
        .add(&members, Some(true))
        .expect("members add request succeeds");

    let requests = server.join().expect("server thread");
    let request = &requests[0];
    assert_eq!(request.method, "POST");
    assert_eq!(request.target, "/enterprises/ent-1/openapi/members/add");
    assert!(request
        .header("content-type")
        .is_some_and(|value| value.starts_with("application/json")));
    assert_eq!(
        serde_json::from_slice::<Value>(&request.body).expect("JSON request body"),
        json!({"members": members, "grantLicense": true})
    );
}

#[test]
fn license_and_usage_option_methods_serialize_all_yaml_selector_fields() {
    let (base_url, server) = spawn_server(vec![ok_response(); 5]);
    let client = client(base_url);
    client
        .licenses()
        .query_members_with_options(Some(&["u1"]), Some(&["alice"]))
        .expect("license query succeeds");
    client
        .licenses()
        .grant_with_options(Some(&["u1"]), Some(&["alice"]))
        .expect("license grant succeeds");
    client
        .licenses()
        .revoke_with_reason(&["u1"], Some("offboarding"))
        .expect("license revoke succeeds");
    client
        .usage()
        .query_members_with_options(
            Some(&["u1"]),
            Some(&["alice"]),
            Some(2),
            Some(50),
            Some("2026-01-01T00:00:00Z"),
            Some("2026-01-02T00:00:00Z"),
        )
        .expect("usage query succeeds");
    client
        .usage()
        .query_member_limits_with_options(Some(&["u1"]), Some(&["alice"]), Some(3), Some(25))
        .expect("usage limit query succeeds");

    let requests = server.join().expect("server thread");
    let bodies: Vec<Value> = requests
        .iter()
        .map(|request| serde_json::from_slice(&request.body).expect("JSON request body"))
        .collect();
    assert_eq!(
        bodies[0],
        json!({"userIds": ["u1"], "userNames": ["alice"]})
    );
    assert_eq!(
        bodies[1],
        json!({"userIds": ["u1"], "userNames": ["alice"]})
    );
    assert_eq!(
        bodies[2],
        json!({"userIds": ["u1"], "reason": "offboarding"})
    );
    assert_eq!(
        bodies[3],
        json!({
            "userIds": ["u1"],
            "userNames": ["alice"],
            "pageNum": 2,
            "pageSize": 50,
            "startTime": "2026-01-01T00:00:00Z",
            "endTime": "2026-01-02T00:00:00Z"
        })
    );
    assert_eq!(
        bodies[4],
        json!({"userIds": ["u1"], "userNames": ["alice"], "pageNum": 3, "pageSize": 25})
    );
}

#[test]
fn model_visibility_serializes_scope_and_allow_lists() {
    let (base_url, server) = spawn_server(vec![ok_response()]);
    client(base_url)
        .models()
        .set_builtin_visibility("m1", "specified", Some(&["u1", "u2"]), Some(&["g1"]))
        .expect("model visibility request succeeds");

    let requests = server.join().expect("server thread");
    let request = &requests[0];
    assert_eq!(
        request.target,
        "/enterprises/ent-1/openapi/models/builtin/m1/visibility"
    );
    assert_eq!(
        serde_json::from_slice::<Value>(&request.body).expect("JSON request body"),
        json!({"scope": "specified", "userIds": ["u1", "u2"], "groupIds": ["g1"]})
    );
}

#[test]
fn post_empty_sends_no_json_body_or_content_type() {
    let (base_url, server) = spawn_server(vec![ok_response()]);
    client(base_url)
        .users()
        .delete("u1")
        .expect("delete request succeeds");

    let requests = server.join().expect("server thread");
    let request = &requests[0];
    assert_eq!(request.method, "POST");
    assert_eq!(request.target, "/enterprises/ent-1/users/u1/delete");
    assert!(request.body.is_empty());
    assert!(request.header("content-type").is_none());
}

#[test]
fn path_parameters_are_encoded_as_single_segments() {
    let (base_url, server) = spawn_server(vec![ok_response(); 6]);
    let client = client(base_url);
    let identifier = "id/with?hash#percent%中";

    client
        .users()
        .update(identifier, json!({}))
        .expect("user update succeeds");
    client.groups().get(identifier).expect("group get succeeds");
    client
        .models()
        .get_custom(identifier)
        .expect("custom model get succeeds");
    client.skills().get(identifier).expect("skill get succeeds");
    client
        .experts()
        .get(identifier)
        .expect("expert get succeeds");
    client
        .usage()
        .update_department_quota(identifier, json!({"limitType": "unlimited"}))
        .expect("department quota request succeeds");

    let encoded = "id%2Fwith%3Fhash%23percent%25%E4%B8%AD";
    for request in server.join().expect("server thread") {
        assert!(request.target.contains(encoded), "{}", request.target);
        assert!(!request.target.contains('#'));
        assert!(!request.target.contains('中'));
    }
}

#[test]
fn skill_and_expert_updates_reject_empty_multipart_requests() {
    let client = client("http://127.0.0.1:9".into());
    let empty = HashMap::new();
    assert!(matches!(
        client.skills().update("sk-1", None, empty.clone()),
        Err(Error::Config(_))
    ));
    assert!(matches!(
        client.experts().update("ex-1", None, empty),
        Err(Error::Config(_))
    ));
}
