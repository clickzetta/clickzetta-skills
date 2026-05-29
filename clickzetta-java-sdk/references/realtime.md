# RealtimeStream Real-Time Write Reference

> Best for: Kafka consumption and writes, high-frequency real-time ingestion with second-level queryability, and CDC writes to primary-key tables.

## Maven Dependency

```xml
<!-- See https://central.sonatype.com/artifact/com.clickzetta/clickzetta-java for the latest version. -->
<dependency>
    <groupId>com.clickzetta</groupId>
    <artifactId>clickzetta-java</artifactId>
    <version>2.0.0</version>
</dependency>
<dependency>
    <groupId>org.apache.kafka</groupId>
    <artifactId>kafka-clients</artifactId>
    <version>3.2.0</version>
</dependency>
```

## Usage Limits

- Real-time written data can be queried within seconds.
- Table Streams and Dynamic Tables need about **1 minute** before they can see the written data.
- When the table schema changes, stop the task and restart it about **90 minutes** after the schema change.

## Operation Modes

| Mode | Target table | Available operators |
|---|---|---|
| `RealTimeOperate.APPEND_ONLY` | Regular table | `Stream.Operator.INSERT` |
| `RealTimeOperate.CDC` | Primary-key table | `Stream.Operator.UPSERT`, `Stream.Operator.DELETE_IGNORE` |

## Write to a Regular Table: APPEND_ONLY

```java
// Recommended: explicit parameters. Supported in 2.0.0+ and does not depend on URL parsing.
ClickZettaClient client = ClickZettaClient.newBuilder()
    .service("cn-shanghai-alicloud.api.clickzetta.com")
    .instance("your_instance")
    .workspace(workspace)
    .schema(schema)
    .username(user)
    .password(password)
    .vcluster(vc)
    .build();
Options options = Options.builder().withMutationBufferLinesNum(10).build();

RealtimeStream stream = client.newRealtimeStreamBuilder()
    .operate(RowStream.RealTimeOperate.APPEND_ONLY)
    .options(options)
    .schema(schema)
    .table("events")
    .build();

// RealtimeStream uses column names, not indexes.
Row row = stream.createRow(Stream.Operator.INSERT);
row.setValue("id", 1);
row.setValue("event", "{\"type\":\"click\"}");
stream.apply(row);
```

## Write to a Primary-Key Table: CDC Mode

```java
// Create a primary-key table.
// CREATE TABLE orders (`txid` STRING PRIMARY KEY, `amount` DOUBLE, `status` STRING);

RealtimeStream stream = client.newRealtimeStreamBuilder()
    .operate(RowStream.RealTimeOperate.CDC)
    .options(options)
    .schema(schema)
    .table("orders")
    .build();

// UPSERT: update an existing row or insert a new row.
Row row = stream.createRow(Stream.Operator.UPSERT);
row.setValue("txid", "order-001");
row.setValue("amount", 299.99);
row.setValue("status", "paid");
stream.apply(row);

// DELETE_IGNORE: delete the row and ignore the operation if the target row does not exist.
Row delRow = stream.createRow(Stream.Operator.DELETE_IGNORE);
delRow.setValue("txid", "order-001");
stream.apply(delRow);
```

## Complete Example: Kafka to Lakehouse

### KafkaReader Class

```java
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import java.util.Collections;
import java.util.Properties;

public class KafkaReader {
    private KafkaConsumer<String, String> consumer;

    public KafkaReader() {
        Properties props = new Properties();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ConsumerConfig.GROUP_ID_CONFIG, "test-group");
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG,
            "org.apache.kafka.common.serialization.StringDeserializer");
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG,
            "org.apache.kafka.common.serialization.StringDeserializer");
        props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, "true");
        props.put(ConsumerConfig.AUTO_COMMIT_INTERVAL_MS_CONFIG, "1000");
        consumer = new KafkaConsumer<>(props);
    }

    public KafkaConsumer<String, String> readFromTopic(String topic) {
        consumer.subscribe(Collections.singleton(topic));
        return consumer;
    }
}
```

### Kafka2Lakehouse Main Class

```java
import com.clickzetta.client.ClickZettaClient;
import com.clickzetta.client.RealtimeStream;
import com.clickzetta.client.RowStream;
import com.clickzetta.platform.client.api.Options;
import com.clickzetta.platform.client.api.Row;
import com.clickzetta.platform.client.api.Stream;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import java.time.Duration;

public class Kafka2Lakehouse {
    private static ClickZettaClient client;
    private static final String password = "";
    private static final String table = "realtime_stream";
    private static final String workspace = "";
    private static final String schema = "public";
    private static final String user = "";
    private static final String vc = "default";
    static RealtimeStream realtimeStream;

    public static void main(String[] args) throws Exception {
        initialize();
        KafkaReader kafkaReader = new KafkaReader();
        final KafkaConsumer<String, String> consumer = kafkaReader.readFromTopic("lakehouse-stream");
        int i = 1;
        while (true) {
            ConsumerRecords<String, String> records = consumer.poll(Duration.ofSeconds(1));
            for (ConsumerRecord<String, String> record : records) {
                Row row = realtimeStream.createRow(Stream.Operator.INSERT);
                row.setValue("id", i++);
                row.setValue("event", record.value());
                realtimeStream.apply(row);
            }
        }
    }

    private static void initialize() throws Exception {
        Options options = Options.builder().withMutationBufferLinesNum(10).build();
        client = ClickZettaClient.newBuilder()
            .service("cn-shanghai-alicloud.api.clickzetta.com")
            .instance("your_instance")
            .workspace(workspace)
            .schema(schema)
            .username(user)
            .password(password)
            .vcluster(vc)
            .build();
        realtimeStream = client.newRealtimeStreamBuilder()
            .operate(RowStream.RealTimeOperate.APPEND_ONLY)
            .options(options)
            .schema(schema)
            .table(table)
            .build();
    }
}
```

## Key APIs

| API | Description |
|---|---|
| `realtimeStream.createRow(Stream.Operator.INSERT)` | Create an insert row for a regular table. |
| `realtimeStream.createRow(Stream.Operator.UPSERT)` | Create an upsert row for a primary-key table. |
| `realtimeStream.createRow(Stream.Operator.DELETE_IGNORE)` | Create a delete row for a primary-key table. |
| `row.setValue(String columnName, Object value)` | Set a value by column name, not by index. |
| `realtimeStream.apply(row)` | Send the row to the server. |
| `Options.builder().withMutationBufferLinesNum(n)` | Set the number of buffered rows. The default is 10. |

## BulkloadStream vs RealtimeStream

| Dimension | BulkloadStream | RealtimeStream |
|---|---|---|
| Column value setter | `setValue(int index, value)` | `setValue(String name, value)` |
| URL parameter | `virtualcluster=` | `vcluster=` |
| `createRow` argument | No argument | `Stream.Operator.INSERT/UPSERT/DELETE_IGNORE` |
| Suitable write frequency | Low frequency, >=5 minutes per batch | High frequency, second-level writes |
| Data visibility latency | Visible after `close()` | Visible after about 1 minute |
| Primary-key table support | Not supported | Supported in CDC mode |

## FAQ

| Issue | Cause | Solution |
|---|---|---|
| Connection fails | Wrong URL parameter name | RealtimeStream uses `vcluster=`, not `virtualcluster=`. |
| Column name not found | Column name is misspelled | Column names are case-sensitive and must match the table DDL. |
| Writes fail after a schema change | The old Stream instance cached the old schema | Stop the task and restart it about 90 minutes after the schema change. |
| Dynamic Table cannot see the data | Real-time writes have about 1 minute of confirmation latency | Query again after about 1 minute. |
