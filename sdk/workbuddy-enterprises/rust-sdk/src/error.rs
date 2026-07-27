
use thiserror::Error;

pub type Result<T> = std::result::Result<T, Error>;

#[derive(Debug, Error)]
pub enum Error {
    #[error("configuration error: {0}")]
    Config(String),

    #[error("auth error: {0}")]
    Auth(String),

    #[error("http {status}: {message}")]
    Http {
        status: u16,
        message: String,
        code: Option<i64>,
        request_id: Option<String>,
    },

    #[error("api code={code}: {message}")]
    Api {
        code: i64,
        message: String,
        request_id: Option<String>,
    },

    #[error("timeout: {0}")]
    Timeout(String),

    #[error("transport: {0}")]
    Transport(String),

    #[error("invalid json: {0}")]
    Json(String),

    #[error("io: {0}")]
    Io(String),
}

impl Error {
    pub fn request_id(&self) -> Option<&str> {
        match self {
            Error::Http { request_id, .. } | Error::Api { request_id, .. } => {
                request_id.as_deref()
            }
            _ => None,
        }
    }
}
