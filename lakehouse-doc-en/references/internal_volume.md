# Using Internal Volume

Internal Volume is the default file storage area provided by the system, used for temporarily storing data files to be processed or loaded.

* For users without cloud storage, files can be directly uploaded to the Internal Volume as the main storage area for data files. The system provides fully managed storage services.
* Users who already use cloud object storage can choose to use External Volume, accessing it by directly mounting the cloud storage path without additional data migration and copying.

The system currently supports three types of internal Volumes: User Volume, Table Volume, and Named Volume.

### Using User Volume

User Volume is the user's exclusive personal storage space, similar to the user's home directory in an operating system, and cannot be deleted. Space users have read and write permissions to the User Volume by default.

* **View files under User Volume**

```
show user volume directory;

relative_path                            url                                                                                                                                              size   last_modified_time  
---------------------------------------- ------------------------------------------------------------------------------------------------------------------------------------------------ ------ ------------------- 
images/image-2024-05-22-11-25-23-519.png oss://lakehouse-hz/86/workspaces/ql_ws_8133192700078175627/internal_volume/user_4371011337311368544/images/image-2024-05-22-11-25-23-519.png 200494 2024-05-28 23:30:27 
images/image.png                         oss://lakehouse-hz/86/workspaces/ql_ws_8133192700078175627/internal_volume/user_4371011337311368544/images/image.png                         513894 2024-05-28 23:30:27 
taxi_zone_lookup.csv                     oss://lakehouse-hz/86/workspaces/ql_ws_8133192700078175627/internal_volume/user_4371011337311368544/taxi_zone_lookup.csv                     12331  2024-05-28 23:04:54 
tmp/taxi_zone_lookup.csv                 oss://lakehouse-hz/86/workspaces/ql_ws_8133192700078175627/internal_volume/user_4371011337311368544/tmp/taxi_zone_lookup.csv                 12331  2024-05-28 23:05:54 
tmp/taxi_zone_lookup_02.csv              oss://lakehouse-hz/86/workspaces/ql_ws_8133192700078175627/internal_volume/user_4371011337311368544/tmp/taxi_zone_lookup_02.csv              12331  2024-05-28 23:34:24
```

* **Upload, Download, and Delete Files**

```

-- Upload file to the root directory of user volume
PUT  '/Users/Downloads/taxi_zone_lookup.csv' TO USER VOLUME;

-- Upload file and save it as a specified file name in the specified directory of user volume
PUT '/Users/Downloads/taxi_zone_lookup.csv'  TO USER VOLUME FILE 'tmp/taxi_zone_lookup_02.csv';

-- Upload multiple files to a volume subdirectory using a wildcard
PUT '/Users/Downloads/images/*'  TO USER VOLUME SUBDIRECTORY 'images/';

-- Download file from User Volume
GET USER VOLUME FILE 'images/image-2024-05-22-11-25-23-519.png'   TO '/Users/Downloads/output/' ;

-- Delete specified file from User Volume
REMOVE USER VOLUME FILE 'images/image-2024-05-22-11-25-23-519.png'

-- Delete all files in the specified path under User Volume
REMOVE USER VOLUME SUBDIRECTORY 'tmp/'
```

* **Query files under User Volume through SQL**

```SQL
-- Query specified files under User Volume through SQL
SELECT * FROM USER VOLUME 
USING CSV
OPTIONS(
        'header'='true'
)
FILES( 'taxi_zone_lookup.csv')
LIMIT 5;

LocationID Borough       Zone                    service_zone 
---------- ------------- ----------------------- ------------ 
1          EWR           Newark Airport          EWR          
2          Queens        Jamaica Bay             Boro Zone    
3          Bronx         Allerton/Pelham Gardens Boro Zone    
4          Manhattan     Alphabet City           Yellow Zone  
5          Staten Island Arden Heights           Boro Zone    


-- Query all files under the specified path of User Volume through SQL
SELECT * FROM USER VOLUME using csv subdirectory '/tmp/';
```

* **Use the** \`\` **function to get the real access path of the file under the Volume in object storage with a temporary signature**.

```SQL
--Get presigned URL, get OSS internal URL
SELECT get_presigned_url(USER VOLUME , 'images/image.png' , 60) as url;

--Get presigned URL, get external URL
set cz.sql.function.get.presigned.url.force.external=true;
SELECT get_presigned_url(USER VOLUME , 'images/image.png' , 60) as url;
```

### Using Table Volume

Each Lakehouse table is associated with a storage space by default, which we refer to as Table Volume. Users need to have the following permissions to operate on the Table Volume of a specified table:

| **TABLE VOLUME Operation**                 | **Corresponding TABLE Permissions Required** |
| :----------------------------------------- | :------------------------------------------- |
| SHOW TABLE VOLUME DIRECTORY \<table\_name> | SELECT                                       |
| SELECT FROM VOLUME \<table\_name>          | SELECT                                       |
| GET                                        | SELECT                                       |
| PUT                                        | INSERT, UPDATE, DELETE                       |
| REMOVE                                     | INSERT, UPDATE, DELETE                       |

The following examples illustrate the use of TABLE VOLUME operations.

```SQL
--Create table
CREATE TABLE t_copy_from_volume(id int, name string);

--View the Table volume of the specified table
SHOW TABLE VOLUME DIRECTORY t_copy_from_volume;
```

Uploading files to the target table's TABLE VOLUME requires the user to have write permissions for the target table.

```SQL
--Upload file to table volume, if storage path is not specified, it will be saved in the root path by default
PUT '/Users/Downloads/data.csv' TO TABLE VOLUME t_copy_from_volume FILE 'data.csv';

source                           target   source_size target_size status  
-------------------------------- -------- ----------- ----------- ------- 
/Users/Downloads/data.csv data.csv 34          34          SUCCEED 
```

Using SQL to Explore Data Uploaded to TABLE STREAM.

```SQL
--Query
SELECT * FROM TABLE VOLUME t_copy_from_volume
USING CSV
OPTIONS(
        'header'='true',
        'lineSep'='\n'
)

id name  
-- ----- 
1  hello 
2  world 
3  !     
```

Use the COPY INTO command to import file data into the target table.

```SQL
COPY INTO t_copy_from_volume FROM TABLE VOLUME t_copy_from_volume(id int, name string)  USING csv  
OPTIONS(
        'header'='true',
        'lineSep'='\n'
)
FILES ('data.csv')
--Delete files in the volume to save storage
PURGE=TRUE;
```

Query the target table to verify the import results.

```SQL
-- View import results
SELECT * FROM t_copy_from_volume;

id name  
-- ----- 
1  hello 
2  world 
3  !     
```

Delete files under USER VOLUME.

```SQL
-- Delete the specified file under User Volume
REMOVE TABLE VOLUME t_copy_from_volume FILE 'data.csv'
-- Delete all files under the specified path in User Volume
REMOVE TABLE VOLUME t_copy_from_volume subdirectory '/'
```
### Using Named Volumes

Named Volumes are explicitly created by users and stored in internal storage managed by Lakehouse, eliminating the need for additional cloud storage configuration. They offer more precise control compared to automatically generated User Volumes and Table Volumes.

#### Syntax Description

#### Creating a Named Volume

```SQL
CREATE VOLUME [IF NOT EXISTS] <volume_name>
    DIRECTORY = (
        enable = true
        auto_refresh = true
    )
    RECURSIVE = true          -- Specifies whether to recursively scan subdirectories (default is false)
[COMMENT = 'volume_description']
```

#### Dropping a Volume

```SQL
DROP VOLUME [IF EXISTS] <volume_name>
```

#### Usage Example

Uploading and Downloading Data

```sql
-- Create a volume
CREATE VOLUME my_volume
    DIRECTORY = (
        enable = true,
        auto_refresh = true
    )
    RECURSIVE = true;
SHOW VOLUME DIRECTORY my_volume;

COPY INTO VOLUME my_volume SUBDIRECTORY 'dau_unload/'
FROM TABLE public.students01
file_format = (
    type = CSV
    writebom = true
);
SHOW VOLUME DIRECTORY my_volume;

-- Test local upload and download
GET VOLUME my_volume FILE 'dau_unload/part00001.csv' TO '/tmp';
+---------------+--------------------+-------------+-------------+---------+
|    source     |       target       | source_size | target_size | status  |
+---------------+--------------------+-------------+-------------+---------+
| part00001.csv | /tmp/part00001.csv | 1472        | 1472        | SUCCEED |
+---------------+--------------------+-------------+-------------+---------+

PUT '/tmp/part00001.csv' TO VOLUME my_volume FILE 'my.csv';
+--------------------+--------+-------------+-------------+---------+
|       source       | target | source_size | target_size | status  |
+--------------------+--------+-------------+-------------+---------+
| /tmp/part00001.csv | my.csv | 1472        | 1472        | SUCCEED |
+--------------------+--------+-------------+-------------+---------+
```

## Data Operation Protocols

| Protocol Type   | Address Format                             | Typical Scenario      |
| --------------- | ------------------------------------------ | --------------------- |
| User Volume     | volume:user://~/filename                   | User-specific resources |
| Table Volume    | volume:table://table_name/file             | Table-associated ETL files |
| Named Volume    | volume://volume_name/path                  | Cross-team shared resources |

* **User Volume Address Format**: `volume:user://~/upper.jar`
  * `user` indicates the User Volume protocol.
  * `~` represents the current user (a fixed value).
  * `upper.jar` is the target filename.

* **Table Volume Address Format**: `volume:table://table_name/upper.jar`
  * `table` indicates the Table Volume protocol.
  * `table_name` is the name of the table and should be filled in according to the actual situation.
  * `upper.jar` is the target filename.

* **Named Volume Address Format**: `volume://volume_name/upper.jar`
  * `volume_name` is the name of the created volume.
  * `upper.jar` is the target filename.
