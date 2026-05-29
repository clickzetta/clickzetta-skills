## READ_KAFKA

**Syntax**
```SQL
SELECT ... FROM READ_KAFKA(
 'bootstrap',
 'topic',
'topic_pattern',
 'group_id', 
'STARTING_OFFSETS', 'ENDING_OFFSETS', 'STARTING_OFFSETS_TIMESTAMP', 'ENDING_OFFSETS_TIMESTAMP', 
'KEY_FORMAT', 
'VALUE_FORMAT', 
   0,
MAP()      
)
```

The `read_kafka` function is used to read data from Kafka. It supports the following parameters:

* **bootstrap**: Kafka server address, such as `1.2.3.1:9092,1.2.3.2:9092`.
* **topic**: Kafka topic name, multiple topics separated by commas, such as `topicA,topicB`.
* **topic\_patternt***: topic regex, not supported yet, leave it empty by default. For example: ''.
* **group\_id**: Kafka consumer group ID.
* **STARTING\_OFFSETS**: Specify the starting offset to read from, default is `earliest`.
* **ENDING\_OFFSETS**: Specify the ending offset to read to, default is `latest`.
* **STARTING\_OFFSETS\_TIMESTAMP**: Specify the timestamp for the starting offset.
* **ENDING\_OFFSETS\_TIMESTAMP**: Specify the timestamp for the ending offset.
* **KEY\_FORMAT**: Specify the format of the key to read, type is STRING and case-insensitive. Currently only supports raw format.
* **VALUE\_FORMAT**: Specify the format of the value to read, type is STRING and case-insensitive. Currently only supports raw format.
* **MAX\_ERROR\_NUMBER**: The maximum number of error rows allowed within the read window. Must be greater than or equal to 0. Default is 0, which means no error rows are allowed, range is 0-100000.
* **MAP()**: Parameters to be passed to Kafka, prefixed with kafka., directly use Kafka's parameters, can be found in Kafka. Format like MAP('kafka.security.protocol', 'PLAINTEXT', 'kafka.auto.offset.reset', 'earliest'), refer to [Kafka documentation](https://kafka.apache.org/documentation/#consumerconfigs) for values.

`read_kafka` result return value:

|                 |              |                      |
| --------------- | ------------ | -------------------- |
| Field           | Meaning      | Type                 |
| topic           | Kafka topic name | STRING               |
| partition       | Data partition ID | INT                  |
| offset          | Offset in Kafka partition | BIGINT               |
| timestamp       | Kafka message timestamp | TIMESTAMP\_LTZ       |
| timestamp\_type | Kafka message timestamp type | STRING               |
| headers         | Kafka message headers | MAP\<STRING, BINARY> |
| key             | Kafka key value | BINARY               |
| value           | Kafka value value | BINARY               |

**Notes**

* When using read\_kafka, please ensure network connectivity with Lakehouse.

**Examples**

```SQL
SELECT topic, partition, offset, `timestamp`, `timestamp_type`, headers,
           cast(key as string) as key_str, cast(value as string) as value_str
    FROM read_kafka(
        '1.2.3.1:9092,1.2.3.2:9092',
        'my_topic',
        'my_group',
        'earliest','latest','','',
        'RAW', 'RAW',
        0,
        MAP('kafka.security.protocol', 'PLAINTEXT', 'kafka.auto.offset.reset', 'earliest')
    )
```