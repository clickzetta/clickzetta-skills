# Internal Volume

Internal Volume is **automatically provided file storage space** in Lakehouse. No creation is needed — it is available out of the box. It is suitable for scenarios where you do not have a cloud object storage account or need temporary file storage.

## Two Types of Internal Volume

### User Volume

Each user automatically has a dedicated storage space for uploading local files and importing them into tables.

```sql
-- Upload a local file
PUT '/local/data.csv' TO USER VOLUME;

-- View uploaded files
SHOW USER VOLUME DIRECTORY;

-- Import data from User Volume
COPY INTO my_table
FROM USER VOLUME
USING CSV OPTIONS('header'='true')
FILES('data.csv');

-- Download a file to local
GET USER VOLUME FILE 'data.csv' TO '/local/output/';
```

### Table Volume

Each table is automatically associated with a storage space for managing its data files. This is typically used internally by the system; users generally do not need to operate it directly.

## Choosing Between Internal and External Volume

| Scenario | Recommendation |
|------|------|
| No cloud storage account, need to upload files | User Volume |
| Already have OSS/COS/S3, need direct access | [External Volume](om-external-volume.md) |
| Team-shared internal storage space | Named Volume (`CREATE VOLUME`) |

## Related Documents

- [Internal Volume Details](internal_volume.md)
- [External Volume](om-external-volume.md)
