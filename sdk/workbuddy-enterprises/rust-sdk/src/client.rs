use crate::auth::{ClientConfig, TokenProvider, DEFAULT_BASE_URL, DEFAULT_TOKEN_URL};
use crate::error::{Error, Result};
use crate::operations::{validate_json_operation, validate_multipart_operation};
use crate::resources::{
    AnalyticsResource, EnterpriseResource, ExpertCategoriesResource, ExpertsResource,
    GroupsResource, LicensesResource, MembersResource, ModelsResource, SkillCategoriesResource,
    SkillsResource, UsageResource, UsersResource,
};
use crate::response::{parse_page, ApiResponse, Page, WireEnvelope};
use reqwest::blocking::{multipart, Client as HttpClient};
use reqwest::header::{HeaderMap, HeaderValue, AUTHORIZATION};
use serde_json::Value;
use std::collections::HashMap;
use std::path::Path;
use std::time::Duration;
use url::Url;

pub struct Client {
    config: ClientConfig,
    http: HttpClient,
    tokens: std::sync::Mutex<TokenProvider>,
}

impl Client {
    pub fn new(config: ClientConfig) -> Result<Self> {
        config.validate()?;
        let http = HttpClient::builder()
            .timeout(config.timeout)
            .build()
            .map_err(|e| Error::Transport(e.to_string()))?;
        let tokens = TokenProvider::new(config.clone(), http.clone());
        Ok(Self {
            config,
            http,
            tokens: std::sync::Mutex::new(tokens),
        })
    }

    pub fn from_client_credentials(
        client_id: impl Into<String>,
        client_secret: impl Into<String>,
        enterprise_id: impl Into<String>,
    ) -> Result<Self> {
        Self::new(ClientConfig {
            enterprise_id: enterprise_id.into(),
            client_id: Some(client_id.into()),
            client_secret: Some(client_secret.into()),
            api_key: None,
            base_url: DEFAULT_BASE_URL.into(),
            token_url: DEFAULT_TOKEN_URL.into(),
            timeout: Duration::from_secs(30),
        })
    }

    pub fn from_api_key(
        api_key: impl Into<String>,
        enterprise_id: impl Into<String>,
    ) -> Result<Self> {
        Self::new(ClientConfig {
            enterprise_id: enterprise_id.into(),
            client_id: None,
            client_secret: None,
            api_key: Some(api_key.into()),
            base_url: DEFAULT_BASE_URL.into(),
            token_url: DEFAULT_TOKEN_URL.into(),
            timeout: Duration::from_secs(30),
        })
    }

    pub fn from_env() -> Result<Self> {
        Self::new(ClientConfig::from_env()?)
    }

    pub fn enterprise_id(&self) -> &str {
        &self.config.enterprise_id
    }

    pub fn base_url(&self) -> &str {
        &self.config.base_url
    }

    pub fn enterprise(&self) -> EnterpriseResource<'_> {
        EnterpriseResource { client: self }
    }
    pub fn users(&self) -> UsersResource<'_> {
        UsersResource { client: self }
    }
    pub fn members(&self) -> MembersResource<'_> {
        MembersResource { client: self }
    }
    pub fn licenses(&self) -> LicensesResource<'_> {
        LicensesResource { client: self }
    }
    pub fn usage(&self) -> UsageResource<'_> {
        UsageResource { client: self }
    }
    pub fn groups(&self) -> GroupsResource<'_> {
        GroupsResource { client: self }
    }
    pub fn models(&self) -> ModelsResource<'_> {
        ModelsResource { client: self }
    }
    pub fn skills(&self) -> SkillsResource<'_> {
        SkillsResource { client: self }
    }
    pub fn skill_categories(&self) -> SkillCategoriesResource<'_> {
        SkillCategoriesResource { client: self }
    }
    pub fn experts(&self) -> ExpertsResource<'_> {
        ExpertsResource { client: self }
    }
    pub fn expert_categories(&self) -> ExpertCategoriesResource<'_> {
        ExpertCategoriesResource { client: self }
    }
    pub fn analytics(&self) -> AnalyticsResource<'_> {
        AnalyticsResource { client: self }
    }

    pub(crate) fn enterprise_path(&self, suffix: &str) -> String {
        let eid = encode_path_segment(&self.config.enterprise_id);
        format!("/enterprises/{eid}{suffix}")
    }

    /// Executes a known Enterprise OpenAPI GET suffix under this client's enterprise.
    /// Prefer resource methods when their typed convenience signature covers the request.
    pub fn get_json(&self, suffix: &str, query: &[(String, String)]) -> Result<ApiResponse<Value>> {
        self.request("GET", suffix, query, None, None)
    }

    /// Executes a known Enterprise OpenAPI POST suffix with no request body.
    pub fn post_empty(
        &self,
        suffix: &str,
        query: &[(String, String)],
    ) -> Result<ApiResponse<Value>> {
        self.request("POST", suffix, query, None, None)
    }

    /// Executes a known Enterprise OpenAPI POST suffix with an application/json body.
    pub(crate) fn post_json(
        &self,
        suffix: &str,
        query: &[(String, String)],
        body: Value,
    ) -> Result<ApiResponse<Value>> {
        self.request("POST", suffix, query, Some(body), None)
    }

    /// Validates a registry operation's JSON body contract, then sends it to the supplied suffix.
    pub fn post_operation_json(
        &self,
        operation: &str,
        suffix: &str,
        query: &[(String, String)],
        body: Value,
    ) -> Result<ApiResponse<Value>> {
        validate_json_operation(operation, &body)?;
        self.post_json(suffix, query, body)
    }

    /// Sends a multipart form after a resource or registry helper validates it.
    pub(crate) fn post_multipart(
        &self,
        suffix: &str,
        fields: &HashMap<String, String>,
        file_path: Option<&Path>,
    ) -> Result<ApiResponse<Value>> {
        let mut form = multipart::Form::new();
        for (k, v) in fields {
            form = form.text(k.clone(), v.clone());
        }
        if let Some(path) = file_path {
            form = form
                .file("package", path)
                .map_err(|e| Error::Io(format!("open package file: {e}")))?;
        }
        self.request("POST", suffix, &[], None, Some(form))
    }

    /// Validates a registry operation's multipart fields, then sends them to the supplied suffix.
    pub fn post_operation_multipart(
        &self,
        operation: &str,
        suffix: &str,
        fields: &HashMap<String, String>,
        file_path: Option<&Path>,
    ) -> Result<ApiResponse<Value>> {
        validate_multipart_operation(operation, fields, file_path.is_some())?;
        self.post_multipart(suffix, fields, file_path)
    }

    pub(crate) fn get_page(
        &self,
        suffix: &str,
        query: &[(String, String)],
    ) -> Result<ApiResponse<Page<Value>>> {
        let resp = self.get_json(suffix, query)?;
        Ok(ApiResponse {
            data: parse_page(resp.data),
            code: resp.code,
            message: resp.message,
            request_id: resp.request_id,
            raw: resp.raw,
        })
    }

    fn request(
        &self,
        method: &str,
        suffix: &str,
        query: &[(String, String)],
        json_body: Option<Value>,
        multipart_form: Option<multipart::Form>,
    ) -> Result<ApiResponse<Value>> {
        let token = self
            .tokens
            .lock()
            .map_err(|_| Error::Transport("token lock poisoned".into()))?
            .get_token()?;

        let path = self.enterprise_path(suffix);
        let mut url = Url::parse(&format!("{}{}", self.config.base_url, path))
            .map_err(|e| Error::Config(format!("invalid url: {e}")))?;
        if query.iter().any(|(_, value)| !value.is_empty()) {
            let mut pairs = url.query_pairs_mut();
            for (k, v) in query {
                if !v.is_empty() {
                    pairs.append_pair(k, v);
                }
            }
        }

        let mut headers = HeaderMap::new();
        headers.insert(
            AUTHORIZATION,
            HeaderValue::from_str(&format!("Bearer {token}"))
                .map_err(|e| Error::Auth(format!("invalid token header: {e}")))?,
        );
        headers.insert("Accept", HeaderValue::from_static("application/json"));

        let builder = match method {
            "GET" => self.http.get(url),
            "POST" => self.http.post(url),
            other => return Err(Error::Config(format!("unsupported method {other}"))),
        }
        .headers(headers);

        let resp = if let Some(form) = multipart_form {
            builder.multipart(form).send()
        } else if let Some(body) = json_body {
            builder.json(&body).send()
        } else {
            builder.send()
        }
        .map_err(|e| {
            if e.is_timeout() {
                Error::Timeout("request timed out".into())
            } else {
                Error::Transport(e.to_string())
            }
        })?;

        let status = resp.status();
        let header_rid = resp
            .headers()
            .get("x-request-id")
            .or_else(|| resp.headers().get("X-Request-Id"))
            .and_then(|v| v.to_str().ok())
            .map(|s| s.to_string());

        let text = resp.text().map_err(|e| Error::Transport(e.to_string()))?;
        if text.trim().is_empty() {
            if !status.is_success() {
                return Err(Error::Http {
                    status: status.as_u16(),
                    message: format!("HTTP {}", status.as_u16()),
                    code: None,
                    request_id: header_rid,
                });
            }
            return Ok(ApiResponse {
                data: Value::Null,
                code: 0,
                message: "OK".into(),
                request_id: header_rid,
                raw: None,
            });
        }

        let body: Value =
            serde_json::from_str(&text).map_err(|e| Error::Json(format!("{e}; body={text}")))?;

        if !status.is_success() {
            let env: WireEnvelope = serde_json::from_value(body.clone()).unwrap_or(WireEnvelope {
                code: None,
                msg: None,
                message: None,
                request_id: None,
                data: None,
            });
            return Err(Error::Http {
                status: status.as_u16(),
                message: env
                    .msg
                    .or(env.message)
                    .unwrap_or_else(|| format!("HTTP {}", status.as_u16())),
                code: env.code,
                request_id: env.request_id.or(header_rid),
            });
        }

        let env: WireEnvelope =
            serde_json::from_value(body.clone()).map_err(|e| Error::Json(e.to_string()))?;
        let code = env.code.unwrap_or(0);
        let message = env.msg.or(env.message).unwrap_or_else(|| "OK".to_string());
        let request_id = env.request_id.or(header_rid);
        if code != 0 {
            return Err(Error::Api {
                code,
                message,
                request_id,
            });
        }
        Ok(ApiResponse {
            data: env.data.unwrap_or(Value::Null),
            code,
            message,
            request_id,
            raw: Some(body),
        })
    }
}

pub(crate) fn push_q(q: &mut Vec<(String, String)>, key: &str, value: Option<String>) {
    if let Some(v) = value {
        if !v.is_empty() {
            q.push((key.to_string(), v));
        }
    }
}

pub(crate) fn push_qi(q: &mut Vec<(String, String)>, key: &str, value: Option<i64>) {
    if let Some(v) = value {
        q.push((key.to_string(), v.to_string()));
    }
}

pub(crate) fn push_qb(q: &mut Vec<(String, String)>, key: &str, value: Option<bool>) {
    if let Some(v) = value {
        q.push((key.to_string(), if v { "true" } else { "false" }.into()));
    }
}

pub fn encode_path_segment(s: &str) -> String {
    let mut out = String::with_capacity(s.len());
    for b in s.bytes() {
        match b {
            b'A'..=b'Z' | b'a'..=b'z' | b'0'..=b'9' | b'-' | b'_' | b'.' | b'~' => {
                out.push(b as char)
            }
            _ => out.push_str(&format!("%{b:02X}")),
        }
    }
    out
}
