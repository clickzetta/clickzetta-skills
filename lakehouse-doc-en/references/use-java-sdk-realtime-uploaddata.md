# Realtime Data Upload Using Java SDK to Read Kafka Data

This document details how to use the Java SDK to write data into Lakehouse in real-time, suitable for business scenarios requiring real-time data stream processing, especially for developers familiar with Java. This example uses Kafka as the data source to demonstrate how to read Kafka data and write it through Lakehouse's RealtimeStream interface. If you do not have special requirements for reading Kafka data, it is recommended to use Lakehouse Studio data integration, which provides visual monitoring and improves data management transparency.

## Reference Documents

[Java SDK Real-time Data Upload](java_reference/realtime-upload.md)

### Application Scenarios

* Suitable for business scenarios requiring real-time data stream processing.
* Suitable for developers familiar with Java and needing custom logic processing.

### Usage Restrictions

* Real-time written data can be queried at the second level.
* When the table structure changes, the real-time writing task needs to be stopped and restarted about 90 minutes after the change.
* Table stream, materialized view, and dynamic table can only display committed data. Data written by real-time tasks needs to wait for 1 minute to be confirmed, so table stream also needs to wait for 1 minute to see it.

## Use Case

This example uses Kafka's Java client to read data and calls Lakehouse's RealtimeStream interface to write it.

### Environment Preparation

* Have a Kafka cluster (this demonstration uses a locally built Kafka), create a Topic 'lakehouse-stream'
  * ```SQL
    bin/kafka-topics.sh --create --topic lakehouse-stream --bootstrap-server localhost:9092
    ```
* The data format is JSON, use the Kafka command line to produce data:
* ```SQL
    {"id": 1, "name": "John Doe", "email": "johndoe@example.com", "isActive": true}
    --kafka producer command line
    bin/kafka-console-producer.sh --topic lakehouse-stream --bootstrap-server localhost:9092
  ```
* Create a Table on the Lakehouse
  * ```SQL
    create table realtime_stream(id int,event json);
    ```

### Developing with Java Code

#### Maven Dependencies

Add the following dependencies to the project's `pom.xml` file. The latest lakehouse Maven dependencies can be found in the [Maven repository](https://central.sonatype.com/artifact/com.clickzetta/clickzetta-java).

```SQL
<dependency>
    <groupId>com.clickzetta</groupId>
    <artifactId>clickzetta-java</artifactId>
    <version>1.3.1</version>
</dependency>
<!-- https://mvnrepository.com/artifact/org.apache.kafka/kafka-clients -->
<dependency>
    <groupId>org.apache.kafka</groupId>
    <artifactId>kafka-clients</artifactId>
    <version>3.2.0</version>
</dependency>
```

#### Writing Java Code

1. **Define Kafka Connection Class**: Create a `KafkaReader` class to configure the Kafka consumer.
2. **Consume Kafka and Write to Lakehouse**: Create a `Kafka2Lakehouse` class to implement the logic of reading data from Kafka and writing it to the Lakehouse via RealtimeStream.

Define a Kafka connection class. The Java code configuration for Kafka can be referenced from the [Kafka official website](https://docs.confluent.io/kafka-clients/java/current/overview.html)

```SQL
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import java.util.Collections;
import java.util.Properties;
// Create a consumer class
public class KafkaReader {
    // Define a Kafka consumer object
    private KafkaConsumer<String, String> consumer;
    // Define a constructor to initialize the consumer's configuration
    public KafkaReader() {
        // Create a Properties object to store the consumer's configuration information
        Properties props = new Properties();
        // Specify the address of the Kafka cluster to connect to
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        // Specify the consumer group to which the consumer belongs
        props.put(ConsumerConfig.GROUP_ID_CONFIG, "test-group");
        // Specify the deserializer for the consumer's key and value
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, "org.apache.kafka.common.serialization.StringDeserializer");
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, "org.apache.kafka.common.serialization.StringDeserializer");
        // Specify the consumer's auto offset commit policy
        props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, "true");
        // Specify the consumer's auto offset commit interval
        props.put(ConsumerConfig.AUTO_COMMIT_INTERVAL_MS_CONFIG, "1000");
        // Create a Kafka consumer object using the configuration information
        consumer = new KafkaConsumer<>(props);
    }
    // Define a method to read data from the specified topic
    public KafkaConsumer<String, String> readFromTopic(String topic) {
        consumer.subscribe(Collections.singleton(topic));
        return consumer;
    }
}
```

Consuming Kafka and Writing to Lakhouse

```SQL

import com.clickzetta.client.ClickZettaClient;
import com.clickzetta.client.RealtimeStream;
import com.clickzetta.client.RowStream;
import com.clickzetta.platform.client.api.Options;
import com.clickzetta.platform.client.api.Row;
import com.clickzetta.platform.client.api.Stream;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;

import java.text.MessageFormat;
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
    static KafkaReader kafkaReader;
    // Read Topic and write to Lakehouse
    public static void main(String[] args) throws Exception {
        initialize();
        kafkaReader = new KafkaReader();
        final KafkaConsumer<String, String> consumer = kafkaReader.readFromTopic("lakehouse-stream");
        // Start consuming messages
        while (true) {
            int i = 1;
            try {
                ConsumerRecords<String, String> records = consumer.poll(Duration.ofSeconds(1));
                for (ConsumerRecord<String, String> record : records) {
                    Row row = realtimeStream.createRow(Stream.Operator.INSERT);
                    i++;
                    row.setValue("id", i);
                    row.setValue("event", record.value());

                    realtimeStream.apply(row);
                }
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        }
    }
    // Initialize Lakehouse client and realtimeStream
    private static void initialize() throws Exception {
        String url = MessageFormat.format("jdbc:clickzetta://jnsxwfyr.uat-api.clickzetta.com/{0}?" + "schema={1}&username={2}&password={3}&vcluster={4}", workspace, schema, user, password, vc);
        Options options = Options.builder().withMutationBufferLinesNum(10).build();
        client = ClickZettaClient.newBuilder().url(url).build();
        realtimeStream = client.newRealtimeStreamBuilder().operate(RowStream.RealTimeOperate.APPEND_ONLY).options(options).schema(schema).table(table).build();
    }
}
```

^
