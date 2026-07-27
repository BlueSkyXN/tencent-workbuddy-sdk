use crate::error::{Error, Result};
use base64::{engine::general_purpose::URL_SAFE_NO_PAD, Engine as _};
use reqwest::blocking::Client as HttpClient;
use serde::Deserialize;
use serde_json::Value;
use std::time::{Duration, Instant};

pub const DEFAULT_BASE_URL: &str = "https://api.copilot.tencent.com/api/v1";
pub const DEFAULT_TOKEN_URL: &str = "https://copilot.tencent.com/oauth2/token";

#[derive(Debug, Clone)]
pub struct ClientConfig {
    pub enterprise_id: String,
    pub client_id: Option<String>,
    pub client_secret: Option<String>,
    pub api_key: Option<String>,
    pub base_url: String,
    pub token_url: String,
    pub timeout: Duration,
}

impl ClientConfig {
    pub fn validate(&self) -> Result<()> {
        if self.enterprise_id.trim().is_empty() {
            return Err(Error::Config(
                "enterprise_id is required (WORKBUDDY_ENTERPRISE_ID)".into(),
            ));
        }
        let has_oauth = self.client_id.as_ref().is_some_and(|s| !s.is_empty())
            && self.client_secret.as_ref().is_some_and(|s| !s.is_empty());
        let has_key = self.api_key.as_ref().is_some_and(|s| !s.is_empty());
        if has_oauth && has_key {
            return Err(Error::Config(
                "provide either OAuth client credentials or api_key, not both".into(),
            ));
        }
        if !has_oauth && !has_key {
            return Err(Error::Config(
                "provide OAuth client_id/client_secret or enterprise api_key".into(),
            ));
        }
        Ok(())
    }

    pub fn from_env() -> Result<Self> {
        use std::env;
        let mut cfg = Self {
            enterprise_id: env::var("WORKBUDDY_ENTERPRISE_ID").unwrap_or_default(),
            client_id: env::var("WORKBUDDY_CLIENT_ID")
                .ok()
                .filter(|s| !s.is_empty()),
            client_secret: env::var("WORKBUDDY_CLIENT_SECRET")
                .ok()
                .filter(|s| !s.is_empty()),
            api_key: env::var("WORKBUDDY_API_KEY").ok().filter(|s| !s.is_empty()),
            base_url: env::var("WORKBUDDY_BASE_URL").unwrap_or_else(|_| DEFAULT_BASE_URL.into()),
            token_url: env::var("WORKBUDDY_TOKEN_URL").unwrap_or_else(|_| DEFAULT_TOKEN_URL.into()),
            timeout: Duration::from_secs(30),
        };
        cfg.base_url = cfg.base_url.trim_end_matches('/').to_string();
        cfg.validate()?;
        Ok(cfg)
    }
}

#[derive(Debug, Deserialize)]
struct TokenResponse {
    access_token: String,
    expires_in: Option<u64>,
}

pub(crate) struct TokenProvider {
    config: ClientConfig,
    http: HttpClient,
    cached: Option<(String, Instant)>,
}

impl TokenProvider {
    pub fn new(config: ClientConfig, http: HttpClient) -> Self {
        Self {
            config,
            http,
            cached: None,
        }
    }

    pub fn get_token(&mut self) -> Result<String> {
        if let Some(key) = &self.config.api_key {
            return Ok(key.clone());
        }
        if let Some((token, exp)) = &self.cached {
            if Instant::now() < *exp {
                return Ok(token.clone());
            }
        }
        let client_id = self
            .config
            .client_id
            .as_ref()
            .ok_or_else(|| Error::Config("client_id missing".into()))?;
        let client_secret = self
            .config
            .client_secret
            .as_ref()
            .ok_or_else(|| Error::Config("client_secret missing".into()))?;

        let resp = self
            .http
            .post(&self.config.token_url)
            .form(&[
                ("grant_type", "client_credentials"),
                ("client_id", client_id.as_str()),
                ("client_secret", client_secret.as_str()),
            ])
            .header("Accept", "application/json")
            .send()
            .map_err(|e| {
                if e.is_timeout() {
                    Error::Timeout("token request timed out".into())
                } else {
                    Error::Auth(format!("token request failed: {e}"))
                }
            })?;

        let status = resp.status();
        let body: Value = resp.json().map_err(|e| Error::Json(e.to_string()))?;
        if !status.is_success() {
            return Err(Error::Auth(format!(
                "token HTTP {}: {}",
                status.as_u16(),
                body
            )));
        }
        let parsed: TokenResponse = serde_json::from_value(body)
            .map_err(|e| Error::Auth(format!("invalid token response: {e}")))?;
        let ttl = parsed.expires_in.unwrap_or(3600).saturating_sub(30);
        self.cached = Some((
            parsed.access_token.clone(),
            Instant::now() + Duration::from_secs(ttl),
        ));
        Ok(parsed.access_token)
    }
}

/// Opt-in helper: parse `ent-member:{id}` roles from a JWT access token.
pub fn extract_enterprise_ids_from_token(token: &str) -> Vec<String> {
    let mut out = Vec::new();
    let parts: Vec<_> = token.split('.').collect();
    if parts.len() < 2 {
        return out;
    }
    let Ok(bytes) = URL_SAFE_NO_PAD.decode(parts[1]) else {
        return out;
    };
    let Ok(v) = serde_json::from_slice::<Value>(&bytes) else {
        return out;
    };
    let roles = v
        .pointer("/realm_access/roles")
        .or_else(|| v.get("roles"))
        .and_then(|r| r.as_array())
        .cloned()
        .unwrap_or_default();
    for role in roles {
        if let Some(s) = role.as_str() {
            if let Some(rest) = s.strip_prefix("ent-member:") {
                let id = rest.trim();
                if !id.is_empty() && !out.iter().any(|x| x == id) {
                    out.push(id.to_string());
                }
            }
        }
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rejects_both_auth_modes() {
        let cfg = ClientConfig {
            enterprise_id: "e".into(),
            client_id: Some("c".into()),
            client_secret: Some("s".into()),
            api_key: Some("pt_x".into()),
            base_url: DEFAULT_BASE_URL.into(),
            token_url: DEFAULT_TOKEN_URL.into(),
            timeout: Duration::from_secs(5),
        };
        assert!(cfg.validate().is_err());
    }

    #[test]
    fn jwt_role_parse() {
        // header.payload.sig with payload {"realm_access":{"roles":["ent-member:abc"]}}
        let payload = URL_SAFE_NO_PAD.encode(br#"{"realm_access":{"roles":["ent-member:abc"]}}"#);
        let token = format!("aaa.{payload}.bbb");
        assert_eq!(extract_enterprise_ids_from_token(&token), vec!["abc"]);
    }
}
