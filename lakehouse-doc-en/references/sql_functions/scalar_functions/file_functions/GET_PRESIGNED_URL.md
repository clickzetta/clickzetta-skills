# GET\_PRESIGNED\_URL Function

This function generates a pre-signed URL for a file in a Volume by providing the Volume name, the relative file path, and an expiration time in seconds. This functionality allows applications to access files stored in external Volumes.

## Use Cases

The following are methods for accessing files in a Volume:

1. Directly access a pre-signed URL (of string type) in a web browser.
2. Send the pre-signed URL of a file in the Volume to a remote function for processing.

## Notes

1. The user executing this function must have READ permission on the Volume object.

2. This function requires file metadata (e.g., `relative_path`) to be fetched from the Volume's local metadata system. Ensure that the file metadata for a newly imported Volume has been synced to the Lakehouse metadata system, or use the following command to refresh:

   ```
   ALTER VOLUME <volume_name> REFRESH;
   ```

3. GET\_PRESIGNED\_URL is a non-deterministic function, meaning that for the same input values, the output may differ across executions.

## Syntax

```
GET_PRESIGNED_URL(VOLUME volume_name | TABLE VOLUME table_name | USER VOLUME , '<relative_file_path>', [<expiration_time>])
```

## Parameters

* **volume \<volume\_name**\>**: `volume` is a fixed keyword indicating that the following object type is a Volume; `volume_name` is the name of a system-created Volume.
* **relative\_file\_path**: The file path and filename relative to the Volume's designated location. It can be obtained by calling the `directory` function:
  ```
  SELECT GET_PRESIGNED_URL(volume <volume_name>, relative_path) AS pre_signed_url
  FROM DIRECTORY(volume <volume_name>);
  ```
* **expiration\_time**: The validity period of the generated pre-signed URL, in seconds. The default value is 3600 seconds (60 minutes).

## Return Value

A pre-signed URL (of string type).

## Examples

The following are several examples of using the GET\_PRESIGNED\_URL function:

1. Generate a pre-signed URL valid for 1 hour:

   ```
   SELECT GET_PRESIGNED_URL(volume hz_image_volume, 'example.jpg', 3600) AS pre_signed_url;
   ```

2. Generate a pre-signed URL with the default expiration time (1 hour):

   ```
   SELECT GET_PRESIGNED_URL(USER VOLUME, 'pangxie_pic.jpg', 3600) AS pre_signed_url;
   ```

3. Obtain the relative path of a file from a directory and generate a pre-signed URL:

   ```
   SELECT GET_PRESIGNED_URL(volume hz_image_volume, relative_path) AS pre_signed_url
   FROM DIRECTORY(volume hz_image_volume);
   ```

> Note: If the generated URL is inaccessible, it may be because an internal object storage link was generated. Try adding the following parameter before executing the SQL and then retry:
>
> `set cz.sql.function.get.presigned.url.force.external=true;`
>
> For example:
>
> ```
> SET cz.sql.function.get.presigned.url.force.external=true; 
> SELECT GET_PRESIGNED_URL(USER VOLUME, 'pangxie_pic.jpg', 3600) AS pre_signed_url;
> ```

4. Batch retrieve pre-signed URLs for images in the USER VOLUME

   ```
    SET cz.sql.function.get.presigned.url.force.external=true;
    SELECT relative_path,
    GET_PRESIGNED_URL(USER VOLUME, relative_path, 3600) AS pre_signed_url
    FROM (
          SELECT relative_path FROM (LIST USER VOLUME)
    );
    ```

The examples above help you better understand how to use the GET\_PRESIGNED\_URL function in various scenarios. Adjust the parameters and code according to your actual needs.

^
