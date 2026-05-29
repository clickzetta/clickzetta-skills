# cz-cli Installation and Usage Guide

^

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
| AI Agent Integration   | Enable Agents to invoke Singdata capabilities using natural language | cz-cli agent run, cz-cli ai-guide                             |
| Data Source Management | Manage external data sources, preparing for sync and import tasks | cz-cli datasource                                            |

## Prerequisites

Before installation, confirm you have the following information. Refer to the documentation if unsure:

| Item                | Description                           | Example                                                                                    |
| ------------------- | ------------------------------------- | ----------------------------------------------------------------------------------------- |
| Service Endpoint    | Singdata API service address          | [cn-shanghai-alicloud.api.singdata.com](http://cn-shanghai-alicloud.api.singdata.com) |
| Instance Name       | Singdata instance name or ID          | demo\_instance                                                                            |
| Workspace           | Workspace name                        | analytics\_prod                                                                           |
| Username & Password | Account credentials for connecting to Singdata | data\_user                                                                                |
| Default Schema      | Schema to use after login             | public                                                                                    |
| Default Compute Group | Virtual Cluster used for SQL execution or tasks | DEFAULT                                                                                   |

If using a Personal Access Token (PAT), you can replace username and password with the PAT.

## Installing cz-cli

### macOS / Linux

Recommended: install via npm:

```Plain
npm install -g @clickzetta/cz-cli
```


Alternatively, use the one-line install script:

```Plain
curl -fsSL https://github.com/clickzetta/cz-cli/releases/latest/download/install.sh | sh
```

After installation, reload your Shell configuration:

#### zsh Users

```Plain
source ~/.zshrc
```

#### bash Users

```Plain
source ~/.bashrc
```

### Windows

Method 1: Install via npm.

If Node.js and npm are already installed on your machine, install the npm package directly:

```Plain
npm install -g @clickzetta/cz-cli
```

Method 2: Download the installer package.

1. Open GitHub Releases: <https://github.com/clickzetta/cz-cli/releases>
2. Download the Windows archive, e.g., cz-cli-windows-x64.zip.
3. Extract and add the directory containing cz-cli.exe to your system PATH.
4. Re-open PowerShell or CMD.

### Verify Installation

```Plain
cz-cli --version
```

Seeing a version number indicates a successful installation.

You can also check the help:

```Plain
cz-cli --help
```

## Configuring Connection Profiles

A Profile is a local configuration that stores connection information for cz-cli. We recommend creating a separate profile for each environment, e.g., prod, uat, dev.

### Create with Username and Password

```SQL
cz-cli profile create prod  --service api.clickzetta.com  --instance <instance_name>  --workspace <workspace_name>  --username <username>  --password '<password>'  --schema public  --vcluster DEFAULT
```

Example:

```SQL
cz-cli profile create prod  --service api.clickzetta.com  --instance demo_instance  --workspace analytics_prod  --username data_user  --password 'your_password'  --schema public  --vcluster DEFAULT
```

### Create from JDBC Connection String

If you already have a JDBC connection string, you can create a profile directly:

```Plain
cz-cli profile create prod   --jdbc "jdbc:clickzetta://<instance_name>.<service_endpoint>/<workspace_name>?username=<username>&password=<password>&schema=public&virtualCluster=DEFAULT"
```

### Create with CLI Credential

```Scala
cz-cli setup --credencial <your cli Connection String>
```

#### How to Obtain a PAT

1\) Log in to your [Singdata account](https://accounts.singdata.com/login?ref=cz-cli), and select LakehouseMCP from the left menu.

![](/.topwrite/assets/image_1779090472848.png)

^

2\) If you have not created a PAT, please create one first.

![](/.topwrite/assets/image_1779090523412.png)

^

3\) After creation, switch to the CLI tab and copy your CLI connection string.

![](/.topwrite/assets/image_1779090540263.png)

^

4\) If you already have a PAT, paste your PAT into the popup window for CLI creation, then click the "Generate Connection String" button.

![](/.topwrite/assets/image_1779090555582.png)

^

Once you have copied the CLI connection string, return to the cz-cli window, insert the connection string into the following command, and execute:

```Plain
cz-cli setup --credential <your cli Connection String >
```

Once execution completes, the profile configuration is done.

## Viewing and Switching Profiles

**View profiles configured on this machine**

```Plain
cz-cli profile list
```

**Set the default profile**

```Plain
cz-cli profile use prod
```

**Temporarily use a specific profile for a command**

```Plain
cz-cli -p uat status
```

**Verify connection**

```Plain
cz-cli -p prod status
```

If `connected` is `true` in the result, the connection is successful.

## First-Time Usage

**View the current workspace**

```Plain
cz-cli -p prod workspace current
```

**View Schemas**

```Plain
cz-cli -p prod schema list
```

**Execute a read-only query**

**cz-cli sql** defaults to asynchronous submission, suitable for long-running queries; add `--sync` if you want the command to wait and return results directly.

```Plain
cz-cli -p prod sql "SELECT current_timestamp()" --sync
```

You can also pass SQL using **-e**:

```Plain
cz-cli -p prod sql -e "SELECT * FROM public.your_table LIMIT 10" --sync
```

**Execute write operations**

To prevent accidental operations, write operations such as *INSERT*, *UPDATE*, *DELETE*, *CREATE*, *DROP* require explicitly adding --*write*.

```Plain
cz-cli -p prod sql --write --sync -e "CREATE TABLE IF NOT EXISTS public.demo_orders (id INT, amount DECIMAL(18,2))"
```

**View table structure and sample data**

```Plain
cz-cli -p prod table describe public.demo_orderscz-cli -p prod table preview public.demo_orders
```

## Studio Task Development and Operations

cz-cli can operate tasks in Singdata Studio, suitable for data development and daily operations.

### Create a SQL Task

```Plain
cz-cli -p prod task create daily_order_summary --type SQL --description "Daily order summary"
```

### Save Task SQL

```Plain
cz-cli -p prod task save-content daily_order_summary  --content "INSERT INTO public.order_summary SELECT current_date(), COUNT(*) FROM public.orders"
```

### Configure Scheduling

The following example schedules execution daily at 02:00:

```Plain
cz-cli -p prod task save-cron daily_order_summary --cron "0 0 2 * * ? *"
```

### Deploy Task

```Plain
cz-cli -p prod task deploy daily_order_summary
```

### Manually Execute Task

```Plain
cz-cli -p prod task execute daily_order_summary --max-wait-seconds 300
```

## Viewing Execution Records and Logs

### View Recent Runs

```Plain
cz-cli -p prod runs list --task daily\_order\_summary --limit 5
```

### View Run Details

```Plain
cz-cli -p prod runs detail \<run\_id>
```

### View Run Logs

```Plain
cz-cli -p prod runs logs \<run\_id>
```

### Wait for a Run to Complete

```Plain
cz-cli -p prod runs wait \<run\_id>
```

## Using with AI Agents

A key value of cz-cli is giving AI Agents a controllable, auditable entry point for operating Singdata. Users can have Agents invoke cz-cli via command line within tools such as Codex, Claude Code, Cursor, Kiro, and Hermes.

### Recommended Agent Prompt

Share the following prompt with your AI Agent:

```Plain
You can use cz-cli to operate Singdata Lakehouse. First run cz-cli status to verify the connection. For write operations, task deployment, backfill, deletion, decommissioning, and other high-risk actions, you must present the execution plan first and wait for my confirmation. Queries and inspections can be executed directly. Present results as concise tables or bullet-point summaries.
```

### Common Natural Language Requests

In the examples below, \<profile>, \<task\_name>, and \<job\_id> should be replaced with the user's own connection profile, task name, and Job ID. It is recommended to have the Agent first execute cz-cli -p \<profile> status to confirm the connection is available.

```Scala
Using the <profile> environment, first confirm the cz-cli connection status, then list the schemas in the current workspace, and then list the first 20 tables under the public schema.Using the <profile> test environment, help me create an order details table in the demo schema, insert a few rows of test data, and verify that the data can be queried. Before executing write operations, present the plan and wait for my confirmation.Using the <profile> environment, check whether task <task_name> has failed runs today. If so, review the run details and logs, and provide the failure cause and suggested fixes.Using the <profile> environment, analyze the execution of SQL job <job_id>. Check the job status, results, and execution profile to determine if there are performance bottlenecks.
```

### Executing via cz-cli's Built-in Agent Entry Point

If the current environment already has the LLM parameters configured for the cz-cli Agent, you can also run directly:

```Plain
cz-cli -p \<profile> agent run "Help me check today's failed scheduled tasks and categorize them by failure reason"
```

To generate command descriptions for external Agents:

```Plain
cz-cli ai-guide
cz-cli ai-guide --wide
cz-cli ai-guide -f json
```

### Using in Enterprise Bot Scenarios

If you use enterprise bots such as Hermes to host AI Agents, we recommend installing cz-cli in the bot execution environment and adopting the following strategies:

* Grant the bot only the necessary Singdata permissions; avoid using high-privilege administrator accounts.
* Enable manual confirmation for write, delete, deploy, decommission, backfill, and similar operations.
* Implement whitelisting or approval controls for users who can access the bot.
* Store credentials such as profiles, PATs, and passwords in controlled environment variables or local configuration — never in public documentation, chat history, or code repositories.

## Output Formats and Automation

cz-cli outputs JSON by default, making it easy for AI Agents and scripts to parse. Other formats can also be specified:

**Table format, suitable for human reading**

```Plain
cz-cli -p prod -o table status
```

**CSV format, suitable for export**

```Plain
cz-cli -p prod -o csv sql "SELECT \* FROM public.orders LIMIT 100" --sync
```

**Extract a single field**

```Plain
cz-cli -p prod --field data.connected status
```

In CI/CD or automation scripts, we recommend:

* Using fixed profile names, e.g., prod-readonly, uat-admin.
* Using --sync and --timeout for query commands to control wait time.
* Explicitly adding --write for write operations, with approval or manual confirmation retained in the workflow.
* Prioritizing JSON output to avoid parsing natural language text.

## Upgrading

Check the current version:

```Plain
cz-cli --version
```

Upgrade to the latest version:

```Plain
cz-cli update
```

If installed via npm:

```Plain
npm install -g @clickzetta/cz-cli
```

## FAQ

### Q: After installation, I get "cz-cli: command not found"?

Usually the PATH has not taken effect. Reload your Shell configuration:

```Plain
source \~/.zshrc
```

Or manually add to PATH:

```Plain
echo 'export PATH="$$HOME/.clickzetta/bin$$PATH"' >> \~/.zshrc

source \~/.zshrc
```

### Q: The status command shows connected: false?

Check the following in order:

```Plain
cz-cli profile list
cz-cli -p <profile_name> status
```

Verify that the service, instance, workspace, username, and password or PAT in the profile are correct. If your Lakehouse instance has network policies configured, confirm that your machine's network can access the Lakehouse service.

### Q: How do I modify fields in a profile?

The profile configuration file is located at the `.clickzetta/profiles.toml` path under your current user directory.

You can modify it using the profile update command:

```Plain
cz-cli profile update prod workspace <new_workspace_name>

cz-cli profile update prod password '<new_password>'

cz-cli profile update prod schema public

cz-cli profile update prod vcluster DEFAULT
```

### Q: Queries succeed, but task-related commands fail?

Commands like task, runs, and attempts depend on Studio capabilities. Verify that the environment corresponding to the current profile has Studio task capabilities enabled, and that the account has permissions to view or manage tasks.

### Q: CREATE TABLE or INSERT is rejected?

Write operations require adding --write:

```Plain
cz-cli -p prod sql --write --sync -e "INSERT INTO public.demo\_orders VALUES (1, 99.9)"
```

### Q: SQL returns a job\_id but no data directly?

This is because execution defaults to asynchronous mode. To get query results returned directly, add --sync:

```Plain
cz-cli -p prod sql "SELECT \* FROM public.demo\_orders LIMIT 10" --sync
```

If you already have a job\_id, you can continue with:

```Plain
cz-cli -p prod job status \<job\_id>

cz-cli -p prod job result \<job\_id>
```

### Q: How can I reduce the risk of misoperations?

* Queries, inspections, and diagnostics can be executed by the Agent directly.
* For write, delete, task deploy, task decommission, backfill, and retry-on-failure actions, we recommend requiring the Agent to first present a plan and wait for manual confirmation.
* Configure a separate low-privilege account or read-only profile for the Agent.
* Use explicit profile names for production environments, e.g., prod-readonly, prod-operator.

## Recommended Getting Started Path

1. Install cz-cli and verify that cz-cli --version works.
2. Create a profile and verify the connection with cz-cli -p \<profile> status.
3. Use schema list, table list, and sql --sync to complete a read-only query.
4. In a test environment, try creating a table or inserting data to become familiar with the --write protection mechanism.
5. Review task --help and runs --help to understand task development and operations commands.
6. Hand cz-cli over to your AI Agent, with an agreement that high-risk operations require manual confirmation.

For concepts such as account name (account\_name) and service name (instance\_name) and how to find them, see: <https://www.singdata.com/documents/key-concepts>

---

## Related Documentation

- [SQL Execution and Data Exploration](cz-cli-sql.md) — Complete command reference for sql, schema, table, job, workspace
- [Studio Task Development and Operations](cz-cli-studio-tasks.md) — Task creation, scheduling, runs operations, backfill, task flow
- [AI Agent Integration](cz-cli-agent.md) — Agent LLM configuration, natural language operations, enterprise bot scenarios
- [External Data Source Management](cz-cli-datasource.md) — Data source browsing, connectivity testing, sample data preview

^

^
