## Introduction

In the era of data engineering and AI-driven automation, the Model Context Protocol (MCP) is transforming how we interact with data platforms. Singdata MCP-Server, as a powerful integration solution, enables AI Agents to directly operate data lakehouses,
create tasks, manage scheduling, and achieve true "conversational data engineering".

This article provides an in-depth analysis of the Singdata Lakehouse MCP-Server's architecture design, core capabilities, and offers a comprehensive hands-on guide to help data engineers and AI developers quickly get started with this innovative tool.

## 1. What is MCP Server?

### 1.1 Introduction to the MCP Protocol

The Model Context Protocol (MCP) is an open protocol introduced by Anthropic, aiming to standardize the interaction between AI models and external tools/data sources. Through MCP, AI Agents can:

* **Access external data sources**: Databases, APIs, file systems, etc.
* **Execute operations**: Create tasks, run queries, manage resources
* **Obtain context**: Understand business logic, table structures, dependencies

### 1.2 Positioning of Singdata Lakehouse MCP-Server

Singdata Lakehouse MCP-Server is an MCP service specifically designed for the Singdata Lakehouse data platform. After connecting to this service, you can directly operate product features by entering natural language in third-party AI Agents, without needing to focus on excessive product operation details.

Currently, this service provides **40+ professional tools**: covering SQL queries, task creation, operations management, and data quality scenarios.

## 2. Quick Start: Configure Your First MCP Server

### 2.1 Environment Preparation

**Recommended Tools**:

* **Claude Desktop**: Native MCP support
* **Cherry Studio**: Open-source AI client with MCP configuration support

**Prerequisites**:

* Singdata Lakehouse account and Personal Access Token (PAT)
* Access permissions for the target workspace and project
* Node.js environment (for running `mcp-remote`)

### 2.2 Claude Desktop Configuration Details

#### Step 1: Locate the Configuration File

In Claude Desktop's Settings, find the **Local MCP servers** configuration entry, click **Edit Config** to open the `claude_desktop_config.json` file.

The configuration file path is usually:

* **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
* **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

#### Step 2: Configure MCP

* In the product, click the personal information icon in the bottom-left corner and select **Lakehouse MCP**
* Generate a personal token on the page shown below, and configure the connection environment information for that token.

Note: When using this token, you have the full permissions of this user identity. Therefore, please keep the token secure to avoid security risks from leakage.


![](/.topwrite/assets/image_1766485071003.png)

^

* After generating the token, you can see the MCP configuration JSON in the connection configuration on the right side. Copy and paste it into the `claude_desktop_config.json` file.

```SQL
{  "clickzetta-http": {   
 "command": "npx",   
 "args":  [     
 "-y", "mcp-remote",   
   "https://cn-shanghai-alicloud-mcp.singdata.com/mcp",   
   "--allow-http",  
    "--transport", "http",    
  "--header", "x-Lakehouse-Token: Bearer <your_token>"    ]  }}
```

### 2.3 Cherry Studio Configuration

If using Cherry Studio:

1. Open **Settings** → **MCP** → Click **Add Server**

2. Configure as follows:

   1. **Name**: `Singdata MCP`
   2. **Type**: `Streamable HTTP (streamableHttp)`
   3. **URL**: `https://cn-shanghai-alicloud-mcp.singdata.com/mcp`
   4. **Request Headers** (one per line):

```Plain
 x-Lakehouse-Token=Bearer <your_pat>
x-Lakehouse-Region= cn-shanghai-alicloud
```

### 2.4 Verify Configuration

Restart Claude Desktop or Cherry Studio, and enter the following in the dialog:

```Plain
List all folders in the current workspace
```

If a folder list is returned, the configuration is successful!

## 3. Tool List Overview

### 3.1 Query Tools

| Tool Name                | Function Description                                                                                                          |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------- |
| LH-execute\_read\_query  | Execute read-only SQL queries and return results, with automatic result limiting. Supports SELECT, DESCRIBE/DESC, SHOW, EXPLAIN, and similar statements. Suitable for ad-hoc queries, data exploration, and quick verification. |
| LH-execute\_write\_query | Execute write-operation SQL statements (INSERT/UPDATE/DELETE/CREATE/DROP, etc.). Supports data modification, object creation/deletion, permission management, and more. Write operations are irreversible, use with caution. |
| LH-show\_object\_list    | List Lakehouse database objects without constructing SQL, avoiding SQL dialect issues. Supports smart filtering, statistical analysis, and filter suggestions. Can list WORKSPACES, TABLES, VIEWS, SCHEMAS, FUNCTIONS, VCLUSTERS, and other objects. |

### 3.2 Studio Task Management Tools

| Tool Name                             | Function Description                                                                                       |
| ------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| create\_task                          | Create a new task in a Singdata Studio project. Supports SQL, Shell, Python, data integration, Notebook, and other task types. Returns a studio\_url link to open the task directly. |
| get\_task\_detail                     | Get detailed task information, including metadata such as task name, type, owner, description, content, version, and configuration. Returns studio\_url for user access. |
| list\_singdata\_tasks                 | List tasks with filtering by folder, name, and type. Returns tasks in all states including draft and submitted tasks. |
| save\_non\_integration\_task\_content | Save content for non-data-integration tasks (SQL scripts, Shell scripts, Python code, etc.). Supports parameterized configuration. Returns studio\_url. |
| save\_integration\_task               | Save a complete data integration task configuration. Automatically handles table checking, metadata retrieval, auto table creation, and other processes. Returns studio\_url. |
| get\_file\_configuration\_detail      | Get the configuration details of a task. Returns complete configuration information and an input parameter block that can be used with save\_task\_configuration. |
| save\_task\_configuration             | Save the scheduling configuration of a task, including Cron expressions, retry policies, validity period, dependencies, etc. For integration tasks, automatically checks the Sync VCluster. |
| publish\_task                         | Publish a task to the scheduler so it can execute on schedule. Task content and configuration must be saved before publishing. Requires user confirmation before execution. |
| execute\_task                         | Asynchronously execute a data task. Supports data integration and Lakehouse SQL tasks. Automatically parses task content, handles variables, selects VC, submits execution, and polls status. |

### 3.3 Task Execution and Monitoring Tools

| Tool Name                   | Function Description                                                            |
| --------------------------- | ------------------------------------------------------------------------------- |
| list\_task\_run             | List task run records matching conditions (supports pagination). Supports filtering by project, task type, task name, run type, scheduled time, status, etc. |
| get\_task\_run\_stats       | Get task run statistics (aggregated by task). Supports filtering by project, task type, run type, time range, status, etc. Suitable for answering statistical questions such as "how is the execution going". |
| list\_executions            | List execution records under a specific task run (supports pagination). Each task run may have multiple executions. |
| get\_execution\_log         | Get the log content of a specific execution. Supports querying logs from the head, tail, or specified offset position. |
| get\_task\_instance\_detail | Get the execution status and detailed information of a task instance, including status, time, error information, etc. Used for debugging and status checking. |

### 3.4 Task Dependency and Statistics Tools

| Tool Name                          | Function Description                                                  |
| ---------------------------------- | --------------------------------------------------------------------- |
| get\_published\_task\_dependencies | Get the upstream and downstream dependency tree of a published task. Supports configuring the depth level for both upstream and downstream. |
| get\_task\_run\_dependencies       | Get the upstream and downstream dependency tree of a task run instance. Supports configuring the depth level for both upstream and downstream. |
| get\_task\_statistics              | Get statistics aggregated by task. Supports filtering by project, task type, edit status, owner, etc. Suitable for answering statistical questions such as "how many tasks are there". |

### 3.5 Data Source and Metadata Tools

| Tool Name               | Function Description                                                                            |
| ----------------------- | ----------------------------------------------------------------------------------------------- |
| list\_data\_sources     | List all available data source configurations in a project, including MySQL, PostgreSQL, Kafka, Hive, ClickHouse, etc. Supports filtering by name and type. Using filter parameters is strongly recommended. |
| list\_namespaces        | List namespace (Schema/Database) lists in a specified data source. Supports fuzzy matching filtering. |
| list\_metadata\_objects | List data objects (tables/views/collections) in a specified namespace. Supports fuzzy matching filtering. |
| get\_metadata\_detail   | Get detailed metadata information for a specified data object, including column names, data types, constraints, etc. |

### 3.6 Folder Management Tools

| Tool Name      | Function Description                                       |
| -------------- | ---------------------------------------------------------- |
| create\_folder | Create a new folder under a specified parent folder for organizing task structures. |
| list\_folders  | List folders with filtering by parent folder, name, type, and pagination. Recursively query all levels to discover all tasks. |

### 3.7 Backfill Management Tools

| Tool Name                   | Function Description                                             |
| --------------------------- | ---------------------------------------------------------------- |
| list\_backfill\_tasks       | List backfill (complement) tasks. Supports filtering by project, time range, status, submitter, task name, with pagination. |
| get\_backfill\_task\_detail | Get the complete metadata and configuration information of a backfill task. |
| list\_backfill\_instances   | List instances under a specific backfill task. Supports filtering by status and task name, with pagination. |

### 3.8 Data Quality Check Tools

| Tool Name         | Function Description                                                           |
| ----------------- | ------------------------------------------------------------------------------ |
| create\_dqc\_rule | Create and optionally execute a data quality check rule. Supports built-in metrics (row count, nulls, mean, etc.) and custom SQL. Supports manual trigger, scheduled, and task-associated trigger modes. |

### 3.9 CDC Real-Time Sync Tools

|                          |                                                                                           |
| ------------------------- | ----------------------------------------------------------------------------------------- |
| Tool Name                 | Function Description                                                                      |
| save\_cdc\_realtime\_task | Save a multi-table real-time CDC (Change Data Capture) task configuration. Supports real-time synchronization from MySQL, PostgreSQL, SQL Server, and other sources to Lakehouse/Kafka. Automatic table creation, supports full + incremental mode. |

### 3.10 Semantic View Tools

| Tool Name                    | Function Description                                                        |
| ---------------------------- | --------------------------------------------------------------------------- |
| LH-desc-logical-table        | Get the definition of a logical table in a semantic view, including associated physical tables and dimension information. |
| LH-desc-semantic-view        | Return the YAML format definition of a semantic view (Snowflake Cortex Analyst format). |
| LH-create-semantic-view      | Create a semantic view from a YAML definition (Snowflake Cortex Analyst format). Supports IF NOT EXISTS option. |
| LH-brief-semantic-view       | Describe the field information of a semantic view in a concise format. |
| LH-semantic-view-dim-add     | Add a dimension field to a semantic view. |
| LH-semantic-view-dim-del     | Delete a dimension field from a semantic view. |
| LH-get\_semantic\_view\_dims | Get all dimension information of a semantic view. |
| LH-query-semantic-value      | Query semantic view data based on natural language, by specifying dimensions, metrics, and filter conditions to retrieve data. |

### 3.11 Knowledge Base and Skills Tools

| Tool Name               | Function Description                                                  |
| ----------------------- | --------------------------------------------------------------------- |
| find\_helpful\_skills   | [Highest Priority] Search the remote skills library and return sorted candidate skills with step-by-step guidance. This tool must be called first when handling any request. |
| read\_skill\_document   | Read a specific document (script, reference, example) within a skill. When called without a path, lists all available files. |
| list\_skills            | List all available Singdata company skills in the knowledge base. Used for exploring or verifying loaded skills. |
| get\_product\_knowledge | Search Singdata product documentation (Lakehouse and Studio specification knowledge base). Used for obtaining technical documentation and product knowledge. |
| put\_knowledge          | Store text knowledge entries into the knowledge base and create indexes. Supports vector and scalar indexes. |
| search\_knowledge       | Search text knowledge entries from the knowledge base (only manually entered and annotated knowledge, including success cases and feedback). |

^

### Q&A

#### 1. Claude Desktop Reports "npx Not Found" / Failed to Spawn Process

Q1: After configuring the MCP Server in Claude Desktop, the connection fails with `Failed to spawn process: No such file or directory` in the logs.

**A**: This usually means that when Claude Desktop tries to start the local MCP connection and needs to execute the `command` in your configuration (commonly `npx`), it cannot find the executable in Claude Desktop's runtime environment (or cannot locate it in PATH).
In the HTTP (streamable) example in this article, the default `command` is `npx`, and `mcp-remote` depends on the Node.js/npm environment.

**Fix as follows**:

**On macOS**:

**1) Check if Node.js (including npx) is installed on your machine**
Open Terminal and run:

* `node -v`
* `npx -v`
* `which npx`

If `npx -v` reports an error or `which npx` has no output, it means Node.js/npm is not installed or not available.

**2) Install Node.js (recommended method so GUI apps can also find npx)**

* **Recommended approach:** Install Node.js via Homebrew (the npx path is more stable and easier for GUI apps to recognize).

  * If you get `brew: command not found`, install Homebrew first, then run `brew install node`.

* **Alternative approach:** Use the Node.js official macOS Installer (also works).

**3) Handle GUI App PATH vs Terminal inconsistency**
Even if `npx` works fine in Terminal, Claude Desktop may still not find it. In this case, we recommend:

* In `claude_desktop_config.json`, change `"command": "npx"` to the **absolute path of npx** (from `which npx` output), for example:

  * Common for Apple Silicon: `/opt/homebrew/bin/npx`
  * Common for Intel: `/usr/local/bin/npx`

**4) Restart Claude Desktop and verify again**

****

**On Windows**:

**1) Check if Node.js is installed and added to PATH**
Open PowerShell or CMD and run:

* `node -v`
* `npx -v`
* `where npx`

If not found, install Node.js (LTS recommended) and check **Add to PATH** during installation (or manually add the Node installation directory to the system PATH after installation).

**2) If Claude Desktop still cannot find npx: use absolute path for the command**
In `claude_desktop_config.json`, change `"command": "npx"` to the absolute path of `npx.cmd` (from `where npx` output). Common paths look like:

* `C:\Program Files\nodejs\npx.cmd`

**3) Restart Claude Desktop and verify again**

^
