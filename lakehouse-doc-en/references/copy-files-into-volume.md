# COPY FILES INTO VOLUME

## Overview

Copies **existing files verbatim** from one Volume to another (file content is preserved — not parsed or reformatted). Commonly used to move files between external Volumes (OSS/COS/S3), Managed Volumes, USER VOLUMEs, and TABLE VOLUMEs — for example, transferring an archived file from object storage into a table's staging area before importing it, or backing up files between Volumes.

Unlike `COPY INTO VOLUME` (which exports a table or query result as files), this command has a Volume as both source and destination, copies files as-is, does not involve table data, and does not take a `FILE_FORMAT`.

## Syntax

```Plain
COPY FILES INTO { VOLUME <volume_name> | TABLE VOLUME <table_name> | USER VOLUME }
    [ SUBDIRECTORY '<dest_path>' ]
FROM { VOLUME <volume_name> | TABLE VOLUME <table_name> | USER VOLUME }
    [ SUBDIRECTORY '<src_path>' ]
[ FILES = ( '<file_name>' [, ...] ) | REGEXP = '<pattern>' ]
```

## Parameters

* **Destination Volume (`INTO`)**: choose one of the three Volume types.
  * `VOLUME <volume_name>`: an external Volume (OSS/COS/S3) or a Managed Volume.
  * `TABLE VOLUME <table_name>`: the staging Volume of the specified table.
  * `USER VOLUME`: the current user's USER VOLUME.
  * `SUBDIRECTORY '<dest_path>'`: optional, destination subdirectory; when omitted, files are written to the root of the destination Volume.

* **Source Volume (`FROM`)**: choose one of the three Volume types; it may differ from the destination type (cross-type copy is supported).
  * `SUBDIRECTORY '<src_path>'`: optional, copies only files under the specified subdirectory of the source Volume.

* **File filter** (`FILES` and `REGEXP` are mutually exclusive; both optional):
  * `FILES = ( '<file_name>' [, ...] )`: specify files by exact name, relative to the source (sub)directory. If any file in the list does not exist, the whole operation fails with `CZLH-70002: File not found`.
  * `REGEXP = '<pattern>'`: match files by their relative path with a regular expression.

  > ⚠️ **Note**: The regex parameter must be written as `REGEXP = '<pattern>'` (with the equals sign), which differs from the import syntax `COPY INTO TABLE ... REGEXP '<pattern>'` (no equals sign).

  > 💡 **Tip**: When both `FILES` and `REGEXP` are omitted, **all** files under the source (sub)directory are copied recursively.

## Return Value

On success, returns a single `file` column listing the relative path of each copied file within the source Volume.

## Notes

* **The `FILES` keyword is required**: you must write `FILES` between `COPY` and `INTO`. Writing `COPY INTO VOLUME ... FROM VOLUME` is parsed as the table-export syntax and raises a syntax error.
* **Overwrites by default**: an existing file with the same name in the destination Volume is overwritten; the operation is idempotent on repeated runs. There is no `OVERWRITE` keyword.
* **Destination keeps only the file name**: the source subdirectory hierarchy is not retained; the file lands under the destination `SUBDIRECTORY`.
* **Missing source file fails**: if any file in the `FILES` list does not exist in the source, the whole command fails.

## Examples

Prerequisites: create two Volumes and place files in the source Volume.

```sql
CREATE VOLUME src_vol;
CREATE VOLUME dst_vol;

-- PUT must run in a client tool (e.g., sqlline); Studio runs server-side and cannot read local files, so PUT is not supported there.
PUT '/tmp/orders_2024_01.csv' TO VOLUME src_vol;
PUT '/tmp/orders_2024_02.csv' TO VOLUME src_vol;
PUT '/tmp/orders_2024_03.csv' TO VOLUME src_vol SUBDIRECTORY '2024/';
```

Copy a single file (simplest form):

```sql
COPY FILES INTO VOLUME dst_vol
FROM VOLUME src_vol
FILES = ('orders_2024_01.csv');
```

```
file
--------------------
orders_2024_01.csv
```

Copy multiple files into a subdirectory:

```sql
COPY FILES INTO VOLUME dst_vol SUBDIRECTORY 'archive/'
FROM VOLUME src_vol
FILES = ('orders_2024_01.csv', 'orders_2024_02.csv');
```

```
file
--------------------
orders_2024_01.csv
orders_2024_02.csv
```

Copy with a regular expression (note `REGEXP =` with the equals sign):

```sql
COPY FILES INTO VOLUME dst_vol SUBDIRECTORY 'archive/'
FROM VOLUME src_vol
REGEXP = 'orders_2024_0[12].csv';
```

```
file
--------------------
orders_2024_01.csv
orders_2024_02.csv
```

Copy from a subdirectory of the source Volume (the returned `file` is the source-relative path):

```sql
COPY FILES INTO VOLUME dst_vol SUBDIRECTORY 'from_2024/'
FROM VOLUME src_vol SUBDIRECTORY '2024/'
FILES = ('orders_2024_03.csv');
```

```
file
--------------------
2024/orders_2024_03.csv
```

Copy all files recursively when no filter is given:

```sql
COPY FILES INTO VOLUME dst_vol SUBDIRECTORY 'backup/'
FROM VOLUME src_vol;
```

```
file
--------------------
2024/orders_2024_03.csv
orders_2024_01.csv
orders_2024_02.csv
```

Copy across Volume types — copy a file from an external Volume to a USER VOLUME:

```sql
COPY FILES INTO USER VOLUME SUBDIRECTORY 'download/'
FROM VOLUME my_oss_volume
FILES = ('orders_2024_01.csv');
```

Copy a file into a table's TABLE VOLUME staging area, then import it with COPY INTO:

```sql
COPY FILES INTO TABLE VOLUME orders SUBDIRECTORY 'incoming/'
FROM VOLUME src_vol
FILES = ('orders_2024_01.csv');

-- Import from the TABLE VOLUME into the table
COPY INTO orders
FROM TABLE VOLUME orders
USING CSV OPTIONS('header' = 'true')
FILES ('orders_2024_01.csv');
```

Verify the result with `SHOW VOLUME DIRECTORY`:

```sql
SHOW VOLUME DIRECTORY dst_vol SUBDIRECTORY 'archive/';
```

```
relative_path                 size
----------------------------- ----
archive/orders_2024_01.csv    36
archive/orders_2024_02.csv    36
```

## Related Documentation

- [Export Data to VOLUME - COPY INTO VOLUME](from_lakehouse_to_volume.md): export a table or query result as files to a Volume
- [Import Data from VOLUME to Table - COPY INTO TABLE](copy-into-table.md): import files from a Volume into a table
- [Volume Introduction](volume-introduction.md): Volume concepts and operations
