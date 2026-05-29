# Spark Connecting to Lakehouse (Iceberg REST)

## Overview

Lakehouse provides standard Apache Iceberg Catalog REST API interfaces, allowing external compute engines (such as Apache Spark) to access and query Iceberg tables stored in the Lakehouse data lake (such as OSS object storage) through a unified REST protocol. This enables flexible selection of different compute engines for data analysis while maintaining unified data storage.

## Core Features

* **Standard Compatibility**: Compatible with Apache Iceberg REST Catalog specification
* **Engine Support**: Supports the Spark compute engine
* **Credential Delegation**: Manages storage access permissions via vended-credentials mode
* **Multi-Cloud Support**: Supports Alibaba Cloud OSS (future versions will support AWS S3, Tencent Cloud COS, etc.)

## Usage Limitations

**Data Type Compatibility**

When accessing Singdata Lakehouse tables via the Spark engine, the following data type limitations exist:

Currently unsupported data types:

* **Integer types**: `SMALLINT`, `TINYINT`
* **Semi-structured types**: `JSON`
* **Vector types**: `VECTOR`

## Quick Start

### Prerequisites

1. Account and password for a Singdata Lakehouse instance

2. Target compute engine environment: Spark 3.5+

3. Required dependency packages:

   1. Apache Iceberg library (Scala 2.12 / Spark 3.5.x): `org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.6.1`

   2. Corresponding cloud object storage SDK (e.g., Alibaba Cloud OSS: `com.aliyun.oss:aliyun-sdk-oss:3.18.1`)

### PySpark Integration Example

#### Environment Preparation

```python
import os
import base64
from pyspark.sql import SparkSession
```

Set SPARK_HOME environment variable (adjust to actual installation path):

```python
os.environ['SPARK_HOME'] = '/path/to/pyspark'
```

Authentication configuration for connecting to Singdata Lakehouse

Configure authentication information:

```python
username = "your_username"
password = "your_password"

```

Generate Basic Authentication header:

```python
credentials = f"{username}:{password}"
encoded_bytes = base64.b64encode(credentials.encode("utf-8"))
encoded_str = encoded_bytes.decode("utf-8")
auth_header = f"Basic {encoded_str}"
```

Create Spark Session

```python
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

Usage Example

View all namespaces (schemas):

```python
spark.sql("SHOW NAMESPACES IN clickzetta_catalog").show()

```

View tables in a specified namespace:

```python
spark.sql("SHOW TABLES IN clickzetta_catalog.public").show()

```

View table structure:

```python
spark.sql("DESCRIBE TABLE clickzetta_catalog.public.your_table").show()

```

Query data:

```python
df = spark.sql("SELECT * FROM clickzetta_catalog.public.your_table LIMIT 10")
df.show()

```

Use DataFrame API:

```python
table_df = spark.table("clickzetta_catalog.public.your_table")
table_df.filter("column_name > 100").select("col1", "col2").show()
```

## Detailed Configuration Parameters

| Parameter                                                                | Description                                                                                                                                                                                                                                                                                                                                                             | Example Value                                                                                                                                                                                               | Required?            |
| ------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------- |
| Spark & Iceberg Basic Configuration                                      |                                                                                                                                                                                                                                                                                                                                                                         |                                                                                                                                                                                                             |                      |
| spark.jars.packages                                                      | Specifies the dependency packages to be automatically downloaded from Maven Central when the Spark session starts. Includes Iceberg Spark runtime and the SDK for interacting with Alibaba Cloud OSS.                                                                                                                                                                   | org.apache.iceberg\:iceberg-spark-runtime-3.5\_2.12:1.6.1,com.aliyun.oss\:aliyun-sdk-oss:3.18.1                                                                                                             | Yes                  |
| spark.sql.extensions                                                     | Injects Iceberg extension features into Spark SQL. This allows Spark to parse and execute Iceberg-specific DDL and DML statements (e.g., CREATE TABLE ... USING iceberg).                                                                                                                                                                                               | org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions                                                                                                                                           | Yes                  |
| Lakehouse REST Catalog Core Configuration                                |                                                                                                                                                                                                                                                                                                                                                                         |                                                                                                                                                                                                             |                      |
| spark.sql.catalog.clickzetta\_catalog                                    | Fixed value. Registers a new catalog named clickzetta\_catalog with the Iceberg SparkCatalog implementation. This is the entry point for defining an Iceberg Catalog.                                                                                                                                                                                                   | org.apache.iceberg.spark.SparkCatalog                                                                                                                                                                       | Yes                  |
| spark.sql.catalog.clickzetta\_catalog.type                               | Fixed value. Specifies the type of clickzetta\_catalog as rest. This tells Iceberg that the Catalog is a remote service communicating via REST API.                                                                                                                                                                                                                     | rest                                                                                                                                                                                                        | Yes                  |
| spark.sql.catalog.clickzetta\_catalog.uri                                | The API endpoint address of the REST Catalog service. Spark sends all metadata management requests (e.g., create table, get table info) to this URL.                                                                                                                                                                                                                    | https\://{endpoint}/api/v1/catalog/iceberg-rest. For the endpoint value, refer to the [documentation](https://www.singdata.com/documents/Supported_Cloud_Platforms)                                         | Yes                  |
| spark.sql.catalog.clickzetta\_catalog.header.instanceName                | Custom HTTP request header sent to the REST Catalog. Used to identify your specific instance to the Singdata service.                                                                                                                                                                                                                                                   | your\_instance\_id (replace with your instance ID)                                                                                                                                                          | Yes                  |
| spark.sql.catalog.clickzetta\_catalog.header.Workspace                   | Custom HTTP request header sent to the REST Catalog. Used to specify the workspace to operate on within your Singdata instance.                                                                                                                                                                                                                                         | your\_workspace (replace with your workspace name)                                                                                                                                                          | Yes                  |
| spark.sql.catalog.clickzetta\_catalog.header.Authorization               | Authorization token for API authentication. Typically a Bearer token used to verify client identity. This value should be obtained and passed securely.                                                                                                                                                                                                                 | auth\_header (a variable containing authentication information), e.g.: "Basic VUFUX1RFU1Q6QWJjZDEyMzQ1Ng=="                                                                                                 | Yes                  |
| spark.sql.catalog.clickzetta\_catalog.header.X-Iceberg-Access-Delegation | A special request header used to enable the vended credentials mode. Setting it to vended-credentials indicates that the client (Spark) expects the Catalog service to return temporary security credentials for accessing the underlying storage (OSS). This is a more secure access mode that avoids exposing long-term cloud storage credentials on the client side. | vended-credentials                                                                                                                                                                                          | Yes                  |
| Data Storage (OSS) Configuration                                         |                                                                                                                                                                                                                                                                                                                                                                         |                                                                                                                                                                                                             |                      |
| spark.sql.catalog.clickzetta\_catalog.io-impl                            | Specifies the FileIO implementation for reading and writing data files (e.g., Parquet, ORC). Uses OSSFileIO to interact with Alibaba Cloud OSS.                                                                                                                                                                                                                         | org.apache.iceberg.aliyun.oss.OSSFileIO                                                                                                                                                                     | Yes                  |
| spark.sql.catalog.clickzetta\_catalog.oss.endpoint                       | The regional endpoint of Alibaba Cloud Object Storage Service (OSS). The client accesses OSS buckets through this address.                                                                                                                                                                                                                                              | [oss-cn-hangzhou.aliyuncs.com](http://oss-cn-hangzhou.aliyuncs.com) (modify based on your OSS bucket region; refer to the [documentation](https://help.aliyun.com/zh/oss/user-guide/regions-and-endpoints)) | Yes                  |
| Optional/Auxiliary Configuration                                         |                                                                                                                                                                                                                                                                                                                                                                         |                                                                                                                                                                                                             |                      |
| spark.sql.defaultCatalog                                                 | Sets the default Catalog for Spark SQL. When set, the Catalog name does not need to be explicitly specified before table names in SQL queries (e.g., you can use `SELECT * FROM my_table` instead of `SELECT * FROM clickzetta_catalog.public.my_table`).                                                                                                               | clickzetta\_catalog                                                                                                                                                                                         | No                   |
| spark.sql.catalog.clickzetta\_catalog.default-namespace                  | Sets the default namespace (or database/Schema) within clickzetta\_catalog. If set, table operations will default to this namespace when none is specified.                                                                                                                                                                                                             | public                                                                                                                                                                                                      | No (but recommended) |
| spark.sql.catalog.clickzetta\_catalog.metrics-reporter-impl              | Configures the Iceberg metrics reporter implementation. LoggingMetricsReporter outputs operation metrics (e.g., scan duration, file count) to Spark logs, helpful for debugging and performance analysis.                                                                                                                                                               | org.apache.iceberg.metrics.LoggingMetricsReporter                                                                                                                                                           | No                   |

## Troubleshooting

### Common Issues and Solutions

1. **Authentication Failure**

   1. Check whether the username and password are correct.
   2. Confirm whether the Base64 encoding is correct.
   3. Verify whether the account has the appropriate permissions.

2. **Connection Timeout**

   1. Check network connectivity.
   2. Confirm the API endpoint address is correct.
   3. Adjust timeout parameters.

3. **Table Not Found**

   1. Confirm workspace and namespace settings are correct.
   2. Use `SHOW TABLES` to confirm the table name.
   3. Check user permissions.

^
