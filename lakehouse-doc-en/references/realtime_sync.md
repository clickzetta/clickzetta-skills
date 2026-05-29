# Real-time Sync Tasks

The "Development" module of the Singdata Lakehouse workspace integrates the capabilities of defining and scheduling data sync tasks. With the data sync task editor in the data development module, you can quickly create data sync tasks. The following explains the creation and use of real-time sync tasks.

## Create a New Data Sync Task

You can create a new sync task from both the workspace and the development entry.

* Create from Workspace
  Through the console "Workspace" entry, select to create a new offline sync or real-time sync task under the "New" button on the right.

* Create from Development Entry
  You can enter the "Development" page and select to create a new sync task in the specified directory in the task area.

## Real-time Sync Task Development

Here, we take the real-time sync of Kafka data source to Lakehouse as an example.

* Create a new real-time data sync task and configure source and target information
  Select the Kafka data source, choose the Topic through the data object, and specify the offset and message format. Select the Lakehouse data source and the corresponding data object for the target end.

  By default, the built-in fields of the Kafka Topic are used for data field mapping. If the message format in the Topic is JSON, you can also use the new calculated column method to parse the content in the value field through JSONPath rules, such as $.id, $.data.code。

* Deploy to Production
  Real-time sync tasks do not support test runs in the development state and do not require scheduling strategy configuration. You can publish the task through the "Submit" button.

  After submission, you can perform start and stop operations and monitoring of real-time sync tasks in the Operations Center.


^
