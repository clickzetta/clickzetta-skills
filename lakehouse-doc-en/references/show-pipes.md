# SHOW PIPES

Lists all Pipe objects within a specified scope.

## Syntax

```SQL
-- List all Pipes in the current Schema
SHOW PIPES;
-- List all Pipes in a specified Schema
SHOW PIPES IN SCHEMA schema_name;
-- List all Pipes in a specified Workspace
SHOW PIPES IN WORKSPACE workspace_name;
```

## Return Column Description

| Column Name | Description |
|------|------|
| `pipe_name` | Pipe name |
| `pipe_kind` | Pipe type (object storage or Kafka) |
| `status` | Current status, e.g., `RUNNING`, `PAUSED`, `INVALID`, etc. |
| `copy_statement` | The COPY INTO statement associated with the Pipe |

## Related Documents

- [Pipe Full Syntax Reference](pipe-syntax.md)
- [Continuously Import Object Storage Data Using Pipe](pipe-storage-object.md)
- [Continuously Import Kafka Data Using read_kafka](pipe-kafka.md)
