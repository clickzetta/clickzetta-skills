# Internal Volume

An Internal Volume is a **file storage space automatically provided by the Lakehouse** — no setup required, ready to use out of the box. It is ideal for scenarios where you don't have a cloud object storage account or need a place to temporarily store files.

## Two Types of Internal Volumes

### User Volume

Every user automatically has a dedicated private storage space for uploading local files and importing them into tables. A User Volume is private to the user — other users cannot access it.

```sql
-- Upload a local file
PUT '/local/data.csv' TO USER VOLUME;

-- List uploaded files
SHOW USER VOLUME DIRECTORY;

-- Query file contents directly (no need to import into a table first)
SELECT * FROM USER VOLUME
USING CSV OPTIONS('header' = 'true')
FILES('data.csv');

-- Import data from User Volume into a table
COPY INTO my_table
FROM USER VOLUME
USING CSV OPTIONS('header' = 'true')
FILES('data.csv');

-- Download a file to local
GET USER VOLUME FILE 'data.csv' TO '/local/output/';

-- Delete a file
REMOVE USER VOLUME FILE 'data.csv';
```

### Table Volume

Every table is automatically associated with a dedicated storage space that exists alongside the table. A Table Volume **does not store the table's live data** (table data is managed internally by the system). Instead, it serves as a file storage area bound to the table, for manually exporting or importing files.

Operations on a Table Volume require the corresponding table's permissions.

```sql
-- List files in a Table Volume
SHOW TABLE VOLUME DIRECTORY my_table;
-- Example result (empty for a newly created table):
-- +---------------+-----+------+--------------------+
-- | relative_path | url | size | last_modified_time |
-- +---------------+-----+------+--------------------+
-- (empty)

-- Export table data to Table Volume (backup scenario)
COPY INTO TABLE VOLUME my_table
SUBDIRECTORY 'backup/'
FROM my_table
FILE_FORMAT = (TYPE = PARQUET);

-- List files after export
SHOW TABLE VOLUME DIRECTORY my_table;
-- Example result:
-- +---------------------------+-----+------+----------------------------+
-- | relative_path             | url | size | last_modified_time         |
-- +---------------------------+-----+------+----------------------------+
-- | backup/part00001.parquet  |     | 1296 | 2026-05-22T13:24:11.000Z   |
-- +---------------------------+-----+------+----------------------------+

-- Query file contents in the Table Volume
SELECT * FROM TABLE VOLUME my_table
USING PARQUET SUBDIRECTORY 'backup/';

-- Import data from Table Volume into a table
COPY INTO my_table
FROM TABLE VOLUME my_table
USING PARQUET SUBDIRECTORY 'backup/';
```

> ⚠️ **Note**: `SHOW VOLUME DIRECTORY my_table` will produce an error (the system will attempt to find a Named Volume with that name). To list a Table Volume's contents, you must use `SHOW TABLE VOLUME DIRECTORY my_table`.

## Choosing Between Volume Types

| Scenario | Recommended |
|------|------|
| No cloud storage account; need to upload files | User Volume |
| Backup/export files tied to a specific table | Table Volume |
| Team-shared internal storage space | [Named Volume](om-named-volume.md) (`CREATE VOLUME`) |
| Already have OSS/COS/S3 and need direct access | [External Volume](om-external-volume.md) |

## Related Documentation

- [Named Volume](om-named-volume.md) — Manually created team-shared storage
- [External Volume](om-external-volume.md) — Mounting OSS / COS / S3
- [internal_volume.md](internal_volume.md) — Complete operations reference
