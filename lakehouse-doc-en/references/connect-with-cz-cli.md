# Connecting to Lakehouse with cz-cli

cz-cli is the command-line tool for Singdata Lakehouse. It provides connection profile management, SQL execution, job operations, and more. Compared to JDBC clients, cz-cli uses **Profiles to manage connection information** — configure once, and all subsequent operations automatically use the same connection parameters without needing to re-enter a JDBC URL, username, or password every time.

---

## Prerequisites

1. cz-cli is installed (see [cz-cli Installation and Setup Guide](setup_cz_cli.md))
2. A Lakehouse instance exists and a workspace has been created
3. Your user account has been added to the target workspace with appropriate permissions

---

## Configuring a Connection Profile

A Profile is a local configuration where cz-cli stores connection information. One Profile corresponds to one Lakehouse connection environment (instance + workspace + schema + Virtual Cluster). It is recommended to create a separate Profile for each environment such as production, test, and UAT.

### Option 1: Create a Profile with Parameters (Recommended)

```bash
cz-cli profile create <profile_name> \
  --service    <service> \
  --instance   <instance> \
  --workspace  <workspace> \
  --schema     <schema> \
  --vcluster   <vcluster> \
  --username   <username> \
  --password   '<password>'
```

**Parameter descriptions:**

| Parameter | Description | How to obtain |
|------|------|---------|
| `--service` | Service endpoint address | See the cloud region table below |
| `--instance` | Instance ID | Instance name in the top-left of Studio homepage, or the `instanceId` parameter in the URL |
| `--workspace` | Workspace name | Dropdown at the top of Studio |
| `--schema` | Default schema | Run `SELECT CURRENT_SCHEMA()` after connecting |
| `--vcluster` | Default Virtual Cluster | Typically `DEFAULT` (general-purpose GP cluster) |
| `--username` | Login username | Your platform account |
| `--password` | Login password | Your platform password |

**Example: Configure Alibaba Cloud Shanghai production environment**

```bash
cz-cli profile create prod_sh \
  --service   https://cn-shanghai-alicloud.api.clickzetta.com \
  --instance  f8866243 \
  --workspace quick_start \
  --schema    semantic_model_test \
  --vcluster  DEFAULT \
  --username  qiliang \
  --password  'your_password'
```

### Option 2: Create from a Connection String Generated in Studio

In Studio → Personal Settings → Developer Tools → CLI tab, select PAT or password authentication, click "Generate Connection String", copy it, and run it in the terminal.

### Option 3: Create with a JDBC URL

```bash
cz-cli profile create prod \
  --jdbc "jdbc:clickzetta://<instance_name>.<service_endpoint>/<workspace_name>?username=<username>&password=<password>&schema=<schema>&virtualCluster=<vcluster>"
```

---

## Verifying the Connection

```bash
# View the list of created Profiles
cz-cli profile list

# Run a query using a specific Profile to verify the connection
cz-cli sql "SELECT 1" --profile prod_sh

# Set a commonly used Profile as default to omit --profile in future commands
cz-cli profile use prod_sh
```

---

## Basic Operations After Connecting

### Executing SQL

```bash
# Query
cz-cli sql "SELECT * FROM silver.dim_player LIMIT 5" --sync

# DDL/DML (requires --write)
cz-cli sql "CREATE TABLE test (id INT)" --sync --write

# Execute a SQL file
cz-cli sql -f deploy.sql --write
```

### Switching Environments

```bash
# View all Profiles
cz-cli profile list

# Switch to a different environment
cz-cli profile use prod_sh    # production
cz-cli profile use uat        # UAT
cz-cli profile use tencent_sh # Tencent Cloud Shanghai
```

---

## Common Service Endpoints by Cloud and Region

| Cloud Platform | Region | Service Endpoint |
|--------|------|-----------------|
| Alibaba Cloud | Shanghai | `https://cn-shanghai-alicloud.api.clickzetta.com` |
| Tencent Cloud | Shanghai | `https://ap-shanghai-tencentcloud.api.clickzetta.com` |
| Tencent Cloud | Beijing | `https://ap-beijing-tencentcloud.api.clickzetta.com` |
| Tencent Cloud | Guangzhou | `https://ap-guangzhou-tencentcloud.api.clickzetta.com` |
| AWS | Beijing | `https://cn-north-1-aws.api.clickzetta.com` |
| AWS | Singapore | `https://ap-southeast-1-aws.api.singdata.com` |

> **Tip**: If you are unsure about the endpoint, go to Studio → Personal Settings → Developer Tools → CLI tab and copy the complete connection command, which includes the correct Service address.

---

## Troubleshooting

### Connection Timeout or Refused

Check whether the network can reach the Service endpoint (production environments typically require a proxy or bastion host). Verify that the instance ID and workspace name are correct.

### Schema or Virtual Cluster Not Found

Run `cz-cli sql "SHOW SCHEMAS"` to list available schemas, and `cz-cli sql "SHOW VCLUSTERS"` to list available Virtual Clusters. Confirm the spelling is correct, then recreate the Profile.

### Authentication Failed

Verify the username and password are correct. If using PAT authentication, check whether the PAT has expired (regenerate it if it has).

---

## Related Documentation

- [cz-cli Installation and Setup Guide](setup_cz_cli.md) — Installation steps, PAT authentication, detailed Profile configuration
- [cz-cli SQL Execution and Data Exploration](cz-cli-sql.md) — SQL execution parameters, output format control
- [JDBC Driver Connection](JDBC-Driver.md) — Java application integration
- [Connecting with the CLI Client](connect-with-cli.md) — sqlline Java client
- [Connecting with SQLAlchemy](sqlalchemy.md) — Python SQLAlchemy integration
