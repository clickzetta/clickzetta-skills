# GET\_PRESIGNED\_URL Function

This function generates a presigned URL for a file in a Volume by inputting the Volume name, the relative path of the file, and the expiration time (in seconds). This feature allows applications to access files stored in an external Volume.

## Usage Scenarios

Here are several methods to access files in a Volume:

1. Directly access the presigned URL in a web browser.
2. Send the presigned URL of the Volume file to a remote function for processing.

## Notes

1. The user executing this function needs to have READ permission on the Volume object.

2. This function needs to obtain file information (such as `relative_path`) from the local metadata system of the Volume. Please ensure that the file metadata corresponding to the newly imported Volume has been synchronized to the Lakehouse metadata system, or use the following command to refresh:
   ```
   ALTER VOLUME <volume_name> REFRESH;
   ```
3. GET\_PRESIGNED\_URL is a non-deterministic function, meaning that given the same input values, the output may be different each time it is executed.

## Syntax
```
GET_PRESIGNED_URL(volume <volume_name>, '<relative_file_path>', [<expiration_time>])
```
## Parameters

* **volume \<volume\_name**>: volume is a fixed keyword, indicating that the following object type is Volume; volume\_name is the name of the Volume created by the system.
* **relative\_file\_path**: The file path and file name relative to the specified location of the Volume. It can be obtained by calling the directory function:
  ```
  SELECT GET_PRESIGNED_URL(volume <volume_name>, relative_path) AS pre_signed_url
  FROM DIRECTORY(volume <volume_name>);
  ```
* **expiration\_time**: The validity period of the generated URL, in seconds. The default value is 3600 seconds (60 minutes).

## Return Value

The pre-signed URL.

## Usage Example

Here are some examples of using the GET\_PRESIGNED\_URL function:

1. Generate a pre-signed URL with a validity period of 1 hour:
   ```
   SELECT GET_PRESIGNED_URL(volume hz_image_volume, 'example.jpg', 3600) AS pre_signed_url;
   ```
2. Generate a pre-signed URL with a default validity period (1 hour):
   ```
   SELECT GET_PRESIGNED_URL(volume hz_image_volume, 'example.jpg') AS pre_signed_url;
   ```
```markdown
3. Get the relative path of the file from the directory and generate a pre-signed URL:
```
   ```
   SELECT GET_PRESIGNED_URL(volume hz_image_volume, relative_path) AS pre_signed_url
   FROM DIRECTORY(volume hz_image_volume);
   ```
By the above example, you can better understand how to use the GET\_PRESIGNED\_URL function in different scenarios. Please adjust the parameters and code according to your actual needs.