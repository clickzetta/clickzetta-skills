# Create Virtual Cluster

## Description

This feature allows users to create a virtual cluster in the SQL workspace based on the specified name and configuration. The virtual cluster (abbreviated as: VCluster) is a compute resource cluster service provided by Singdata Lakehouse, offering resources such as CPU, memory, and temporary storage required for executing query analysis. Users can use the virtual cluster to perform various ETL, streaming analysis, ad-hoc queries, and data integration tasks. When executing SQL Select queries or various DML operations (such as DELETE, INSERT, UPDATE, etc.) that require computation in Lakehouse, the irtual cluster will be used.

The virtual cluster includes three types: General Purpose Virtual Cluster (abbreviated as: GP type), Analytics Purpose Virtual Cluster (abbreviated as: AP type), and Integration Virtual Cluster.

In the General Purpose virtual cluster, jobs submitted to the virtual cluster share the cluster's computing resources, suitable for handling offline jobs; the Analytics Purpose cluster has features such as multiple virtual cluster instances and automatic scaling, suitable for handling online, high-concurrency jobs. The Integration cluster is specifically used for data integration tasks.

## Syntax

```SQL
-- CREATE VCLUSTER
CREATE VCLUSTER [IF NOT EXISTS] <name>
objectProperties
[COMMENT '']

-- Parameter Description
-- Applicable attributes for creating an Analytics-Purpose Virtual Cluster      
objectProperties ::=
            VCLUSTER_SIZE = num --integer from 1 to 256
            VCLUSTER_TYPE = ANALYTICS
            MIN_REPLICAS = num
            MAX_REPLICAS = num
            AUTO_SUSPEND_IN_SECOND = num
            AUTO_RESUME = TRUE| FALSE
            MAX_CONCURRENCY = num
            QUERY_RUNTIME_LIMIT_IN_SECOND = num
            PRELOAD_TABLES = "<schema_name>.<table_name>[,<schema_name>.<table_name>,...]"
            AUTO_PRELOAD_IN_SECOND = num
            
-- Applicable attributes for creating a General-Purpose Virtual Cluster             
objectProperties ::=
            [VCLUSTER_SIZE = num | MIN_VCLUSTER_SIZE=num  MAX_VCLUSTER_SIZE=num] --integer from 1 to 256
            VCLUSTER_TYPE = GENERAL 
            AUTO_SUSPEND_IN_SECOND = num
            AUTO_RESUME = TRUE| FALSE
            QUERY_RUNTIME_LIMIT_IN_SECOND = num
            QUERY_RESOURCE_LIMIT_RATIO=num;

-- Applicable attributes for creating an Integration Virtual Cluster            
objectProperties ::=
            [VCLUSTER_SIZE = num | MIN_VCLUSTER_SIZE=num  MAX_VCLUSTER_SIZE=num] --integer from 1 to 256
            VCLUSTER_TYPE = INTEGRATION 
            AUTO_SUSPEND_IN_SECOND = num
            AUTO_RESUME = TRUE| FALSE
            QUERY_RUNTIME_LIMIT_IN_SECOND = num;
```

**1 .name**: The name of the virtual cluster. It must be unique within the workspace and cannot be changed once created. Naming rules: 3 to 28 characters, only letters, underscores, and decimal numbers (0-9) are supported, and spaces are not allowed.

**2. objectProperties**: The properties that can be specified when creating a virtual cluster, along with their specific meanings and values, are as follows:

| Field Name                        | Field Meaning                                                                                                                                                                                                                                                                        | Value Range                                                                                                     | Default |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------- | ------- |
| VCLUSTER\_SIZE                    | Virtual cluster size. Supports sizes from 1 CRU to 256 CRU, with increasing computing power. (Synchronous clusters separately support two small sizes: 0.25 CRU and 0.5 CRU)                                                                                                         | Number: 1-256, unit is CRU (Compute Resource Unit).                                                             | 1       |
| MIN\_VCLUSTER\_SIZE               | Applicable only to GENERAL clusters.&#xA;The minimum size of the virtual cluster when scaling, supporting sizes from 1 CRU to 256 CRU, and must be less than or equal to the MAX\_VCLUSTER\_SIZE parameter. Cannot be used simultaneously with VCLUSTER\_SIZE.                       | Number: 1-256, unit is CRU (Compute Resource Unit).                                                             | None    |
| MAX\_VCLUSTER\_SIZE               | Applicable only to GENERAL clusters.&#xA;The maximum size of the virtual cluster when scaling, supporting sizes from 1 CRU to 256 CRU, and must be greater than or equal to the MIN\_VCLUSTER\_SIZE parameter. Cannot be used simultaneously with VCLUSTER\_SIZE.                    | Number: 1-256, unit is CRU (Compute Resource Unit).                                                             | None    |
| VCLUSTER\_TYPE                    | Virtual cluster type.&#xA;GENERAL: Suitable for data ingestion and ELT operations;&#xA;ANALYTICS: Suitable for scenarios with strong requirements for query latency and concurrency capabilities;&#xA;INTEGRATION: Used for data integration task scenarios.                         | GENERAL \| ANALYTICS \| INTEGRATION                                                                             | GENERAL |
| MIN\_REPLICAS                     | Minimum number of instances for the virtual cluster. Only applicable to analytics virtual cluster.                                                                                                                                                                                   | 1-10                                                                                                            | 1       |
| MAX\_REPLICAS                     | Maximum number of instances in the virtual cluster. Only applicable to analytics virtual clusters.                                                                                                                                                                                   | 1-10                                                                                                            | 1       |
| AUTO\_SUSPEND\_IN\_SECOND         | Idle time before the cluster automatically shuts down. Unit: seconds.                                                                                                                                                                                                                | Valid values: `-1` (never auto suspend) or integers `≥ 15`.            | 600     |
| AUTO\_RESUME                      | Whether to automatically resume.                                                                                                                                                                                                                                                     | TRUE｜FALSE                                                                                                      | TRUE    |
| MAX\_CONCURRENCY                  | Maximum concurrency load per vcluster instance in the virtual cluster. Only applicable to analytics virtual clusters.                                                                                                                                                                | 1-32                                                                                                            | 8       |
| QUERY\_RUNTIME\_LIMIT\_IN\_SECOND | Maximum execution time for jobs submitted to this virtual cluster. Unit: seconds.                                                                                                                                                                                                    | Integer greater than 0.                                                                                         | 86400   |
| PRELOAD\_TABLES                   | The virtual cluster can cache specified table data to the local SSD disk of the virtual cluster by configuring preload\_table, either on a schedule or triggered. You can also [set cache policies](create-table-ddl.md) on the table. Only applicable to analytics virtual cluster. | schema\_name.table\_name, multiple table names separated by commas. Supports wildcards, e.g., sample\_schema.\* | null    |
| QUERY\_RESOURCE\_LIMIT\_RATIO     | **Single Job Resource Ratio Threshold**, the maximum proportion of CPU/memory resources that a single query task can use, relative to the total cluster resources                                                                                                                    | `0.0` \~ `1.0` (e.g., `0.1` means 10%)                                                                          | 1.0     |

3. Specify the maximum and minimum values for GP type VC during creation

```SQL
CREATE VCLUSTER [IF NOT EXISTS] <name> 
VCLUSTER_TYPE=GENERAL 
MIN_VCLUSTER_SIZE=num 
MAX_VCLUSTER_SIZE=num;
```

* VCLUSTER\_SIZE, MIN\_VCLUSTER\_SIZE, and MAX\_VCLUSTER\_SIZE cannot be set simultaneously.

4. comment
   Specify the description information of the computing cluster, supporting up to 1024 characters.

## Usage Example

1. Create a computing cluster using default properties:
   ```SQL
   CREATE VCLUSTER sample_vc;
   ```

2. Specify the creation of a general-purpose computing cluster, XSMALL specification, auto-start, auto-stop time of 60 seconds, maximum job execution time of 600 seconds:

   ```SQL
   CREATE VCLUSTER demo_gp_vcluster 
   VCLUSTER_SIZE = 1 
   VCLUSTER_TYPE = GENERAL 
   AUTO_SUSPEND_IN_SECOND = 60 
   AUTO_RESUME = TRUE 
   QUERY_RUNTIME_LIMIT_IN_SECOND = 600;
   ```

Specify the creation of an analytical computing cluster, XSMALL specification, auto-start, auto-stop time of 1 minute, minimum instance count of 1, maximum instance count of 2, maximum concurrency per instance of 16, maximum job execution time of 600 seconds, pre-read data from public.demo and billing.payment tables, pull table data cache every 600 seconds:

```
CREATE VCLUSTER demo_ap_vcluster 
VCLUSTER_SIZE = 1
VCLUSTER_TYPE = ANALYTICS
MIN_REPLICAS = 1
MAX_REPLICAS = 2
MAX_CONCURRENCY = 16
AUTO_SUSPEND_IN_SECOND = 60 
AUTO_RESUME = TRUE 
QUERY_RUNTIME_LIMIT_IN_SECOND = 600
PRELOAD_TABLES = 'public.demo,billing.payment';
```

^
