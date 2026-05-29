# ALTER PIPE

Modifies the execution state or configuration properties of a Pipe.

## Pause and Start Pipe

Controls the execution state of a Pipe:

```SQL
-- Pause Pipe
ALTER PIPE pipe_name SET PIPE_EXECUTION_PAUSED = true;

-- Start Pipe
ALTER PIPE pipe_name SET PIPE_EXECUTION_PAUSED = false;
```

## Modify Pipe Properties

Modifies the configuration properties of a Pipe. Only one property can be modified at a time. To modify multiple properties, execute the `ALTER` command multiple times.

```SQL
ALTER PIPE pipe_name SET
    [VIRTUAL_CLUSTER = 'virtual_cluster_name']
    | [BATCH_INTERVAL_IN_SECONDS = '']
    | [BATCH_SIZE_PER_KAFKA_PARTITION = '']
    | [MAX_SKIP_BATCH_COUNT_ON_ERROR = '']
    | [COPY_JOB_HINT = ''];
```

**Example:**

```SQL
-- Modify compute cluster
ALTER PIPE pipe_name SET VIRTUAL_CLUSTER = 'default';
-- Set COPY_JOB_HINT
ALTER PIPE pipe_name SET COPY_JOB_HINT = '{"cz.mapper.kafka.message.size": "2000000"}';
```

## Related Documents

- [Pipe Full Syntax Reference](pipe-syntax.md)
- [Continuously Import Object Storage Data Using Pipe](pipe-storage-object.md)
- [Continuously Import Kafka Data Using read_kafka](pipe-kafka.md)
