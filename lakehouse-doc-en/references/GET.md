# GET Command

## Description

The GET command is used to download files from the Singdata Lakehouse data lake Volume object to the client's local path. With this command, users can easily synchronize data from the cloud to the local environment for further analysis and processing. To execute the GET command, you can use the [sqlline](connect-with-cli.md) tool or [database management tools](eco_integration/dbeaver-lakehouse.md).

## Use Cases

* Data Analysis: Download data files from the cloud to the local environment for analysis and mining.
* Data Migration: Migrate data from the cloud to local storage for backup or migration to other cloud platforms.
* Data Recovery: Recover lost or damaged data from the cloud to the local environment.

## Syntax
```
GET 
    [ VOLUME volume_name | TABLE VOLUME table_name | USER VOLUME ]
    [ SUBDIRECTORY 'dir' | FILE 'file' ] 
    TO 'local_path'
    [ option_key = option_value ] ...
```
## Parameter Description

* `VOLUME/TABLE VOLUME/USER VOLUME`: Refers to downloading data from external Volume, TABLE VOLUME, and USER VOLUME to the local system.
* `SUBDIRECTORY/FILE`: Specifies the range of files to be downloaded, which can be subdirectories in the volume (`SUBDIRECTORY`) or multiple files using the FILE parameter.
* `local_path`: The local path for downloading, which varies depending on the operating system.

## Example

1. Export data from the table to the local system
```
--Export data to internal user volume
COPY INTO USER VOLUME SUBDIRECTORY 'tmp/' FROM TABLE mytable ;

-- View the exported files
SHOW USER VOLUME DIRECTORY;
+-------------------+------------------------------------------------------------------------------------------------------------+------+---------------------+
|   relative_path   |                                                    url                                                     | size | last_modified_time  |
+-------------------+------------------------------------------------------------------------------------------------------------+------+---------------------+
| tmp/part00001.csv | oss://xxxx/tmp/part00001.csv | 5    | 2024-11-14 19:44:37 |
+-------------------+------------------------------------------------------------------------------------------------------------+------+---------------------+

--Download file
GET USER VOLUME FILE 'tmp/part00001.csv' to './';
--Delete the file in the volume to avoid occupying storage
remove user volume file 'tmp/part00001.csv';
SHOW USER VOLUME DIRECTORY;
+---------------+-----+------+--------------------+
| relative_path | url | size | last_modified_time |
+---------------+-----+------+--------------------+
```


2. Retrieve all data from the `/temp` directory in the USER Volume to the local `/tmp` directory:
```
   GET USER VOLUME SUBDIRECTORY '/temp/' TO '/tmp/';
```
## Precautions

* Downloading files from an external Volume will incur object storage download fees for the associated cloud account. For specific pricing, please refer to the [official documentation](https://www.aliyun.com/price/detail/oss).
* The GET command cannot be executed through the Studio SQL task node. It can be executed through the Singdata Lakehouse SQLline client, JDBC client, and SDK.

