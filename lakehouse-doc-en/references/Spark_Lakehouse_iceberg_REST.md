## Overview

Lakehouse provides a standard Apache Iceberg Catalog REST API interface, allowing external compute engines (such as Apache Spark) to access and query Iceberg tables stored in Lakehouse data lakes (such as Alibaba Cloud OSS object storage) through a unified REST protocol. This enables flexible selection of different compute engines for data analytics while maintaining unified data storage.

## Core Features

* **Standard Compatibility**: Compatible with the Apache Iceberg REST Catalog specification.
* **Engine Support**: Supports the Spark compute engine.
* **Credential Delegation**: Manages storage access permissions through the vended-credentials mode.
* **Multi-Cloud Support**: Supports Alibaba Cloud OSS (future versions will support AWS S3, Tencent Cloud COS, etc.).

## Usage Restrictions

**Data Type Compatibility**

When accessing Singdata Lakehouse tables through the Spark engine, the following data type restrictions apply:

Currently unsupported data types:

* **Integer Types**: `SMALLINT`, `TINYINT`
* **Semi-structured Types**: `JSON`
* **Vector Type**: `VECTOR`

## Quick Start

### Prerequisites

1. Account and password for a Singdata Lakehouse instance.

2. Target compute engine environment: Spark 3.5+.

3. Required dependency packages:

   1. Apache Iceberg library (Scala 2.12 / Spark 3.5.x): `org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.6.1`

   2. Corresponding cloud object storage SDK (e.g., Alibaba Cloud OSS: `com.aliyun.oss:aliyun-sdk-oss:3.18.1`)

### PySpark Integration Example

#### Environment Setup

```Python
import os
import base64
from pyspark.sql import SparkSession
# Set the SPARK_HOME environment variable (adjust according to the actual installation path)
os.environ['SPARK_HOME'] = '/path/to/pyspark'
```

Authentication configuration for connecting to Singdata Lakehouse:

```Python
# Configure authentication information
username = "your_username"
password = "your_password"

# Generate Basic Authentication header
credentials = f"{username}:{password}"
encoded_bytes = base64.b64encode(credentials.encode("utf-8"))
encoded_str = encoded_bytes.decode("utf-8")
auth_header = f"Basic {encoded_str}"
```

Create Spark Session:

```Python
spark = SparkSession.builder \
    .appName('IcebergCatalogIntegration') \
    .config("spark.jars.packages", "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.6.1," + "com.aliyun.oss:aliyun-sdk-oss:3.18.1") \
    .config('spark.sql.extensions', 'org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions') \
    .config('spark.sql.defaultCatalog', 'clickzetta_catalog') \
    .config('spark.sql.catalog.clickzetta_catalog', 'org.apache.iceberg.spark.SparkCatalog') \
    .config('spark.sql.catalog.clickzetta_catalog.type', 'rest') \
    .config("spark.sql.catalog.clickzetta_catalog.header.instanceName", "your_instance_id") \
    .config("spark.sql.catalog.clickzetta_catalog.header.Workspace", "your_workspace") \
    .config('spark.sql.catalog.clickzetta_catalog.uri','https://api.singdata.com/api/v1/catalog/iceberg-rest') \
    .config("spark.sql.catalog.clickzetta_catalog.header.Authorization", auth_header) \
    .config("spark.sql.catalog.clickzetta_catalog.io-impl", "org.apache.iceberg.aliyun.oss.OSSFileIO") \
    .config("spark.sql.catalog.clickzetta_catalog.oss.endpoint", "oss-cn-hangzhou.aliyuncs.com") \
    .config('spark.sql.catalog.clickzetta_catalog.header.X-Iceberg-Access-Delegation','vended-credentials') \
    .config("spark.sql.catalog.clickzetta_catalog.default-namespace", "public") \
    .config("spark.sql.catalog.clickzetta_catalog.metrics-reporter-impl", "org.apache.iceberg.metrics.LoggingMetricsReporter") \
    .getOrCreate()
```

Usage Example:

```Python
# View all namespaces (schemas)
spark.sql("SHOW NAMESPACES IN clickzetta_catalog").show()

# View tables in a specified namespace
spark.sql("SHOW TABLES IN clickzetta_catalog.public").show()

# View table structure
spark.sql("DESCRIBE TABLE clickzetta_catalog.public.your_table").show()

# Query data
df = spark.sql("SELECT * FROM clickzetta_catalog.public.your_table LIMIT 10")df.show()

# Use the DataFrame API
table_df = spark.table("clickzetta_catalog.public.your_table")
table_df.filter("column_name > 100").select("col1", "col2").show()
```

## Detailed Configuration Parameters

| Parameter                                                           | Description                                                                                                                                          | Example Value                                                                                                                                              | Required? |
| ------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- |
| Spark and Iceberg Basic Configuration                                                        |                                                                                                                                                           |                                                                                                                                                                  |                  |
| spark.jars.packages                                                      | Specifies the dependency packages that Spark should automatically download from the Maven Central repository at session startup. This includes the Iceberg Spark runtime and the SDK needed to interact with Alibaba Cloud OSS.                                                                     | org.apache.iceberg\:iceberg-spark-runtime-3.5\_2.12:1.6.1,com.aliyun.oss\:aliyun-sdk-oss:3.18.1                                                                  | Yes                |
| spark.sql.extensions                                                     | Injects Iceberg extension capabilities into Spark SQL. This enables Spark to parse and execute Iceberg-specific DDL and DML statements (e.g., CREATE TABLE ... USING iceberg).                                             | org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions                                                                                                | Yes                |
| Lakehouse REST Catalog Core Configuration                                              |                                                                                                                                                           |                                                                                                                                                                  |                  |
| spark.sql.catalog.clickzetta\_catalog                                    | Fixed value. Registers a new catalog named clickzetta\_catalog and specifies its implementation class as Iceberg's SparkCatalog. This is the entry point for defining an Iceberg Catalog.                                                          | org.apache.iceberg.spark.SparkCatalog                                                                                                                            | Yes                |
| spark.sql.catalog.clickzetta\_catalog.type                               | Fixed value. Specifies the type of clickzetta\_catalog as rest. This tells Iceberg that the Catalog is a remote service communicating via the REST API.                                                                      | rest                                                                                                                                                             | Yes                |
| spark.sql.catalog.clickzetta\_catalog.uri                                | The API endpoint address of the REST Catalog service. Spark will send all metadata management requests (such as creating tables, getting table info, etc.) to this URL.                                                                                         | https://{endpoint}/api/v1/catalog/iceberg-rest. For endpoint values, refer to the [documentation](https://www.singdata.com/documents/Supported_Cloud_Platforms).                                    | Yes                |
| spark.sql.catalog.clickzetta\_catalog.header.instanceName                | A custom HTTP request header sent to the REST Catalog. Used to identify your specific instance to the Singdata service.                                                                                                 | your\_instance\_id (replace with your instance ID)                                                                                                                                  | Yes                |
| spark.sql.catalog.clickzetta\_catalog.header.Workspace                   | A custom HTTP request header sent to the REST Catalog. Used to specify the workspace to operate in within your Singdata instance.                                                                                            | your\_workspace (replace with your workspace name)                                                                                                                                   | Yes                |
| spark.sql.catalog.clickzetta\_catalog.header.Authorization               | The authorization token used for API authentication. Typically a Bearer token used to verify client identity. This value should be obtained and passed in a secure manner.                                                                                                 | auth\_header (a variable containing authentication information), e.g.: "Basic VUFUX1RFU1Q6QWJjZDEyMzQ1Ng=="                                                                                                | Yes                |
| spark.sql.catalog.clickzetta\_catalog.header.X-Iceberg-Access-Delegation | This is a special request header for enabling the Vended Credentials mode. Setting it to vended-credentials indicates that the client (Spark) expects the Catalog service to return temporary security credentials for accessing the underlying storage (OSS). This is a more secure access mode that avoids exposing long-term cloud storage keys on the client side.        | vended-credentials                                                                                                                                               | Yes                |
| Data Storage (OSS) Configuration                                                            |                                                                                                                                                           |                                                                                                                                                                  |                  |
| spark.sql.catalog.clickzetta\_catalog.io-impl                            | Specifies the FileIO implementation used to read and write data files (such as Parquet, ORC). Here, OSSFileIO is used to interact with Alibaba Cloud OSS.                                                                                      | org.apache.iceberg.aliyun.oss.OSSFileIO                                                                                                                          | Yes                |
| spark.sql.catalog.clickzetta\_catalog.oss.endpoint                       | The regional endpoint of Alibaba Cloud Object Storage Service (OSS). The client will access OSS buckets through this address.                                                                                                                | [oss-cn-hangzhou.aliyuncs.com](http://oss-cn-hangzhou.aliyuncs.com) (can be modified according to your OSS bucket region; refer to the [documentation](https://help.aliyun.com/zh/oss/user-guide/regions-and-endpoints)) | Yes                |
| Optional / Auxiliary Configuration                                                                  |                                                                                                                                                           |                                                                                                                                                                  |                  |
| spark.sql.defaultCatalog                                                 | Sets the default Catalog for Spark SQL. When set, you do not need to explicitly specify the Catalog name before the table name in SQL queries (e.g., you can use `SELECT * FROM my_table` instead of `SELECT * FROM clickzetta_catalog.public.my_table`). | clickzetta\_catalog                                                                                                                                              | No                |
| spark.sql.catalog.clickzetta\_catalog.default-namespace                  | Sets the default namespace (or database/Schema) within clickzetta\_catalog. When set, table operations will default to this namespace if no namespace is specified.                                                                        | public                                                                                                                                                           | No (but recommended)          |
| spark.sql.catalog.clickzetta\_catalog.metrics-reporter-impl              | Configures the reporter implementation for Iceberg metrics. LoggingMetricsReporter outputs operation metrics (such as scan duration, file count, etc.) to the Spark logs, which is useful for debugging and performance analysis.                                                          | org.apache.iceberg.metrics.LoggingMetricsReporter                                                                                                                | No                |

## Troubleshooting

### Common Issues and Solutions

1. **Authentication Failure**

   1. Check that the username and password are correct.
   2. Verify that the Base64 encoding is correct.
   3. Verify that the account has the appropriate permissions.

2. **Connection Timeout**

   1. Check the network connection.
   2. Verify that the API endpoint address is correct.
   3. Adjust timeout parameters.

3. **Table Does Not Exist**

   1. Confirm that the workspace and namespace settings are correct.
   2. Use `SHOW TABLES` to verify the table name.
   3. Check user permissions.

^
