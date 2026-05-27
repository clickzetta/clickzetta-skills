# Complete Guide to Importing Data into Singdata Lakehouse

## Data Ingestion: Real-time Synchronization of Kafka Data Using Lakehouse Studio

#### Overview

#### Use Case

Existing Kafka data source with high real-time requirements for data synchronization, expecting to synchronize to Lakehouse tables in real-time with end-to-end second-level latency.

#### Implementation Steps

Navigate to Development -> Tasks, click "+", select "Real-time Sync", and create a new "Real-time Sync" job.

:-: ![](.topwrite/assets/image_1736319394961.png =740)

Main configuration as follows:

:-: ![](.topwrite/assets/image_1736319702232.png =740)

^

When selecting the source Kafka data source on the left, please configure the correct mode, groupId, and codec. Pay special attention to avoid reusing the groupId in multiple real-time sync tasks to prevent mutual interference and simultaneous data consumption, which could result in incomplete target data.

^

Then select the Lakehouse target on the right, choose an existing data table, or create a new data table (recommended): target\_table\_from\_kafka.

In the "Create Data Table" SQL code, change the table name to "target\_table\_from\_kafka".

:-: ![](.topwrite/assets/image_1736321482644.png =740)

^

In the "Field Mapping Configuration" area, Kafka Topic built-in fields will be used for data field mapping by default. If the message format in the Topic is JSON, you can also use the new calculated column method to parse the content in the value field using JSONPath rules. For example, extract the accountId field in the \_\_value\_\_ from the source topic and write it into the target \_\_value\_\_ field as shown in the figure below.

:-: ![](.topwrite/assets/image_1736322127793.png =740)

^

In the "Sync Rule Configuration", set the maximum concurrency for synchronization, which can increase the consumption speed through concurrency.

^

After checking that the field mapping meets expectations, set the required information such as "Cluster" in the configuration, click "OK", and then click "Save" to save the task configuration.

:-: ![](.topwrite/assets/image_1736322224165.png =740)

Real-time sync tasks currently do not support direct test runs. You need to submit and publish them, then check if the results are normal.

:-: ![](.topwrite/assets/image_1736322037109.png =740)

#### Next Steps

* In the Operations Center, start the real-time sync task, observe the task running metrics, and verify if the data synchronization results are normal.

  :-: ![](.topwrite/assets/image_1736322337162.png =740)

* For the first start, select the "Stateless Start" method.

  :-: ![](.topwrite/assets/image_1736322414065.png =740)

* After a normal start, you can see the following monitoring metrics, indicating that the sync task is running normally.

  :-: ![](.topwrite/assets/image_1736322603085.png =740)

* Spot check the data in the target table and verify it against the source to see if it meets expectations.

####

#### Resources

[Real-time Sync Tasks](realtime_sync.md)