# The Cost of Experiencing TPC-H 100G Performance Testing with a Bottle of Water in Three Minutes

TPC-H is a decision support benchmark developed by the Transaction Processing Performance Council (TPC). It consists of a suite of business-oriented ad-hoc queries and concurrent data modifications. TPC-H can model real production environments and simulate the data warehouse of a sales system. This test uses 8 tables with a data size of 100GB. A total of 22 queries were tested, with the main performance metric being the response time of each query, i.e., the duration between submitting the query and returning the result.
TPC-H performance testing is a time-consuming and costly process. To complete the test, you need to prepare machines, data, generate reports, etc., which often takes several days and incurs significant expenses. Based on Singdata Lakehouse's second-level elastic scaling virtual clusters and shared TPC-H datasets, the resource and data preparation process is eliminated. Using the method provided in this article, you can experience the complete performance test of Singdata Lakehouse and view the comparison report in 3 minutes.
The code in this article runs on [Zeppelin](eco_integration/Zeppelin.md). If you want to run the code in this article, please follow the documentation to install [Zeppelin](eco_integration/Zeppelin.md).

## Create a Test AP VC
```
-- Create analytical virtual computing resources
create vcluster if not exists VC_TPCH_100GB vcluster_size='Large' vcluster_type='Analytics'  AUTO_RESUME=TRUE AUTO_SUSPEND_IN_SECOND=300 min_replicas=1 max_replicas=1 comment 'TPCH 100GB TEST';

use vcluster VC_TPCH_100GB;
```
## Understanding the Data to be Tested

This test uses the TPC-H 100 GB dataset. Based on Singdata Lakehouse's inherent separation of storage and computation architecture, this dataset (clickzetta\_sample\_data.tpch\_100g) is shared and can be directly accessed by users, thus eliminating the data preparation process.
```
select "customer" as tablename, count(*) as row_count from clickzetta_sample_data.tpch_100g.customer
union all select "lineitem" as tablename, count(*) as row_count from clickzetta_sample_data.tpch_100g.lineitem
union all select "nation" as tablename, count(*) as row_count from clickzetta_sample_data.tpch_100g.nation
union all select "orders" as tablename, count(*) as row_count from clickzetta_sample_data.tpch_100g.orders
union all select "part" as tablename, count(*) as row_count from clickzetta_sample_data.tpch_100g.part
union all select "partsupp" as tablename, count(*) as row_count from clickzetta_sample_data.tpch_100g.partsupp
union all select "region" as tablename, count(*) as row_count from clickzetta_sample_data.tpch_100g.region
union all select "supplier" as tablename, count(*) as row_count from clickzetta_sample_data.tpch_100g.supplier;
```
Running the above code, we get the number of rows for each table in the test dataset:
![](.topwrite/assets/image_1718710238102.png)

## Test Process

![](.topwrite/assets/20240618195336_rec_.gif)

The entire process took less than 3 minutes, with 22 SQL queries running in a total of 16.718 seconds. The cost for this test, using a Large virtual compute cluster, was approximately 1.38 yuan for 3 minutes, which is about the price of a bottle of water.

## Congratulations, it's done.

Please enjoy and learn more!

## Appendix

### Download Zeppelin Notebook Source Files

[02.Quick Start ClickZetta Lakehouse Benchmark with TPCH Sample Data..ipynb](https://github.com/yunqiqiliang/clickzetta_quickstart/blob/main/zeppelin_notebook/02.Quick%20Start%20ClickZetta%20Lakehouse%20Benchmark%20with%20TPCH%20Sample%20Data..ipynb)
[02.Quick Start ClickZetta Lakehouse Benchmark with TPCH Sample Data\_2JH4XMBUG.zpln](https://github.com/yunqiqiliang/clickzetta_quickstart/blob/main/zeppelin_notebook/02.Quick%20Start%20ClickZetta%20Lakehouse%20Benchmark%20with%20TPCH%20Sample%20Data_2JH4XMBUG.zpln)