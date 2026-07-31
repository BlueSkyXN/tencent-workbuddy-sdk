use clap::{Parser, Subcommand, ValueEnum};
use serde_json::{json, Value};
use std::collections::HashMap;
use std::fs;
use std::io::{self, Read};
use std::path::{Path, PathBuf};
use std::process::ExitCode;
use workbuddy_enterprise::{
    encode_path_segment, find_operation, Client, OperationBodyKind, OperationSpec, SkillSource,
};

#[derive(Debug, Parser)]
#[command(
    name = "workbuddy",
    about = "Unofficial WorkBuddy / CodeBuddy Enterprise OpenAPI CLI (CI-built binary)",
    version
)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Debug, Subcommand)]
enum Commands {
    /// Print SDK/CLI version
    Version,
    /// List every named operation in the 73-operation OpenAPI registry.
    Operations,
    /// Enterprise info / license
    Enterprise {
        #[command(subcommand)]
        cmd: EnterpriseCmd,
    },
    /// OpenAPI members
    Members {
        #[command(subcommand)]
        cmd: MembersCmd,
    },
    /// License overview / grant / revoke / query
    Licenses {
        #[command(subcommand)]
        cmd: LicensesCmd,
    },
    /// Usage quota reads
    Usage {
        #[command(subcommand)]
        cmd: UsageCmd,
    },
    /// Groups
    Groups {
        #[command(subcommand)]
        cmd: GroupsCmd,
    },
    /// Models
    Models {
        #[command(subcommand)]
        cmd: ModelsCmd,
    },
    /// Skills
    Skills {
        #[command(subcommand)]
        cmd: SkillsCmd,
    },
    /// Skill categories
    SkillCategories {
        #[command(subcommand)]
        cmd: CategoryCmd,
    },
    /// Experts
    Experts {
        #[command(subcommand)]
        cmd: ExpertsCmd,
    },
    /// Expert categories
    ExpertCategories {
        #[command(subcommand)]
        cmd: CategoryCmd,
    },
    /// Users (legacy users APIs)
    Users {
        #[command(subcommand)]
        cmd: UsersCmd,
    },
    /// Execute one named operation from the 73-operation OpenAPI registry.
    Api {
        /// Registry name, for example `models-custom-create` or `skills-update`.
        operation: String,
        /// Path parameter in `name=value` form; repeat for multiple path parameters.
        #[arg(long = "param")]
        params: Vec<String>,
        /// Query parameter in `name=value` form; repeat for multiple query parameters.
        #[arg(long = "query")]
        query: Vec<String>,
        /// JSON body file. Use `-` to read JSON from stdin; never put JSON secrets in argv.
        #[arg(long)]
        body_file: Option<PathBuf>,
        /// Multipart text field in `name=value` form; repeat for multiple fields.
        #[arg(long = "field")]
        fields: Vec<String>,
        /// Optional JSON object file containing additional multipart text fields. Use `-` for stdin.
        #[arg(long)]
        fields_file: Option<PathBuf>,
        /// Multipart `package` file for skills/experts create and update operations.
        #[arg(long)]
        package: Option<PathBuf>,
        /// Required for every operation declared as write in the registry.
        #[arg(long, default_value_t = false)]
        yes: bool,
    },
}

#[derive(Debug, Subcommand)]
enum EnterpriseCmd {
    Info,
    License,
}

#[derive(Debug, Subcommand)]
enum MembersCmd {
    List {
        #[arg(long)]
        page_num: Option<i64>,
        #[arg(long)]
        page_size: Option<i64>,
        #[arg(long)]
        keyword: Option<String>,
    },
}

#[derive(Debug, Subcommand)]
enum LicensesCmd {
    Overview,
    Query {
        #[arg(long = "user-id", required = true)]
        user_ids: Vec<String>,
    },
    /// WRITE: grant licenses
    Grant {
        #[arg(long = "user-id", required = true)]
        user_ids: Vec<String>,
        #[arg(long, default_value_t = false)]
        yes: bool,
    },
    /// WRITE: revoke licenses
    Revoke {
        #[arg(long = "user-id", required = true)]
        user_ids: Vec<String>,
        #[arg(long, default_value_t = false)]
        yes: bool,
    },
}

#[derive(Debug, Subcommand)]
enum UsageCmd {
    QuotaCycle,
    DefaultQuota,
}

#[derive(Debug, Subcommand)]
enum GroupsCmd {
    List {
        #[arg(long)]
        page: Option<i64>,
        #[arg(long)]
        page_size: Option<i64>,
        #[arg(long)]
        keyword: Option<String>,
    },
    Get {
        group_id: String,
    },
    Members {
        group_id: String,
        #[arg(long)]
        page: Option<i64>,
        #[arg(long)]
        page_size: Option<i64>,
    },
}

#[derive(Debug, Subcommand)]
enum ModelsCmd {
    List {
        #[arg(long)]
        source: Option<String>,
        #[arg(long)]
        page_num: Option<i64>,
        #[arg(long)]
        page_size: Option<i64>,
    },
    Builtin,
    Custom {
        #[arg(long)]
        page_num: Option<i64>,
        #[arg(long)]
        page_size: Option<i64>,
    },
    Get {
        model_id: String,
    },
}

#[derive(Debug, Clone, ValueEnum)]
enum SourceArg {
    Builtin,
    Custom,
}

impl From<SourceArg> for SkillSource {
    fn from(v: SourceArg) -> Self {
        match v {
            SourceArg::Builtin => SkillSource::Builtin,
            SourceArg::Custom => SkillSource::Custom,
        }
    }
}

#[derive(Debug, Subcommand)]
enum SkillsCmd {
    List {
        #[arg(long, value_enum)]
        source: SourceArg,
        #[arg(long)]
        keyword: Option<String>,
        #[arg(long)]
        page_num: Option<i64>,
        #[arg(long)]
        page_size: Option<i64>,
    },
    Get {
        skill_ref: String,
    },
    Visibility {
        skill_ref: String,
        #[arg(long, value_enum)]
        source: SourceArg,
    },
    /// WRITE: set enabled/disabled
    SetEnabled {
        skill_ref: String,
        #[arg(long, value_enum)]
        source: SourceArg,
        #[arg(long)]
        enabled: bool,
        #[arg(long)]
        reason: Option<String>,
        #[arg(long, default_value_t = false)]
        yes: bool,
    },
    /// WRITE: create skill (multipart)
    Create {
        #[arg(long)]
        name: String,
        #[arg(long)]
        display_name: String,
        #[arg(long)]
        package: Option<PathBuf>,
        #[arg(long, default_value_t = false)]
        yes: bool,
    },
}

#[derive(Debug, Subcommand)]
enum ExpertsCmd {
    List {
        #[arg(long, value_enum)]
        source: SourceArg,
        #[arg(long)]
        page_num: Option<i64>,
        #[arg(long)]
        page_size: Option<i64>,
    },
    Get {
        expert_ref: String,
    },
}

#[derive(Debug, Subcommand)]
enum CategoryCmd {
    List,
}

#[derive(Debug, Subcommand)]
enum UsersCmd {
    List {
        #[arg(long)]
        page: Option<i64>,
        #[arg(long)]
        page_size: Option<i64>,
        #[arg(long)]
        keyword: Option<String>,
    },
}

fn require_yes(yes: bool, action: &str) -> Result<(), String> {
    if yes {
        Ok(())
    } else {
        Err(format!(
            "refusing to run write action `{action}` without --yes"
        ))
    }
}

fn print_json(v: &Value) {
    println!(
        "{}",
        serde_json::to_string_pretty(v).unwrap_or_else(|_| v.to_string())
    );
}

fn print_page(page: &workbuddy_enterprise::Page<Value>) {
    let out = json!({
        "total_count": page.total_count,
        "page": page.page,
        "page_num": page.page_num,
        "page_size": page.page_size,
        "next_page_token": page.next_page_token,
        "items": page.items,
    });
    print_json(&out);
}

fn print_operation_specs() {
    for spec in workbuddy_enterprise::OPERATION_SPECS {
        let body = match spec.body_kind {
            OperationBodyKind::None => "none",
            OperationBodyKind::Json => "application/json",
            OperationBodyKind::Multipart => "multipart/form-data",
        };
        println!(
            "{}\t{}\t{}\tbody={}\twrite={}",
            spec.name, spec.method, spec.suffix_template, body, spec.write
        );
    }
}

fn parse_name_values(values: &[String], flag: &str) -> Result<HashMap<String, String>, String> {
    let mut out = HashMap::new();
    for value in values {
        let (name, value) = value
            .split_once('=')
            .ok_or_else(|| format!("{flag} expects name=value"))?;
        if name.is_empty() {
            return Err(format!("{flag} name must not be empty"));
        }
        if out.insert(name.to_string(), value.to_string()).is_some() {
            return Err(format!("duplicate {flag} name `{name}`"));
        }
    }
    Ok(out)
}

fn read_file_or_stdin(path: &Path, label: &str) -> Result<String, String> {
    if path == Path::new("-") {
        let mut input = String::new();
        io::stdin()
            .read_to_string(&mut input)
            .map_err(|e| format!("read {label} from stdin: {e}"))?;
        Ok(input)
    } else {
        fs::read_to_string(path).map_err(|e| format!("read {label} {}: {e}", path.display()))
    }
}

fn read_json_body(path: Option<&Path>) -> Result<Value, String> {
    let path = path.ok_or_else(|| "this operation requires --body-file <path|->".to_string())?;
    let text = read_file_or_stdin(path, "JSON body")?;
    serde_json::from_str(&text).map_err(|e| format!("parse JSON body: {e}"))
}

fn merge_multipart_fields(
    fields: &[String],
    fields_file: Option<&Path>,
) -> Result<HashMap<String, String>, String> {
    let mut out = parse_name_values(fields, "--field")?;
    if let Some(path) = fields_file {
        let text = read_file_or_stdin(path, "multipart fields")?;
        let object: serde_json::Map<String, Value> =
            serde_json::from_str(&text).map_err(|e| format!("parse multipart fields JSON: {e}"))?;
        for (name, value) in object {
            let value = value
                .as_str()
                .ok_or_else(|| format!("multipart field `{name}` must be a JSON string"))?;
            if out.insert(name.clone(), value.to_string()).is_some() {
                return Err(format!("duplicate multipart field `{name}`"));
            }
        }
    }
    Ok(out)
}

#[rustfmt::skip]
fn render_operation_suffix(
    spec: &OperationSpec,
    mut params: HashMap<String, String>,
) -> Result<String, String> {
    let mut suffix = spec.suffix_template.to_string();
    for name in spec.path_params {
        let value = params
            .remove(*name)
            .ok_or_else(|| format!("{} requires --param {name}=...", spec.name))?;
        if *name == "id" && value.parse::<i64>().is_err() {
            return Err(format!("{} path parameter `id` must be an integer", spec.name));
        }
        suffix = suffix.replace(&format!("{{{name}}}"), &encode_path_segment(&value));
    }
    if let Some((name, _)) = params.into_iter().next() {
        return Err(format!("{} does not define path parameter `{name}`", spec.name));
    }
    Ok(suffix)
}

#[rustfmt::skip]
fn validate_query(spec: &OperationSpec, query: &HashMap<String, String>) -> Result<(), String> {
    for name in spec.required_query {
        if query.get(*name).is_none_or(|value| value.is_empty()) {
            return Err(format!("{} requires --query {name}=...", spec.name));
        }
    }
    for name in query.keys() {
        if !spec.allowed_query.contains(&name.as_str()) {
            return Err(format!("{} does not define query parameter `{name}`", spec.name));
        }
    }
    match spec.name {
        "skills-list" | "experts-list" | "skills-toggle" | "skills-visibility-set"
        | "skills-visibility-get" | "experts-toggle" | "experts-visibility-set"
        | "experts-visibility-get" => validate_query_enum(query, "source", &["builtin", "custom"]),
        "models-list" => validate_query_enum(query, "source", &["builtin", "custom", "all"]),
        _ => Ok(()),
    }?;
    if matches!(spec.name, "skills-list" | "experts-list") {
        validate_query_enum(query, "publishStatus", &["draft", "published"])?;
    }
    Ok(())
}

#[rustfmt::skip]
fn validate_query_enum(
    query: &HashMap<String, String>,
    field: &str,
    allowed: &[&str],
) -> Result<(), String> {
    if let Some(value) = query.get(field) {
        if !allowed.contains(&value.as_str()) {
            return Err(format!(
                "query `{field}` must be one of {}",
                allowed.join(", ")
            ));
        }
    }
    Ok(())
}

#[rustfmt::skip]
#[allow(clippy::too_many_arguments)]
fn run_api_operation(
    client: &Client,
    operation: &str,
    params: Vec<String>,
    query: Vec<String>,
    body_file: Option<PathBuf>,
    fields: Vec<String>,
    fields_file: Option<PathBuf>,
    package: Option<PathBuf>,
    yes: bool,
) -> Result<(), String> {
    let spec = find_operation(operation).ok_or_else(|| {
        format!(
            "unknown operation `{operation}`; valid operations: {}",
            workbuddy_enterprise::operation_names().collect::<Vec<_>>().join(", ")
        )
    })?;
    if spec.write {
        require_yes(yes, spec.name)?;
    }
    let suffix = render_operation_suffix(spec, parse_name_values(&params, "--param")?)?;
    let query = parse_name_values(&query, "--query")?;
    validate_query(spec, &query)?;
    let query: Vec<(String, String)> = query.into_iter().collect();

    match spec.body_kind {
        OperationBodyKind::None => {
            if body_file.is_some() || !fields.is_empty() || fields_file.is_some() || package.is_some() {
                return Err(format!("{} does not accept a request body", spec.name));
            }
            let response = match spec.method {
                "GET" => client.get_json(&suffix, &query),
                "POST" => client.post_empty(&suffix, &query),
                method => return Err(format!("unsupported registry method {method}")),
            }
            .map_err(|error| error.to_string())?;
            print_json(&response.data);
        }
        OperationBodyKind::Json => {
            if !fields.is_empty() || fields_file.is_some() || package.is_some() {
                return Err(format!("{} requires --body-file, not multipart flags", spec.name));
            }
            let body = read_json_body(body_file.as_deref())?;
            if spec.method != "POST" {
                return Err(format!("unsupported JSON registry method {}", spec.method));
            }
            let response = client
                .post_operation_json(spec.name, &suffix, &query, body)
                .map_err(|error| error.to_string())?;
            print_json(&response.data);
        }
        OperationBodyKind::Multipart => {
            if body_file.is_some() {
                return Err(format!("{} is multipart; use --field/--fields-file and --package", spec.name));
            }
            let fields = merge_multipart_fields(&fields, fields_file.as_deref())?;
            let response = client
                .post_operation_multipart(spec.name, &suffix, &fields, package.as_deref())
                .map_err(|error| error.to_string())?;
            print_json(&response.data);
        }
    }
    Ok(())
}

fn main() -> ExitCode {
    if let Err(e) = real_main() {
        eprintln!("error: {e}");
        return ExitCode::from(1);
    }
    ExitCode::SUCCESS
}

fn real_main() -> Result<(), String> {
    let cli = Cli::parse();
    if matches!(cli.command, Commands::Version) {
        println!(
            "workbuddy {} (workbuddy_enterprise)",
            workbuddy_enterprise::VERSION
        );
        return Ok(());
    }
    if matches!(cli.command, Commands::Operations) {
        print_operation_specs();
        return Ok(());
    }

    let client = Client::from_env().map_err(|e| e.to_string())?;

    match cli.command {
        Commands::Version | Commands::Operations => {}
        Commands::Enterprise { cmd } => match cmd {
            EnterpriseCmd::Info => {
                let r = client.enterprise().get_info().map_err(|e| e.to_string())?;
                print_json(&r.data);
            }
            EnterpriseCmd::License => {
                let r = client
                    .enterprise()
                    .get_license()
                    .map_err(|e| e.to_string())?;
                print_json(&r.data);
            }
        },
        Commands::Members { cmd } => match cmd {
            MembersCmd::List {
                page_num,
                page_size,
                keyword,
            } => {
                let r = client
                    .members()
                    .list(page_num, page_size, keyword.as_deref())
                    .map_err(|e| e.to_string())?;
                print_page(&r.data);
            }
        },
        Commands::Licenses { cmd } => match cmd {
            LicensesCmd::Overview => {
                let r = client.licenses().overview().map_err(|e| e.to_string())?;
                print_json(&r.data);
            }
            LicensesCmd::Query { user_ids } => {
                let ids: Vec<&str> = user_ids.iter().map(|s| s.as_str()).collect();
                let r = client
                    .licenses()
                    .query_members(&ids)
                    .map_err(|e| e.to_string())?;
                print_json(&r.data);
            }
            LicensesCmd::Grant { user_ids, yes } => {
                require_yes(yes, "licenses grant")?;
                let ids: Vec<&str> = user_ids.iter().map(|s| s.as_str()).collect();
                let r = client.licenses().grant(&ids).map_err(|e| e.to_string())?;
                print_json(&r.data);
            }
            LicensesCmd::Revoke { user_ids, yes } => {
                require_yes(yes, "licenses revoke")?;
                let ids: Vec<&str> = user_ids.iter().map(|s| s.as_str()).collect();
                let r = client.licenses().revoke(&ids).map_err(|e| e.to_string())?;
                print_json(&r.data);
            }
        },
        Commands::Usage { cmd } => match cmd {
            UsageCmd::QuotaCycle => {
                let r = client
                    .usage()
                    .get_quota_cycle()
                    .map_err(|e| e.to_string())?;
                print_json(&r.data);
            }
            UsageCmd::DefaultQuota => {
                let r = client
                    .usage()
                    .get_default_quota()
                    .map_err(|e| e.to_string())?;
                print_json(&r.data);
            }
        },
        Commands::Groups { cmd } => match cmd {
            GroupsCmd::List {
                page,
                page_size,
                keyword,
            } => {
                let r = client
                    .groups()
                    .list(page, page_size, keyword.as_deref())
                    .map_err(|e| e.to_string())?;
                print_page(&r.data);
            }
            GroupsCmd::Get { group_id } => {
                let r = client.groups().get(&group_id).map_err(|e| e.to_string())?;
                print_json(&r.data);
            }
            GroupsCmd::Members {
                group_id,
                page,
                page_size,
            } => {
                let r = client
                    .groups()
                    .list_members(&group_id, page, page_size, None)
                    .map_err(|e| e.to_string())?;
                print_page(&r.data);
            }
        },
        Commands::Models { cmd } => match cmd {
            ModelsCmd::List {
                source,
                page_num,
                page_size,
            } => {
                let r = client
                    .models()
                    .list(source.as_deref(), page_num, page_size, None, None)
                    .map_err(|e| e.to_string())?;
                print_page(&r.data);
            }
            ModelsCmd::Builtin => {
                let r = client.models().list_builtin().map_err(|e| e.to_string())?;
                print_page(&r.data);
            }
            ModelsCmd::Custom {
                page_num,
                page_size,
            } => {
                let r = client
                    .models()
                    .list_custom(page_num, page_size)
                    .map_err(|e| e.to_string())?;
                print_page(&r.data);
            }
            ModelsCmd::Get { model_id } => {
                let r = client.models().get(&model_id).map_err(|e| e.to_string())?;
                print_json(&r.data);
            }
        },
        Commands::Skills { cmd } => match cmd {
            SkillsCmd::List {
                source,
                keyword,
                page_num,
                page_size,
            } => {
                let r = client
                    .skills()
                    .list(
                        source.into(),
                        keyword.as_deref(),
                        None,
                        None,
                        page_num,
                        page_size,
                    )
                    .map_err(|e| e.to_string())?;
                print_page(&r.data);
            }
            SkillsCmd::Get { skill_ref } => {
                let r = client.skills().get(&skill_ref).map_err(|e| e.to_string())?;
                print_json(&r.data);
            }
            SkillsCmd::Visibility { skill_ref, source } => {
                let r = client
                    .skills()
                    .get_visibility(&skill_ref, source.into())
                    .map_err(|e| e.to_string())?;
                print_json(&r.data);
            }
            SkillsCmd::SetEnabled {
                skill_ref,
                source,
                enabled,
                reason,
                yes,
            } => {
                require_yes(yes, "skills set-enabled")?;
                let r = client
                    .skills()
                    .set_enabled(&skill_ref, source.into(), enabled, reason.as_deref())
                    .map_err(|e| e.to_string())?;
                print_json(&r.data);
            }
            SkillsCmd::Create {
                name,
                display_name,
                package,
                yes,
            } => {
                require_yes(yes, "skills create")?;
                let r = client
                    .skills()
                    .create(&name, &display_name, package.as_deref(), Default::default())
                    .map_err(|e| e.to_string())?;
                print_json(&r.data);
            }
        },
        Commands::SkillCategories { cmd } => match cmd {
            CategoryCmd::List => {
                let r = client
                    .skill_categories()
                    .list()
                    .map_err(|e| e.to_string())?;
                print_page(&r.data);
            }
        },
        Commands::Experts { cmd } => match cmd {
            ExpertsCmd::List {
                source,
                page_num,
                page_size,
            } => {
                let r = client
                    .experts()
                    .list(source.into(), None, None, None, page_num, page_size)
                    .map_err(|e| e.to_string())?;
                print_page(&r.data);
            }
            ExpertsCmd::Get { expert_ref } => {
                let r = client
                    .experts()
                    .get(&expert_ref)
                    .map_err(|e| e.to_string())?;
                print_json(&r.data);
            }
        },
        Commands::ExpertCategories { cmd } => match cmd {
            CategoryCmd::List => {
                let r = client
                    .expert_categories()
                    .list()
                    .map_err(|e| e.to_string())?;
                print_page(&r.data);
            }
        },
        Commands::Users { cmd } => match cmd {
            UsersCmd::List {
                page,
                page_size,
                keyword,
            } => {
                let r = client
                    .users()
                    .list(
                        page,
                        page_size,
                        keyword.as_deref(),
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                    )
                    .map_err(|e| e.to_string())?;
                print_page(&r.data);
            }
        },
        Commands::Api {
            operation,
            params,
            query,
            body_file,
            fields,
            fields_file,
            package,
            yes,
        } => run_api_operation(
            &client,
            &operation,
            params,
            query,
            body_file,
            fields,
            fields_file,
            package,
            yes,
        )?,
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn registry_write_gate_allows_read_posts_and_blocks_mutations_without_yes() {
        let read_post = find_operation("analytics-activity").expect("registered read POST");
        assert!(!read_post.write);
        let read_result = if read_post.write {
            require_yes(false, read_post.name)
        } else {
            Ok(())
        };
        assert!(read_result.is_ok());

        let mutation = find_operation("members-add").expect("registered mutation");
        assert!(mutation.write);
        assert!(require_yes(false, mutation.name).is_err());
    }

    #[test]
    fn required_query_rejects_missing_and_empty_values() {
        let operation = find_operation("models-available").expect("registered operation");
        assert!(validate_query(operation, &HashMap::new()).is_err());
        assert!(validate_query(
            operation,
            &HashMap::from([("userId".to_string(), String::new())]),
        )
        .is_err());
        assert!(validate_query(
            operation,
            &HashMap::from([("userId".to_string(), "u1".to_string())]),
        )
        .is_ok());
    }

    #[test]
    fn generic_path_renderer_requires_known_params_and_encodes_segments() {
        let operation = find_operation("models-get").expect("registered operation");
        assert!(render_operation_suffix(operation, HashMap::new()).is_err());
        assert_eq!(
            render_operation_suffix(
                operation,
                HashMap::from([("modelId".to_string(), "a/b?中".to_string())]),
            )
            .expect("valid path params"),
            "/openapi/models/a%2Fb%3F%E4%B8%AD"
        );
        assert!(render_operation_suffix(
            operation,
            HashMap::from([
                ("modelId".to_string(), "m1".to_string()),
                ("unknown".to_string(), "x".to_string()),
            ]),
        )
        .is_err());
    }

    #[test]
    fn registry_body_kinds_cover_each_transport_branch() {
        assert_eq!(
            find_operation("enterprise-info").unwrap().body_kind,
            OperationBodyKind::None
        );
        assert_eq!(
            find_operation("members-add").unwrap().body_kind,
            OperationBodyKind::Json
        );
        assert_eq!(
            find_operation("skills-create").unwrap().body_kind,
            OperationBodyKind::Multipart
        );
    }
}
