# Virtual Cluster

A Virtual Cluster (VCluster) is a core service provided by Singdata Lakehouse, designed to give you efficient and scalable compute resources. Virtual clusters provide the CPU, memory, and temporary storage needed for query analysis, ETL jobs, streaming analysis, and ad-hoc queries in Lakehouse. Through virtual clusters, you can run a wide range of complex data processing tasks.

## Core Concepts

### Cluster Name

Each virtual cluster requires a unique name within the workspace. Once created, the cluster name cannot be changed. In Lakehouse, a virtual cluster is fully identified by the combination of its workspace name and cluster name.

### Specifications

A virtual cluster's specification defines the amount of compute resources available to each compute replica, measured in Compute Resource Units (CRU). CRU is Singdata Lakehouse's abstraction of IaaS compute capacity, providing consistent performance across different cloud platforms, CPU architectures, and instance types.

> ⚠️ **Note**: Starting from December 2024, the old specification codes for virtual clusters (XS through 5XLarge) have been replaced with numeric specifications. For details, see [Virtual Cluster Specification Code Change Description](vcluster_size_description.md).

| **Type**                              | **Minimum Spec (CRU)** | **Maximum Spec (CRU)** | **Default (CRU)** | **Step Size** (minimum increment/decrement unit)                                          |
| ------------------------------------- | ---------------------- | ---------------------- | ----------------- | ----------------------------------------------------------------------------------------- |
| General Purpose (GP VCluster)         | 1                      | 256                    | 1                 | 1 CRU per step. Examples: 1, 2, 3, 4, 5, 6...256                                         |
| Analytics (AP VCluster)               | 1                      | 256                    | 1                 | Powers of 2. Examples: 1, 2, 4, 8, 16, 32, 64, 128, 256                                  |
| Integration (Integration VCluster)    | 0.25                   | 256                    | 0.5               | Supports any decimal specification. Examples: 0.25, 0.5, 0.75, 1, 1.25...256             |

> ⚠️ **Note**: Analytics cluster specifications must be a power of 2 (1, 2, 4, 8, 16, 32, 64, 128, 256). Setting any other value will result in an error.

The compute resources consumed by a cluster per hour equal its CRU specification × 1 hour (unit: CRU·hour). For example, an Analytics cluster with a 3 CRU specification running for 1 hour consumes 3 CRU × 1 hour = 3 CRU·hours. Costs are calculated based on the "CRU·hour" unit price for the region where the cluster is located.

### Cluster Types

Virtual clusters come in three types: General Purpose, Analytics, and Integration.

* **General Purpose (GENERAL)**: Suitable for offline jobs. Jobs share compute resources, and new and existing jobs are allocated resources using fair scheduling.
* **Analytics (ANALYTICS)**: Supports multiple compute instances and auto-scaling. Suitable for online and high-concurrency workloads. When the concurrency limit is reached, subsequent jobs queue up, ensuring first-submitted jobs are executed first.
* **Integration (INTEGRATION)**: Suitable for offline and real-time integration tasks. Multiple integration tasks can share a single Integration cluster instance. Tasks that exceed the cluster's capacity enter a queue.

The relationship between cluster types and task types is shown below:

| **Task Type**           | **Supported Cluster Types**  | **Recommended Cluster Type**                                                  |
| ----------------------- | ---------------------------- | ----------------------------------------------------------------------------- |
| Offline Sync            | Integration                  | Integration                                                                   |
| SQL                     | General Purpose, Analytics   | **ETL tasks**: General Purpose<br>**Ad-hoc queries**: Analytics               |
| Python                  | No cluster required          | /                                                                             |
| Shell                   | No cluster required          | /                                                                             |
| JDBC                    | No cluster required          | /                                                                             |
| Virtual Node            | No cluster required          | /                                                                             |
| Databricks SQL          | No cluster required          | /                                                                             |
| Databricks Notebook     | No cluster required          | /                                                                             |
| Real-time Sync          | Integration                  | Integration                                                                   |
| Multi-table Real-time Sync | Integration               | Integration                                                                   |
| Dynamic Table           | General Purpose, Analytics   | **Low-frequency, large data volume**: General Purpose<br>**High-frequency, small data volume**: Analytics |
| Streaming SQL           | General Purpose, Analytics   | **Low-frequency, large data volume**: General Purpose<br>**High-frequency, small data volume**: Analytics |

:-: ![](.topwrite/assets/image_1743421840284.png =782)

^

### Minimum Instances

Only supported by Analytics clusters. Specifies the number of cluster instances when the cluster first starts. Default is 1.

### Maximum Instances

Only supported by Analytics clusters. Specifies the maximum number of instances the cluster can use. Default is 2. When new queries exceed the current instance's maximum concurrency, auto-scaling is triggered and a new instance is added. Scaling stops when the maximum instance count is reached.

### Auto Suspend

When no jobs have run within the configured auto-suspend period, the cluster automatically stops, releases resources, and stops incurring compute costs. The minimum auto-suspend unit is seconds, with a minimum configurable value of 15 seconds.

> ⚠️ **Note**: Clusters that run for less than 1 minute are billed for a full minute. If you set the auto-suspend time to less than 1 minute, confirm carefully to avoid unnecessary charges.

### Auto Resume

When a new job is submitted and the cluster is suspended, a cluster with auto-resume enabled will automatically start and execute the job. If auto-resume is disabled, the cluster must be started manually. To manually start a cluster, use the Start button in the cluster list (see "Starting and Stopping Clusters" below) or run `ALTER VCLUSTER <vcluster_name> RESUME;`.

## Managing Virtual Clusters

Singdata Lakehouse provides two ways to manage virtual clusters: 1) Web UI; 2) SQL.

### Web UI

#### Viewing Cluster Information

Log in to the Lakehouse platform and click "Compute" in the left menu to open the "Virtual Clusters" list page. Here you can view all virtual clusters in the current workspace that you have access to.

![](.topwrite/assets/image_1741611037239.png)

Click any cluster name to open the details page, where you can view job execution status, configuration details, and your permissions for that cluster.

:-: ![](.topwrite/assets/image_1728532541352.png =805)

#### Creating a Virtual Cluster

On the "Virtual Clusters" list page, click "New Cluster" to open the creation interface. Fill in the cluster name, select the cluster type, configure the specification, and click "Create Cluster." The new cluster will appear in the list and can be used once its status changes to "Running."

:-: ![](.topwrite/assets/image_1742214451076.png =813)

^

**Creating a General Purpose Cluster**

:-: ![](.topwrite/assets/image_1742216967064.png =414)

If you need to run ETL or other batch workloads, create a General Purpose cluster:

* In the "Type" field, select "General Purpose."
* In the "Specification" field, choose between "Fixed" and "Elastic Scaling." "Fixed" means the cluster size does not change with load, giving you predictable resource consumption and cost control. "Elastic Scaling" means the cluster size adjusts with load, which is better suited for scenarios with strict task SLA requirements.

> ⚠️ **Note**: Elastic scaling for General Purpose clusters is designed to complete all submitted tasks as quickly as possible. When the current specification is fully utilized, the cluster immediately scales out to meet the needs of all tasks. This strategy prioritizes efficiency over cost. Choose "Fixed" or "Elastic Scaling" based on your actual cost and performance needs, and set appropriate minimum and maximum specifications for elastic scaling.

* Choose whether to enable "Auto Resume" and "Auto Suspend," and configure a suitable "Auto Suspend" time. We recommend enabling "Auto Resume" to handle jobs promptly, and setting "Auto Suspend" to 1 minute so the cluster shuts down quickly after jobs complete, saving costs.

After completing the configuration, click "OK" to finish creating the General Purpose cluster.

^

**Creating an Analytics Cluster**

:-: ![](.topwrite/assets/image_1742216902917.png =404)

^

If you need compute resources for ad-hoc queries or BI dashboards, create an Analytics cluster:

* In the "Type" field, select "Analytics."
* In the "Specification" field, choose a size that fits your workload. Cluster size generally correlates positively with request concurrency, data volume, and query complexity, and negatively with expected query response time. After creating the cluster, run concurrency tests and gradually adjust the specification to find the optimal balance of performance and cost.
* Choose whether to enable "Auto Resume" and "Auto Suspend," and configure a suitable "Auto Suspend" time. We recommend enabling "Auto Resume" to handle queries promptly, and setting "Auto Suspend" to 30 minutes or more to take advantage of the Analytics cluster's cache and deliver a better query experience to end users.
* Configure "Maximum Concurrency." This is the maximum number of concurrent jobs each instance can handle. When concurrency exceeds this value, jobs will queue or trigger a new instance to be added.
* "Minimum Instances" and "Maximum Instances" define the lower and upper bounds for auto-scaling. When all instances in the cluster reach maximum concurrency, new instances are added until concurrency is satisfied or the maximum instance count is reached. Queued or newly submitted jobs are distributed to the new instances; jobs already in progress are not affected. When the cluster can still handle all concurrency after removing one instance, it begins scaling in, stopping at the minimum instance count or the smallest count that satisfies all concurrency. During scale-in, queued or newly submitted jobs are not assigned to the instance being removed, and jobs already running on that instance are not interrupted.

^

**Creating an Integration Cluster**

:-: ![](.topwrite/assets/image_1742217991159.png =411)

If you need to run offline or real-time integration tasks, create an Integration cluster:

* In the "Type" field, select "Integration."
* In the "Specification" field, choose between "Fixed" and "Elastic Scaling." "Fixed" means the cluster size does not change with load, giving you predictable resource consumption and cost control. "Elastic Scaling" means the cluster size adjusts with load, which is better suited for scenarios with strict task SLA requirements.

> ⚠️ **Note**: Elastic scaling for Integration clusters is also designed to complete all submitted tasks as quickly as possible. When the current specification is fully utilized, the cluster immediately scales out to meet the needs of all tasks. This strategy prioritizes efficiency over cost. Choose "Fixed" or "Elastic Scaling" based on your actual cost and performance needs, and set appropriate minimum and maximum specifications.

* Integration clusters provide a "Specification Estimation" feature to help you choose an appropriate size. Enter the "Number of Tasks" and "Average Task Concurrency," and the system calculates an estimated specification using the formula: Specification = Number of Tasks × Average Task Concurrency × 0.05.

:-: ![](.topwrite/assets/image_1742218209994.png =441)

* Choose whether to enable "Auto Resume" and "Auto Suspend," and configure a suitable "Auto Suspend" time. We recommend enabling "Auto Resume" to handle jobs promptly, and setting "Auto Suspend" to 1 minute so the cluster shuts down quickly after jobs complete, saving costs.

^

#### Modifying Virtual Cluster Properties

In the cluster list, select the cluster and click "Modify" in the "Actions" column to adjust its configuration. Configuration changes may affect cluster status. When modifying key attributes such as specification or instance count, make sure there are no jobs currently running on the cluster.

:-: ![](.topwrite/assets/image_1733812147311.png =813)

#### Starting and Stopping a Virtual Cluster

In the cluster list, click "Start" or "Stop" in the "Actions" column to start or stop the cluster. When stopping a cluster, it waits for all running jobs to complete before fully stopping.

:-: ![](.topwrite/assets/image_1733812217836.png =813)

^

#### Deleting a Virtual Cluster

In the cluster list, click "Delete" in the "Actions" column to delete the specified cluster. The cluster must be stopped and all jobs must be complete before deletion can proceed.

:-: ![](.topwrite/assets/image_1733812348735.png =810)

### SQL

In addition to the Web UI, Lakehouse also supports managing virtual clusters directly with SQL commands. For specific commands and usage, see the [Virtual Cluster DDL](create_cluster.md) documentation.

## Virtual Cluster Configuration Best Practices

#### Automated Cluster Management

Virtual cluster instances can be woken up by submitted jobs while stopped, start within seconds, and automatically shut down when idle to save costs. Taking full advantage of this capability allows cluster costs to closely track business load, significantly improving resource utilization.

* **Configure auto-suspend and auto-resume**: In the cluster creation or modification window, find the "Auto Resume" and "Auto Suspend" configuration options. These two settings are typically configured together: enable "Auto Resume" and set an "Auto Suspend" time.
* **Set an appropriate timeout**: The "Auto Suspend" time can be set from 1 minute to 3 hours. Consider the impact of cluster start/stop on your jobs when choosing:
  1. For offline jobs, set "Auto Suspend" as short as possible — for example, 1 minute — so the cluster stops quickly after jobs complete, avoiding idle resource waste.
  2. For online query services, extend "Auto Suspend" appropriately — for example, 30 minutes. This minimizes query latency caused by the cluster transitioning from stopped to running, and extends the cache lifetime for Analytics clusters, improving query performance. To proactively preload hot tables into the cluster cache for further query acceleration, see [Compute Cluster Cache](vc_cache.md).
  3. It is strongly discouraged to set "Auto Suspend" to less than 1 minute. Since billing is per second and any run under 60 seconds is billed as 60 seconds, a very short auto-suspend time combined with very short jobs could cause the cluster to start and stop multiple times within a minute, each time incurring a 60-second charge. Only set auto-suspend below 1 minute if you are certain the jobs on that cluster will not cause multiple start/stop cycles within a minute.

#### Scaling Cluster Specifications Up or Down

Cluster specification is the option for vertically scaling a virtual cluster. Adjusting the specification gives individual jobs more compute power to improve performance.

In practice, user-facing data products often have SLA requirements — for example, P99 query latency under 100 concurrent users must be under 2 seconds. At the same time, you want resources to be fully utilized and costs minimized while meeting business needs.

In practice, it is recommended to test queries with different cluster sizes (for example, from 8 CRU down to 1 CRU) to find the smallest specification that does not significantly degrade performance.

The following table provides sample specifications across several dimensions — business load type, execution frequency, job concurrency, data volume, and SLA requirements — for reference:

| Business Scenario                       | Load Type                  | Execution Frequency | Job Concurrency | Data Volume | VCluster Type   | Job Latency SLA              | VCluster Size |
| --------------------------------------- | -------------------------- | ------------------- | --------------- | ----------- | --------------- | ---------------------------- | ------------- |
| ETL Scheduling Jobs                     | Near real-time offline     | Hourly              | 1               | 1 TB        | General Purpose | 15 min                       | 4             |
|                                         | T+1 offline                | Daily               | 1               | 10 TB       | General Purpose | 4 hours                      | 8             |
| Tableau/FineBI                          | Ad-hoc analytics           | Ad-hoc              | 8               | 1 TB        | General Purpose | <1 min, TP90 <5s             | 16            |
| Data Application Products               | Applications               | On demand           | 8               | 100 GB      | Analytics       | <1s                          | 4             |
|                                         |                            | On demand           | 96              | 100 MB      | Analytics       | <1s                          | 4             |
| Singdata Web UI (Data Development/Test) | Ad-hoc analytics           | Ad-hoc              | 8               | 3 TB        | General Purpose | <1 min, TP90 <15s            | 16            |

#### Load Isolation with Multiple Clusters

* Use multiple independent clusters to support different business workloads. Create separate clusters for different needs — such as periodic ELT, online business reports, and analyst data exploration — and assign them to different users or applications. This prevents resource contention between different teams or workloads from degrading SLAs.

  For example:

  * Periodic ELT tasks and online business report queries should use separate clusters for isolation. Use General Purpose for ELT and Analytics for reports to take full advantage of each type's performance characteristics. This also makes it easy to configure different auto-suspend times — set a short auto-suspend (e.g., 1 minute) for the ELT cluster, and a slightly longer one (e.g., 5 minutes) for the reporting cluster.

  * Isolate clusters running large jobs from those running small jobs. Configure a larger cluster for large jobs to ensure sufficient runtime, and a smaller cluster for small jobs to avoid underutilization and resource waste.
