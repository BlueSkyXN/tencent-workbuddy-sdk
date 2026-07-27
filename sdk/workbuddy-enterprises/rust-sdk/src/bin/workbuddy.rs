use clap::{Parser, Subcommand, ValueEnum};
use serde_json::{json, Value};
use std::path::PathBuf;
use std::process::ExitCode;
use workbuddy_enterprise::{Client, SkillSource};

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

    let client = Client::from_env().map_err(|e| e.to_string())?;

    match cli.command {
        Commands::Version => {}
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
                    .list(page, page_size, keyword.as_deref(), None, None)
                    .map_err(|e| e.to_string())?;
                print_page(&r.data);
            }
        },
    }
    Ok(())
}
