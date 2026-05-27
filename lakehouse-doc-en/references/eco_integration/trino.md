# Trino Clickzetta Connector User Guide

## Introduction to Trino

Trino is a high-performance, open-source, distributed SQL query engine that supports querying across various data sources, including but not limited to Hive, MySQL, PostgreSQL, MongoDB, Redis, Cassandra, Kafka, etc. Trino is commonly used for offline query acceleration and federated queries across multiple data sources, providing users with a convenient data processing and analysis experience.

This document will introduce how to use the Trino-Clickzetta plugin to directly access and analyze data in the ClickZetta LakeHouse through Trino.

## Preparations

1. Please ensure that Trino is installed. You can choose to download the [Trino 402 version server](https://repo1.maven.org/maven2/io/trino/trino-server/402/trino-server-402.tar.gz).
2. Download the Trino-Clickzetta plugin by visiting the [plugin download page](https://autolake-dev-beijing.oss-cn-beijing.aliyuncs.com/clickzetta-tool/release/trino-clickzetta-402.zip), and extract the plugin to the `plugin` folder in the Trino installation directory.
3. Download the Trino Clickzetta plugin configuration file by visiting the [configuration file download page](https://autolake-dev-beijing.oss-cn-beijing.aliyuncs.com/clickzetta-tool/release/cziceberg.properties), and copy the configuration file to the `etc/catalog` folder in the Trino installation directory. Modify the following three items in the configuration file according to your actual situation:
   ```
   iceberg.cz.uri=jdbc:clickzetta://instance.api.singdata.com/workspace?schema=public&vcluster=default
   iceberg.cz.user=username
   iceberg.cz.password=password
   ```
4. Start or restart the Trino service. Execute the following command in the Trino installation directory:
   ```shell
   bin/launcher start/restart
   ```
## Using Trino Clickzetta Plugin

1. Use the Trino client to connect to the Trino server. You can download the [Trino client](https://repo1.maven.org/maven2/io/trino/trino-cli/402/trino-cli-402-executable.jar) and refer to the [Client Usage Guide](https://trino.io/docs/current/client/cli.html) for instructions.
   ```shell
   java -jar trino-cli-402-executable.jar --server localhost:8080 --catalog cziceberg --schema public
   ```
## 2. View tables in ClickZetta LakeHouse from Trino client

2. In the Trino client, execute the following command to view the tables in ClickZetta LakeHouse:
   ```sql
   show tables;
   ```
You will see a table list similar to the following:
   ```
           Table
   ----------------------------
   lh_smoke_test_bulkload
   lh_smoke_test_igs
   spark_src
   spark_src_complex_type
   spark_srcpart
   spark_srcpart_complex_type
   spark_srcpart_date
   spark_srcpart_int
   (8 rows)
   ```
```markdown
### 3. Query data in the table. For example, query the total number of records in the `lh_smoke_test_igs` table:
```
   ```sql
   select count(*) from lh_smoke_test_igs;
   ```
The result is similar to:
   ```
   _col0
   -------
   100
   ```
## Precautions

1. This plugin is developed and verified only for Trino version 402.
2. Currently, the plugin only supports reading data from ClickZetta LakeHouse, and does not support writing data.
3. The plugin does not currently support reading tables that have been updated or deleted in ClickZetta LakeHouse.
4. For detailed information on Trino configuration files, please refer to the [Trino official documentation](https://trino.io/docs/current/installation/deployment.html#configuration).

^