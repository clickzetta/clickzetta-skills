# BI Tool Connection Reference

> Source: https://www.yunqi.tech/documents/ecosystem-all

## Connection Method Overview

| Tool | Connection Method | Notes |
|---|---|---|
| Apache Superset | SQLAlchemy URL | Requires clickzetta-connector |
| Tableau | JDBC + plugin | Requires .taco plugin |
| Metabase | Dedicated driver | Requires .jar driver |
| DBeaver | JDBC | General-purpose database client |
| DataGrip | JDBC | JetBrains database IDE |
| FineBI | JDBC | BI tool |

---

## JDBC Connection String Format

```
jdbc:clickzetta://<instance_name>.<region_id>.api.clickzetta.com/<workspace_name>?username=<user>&password=<pwd>&schema=<schema>&virtualCluster=<vc_name>
```

Example:
```
jdbc:clickzetta://f8866243.cn-shanghai-alicloud.api.clickzetta.com/quick_start?username=alice&password=xxxx&schema=public&virtualCluster=default_ap
```

JDBC driver class: `com.clickzetta.client.jdbc.ClickZettaDriver`

JDBC driver download:
- Maven: `com.clickzetta:clickzetta-java`
- Direct download: https://central.sonatype.com/artifact/com.clickzetta/clickzetta-java/versions

---

## SQLAlchemy URL Format

```
clickzetta://<username>:<password>@<instance_name>.<region_id>.api.clickzetta.com/<workspace_name>?schema=<schema>&vcluster=<vc_name>
```

Example:
```
clickzetta://alice:xxxx@f8866243.cn-shanghai-alicloud.api.clickzetta.com/quick_start?schema=public&vcluster=default_ap
```

Install:
```bash
pip uninstall -y clickzetta-sqlalchemy clickzetta-connector && pip install clickzetta-connector -U
```

---

## Apache Superset

### Quick Start (Docker)

```bash
docker pull clickzetta/superset:2.1.0-1
docker run -p 8088:8088 clickzetta/superset:2.1.0-1
# Visit http://localhost:8088, default credentials: admin/clickzetta
```

### Local Install

```bash
pip uninstall -y clickzetta-sqlalchemy clickzetta-connector
pip install clickzetta-connector -U
pip install 'apache-superset>=2.1'

export FLASK_APP=superset
superset db upgrade
superset fab create-admin
superset init
superset run -p 8088 --with-threads --reload --debugger
```

### Configure Database Connection

1. Settings → Database Connections → + Database
2. Select **Other** as the database type
3. Enter the SQLAlchemy URI:
   ```
   clickzetta://username:password@instance.region.api.clickzetta.com/workspace?vcluster=default_ap
   ```
4. Click TESTING CONNECTION to verify, then CONNECT

---

## Tableau

### Prerequisites

1. Download the JDBC driver JAR
2. Download the Tableau plugin: `clickzetta_jdbc-v0.0.1.taco`

### Installation

**Place the JDBC driver:**
- Windows: `C:\Program Files\Tableau\Drivers`
- macOS: `~/Library/Tableau/Drivers`
- Linux: `/opt/tableau/tableau_driver/jdbc`

**Place the Tableau plugin (.taco file):**
- Windows: `C:\Users\[User]\Documents\My Tableau Repository\Connectors`
- macOS: `/Users/[user]/Documents/My Tableau Repository/Connectors`

**Launch Tableau (disable signature verification):**
```bash
# macOS
/Applications/Tableau\ Desktop\ [version].app/Contents/MacOS/Tableau -DDisableVerifyConnectorPluginSignature=true

# Windows
tableau.exe -DDisableVerifyConnectorPluginSignature=true
```

**Connect:** Left nav → To Server → More → Lakehouse x ClickZetta → enter server/username/password

---

## Metabase

### Docker Deployment

```bash
docker pull metabase/metabase:v0.54.6
docker run -d -p 3000:3000 --name metabase metabase/metabase:v0.54.6

# Install the ClickZetta driver
docker cp clickzetta.metabase-driver.jar metabase:/plugins/clickzetta.metabase-driver.jar
docker restart metabase
```

Driver download: `clickzetta.metabase-driver.jar` (contact ClickZetta support)

### Configure Connection

1. Visit `http://localhost:3000`
2. Admin Settings → Databases → Add a database
3. Select ClickZetta Lakehouse and fill in connection details
4. Test connection → Save

---

## DBeaver

### Configuration Steps

1. Database → Driver Manager → New Driver
2. Fill in:
   - Driver name: `Clickzetta`
   - Class name: `com.clickzetta.client.jdbc.ClickZettaDriver`
   - URL template: `jdbc:clickzetta://{instanceName}.{service}/{workspaceName}?virtualCluster={vc_name}`
3. Libraries → Add the JDBC JAR
4. New Connection → search Clickzetta → paste JDBC connection string → enter username/password

---

## Region Code (region_id) Reference

| Cloud Provider | Region | region_id |
|---|---|---|
| Alibaba Cloud | East China 2 (Shanghai) | cn-shanghai-alicloud |
| Tencent Cloud | East China (Shanghai) | ap-shanghai-tencentcloud |
| Tencent Cloud | North China (Beijing) | ap-beijing-tencentcloud |
| Tencent Cloud | South China (Guangzhou) | ap-guangzhou-tencentcloud |
| AWS | China (Beijing) | cn-north-1-aws |
| Alibaba Cloud (Singapore) | Asia Pacific SE 1 | ap-southeast-1-alicloud |
| AWS (Singapore) | Asia Pacific (Singapore) | ap-southeast-1-aws |
