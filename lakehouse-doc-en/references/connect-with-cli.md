# Connect to Lakehouse Using the Command Line Client

This article describes how to install, configure, and use the sqlline-based Lakehouse command line client.

> 💡 **cz-cli is recommended**: cz-cli is the upgraded replacement for this tool (sqlline), offering a more modern terminal experience—Profile management (configure once, reuse globally), structured JSON output, task operations commands, AI Agent integration, and more. The sqlline client is no longer actively updated; new users are advised to use cz-cli directly.
>
> → [Connect using the cz-cli command line tool](connect-with-cz-cli.md)

---

## Prerequisites

Before using the client, ensure the following conditions are met:

1. Your device has Java 8 or a higher version installed
2. You have registered an account on the Singdata platform and created a Lakehouse service instance
3. You have created a workspace for connection access
4. The user identity using the client has been added to the workspace and authorized for access

---

## Installing the Client

The Lakehouse command line client is a secondary development of the open-source SQL Line project. Follow these steps to install and configure the client:

1. Download the client installation package [sqlline_cz.tar.gz](https://autolake-dev-beijing.oss-cn-beijing.aliyuncs.com/clickzetta-tool/release/sqlline_cz.tar.gz) from the public network or obtain it from Singdata staff
2. Unzip the installation package file to get the client tool's executable and configuration files:

```bash
tar -zxvf sqlline_cz.tar.gz
```

Extracted contents:

```
sqlline_cz/
├── example.properties
├── log4j.properties
├── setup.sh
├── sqlline
└── sqlline-2.13.0-SNAPSHOT-jar-with-dependencies.jar
```

---

## Initialize Connection Environment

1. Enter the working directory:

```bash
cd sqlline_cz
```

2. Initialize the connection environment, downloading the latest JDBC driver:

```bash
sh setup.sh
```

If the setup script fails to download, manually download the JDBC driver and place it in the `sqlline_cz` directory:

- [Maven Central](https://central.sonatype.com/artifact/com.clickzetta/clickzetta-java/versions)
- [MVN Repository](https://mvnrepository.com/artifact/com.clickzetta/clickzetta-java)

---

## Configure Client Connection

### Method 1: Specify Connection Parameters via Command Line

```bash
sh sqlline -d com.clickzetta.client.jdbc.ClickZettaDriver \
  -u "jdbc:clickzetta://<instance>.<region>.api.clickzetta.com/<workspace>?schema=<schema>&vcluster=<vcluster>" \
  -n <user_name> \
  -p <password>
```

**JDBC URL format:**

```
jdbc:clickzetta://<instance_name>.<region_id>.api.clickzetta.com/<workspace_name>?schema=<schema_name>&vcluster=<vcluster_name>
```

**Parameter descriptions:**

| Parameter | Description |
|------|------|
| `-d` | JDBC driver class name, fixed as `com.clickzetta.client.jdbc.ClickZettaDriver` |
| `-u` | JDBC connection URL, see [JDBC Driver](JDBC-Driver.md) for full format |
| `-n` | Workspace member username |
| `-p` | Workspace member password |
| `schema` | Specifies the Schema to connect to, required |
| `vcluster` | Virtual Cluster to use, required |

**Example:**

```bash
sh sqlline -d com.clickzetta.client.jdbc.ClickZettaDriver \
  -u "jdbc:clickzetta://my_instance.cn-shanghai-alicloud.api.clickzetta.com/my_workspace?schema=public&vcluster=DEFAULT" \
  -n data_user \
  -p your_password
```

### Method 2: Specify Configuration File via Command Line

1. Modify the configuration file template `example.properties`:

```properties
url=jdbc:clickzetta://<instance>.<region>.api.clickzetta.com/<workspace>?schema=<schema>&vcluster=<vcluster>
driver=com.clickzetta.client.jdbc.ClickZettaDriver
user=<your_user_name>
password=<your_password>
```

2. Connect using the configuration file:

```bash
sh sqlline properties test.properties
```

After connecting, use the `!properties` command to quickly switch to another configuration file within the session:

```
0: jdbc:clickzetta://xxxx.api.clickzetta.com> !properties test.properties.1
1: jdbc:clickzetta://yyyy.api.clickzetta.com>
```

---

## Running SQL Commands

After a successful connection, you can execute Lakehouse SQL commands in the command line client:

```sql
-- Switch Virtual Cluster and Schema
use vcluster DEFAULT;
use schema nyc_taxi_data;

-- View tables in the current Schema
show tables;

-- Query data
select * from fhv_trips_staging limit 10;
```

---

## Exit Client

```
!quit
```

---

## Enable Debug Logging

Enable debug mode by setting an environment variable to output log files for troubleshooting:

```bash
export SQLLINE_DEBUG_ENABLE=TRUE
```

---

## Related Documents

- [Connect using the cz-cli command line tool](connect-with-cz-cli.md) — Recommended alternative
- [JDBC Driver Connection](JDBC-Driver.md) — Full JDBC URL format and parameters
- [Connect to Lakehouse Tutorial](tutorial_connect_to_lakehouse.md) — Comparison of all connection methods

