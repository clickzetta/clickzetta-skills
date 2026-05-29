# Using Internal Volume

Internal Volume is the default file storage area provided by Singdata Lakehouse, used for temporarily storing data files to be processed or loaded.

- For users without cloud storage, files can be directly uploaded to the Internal Volume as the main storage area for data files. The system provides fully managed storage services.
- Users who already use cloud object storage can choose to use External Volume, accessing it by directly mounting the cloud storage path without additional data migration and copying.

The system provides three types of internal Volumes: **User Volume**, **Table Volume**, and **Named Volume**. User Volume and Table Volume are created automatically by the system. Named Volume must be explicitly created by the user, who manages its lifecycle.

## Using User Volume

User Volume is the user's exclusive personal storage space, similar to the user's default working directory in an operating system. In Lakehouse, each user has read and write permissions to their User Volume by default.

### User Volume Operations

| Operation | Command |
|---|---|
| View file list | `SHOW USER VOLUME DIRECTORY` |
| Query files via SQL | `SELECT FROM USER VOLUME` |
| Upload files | `PUT ... TO USER VOLUME` |
| Download files | `GET USER VOLUME FILE ... TO ...` |
| Delete files | `REMOVE USER VOLUME FILE ...` |

### View Files Under User Volume

```sql
-- View files in the root directory of User Volume
SHOW USER VOLUME DIRECTORY;

relative_path                            url                                                                                                                                              size   last_modified_time  
---------------------------------------- ------------------------------------------------------------------------------------------------------------------------------------------------ ------ ------------------- 
images/image-2024-05-22-11-25-23-519.png oss://lakehouse-hz/86/workspaces/ql_ws_8133192700078175627/internal_volume/user_4371011337311368544/images/image-2024-05-22-11-25-23-519.png 200494 2024-05-28 23:30:27 
images/image.png                         oss://lakehouse-hz/86/workspaces/ql_ws_8133192700078175627/internal_volume/user_4371011337311368544/images/image.png                         513894 2024-05-28 23:30:27 
taxi_zone_lookup.csv                     oss://lakehouse-hz/86/workspaces/ql_ws_8133192700078175627/internal_volume/user_4371011337311368544/taxi_zone_lookup.csv                     12331  2024-05-28 23:04:54 
tmp/taxi_zone_lookup.csv                 oss://lakehouse-hz/86/workspaces/ql_ws_8133192700078175627/internal_volume/user_4371011337311368544/tmp/taxi_zone_lookup.csv                 12331  2024-05-28 23:05:54 
```

### Upload, Download, and Delete Files

```sql
-- Upload file to the root directory of User Volume
PUT '/Users/Downloads/taxi_zone_lookup.csv' TO USER VOLUME;

-- Upload file and save to a specified path in User Volume
PUT '/Users/Downloads/taxi_zone_lookup.csv' TO USER VOLUME FILE 'tmp/taxi_zone_lookup_02.csv';

-- Upload multiple files to a Volume subdirectory using a wildcard
PUT '/Users/Downloads/images/*' TO USER VOLUME SUBDIRECTORY 'images/';

-- Download file from User Volume
GET USER VOLUME FILE 'images/image-2024-05-22-11-25-23-519.png' TO '/Users/Downloads/output/';

-- Delete specified file from User Volume
REMOVE USER VOLUME FILE 'images/image-2024-05-22-11-25-23-519.png';

-- Delete all files under the specified path in User Volume
REMOVE USER VOLUME SUBDIRECTORY '/';
```

### Query Files Under User Volume via SQL

```sql
-- Query a specified file under User Volume
SELECT * FROM USER VOLUME 
USING CSV
OPTIONS(
    'header' = 'true'
)
FILES ('taxi_zone_lookup.csv')
LIMIT 5;

LocationID Borough       Zone                    service_zone 
---------- ------------- ----------------------- ------------ 
1          EWR           Newark Airport          EWR          
2          Queens        Jamaica Bay             Boro Zone    
3          Bronx         Allerton/Pelham Gardens Boro Zone    
4          Manhattan     Alphabet City           Yellow Zone  
5          Staten Island Arden Heights           Boro Zone    

-- Query all files under the specified path in User Volume
SELECT * FROM USER VOLUME USING CSV SUBDIRECTORY '/tmp/';
```

### Get Temporary Access URL for Files

Use the `get_presigned_url` function to get a temporary signed access URL for a file in the Volume from object storage:

```sql
-- Get presigned URL (internal network)
SELECT get_presigned_url(USER VOLUME, 'images/image.png', 60) as url;

-- Get presigned URL (external network)
SET cz.sql.function.get.presigned.url.force.external = true;
SELECT get_presigned_url(USER VOLUME, 'images/image.png', 60) as url;
```

## Using Table Volume

Each Lakehouse table is associated with a storage space by default, which is referred to as Table Volume. Users need the corresponding table permissions to operate on the Table Volume of a specified table:

| Table Volume Operation | Corresponding Table Permission Required |
|---|---|
| `SHOW TABLE VOLUME DIRECTORY <table_name>` | SELECT |
| `SELECT FROM VOLUME <table_name>` | SELECT |
| `PUT ... TO TABLE VOLUME <table_name>` | INSERT, UPDATE, DELETE |
| `GET TABLE VOLUME <table_name> FILE ...` | SELECT |
| `SHOW TABLE VOLUME DIRECTORY` | SCHEMA READ |
| `REMOVE TABLE VOLUME <table_name> FILE ...` | INSERT, UPDATE, DELETE |

### Table Volume Operation Examples

```sql
-- Create a table (automatically creates the associated Table Volume)
CREATE TABLE t_copy_from_volume(id INT, name STRING);

-- View the Table Volume of the specified table
SHOW TABLE VOLUME DIRECTORY t_copy_from_volume;
```

Uploading files to the target table's Table Volume requires the user to have write permissions for the target table:

```sql
-- Upload file to Table Volume; if no storage path is specified, it is saved in the root path by default
PUT '/Users/Downloads/data.csv' TO TABLE VOLUME t_copy_from_volume FILE 'data.csv';

source                           target   source_size target_size status  
-------------------------------- -------- ----------- ----------- ------- 
/Users/Downloads/data.csv        data.csv 34          34          SUCCEED 
```

Use SQL to explore the data uploaded to Table Volume:

```sql
-- Query files in Table Volume
SELECT * FROM TABLE VOLUME t_copy_from_volume
USING CSV
OPTIONS(
    'header' = 'true',
    'lineSep' = '\n'
);

id name  
-- ----- 
1  hello 
2  world 
3  !     
```

Use the COPY INTO command to import file data into the target table:

```sql
COPY INTO t_copy_from_volume FROM TABLE VOLUME t_copy_from_volume(id INT, name STRING)
USING CSV  
OPTIONS(
    'header' = 'true',
    'lineSep' = '\n'
)
FILES ('data.csv')
PURGE = TRUE;  -- Delete files in the Volume after import to save storage
```

Query the target table to verify the import results:

```sql
-- View import results
SELECT * FROM t_copy_from_volume;

id name  
-- ----- 
1  hello 
2  world 
3  !     
```

Delete files under Table Volume:

```sql
-- Delete the specified file under Table Volume
REMOVE TABLE VOLUME t_copy_from_volume FILE 'data.csv';

-- Delete all files under the specified path in Table Volume
REMOVE TABLE VOLUME t_copy_from_volume SUBDIRECTORY '/';
```

## Data Operation Protocols

| Protocol Type | Address Format | Typical Scenario |
|---|---|---|
| User Volume | `volume:user://~/filename` | User-private resources |
| Table Volume | `volume:table://table_name/file` | Table-associated ETL files |

### User Volume Address Format

`volume:user://~/upper.jar`

- `user`: indicates the User Volume protocol
- `~`: represents the current user, a fixed value
- `upper.jar`: the target filename

### Table Volume Address Format

`volume:table://table_name/upper.jar`

- `table`: indicates the Table Volume protocol
- `table_name`: the table name, to be filled in according to the actual situation
- `upper.jar`: the target filename

## Related Documentation

- [Data Lake Storage Management: Volume](datalake_volume.md)
- [Using External Volume](external_volume.md)
- [Import Data from Volume to Table](from_volume_to_table.md)
- [Export Data to Volume](from_lakehouse_to_volume.md)
