# Create VOLUME to Access AWS S3 Data:

## Prerequisites:

After the STORAGE CONNECTION is created, you can create a VOLUME object to access object storage data.

```sql
CREATE EXTERNAL VOLUME aws_s3_volume_arn
  LOCATION 's3://cz-udf-user/'
  USING CONNECTION aws_bj_conn_arn
  DIRECTORY = (
    ENABLE=true
  )
  RECURSIVE = true;
```

### View Detailed Information of Created VOLUME Objects

```SQL
DESC VOLUME aws_s3_volume_arn
```

### Access S3 to View Files Under the VOLUME Path

```SQL
SHOW VOLUME DIRECTORY aws_s3_volume_arn;
```

### Store the file metadata of the VOLUME directory to Lakehouse and view it

```
ALTER VOLUME aws_s3_volume_arn refresh;

SELECT * FROM DIRECTORY(VOLUME aws_s3_volume_arn);
```

![](.topwrite/assets/20250219-153427.jpeg)
