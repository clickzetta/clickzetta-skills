# DESC PIPE

Views detailed information of a specific Pipe object.

## Syntax

```SQL
DESC PIPE [EXTENDED] <name>;
```

## Example

```
DESC PIPE EXTENDED kafka_pipe_stream;
+--------------------+-----------------------------------------------------+
|     info_name      |                     info_value                      |
+--------------------+-----------------------------------------------------+
| name               | kafka_pipe_stream                                   |
| creator            | UAT_TEST                                            |
| created_time       | 2025-03-05 10:40:55.405                             |
| last_modified_time | 2025-03-05 10:40:55.405                             |
| comment            |                                                     |
| properties         | ((virtual_cluster,test_alter))                      |
| copy_statement     | COPY INTO TABLE example.pipe_schema.sink_table ...  |
| pipe_status        | RUNNING                                             |
| output_name        | workspace.pipe_schema.sink_table                    |
| input_name         | kafka_table_stream:workspace.pipe_schema.stream1    |
| invalid_reason     |                                                     |
| pipe_latency       | {"kafka":{"lags":{"0":0},"offsetLag":0}}            |
+--------------------+-----------------------------------------------------+
```

## Related Documents

- [Pipe Full Syntax Reference](pipe-syntax.md)
- [Continuously Import Object Storage Data Using Pipe](pipe-storage-object.md)
- [Continuously Import Kafka Data Using read_kafka](pipe-kafka.md)
