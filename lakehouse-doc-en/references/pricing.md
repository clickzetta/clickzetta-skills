# Overview of Billing Methods

Singdata Lakehouse is an integrated data platform built on cloud-native technology. The platform records the resources you consume in scenarios such as data integration, data analysis, storage, and network data transmission, and charges you accordingly based on three resource types — computing, storage, and network — depending on the cloud platform and region where the service occurs.

The billing of Singdata Lakehouse is mainly based on the following aspects:

* **Computing Resources**: The billing unit for computing resources is **CRU\*hour**, where 1 CRU\*hour represents running with the same computing power for 1 hour in a service region of a cloud platform. The use of general-purpose, analytical, and synchronous computing clusters for data integration or data analysis, tasks processed using Python or Shell scripts, and operations such as automatic materialized views (Auto\_MV), data compression, and job scheduling automatically handled by the system will all generate computing resource consumption. Singdata will measure and bill based on the actual amount of computing power consumed.
* **Storage Resources**: The billing unit for storage resources is **GiB**, and billing is based on the actual storage capacity you use on Singdata Lakehouse. The following scenarios will occupy storage capacity: 1) Data stored in Lakehouse in the form of tables, materialized views, etc.; 2) Data deleted but not yet cleaned up within the lifecycle of the data table; 3) Cached query results. Items 2 and 3 are currently only measured and temporarily free of charge.
* **Data Transmission**: The billing unit for data transmission is **GB**, and billing is based on the actual amount of data transmitted. The following scenarios will incur data transmission fees: 1) Data queries through the public network, full download of query results; 2) Data transmission between Singdata Lakehouse and other data sources; 3) Network connectivity through the Internet, cross-VPC connections, dedicated lines, or other methods. For Internet network traffic, only the data transmission volume flowing out of Singdata Lakehouse is measured; uploading data to Singdata Lakehouse is free of charge.

## Billing Methods

### 1. Pay-as-you-go

In Singdata Lakehouse, all types of resources are flexibly scalable and used on-demand. You only need to pay for the amount of resources actually used.

| Resource Type       | Metering Method                     | Settlement Cycle |
| ------------------- | ----------------------------------- | ---------------- |
| Computing Resources | Metered by the second, in CRU       | Every hour       |
| Storage Resources   | Sampled 24 hours a day, averaged    | Every day        |
| Data Transmission   | Metered by actual traffic generated | Every hour       |

This mode is primarily deducted through balance top-up via the Lakehouse console. Due to different prices of resources on different cloud platforms and in different regions, the unit prices of computing, storage, and data transmission may vary. Please refer to the pricing tables below for prices; the actual bill within the system shall prevail. You can view resource usage and cost details on the "Management Center" - "Billing Statement" page.

### 2. Annual Prepaid

Singdata Lakehouse can also provide enterprise customers with specified resource specifications and annual prepaid billing methods. When using annual prepaid, the unit prices of computing and storage resources can offer corresponding discounts. For details, please contact Singdata sales personnel.

## Billing Principles

### 1. Computing Resource Billing

The billing items for [computing resources](https://www.singdata.com/documents/virtual-cluster) include: general-purpose computing clusters, analytical computing clusters, synchronous computing clusters, task scheduling, and serverless jobs. The billing cycle for computing resources **is measured in hours**.

The billing principles for each computing resource item are as follows:

#### General-purpose Computing Clusters

When a general-purpose computing cluster starts and reaches the "running" state, it begins to generate corresponding CRU consumption based on the cluster's specification size and number of instances. When the computing cluster enters the "stopping" state, it stops generating CRU consumption.

> 🗒️ **Billing Formula**:&#x20;
> General-purpose Computing Cluster = Runtime (hours) × Cluster Specification (CRU) × CRU Unit Price (RMB/CRU\*hour)

The minimum specification for general-purpose computing resources is 1 CRU, the maximum is 256 CRU, with a step size of 1 CRU. The table below shows the specifications and corresponding hourly CRU consumption:

| Cluster Specification | Hourly CRU Consumption (CRU\*hour) |
| --------------------- | ---------------------------------- |
| 1                     | 1                                  |
| 2                     | 2                                  |
| 3                     | 3                                  |
| 4                     | 4                                  |
| 5                     | 5                                  |
| ...                   | ...                                |
| 256                   | 256                                |

#### Analytical Computing Clusters

The billing principle of analytical computing clusters is the same as that of general-purpose computing clusters, measured from the start time of the "running" state until entering the "stopping" state.

Analytical computing clusters support automatic instance scaling on top of the specifications. When query concurrency exceeds the maximum concurrency that all current instances can handle, the system will automatically scale out instances. Each additional instance increases the consumption of a computing cluster of the same specification. When reducing one instance still meets the current concurrency, the system will automatically scale in and reduce analytical computing resource consumption. Analytical clusters have elastic scaling enabled by default upon creation, with a default minimum of 1 instance and maximum of 2 instances. You can also manually set the minimum and maximum instance values for auto-scaling, with up to 25 instances.

> 🗒️ **Billing Formula**:&#x20;
> Analytical Computing Cluster = Runtime (hours) × Number of Instances × Cluster Specification (CRU) × CRU Unit Price (RMB/CRU\*hour)

The minimum specification for analytical computing resources is 1 CRU, the maximum is 256 CRU, with a step size of 2^n CRU. The table below shows the hourly CRU consumption for 1 to 5 instances:

| Cluster Specification | 1 Instance Hourly Consumption | 2 Instances Hourly Consumption | 3 Instances Hourly Consumption | 4 Instances Hourly Consumption | 5 Instances Hourly Consumption |
| --------------------- | ----------------------------- | ------------------------------ | ------------------------------ | ------------------------------ | ------------------------------ |
| 1                     | 1 CRU\*hour                   | 2 CRU\*hour                    | 3 CRU\*hour                    | 4 CRU\*hour                    | 5 CRU\*hour                    |
| 2                     | 2 CRU\*hour                   | 4 CRU\*hour                    | 6 CRU\*hour                    | 8 CRU\*hour                    | 10 CRU\*hour                   |
| 4                     | 4 CRU\*hour                   | 8 CRU\*hour                    | 12 CRU\*hour                   | 16 CRU\*hour                   | 20 CRU\*hour                   |
| 8                     | 8 CRU\*hour                   | 16 CRU\*hour                   | 24 CRU\*hour                   | 32 CRU\*hour                   | 40 CRU\*hour                   |
| 16                    | 16 CRU\*hour                  | 32 CRU\*hour                   | 48 CRU\*hour                   | 64 CRU\*hour                   | 80 CRU\*hour                   |
| 32                    | 32 CRU\*hour                  | 64 CRU\*hour                   | 96 CRU\*hour                   | 128 CRU\*hour                  | 160 CRU\*hour                  |
| 64                    | 64 CRU\*hour                  | 128 CRU\*hour                  | 192 CRU\*hour                  | 256 CRU\*hour                  | 320 CRU\*hour                  |
| 128                   | 128 CRU\*hour                 | 256 CRU\*hour                  | 384 CRU\*hour                  | 512 CRU\*hour                  | 640 CRU\*hour                  |
| 256                   | 256 CRU\*hour                 | 512 CRU\*hour                  | 768 CRU\*hour                  | 1024 CRU\*hour                 | 1280 CRU\*hour                 |

#### Synchronous Computing Clusters

Synchronous computing clusters are used for running data integration tasks, including offline integration and real-time integration. Multiple integration tasks can be submitted to the same synchronous computing cluster to reuse resources. The billing principle of synchronous computing clusters is the same as that of general-purpose computing clusters, measured from the start time of the "running" state until entering the "stopping" state.

> 🗒️ **Billing Formula**:&#x20;
> Synchronous Computing Cluster = Runtime (hours) × Cluster Specification (CRU) × CRU Unit Price (RMB/CRU\*hour)

Note: **The synchronous computing cluster is currently in trial operation**.During this period, to help you manage and account for offline and real-time business costs more precisely, the system will record billing details separately under the "Offline Integration" and "Real-time Integration" billing items on a per-job basis according to actual resource consumption. The CRU\*hour unit price remains unchanged under this billing model. When creating a synchronous cluster, you can use the "[Specification Estimation](https://www.singdata.com/documents/virtual-cluster)" feature to help determine the appropriate size.

Offline integration tasks can automatically wake up the synchronous computing cluster and automatically stop it after the task is completed; real-time integration tasks require their synchronous computing cluster to remain in the "running" state.

> 🗒️ **Billing Formulas during Trial Operation**:&#x20;
> Offline Integration = Runtime (hours) × CRU consumed by offline integration (CRU) × CRU Unit Price (RMB/CRU\*hour)
>
> Real-time Integration = Runtime (hours) × CRU consumed by real-time integration (CRU) × CRU Unit Price (RMB/CRU\*hour)

After the trial operation ends, data integration fees will be merged into the "Synchronous Computing Cluster" billing item. When the new billing model changes, we will notify you one month in advance to ensure you have sufficient time for business evaluation.

After official operation, the synchronous computing cluster will have specification restrictions: minimum specification of 0.25 CRU, maximum of 256 CRU, with no fixed step size restriction and support for any specification value. The hourly CRU consumption equals the cluster specification, for example:

| Cluster Specification | Hourly CRU Consumption |
| --------------------- | ---------------------- |
| 0.25                  | 0.25 CRU\*hour         |
| 0.26                  | 0.26 CRU\*hour         |
| 0.27                  | 0.27 CRU\*hour         |
| ...                   | ...                    |
| 256                   | 256 CRU\*hour          |

#### Task Scheduling

Task scheduling billing mainly covers two types of scenarios: one is the scheduling computing resource consumption generated when Python, Shell, and other script tasks are executed; the other is the small amount of computing resource consumption generated during the job submission and scheduling management process of offline and real-time integration tasks.

Task scheduling has no fixed minimum specification or step size restrictions. In all scenarios, the actual resource consumption from task scheduling will generate billing in CRU\*hour units.

For Python, Shell, and other script tasks, the system will meter based on the computing resources allocated to the task and the actual runtime. The metering period starts when the task execution begins and ends when the task execution completes.

For offline integration tasks, Singdata Lakehouse provides a small amount of computing resources for job submission and scheduling management. These resources begin metering after the offline integration task starts, do not consume during queue waiting, and persist throughout task execution.

For real-time integration tasks, Singdata Lakehouse similarly provides a small amount of computing resources for job submission and scheduling management. These resources begin metering after the real-time integration task starts and end after the task is officially running. Computing resource consumption during this period will be metered.

> 🗒️ **Billing Formula**:&#x20;
> Task Scheduling = Runtime (hours) × Cluster Specification (CRU) × CRU Unit Price (RMB/CRU\*hour)

#### Serverless Jobs

Serverless jobs refer to jobs that do not require users to actively create computing cluster instances, but are handled by the public computing resources provided by Singdata Lakehouse. This includes query job scheduling, data compression, automatic materialized views, etc.

The current CRU\*hour unit price for serverless jobs is the same as that of general-purpose computing clusters.

> 🗒️ **Billing Formula**:&#x20;
> Serverless Jobs = Runtime (hours) × Cluster Specification (CRU) × CRU Unit Price (RMB/CRU\*hour)

### 2. Storage Capacity Billing

Storage fees are calculated based on the actual storage capacity you use on the Lakehouse platform. The billing cycle for storage **is measured in days**.

When you write data into the Lakehouse data warehouse, the written data and some of its metadata information will occupy storage capacity in Lakehouse. Lakehouse measures your actual data storage usage by sampling multiple times within a day and **uses the average value of the sampled storage capacity** as the storage capacity measurement value for that day for billing.

When you use the [Time Travel ](https://www.singdata.com/documents/timetravel-summary)feature of Lakehouse, to ensure data multi-version and recoverability, Lakehouse will automatically back up your data in multiple versions. The multi-version backup data generated will incur corresponding storage fees, charged at the storage capacity unit price.

When you perform SQL queries, to reduce the consumption of computing resources for repeated queries, the query results will be cached, exchanging storage costs for computing resource savings. This part of the storage usage will be included in "[Result Cache](https://www.singdata.com/documents/result_cache)" and charged at the storage capacity unit price.

**Time Travel and Result Cache are currently free of charge**. You will be notified one month in advance when the billing status changes.

> 🗒️ **Billing Formula**:&#x20;
> Storage = Storage Duration (days) / 30 (days) × Daily Average Storage (GiB) × Storage Unit Price (RMB/GiB/month)

### 3. Data Transmission Billing

When you use Lakehouse as a data source for outbound network data transmission, such as downloading or exporting data through the public network, data transmission fees will be incurred. Data transmission is metered based on the actual amount of data transferred, with a billing cycle **measured in hours**.

When you use other data sources to transfer data into Lakehouse through the Internet, the network transfer traffic used will not incur fees.

When you use dedicated lines, Private Link, or other network products to achieve cross-cloud vendor, cross-region, or cross-VPC network connectivity, the network connectivity itself will incur data transmission fees. These fees may be charged by multiple parties due to different network connectivity methods. Data transmission fees generated on the Singdata Lakehouse side are charged by Singdata, while data transmission fees generated in your cloud platform account are charged directly by the cloud platform.

> 🗒️ **Billing Formula**:&#x20;
> Data Transmission = Data Transfer Volume (GB) × Data Transmission Unit Price (RMB/GB)

### 4. Other Cloud Resource Billing

When Singdata Lakehouse performs metadata management, parses SQL statements, generates query plans, schedules and allocates query tasks, and merges and cleans data files, it will consume cloud resources. Lakehouse will meter the consumption of these cloud resources, which are currently free for a limited time. You will be notified one month in advance when the billing status changes.

## Pricing

### 1. CRU Hour Price

**Standard Edition**：

| Cloud Provider | Region    | Version          | Unit Price          |
| -------------- | --------- | ---------------- | ------------------- |
| Alibaba Cloud  | Shanghai  | Standard Edition | 3.5 RMB/CRU\* hour  |
|                | Beijing   | Standard Edition | 3.5 RMB/CRU\* hour  |
|                | Hangzhou  | Standard Edition | 3.5 RMB/CRU\* hour  |
|                | Singapore | Standard Edition | 0.8 USD/CRU\* hour  |
| Tencent Cloud  | Beijing   | Standard Edition | 3.5 RMB/CRU\* hour  |
|                | Shanghai  | Standard Edition | 3.5 RMB/CRU\* hour  |
|                | Guangzhou | Standard Edition | 3.5 RMB/CRU\* hour  |
| AWS            | Beijing   | Standard Edition | 9.95 RMB/CRU\* hour |
|                | Singapore | Standard Edition | 1.24 USD/CRU\* hour |

**Enterprise Edition**：

| Cloud Provider | Region    | Version            | Unit Price          |
| -------------- | --------- | ------------------ | ------------------- |
| Alibaba Cloud  | Shanghai  | Enterprise Edition | 5.25 RMB/CRU\* hour |
|                | Beijing   | Enterprise Edition | 5.25 RMB/CRU\* hour |
|                | Hangzhou  | Enterprise Edition | 5.25 RMB/CRU\* hour |
|                | Singapore | Enterprise Edition | 1.2 USD/CRU\* hour  |
| Tencent Cloud  | Beijing   | Enterprise Edition | 5.25 RMB/CRU\* hour |
|                | Shanghai  | Enterprise Edition | 5.25 RMB/CRU\* hour |
|                | Guangzhou | Enterprise Edition | 5.25 RMB/CRU\* hour |
| AWS            | Beijing   | Enterprise Edition | 15 RMB/CRU\* hour   |
|                | Singapore | Enterprise Edition | 1.86 USD/CRU\* hour |

Note: In addition to the Standard Edition, the platform also offers an Enterprise Edition with enhanced data governance and security capabilities. The CRU hour unit price for the Enterprise Edition is higher than that of the Standard Edition. For a detailed comparison of features between the two editions, please refer to the product documentation at [Editions Overview](EditionsOverview.md).

### 2.Storage Capacity Price

| Cloud Provider | Region    | Version                               | Storage Capacity Price |
| -------------- | --------- | ------------------------------------- | ---------------------- |
| Alibaba Cloud  | Shanghai  | Enterprise Edition & Standard Edition | 0.12 RMB/GiB/month     |
|                | Singapore | Enterprise Edition & Standard Edition | 0.017 USD/GiB/month    |
| Tencent Cloud  | Beijing   | Enterprise Edition & Standard Edition | 0.12 RMB/GiB/month     |
|                | Shanghai  | Enterprise Edition & Standard Edition | 0.12 RMB/GiB/month     |
|                | Guangzhou | Enterprise Edition & Standard Edition | 0.12 RMB/GiB/month     |
| AWS            | Beijing   | Enterprise Edition & Standard Edition | 0.195 RMB/GiB/month    |
|                | Singapore | Enterprise Edition & Standard Edition | 0.025 USD/GiB/month    |

Note: Since the billing cycle for storage is measured in days, the monthly unit price shown above is prorated on a 30-day basis for daily deductions.

### 3. Data Transmission Pricing

| Cloud Provider | Region    | Edition                               | Internet Data Transfer Price |
| -------------- | --------- | ------------------------------------- | ---------------------------- |
| Alibaba Cloud  | Shanghai  | Enterprise Edition & Standard Edition | 0.8 RMB/GB                   |
|                | Singapore | Enterprise Edition & Standard Edition | 0.081 USD/GB                 |
| Tencent Cloud  | Beijing   | Enterprise Edition & Standard Edition | 0.8 RMB/GB                   |
|                | Shanghai  | Enterprise Edition & Standard Edition | 0.8 RMB/GB                   |
|                | Guangzhou | Enterprise Edition & Standard Edition | 0.8 RMB/GB                   |
| AWS            | Beijing   | Enterprise Edition & Standard Edition | 0.933 RMB/GB                 |
|                | Singapore | Enterprise Edition & Standard Edition | 0.12 USD/GB                  |

## Cost Examples in Common Scenarios

### General-purpose Computing Cluster Cost Example

Taking an AWS Singapore Standard Edition service instance in SaaS mode as an example:

* A general-purpose computing cluster with a specification of 2 CRU, running for 1 hour, with a unit price of 1.24 USD per CRU\*hour, the cost is:

  * 1 hour × 2 CRU × 1.24 USD/CRU\*hour = **2.48 USD**
* A general-purpose computing cluster with a specification of 1 CRU, running for 1 minute and 20 seconds (approximately 1.33 minutes), with a unit price of 1.24 USD per CRU\*hour, the cost is:

  * 1.33/60 minutes × 1 CRU × 1.24 USD/CRU\*hour = **0.027 USD**
* A general-purpose computing cluster with a specification of 1 CRU running from 10:00-10:02 for 2 minutes, and another general-purpose computing cluster with a specification of 2 CRU running from 10:00-10:10 for 10 minutes, with a unit price of 1.24 USD per CRU\*hour, the cost is:

  * (2/60 minutes × 1 CRU × 1.24 USD/CRU\*hour) + (10/60 minutes × 2 CRU × 1.24 USD/CRU\*hour) = 0.041 USD + 0.413 USD = **0.455 USD**

### Analytical Computing Cluster Cost Example

Taking an AWS Singapore Standard Edition service instance in SaaS mode as an example:

* An analytical cluster with a specification of 1 CRU, running for 30 minutes with 1 instance, and then running for 30 minutes with 2 instances, with a unit price of 1.24 USD per CRU\*hour, the cost is:
  * (30/60 minutes × 1 instance × 1 CRU × 1.24 USD/CRU\*hour) + (30/60 minutes × 2 instances × 1 CRU × 1.24 USD/CRU\*hour) = 0.62 USD + 1.24 USD = **1.86 USD**

### Offline Integration Task Cost Example

During the current trial operation period, offline integration tasks are not charged separately; only the running costs of the synchronous computing cluster to which the tasks are submitted are charged. Offline integration tasks can automatically wake up the synchronous computing cluster.

An offline integration task requires computing resources for scheduling and concurrent execution. A single offline task typically requires at least approximately 0.05 CRU of scheduling resources, with a total consumption of at least approximately 0.1 CRU (0.05 CRU + 1 × 0.05 CRU). Based on this estimate, 5 single-concurrent offline integration tasks can fully utilize a synchronous computing cluster with a specification of 0.5 CRU.

> 🗒️ **Estimation Formula**:&#x20;
> Offline Integration Task Resource Consumption ≈ Scheduling Resource Specification (CRU) + Concurrency × Scheduling Resource Specification (CRU)

Taking an AWS Singapore Standard Edition service instance in SaaS mode as an example:

* A single-concurrent offline integration task running for 10 minutes, with actual hourly computing resource consumption of 0.1 CRU, and a unit price of 1.24 USD per CRU\*hour, the cost is:

  * 10/60 minutes × 0.1 CRU × 1.24 USD/CRU\*hour = **0.021 USD**
* A single-concurrent offline integration task running from 10:00-10:10 for 10 minutes with actual hourly consumption of 0.1 CRU, and another 5-concurrent offline integration task running from 10:05-10:25 for 20 minutes with actual hourly consumption of 0.3 CRU, with a unit price of 1.24 USD per CRU\*hour, the cost is:

  * (5/60 minutes × 0.1 CRU × 1.24 USD/CRU\*hour) + (5/60 minutes × 0.4 CRU × 1.24 USD/CRU\*hour) + (15/60 minutes × 0.3 CRU × 1.24 USD/CRU\*hour) = 0.010 USD + 0.041 USD + 0.093 USD = **0.145 USD**

### Real-time Integration Task Cost Example

During the trial operation period, in addition to offline integration tasks, the computing resource consumption of real-time integration tasks in the synchronous computing cluster is also metered separately.

Unlike offline integration tasks, real-time integration tasks run continuously after startup and perform real-time data caching and state management in memory. Therefore, the execution resource consumption of real-time tasks does not have a simple linear relationship with concurrency, but mainly depends on the complexity of data processing and the required state cache size. A single-concurrent real-time integration task will incur at least approximately 0.05 CRU of scheduling resource consumption and approximately 0.0625 CRU of execution consumption, totaling at least approximately 0.1125 CRU per hour.

Taking an AWS Singapore Standard Edition service instance in SaaS mode as an example:

* A single-concurrent real-time integration task running for 24 hours, with actual hourly resource consumption of 0.1125 CRU, requiring a minimum cluster specification of 0.25 CRU, and a unit price of 1.24 USD per CRU\*hour, the cost is:
  * 24 hours × 0.1125 CRU × 1.24 USD/CRU\*hour = **3.348 USD**
* A multi-concurrent real-time integration task consuming 1 CRU per hour running from January 1-5 for 5 days, and another multi-concurrent real-time integration task consuming 2 CRU per hour running from January 3-10 for 8 days, with a unit price of 1.24 USD per CRU\*hour, the cost is:
  * (2 × 24 hours × 1 CRU × 1.24 USD/CRU\*hour) + (3 × 24 hours × 3 CRU × 1.24 USD/CRU\*hour) + (5 × 24 hours × 2 CRU × 1.24 USD/CRU\*hour) = 59.52 USD + 267.84 USD + 297.60 USD = **624.96 USD**

### Synchronous Computing Cluster Cost Example

After the trial operation ends, synchronous computing clusters will be billed according to this standard.

Taking an AWS Singapore Standard Edition service instance in SaaS mode as an example:

* A synchronous cluster with a specification of 2 CRU, running for 1 hour, with a unit price of 1.24 USD per CRU\*hour, the cost is:

  * 1 hour × 2 CRU × 1.24 USD/CRU\*hour = **2.48 USD**
* A real-time integration task consuming 0.2 CRU per hour running from January 1-5 for 5 days, with an additional offline integration task consuming 0.1 CRU running for 1 hour on January 2 from 0:00-1:00, with a unit price of 1.24 USD per CRU\*hour, the cost is:

  * "**Fixed" mode** total cost: 5 × 24 hours × 0.5 CRU × 1.24 USD/CRU\*hour = **74.40 USD**
  * "**Elastic Scaling" mode** total cost: (1 × 24 hours × 0.25 CRU × 1.24 USD/CRU\*hour) + (1 hour × 0.5 CRU × 1.24 USD/CRU\*hour) + ((23 + 3×24) hours × 0.25 CRU × 1.24 USD/CRU\*hour) = 7.44 USD + 0.62 USD + 29.45 USD = **37.51 USD**

As shown in the examples above, to better save synchronous computing resource costs, it is recommended to reuse synchronous computing cluster resources as much as possible and avoid using overly large specifications.

### Task Scheduling - Python Script Task Cost Example

When executing Python script tasks, the cost is calculated based on the task execution time and the computing resources consumed. Generally, when a Python script runs for 1 hour, the computing resources used are 0.125 CRU.

Taking an AWS Singapore Standard Edition service instance in SaaS mode as an example:

* A Python script task with an execution time of 10 minutes, with a unit price of 1.24 USD per CRU\*hour, the cost is:
  * 10/60 minutes × 0.125 CRU × 1.24 USD/CRU\*hour = **0.026 USD**

### Storage Capacity Cost Example

Taking an AWS Singapore Standard Edition service instance in SaaS mode as an example:

* A workspace with a daily storage capacity low point of 910 GiB, high point of 1100 GiB, and daily average of 1000 GiB, with a monthly storage unit price of 0.025 USD/GiB/month (calculated on a 30-day basis), the storage cost for that day is:
  * 1/30 month × 1000 GiB × 0.025 USD/GiB/month = **0.833 USD**

### Data Transmission Cost Example

Taking an AWS Singapore Standard Edition service instance in SaaS mode as an example:

* A task generating 10 GB of outbound network data transmission traffic, with a data transmission unit price of 0.12 USD/GB, the data transmission cost is:
  * 10 GB × 0.12 USD/GB = **1.20 USD**

^
