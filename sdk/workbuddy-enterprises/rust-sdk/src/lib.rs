
//! Unofficial WorkBuddy / CodeBuddy Enterprise OpenAPI Rust SDK.
//!
//! # Build policy
//! This crate is intended to be built in CI. See repository
//! `docs/local-disk-and-ci-builds.md`.

pub mod auth;
pub mod client;
pub mod error;
pub mod resources;
pub mod response;
pub mod types;

pub use auth::{
    extract_enterprise_ids_from_token, ClientConfig, DEFAULT_BASE_URL, DEFAULT_TOKEN_URL,
};
pub use client::Client;
pub use error::{Error, Result};
pub use response::{ApiResponse, Page};
pub use types::{PublishStatus, SkillSource, VisibilityType};

pub const VERSION: &str = env!("CARGO_PKG_VERSION");
