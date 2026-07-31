use serde_json::{json, Value};
use std::fs;
use std::io::{Read, Write};
use std::net::{TcpListener, TcpStream};
use std::path::{Path, PathBuf};
use std::process::{Command, Output, Stdio};
use std::sync::atomic::{AtomicU64, Ordering};
use std::thread::{self, JoinHandle};
use std::time::Duration;

const WORKBUDDY_ENV: &[&str] = &[
    "WORKBUDDY_ENTERPRISE_ID",
    "WORKBUDDY_CLIENT_ID",
    "WORKBUDDY_CLIENT_SECRET",
    "WORKBUDDY_API_KEY",
    "WORKBUDDY_BASE_URL",
    "WORKBUDDY_TOKEN_URL",
];

static NEXT_TEMP_FILE: AtomicU64 = AtomicU64::new(0);

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

struct TempFile {
    path: PathBuf,
}

impl TempFile {
    fn new(label: &str, contents: &[u8]) -> Self {
        let sequence = NEXT_TEMP_FILE.fetch_add(1, Ordering::Relaxed);
        let path = std::env::temp_dir().join(format!(
            "workbuddy-cli-contract-{}-{sequence}-{label}",
            std::process::id()
        ));
        fs::write(&path, contents).expect("write CLI test fixture");
        Self { path }
    }

    fn path(&self) -> &Path {
        &self.path
    }
}

impl Drop for TempFile {
    fn drop(&mut self) {
        let _ = fs::remove_file(&self.path);
    }
}

fn command(base_url: &str) -> Command {
    let mut command = Command::new(env!("CARGO_BIN_EXE_workbuddy"));
    for &name in WORKBUDDY_ENV {
        command.env_remove(name);
    }
    command
        .env("WORKBUDDY_ENTERPRISE_ID", "ent-1")
        .env("WORKBUDDY_API_KEY", "test-application-key")
        .env("WORKBUDDY_BASE_URL", base_url)
        .env(
            "WORKBUDDY_TOKEN_URL",
            "http://127.0.0.1/unused-token-endpoint",
        );
    command
}

fn run_with_stdin(mut command: Command, stdin: &[u8]) -> Output {
    let mut child = command
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .expect("spawn workbuddy CLI");
    child
        .stdin
        .take()
        .expect("CLI stdin pipe")
        .write_all(stdin)
        .expect("write CLI stdin");
    child.wait_with_output().expect("wait for workbuddy CLI")
}

fn ok_response() -> String {
    r#"{"code":0,"msg":"OK","requestId":"rid","data":{}}"#.into()
}

fn spawn_server() -> (String, JoinHandle<CapturedRequest>) {
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind CLI test listener");
    let base_url = format!(
        "http://{}",
        listener.local_addr().expect("CLI test listener address")
    );
    let server = thread::spawn(move || {
        let (mut stream, _) = listener.accept().expect("accept CLI request");
        let request = read_request(&mut stream);
        write_response(&mut stream, &ok_response());
        request
    });
    (base_url, server)
}

fn read_request(stream: &mut TcpStream) -> CapturedRequest {
    stream
        .set_read_timeout(Some(Duration::from_secs(3)))
        .expect("set CLI request timeout");
    let mut bytes = Vec::new();
    let header_end = loop {
        let mut chunk = [0_u8; 4096];
        let count = stream.read(&mut chunk).expect("read CLI request");
        assert!(count > 0, "connection closed before HTTP headers");
        bytes.extend_from_slice(&chunk[..count]);
        if let Some(index) = bytes.windows(4).position(|window| window == b"\r\n\r\n") {
            break index + 4;
        }
    };

    let header_text = std::str::from_utf8(&bytes[..header_end]).expect("UTF-8 HTTP headers");
    let mut lines = header_text.split("\r\n");
    let request_line = lines.next().expect("CLI request line");
    let mut request_parts = request_line.split_whitespace();
    let method = request_parts.next().expect("CLI request method").to_owned();
    let target = request_parts.next().expect("CLI request target").to_owned();
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
        let count = stream.read(&mut chunk).expect("read CLI request body");
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
        .expect("write CLI response");
}

fn stderr(output: &Output) -> String {
    String::from_utf8_lossy(&output.stderr).into_owned()
}

#[test]
fn operations_lists_the_complete_registry_without_credentials() {
    let mut command = Command::new(env!("CARGO_BIN_EXE_workbuddy"));
    for &name in WORKBUDDY_ENV {
        command.env_remove(name);
    }
    let output = command
        .arg("operations")
        .output()
        .expect("run operations command");

    assert!(output.status.success(), "{}", stderr(&output));
    let stdout = String::from_utf8(output.stdout).expect("UTF-8 operations output");
    assert_eq!(stdout.lines().filter(|line| !line.is_empty()).count(), 73);
}

#[test]
fn generic_get_sends_encoded_path_and_required_query() {
    let (base_url, server) = spawn_server();
    let output = command(&base_url)
        .args([
            "api",
            "skills-visibility-get",
            "--param",
            "skillRef=a/b?中",
            "--query",
            "source=custom",
        ])
        .output()
        .expect("run generic GET");

    assert!(output.status.success(), "{}", stderr(&output));
    let request = server.join().expect("CLI GET server thread");
    assert_eq!(request.method, "GET");
    assert_eq!(
        request.target,
        "/enterprises/ent-1/openapi/skills/a%2Fb%3F%E4%B8%AD/visibility?source=custom"
    );
    assert_eq!(
        request.header("authorization"),
        Some("Bearer test-application-key")
    );
}

#[test]
fn read_only_json_post_accepts_stdin_without_yes() {
    let body = json!({
        "timeRange": {
            "startTime": "2026-01-01T00:00:00Z",
            "endTime": "2026-01-02T00:00:00Z"
        },
        "memberFilter": {"type": "all"},
        "clientFilter": {"type": "all"},
        "pluginFilter": {"type": "all"},
        "viewType": "metrics",
        "activityOptions": {"distributionDimension": "client"}
    });
    let (base_url, server) = spawn_server();
    let mut cli = command(&base_url);
    cli.args(["api", "analytics-activity", "--body-file", "-"]);
    let output = run_with_stdin(cli, body.to_string().as_bytes());

    assert!(output.status.success(), "{}", stderr(&output));
    let request = server.join().expect("CLI JSON server thread");
    assert_eq!(request.method, "POST");
    assert_eq!(
        request.target,
        "/enterprises/ent-1/dashboard/analytics/activity"
    );
    assert!(request
        .header("content-type")
        .is_some_and(|value| value.starts_with("application/json")));
    assert_eq!(
        serde_json::from_slice::<Value>(&request.body).expect("CLI JSON body"),
        body
    );
}

#[test]
fn mutation_without_yes_exits_before_reading_body_or_contacting_transport() {
    let output = command("http://127.0.0.1:9")
        .args(["api", "members-add", "--body-file", "-"])
        .output()
        .expect("run blocked mutation");

    assert!(!output.status.success());
    let stderr = stderr(&output);
    assert!(stderr.contains("without --yes"), "{stderr}");
    assert!(!stderr.contains("transport"), "{stderr}");
}

#[test]
fn generic_multipart_sends_fields_file_inline_field_and_package() {
    let fields = TempFile::new("fields.json", br#"{"displayName":"Skill"}"#);
    let package = TempFile::new("skill.zip", b"skill-package-bytes");
    let (base_url, server) = spawn_server();
    let output = command(&base_url)
        .args([
            "api",
            "skills-create",
            "--field",
            "name=skill",
            "--fields-file",
        ])
        .arg(fields.path())
        .arg("--package")
        .arg(package.path())
        .arg("--yes")
        .output()
        .expect("run generic multipart mutation");

    assert!(output.status.success(), "{}", stderr(&output));
    let request = server.join().expect("CLI multipart server thread");
    assert_eq!(request.method, "POST");
    assert_eq!(request.target, "/enterprises/ent-1/openapi/skills");
    assert!(request
        .header("content-type")
        .is_some_and(|value| value.starts_with("multipart/form-data; boundary=")));
    let body = String::from_utf8_lossy(&request.body);
    assert!(body.contains("name=\"name\""), "{body}");
    assert!(body.contains("skill"), "{body}");
    assert!(body.contains("name=\"displayName\""), "{body}");
    assert!(body.contains("Skill"), "{body}");
    assert!(body.contains("name=\"package\""), "{body}");
    assert!(body.contains("skill-package-bytes"), "{body}");
}
