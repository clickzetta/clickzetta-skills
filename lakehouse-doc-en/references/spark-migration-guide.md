# Spark Job Smooth Migration to Lakehouse: A Practical Guide

This guide helps teams with existing Spark jobs migrate smoothly to Singdata Lakehouse.

## Why Migrate?

**What this is**:
Singdata Lakehouse natively supports Spark-type virtual clusters (VCluster). Your RDD, DataFrame, and UDF logic can run with almost no changes — you only need to replace the data read/write entry point from Hive/Parquet with the **Spark Connector**.

**Migration benefits**:
- **No logic rewrite**: Core compute code (RDD/DataFrame) is 100% compatible.
- **Unified entry point**: Compute jobs run directly on the Lakehouse storage-compute separation architecture, with elastic scaling and no traditional Hadoop cluster maintenance.
- **Data lake native**: Read and write Iceberg/Parquet data directly, no intermediate transfers.

---

## 1. Compatibility Overview

Before migrating, assess whether your code falls within the supported scope:

| Spark Operation | Support Status | Notes and Recommendations |
|:---|:---|:---|
| **RDD operations** | ✅ Supported | Legacy code and flexible control logic require no changes. |
| **DataFrame operations** | ✅ Supported | Data warehouse task development and big data processing. |
| **Read/write warehouse data** | ⚠️ Requires adaptation | **Not supported**: `df.write.format("parquet").saveAsTable("hive_db.table")`. Must be changed to `df.write.format("clickzetta")`. |
| **SQL operations** | ⚠️ Requires adaptation | **Not supported**: `spark.sql("SELECT ... FROM lakehouse_table")` direct queries. You must first read data via the Connector and register it as a temporary table. |
| **Spark Streaming** | ❌ Not yet supported | For real-time stream processing, migrate to **Kafka Pipe** or **real-time sync tasks**. |
| **Hive metadata access** | ❌ Not yet supported | Cannot access Hive tables via `enableHiveSupport()`. Data must be imported into Lakehouse first. |

> **Core recommendation**:
> If your jobs rely on `spark.sql` to directly read/write Hive tables, or use `Spark Streaming`, this approach does not apply.

---

## 2. Core Migration Steps

### 2.1 Environment Setup

1. **Create a Spark VCluster**:
   Run the following in the Lakehouse SQL window:
   ```sql
   CREATE VCLUSTER spark_vc TYPE SPARK;
   ```
2. **Download tools**:
   - [Spark Connector JAR](spark-connector-summary.md) (contact technical support to obtain)
   - [spark-submit client](https://autolake-dev-beijing.oss-cn-beijing.aliyuncs.com/clickzetta-tool/release/cz-spark-toolkit-submit.tar.gz)

### 2.2 Code Adaptation: Wrapping Read/Write Methods

Since direct `spark.sql` operations on Lakehouse tables are not supported, you need to wrap two utility methods:

**Read**: Load data via the Connector and register it as a temporary view, so subsequent `spark.sql` calls can operate on it like a regular table.

```scala
import org.apache.spark.sql.SparkSession
import com.clickzetta.spark.connector.ClickzettaOptions

def readClickzettaTable(spark: SparkSession, tableName: String, schema: String = "public"): Unit = {
  val df = spark.read.format("clickzetta")
    .option(ClickzettaOptions.CZ_ENDPOINT, "cn-shanghai-alicloud.api.clickzetta.com")
    .option(ClickzettaOptions.CZ_USERNAME, "your_username")
    .option(ClickzettaOptions.CZ_PASSWORD, "your_password")
    .option(ClickzettaOptions.CZ_WORKSPACE, "your_workspace")
    .option(ClickzettaOptions.CZ_VIRTUAL_CLUSTER, "spark_vc")
    .option(ClickzettaOptions.CZ_SCHEMA, schema)
    .option(ClickzettaOptions.CZ_TABLE, tableName)
    .load()
  
  // Register as a temporary table for subsequent spark.sql use
  df.createOrReplaceTempView(tableName)
}
```

**Write**: Use `format("clickzetta")` to write a DataFrame to Lakehouse.

```scala
def writeClickzettaTable(df: org.apache.spark.sql.DataFrame, tableName: String, mode: String = "overwrite"): Unit = {
  df.write.format("clickzetta")
    .option(ClickzettaOptions.CZ_ENDPOINT, "cn-shanghai-alicloud.api.clickzetta.com")
    .option(ClickzettaOptions.CZ_USERNAME, "your_username")
    .option(ClickzettaOptions.CZ_PASSWORD, "your_password")
    .option(ClickzettaOptions.CZ_WORKSPACE, "your_workspace")
    .option(ClickzettaOptions.CZ_VIRTUAL_CLUSTER, "spark_vc")
    .option(ClickzettaOptions.CZ_SCHEMA, "public")
    .option(ClickzettaOptions.CZ_TABLE, tableName)
    .mode(mode)
    .save()
}
```

### 2.3 Code Adaptation Comparison

| Original Spark Code (Hive) | Adapted Code (Lakehouse) |
|:---|:---|
| `spark.sql("SELECT * FROM hive_db.users")` | 1. `readClickzettaTable(spark, "users")`<br>2. `spark.sql("SELECT * FROM users")` |
| `df.write.saveAsTable("hive_db.result")` | `writeClickzettaTable(df, "result")` |

---

## 3. Job Submission Guide

Upload your packaged JAR to OSS and submit it using the `spark-submit` client provided by Lakehouse.

**Command example**:

```bash
./bin/spark-submit oss://your-bucket/jars/app-1.0-SNAPSHOT.jar \\
  --jars oss://your-bucket/jars/spark-clickzetta-connector.jar \\
  --master cn-shanghai-alicloud.api.clickzetta.com \\
  --name my_spark_job \\
  --class com.example.MyMainClass \\
  --conf spark.cz.instance.name=your_instance_id \\
  --conf spark.cz.workspace=your_workspace \\
  --conf spark.cz.user.name=your_username \\
  --conf spark.cz.password=your_password \\
  --conf spark.cz.vcluster=spark_vc \\
  --conf spark.cz.job.type=SPARK
```

**Key parameter reference**:

| Parameter | Description | Where to Find |
|:---|:---|:---|
| `--master` | Lakehouse API Endpoint | Studio → Management → Workspace → JDBC connection string domain |
| `--jars` | **Required** Connector dependency JAR | [Spark Connector Overview](spark-connector-summary.md) |
| `spark.cz.vcluster` | Target compute cluster | Must be a VCluster of type SPARK |
| `spark.cz.instance.name` | Instance ID | Studio → Management → Workspace → Instance ID |

---

## 4. Maven Dependency Configuration

In `pom.xml`, set Spark core dependencies to `<scope>provided</scope>`. The Connector can be included via `--jars` or set to `compile` scope if bundled into a Fat JAR.

```xml
<dependency>
  <groupId>com.clickzetta</groupId>
  <artifactId>spark-clickzetta</artifactId>
  <version>1.0.0-SNAPSHOT</version>
  <!-- If submitting via --jars, this can be omitted or set to provided -->
</dependency>

<!-- Spark core libraries are typically available on the cluster; set to provided to reduce package size -->
<dependency>
  <groupId>org.apache.spark</groupId>
  <artifactId>spark-sql_2.12</artifactId>
  <version>3.5.0</version>
  <scope>provided</scope>
</dependency>
```

---

## Related Documentation

- [Spark Connector Overview](spark-connector-summary.md)
- [Spark Connector Usage Guide](spark-connector-use.md)
- [Creating a Virtual Cluster (VCluster)](om-vcluster.md)
