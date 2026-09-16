# RESTORE TABLE (Archive File Retrieval)

## Overview

This form of `RESTORE TABLE` asynchronously retrieves `ARCHIVE` files from a table's Table Volume and restores them to readable standard storage. It retrieves archive files only; it does not roll a table back to a historical version. To roll back a historical version, use the `RESTORE TABLE ... TO TIMESTAMP AS OF` syntax.

## Syntax

```Plain
RESTORE TABLE [<namespace>.]<table_name>
  SUBDIRECTORY '<path>';
```

## Parameters

| Parameter | Description |
|-----------|-------------|
| `<namespace>` | Optional schema name. If omitted, the current schema is used. |
| `<table_name>` | Name of the table containing the archive files. The files must be in this table's Table Volume. |
| `SUBDIRECTORY '<path>'` | Specifies the archive-file subdirectory to retrieve. Use the same path that was specified in `ARCHIVE TABLE`. |

> ⚠️ **Note**: Only `ARCHIVE` files support this command. `IA` files can be read directly and cannot be retrieved.

## Examples

### Example 1: Prepare an ARCHIVE file

```sql
CREATE TABLE public.doc_archive_orders_20260829 (
  order_id BIGINT,
  amount DECIMAL(18,2)
) PARTITIONED BY (dt STRING);

INSERT INTO public.doc_archive_orders_20260829 PARTITION (dt = '2026-08-29')
VALUES (3, 90.12);

ARCHIVE TABLE public.doc_archive_orders_20260829
PARTITION (dt = '2026-08-29')
SUBDIRECTORY 'archive/20260829/'
STORAGE_CLASS = 'ARCHIVE';
```

After the archive command succeeds, the Table Volume contains the `archive/20260829/` subdirectory.

### Example 2: Submit the retrieval task

```sql
RESTORE TABLE public.doc_archive_orders_20260829
SUBDIRECTORY 'archive/20260829/';
```

The command returns the submission result for each file. For example:

| file | status |
|---|---|
| `archive/20260829/part00001` | `{"message":"","success":true}` |

`success=true` means that the retrieval task was submitted; it does not mean that retrieval has completed.

### Example 3: Check the retrieval result

```sql
SHOW RESTORE STATUS public.doc_archive_orders_20260829
SUBDIRECTORY 'archive/20260829/';
```

While retrieval is in progress, the file status can be:

| file | state |
|---|---|
| `archive/20260829/part00001` | `{"status":"RESTORING"}` |

After the task completes, the status becomes:

| file | state |
|---|---|
| `archive/20260829/part00001` | `{"status":"RESTORED"}` |

Read or import files only after their status is `RESTORED`.

## Notes

- Retrieval is asynchronous. A successful command response means only that the task was submitted.
- Use [SHOW RESTORE STATUS](show-restore-status.md) to confirm that files are `RESTORED` before reading them.
- Only `ARCHIVE` files support retrieval; `IA` files do not.
- A single retrieval operation cannot contain more than 10,000 partition files.
- Retrieval incurs object-storage retrieval charges and temporary standard-storage charges.
- The executing user needs `SELECT` permission on the target table.

## Related Documentation

- [Archive and Recovery](archive-recovery.md)
- [ARCHIVE TABLE](archive-table.md)
- [SHOW RESTORE STATUS](show-restore-status.md)
- [Table Volume](internal_volume.md)
