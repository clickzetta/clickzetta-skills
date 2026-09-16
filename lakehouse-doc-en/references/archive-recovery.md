# Archive and Recovery

Archive and recovery commands convert partitioned-table data files to `IA` (infrequent access) or `ARCHIVE` storage and retrieve archived files when needed. `IA` files can be read directly; `ARCHIVE` files must be retrieved first, and the retrieval progress is monitored with `SHOW RESTORE STATUS`.

---

## In This Chapter

| Page | Description |
|------|-------------|
| [ARCHIVE TABLE](archive-table.md) | Archive a specified partition of a partitioned table to `IA`, `ARCHIVE`, or `STANDARD` storage |
| [RESTORE TABLE (Archive File Retrieval)](restore-archive-table.md) | Asynchronously retrieve archived files stored as `ARCHIVE` |
| [SHOW RESTORE STATUS](show-restore-status.md) | View the status of archive-file retrieval tasks |

## Common Operations

### Archive a Partition

```sql
-- Low-frequency data that still needs to remain online
ARCHIVE TABLE public.orders
PARTITION (dt = '2026-08-24')
SUBDIRECTORY 'ia/20260824/'
STORAGE_CLASS = 'IA';

-- Data retained for a long time and rarely accessed
ARCHIVE TABLE public.orders
PARTITION (dt = '2026-08-25')
SUBDIRECTORY 'archive/20260825/'
STORAGE_CLASS = 'ARCHIVE';
```

`ARCHIVE TABLE` applies to the specified partition of a partitioned table. A successful command completes the archive operation but does not delete data from the source table.

### Retrieve Archived Files

```sql
RESTORE TABLE public.orders
SUBDIRECTORY 'archive/20260825/';

-- Retrieval is asynchronous. Wait until the status is RESTORED.
SHOW RESTORE STATUS public.orders
SUBDIRECTORY 'archive/20260825/';
```

Only `ARCHIVE` files support `RESTORE TABLE`. `IA` files can be read directly without retrieval.

## Related Documentation

| Document | Description |
|----------|-------------|
| [ARCHIVE TABLE](archive-table.md) | Complete syntax, parameters, and limitations for archiving partitions |
| [RESTORE TABLE (Archive File Retrieval)](restore-archive-table.md) | Complete syntax and asynchronous processing details for retrieving archived files |
| [SHOW RESTORE STATUS](show-restore-status.md) | Retrieval status and status values |
| [Partitioned Tables](partition_table.md) | Create and manage partitioned tables |
| [Table Volume](internal_volume.md) | View the Table Volume associated with a table and its files |
