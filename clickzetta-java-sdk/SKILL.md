---
name: clickzetta-java-sdk
description: |
  Use the ClickZetta Java SDK to write data to Lakehouse tables in batch or in real time.
  Covers complete usage patterns for BulkloadStream (local file/database batch uploads)
  and RealtimeStream (Kafka real-time consumption and writes), including Maven dependencies,
  connection URL formats, row write APIs, status monitoring, Options tuning, and common error handling.
  Trigger when users say "Java SDK", "BulkloadStream", "RealtimeStream",
  "write to Lakehouse with Java", "Java batch upload", "Kafka Java write",
  "clickzetta-java", "Maven dependency", "Java data import",
  "Java 写入 Lakehouse", "Java 批量上传", or "Kafka Java 写入".
  Keywords: Java SDK, BulkloadStream, RealtimeStream, Kafka consumer, batch write, real-time write
---

# ClickZetta Java SDK

The Java SDK provides two write interfaces:
- **BulkloadStream** - batch writes for scheduled ETL and local file imports. It does not support primary-key tables and is not recommended for high-frequency writes under 5 minutes.
- **RealtimeStream** - real-time writes for Kafka consumption and streaming ingestion. Data can be queried within seconds.

Read [references/bulkload.md](references/bulkload.md) for batch writes and [references/realtime.md](references/realtime.md) for real-time writes.

---

## Maven Dependency

```xml
<!-- See https://central.sonatype.com/artifact/com.clickzetta/clickzetta-java for the latest clickzetta-java version. -->
<dependency>
    <groupId>com.clickzetta</groupId>
    <artifactId>clickzetta-java</artifactId>
    <version>2.0.0</version>
</dependency>
```

RealtimeStream with Kafka also requires:

```xml
<dependency>
    <groupId>org.apache.kafka</groupId>
    <artifactId>kafka-clients</artifactId>
    <version>3.2.0</version>
</dependency>
```

---

## Connection URL Format

```java
// Recommended: explicit parameters. Supported in 2.0.0+ and does not depend on URL parsing.
ClickZettaClient client = ClickZettaClient.newBuilder()
    .service("cn-shanghai-alicloud.api.clickzetta.com")
    .instance("your_instance")
    .workspace("your_workspace")
    .schema("public")
    .username("your_user")
    .password("your_password")
    .vcluster("default")
    .build();

// Compatible URL-based mode. BulkloadStream uses virtualcluster=, while RealtimeStream uses vcluster=.
String bulkUrl = MessageFormat.format(
    "jdbc:clickzetta://{0}.{1}/{2}?schema={3}&username={4}&password={5}&virtualcluster={6}",
    instance, region_endpoint, workspace, schema, username, password, vcluster
);
String rtUrl = MessageFormat.format(
    "jdbc:clickzetta://{0}.{1}/{2}?schema={3}&username={4}&password={5}&vcluster={6}",
    instance, region_endpoint, workspace, schema, username, password, vcluster
);
ClickZettaClient client = ClickZettaClient.newBuilder().url(url).build();
```

JDBC connection for DDL and queries:

```java
// Driver class for 2.0.0+: com.clickzetta.client.jdbc.ClickZettaDriver
// Driver class for 1.x: com.clickzetta.jdbc.ClickZettaDriver
Class.forName("com.clickzetta.client.jdbc.ClickZettaDriver");
Connection conn = DriverManager.getConnection(jdbcUrl);
```

---

## BulkloadStream Quick Example

```java
// Create a BulkloadStream.
BulkloadStream stream = client.newBulkloadStreamBuilder()
    .schema("public")
    .table("orders")
    .operate(RowStream.BulkLoadOperate.APPEND)
    .build();

// Write data. Column indexes start at 0 and must match the table DDL order.
Row row = stream.createRow();
row.setValue(0, "order-001");   // STRING
row.setValue(1, 1);             // INT
row.setValue(2, 299.99);        // DOUBLE
stream.apply(row);              // Required. Otherwise the row is not sent to the server.

// Close and wait for completion.
stream.close();
while (stream.getState() == StreamState.RUNNING) {
    Thread.sleep(1000);
}
if (stream.getState() == StreamState.FAILED) {
    throw new RuntimeException(stream.getErrorMessage());
}
client.close();
```

---

## RealtimeStream Quick Example

```java
// Options tuning.
Options options = Options.builder()
    .withMutationBufferLinesNum(10)  // Number of buffered rows.
    .build();

// Create a RealtimeStream for a regular table in APPEND_ONLY mode.
RealtimeStream stream = client.newRealtimeStreamBuilder()
    .operate(RowStream.RealTimeOperate.APPEND_ONLY)
    .options(options)
    .schema("public")
    .table("events")
    .build();

// Write data by column name, not by index.
Row row = stream.createRow(Stream.Operator.INSERT);
row.setValue("id", 1);
row.setValue("event", "{\"type\":\"click\"}");
stream.apply(row);
stream.close();
```

## RealtimeStream CDC Example for Primary-Key Tables

```java
// Table DDL: CREATE TABLE orders (txid STRING NOT NULL PRIMARY KEY, amount DOUBLE, status STRING);

RealtimeStream stream = client.newRealtimeStreamBuilder()
    .operate(RowStream.RealTimeOperate.CDC)   // Primary-key tables must use CDC.
    .options(options)
    .schema("public")
    .table("orders")
    .build();

// UPSERT: update an existing row or insert a new row.
Row row = stream.createRow(Stream.Operator.UPSERT);
row.setValue("txid", "order-001");
row.setValue("amount", 299.99);
row.setValue("status", "paid");
stream.apply(row);

// DELETE_IGNORE: delete the row and ignore the operation if the target row does not exist.
Row del = stream.createRow(Stream.Operator.DELETE_IGNORE);
del.setValue("txid", "order-001");
stream.apply(del);

stream.close();
```

---

## Selection Guide

| Scenario | Recommended interface |
|---|---|
| Scheduled batch ETL, hourly or daily | BulkloadStream |
| Kafka real-time consumption | RealtimeStream |
| High-frequency writes under 5 minutes | RealtimeStream |
| Primary-key table writes with UPSERT or DELETE | RealtimeStream CDC mode |

---

## Usage Limits

| Limit | BulkloadStream | RealtimeStream |
|---|---|---|
| Primary-key tables | Not supported | Supported in CDC mode |
| High-frequency writes under 5 minutes | Not recommended | Supported |
| Data visibility latency | Visible after `close()` | Visible after about 1 minute |
| Table Stream/Dynamic Table visibility | After `close()` | After about 1 minute |
| Schema changes | Recreate the stream | Stop the task and restart about 90 minutes after the schema change |
