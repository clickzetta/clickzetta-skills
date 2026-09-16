# ARCHIVE TABLE

## Overview

`ARCHIVE TABLE` converts the data files in a specified partition of a partitioned table to `STANDARD`, `IA`, or `ARCHIVE` object-storage class and writes them to the table's Table Volume. Use this command to reduce storage costs for data that is accessed infrequently. Archiving does not delete data from the source table and does not depend on `data_retention_days`.

## Syntax

```Plain
ARCHIVE TABLE [<namespace>.]<table_name>
  PARTITION (<partition_key> = <partition_value>)
  SUBDIRECTORY '<path>'
  STORAGE_CLASS = '<storage_class>';
```

## Parameters

| Parameter | Description |
|-----------|-------------|
| `<namespace>` | Optional schema name. If omitted, the current schema is used. |
| `<table_name>` | Name of the partitioned table to archive. Non-partitioned tables are not supported. |
| `PARTITION` | Specifies the partition to archive. The partition key must belong to the target table. One partition can be specified per command. |
| `SUBDIRECTORY '<path>'` | Specifies the subdirectory under the target table's Table Volume where archived files are written. Use a separate directory for each archive, such as `archive/20260825/`. |
| `STORAGE_CLASS` | Specifies the object-storage class: `STANDARD`, `IA`, or `ARCHIVE` (case-insensitive). `IA` files can be read directly; `ARCHIVE` files require `RESTORE TABLE` before they can be read. |

> ⚠️ **Note**: A partition cannot be archived more than once. To archive it again, remove the existing archive files first.

## Examples

### Example 1: Prepare a partitioned table and test data

```sql
CREATE TABLE public.doc_archive_orders_20260829 (
  order_id BIGINT,
  amount DECIMAL(18,2)
) PARTITIONED BY (dt STRING);

INSERT INTO public.doc_archive_orders_20260829 PARTITION (dt = '2026-08-28')
VALUES (1, 12.34), (2, 56.78);

INSERT INTO public.doc_archive_orders_20260829 PARTITION (dt = '2026-08-29')
VALUES (3, 90.12);
```

The table contains two partitions: `2026-08-28` and `2026-08-29`.

### Example 2: Archive a partition as IA

```sql
ARCHIVE TABLE public.doc_archive_orders_20260829
PARTITION (dt = '2026-08-28')
SUBDIRECTORY 'ia/20260828/'
STORAGE_CLASS = 'IA';
```

The command runs synchronously. After it succeeds, the archive file is stored in the table's Table Volume and can be read directly.

### Example 3: Archive a partition as ARCHIVE

```sql
ARCHIVE TABLE public.doc_archive_orders_20260829
PARTITION (dt = '2026-08-29')
SUBDIRECTORY 'archive/20260829/'
STORAGE_CLASS = 'ARCHIVE';
```

The command runs synchronously. After it succeeds, the archive file is stored in the table's Table Volume. Run [RESTORE TABLE (Archive File Retrieval)](restore-archive-table.md) before reading this partition.

### Example 4: View archived files

```sql
SHOW TABLE VOLUME DIRECTORY public.doc_archive_orders_20260829;
```

The file listing from the example is:

| relative_path | size |
|---|---:|
| `archive/20260829/part00001` | 1832 |
| `ia/20260828/part00001` | 1850 |

`relative_path` is relative to the table's Table Volume. Record the archive job ID, partition key and value, archive time, and file listing together so that the archive can be checked and retrieved later.

## Notes

- Only partitioned tables are supported, and one partition can be specified per command.
- A single archive operation cannot contain more than 10,000 partition files. Reduce the scope or run compaction first when the file count is larger.
- The archive operation is synchronous. A successful response means that the specified partition has been archived.
- Archiving does not delete data from the source table. Delete the partition separately or configure a lifecycle policy if you need to release the source-table storage.
- `IA` files can be read directly and incur the corresponding object-storage request and data-transfer charges.
- `ARCHIVE` files cannot be read directly. Retrieve them with `RESTORE TABLE` first; retrieval and temporary standard-storage charges apply.
- The executing user needs `SELECT` permission on the target table.

## Related Documentation

- [Archive and Recovery](archive-recovery.md)
- [RESTORE TABLE (Archive File Retrieval)](restore-archive-table.md)
- [SHOW RESTORE STATUS](show-restore-status.md)
- [Partitioned Tables](partition_table.md)
- [Table Volume](internal_volume.md)
