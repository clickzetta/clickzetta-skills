---
name: clickzetta-bi-connect
description: |
  Connect BI tools and database clients to ClickZetta Lakehouse. Covers complete
  connection setup for Apache Superset, Tableau, Metabase, DBeaver, DataGrip,
  FineBI, and more — including JDBC connection string format, SQLAlchemy URL
  format, and driver installation steps.
  Trigger when user mentions: "connect Superset", "Tableau connect Lakehouse",
  "Metabase", "DBeaver", "DataGrip", "BI tool", "JDBC connection",
  "SQLAlchemy connection", "FineBI", "database client", "visualization tool",
  "BI report", "PowerBI", "Navicat", "MySQL protocol connection".
  Keywords: BI, Superset, Tableau, Metabase, DBeaver, DataGrip, FineBI, JDBC, connection
---

# ClickZetta BI Tool Connections

See [references/bi-tools.md](references/bi-tools.md) for detailed configuration per tool.

## Connection Method Quick Reference

| Tool | Connection Method |
|---|---|
| Apache Superset | SQLAlchemy URL |
| Tableau | JDBC + .taco plugin |
| Metabase | Dedicated .jar driver |
| DBeaver / DataGrip | JDBC |
| FineBI | JDBC or MySQL protocol |
| PowerBI | MySQL protocol |
| Navicat | MySQL protocol |
| Python / ORM | SQLAlchemy |

---

## JDBC Connection String

```
jdbc:clickzetta://<instance>.<region_id>.api.clickzetta.com/<workspace>?username=<user>&password=<pwd>&schema=<schema>&virtualCluster=<vc_name>
```

**Example:**
```
jdbc:clickzetta://f8866243.cn-shanghai-alicloud.api.clickzetta.com/quick_start?username=alice&password=xxxx&schema=public&virtualCluster=default_ap
```

- Driver class: `com.clickzetta.client.jdbc.ClickZettaDriver`
- Driver download: Maven `com.clickzetta:clickzetta-java` or [sonatype](https://central.sonatype.com/artifact/com.clickzetta/clickzetta-java/versions)

---

## SQLAlchemy URL (Superset / Python ORM)

```
clickzetta://<username>:<password>@<instance>.<region_id>.api.clickzetta.com/<workspace>?schema=<schema>&vcluster=<vc_name>
```

Install:
```bash
pip uninstall -y clickzetta-sqlalchemy clickzetta-connector
pip install clickzetta-connector -U
```

---

## Apache Superset

**Quick start with Docker:**
```bash
docker pull clickzetta/superset:2.1.0-1
docker run -p 8088:8088 clickzetta/superset:2.1.0-1
# Visit http://localhost:8088, credentials: admin/clickzetta
```

**Configure database connection:**
1. Settings → Database Connections → + Database → select **Other**
2. Enter SQLAlchemy URI:
   ```
   clickzetta://username:password@instance.cn-shanghai-alicloud.api.clickzetta.com/workspace?vcluster=default_ap
   ```
3. TESTING CONNECTION → CONNECT

---

## Tableau

1. Place the JDBC JAR in the Tableau Drivers directory
2. Place the `.taco` plugin in the Connectors directory
3. Launch with `-DDisableVerifyConnectorPluginSignature=true`
4. Connect: To Server → More → **Lakehouse x ClickZetta**

---

## Metabase

```bash
docker run -d -p 3000:3000 --name metabase metabase/metabase:v0.54.6
docker cp clickzetta.metabase-driver.jar metabase:/plugins/
docker restart metabase
```

Visit `http://localhost:3000` → Admin Settings → Databases → Add a database → select ClickZetta

---

## DBeaver

1. Driver Manager → New Driver
2. Class name: `com.clickzetta.client.jdbc.ClickZettaDriver`
3. Add the JDBC JAR
4. New Connection → paste the JDBC connection string

---

## MySQL Protocol (PowerBI / Navicat / FineBI)

Lakehouse supports MySQL protocol connections for tools that don't support custom JDBC drivers.

**Prerequisites:**
1. Reset the MySQL protocol password for the user in the admin console
2. Set the user's default virtual cluster (`ALTER USER username SET DEFAULT_VCLUSTER = default_ap`)

**Username format:** `<instance_name>.<workspace_name>.<username>`

**Connection parameters:**
- Host: `<instance>.<region_id>.mysql.clickzetta.com`
- Port: `3306`
- Username: `instance.workspace.username` (three-part format)
- Password: MySQL protocol password (not the Lakehouse login password)

### PowerBI

1. Get Data → MySQL database
2. Server: `instance.cn-shanghai-alicloud.mysql.clickzetta.com`
3. Username: `instance.workspace.username`
4. Password: MySQL protocol password
5. Data connectivity mode: DirectQuery

### Navicat

1. New Connection → MySQL
2. Host: `instance.cn-shanghai-alicloud.mysql.clickzetta.com`
3. Port: `3306`
4. Username: `instance.workspace.username`
5. Password: MySQL protocol password

### FineBI (MySQL protocol)

1. Admin → Data Connection → New Connection → MySQL
2. URL: `jdbc:mysql://instance.cn-shanghai-alicloud.mysql.clickzetta.com:3306/workspace`
3. Username: `instance.workspace.username`
4. Password: MySQL protocol password

> ⚠️ MySQL protocol connections have some SQL syntax limitations. See the [MySQL client connection guide](https://www.yunqi.tech/documents/use-mysql-client) for details.

---

## Common Region Codes

| Region | region_id |
|---|---|
| Alibaba Cloud Shanghai | `cn-shanghai-alicloud` |
| Tencent Cloud Shanghai | `ap-shanghai-tencentcloud` |
| Tencent Cloud Beijing | `ap-beijing-tencentcloud` |
| AWS Singapore | `ap-southeast-1-aws` |

---

## Troubleshooting

| Issue | Solution |
|---|---|
| Superset connection fails | Verify `clickzetta-connector` is installed and the URL format is correct |
| Tableau can't find the Lakehouse connector | Confirm the .taco file is in the correct directory and signature verification is disabled at launch |
| DBeaver driver fails to load | Verify the JAR version matches the Lakehouse version |
| Connection timeout | Check network; confirm instance and region_id are correct |
| Permission denied on query | Confirm the user was added via `CREATE USER` and has `USE VCLUSTER` permission |
| MySQL protocol connection fails | Confirm username is in three-part format (instance.workspace.username) and the MySQL protocol password is used |
| PowerBI DirectQuery error | Confirm the user's default virtual cluster is set (`ALTER USER ... SET DEFAULT_VCLUSTER`) |
