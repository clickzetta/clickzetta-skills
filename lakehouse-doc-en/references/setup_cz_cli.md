# cz-cli Installation and Usage Guide

**cz-cli** is the command-line and AI Agent operational tool for Singdata Lakehouse. It encapsulates Lakehouse capabilities — connection configuration, SQL execution, Schema and table management, Studio task development, task execution inspection, Job diagnostics, and more — into stable CLI commands. Users can operate directly in the terminal, and AI Agents such as Codex, Claude Code, Cursor, Kiro, and Hermes can use natural language to assist with data warehouse development and operations.

With cz-cli, users can delegate tasks like "create a test data warehouse", "check why today's tasks failed", "backfill data for a time range", "query table schema and sample data" to cz-cli for execution; cz-cli performs the actual operations and returns structured results.

## Target Users

* Data development, data platform, operations, and analytics teams who need to manage Singdata Lakehouse via the command line.
* Users who want to connect AI Agents to Singdata, enabling agents to execute queries, create tasks, diagnose runtime issues, and generate operational solutions.
* Teams needing to automate Singdata operations locally, in CI/CD, corporate bots, or operational dashboards.

## Core Capabilities

| Capability             | Description                                                     | Common Commands                                                |
| ---------------------- | --------------------------------------------------------------- | ------------------------------------------------------------ |
| Connection Management  | Create and switch connection profiles for different environments (e.g., production, testing, UAT) | cz-cli profile create, cz-cli profile list, cz-cli profile use |
| SQL Queries            | Execute SELECT, DDL, DML; supports sync wait and async Job        | cz-cli sql, cz-cli job status, cz-cli job result              |
| Schema & Table Management | View, create, describe, preview, and gather statistics on Schemas and tables | cz-cli schema, cz-cli table                                   |
| Studio Tasks           | Create SQL, offline integration, real-time sync, and other tasks; configure scheduling, publish online, and manually execute | cz-cli task                                                  |
| Run Inspection         | View task execution records, logs, dependencies, statistics; retry on failure and backfill data | cz-cli runs, cz-cli attempts                                  |
| Performance Diagnostics | View SQL Job status, results, and execution profile              | cz-cli job, cz-cli sql --job-profile                          |
| AI Agent Integration   | Enable Agents to invoke Singdata capabilities using natural language | cz-cli mcp init, cz-cli agent run                             |
| Data Source Management | Manage external data sources, preparing for sync and import tasks | cz-cli datasource                                            |

## Prerequisites

Before installation, confirm that you have the information required by your sign-in method. For help finding it, see:

* [Singdata Lakehouse Key Concepts](key-concepts.md) — Understand instances, Workspaces, Schemas, and Virtual Clusters.
* [Supported Cloud Platforms and Regions](supported-cloud-platforms.md#service-domains) — Find service endpoints and instance domains for each cloud provider and region.

| Item                | Description                           | Example                                                                                    |
| ------------------- | ------------------------------------- | ----------------------------------------------------------------------------------------- |
| Service Endpoint    | Singdata API service address          | [cn-shanghai-alicloud.api.singdata.com](http://cn-shanghai-alicloud.api.singdata.com) |
| Instance Name       | Singdata instance name or ID          | demo\_instance                                                                            |
| Workspace           | Workspace name                        | analytics\_prod                                                                           |
| Username & Password | Account credentials for connecting to Singdata | data\_user                                                                                |
| Default Schema      | Schema to use after login             | public                                                                                    |
| Default Compute Group | Virtual Cluster used for SQL execution or tasks | DEFAULT                                                                                   |

## Installing cz-cli

### macOS / Linux

Use the one-line install script:

```bash
curl -fsSL https://cz-cli.ai/install.sh | bash
```

After installation, reload your Shell configuration:

#### zsh Users

```bash
source ~/.zshrc
```

#### bash Users

```bash
source ~/.bashrc
```

### Windows

The install script must run in a Bash environment. Run it in WSL (Windows Subsystem for Linux) or Git Bash:

```bash
curl -fsSL https://cz-cli.ai/install.sh | bash
```

### Verify Installation

```bash
cz-cli --version
```

Seeing a version number indicates a successful installation.

You can also check the help:

```bash
cz-cli --help
```

## Configuring Connection Profiles

A Profile is a local configuration that stores connection information for cz-cli. We recommend creating a separate profile for each environment, e.g., prod, uat, dev.

> ⚠️ **Note**: `cz-cli setup` is deprecated. New users should use `cz-cli login`; if you already have a JDBC connection string, use `cz-cli profile create` as described below.

### Sign In with `cz-cli login` (Recommended)

`cz-cli login` uses browser-based OAuth by default. After you sign in, cz-cli stores the authentication session and token, discovers the instances and Workspaces your account can access, and automatically creates one Profile for each instance and Workspace combination. It also configures the Singdata built-in LLM for later use with `cz-cli agent`.

Give the login session a name, such as `prod`:

```bash
cz-cli login prod
```

Follow the terminal prompt to complete sign-in and authorization in your browser, then return to the terminal and wait for configuration to finish. `prod` is the login session name, not necessarily the final Profile name. Automatically created Profiles are typically named `prod_0`, `prod_1`, and so on.

To skip region selection, specify the region explicitly:

```bash
cz-cli login prod --partition intl
```

Use `intl` for the Singdata international site and `cn` for the China site. For headless automation, run `cz-cli login --help` to view non-OAuth options such as `--pat`, `--username`, and `--password`.

After signing in, view the session and automatically created Profiles:

```bash
cz-cli auth status
cz-cli auth list
cz-cli profile list
```

Select the Profile you want to use and verify the connection:

```bash
cz-cli profile use prod_0
cz-cli -p prod_0 status
```

### Create a Profile from a JDBC Connection String

If you already have a JDBC connection string, you can create a profile directly:

```bash
cz-cli profile create prod --jdbc "jdbc:clickzetta://<instance_name>.<service_endpoint>/<workspace_name>?username=<username>&password=<password>&schema=public&virtualCluster=DEFAULT"
```

In this example, `prod` is the custom Profile name.

## Viewing and Switching Profiles

Replace `prod` in the following commands with the actual Profile name. OAuth login usually creates names such as `prod_0` and `prod_1`; the JDBC method uses the name supplied to `cz-cli profile create`.

**View profiles configured on this machine**

```bash
cz-cli profile list
```

**Set the default profile**

```bash
cz-cli profile use prod
```

**Temporarily use a specific profile for a command**

```bash
cz-cli -p uat status
```

**Verify connection**

```bash
cz-cli -p prod status
```

If `connected` is `true` in the result, the connection is successful.

## First-Time Usage

**View the current workspace**

```bash
cz-cli -p prod workspace list
```

**View Schemas**

```bash
cz-cli -p prod schema list
```

**Execute a read-only query**

**cz-cli sql** defaults to synchronous execution (`--sync`), waiting and returning results directly; for large or long-running queries, add `--async` to return only a job_id and fetch the results later.

```bash
cz-cli -p prod sql "SELECT current_timestamp()" --sync
```

You can also pass SQL using **-e**:

```bash
cz-cli -p prod sql -e "SELECT * FROM public.your_table LIMIT 10" --sync
```

**Execute write operations**

To prevent accidental operations, write operations such as *INSERT*, *UPDATE*, *DELETE*, *CREATE*, *DROP* require explicitly adding --*write*.

```bash
cz-cli -p prod sql --write --sync -e "CREATE TABLE IF NOT EXISTS public.demo_orders (id INT, amount DECIMAL(18,2))"
```

**View table structure and sample data**

```bash
cz-cli -p prod table describe public.demo_orders
cz-cli -p prod table preview public.demo_orders
```

## Studio Task Development and Operations

cz-cli can operate tasks in Singdata Studio, suitable for data development and daily operations.

### Create a SQL Task

A task must be created inside a folder using `--folder`. First list the existing folders (or create one with `cz-cli -p prod task create-folder <name>`):

```bash
cz-cli -p prod task folder-tree
```

Then create the task under a specific folder:

```bash
cz-cli -p prod task create daily_order_summary --type SQL --description "Daily order summary" --folder <folder_name_or_id>
```

### Save Task SQL

```bash
cz-cli -p prod task save-content daily_order_summary --content "INSERT INTO public.order_summary SELECT current_date(), COUNT(*) FROM public.orders"
```

### Configure Scheduling

The following example schedules execution daily at 02:00:

```bash
cz-cli -p prod task save-cron daily_order_summary --cron "0 0 2 * * ? *"
```

### Deploy Task

```bash
cz-cli -p prod task deploy daily_order_summary
```

### Manually Execute Task

```bash
cz-cli -p prod task execute daily_order_summary --max-wait-seconds 300
```

## Viewing Execution Records and Logs

### View Recent Runs

```bash
cz-cli -p prod runs list --task daily_order_summary --limit 5
```

### View Run Details

```bash
cz-cli -p prod runs detail <run_id>
```

### View Run Logs

```bash
cz-cli -p prod runs logs <run_id>
```

### Wait for a Run to Complete

```bash
cz-cli -p prod runs wait <run_id>
```

## Using with AI Agents

A key value of cz-cli is giving AI Agents a controllable, auditable entry point for operating Singdata. You can register cz-cli with external Agents such as Claude Code, Cursor, Codex, and Kiro through MCP, or use the built-in `agent run` entry point.

The two approaches differ as follows:

| Approach | When to Use | Model Source | Configuration |
| --- | --- | --- | --- |
| External Agent calls cz-cli through MCP | You already use Claude Code, Cursor, Codex, Kiro, or a similar tool | The external Agent's model | `cz-cli mcp init` or manual MCP configuration |
| Built-in cz-cli Agent | You want to start natural-language tasks directly from the terminal | Model configured in `~/.clickzetta/llm.json` | `cz-cli agent llm` |

For either approach, first install cz-cli, configure a Lakehouse Profile, and verify the connection:

```bash
cz-cli profile list
cz-cli status
```

### Configure cz-cli MCP for External Agents

`cz-cli mcp init` registers the local cz-cli executable as a standard input/output (stdio) MCP Server and writes the configuration required by external Agents. You only need to run `cz-cli mcp init`; do not run `cz-cli mcp serve` manually. The external Agent starts the MCP Server automatically when needed.

Run the initialization command without options to let cz-cli detect supported clients on your machine:

```bash
cz-cli mcp init
```

You can also select clients explicitly. The current version supports `claude`, `cursor`, and `codex`. Repeat `-a` or `--client` to select multiple clients:

```bash
# Claude Code
cz-cli mcp init -a claude

# Codex
cz-cli mcp init -a codex

# Claude Code, Cursor, and Codex
cz-cli mcp init -a claude -a cursor -a codex

# All natively supported clients
cz-cli mcp init --all
```

By default, cz-cli writes user-level global configuration so the MCP Server is available across projects. To configure only the current project, run the command from the project root with `--no-global`:

```bash
cz-cli mcp init -a claude --no-global
cz-cli mcp init -a codex --no-global
```

The generated MCP configuration uses the absolute path to the cz-cli executable. First obtain that path:

```bash
command -v cz-cli
```

Place the returned absolute path in `command`. The configuration written by `cz-cli mcp init` is equivalent to:

```json
{
  "mcpServers": {
    "cz-cli": {
      "command": "/absolute/path/to/cz-cli",
      "args": ["mcp", "serve"]
    }
  }
}
```

#### Claude Code

Initialize the configuration:

```bash
cz-cli mcp init -a claude
```

Restart Claude Code, then check the MCP status:

```bash
claude mcp list
```

#### Codex

Initialize the configuration:

```bash
cz-cli mcp init -a codex
```

Restart Codex, then check the MCP status:

```bash
codex mcp list
```

#### Kiro

The current `cz-cli mcp init` command does not provide a `kiro` client option, so configure it manually. Kiro uses `.kiro/settings/mcp.json` for workspace-level configuration and `~/.kiro/settings/mcp.json` for user-level configuration. Add the following definition to the required file:

```json
{
  "mcpServers": {
    "cz-cli": {
      "command": "/absolute/path/to/cz-cli",
      "args": ["mcp", "serve"]
    }
  }
}
```

Replace `/absolute/path/to/cz-cli` with the path returned by `command -v cz-cli`. Restart Kiro, then enter `/mcp` in an interactive chat to view the server status and available tools.

> ⚠️ **Note**: Do not replace the absolute path with the string `"cz-cli"`. An Agent started from a graphical interface may not inherit your Shell PATH, which can prevent the MCP Server from starting.

#### Select a Lakehouse Profile

The generated MCP configuration does not pin a Profile. When started, `cz-cli mcp serve` reads `default_profile` from `profiles.toml`. To switch the default environment, run:

```bash
cz-cli profile use <profile>
```

If an Agent must always use a specific environment, manually pin the Profile in the MCP arguments:

```json
{
  "mcpServers": {
    "cz-cli": {
      "command": "/absolute/path/to/cz-cli",
      "args": ["mcp", "serve", "--profile", "<profile>"]
    }
  }
}
```

For production, use a dedicated low-privilege or read-only Profile with an explicit environment name, such as `prod-readonly`.

### Recommended Agent Prompt

Share the following prompt with your AI Agent:

```Plain
You can use cz-cli to operate Singdata Lakehouse. First run cz-cli status to verify the connection. For write operations, task deployment, backfill, deletion, decommissioning, and other high-risk actions, you must present the execution plan first and wait for my confirmation. Queries and inspections can be executed directly. Present results as concise tables or bullet-point summaries.
```

### Common Natural Language Requests

In the examples below, \<profile>, \<task\_name>, and \<job\_id> should be replaced with the user's own connection profile, task name, and Job ID. It is recommended to have the Agent first execute cz-cli -p \<profile> status to confirm the connection is available.

```Plain
Using the <profile> environment, first confirm the cz-cli connection status, then list the schemas in the current workspace, and then list the first 20 tables under the public schema.

Using the <profile> test environment, help me create an order details table in the demo schema, insert a few rows of test data, and verify that the data can be queried. Before executing write operations, present the plan and wait for my confirmation.

Using the <profile> environment, check whether task <task_name> has failed runs today. If so, review the run details and logs, and provide the failure cause and suggested fixes.

Using the <profile> environment, analyze the execution of SQL job <job_id>. Check the job status, results, and execution profile to determine if there are performance bottlenecks.
```

### Executing via cz-cli's Built-in Agent Entry Point

If the current environment already has the LLM parameters configured for the cz-cli Agent, you can also run directly:

```bash
cz-cli -p <profile> agent run "Help me check today's failed scheduled tasks and categorize them by failure reason"
```

### Using in Enterprise Bot Scenarios

If you use enterprise bots such as Hermes to host AI Agents, we recommend installing cz-cli in the bot execution environment and adopting the following strategies:

* Grant the bot only the necessary Singdata permissions; avoid using high-privilege administrator accounts.
* Enable manual confirmation for write, delete, deploy, decommission, backfill, and similar operations.
* Implement whitelisting or approval controls for users who can access the bot.
* Store credentials such as profiles, PATs, and passwords in controlled environment variables or local configuration — never in public documentation, chat history, or code repositories.

## Configure an LLM for the cz-cli Agent

`cz-cli agent run` requires an LLM. The LLM configuration is separate from the Lakehouse connection Profile:

| Configuration | Location | Purpose |
| --- | --- | --- |
| Lakehouse Profile | `~/.clickzetta/profiles.toml` | Connect to an instance, Workspace, Schema, and compute group |
| Agent LLM | `~/.clickzetta/llm.json` | Provide the model used by `cz-cli agent run` |

> ⚠️ **Note**: Configuring MCP for an external Agent such as Claude Code, Codex, or Kiro does not configure the cz-cli Agent's LLM. Configure `cz-cli agent llm` only when you use `cz-cli agent run` or another capability that depends on cz-cli's internal model.

### Configure the Singdata Built-in LLM with cz-cli Login

Browser-based OAuth is recommended. The first sign-in configures the OAuth session, Lakehouse Profiles, and the Singdata built-in LLM:

```bash
cz-cli login prod
```

`prod` is the login session name. After sign-in, cz-cli creates Profiles such as `prod_0` and `prod_1` for the instances and Workspaces your account can access, and writes the LLM configuration to `~/.clickzetta/llm.json`.

Signing in again with the same session name preserves the current LLM configuration by default, so a custom AI Gateway key is not overwritten. To rewrite the built-in LLM configuration from the current account, run:

```bash
cz-cli login prod --refresh-llm
```

### Connect an External LLM

`cz-cli agent llm add` supports providers including `clickzetta`, `anthropic`, `openai`, `openai-compatible`, `bedrock`, `google`, `azure`, and `openrouter`.

To connect OpenAI:

```bash
cz-cli agent llm add my-openai \
  --provider openai \
  --api-key "$OPENAI_API_KEY"
```

To connect an enterprise gateway or relay with an OpenAI-compatible API:

```bash
cz-cli agent llm add my-gateway \
  --provider openai-compatible \
  --base-url https://your-gateway.example.com/v1 \
  --api-key "$LLM_API_KEY"
```

Set `--base-url` to the gateway's actual OpenAI-compatible API endpoint, not its console URL. Never place a real API key in documentation, source control, or chat history.

### Verify and Manage LLMs

Show the active model and all configuration details:

```bash
cz-cli agent llm show
```

List all configured LLM entries:

```bash
cz-cli agent llm list
```

Test API connectivity for an entry:

```bash
cz-cli agent llm test my-openai
```

List the models available through an entry:

```bash
cz-cli agent llm models my-openai
```

Set the default model using the full `<entry-name>/<model-id>` reference:

```bash
cz-cli agent llm use my-openai/gpt-4.1
```

Remove an LLM entry:

```bash
cz-cli agent llm remove my-openai
```

After configuration, run a simple task to verify that the Agent can use both the model and the Lakehouse Profile:

```bash
cz-cli -p <profile> agent run "Check the connection status, then list the schemas in the current workspace"
```

## Output Formats and Automation

cz-cli outputs JSON by default, making it easy for AI Agents and scripts to parse. Other formats can also be specified:

**Table format, suitable for human reading**

```bash
cz-cli -p prod --format table status
```

**CSV format, suitable for export**

```bash
cz-cli -p prod --format csv sql "SELECT * FROM public.orders LIMIT 100" --sync
```

**Extract a single field**

```bash
cz-cli -p prod --field data.connected status
```

In CI/CD or automation scripts, we recommend:

* Using fixed profile names, e.g., prod-readonly, uat-admin.
* Using --sync and --timeout for query commands to control wait time.
* Explicitly adding --write for write operations, with approval or manual confirmation retained in the workflow.
* Prioritizing JSON output to avoid parsing natural language text.

## Upgrading

Check the current version:

```bash
cz-cli --version
```

Upgrade to the latest version:

```bash
cz-cli update
```

You can also re-run the install script to upgrade to the latest version:

```bash
curl -fsSL https://cz-cli.ai/install.sh | bash
```

## FAQ

### Q: After installation, I get "cz-cli: command not found"?

Usually the PATH has not taken effect. Reload your Shell configuration:

```bash
source ~/.zshrc
```

Or manually add to PATH:

```bash
echo 'export PATH="$HOME/.clickzetta/bin:$PATH"' >> ~/.zshrc

source ~/.zshrc
```

### Q: The status command shows connected: false?

Check the following in order:

```bash
cz-cli profile list
cz-cli -p <profile_name> status
```

Verify that the service, instance, workspace, username, and password or PAT in the profile are correct. If your Lakehouse instance has network policies configured, confirm that your machine's network can access the Lakehouse service.

### Q: How do I modify fields in a profile?

The profile configuration file is located at the `.clickzetta/profiles.toml` path under your current user directory.

You can modify it using the profile update command:

```bash
cz-cli profile update prod workspace <new_workspace_name>

cz-cli profile update prod password '<new_password>'

cz-cli profile update prod schema public

cz-cli profile update prod vcluster DEFAULT
```

### Q: Queries succeed, but task-related commands fail?

Commands like task, runs, and attempts depend on Studio capabilities. Verify that the environment corresponding to the current profile has Studio task capabilities enabled, and that the account has permissions to view or manage tasks.

### Q: CREATE TABLE or INSERT is rejected?

Write operations require adding --write:

```bash
cz-cli -p prod sql --write --sync -e "INSERT INTO public.demo_orders VALUES (1, 99.9)"
```

### Q: SQL returns a job\_id but no data directly?

This is because execution defaults to asynchronous mode. To get query results returned directly, add --sync:

```bash
cz-cli -p prod sql "SELECT * FROM public.demo_orders LIMIT 10" --sync
```

If you already have a job_id, you can continue with:

```bash
cz-cli -p prod job status <job_id>

cz-cli -p prod job result <job_id>
```

### Q: How can I reduce the risk of misoperations?

* Use explicit profile names for production environments, e.g., prod-readonly, prod-operator.
* For write, delete, task deploy, task decommission, backfill, and retry-on-failure actions, we recommend requiring the Agent to first present a plan and wait for manual confirmation.
* Queries, inspections, and diagnostics can be executed by the Agent directly.
* Configure a separate low-privilege account or read-only profile for the Agent.

## Recommended Getting Started Path

1. Install cz-cli and verify that cz-cli --version works.
2. Create a profile and verify the connection with cz-cli -p \<profile> status.
3. Use schema list, table list, and sql --sync to complete a read-only query.
4. In a test environment, try creating a table or inserting data to become familiar with the --write protection mechanism.
5. Review task --help and runs --help to understand task development and operations commands.
6. Run `cz-cli mcp init` to register cz-cli with an external Agent, or configure an LLM and use `cz-cli agent run`.
7. Require manual confirmation for high-risk operations performed by an Agent.

For concepts such as account name (account\_name) and service name (instance\_name) and how to find them, see: <https://www.singdata.com/documents/key-concepts>

---

## Related Documentation

- [SQL Execution and Data Exploration](cz-cli-sql.md) — Complete command reference for sql, schema, table, job, workspace
- [Studio Task Development and Operations](cz-cli-studio-tasks.md) — Task creation, scheduling, runs operations, backfill, task flow
- [External Data Source Management](cz-cli-datasource.md) — Data source browsing, connectivity testing, sample data preview
