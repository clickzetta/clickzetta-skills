# Create Volume to Access Alibaba Cloud OSS Data:

## Prerequisites:

After the STORAGE CONNECTION to Alibaba Cloud is created, you can create a Volume object to access object storage data:

## Create Volume Object

```SQL

CREATE EXTERNAL VOLUME sh_image_volume
    LOCATION 'oss://{bucket_name}/{path_to_data}'
    USING CONNECTION sh_oss_conn_public
    DIRECTORY = (
        enable=true,
        auto_refresh=true
    )
    RECURSIVE=true;
```

####

#### 2. View Details of Created Volume Objects

```SQL
DESC VOLUME sh_image_volume
```

#### 3. View the files in the created Volume path

```SQL
SHOW VOLUME DIRECTORY sh_image_volume;
```

#### 4. Displaying Images in the Volume Path in Lakehouse Studio

When in the Lakehouse Studio development interface, you can directly click the URL -> **Preview** to open the image after obtaining the access URL of the image through the [get\_presigned\_url](sql_functions/scalar_functions/file_functions/get_presigned_url.md) function:

![](.topwrite/assets/20250219-153030.jpeg)
