# Analyze Data in Singdata Lakehouse with FineBI

FineBI is a Business Intelligence (BI) product launched by FanRuan Software Co., Ltd.

FineBI is a new generation of big data analysis BI tool designed to help business personnel fully understand and utilize their data. With a powerful big data engine, users can create a variety of rich data visualizations by simply dragging and dropping, freely analyze and explore data, and unleash more unknown potential from the data.

## Preparation

### Download and Install FineBI

Please refer to the [FineBI official website](https://www.finebi.com/). If you have already installed it, please skip this step.

### Download Singdata Lakehouse JDBC Driver

Please refer to the Singdata Lakehouse [JDBC Driver](JDBC-Driver.md).

Download the latest version of the JDBC driver to your local machine for subsequent use.

### Modify SystemConfig.driverUpload to Allow Jar File Upload

Due to the high-security requirements of most users, FineBI by default prohibits uploading drivers through driver management.

Therefore, before using driver management, you need to set the SystemConfig.driverUpload field in the fine_conf_entity table of the [FineDB](https://help.fanruan.com/finebi/doc-view-1080.html) database, which stores FineBI information, to true.

* Change the parameter value to true: Allows uploading drivers through driver management.
* Change the parameter value to false: (The default value is false) Prohibits uploading drivers through driver management. An error will be reported when uploading: uploading driver jar files is not allowed. You can modify the SystemConfig.driverUpload configuration value to enable this feature.

^

:-: ![](.topwrite/assets/image_1736994756848.png =672)

^

For more details, please refer to [here](https://help.fanruan.com/finebi/doc-view-1540.html).

After restarting, log in to the FineBI system again, and you can upload the driver through "Driver Management".

## Install Singdata Lakehouse JDBC Driver in FineBI

Users can use the "Driver Management" function to upload the corresponding driver. "Driver Management" uses hot loading, so you can use the driver directly without restarting FineReport after uploading the driver.

When encountering some driver-related issues, you can quickly modify the driver loading method to achieve a quick connection.

Navigate to Data Connection -> Data Connection Management:

^

:-: ![](.topwrite/assets/image_1736937201539.png =320)

^

Click Driver Management -> New Driver.

By default, the current uploaded driver is prioritized for loading, as shown below:

^

:-: ![](.topwrite/assets/image_1736936446966.png =698)

* Prioritize loading the currently uploaded driver: Load the jar from driver management first.
* Only load the currently uploaded driver: Only load the jar from driver management.

When installing the Singdata Lakehouse JDBC driver, please select "Only load the jar from driver management".

Please fill in the driver name as "Singdata Lakehouse".
Select the driver as "com.clickzetta.client.jdbc.ClickZettaDriver".

## Using the Driver

1) In the "Data Connection Management" interface, click "New Data Connection" to create a new Singdata Lakehouse data connection.
First, select the data connection type as Other -> Other JDBC:

^

:-: ![](.topwrite/assets/image_1736937496339.png =684)

^

2) Select "Custom" for the driver, choose the Singdata Lakehouse driver you just uploaded from the dropdown, and fill in the connection information as shown below:

:-: ![](.topwrite/assets/image_1736938479094.png =676)

^

* Data Connection URL:
  jdbc:clickzetta://your-instance-ID.api.singdata.com/your-workspace-name?virtualCluster=your-cluster-name&schema=your-database-schema-name&username=username&password=password

In Singdata Lakehouse, navigate to the workspace, find the workspace you need to access, and click copy to copy the JDBC URL connection string. Then add the username and password to the string in the format above.

^

![](.topwrite/assets/image_1736939576798.png)

^

* Please enter the validation statement:
  set cz.sql.double.quoted.identifiers=true;
  select 1;
* Please keep other parameters unchanged.

3) Click Test Connection, and you can see that the database is successfully connected, as shown below:

^
:-: ![](.topwrite/assets/image_1736937895239.png =664)

^

## Verify Connection

### By Creating a Server Dataset

Navigate to Data Connection -> Server Dataset, and create a new SQL dataset.

Dataset Name: Singdata Lakehouse-TPCH-Q01

SQL Statement:
```sql
--LAKE_HOUSE SQL
--********************************************************************--
--Query a pricing summary report for lineItems. Query various types of goods that have been paid for,
--shipped, etc., within a certain time period on a single table lineitem, including information on billing,
--shipping, discounts, taxes, average prices, etc.
--********************************************************************--
select
    l_returnflag,
    l_linestatus,
    sum(l_quantity) as sum_qty,
    sum(l_extendedprice) as sum_base_price,
    sum(l_extendedprice * (1 - l_discount)) as sum_disc_price,
    sum(l_extendedprice * (1 - l_discount) * (1 + l_tax)) as sum_charge,
    avg(l_quantity) as avg_qty,
    avg(l_extendedprice) as avg_price,
    avg(l_discount) as avg_disc,
    count(*) as count_order
from
    clickzetta_sample_data.tpch_100g.lineitem
where
    l_shipdate <= date '1998-12-01' - interval '85' day
group by
    l_returnflag,
    l_linestatus
order by
    l_returnflag,
    l_linestatus
limit 1;
Click Preview. The result below indicates the data connection is available.

^

:-: ![](.topwrite/assets/image_1736938941276.png =657)

### By Creating Public Data

Select New Dataset -> SQL Dataset:

^

:-: ![](.topwrite/assets/image_1736939075914.png =660)

This indicates that the tables in Singdata Lakehouse are available as “Public Data” in FineBI.

Using data from Lakehouse in analysis topics:

^

:-: ![](.topwrite/assets/image_1736939239963.png =657)

^

### By Analysis View

Generate a new data view by dragging and dropping

:-: ![](.topwrite/assets/image_1736994382813.png =660)

^

Visualization component based on data view - Pie chart: analyzing used car sales by engine type

^

:-: ![](.topwrite/assets/image_1736994510861.png =665)

^

Visualization component based on data view - Cross table: analyzing used car sales by engine type and year

^

:-: ![](.topwrite/assets/image_1736994646263.png =669)

^