# Flink Write Connector Detailed Reference

## Scope

The ClickZetta Flink Write Connector writes Flink streaming data to ClickZetta Lakehouse. When generating guidance for users or agents, prefer the Flink Table API / SQL path. Use the Stream API `IgsSink` only when the user explicitly needs to integrate a `DataStream` directly in Java code.

## Selection Guide

| Usage / connector | Use case | Key requirements |
|---|---|---|
| Stream API `IgsSink` | Write `DataStream<Row>` or POJOs directly from a Java job | You must define the field mapping and `RowCreate.Operator` yourself |
| `igs-dynamic-table` | Table API / SQL CDC, upsert, or retract writes | For primary-key tables, use `sink.parallelism = 1` |
| `igs-dynamic-table-append-only` | Write a changelog stream to a non-primary-key table in append-only mode | Must configure `mapping.operation.type.to`; the target field must be `STRING` |
| `igs-dynamic-table-multi` | Write one CDC stream to multiple target tables | Must configure schema/table mapping fields |
| `bulkload-dynamic-table` | BulkLoad writes for throughput-oriented batch ingestion | Requires BulkLoad-related `properties` |
| `bulkload-dynamic-table-append-only` | BulkLoad append-only writes | Must configure `mapping.operation.type.to` |

For regular CDC synchronization, prefer `igs-dynamic-table`. Consider `igs-dynamic-table-append-only` only when you need to preserve each changelog operation type or when the target table is not a primary-key table.

## Versions and Dependencies

Connector artifacts are split by Flink version. The current codebase provides modules for Flink 1.14, 1.15, 1.17, and 1.18.

| Flink version | Maven artifactId |
|---|---|
| 1.14.x | `igs-flink-connector-14` |
| 1.15.x | `igs-flink-connector-15` |
| 1.17.x | `igs-flink-connector-17` |
| 1.18.x | `igs-flink-connector-18` |

```xml
<dependency>
    <groupId>com.clickzetta</groupId>
    <artifactId>igs-flink-connector-15</artifactId>
    <version>Contact ClickZetta support for the version number</version>
</dependency>
```

Flink dependencies are usually provided by the Flink cluster or job runtime. Do not package them into the application jar unless your deployment explicitly requires it.

```xml
<dependency>
    <groupId>org.apache.flink</groupId>
    <artifactId>flink-streaming-java</artifactId>
    <version>1.15.0</version>
    <scope>provided</scope>
</dependency>
<dependency>
    <groupId>org.apache.flink</groupId>
    <artifactId>flink-table-api-java-bridge</artifactId>
    <version>1.15.0</version>
    <scope>provided</scope>
</dependency>
```

If the user uses an offline jar, add the connector jar that matches the Flink version to the Flink job classpath.

## Flink Table API: CDC / Primary-Key Tables

`igs-dynamic-table` writes according to Flink changelog semantics. It is suitable for MySQL CDC and other streams containing INSERT, UPDATE, and DELETE events. When the target table is a primary-key table, use `sink.parallelism = 1` to avoid out-of-order UPDATE / DELETE records for the same key.

```sql
CREATE TABLE lakehouse_orders_sink (
    order_id   INT,
    customer   STRING,
    amount     DOUBLE,
    status     STRING,
    updated_at TIMESTAMP(3),
    PRIMARY KEY (order_id) NOT ENFORCED
) WITH (
    'connector'        = 'igs-dynamic-table',
    'curl'             = 'igs:clickzetta://your_instance.your_gateway/default?username=user&password=***&schema=public',
    'schema-name'      = 'public',
    'table-name'       = 'orders',
    'sink.parallelism' = '1',
    'properties'       = 'authentication:true'
);
```

`curl` can also be a comma-separated list of controller addresses:

```sql
'curl' = 'host1:10086,host2:10086'
```

When `curl` uses controller addresses instead of an `igs:` or `jdbc:` URL, `instance-id` and `workspace` specify the workspace:

```sql
'instance-id' = '1',
'workspace'   = 'default'
```

## Flink Table API: Append-Only

`igs-dynamic-table-append-only` writes every upstream changelog record as an INSERT into the target table, and writes the original changelog operation type into the target Lakehouse field specified by `mapping.operation.type.to`. This field must exist in the target Lakehouse table and must be of type `STRING`; it usually does not need to appear in the Flink sink DDL input schema.

Operation type values written to the target field include:

- `INSERT`
- `UPDATE_BEFORE`
- `UPDATE_AFTER`
- `DELETE`

```sql
CREATE TABLE lakehouse_events_sink (
    event_id   BIGINT,
    user_id    BIGINT,
    event_type STRING,
    event_time TIMESTAMP(3)
) WITH (
    'connector'                 = 'igs-dynamic-table-append-only',
    'curl'                      = 'igs:clickzetta://your_instance.your_gateway/default?username=user&password=***&schema=public',
    'schema-name'               = 'public',
    'table-name'                = 'events',
    'mapping.operation.type.to' = 'op_type',
    'sink.parallelism'          = '4',
    'properties'                = 'authentication:true'
);
```

Note: the append-only connector requires `mapping.operation.type.to`. Even when the upstream stream only contains INSERT records, configure an operation type field explicitly to avoid DDL validation failures.

## Complete CDC Synchronization Example: MySQL to Lakehouse

```sql
CREATE TABLE mysql_orders_source (
    order_id   INT,
    customer   STRING,
    amount     DOUBLE,
    status     STRING,
    updated_at TIMESTAMP(3),
    PRIMARY KEY (order_id) NOT ENFORCED
) WITH (
    'connector'     = 'mysql-cdc',
    'hostname'      = 'mysql-host',
    'port'          = '3306',
    'username'      = 'cdc_user',
    'password'      = 'cdc_password',
    'database-name' = 'orders_db',
    'table-name'    = 'orders'
);

CREATE TABLE lakehouse_orders_sink (
    order_id   INT,
    customer   STRING,
    amount     DOUBLE,
    status     STRING,
    updated_at TIMESTAMP(3),
    PRIMARY KEY (order_id) NOT ENFORCED
) WITH (
    'connector'        = 'igs-dynamic-table',
    'curl'             = 'igs:clickzetta://your_instance.your_gateway/default?username=user&password=***&schema=public',
    'schema-name'      = 'public',
    'table-name'       = 'orders',
    'sink.parallelism' = '1',
    'properties'       = 'authentication:true'
);

INSERT INTO lakehouse_orders_sink
SELECT order_id, customer, amount, status, updated_at
FROM mysql_orders_source;
```

## Flink Table API: Multi-Table Writes

`igs-dynamic-table-multi` does not use a fixed `schema-name` / `table-name`. Instead, it reads the target schema and table from fields in the upstream data. Use it when a CDC stream contains multiple source tables and rows must be routed to different Lakehouse tables.

Required mapping parameters:

| Parameter | Description |
|---|---|
| `mapping.schema.type.to` | Field name that contains the target schema |
| `mapping.table.type.to` | Field name that contains the target table |
| `mapping.source.data.type.to` | Field name that contains the original data JSON when `cdc.data.mode` is `JSON` or `DEBEZIUM_JSON` |

```sql
CREATE TABLE multi_lakehouse_sink (
    target_schema STRING,
    target_table  STRING,
    payload       STRING
) WITH (
    'connector'                   = 'igs-dynamic-table-multi',
    'curl'                        = 'igs:clickzetta://your_instance.your_gateway/default?username=user&password=***&schema=public',
    'cdc.data.mode'               = 'JSON',
    'mapping.schema.type.to'      = 'target_schema',
    'mapping.table.type.to'       = 'target_table',
    'mapping.source.data.type.to' = 'payload',
    'sink.parallelism'            = '1',
    'properties'                  = 'authentication:true'
);
```

## `cdc.data.mode`

`igs-dynamic-table` and `igs-dynamic-table-multi` support the following data encoding modes:

| Value | Description | Additional requirement |
|---|---|---|
| `ROW` | Write by Flink row fields. This is the default value | None |
| `JSON` | Read source data JSON from a specified Flink row field, then write according to the target table schema | Must configure `mapping.source.data.type.to` |
| `DEBEZIUM_JSON` | Read Debezium JSON from a specified Flink row field, then write according to the target table schema | Must configure `mapping.source.data.type.to` |

If there is no clear need to preserve the original JSON, prefer the default `ROW` mode.

## Stream API Example

The Stream API is suitable when Java code writes a `DataStream<Row>` directly to Lakehouse. Field order is defined by the field name array in `RowOperationMapper`, and write semantics are defined by `RowCreate.Operator`.

```java
import com.clickzetta.platform.client.RowCreate;
import com.clickzetta.platform.client.api.FlushMode;
import com.clickzetta.platform.client.api.ProtocolType;
import com.clickzetta.platform.flink.connector.internal.mapper.single.RowOperationMapper;
import com.clickzetta.platform.flink.connector.internal.options.IgsTableInfo;
import com.clickzetta.platform.flink.connector.internal.options.IgsWriterOptions;
import com.clickzetta.platform.flink.connector.sink.IgsSink;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.types.Row;

// DataStream<Row> dataStream = ...

IgsWriterOptions writerOptions = IgsWriterOptions.builder()
    .withProtocolType(ProtocolType.V2)
    .withStreamUrl("igs:clickzetta://your_instance.your_gateway/default?username=user&password=***&schema=public")
    .withFlushMode(FlushMode.AUTO_FLUSH_BACKGROUND)
    .withFlushInterval(10 * 1000)
    .withMutationBufferMaxNum(3)
    .withMutationBufferLinesNum(8)
    .withProperties(new java.util.Properties() {{
      put("authentication", "true");
    }})
    .build();

IgsSink<Row> sink = new IgsSink<>(
    writerOptions,
    IgsTableInfo.from("public", "orders"),
    new RowOperationMapper(
        new String[]{"order_id", "status", "amount"},
        RowCreate.Operator.INSERT)
);

dataStream.addSink(sink).name("clickzetta-igs-sink");
```

The Stream API supports the following `RowCreate.Operator` values:

- `INSERT`
- `INSERT_IGNORE`
- `UPDATE`
- `UPSERT`
- `DELETE`
- `DELETE_IGNORE`

`UPDATE`, `UPSERT`, `DELETE`, and related semantics require the target table and primary-key capability to match. For ordinary append tables, prefer `INSERT`.

## Connection Addresses and Network Parameters

`curl` supports three forms:

| Form | Example | Description |
|---|---|---|
| Controller address | `host1:10086,host2:10086` | Connect to controllers directly. In this mode, `instance-id` / `workspace` can specify the workspace |
| IGS stream URL | `igs:clickzetta://instance.gateway/default?username=user&password=***&schema=public` | Gateway mode, commonly used in production |
| JDBC URL | `jdbc:clickzetta://instance.endpoint:8033/default?username=user&password=***&schema=public&use_http=true` | Available for HTTP / PrivateLink scenarios |

To pin worker addresses, configure `worker-addrs`:

```sql
'worker-addrs' = '10.109.5.140:10088,10.109.5.141:10088'
```

Common `properties` syntax:

```sql
'properties' = 'authentication:true,isInternal:true,isDirect:false'
```

Common properties:

| Property | Description |
|---|---|
| `authentication` | Whether to enable authentication. Production and UAT environments usually require it |
| `username` | Authentication username; can also be passed in `curl` query parameters |
| `password` | Authentication password; can also be passed in `curl` query parameters |
| `isInternal` | Whether to get an internal address in gateway mode. `true` means internal network |
| `isDirect` | Whether to connect directly to a worker pod |
| `getRegionUrl` | Cross-region gateway support. Usually not needed |
| `row.pool.support` | Whether to enable row reuse. Useful for reducing object creation in high-throughput scenarios |
| `row.pool.max.size` | Maximum row pool size. The implementation default is `20000` |
| `row.pool.type` | Row pool type. Supports `array` / `queue` |
| `schema.evolution.support` | Whether to enable schema evolution. Disabled by default |
| `string.bytes.encode.support` | Whether to encode strings as bytes. Disabled by default |
| `json.int.date.support` | Whether to support int date in JSON mode. Disabled by default |
| `rowData.jsonBytes.support` | Whether to read JSON from bytes in JSON mode. Disabled by default |

Network access reference:

| Access method | `isInternal` | `isDirect` | Description |
|---|---|---|---|
| Connect to IGS worker public SLB | `false` or omitted | `false` or omitted | Default public network access |
| Connect to IGS worker pod | `false` | `true` | Direct pod connection. Requires environment support |
| Connect to IGS worker internal SLB | `true` | `false` | VPC / internal network access |
| Connect to a fixed worker | `true` | Any value | Usually used with `worker-addrs` |

To access a different Lakehouse service, add `lh_service` to the end of `curl` or `streamUrl`:

```text
igs:clickzetta://instance.gateway/default?username=user&password=***&schema=public&lh_service=k8s
```

## Table API Parameters

### Base Parameters

| Parameter | Default | Description |
|---|---|---|
| `connector` | None | `igs-dynamic-table`, `igs-dynamic-table-append-only`, `igs-dynamic-table-multi`, etc. |
| `curl` | None | Controller address, `igs:` URL, or `jdbc:` URL |
| `worker-addrs` | Empty string | Explicit worker addresses. If omitted, worker addresses are obtained from the controller |
| `instance-id` | `1` | Lakehouse instance for controller-address mode |
| `workspace` | `default` | Workspace for controller-address mode |
| `schema-name` | None | Target schema for single-table writes. Not used by the multi connector |
| `table-name` | None | Target table for single-table writes. Not used by the multi connector |
| `tablet-num` | `1` | Tablet count. New jobs usually should not set this explicitly |
| `properties` | Empty map | Extended properties passed to the IGS SDK |
| `showDebugLog` | `false` | Whether to enable debug logs |
| `sink.parallelism` | Flink default | Sink parallelism. Use `1` for primary-key tables |

### Write and Encoding Parameters

| Parameter | Default | Description |
|---|---|---|
| `protocol.type` | `V2` | IGS protocol version. The current implementation only uses `V2` |
| `table-sink-mode` | `upsert` | Used by the legacy TableSink mode. Supports `upsert` / `retract` |
| `cdc.data.mode` | `ROW` | Supports `ROW`, `JSON`, and `DEBEZIUM_JSON` |
| `mapping.operation.type.to` | None | Required by append-only connectors. Writes the changelog operation type |
| `mapping.schema.type.to` | None | Required by the multi connector. Writes the target schema |
| `mapping.table.type.to` | None | Required by the multi connector. Writes the target table |
| `mapping.source.data.type.to` | None | Required when `cdc.data.mode` is `JSON` / `DEBEZIUM_JSON` |

## Buffer, Flush, and Failure Retry

Defaults are taken from the current IGS Java SDK / Flink connector implementation:

| Parameter | Default | Description |
|---|---|---|
| `flush.mode` | `AUTO_FLUSH_BACKGROUND` | Supports `AUTO_FLUSH_BACKGROUND`, `AUTO_FLUSH_SYNC`, and `MANUAL_FLUSH` |
| `mutation.flush.interval` | `10000` | Automatic flush interval in milliseconds |
| `mutation.buffer.space` | `10485760` | Maximum bytes per buffer. Default is 10 MB |
| `mutation.buffer.max.num` | `10` | Maximum number of buffers |
| `mutation.buffer.lines.num` | `1000` | Maximum rows per buffer |
| `error.type.handler` | `TerminateErrorTypeHandler` | By default, mutate failures terminate the job. When configured explicitly, use the full class name, for example `com.clickzetta.platform.client.api.ErrorTypeHandler$TerminateErrorTypeHandler` |
| `request.failed.retry.enable` | `true` | Whether to enable failed request retry |
| `request.failed.retry.times` | `5` | Maximum retry attempts |
| `request.failed.retry.internal.ms` | `5000` | Retry interval in milliseconds |
| `request.failed.retry.logDebug.enable` | `true` | Whether to emit retry debug logs |
| `request.failed.retry.status` | Empty string | Empty string means the SDK default retry status set is used |
| `ckp.abort.strict.mode` | `true` | Whether to mark the write as failed when a checkpoint is aborted |
| `tablet.rpc.heartbeat` | `false` | Whether to send a tablet heartbeat after checkpoint completion |

Supported `request.failed.retry.status` values:

- `THROTTLED`
- `FAILED`
- `NOT_FOUND`
- `INTERNAL_ERROR`
- `PRECHECK_FAILED`
- `STREAM_UNAVAILABLE`

Tuning example:

```sql
'flush.mode'                       = 'AUTO_FLUSH_BACKGROUND',
'mutation.flush.interval'          = '5000',
'mutation.buffer.space'            = '10485760',
'mutation.buffer.max.num'          = '10',
'mutation.buffer.lines.num'        = '1000',
'request.failed.retry.enable'      = 'true',
'request.failed.retry.times'       = '5',
'request.failed.retry.internal.ms' = '5000'
```

## Checkpoint Configuration

`IgsSink` flushes during checkpoints. In production, enable checkpointing and limit the number of concurrent checkpoints.

```java
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

env.enableCheckpointing(60000);
env.getCheckpointConfig().setCheckpointingMode(CheckpointingMode.EXACTLY_ONCE);
env.getCheckpointConfig().setMaxConcurrentCheckpoints(1);
env.getCheckpointConfig().setMinPauseBetweenCheckpoints(30000);
env.getCheckpointConfig().setCheckpointTimeout(120000);
```

If checkpoints are frequently aborted, first check IGS write latency, network connectivity, and buffer settings. Do not disable `ckp.abort.strict.mode` unless you explicitly accept non-strict failure behavior after checkpoint aborts.

## BulkLoad Connector

The BulkLoad connector is suitable for throughput-oriented batch ingestion. It is not the default choice for regular real-time CDC writes.

| Connector | Description |
|---|---|
| `bulkload-dynamic-table` | BulkLoad dynamic table writes |
| `bulkload-dynamic-table-append-only` | BulkLoad append-only writes. Must configure `mapping.operation.type.to` |

Common parameters:

| Parameter | Default | Description |
|---|---|---|
| `stream-id` | Empty string | BulkLoad stream id |
| `schema-name` | None | Target schema |
| `table-name` | None | Target table |
| `operator` | `APPEND` | Supports `APPEND`, `OVERWRITE`, and `UPSERT` |
| `partition.specs` | Empty string | Partition specs |
| `record.key` | Empty string | Comma-separated record keys |
| `prefer.internal.endpoint` | `false` | Whether to prefer the internal endpoint |
| `properties` | None | Properties required by BulkLoad |
| `sink.parallelism` | `1` | Write parallelism |

```sql
CREATE TABLE bulkload_orders_sink (
    order_id INT,
    amount   DOUBLE,
    status   STRING
) WITH (
    'connector'        = 'bulkload-dynamic-table',
    'schema-name'      = 'public',
    'table-name'       = 'orders',
    'operator'         = 'APPEND',
    'properties'       = 'username:user,password:***',
    'sink.parallelism' = '1'
);
```

## Validation Suggestions

- First use a minimal `CREATE TABLE ... WITH (...)` statement to verify that Flink SQL recognizes the connector parameters.
- For primary-key table CDC, verify INSERT, UPDATE, and DELETE separately and confirm the final target table state.
- For append-only scenarios, confirm that the `mapping.operation.type.to` field contains the expected changelog operation type.
- Temporarily reduce `mutation.buffer.lines.num` in test environments to trigger flushes sooner.
- After the job finishes, query the target Lakehouse table and check row counts, field mappings, and primary-key update results.

## FAQ

| Issue | Cause | Solution |
|---|---|---|
| Data written to a primary-key table is not updated | The append-only connector is being used | Switch to `igs-dynamic-table` |
| UPDATE / DELETE results are out of order | Sink parallelism is too high for a primary-key table | Set `sink.parallelism` to `1` |
| Append-only DDL validation fails | `mapping.operation.type.to` is missing | Add a `STRING` operation field and configure this parameter |
| JSON / Debezium JSON mode fails to start | `mapping.source.data.type.to` is missing | Add a field for the original JSON and configure this parameter |
| Checkpoint failure | Flush timeout, network blocking, or IGS write latency | Increase checkpoint timeout and check network and buffer settings |
| Connection timeout | `curl`, authentication, or internal/external network parameters do not match | Check `curl`, `properties`, `isInternal`, `isDirect`, and `worker-addrs` |
