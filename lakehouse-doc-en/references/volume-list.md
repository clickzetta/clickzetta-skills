# LIST Command

## Overview

The LIST command returns a list of files stored in an internal or external Volume within Lakehouse. This command can be executed in Studio and the Lakehouse client.

## Use Cases

* **Pre-import File Verification**: Before importing data files into a table, confirm that the files have been successfully uploaded to the Volume and check whether the file naming conventions are correct.
* **Post-export Confirmation**: After using COPY INTO to export data to a Volume, verify that all files are correctly generated and whether file sizes are reasonable.
* **Pre-cleanup Confirmation**: Before executing the REMOVE command to delete files from a Volume, use the LIST command to confirm the file list and avoid accidental operations.

## Syntax

```
LIST { VOLUME volume_name | TABLE VOLUME table_name | USER VOLUME } 
     [ SUBDIRECTORY 'subdir'| REGEXP = 'pattern' ]
```

## Parameters

* `VOLUME volume_name`: Lists all files in the specified external VOLUME.
* `TABLE VOLUME table_name`: Lists all files in the VOLUME space of the specified table.
* `USER VOLUME`: Lists all files in the current user's Volume space.
* `SUBDIRECTORY 'subdir'`: Optional parameter. Specifies a subdirectory within the Volume to list. This option helps narrow down the results.
* `REGEXP = 'pattern'`: Optional parameter. Specifies a regular expression pattern to filter the returned files, allowing you to precisely select files that match specific naming rules or formats.

## Examples

* List all files containing the digit "1" in the external VOLUME `foodimages`:

```
LIST VOLUME foodimages REGEXP = '.*1.*'
```

* List all files in the `t_search_log` subdirectory of the external VOLUME `parquet_files`:

```
LIST VOLUME parquet_files SUBDIRECTORY 't_search_log'
```

* List files ending with `c000` in the `t_search_log` subdirectory of the external VOLUME `parquet_file`:

```
LIST VOLUME parquet_file SUBDIRECTORY 't_search_log' REGEXP = '.*c000' ;
```

## Notes

* Users must have the `READ` permission on the corresponding Volume to execute the `LIST` command.
