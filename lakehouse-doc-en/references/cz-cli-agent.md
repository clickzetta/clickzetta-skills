# AI Agent Integration

A key value of cz-cli is giving AI Agents a controllable, auditable entry point for Singdata operations. In tools like Claude Code, Cursor, Kiro, and Hermes, you can have an agent invoke cz-cli via the command line.

## Recommended Prompt for Agents

Send the following to your AI Agent:

```Plain
You can use cz-cli to operate Singdata Lakehouse. First run cz-cli status to confirm the connection. For high-risk actions involving writes, task deployment, backfill, deletion, or decommissioning, you must present an execution plan and wait for my confirmation before proceeding. Queries and inspection operations can be executed directly — summarize results in a concise table or bullet points.
```

## Common Natural Language Requests

In the examples below, replace \<profile\>, \<task\_name\>, and \<job\_id\> with your own connection profile, task name, and job ID. It is recommended to have the agent run `cz-cli -p <profile> status` first to confirm the connection is available.

```Plain
Using the <profile> environment, first confirm the cz-cli connection status, then list the schemas in the current workspace, then list the first 20 tables in the public schema.

Using the test environment <profile>, create an order detail table under the demo schema, insert a few rows of test data, and verify the data can be queried. Present a plan and wait for my confirmation before executing any write operations.

Using the <profile> environment, check whether task <task_name> has any failed runs today. If so, view the run details and logs, and provide the failure reason and suggested fix.

Using the <profile> environment, analyze the execution of SQL job <job_id> — check the job status, results, and execution profile, and determine whether there are any performance bottlenecks.
```

## Running via the Built-in cz-cli Agent Entry Point

If the current environment already has the LLM parameters configured for the cz-cli agent, you can run directly:

```bash
cz-cli -p <profile> agent run "Check today's failed scheduled tasks and categorize them by failure reason"
```

To generate a command reference for an external agent:

```bash
cz-cli ai-guide
cz-cli ai-guide --wide
cz-cli ai-guide -f json
```

## Using in Enterprise Bot Scenarios

If you use an enterprise bot such as Hermes to host an AI Agent, it is recommended to install cz-cli in the bot's execution environment and adopt the following strategy:

* Grant the bot only the necessary Singdata permissions — avoid using high-privilege admin accounts.
* Enable human confirmation for write, delete, deploy, decommission, and backfill operations.
* Apply allowlist or approval controls for users who can access the bot.
* Store credentials such as profiles, PATs, and passwords in controlled environment variables or local configuration — never write them into public documents, chat logs, or code repositories.

---

## Configuring the AI Agent LLM (agent llm)

`cz-cli agent run` requires an LLM to be configured before use. LLM configuration is independent of the Lakehouse connection profile and is stored in the `[llm.*]` section of `~/.clickzetta/profiles.toml`.

### Method 1: Use the Singdata Built-in LLM (Recommended for New Users)

Complete configuration in one step using the CLI connection string:

```bash
cz-cli setup --credential <CLI connection string>
```

The CLI connection string is available on the LakehouseMCP page in the account console (see the [Installation and Configuration Guide](setup_cz_cli.md)).

### Method 2: Connect an External LLM

**OpenAI / GPT**

```bash
cz-cli agent llm add my-openai \
  --provider openai \
  --api-key $OPENAI_API_KEY \
  --use
```

**OpenAI-compatible relay gateway (enterprise proxy, etc.)**

```bash
cz-cli agent llm add my-relay \
  --provider openai-compatible \
  --base-url https://your-gateway.example.com/v1 \
  --api-key <API_KEY> \
  --use
```

### Verify and Manage

```bash
```

View the currently active LLM and all configurations:

```bash
cz-cli agent llm show

```

List all configured LLMs:

```bash
cz-cli agent llm list

```

Test connectivity:

```bash
cz-cli agent llm test my-openai

```

Switch the active LLM:

```bash
cz-cli agent llm use my-openai

```

Remove an LLM configuration:

```bash
cz-cli agent llm remove my-openai
```

> ⚠️ LLM configuration and Lakehouse connection profiles are two separate configurations. `cz-cli setup` configures the Lakehouse connection; `cz-cli agent llm add` configures the LLM. Both must be configured for `cz-cli agent run` to work.

## Related Documentation

**cz-cli Documentation**

- [Installation and Configuration Guide](setup_cz_cli.md) — Installation, profile configuration, basic usage
- [SQL Execution and Data Exploration](cz-cli-sql.md) — sql, schema, table command reference
- [Studio Task Development and Operations](cz-cli-studio-tasks.md) — Task management, runs, backfill

**Lakehouse Documentation**

- [Studio Guide](studio_manual.md) — Complete Studio Web UI operations guide
- [Workspace](workspace-introduction.md) — User management, permission model
- [Singdata CLI](cz-cli.md) — cz-cli overview and agent value
