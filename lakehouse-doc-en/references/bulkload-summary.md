# Lakehouse Bulkload Quick Start

## Introduction

Bulkload is a high-throughput batch data write interface provided by Lakehouse, particularly suitable for scenarios with large volumes of continuous writes. Data written using Bulkload is immediately available for querying after commit.

## Batch Import Principles

The batch upload SDK provides an efficient data import mechanism for Singdata Lakehouse. Below is a simplified description and flowchart of its working principles:

1. **Data Upload**: Through the SDK, your data is first uploaded to the object storage service. The performance of this step is affected by local network speed and the number of concurrent connections.
2. **Trigger Import**: After the data upload is complete, when you call the `bulkloadStream.close()` method, the SDK automatically triggers a SQL command to import data from object storage into the Lakehouse table. It is not recommended to frequently call `bulkloadStream.close()` within a single task; this method should ultimately be called only once.
3. **Compute Resources**: For data uploads, it is recommended to select [General Purpose Virtual Cluster](virtual-cluster.md) (GENERAL PURPOSE VIRTUAL CLUSTER), which is better suited for running batch jobs and data loading tasks. The speed of data import from object storage to Lakehouse tables depends on the size of your configured compute resources.
4. **Shard Upload Optimization**: When processing compressed data larger than 1GB, it is recommended to assign a unique shard ID to each concurrent thread or process in the `createRow` method. This approach fully leverages the parallel processing advantages of multi-threading or multi-processing, significantly improving data import efficiency. Best practice is to determine the number of shard IDs based on the number of concurrent tasks, ensuring each concurrent task corresponds to an independent shard ID. If multiple concurrent tasks are assigned the same shard ID, the final written data may be overwritten, causing previously written data to be lost. To ensure all shard data is correctly imported into the table, call `bulkloadStream.close()` after all concurrent operations are complete to commit the entire import task.

Below is the flowchart of the batch import principle:

```
[SDK Upload Data] ──> [Object Storage] ──> [Call bulkloadStream.close()]
                                ↓
                         [Trigger SQL Command] ──> [Lakehouse Table]
```

## Applicable Scenarios

The batch file upload SDK is particularly suitable for the following situations:

* **One-Time Large Data Import**: When you need to import large amounts of data, whether it is a one-time batch task or a periodic operation with longer intervals.
* **Low Import Frequency**: If your data import frequency is not high (time interval greater than five minutes), using the batch import SDK is still appropriate even if the single import data volume is not large.

## Not Applicable Scenarios

The batch file upload SDK is not suitable for the following situations:

* **Real-Time Data Import**: If you need to import data frequently within a very short time (such as within 5 minutes), it is recommended to use the real-time data interface to meet real-time requirements.

^
