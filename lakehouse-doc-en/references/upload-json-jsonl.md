# How to Upload JSON/JSONL Files and Import into Lakehouse Tables

^

## Prerequisites

Currently only JSON/JSONL files in the following standard formats are supported. Files that do not comply will not be successfully parsed.

**JSONL Format**

> * One complete JSON object per line
> * Lines separated by newline characters (\n)
> * No trailing commas at line ends
> * Each line must be valid JSON
> * Standard formatted JSON lines are supported
>   -----Example 1---
>   {"id": 1, "name": "Alice", "age": 30, "city": "New York"}{"id": 2, "name": "Bob", "age": 28, "city": "Los Angeles"}{"id": 3, "name": "Charlie", "age": 35, "city": "Chicago"}{"id": 4, "name": "Diana", "age": 32, "city": "Houston"}
>   -----Example 2---
>   {"id": 1, "name": "Alice", "age": 30, "city": "New York"}
>   {
>   "id": 2,
>   "name": "Bob",
>   "age": 28,
>   "city": "Los Angeles"
>   }

**JSON Format**

> --JSON array format---
> [{"id": 1, "name": "Alice", "age": 30, "city": "New York"},{"id": 2, "name": "Bob", "age": 28, "city": "Los Angeles"},{"id": 3, "name": "Charlie", "age": 35, "city": "Chicago"},{"id": 4, "name": "Diana", "age": 32, "city": "Houston"}]
> --JSON formatted---
> {
> "id": 2,
> "name": "Bob",
> "age": 28,
> "city": "Los Angeles"
> }

## Method 1: Import Using Singdata Lakehouse Web Upload

**Steps**:

You can click "Upload Data" in the following locations:

* Instance Homepage -> Data Upload
* Development -> Data Tree (left side)
* Data Asset Map -> Data Upload
* Data Asset Map -> Data Management -> Data Tree -> Data Upload

Drag/add JSON/JSONL files that comply with standard format specifications to the upload area, and select specific configuration information. For detailed operations, see [Data Upload](<upload_data.md>)


**Upload to a New Table**

| ![](.topwrite/assets/774c65e217/dcc4141809b8624f9869df74f16143d62d0c4618.jpeg =290) | ![](.topwrite/assets/774c65e217/620b74b85135aaf3f07902fc33d9fa1c6ce62ae0.jpeg =475) |
| ----------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |

After the file is added, the system will parse the information in the file based on JSON/JSONL rules and generate the corresponding field names, types, and specific values.

When the parsed information is confirmed to be accurate, you can customize which data you want to upload and import this time.

After clicking Confirm, the system automatically creates the corresponding table and imports the JSON file data into that table.

**Upload to an Existing Table**

| ![](.topwrite/assets/774c65e217/cd685005810b036910d46bd65780b5426676360e.png =259) | ![](.topwrite/assets/774c65e217/96a4ea3793bc69dedc0d9156a20b0d3a90df6167.jpeg =391) |
| ---------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |

* After selecting the target table, click Next to list the specific fields of the target table.
* Ensure that the data in the target file has the corresponding field information. If there are scenarios where fields do not match between the file and the table, the processing rules are as follows:
* If a target table field is not in the file, the field value defaults to null
* If a field in the file is not in the table, that field is not processed by default.
* If a field name in the file matches a field name in the table, but the types are inconsistent, that value will be identified as erroneous data.

## Method 2: Import Using External Volume

> Only supports importing in the form of one complete JSON object per line. If the file contains line breaks or formatted JSON, it cannot be parsed.

Step 1: Create an external volume connection

```Plain
CREATE STORAGE CONNECTION IF NOT EXISTS oss_test3
     TYPE oss
     ENDPOINT = 'corresponding endpoint'
     ACCESS_ID = 'your access_id'
     ACCESS_KEY = 'your access_key'
     COMMENTS = 'OSS public endpoint' ;
```

Step 2: Create an external volume

```SQL
CREATE EXTERNAL VOLUME  if not exists my_volume
LOCATION 'oss://json_file/'
USING CONNECTION oss_test3
DIRECTORY = (enable=true, auto_refresh=true)
RECURSIVE=true;
```

Step 3: Verify whether the volume is created successfully (optional)

```Plain
list VOLUME my_volume;
```

Step 4: Use the sqlline tool or a database management tool. This command is not currently supported for execution in Studio.

```Plain
PUT '/Users/xxx/xxxx.json'  to  volume public.my_volume  file  'ods.json';
```

Step 5: Query the uploaded JSON file format (optional)

```Plain
SELECT * FROM VOLUME my_volume  USING  json FILES('odst.json') LIMIT 5;
```

Step 6: Create the corresponding Lakehouse table based on the parsed fields from the file (table creation process omitted) and import the data into the table

```Plain
COPY INTO day_report_simple
FROM VOLUME my_volume
USING JSON
FILES('ods.json');
```

QA

Q1: The fields parsed by the data upload feature are incomplete

The data upload feature only parses field information from the first 1,000 rows of JSON by default. If data beyond the first 1,000 rows has different keys and values, they will not be processed by default.

Q2: Why does the file upload still fail even though CONNECTION and VOLUME have been created?

Currently, within the Singdata Studio product, you cannot directly determine whether CONNECTION and VOLUME have been created successfully from the execution results. It is recommended to refer to Step 3 in Method 2 to verify whether the creation was successful.
