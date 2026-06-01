# Lakehouse Volume File Management Guide

## Overview

Volume is Singdata Lakehouse's file storage and management object, supporting internal User Volumes and external External Volumes. With Volume, you can upload, download, list, and delete files directly in Lakehouse without external tools. This guide is organized by business scenario to help you quickly master Volume file operations.

### Quick Navigation

* [Upload Files to Volume](#upload-files-to-volume) -- Use PUT to import local files
* [List Volume Files](#list-volume-files) -- Use LIST to view directory contents
* [Download Files from Volume](#download-files-from-volume) -- Use GET to export files
* [Delete Volume Files](#delete-volume-files) -- Use REMOVE to clean up files
* [Query File Content Directly](#query-file-content-directly) -- Use SELECT FROM VOLUME to analyze files

***

## Relevant SQL Commands

| Command | Purpose | Applicable Scenario |
|------|------|----------|
| `PUT 'local_path' TO USER VOLUME FILE 'filename'` | Upload file | Import local CSV/Parquet into Volume |
| `LIST USER VOLUME 'path'` | List files | View Volume directory structure |
| `GET FROM USER VOLUME FILE 'filename' TO 'local_path'` | Download file | Export Volume files to local machine |
| `REMOVE USER VOLUME FILE 'filename'` | Delete file | Clean up temporary files in Volume |
| `SELECT * FROM VOLUME 'path'` | Query file | Read file content directly (supports CSV/JSON/Parquet) |

***

## Prerequisites

The following examples use Lakehouse's built-in User Volume:

```sql
-- View the current user's Volume path
SELECT CURRENT_USER();
-- User Volume path is typically: volume:user//~/
```

***

## Upload Files to Volume

Use the `PUT` command to upload local files to the User Volume.

```sql
-- Upload a local CSV file to Volume
PUT '/tmp/data_export.csv' TO USER VOLUME FILE 'data_export.csv';
```

**Result Notes**:
* After a successful upload, verify with the `LIST` command.
* Uploaded files are only visible to the current user (User Volume isolation).

***

## List Volume Files

Use the `LIST` command to view files and directories in a Volume.

```sql
-- List files in the root directory of User Volume
LIST USER VOLUME '/';
```

**Result Notes**:

| file_name | file_size | last_modified |
|-----------|-----------|---------------|
| data_export.csv | 1024 | 2024-06-01 10:00:00 |

> 💡 **Tip**: `LIST` supports wildcards, e.g., `LIST USER VOLUME '/data/*.csv'`.

***

## Download Files from Volume

Use the `GET` command to download files from Volume to your local machine.

```sql
-- Download a Volume file to local
GET FROM USER VOLUME FILE 'data_export.csv' TO '/tmp/downloaded_data.csv';
```

**Applicable Scenarios**:
* Data backup to local
* File exchange with external systems

***

## Delete Volume Files

Use the `REMOVE` command to delete files that are no longer needed in the Volume.

```sql
-- Delete a Volume file
REMOVE USER VOLUME FILE 'data_export.csv';
```

> ⚠️ **Note**: The `REMOVE` operation is irreversible; deleted files cannot be recovered via Time Travel.

***

## Query File Content Directly

Lakehouse supports directly querying files in Volume without first importing them into tables.

```sql
-- Query CSV file content
SELECT * FROM VOLUME 'volume:user//~/data_export.csv'
USING CSV OPTIONS ('header' = 'true');
```

**Supported Formats**:
* CSV / TSV
* JSON / JSONL
* Parquet / ORC
* Avro

> 💡 **Tip**: Direct querying is suitable for temporary data exploration. For frequent queries, first use `COPY INTO` to import into a table.

***

## Clean Up Test Data

After completing Volume validation, clean up uploaded files:

```sql
-- Delete test file
REMOVE USER VOLUME FILE 'data_export.csv';
```

***

## Notes

1. **Path Format**: User Volume paths start with `volume:user//~/`, External Volume paths start with `volume:ext_vol_name/`.
2. **File Size Limit**: Single file uploads should not exceed 1 GB; use external storage connections for very large files.
3. **Permission Isolation**: User Volumes are only visible to their creator; External Volumes can be configured with shared access.
4. **Query Performance**: Directly querying Volume files has lower performance than querying tables; importing first is recommended for production.
5. **Concurrent Writes**: `PUT` does not support concurrent writes to the same file; ensure file locks or serial operations.

***

## Related Documentation

* [Volume Object](volume-introduction.md)
* [PUT](put.md)
* [GET](get.md)
* [COPY INTO Import](copy-into-table.md)
