# Virtual Cluster

Virtual-Cluster (abbreviated as: VC, Vcluster) is a core service provided by Singdata Lakehouse, designed to offer users efficient and scalable **virtual cluster** resources. Virtual-Clusters provide the necessary CPU, memory, and temporary storage resources for tasks such as query analysis, ETL jobs, streaming analysis, and ad-hoc queries in Lakehouse. Through Virtual-Clusters, users can perform various complex data processing tasks in Lakehouse.

## Core Concepts

### Virtual Cluster Name

Each virtual cluster requires a unique name, which must be unique within a workspace. Once created, the cluster name cannot be changed. In Lakehouse, the full identifier of a virtual cluster is composed of the workspace name and the virtual cluster name.

### Specifications

The specifications of a **virtual cluster** define the amount of resources available to each **virtual cluster** replica. Specifications are measured in Compute Resource Units (CRU), ranging from 1 CRU to 256 CRU (Integration Virtual-Clusters also have two smaller specifications of 0.25 CRU and 0.5 CRU).

> **Note**: Starting from December 2024, the old specification codes for Virtual-Clusters, ranging from XS to 5XLarge, will be changed to numerical expressions. For more details, see: [Description of Virtual Cluster Specification Code Changes](vcluster_size_description.md).

| **Type**                           | **Minimum Specification (CRU**) | **Maximum Specification (CRU**) | **Default Value (CRU**) | **Step Size** (Minimum unit for specification increase/decrease)                                                                                                                    |
| ---------------------------------- | ------------------------------- | ------------------------------- | ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| General Purpose (GP VCluster)      | 1                               | 256                             | 1                       | 1（examples：1, 2, 3, 4, 5, 6...256）                                                                                                                                                  |
| Analytics (AP VCluster)            | 1                               | 256                             | 1                       | Powers of 2 (examples: 1, 2, 4, 8, 16, 32, 64, 128, 256)                                                                                                                            |
| Integration (Integration VCluster) | 0.25                            | 256                             | 0.5                     | 1 (Note that there are two special smaller specifications, 0.25 CRU and 0.5 CRU; all other specifications increase in increments of 1. Examples: 0.25, 0.5, 1, 2, 3, 4, 5, 6...256) |

The amount of resources consumed by each virtual cluster per hour is its CRU specification × 1 hour (i.e., in units of CRU·hour). For example, an Analytics Virtual-Cluster with a specification of 3 CRU running for 1 hour consumes 3 CRU × 1 hour = 3 CRU·hour. The cost is also calculated based on the “CRU·hour” unit price in the region where the **virtual cluster** is located.

### Virtual Cluster Types

Virtual-Clusters are divided into three categories: General Purpose, Analytics, and Integration:

* **General Purpose**: Suitable for handling offline jobs, sharing resources among jobs, and allocating virtual cluster resources to new and old jobs using a fair scheduling method.
* **Analytics**: Equipped with multiple **virtual cluster** instances and auto-scaling capabilities, suitable for handling online and high-concurrency jobs. When the job concurrency limit is reached, subsequent jobs will queue up, ensuring that jobs submitted first are executed first.
* **Integration**: Suitable for handling offline integration and real-time integration tasks. Multiple integration tasks can share a single Integration Virtual-Cluster instance. Integration tasks that exceed the cluster's capacity will enter a queue.

### Minimum Instances

This attribute is only supported by Analytics Virtual-Clusters. It refers to the number of cluster instances when the virtual cluster is initially started, with a default value of 1.

### Maximum Instances

This attribute is only supported by Analytics Virtual-Clusters. It refers to the maximum number of instances that the virtual cluster can use, with a default value of 2. When new queries exceed the current instance’s maximum concurrency, the virtual cluster’s auto-scaling will be triggered, adding a new virtual cluster instance. The upper limit for scaling virtual cluster instances is the maximum instance value.

### Auto Suspend

When there are no jobs running within the time specified in the auto-suspend configuration, the virtual cluster will automatically stop, release resources, and stop incurring costs. The minimum unit for auto-stop configuration is “seconds,” with a minimum configurable value of 15 seconds.

Since Virtual-Clusters running for less than 1 minute will be charged for 1 minute, please carefully confirm when choosing an auto-suspend time of less than 1 minute to avoid unnecessary costs.

### Auto Resume

When a new job is submitted, if the virtual cluster is suspended, the virtual cluster with the auto-start feature enabled will automatically start and execute the job. If this configuration is disabled, the specified virtual cluster needs to be started manually.

## Manage Virtual-Clusters

Singdata Lakehouse provides two ways to manage and control Virtual-Clusters:

1. Web-UI
2. SQL

The following introduces how to manage Virtual-Clusters via the Web-UI:

### View Cluster Information

Log in to the Lakehouse platform, click on the "Compute" function in the left menu to enter the "Virtual-Clusters" list page. On this page, you can view all authorized Virtual-Clusters within the current workspace.

:-: ![](.topwrite/assets/image_1740571665576.png =781)

^

Click on any virtual cluster name to enter the details page, where you can view the job execution status, configuration details, and the current user’s permissions for the cluster.

### Create a Virtual-Cluster

On the "Virtual-Clusters" list page, click the "New Cluster" button to enter the creation interface. After filling in the cluster name, selecting the cluster type, and configuring the specifications, click "Create Cluster" to complete the creation. The newly created virtual cluster will be displayed in the list and can be used once its status changes to “Running.”

^

#### Creating a General-Purpose VCluster

:-: ![](.topwrite/assets/image_1742218824795.png =388)

If you need to run ETL or other batch workloads, we recommend creating a **General-Purpose** compute cluster:

* In the **Type** field, select **General-Purpose**.

* In the **Specification** field, you can choose between **Fixed** or **Elastic**.

  * **Fixed** indicates the cluster size does not scale according to workload, providing predictable resource consumption and cost control.
  * **Elastic** indicates the cluster will scale according to workload demands, which is more suitable for scenarios where stringent task SLAs are required.

> **Note**: The elastic scaling approach for General-Purpose clusters is designed to complete all submitted tasks as quickly as possible. When the current capacity is fully utilized, the cluster immediately scales out to accommodate all tasks. This approach prioritizes speed over cost efficiency. Evaluate your needs for cost versus performance before deciding on a **Fixed** or **Elastic** configuration, and be sure to set an appropriate maximum and minimum specification when using elastic scaling.

* Choose whether to enable **Auto-Start** and **Auto-Stop**, then configure a suitable **Auto-Stop** timeout. We recommend enabling **Auto-Start** to handle incoming workloads promptly, and setting the **Auto-Stop** timeout to **1 minute** so that the compute cluster can be shut down quickly once all jobs have completed—helping to control costs.

After setting these properties, click **OK** to finish creating your General-Purpose cluster.

***

#### Creating an Analytics VCluster

:-: ![](.topwrite/assets/image_1742218772034.png =436)

If you need a cluster to support ad-hoc queries or BI dashboard workloads, we recommend creating an **Analytics** cluster:

* In the **Type** field, select **Analytics**.
* In the **Specification** field, choose the cluster size that meets your workload requirements. Typically, cluster size correlates with the number of concurrent requests, data volume, and query complexity, and inversely with the expected query response time. After creating the cluster, you can perform concurrency tests to fine-tune your cluster size for optimal performance and cost.
* Decide whether to enable **Auto-Start** and **Auto-Stop**, then specify a suitable **Auto-Stop** timeout. We recommend enabling **Auto-Start** to process queries promptly and setting an **Auto-Stop** timeout of at least **30 minutes** so you can make use of the analytics cluster’s caching and deliver faster responses for end users.
* Configure the **Maximum Concurrency**. This setting determines the maximum number of concurrent queries each instance in the cluster can handle. If the workload concurrency exceeds this value, requests will queue or trigger automatic scaling.
* **Minimum Instances** and **Maximum Instances** define the lower and upper bounds when the cluster auto-scales. When every instance in the cluster is at maximum concurrency, the system begins adding instances until concurrency is satisfied or the **Maximum Instances** limit is reached. New or queued queries are then distributed to the new instances, without impacting queries already in progress. When the cluster can still meet concurrency demands after removing an instance, it starts to scale in, continuing until it reaches the **Minimum Instances** or a capacity that meets all concurrency needs. During scale-in, queued or newly submitted queries will not be assigned to the instance being removed, and ongoing queries on that instance are not interrupted.

^

#### Creating a Synchronization VCluster

:-: ![](.topwrite/assets/image_1742218710213.png =398)

If you need to run offline or real-time data integration tasks, create a **INTEGRATION** cluster:

* In the **Type** field, select **Integation**.

* In the **Specification** field, you can choose between **Fixed** or **Elastic**.

  * **Fixed** indicates the cluster size does not change based on workload, which helps manage resource consumption and costs.
  * **Elastic** indicates the cluster automatically adjusts its size to handle varying workloads, which is beneficial when strong SLA guarantees are required.

> **Note**: Elastic scaling for a Integation cluster is also designed to complete all submitted tasks as quickly as possible. When the current capacity is fully utilized, the cluster immediately expands to accommodate the entire set of tasks. This strategy prioritizes efficiency over cost. Carefully weigh performance requirements against cost and configure your cluster with the appropriate **Fixed** or **Elastic** strategy, along with suitable minimum and maximum capacity settings.

* Synchronization clusters offer a **Specification Estimation** feature to help identify an appropriate cluster size. By entering the **Number of Tasks** and the **Average Concurrency** per task, the system calculates a recommended specification using the formula:  Specification = Number of Tasks \* Average Concurrency \* 0.05
* Choose whether to enable **Auto-Start** and **Auto-Stop**, then configure a suitable **Auto-Stop** timeout. We recommend enabling **Auto-Start** for timely task processing and setting **Auto-Stop** to **1 minute** so the cluster can shut down soon after all jobs complete, minimizing costs.

### Modify Virtual-Cluster Properties

In the cluster list, select the corresponding virtual cluster and click the "Modify" button in the "Actions" column to adjust the configuration. Modifying the configuration may affect the cluster status, so ensure there are no running jobs on the virtual cluster when changing key attributes such as specifications and the number of instances.

### Start and Stop Virtual-Clusters

In the cluster list, click the "Start" or "Stop" button in the "Actions" column to start or stop the virtual cluster.Please note that when you stop a virtual cluster, it waits for all ongoing jobs to finish before fully stopping.

^

### Delete a Virtual-Cluster

In the cluster list, click the "Delete" button in the "Actions" column to delete the specified virtual cluster. Before deleting a virtual cluster, it needs to be stopped, and all ongoing jobs must be completed before the deletion can be performed.

## Manage Virtual-Clusters Using DDL

In addition to the Web-UI, Lakehouse also supports using SQL commands to directly operate Virtual-Clusters. For specific commands and usage methods, please refer to the [Virtual-Cluster DDL](create_cluster.md) document.

### Virtual-Cluster Configuration Practices

#### Automated Management of Virtual-Clusters

Virtual-Cluster instances can be awakened by submitted jobs while in a stopped state, start within seconds, and begin executing jobs. They can also automatically shut down when idle to save costs. Fully utilizing this feature can make the cost of Virtual-Clusters closely match the business load, significantly improving resource utilization.

* **Configure Auto-Suspend and Auto-Resume**: In the window for creating or modifying a virtual-cluster instance, you can find the configuration items for “Auto-Resume” and “Auto-Suspend.” Typically, these two configurations are set together: enable “Auto-Resume” and set the “Auto-Suspend” time.
* **Set Appropriate Timeout Limits**: The “Auto-Suspend” time for Virtual-Clusters can be set from 1 minute to 3 hours. When configuring the ‘Auto-Suspend’ time，you should consider the impact that starting and stopping the virtual cluster will have on any running jobs:
  1. For offline jobs, the “Auto-Suspend” time can be set as short as possible, such as 1 minute. This allows the virtual cluster to stop running as soon as the job is completed, avoiding resource waste during idle time.
  2. For online query services, the “Auto-Suspend” time needs to be appropriately extended. This can minimize the query request delay caused by the transition from “Stopped” to “Started,” ensuring a good query experience. It can also extend the cache time of query results (for Analytics Virtual-Clusters), improving query efficiency.
  3. It is strongly discouraged to set the “Auto-Suspend” time to less than 1 minute. Since Virtual-Cluster billing is per second, if the running time is less than 60 seconds, it will be billed as 60 seconds. If the Auto-Suspend time is set to less than 1 minute, and the jobs running on the virtual cluster are very short, it may cause the cluster to start and stop multiple times within 1 minute, resulting in multiple 60-second charges and increased costs. Only when it is confirmed that the job duration on the virtual cluster will not cause multiple starts and stops within 1 minute, can the Auto-Suspend time be set to less than 1 minute.

#### Reasonably Scale Up or Down Virtual-Cluster Specifications

Instance specifications refer to vertically scaling a virtual cluster. Adjusting instance specifications can provide more computing power for a single job to improve job performance.

In actual business scenarios, data products facing users often have SLA requirements, such as P99 query latency under 100 concurrent users being less than 2 seconds. At the same time, it is hoped that resources are fully utilized to minimize costs while meeting business needs.

In actual business use, it is recommended to run queries using Virtual-Clusters of different sizes (e.g., testing with specifications from larger to smaller) to find the smallest possible resource specification that does not significantly degrade performance.

Providing sample specifications from the dimensions of business load type, execution frequency, job concurrency, data processing scale, and SLA requirements for reference:

| Business Scenario         | Load Type                         | Execution Frequency | Job Concurrency | Data Processing Scale | VCluster Type   | Job Latency SLA    | VCluster Size |
| ------------------------- | --------------------------------- | ------------------- | --------------- | --------------------- | --------------- | ------------------ | ------------- |
| ETL Scheduling Jobs       | Near Real-time Offline Processing | Hourly              | 1               | 1 TB                  | General Purpose | 15 Min             | 4             |
|                           | T+1 Offline Processing            | Daily               | 1               | 10 TB                 | General Purpose | 4 Hours            | 8             |
| Tableau/PowerBI           | Ad-Hoc Analytics                  | Ad-Hoc              | 8               | 1 TB                  | General Purpose | <1 Min (TP90 <5s)  | 16            |
| Data Application Products | Applications                      | On demand           | 8               | 100 GB                | Analytics       | <3 seconds         | 4             |
|                           |                                   | On demand           | 96              | 100 MB                | Analytics       | <3 seconds         | 4             |
| ClickZetta Web-UI         | Ad-Hoc Analytics                  | Ad-Hoc              | 8               | 3 TB                  | General Purpose | <1 Min (TP90 <15s) | 16            |

#### Achieving Load Isolation through Multiple Virtual Clusters&#x20;

* Use multiple independent **virtual clusters** to support different business workloads. Different virtual clusters can be created and allocated to different users or applications based on various needs—such as periodic ELT, online business reports, or analyst data exploration—to avoid SLA degradation caused by resource contention among different businesses or personnel.

  **For example**:

  * Periodic ELT tasks and online business report queries should use different virtual clusters for isolation, and use General Purpose and Analytics types of Virtual-Clusters respectively to fully leverage the performance characteristics of different types of virtual clusters. It is also easier to configure different auto-suspended times—setting a very short auto-suspended (e.g., 1 minute) for the virtual cluster running periodic ELT tasks, and setting a slightly longer auto-suspended (e.g., 5 minutes) for the virtual cluster running online business report queries.
  * Isolate virtual clusters running large jobs and small jobs. Configure larger virtual clusters for large jobs to ensure sufficient runtime, and configure smaller virtual clusters for small jobs to avoid underutilizing the cluster, thus preventing resource waste.

^
