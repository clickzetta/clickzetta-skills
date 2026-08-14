# PUT Command

The PUT command is used to upload local files from the client to a Lakehouse Volume object. It supports three target types: external Volume, TABLE VOLUME, and USER VOLUME.

## Execution Methods

PUT is a client-side command; the Lakehouse client tool reads the local file and transfers the data. The following execution methods are supported:

- [SQLLine command-line client](connect-with-cli.md)
- [DBeaver and other JDBC clients](eco_integration/dbeaver-lakehouse.md)

> ⚠️ **Note**: The Studio SQL editor does not support PUT. Studio runs server-side and cannot access files on your local machine; since PUT reads a local file to upload it, it can only be run from the client tools above.

## Syntax

```Plain
PUT 'local_path' [, 'local_path' [, ...]]
    TO
    { VOLUME volume_name | TABLE VOLUME table_name | USER VOLUME }
    [ SUBDIRECTORY 'dir' | FILE 'filename' ]
    [ option_key = option_value ] ...
```

## Parameter Description

| Parameter | Required | Description |
|-----------|----------|-------------|
| `local_path` | Yes | Local file path. Linux/macOS paths start with `/`; Windows uses forward slashes as separators. Enclose paths containing special characters in single quotes. Multiple paths can be specified, separated by commas. |
| `VOLUME volume_name` | One of three | Upload to the specified external Volume. |
| `TABLE VOLUME table_name` | One of three | Upload to the staging space of the specified table's TABLE VOLUME. |
| `USER VOLUME` | One of three | Upload to the current user's USER VOLUME. |
| `SUBDIRECTORY 'dir'` | No | Specifies the target subdirectory; the filename remains unchanged. Mutually exclusive with `FILE`. |
| `FILE 'filename'` | No | Specifies the target filename; can be used to rename the file during upload. Mutually exclusive with `SUBDIRECTORY`. |

## Examples

### Example 1: Upload a File to USER VOLUME

Upload a local file to the root of the current user's USER VOLUME:

```SQL
PUT '/Users/Downloads/data.csv' TO USER VOLUME;
```

After uploading, verify the file is in place:

```SQL
SHOW USER VOLUME DIRECTORY;
```

### Example 2: Upload to USER VOLUME with a Target Path

Upload a file to a subdirectory of USER VOLUME and rename it:

```SQL
PUT '/Users/Downloads/data.csv' TO USER VOLUME FILE 'import/data_2026.csv';
```

### Example 3: Upload to an External Volume and Rename

Upload a local archive to the external Volume named `hz_image_volume` and rename it:

```SQL
PUT '/Users/Downloads/cats_and_dogs.zip' TO VOLUME hz_image_volume FILE 'catsdogs.zip';
```

### Example 4: Upload to TABLE VOLUME and Then Import

Upload a file to the table's staging space, then import it using COPY INTO:

```SQL
-- Upload file to the table's TABLE VOLUME
PUT '/Users/Downloads/region.tbl' TO TABLE VOLUME tbl_region;

-- View staged files
SHOW TABLE VOLUME DIRECTORY tbl_region;

-- Import data from TABLE VOLUME
COPY INTO tbl_region FROM TABLE VOLUME tbl_region (id INT, name STRING)
USING CSV
OPTIONS (
    'header' = 'true',
    'lineSep' = '\n'
)
FILES ('region.tbl')
PURGE = TRUE;
```

## Notes

- The maximum size for a single file is **5 GB**.
- If a file with the same name already exists in the target Volume, the system will automatically overwrite it. Back up the existing file before uploading if needed.
- `SUBDIRECTORY` and `FILE` cannot be used at the same time.
- Uploading to an external Volume incurs object storage write fees for the associated cloud account.
- Executing the PUT command requires write permission on the target Volume.
