# SHOW RESTORE STATUS

## Overview

`SHOW RESTORE STATUS` shows the status of archive-file retrieval tasks submitted by `RESTORE TABLE`. Because retrieval is asynchronous, run this command after submitting `RESTORE TABLE` and confirm that files have changed from `RESTORING` to `RESTORED` before reading or importing them.

## Syntax

```Plain
SHOW RESTORE STATUS [<namespace>.]<table_name>
  SUBDIRECTORY '<path>';
```

## Parameters

| Parameter | Description |
|-----------|-------------|
| `<namespace>` | Optional schema name. If omitted, the current schema is used. |
| `<table_name>` | Name of the table for which `RESTORE TABLE` was executed. |
| `SUBDIRECTORY '<path>'` | Specifies the archive-file subdirectory to inspect. Use the same path that was specified in `RESTORE TABLE`. |

## Examples

### Example 1: Check files that are being retrieved

```sql
SHOW RESTORE STATUS public.doc_archive_orders_20260829
SUBDIRECTORY 'archive/20260829/';
```

While retrieval is in progress, the result can be:

| file | state |
|---|---|
| `archive/20260829/part00001` | `{"status":"RESTORING"}` |

### Example 2: Confirm that retrieval is complete

Run the same query again until the status becomes `RESTORED`:

```sql
SHOW RESTORE STATUS public.doc_archive_orders_20260829
SUBDIRECTORY 'archive/20260829/';
```

| file | state |
|---|---|
| `archive/20260829/part00001` | `{"status":"RESTORED"}` |

Only files with the `RESTORED` status can be read as data. The current response contains `file` and `state` columns; `state` is a JSON string containing the status.

## Notes

- This command reports retrieval tasks for archive files submitted by `RESTORE TABLE`; it does not report Time Travel historical-version recovery.
- Do not read a file while its status is `RESTORING`.
- When retrieval completes, the status is `RESTORED`. If retrieval fails, check the returned status and job information before resubmitting.
- `SUBDIRECTORY` must match the path used for the retrieval task. Use a separate subdirectory for each archived partition.
- `IA` files do not support `RESTORE TABLE` and therefore do not apply to this command.

## Related Documentation

- [Archive and Recovery](archive-recovery.md)
- [ARCHIVE TABLE](archive-table.md)
- [RESTORE TABLE (Archive File Retrieval)](restore-archive-table.md)
