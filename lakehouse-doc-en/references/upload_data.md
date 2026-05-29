## Upload Local Data Using the Data Upload Feature

You can add data to a table in Lakehouse through the "Data Upload" feature on the Singdata Lakehouse web interface.

## Instructions

* Suitable for smaller local files (not larger than 2GB) (CSV, TXT, Parquet, AVRO, ORC) to be directly uploaded to a table in Singdata Lakehouse without programming, making it the simplest method.
* Currently, only one file can be uploaded at a time.
* The data upload feature does not support parsing fields of struct, map, and array data types in the file.

## Using the Data Upload Feature

When using the data upload feature, you can create a new table or upload data to an existing table.

### Creating a New Table

When uploading data, you can usually create a new table for the data at the same time.

#### Prerequisites

**You need to meet the following conditions to use this capability**

* You have one of the following roles: workspace\_admin, workspace\_dev, workspace\_anylst
* Or you have the following permission points: create table, insert + update, delete + insert + update

#### Steps

1. Log in to your Singdata Studio account

2. You can click "Upload Data" in the following places

   1. Instance Homepage -> Data Upload
   2. Development -> Data Tree on the left
   3. Data Asset Map -> Data Upload
   4. Data Asset Map -> Data Management -> Data Tree -> Data Upload

   ![](.topwrite/assets/image_1740368222644.png =386)

3. You can add local files by dragging and dropping, or by clicking to browse files on the local system. Only one file can be added at a time, and the size must not exceed 2GB.

4. Schema: Choose to create the table under a certain schema.

5. Select Table: Choose "Create New Table" and enter the new table name in the field behind.

6. Cluster: Available clusters under the workspace where the current schema is located.

7. Data Import Method: Supports two methods of importing data into the new table: append write and clear before write.

8. After confirming all the information, click "Next". The system will automatically parse the field information in the file based on the uploaded file information.

   ![](.topwrite/assets/image_1736307305607.png =441)

9. Check and judge whether the automatically parsed field names and field types meet expectations. If confirmed to be correct, click "Confirm" to complete the data upload and create a new table.
   If there is a problem with field parsing, you can modify the **File Properties** configuration item to refresh and obtain the automatically parsed field names, field types, etc. Or manually modify the field names or field types. Note: The modified field types may not match the system's parsing, resulting in unsuccessful uploads.

### Upload Data to an Existing Table

#### Prerequisites

**You need to meet the following conditions to use this capability**

* You have one of the following roles: workspace\_admin, workspace\_dev, workspace\_anylst
* Or you have the following permission points: create table, insert + update, delete + insert + update

#### Steps

1. Log in to your Singdata Studio account

2. You can click "Upload Data" in the following places

   1. Development -> Data Tree -> Table -> Upload Data
   2. Data Asset Map -> Data Management -> Data Tree -> Table -> Upload Data

   ![](.topwrite/assets/image_1740368311386.png =377)

3. You can add local files by dragging and dropping, or by clicking to browse files on the local system. Only one file can be added at a time, and the size must not exceed 2GB.

4. Schema: Choose to create the table under a certain schema.

5. Select Table: Choose "Existing Table".

6. Cluster: Available clusters under the workspace where the current schema is located.

7. Data Import Method: Supports two methods of importing data into the **existing table**: append write and clear before write.

8. After confirming all the information, click "Next".

9. Configure the parsing of the uploaded file accordingly.

   1. File Type: The system will automatically parse the file type based on the format suffix of the uploaded file. Users can also choose other file types themselves, but they need to ensure that the selected file type matches the uploaded file type.

   2. File Properties Configuration:

   3. Header:

      * First row as header: Parse from the first row of the file, and directly parse the first row as "field names" and match them with the existing table. If there is no match, it will be judged as a failure.
      * No header: Ignore the first row and start reading from the second row as values.
      * Skip the first N rows: Set the number of rows to skip, and start reading from row N+1 as values.

   4. Field Wrapping Characters:

      * Double quotes: Under the column delimiter setting, parse the content within the "" double quotes as field values. **Recommended option**.
      * Single quotes: Under the column delimiter setting, parse the content within the 'single quotes as field values.
        Here is the translated Markdown content:

* Empty: All information after the column delimiter will be parsed as fields.

5. Line break: Set the handling method for line breaks. For Windows systems, it is \r\n; for Linux and MAC systems, it is \n.

6. Null value representation: Specify the representation of null values in the file.

7. Column delimiter: The delimiter between columns, only a single character is allowed. For CSV files, the default is a comma.

8. Encoding: UTF-8, GBK

9. Stop on error:

   * Stop immediately: Stop reading immediately upon encountering an error and return an error message.
   * Ignore errors: Ignore error lines until all data is read, and return information about the error lines.
   * Set fault tolerance lines: Stop reading when the number of error lines exceeds the set value, and return an error message.

^
