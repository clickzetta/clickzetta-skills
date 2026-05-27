# PUT Command

## Description

The PUT command is a utility in Lakehouse SQL used to upload local files from the client host to the data lake Volume object in Lakehouse. With this command, users can easily transfer local files to the cloud, achieving rapid data migration and synchronization. To execute the PUT command, you can use the [sqlline](connect-with-cli.md) tool or [database management tools](eco_integration/dbeaver-lakehouse.md).

## Usage Scenarios

The PUT command is suitable for the following scenarios:

1. Uploading local files to the data lake Volume object.
2. Rapid migration and synchronization of local and cloud data.

## Syntax
```
PUT 'local_path' [ , 'local_path' [ , ... ] ] 
    TO 
    [ VOLUME volume_name | TABLE VOLUME table_name | USER VOLUME ]
    [ SUBDIRECTORY 'dir' | FILE 'filename' ]
    [ option_key = option_value ] ..
```
## Parameter Description

* `local_path`: The path of the local file to be uploaded. **Linux / macOS**: The path starts with the root directory '/' or uses the `'file:///'` prefix to indicate the local path. **Windows System**: If the directory path and/or file name contains special characters, the entire file URI must be enclosed in single quotes. Note that within the enclosed URI, the separator is a forward slash ('/').
* `VOLUME/TABLE VOLUME/USER VOLUME`: Refer to uploading local data to external Volume, TABLE VOLUME, and USER VOLUME respectively.
* `SUBDIRECTORY/FILE`: Specifies the target path for the uploaded file. You can specify a subdirectory (`SUBDIRECTORY`) or use the FILE parameter to rename the uploaded file.

## Example

1. Use internal volume to upload files to the table
```
-- Upload file
PUT '/Users/Downloads/data.csv' TO TABLE VOLUME my_table FILE 'data.csv';
-- View file
SHOW TABLE VOLUME DIRECTORY my_table;
-- Import file
COPY INTO my_table FROM TABLE VOLUME my_table(id int, name string)  USING csv  
OPTIONS(
        'header'='true',
        'lineSep'='\n'
)
FILES ('data.csv')
-- Delete files in volume to save storage
PURGE=TRUE;
```

2. Create an external volume object named `hz_image_volume` and upload the file `'/Users/derekmeng/Downloads/cats_and_dogs.zip'`
   ```SQL
   PUT '/Users/Downloads/cats_and_dogs.zip' to volume hz_image_volume FILE '/Users/derekmeng/Downloads/catsdogs.zip'
   ```
3. There is a table named `tbl_region`, and you want to upload the local table data to the table's volume space:
   ```SQL
   PUT '/Users/Downloads/region.tbl' TO TABLE VOLUME tbl_region;
   ```
## Notes

* The PUT command cannot be executed through the Studio SQL task node. Users can execute this command through the Lakehouse SQLLine client, JDBC client, and SDK.
* Please ensure that the size of a single file to be uploaded does not exceed 5G.
* When using the PUT command, please ensure that the local file path and file name are correct to avoid upload failures due to incorrect paths.
* When uploading files, if a file with the same name already exists in the target volume object, the system will automatically overwrite the original file. If necessary, please perform the appropriate backup operations before uploading.

