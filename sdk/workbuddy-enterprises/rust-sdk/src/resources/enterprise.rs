use crate::client::Client;
use crate::error::Result;
use crate::response::ApiResponse;
use serde_json::Value;

pub struct EnterpriseResource<'a> {
    pub(crate) client: &'a Client,
}

impl EnterpriseResource<'_> {
    pub fn get_info(&self) -> Result<ApiResponse<Value>> {
        self.client.get_json("/info", &[])
    }

    pub fn get_license(&self) -> Result<ApiResponse<Value>> {
        self.client.get_json("/license", &[])
    }
}
