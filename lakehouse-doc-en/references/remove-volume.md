# REMOVE VOLUME FILE Command

The REMOVE command is used to delete files or directories from Lakehouse Volume objects. The deletion synchronously removes the actual data from the underlying object storage and **cannot be recovered**. It supports three target types: external Volume, TABLE VOLUME, and USER VOLUME. This command can be executed in Studio and the Lakehouse client.

## Syntax

```Plain
REMOVE
    { VOLUME volume_name | TABLE VOLUME table_name | USER VOLUME }
    { FILE 'file' | SUBDIRECTORY 'dir' }
```

## Parameter Description

| Parameter | Required | Description |
|------|----------|------|
| `VOLUME volume_name` | Choose one | Deletes files from the specified external Volume. |
| `TABLE VOLUME table_name` | Choose one | Deletes files from the TABLE VOLUME staging space of the specified table. |
| `USER VOLUME` | Choose one | Deletes files from the current user's USER VOLUME. |
| `FILE 'file'` | Choose one | Specifies the path of the file to delete (relative to the Volume root directory). |
| `SUBDIRECTORY 'dir'` | Choose one | Specifies the subdirectory to delete. All files under this directory will be recursively deleted. |

## Examples

### Example 1: Delete a Single File from USER VOLUME

```SQL
REMOVE USER VOLUME FILE 'university_info.csv';
```

### Example 2: Delete a File in a USER VOLUME Subdirectory

```SQL
REMOVE USER VOLUME FILE 'test_export/part00001.csv';
```

### Example 3: Delete an Entire Subdirectory in USER VOLUME

```SQL
REMOVE USER VOLUME SUBDIRECTORY 'test_export/';
```

### Example 4: Delete a File from an External Volume

```SQL
REMOVE VOLUME hz_image_volume FILE 'catsdogs.zip';
```

### Example 5: Delete a Subdirectory from an External Volume

```SQL
REMOVE VOLUME my_volume SUBDIRECTORY 'delta-format/uploaddelta';
```

### Example 6: Clean Up TABLE VOLUME Staging Files After Import

After data import is complete, delete staging files in TABLE VOLUME to free up storage space:

```SQL
-- View staging files
SHOW TABLE VOLUME DIRECTORY tbl_region;

-- Delete the imported file
REMOVE TABLE VOLUME tbl_region FILE 'region.tbl';
```

## Notes

- **Deletion is irreversible**. Before execution, confirm that the file path is correct. It is recommended to first use `SHOW USER VOLUME DIRECTORY` or `SHOW VOLUME DIRECTORY` to verify the file exists.
- When using `SUBDIRECTORY`, all files under that directory will be recursively deleted. Use with caution.
- Deleting files from an external Volume synchronously removes the actual data from the underlying object storage (OSS/COS/S3).
- Executing the REMOVE command requires write permission on the target Volume.
- You can combine this with Lakehouse scheduled tasks to automatically clean up imported staging files, reducing storage costs.
