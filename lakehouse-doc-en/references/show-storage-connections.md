# SHOW STORAGE CONNECTIONS

## Overview

Lists all Storage Connections (object storage connection configurations) in the current instance, including OSS, S3, COS, and other types.

## Syntax

```Plain
SHOW STORAGE CONNECTIONS [ LIKE '<pattern>' ]
```

## Parameters

`LIKE '<pattern>'`: Optional. Filters results by name. Supports `%` (matches any sequence of characters) and `_` (matches a single character) wildcards.

## Return Columns

| Column | Type | Description |
|--------|------|-------------|
| `name` | STRING | Storage Connection name |
| `category` | STRING | Always `STORAGE` |
| `type` | STRING | Storage type: `OSS` / `S3` / `COS` |
| `enabled` | STRING | Status: `ENABLED` / `DISABLED` |
| `created_time` | TIMESTAMP | Creation time |

## Examples

```SQL
-- List all Storage Connections
SHOW STORAGE CONNECTIONS;

-- Filter by name
SHOW STORAGE CONNECTIONS LIKE '%oss%';
```

## Related Documentation

- [Create Storage Connection](create-storage-connection.md)
- [SHOW VOLUMES](show-volume.md)
- [SHOW CONNECTIONS](show-connections.md)
