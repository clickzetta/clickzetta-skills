# Support Multiple Concurrent Queries with Horizontal Elastic Scaling

## Overview

Through this tutorial, you will learn how to use the horizontal elastic scaling capability of the Lakehouse virtual compute cluster to support dynamically changing multiple concurrent queries from clients.

> This tutorial leverages the Lakehouse Tutorial intelligent assistant, providing online tutorial guides and script import functions. After logging into the Lakehouse Web console, you can access the tutorial through the "Lakehouse Tutorial" entry in the Lakehouse Tutorial and follow the online guide to complete the tutorial.
> ![](.topwrite/assets/image_1736854951691.png)

### Import Scripts

Open the "Lakehouse Tutorial" on the console's Tutorial page and select the "Support Multiple Concurrent Queries with Horizontal Elastic Scaling" course. Follow the prompts on the page to import the script files needed for this course.

View the "Tutorial\_Working\_With\_Concurrency\_Scaling" directory in the "Development Module".

![](.topwrite/assets/image_1725287877169.png =436)

### Basic Knowledge

A virtual compute cluster (Virtual Cluster, abbreviated as VC or cluster) is a computing resource object provided by Singdata Lakehouse for data processing and analysis. Virtual compute clusters provide the CPU, memory, and local temporary storage (SSD medium) resources needed to execute SQL jobs in Lakehouse. Clusters feature rapid creation/destruction, scaling up/down, pausing/resuming, and are charged based on resource specifications and usage duration, with no charges incurred after pausing or deletion. Virtual compute clusters offer two types of clusters, general-purpose and analytical, to meet the isolation and optimization needs of different workloads for ETL and analysis scenarios.

![](.topwrite/assets/image_1714992266569.png =700)

### Tutorial Steps

1. **Environment Preparation**: Create a compute cluster for testing.
2. **Initiate Queries**: Use the Studio Web environment to create Python tasks to perform continuous queries on Lakehouse with different concurrency levels, and observe the execution log results of the Python tasks to understand the cluster's rapid scaling capabilities under different concurrent requests.
3. **Clean Up Environment**: Delete the compute cluster used for testing.

Through the above steps, you will be able to understand how to configure and use the elastic concurrency feature of virtual clusters and understand the performance of elastic concurrency.

## Preparation

First, create an analytical compute cluster and enable and set the elastic concurrency feature through SQL commands.

This tutorial creates a cluster and sets the elastic scaling policy by running the \[Tutorial\_Working\_With\_Concurrency\_Scaling->Step01.Preparation] SQL script task in the "Development" module.
![](.topwrite/assets/image_1725288058473.png)

## Initiate Concurrent Queries Using Python Program

Open the \[Tutorial\_Working\_With\_Concurrency\_Scaling->Step02.Run\_Concurrent\_Queries] Python concurrent task template in the \[Development] module. You need to modify the connect connection configuration parameters before you can connect to Lakehouse and execute queries.

![](https://studio-prod-sh.oss-cn-shanghai.aliyuncs.com/fe-asset/tutorials/resources/tu_concurrent_connection.png?OSSAccessKeyId=LTAI5tBH4MDxrfQw7VTx4w2B\&Expires=1880895431\&Signature=B2eODbnltYz%2FzjifxINWWzcf%2Bzw%3D)

After modifying the connection information, please click to run the task and view the task execution log.

![](https://studio-prod-sh.oss-cn-shanghai.aliyuncs.com/fe-asset/tutorials/resources/tu_concurrent_report.png?OSSAccessKeyId=LTAI5tBH4MDxrfQw7VTx4w2B\&Expires=1880982939\&Signature=%2B1YAL8o1IDjFdlaIpBgxB0Sa%2B90%3D)
By observing the printed performance report, you can see that the Reporting\_VC cluster scales horizontally with millisecond-level latency by dynamically increasing the number of replicas as the client's concurrent requests increase. Dynamic scaling maintains the query SLA for continuous concurrent requests.

While executing the task, you can also view the cluster's concurrent requests and elastic scaling status through the cluster monitoring page.
![](https://studio-prod-sh.oss-cn-shanghai.aliyuncs.com/fe-asset/tutorials/resources/python_concurrency_scaling.gif?OSSAccessKeyId=LTAI5tBH4MDxrfQw7VTx4w2B\&Expires=2034444050\&Signature=wnBuZv1bereCq1etNW66OrF6UsA%3D)

## Environment Cleanup

Open the "Development" module \[Tutorial\_Working\_With\_Concurrency\_Scaling->Step03.Clean\_Up] SQL script file, execute the script to delete the test cluster for this tutorial.
![](.topwrite/assets/image_1725288753867.png)
