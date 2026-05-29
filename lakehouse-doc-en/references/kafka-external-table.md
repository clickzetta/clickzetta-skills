# Kafka External Table

## Overview

**[Preview Release] This feature is currently in public preview release.**

This document mainly introduces how to create an external table in SQL that connects to the Kafka message queue system. By defining an external table, you can easily read data streams from Kafka and query and analyze these data streams as tables.

## Create Storage Connection

First, you need to create a storage connection to connect to the Kafka server. Currently, connections requiring certificates are not supported.

### Syntax
```sql
CREATE STORAGE CONNECTION connection_name
    TYPE kafka
    BOOTSTRAP_SERVERS = ['server1:port1', 'server2:port2', ...]
    SECURITY_PROTOCOL = 'PLAINTEXT';
```
### Parameter Description

* **connection\_name**: The name of the connection, used for subsequent references.
* **TYPE**: The type of connection, here it is `kafka`.
* **BOOTSTRAP\_SERVERS**: The address list of the Kafka cluster, formatted as `['host1:port1', 'host2:port2', ...]`.
* **SECURITY\_PROTOCOL**: Security protocol, can be `PLAINTEXT`, etc.

## Create External Table

After creating a storage connection, you can define an external table to read data from Kafka.

### Syntax
```sql
CREATE EXTERNAL TABLE IF NOT EXISTS external_table_name (
 `topic` string,
 `partition` int,
 `offset` bigint,
 `timestamp` timestamp_ltz,
 `timestamp_type` string,
`headers` map<string, string>,
 `key` binary, `value` binary)
USING kafka
CONNECTION connection_name
OPTIONS (
    'group_id' = 'consumer_group',
    'topics' = 'topic_name',
    'starting_offset' = 'earliest' -- Optional, default value is earliest
);
```
### Parameter Description

* **external\_table\_name**: The name of the external table.
* **Field Description**

| Field            | Meaning                                                                            | Type                   |
| ---------------- | ---------------------------------------------------------------------------------- | ---------------------- |
| topic            | Kafka topic name                                                                   | STRING                 |
| partition        | Data partition ID                                                                  | INT                    |
| offset           | Offset in the Kafka partition                                                      | BIGINT                 |
| timestamp        | Kafka message timestamp                                                            | TIMESTAMP\_LTZ         |
| timestamp\_type  | Kafka message timestamp type                                                       | STRING                 |
| headers          | Kafka message headers                                                              | MAP\<STRING, BINARY>   |
| key              | Column name of the message key, type is `binary`. You can convert the binary type to a readable string using type conversion such as `cast(key_column as string)` | BINARY |
| value            | Column name of the message body, type is `binary`. You can convert the binary type to a readable string using type conversion such as `cast(value_column as string)` | BINARY |

* **USING kafka**: Specify using Kafka as the data source.
* **OPTIONS**:
  * **group\_id**: Kafka consumer group ID.
  * **topics**: Kafka topic name.
  * **starting\_offset**: Starting offset, default is `earliest`, can be `earliest` or `latest`.
  * **ending\_offset**: Ending offset, default is `latest`, can be `earliest` or `latest`.
  * **cz.kafka.seek.timeout.ms**: Kafka seek timeout (milliseconds).
  * **cz.kafka.request.retry.times**: Kafka request retry count.
  * **cz.kafka.request.retry.intervalMs**: Kafka request retry interval (milliseconds).
* **CONNECTION**: Specify the previously created storage connection name.

### Example

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS test_kafka_table (key binary, value binary NOT NULL)
USING kafka
OPTIONS (
    'group_id' = 'test_consumer',
    'topics' = 'commit_log_all_bj_env'
) CONNECTION test_kafka_conn;

SELECT cast(key as string), cast(value as string) FROM test_kafka_table LIMIT 10;

-- Convert to JSON to extract specific fields
SELECT cast(key as string),
parse_json(cast(value as string))['id'] AS id,
parse_json(cast(value as string))['name'] AS name
FROM test_kafka_table LIMIT 10;
```
