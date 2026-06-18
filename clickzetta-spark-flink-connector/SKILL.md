---
name: clickzetta-spark-flink-connector
description: |
  Write data to ClickZetta Lakehouse using the Spark Connector or Flink Write Connector.
  Covers Spark DataFrame read/write configuration (Maven dependencies, connection
  parameters, read/write code), Flink Table API writes (CDC mode igs-dynamic-table,
  append-only mode igs-dynamic-table-append-only), checkpoint configuration,
  buffer/flush tuning, and key constraints such as primary-key table limitations.
  Trigger when the user says "Spark Connector", "Flink Connector", "Spark writes to Lakehouse",
  "Flink writes to Lakehouse", "spark-clickzetta", "igs-flink-connector",
  "Spark DataFrame write", "Flink CDC write", "Flink sink",
  or "spark.read.format clickzetta".
  Keywords: Spark, Flink, DataFrame, connector, read, write, CDC, igs-dynamic-table
---

# ClickZetta Spark & Flink Connector

Read [references/spark.md](references/spark.md) for the Spark Connector and [references/flink.md](references/flink.md) for the Flink Write Connector.

---

## Key Constraints (Required Reading)

| Constraint | Spark Connector | Flink Connector |
|---|---|---|
| Primary-key table writes | Not supported | Supported in `igs-dynamic-table` mode |
| Partial-column writes | Not supported; all columns must be written | Supported |
| CDC (UPDATE/DELETE) | Not supported; append only | Supported in `igs-dynamic-table` mode |
| Spark version | 3.4.0+ | N/A |
| Flink version | N/A | 1.14, 1.15, 1.17, 1.18 |

---

## Spark Connector Quick Example

```scala
// Write
df.write.format("clickzetta")
  .option("endpoint", "your_instance.cn-shanghai-alicloud.api.clickzetta.com")
  .option("username", sys.env("CZ_USERNAME"))
  .option("password", sys.env("CZ_PASSWORD"))
  .option("workspace", "your_workspace")
  .option("virtualCluster", "default")
  .option("schema", "public")
  .option("table", "orders")
  .mode("append")
  .save()

// Read
val df = spark.read.format("clickzetta")
  .option("endpoint", "your_instance.cn-shanghai-alicloud.api.clickzetta.com")
  .option("username", sys.env("CZ_USERNAME"))
  .option("password", sys.env("CZ_PASSWORD"))
  .option("workspace", "your_workspace")
  .option("virtualCluster", "default")
  .option("schema", "public")
  .option("table", "orders")
  .load()
```

---

## Flink Connector Quick Example

```sql
-- CDC mode (supports INSERT/UPDATE/DELETE; the target table must have a primary key)
CREATE TABLE lakehouse_sink (
    order_id   INT,
    status     STRING,
    amount     DOUBLE,
    PRIMARY KEY (order_id) NOT ENFORCED
) WITH (
    'connector'       = 'igs-dynamic-table',
    'curl'            = 'jdbc:clickzetta://your_instance.cn-shanghai-alicloud.api.clickzetta.com/default?username=user&password=***&schema=public',
    'schema-name'     = 'public',
    'table-name'      = 'orders',
    'sink.parallelism' = '1',
    'properties'      = 'authentication:true'
);

INSERT INTO lakehouse_sink SELECT order_id, status, amount FROM source_table;
```

---

## Selection Guide

| Scenario | Recommended option |
|---|---|
| Spark ETL batch writes to a non-primary-key table | Spark Connector |
| Flink real-time stream writes to a non-primary-key table | Flink `igs-dynamic-table-append-only` |
| Flink CDC synchronization to a primary-key table, including UPDATE/DELETE | Flink `igs-dynamic-table` |
| High-frequency real-time writes from a Java application | Java SDK RealtimeStream |
