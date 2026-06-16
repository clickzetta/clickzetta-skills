# Export Data to Local

This document details how to download table data to your local machine. Currently, Lakehouse supports three data download modes:

1. Download files using the GET command and export them locally.
2. Use the visual download interface of Lakehouse Studio.
3. Use the Jdbc client to download data locally with the [COPY](copy.md) command. (This feature has been deprecated in jdbc version 2.0.0, it is recommended to use the GET command for downloading)

# Using the Visual Download Interface of Lakehouse Studio

In data development, when selecting and executing SQL, the results can be downloaded as Excel or CSV files. Due to the interface display result set limit of 10,000 rows, if you want to download all the data, you can click to download the entire CSV file, as shown in the figure below:

![](.topwrite/assets/image_1739954718255.png)

# Using the GET Command to Download Data

1. Prerequisites

* Installed [command line tool](connect-with-cli.md)
* Understand the [GET command](get.md) and [COPY INTO](copy_into_location.md) export commands

2. Export table data to local

```SQL
-- Export data to internal user volume
COPY INTO USER VOLUME SUBDIRECTORY 'tmp/' FROM TABLE mytable file_format = (type = CSV);;

-- View exported files
SHOW USER VOLUME DIRECTORY;
+-------------------+------------------------------------------------------------------------------------------------------------+------+---------------------+
|   relative_path   |                                                    url                                                     | size | last_modified_time  |
+-------------------+------------------------------------------------------------------------------------------------------------+------+---------------------+
| tmp/part00001.csv | oss://xxxx/tmp/part00001.csv | 5    | 2024-11-14 19:44:37 |
+-------------------+------------------------------------------------------------------------------------------------------------+------+---------------------+

-- Download file
GET USER VOLUME FILE 'tmp/part00001.csv' to './';
-- Delete files in volume to avoid occupying storage
remove user volume file 'tmp/part00001.csv';
SHOW USER VOLUME DIRECTORY;
+---------------+-----+------+--------------------+
| relative_path | url | size | last_modified_time |
+---------------+-----+------+--------------------+
```

3. Export the query results to the local machine

```SQL
    -- Export data to the internal user volume
COPY INTO USER VOLUME SUBDIRECTORY 'tmp/' FROM (select 1) file_format = (type = CSV);
SHOW  USER VOLUME DIRECTORY;
    
    -- View the exported files
    SHOW  USER VOLUME DIRECTORY;
   +-------------------+------------------------------------------------------------------------------------------------------------+------+---------------------+
   |   relative_path   |                                                    url                                                     | size | last_modified_time  |
   +-------------------+------------------------------------------------------------------------------------------------------------+------+---------------------+
   | tmp/part00001.csv | oss://xxxx/tmp/part00001.csv | 5    | 2024-11-14 19:44:37 |
   +-------------------+------------------------------------------------------------------------------------------------------------+------+---------------------+

    -- Download the file
    GET  USER VOLUME FILE 'tmp/part00001.csv' to  './';
    -- Delete the file in the volume to avoid occupying storage
    remove user volume file 'tmp/part00001.csv';
    SHOW  USER VOLUME DIRECTORY;
   +---------------+-----+------+--------------------+
   | relative_path | url | size | last_modified_time |
   +---------------+-----+------+--------------------+
```

^
