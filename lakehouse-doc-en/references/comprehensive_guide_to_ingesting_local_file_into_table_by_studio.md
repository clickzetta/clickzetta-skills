# Complete Guide to Importing Data into Singdata Lakehouse

## Data Ingestion: Loading Local Files via Singdata Lakehouse Studio

#### Overview

You will use [Singdata Lakehouse Studio](https://accounts.clickzetta.com/) to load local data into Singdata Lakehouse tables through a web interface, without any coding.

#### Use Cases

Suitable for directly uploading smaller local files (not larger than 2GB) such as CSV, TXT, Parquet, AVRO, ORC into Singdata Lakehouse tables without programming, making it the simplest method.

#### Implementation Steps

##### Upload File

Navigate to Data -> Data Directory, click "Upload Data" to import local files (CSV files generated in the test data generation section) into the table.

:-: ![](.topwrite/assets/image_1736146842294.png =519)

##### Import Data

Click "Upload Data":

* Test data generated in the test data generation section
* Schema created in the Singdata Lakehouse setup section
* Select "Create New Table", table name: lift\_tuckets\_import\_by\_studio\_web
* Virtual compute cluster created in the Singdata Lakehouse setup section

:-: ![](.topwrite/assets/image_1736146857816.png =513)

After clicking "Next", check if the automatic settings for the uploaded data are correct. If the data preview meets expectations, the automatic settings are correct. Click "Confirm" to complete the data upload.

:-: ![](.topwrite/assets/image_1736146867287.png =516)

##### Result Verification

Go to "Data" to check the import status and data:

You can see that the number of rows written in the import result is "100,000", which is consistent with the number generated in the "Test Data Generation" step.

:-: ![](.topwrite/assets/image_1736146881028.png =523)

You can further "Preview Data" to confirm the data was loaded successfully:

:-: ![](.topwrite/assets/image_1736146888569.png =518)

At this point, we have loaded local files into the table via Singdata Lakehouse Studio.

:-: ![](.topwrite/assets/image_1736146899159.png =515)

#### Next Steps

* Continue loading data into the same table or other tables. By clicking "Upload" on the previous page, you can upload more data into the same table.
* Use Singdata Lakehouse's built-in DataGPT for visual data exploration and data analysis through Q&A.
* Develop SQL tasks in the IDE of Singdata Lakehouse Studio to further clean, transform, and analyze data.

#### Resources

[Data Source](DataSourceConfigGuide.md)

[Data Synchronization](data-integration.md)

^