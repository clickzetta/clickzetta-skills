# GET Command

The GET command is used to download files from a Lakehouse Volume object to the client's local path. It supports three source types: external Volume, TABLE VOLUME, and USER VOLUME.

## Execution Methods

GET is a client-side command; the Lakehouse client tool receives the data and writes it to the local file system. The following execution methods are supported:

- [SQLLine command-line client](connect-with-cli.md)
- [DBeaver and other JDBC clients](eco_integration/dbeaver-lakehouse.md)

> ⚠️ **Note**: The Studio SQL editor does not support GET. Studio runs server-side and cannot write files to your local machine; since GET downloads a file to the local filesystem, it can only be run from the client tools above.

## Syntax

```Plain
GET
    { VOLUME volume_name | TABLE VOLUME table_name | USER VOLUME }
    [ FILE 'file' ]
    TO 'local_path'
    [ option_key = option_value ] ...
```

## Parameter Description

| Parameter | Required | Description |
|-----------|----------|-------------|
| `VOLUME volume_name` | One of three | Download files from the specified external Volume. |
| `TABLE VOLUME table_name` | One of three | Download files from the staging space of the specified table's TABLE VOLUME. |
| `USER VOLUME` | One of three | Download files from the current user's USER VOLUME. |
| `FILE 'file'` | No | Specifies the file path to download (relative to the Volume root). If not specified, all files under the Volume root are downloaded. |
| `local_path` | Yes | Local destination path. Linux/macOS paths start with `/`; Windows uses forward slashes as separators. |

## Examples

### Example 1: Download a Specific File from USER VOLUME

```SQL
GET USER VOLUME FILE 'university_info.csv' TO '/Users/Downloads/';
```

### Example 2: Download a File from a Subdirectory of USER VOLUME

```SQL
GET USER VOLUME FILE 'test_export/part00001.csv' TO '/Users/Downloads/output/';
```

### Example 3: Download a File from an External Volume

```SQL
GET VOLUME hz_image_volume FILE 'catsdogs.zip' TO '/Users/Downloads/';
```

### Example 4: Export Table Data and Download Locally

First export the table data to USER VOLUME, then download it locally:

```SQL
-- Export table data to a USER VOLUME subdirectory
COPY INTO USER VOLUME SUBDIRECTORY 'tmp/' FROM TABLE mytable
FILE_FORMAT = (TYPE = CSV);

-- View the exported files
SHOW USER VOLUME DIRECTORY;
```

```
+---------------------------+------+---------------------+
| relative_path             | size | last_modified_time  |
+---------------------------+------+---------------------+
| tmp/part00001.csv         | 61   | 2026-05-09 06:34:53 |
+---------------------------+------+---------------------+
```

```SQL
-- Download the file locally
GET USER VOLUME FILE 'tmp/part00001.csv' TO '/Users/Downloads/';

-- Delete the temporary file from the Volume after downloading
REMOVE USER VOLUME FILE 'tmp/part00001.csv';
```

## Notes

- Downloading files from an external Volume incurs object storage download fees for the associated cloud account.
- Executing the GET command requires read permission on the source Volume.
- The directory specified by `local_path` must already exist on the client's local file system; the command does not create directories automatically.
- When downloading large files, network bandwidth and local disk space are the primary limiting factors. Confirm available space beforehand.
