# Named Volume

A Named Volume is an **internal Volume explicitly created by the user**. Its data is stored in Lakehouse's internal object storage, so no external cloud storage account configuration is required. Like User Volumes and Table Volumes, Named Volumes are **internal Volumes**. The key difference is that a Named Volume is created manually by the user, who manages its lifecycle. It supports configurable sharing permissions, making it well suited for team collaboration.

## Comparison with Other Volume Types

| | User Volume | Table Volume | Named Volume | External Volume |
|---|---|---|---|---|
| **Category** | Internal Volume | Internal Volume | Internal Volume | External Volume |
| Creation | Automatic (per user) | Automatic (per table) | Manual `CREATE VOLUME` | Manual `CREATE EXTERNAL VOLUME` |
| Data storage location | Lakehouse internal | Lakehouse internal | Lakehouse internal | External OSS / COS / S3 |
| Lifecycle management | System-managed | System-managed | **User-managed** | User-managed |
| Shareable | No (user-private) | No (bound to table permissions) | Yes (can be granted to other users) | Yes |
| Use case | Personal temporary files | Table-associated files | Team shared file directory | Existing cloud storage data |

## Create and Manage

```sql
-- Create a Named Volume
CREATE VOLUME shared_files;

-- List all Volumes
SHOW VOLUMES;

-- View files in a Named Volume
SHOW VOLUME DIRECTORY shared_files;

-- Drop a Named Volume
DROP VOLUME shared_files;
```

## File Operations

```sql
-- Upload a local file to a Named Volume
PUT '/local/data.csv' TO VOLUME shared_files;

-- Query file contents
SELECT * FROM VOLUME shared_files
USING CSV OPTIONS('header' = 'true')
FILES('data.csv');

-- Import data into a table
COPY INTO my_table
FROM VOLUME shared_files
USING CSV OPTIONS('header' = 'true')
FILES('data.csv');

-- Export table data to a Named Volume
COPY INTO VOLUME shared_files
SUBDIRECTORY 'export/'
FROM my_table
FILE_FORMAT = (TYPE = PARQUET);

-- Delete a file
REMOVE VOLUME shared_files FILE 'data.csv';
```

## Permission Management

Named Volumes support granting access to other users or roles for team sharing:

```sql
-- Grant read permission to a custom read-only role
GRANT READ VOLUME ON VOLUME shared_files TO ROLE volume_reader;

-- Grant read and write permission
GRANT READ VOLUME, WRITE VOLUME ON VOLUME shared_files TO ROLE workspace_dev;
```

The `VOLUME` suffix in a privilege name is optional, but the full names are recommended. Dropping a Named Volume requires `DROP VOLUME` on that object. Creating a Named Volume requires `CREATE VOLUME` on its parent schema.

## Related Documentation

- [Internal Volume](om-internal-volume.md) — User Volume and Table Volume
- [External Volume](om-external-volume.md) — Mount OSS / COS / S3
- [CREATE VOLUME](create-volume.md) — Complete syntax reference
