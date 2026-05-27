# Experience Performance with TPCH Queries and Sample Data

## Overview

Through this tutorial, you will learn how to use the built-in sample dataset of the Lakehouse platform to quickly use SQL for query analysis and evaluate SQL functionality and performance without preparing data in advance.

> This tutorial leverages the Lakehouse Tutorial, providing an online tutorial guide and script import function. After logging into the Lakehouse Web console, you can enter the tutorial through the Lakehouse Tutorial entry and follow the online guide to complete the tutorial.
> ![](.topwrite/assets/image_1736854694431.png)

### Import Script

Open the "Lakehouse Tutorial" page in the console and select the "Quick Start Query Analysis with Sample Data" course. Follow the prompts on the page to import the script files needed for this course.

View the "Tutorial\_Run\_TPCH\_Queries\_USING\_SQL" directory in the "Development Module".
![](.topwrite/assets/image_1725286019515.png)

### Sample Dataset

The sample dataset is shared by the Singdata platform through a dataset named CLICKZETTA\_SAMPLE\_DATA, available for query by all accounts. This tutorial will use the TPC-H 100gb dataset within it as an example to demonstrate how to quickly complete TPC-H test set queries in Lakehouse and evaluate processing performance.

### Tutorial Steps

1. **Environment Preparation**: Check the raw data through the sample dataset and create a compute cluster for testing.
2. **Initiate Query**: Use the Studio Web environment to create SQL queries to complete 22 TPC-H SQL queries.
3. **Change Cluster Size**: Adjust the cluster size, doubling the previous cluster size.
4. **Initiate Query**: Use the resized cluster to complete the 22 TPC-H SQL queries again.
5. **Observe the changes in query latency under different cluster specifications**
6. **Clean Up Environment**: Delete the compute cluster used for testing.

Through the above steps, you will be able to evaluate the performance of SQL queries under different cluster specifications.

## Preparation

First, after logging into the Lakehouse Web console and entering the specified workspace, you can access the data module to check if the relevant tables under "clickzetta\_sample\_data.tpch\_100g" exist in the data object list under data management.
![](.topwrite/assets/image_1716285499384.png)

Next, we will temporarily create an independent compute cluster for query analysis for this test. You can create a new cluster through the "Compute → Clusters" menu in the Lakehouse Web console by following the page wizard.
![](.topwrite/assets/tpch_100g_vc.png)

At the same time, you can also create a cluster through SQL commands. When operating through SQL commands, you can control cluster creation, scaling, pausing/resuming, and destruction actions without leaving the SQL development context, often improving the efficiency of computing resource operations during Ad-hoc or ETL development processes.

This tutorial creates the compute cluster needed for analyzing the TPCH dataset by running the \[Tutorials/Tutorial\_Run\_TPCH\_Queries\_USING\_SQL/Step01.Preparation] SQL script task in the "Development" module.
![](https://studio-prod-sh.oss-cn-shanghai.aliyuncs.com/fe-asset/tutorials/resources/tu_tpch_vc01.png?OSSAccessKeyId=LTAI5tBH4MDxrfQw7VTx4w2B\&Expires=1880885164\&Signature=wYmSy3IVRKBT7mWtGhuKwT%2BwufQ%3D)

## TPC-H Query on Sample Data

Open the \[Tutorials/Tutorial\_Run\_TPCH\_Queries\_USING\_SQL/Step02.Run\_TPCH\_Queries] SQL script file in the "Development" module. You will see that the 22 TPC-H query statements have been entered. Select the test cluster just created from the \[Cluster] dropdown list, then select all scripts in the task and click the \[Run] button to perform serial queries.
![](.topwrite/assets/image_1725354834261.png)

After execution, you can view the runtime of this task through the current SQL Editor's run history.

If you want to perform performance testing, you can execute the queries more than twice consecutively so that the compute cluster can fully cache the data and achieve optimal performance. The following is the result of the second run, showing a significant performance improvement after the compute cluster caches the data compared to the first run without caching.
![](https://studio-prod-sh.oss-cn-shanghai.aliyuncs.com/fe-asset/tutorials/resources/tu_tpch_run_queries2.png?OSSAccessKeyId=LTAI5tBH4MDxrfQw7VTx4w2B\&Expires=1880886165\&Signature=XHaygkpuFRtqy%2FG1EExOjIfq7vw%3D)

If you want to see the execution details of each of the 22 queries, you can access Compute → Job History, filter the query history by the query tag "tpch100g\_benchmark" and view it.

![](.topwrite/assets/image_1716285600039.png)

## Query After Expanding Cluster Specifications

Through the Compute → Cluster Management page, you can modify the size of the test cluster you just created, changing it from Large to XLarge, where the XLarge size is twice that of Large.
![](https://studio-prod-sh.oss-cn-shanghai.aliyuncs.com/fe-asset/tutorials/resources/tu_tpch_resize_vc.png?OSSAccessKeyId=LTAI5tBH4MDxrfQw7VTx4w2B\&Expires=1880886486\&Signature=MJGwOtPq%2BHpD5E1WsHu1iyGrDnQ%3D)

Or execute the following command in the SQL script to modify:

```
-- Modify cluster size
alter vcluster TPCH_100GB SET VCLUSTER_SIZE = 'XLARGE';
```

After modification, use the resized cluster to perform the query test again.
![](https://studio-prod-sh.oss-cn-shanghai.aliyuncs.com/fe-asset/tutorials/resources/tu_tpch_round2.png?OSSAccessKeyId=LTAI5tBH4MDxrfQw7VTx4w2B\&Expires=1880886763\&Signature=UCaQAhoOLbeCKPrNUz22TVfAXNs%3D)
After the new expanded compute nodes are fully cached, the performance will continue to improve.
By observing the runtime of the job, it can be seen that with the same data scale and query tasks, by increasing the size of the compute cluster, the overall runtime of the task is greatly reduced. After two executions, as the data is cached, query performance can be improved.

## Environment Cleanup

Open the "Development" module \[Tutorial\_Run\_TPCH\_Queries\_USING\_SQL->Step03.Clean\_Up] SQL script file, and execute the script to delete the test cluster for this tutorial.
![](.topwrite/assets/image_1725288859033.png)
