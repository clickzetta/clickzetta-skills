# Complete Guide to Importing Data into Singdata Lakehouse

## Data Ingestion: Batch Loading via Singdata Lakehouse Studio (Public Network Connection)

#### Overview

#### Use Cases

When the existing data source (including databases, data warehouses) has a publicly accessible address (such as through public NAT mapping), the single table data volume is large, and the synchronization cost is low, with low requirements for data freshness (often on an hourly or even daily basis), the data from the source table can be synchronized to the Lakehouse table.

#### Implementation Steps

Navigate to Development -> Tasks, click "+", select "Offline Sync", and create a new "Offline Sync" job.

:-: ![](.topwrite/assets/image_1736147655855.png =464)

Other parameter configurations are as follows:

:-: ![](.topwrite/assets/image_1736147664609.png =470)

Then select to create a new data table: lift\_tickets\_data\_from\_pg\_batch.

In the "Create New Data Table" SQL code, change the table name to "lift\_tickets\_data\_from\_pg\_batch".

:-: ![](.topwrite/assets/image_1736147671728.png =455)

Check if the field mapping meets expectations, then test run the sync task:

:-: ![](.topwrite/assets/image_1736147681157.png =459)

Check the test results:

View the test task logs and check if the number of nubWrite matches the number of rows in the source table.

:-: ![](.topwrite/assets/image_1736147689681.png =469)

#### Next Steps Recommendations

* Configure the where condition to set the data to be synchronized for each run, rather than the full amount. This is generally based on filtering by time fields.

* Configure scheduling parameters and submit, operate, and maintain periodic data synchronization.

  * If it is suitable for small volume dimension table data, there is no need to set the where condition, set the data write mode to "overwrite", and perform a full overwrite each time.
  * If it is large volume fact table data, set the where condition, set the data write mode to "append", and perform incremental append writes each time to reduce the amount of data synchronized and the synchronization cost each time. Avoid the high cost of full synchronization each time.

* Offline sync tasks serve as the beginning of data extraction (E) and loading (L) in data ELT, and further cleaning and transformation (T) of the data loaded into the warehouse can be performed through SQL tasks.

#### Resources

[Data Management](data.md)

^