# Compute Cluster Management

## Overview

This feature allows users to start, stop, cancel jobs, modify property configurations, and update cluster descriptions for a specified compute cluster. With these operations, users can flexibly manage compute resources to meet various business needs.

## Syntax

```SQL
-- Start a compute cluster
ALTER VCLUSTER [IF EXISTS] name RESUME;

-- Stop a compute cluster
ALTER VCLUSTER [IF EXISTS] name SUSPEND [FORCE];

-- Cancel all jobs in a compute cluster
ALTER VCLUSTER [IF EXISTS] name CANCEL ALL JOBS;

-- Modify compute cluster properties
ALTER VCLUSTER [IF EXISTS] name SET objectProperties;

-- Modify compute cluster description
ALTER VCLUSTER [IF EXISTS] name SET COMMENT '';
```

### Object Properties Description

```Plain
-- Modify properties applicable to Analytics Purpose Virtual Cluster
objectProperties ::=
    VCLUSTER_SIZE = num
    MIN_REPLICAS = num
    MAX_REPLICAS = num
    AUTO_SUSPEND_IN_SECOND = num
    AUTO_RESUME = TRUE | FALSE
    MAX_CONCURRENCY = num
    QUERY_RUNTIME_LIMIT_IN_SECOND = num
    PRELOAD_TABLES = "<schema_name>.<table_name>[,<schema_name>.<table_name>,...]"

-- Modify properties applicable to General Purpose Virtual Cluster
objectProperties ::=
    VCLUSTER_SIZE = num | MIN_VCLUSTER_SIZE = num MAX_VCLUSTER_SIZE = num
    AUTO_SUSPEND_IN_SECOND = num
    AUTO_RESUME = TRUE | FALSE
    QUERY_RUNTIME_LIMIT_IN_SECOND = num
    QUERY_RESOURCE_LIMIT_RATIO = num

-- Modify properties applicable to Integration Virtual Cluster
objectProperties ::=
    VCLUSTER_SIZE = num | MIN_VCLUSTER_SIZE = num MAX_VCLUSTER_SIZE = num
    AUTO_SUSPEND_IN_SECOND = num
    AUTO_RESUME = TRUE | FALSE
    QUERY_RUNTIME_LIMIT_IN_SECOND = num
```

## Parameter Details

**1. name**

Specifies the name of the compute cluster.

**2. objectProperties**

Compute cluster property configuration. The specific fields and descriptions are as follows:

| Field Name | Description | Value Range | Default |
|----------|----------|----------|--------|
| `VCLUSTER_SIZE` | Virtual cluster size. General Purpose and Analytics virtual clusters support 1–256 CRU (Analytics sizes must be powers of 2); Integration virtual clusters support 0.05–256 CRU. | In CRU (Compute Resource Unit). Integration: 0.05–256, step 0.025; other types: 1–256. | At creation: Integration: 0.25; other types: 1 |
| `MIN_VCLUSTER_SIZE` | Applicable to General Purpose and Integration virtual clusters. Minimum specification when the compute cluster scales down; must be less than or equal to `MAX_VCLUSTER_SIZE`. Cannot be used together with `VCLUSTER_SIZE`. | General Purpose: 1–256; Integration: 0.05–256, step 0.025. In CRU. | None |
| `MAX_VCLUSTER_SIZE` | Applicable to General Purpose and Integration virtual clusters. Maximum specification when the compute cluster scales up; must be greater than or equal to `MIN_VCLUSTER_SIZE`. Cannot be used together with `VCLUSTER_SIZE`. | General Purpose: 1–256; Integration: 0.05–256, step 0.025. In CRU. | None |
| `MIN_REPLICAS` | Minimum number of compute cluster instances. Only applicable to Analytics Purpose clusters. | 1-10 | 1 |
| `MAX_REPLICAS` | Maximum number of compute cluster instances. Only applicable to Analytics Purpose clusters. | 1-10 | 1 |
| `AUTO_SUSPEND_IN_SECOND` | Idle duration before the cluster auto-suspends. Unit: seconds. -1 means never auto-suspend. | -1 or integer >= 0 | 600 |
| `AUTO_RESUME` | Whether to auto-resume. | `TRUE` \| `FALSE` | TRUE |
| `MAX_CONCURRENCY` | Maximum concurrency per compute instance. Only applicable to Analytics Purpose clusters. | 1-32 | 8 |
| `QUERY_RUNTIME_LIMIT_IN_SECOND` | Maximum duration a job submitted to this cluster can execute. Unit: seconds. | Integer > 0 | 86400 |
| `PRELOAD_TABLES` | Periodically or on-trigger pull specified table data into cluster local SSD cache. Only applicable to Analytics Purpose clusters. | `schema_name.table_name`, multiple table names separated by commas, supports wildcards | null |
| `QUERY_RESOURCE_LIMIT_RATIO` | Single job resource ratio threshold: the CPU/memory resources used by a single query task must not exceed the specified proportion of total cluster resources. | `0.0` ~ `1.0` | 1.0 |

> Note: The `VCLUSTER_SIZE` parameter supports both T-shirt size notation (XSMALL, SMALL, LARGE, etc.) and numeric notation (1, 2, 4, 16, etc.). For more information, see: [Compute Cluster Specification Code Change Notes](vcluster_size_description.md)

**3. Modifying the Scaling Range of General Purpose Clusters**

```SQL
ALTER VCLUSTER [IF EXISTS] <name>
SET MIN_VCLUSTER_SIZE = num
    MAX_VCLUSTER_SIZE = num;
```

`VCLUSTER_SIZE`, `MIN_VCLUSTER_SIZE`, and `MAX_VCLUSTER_SIZE` cannot be set simultaneously.

## Examples

1. Start the compute cluster named `sample_vc`:

   ```SQL
   ALTER VCLUSTER sample_vc RESUME;
   ```

2. Stop the compute cluster named `sample_vc`:

   ```SQL
   ALTER VCLUSTER sample_vc SUSPEND;
   ```

3. Force stop the compute cluster named `sample_vc` (immediately terminate all running jobs):

   ```SQL
   ALTER VCLUSTER sample_vc SUSPEND FORCE;
   ```

4. Cancel all jobs in the compute cluster named `sample_vc`:

   ```SQL
   ALTER VCLUSTER sample_vc CANCEL ALL JOBS;
   ```

5. Change the compute cluster named `sample_vc` specification to XSMALL (1 CRU):

   ```SQL
   ALTER VCLUSTER sample_vc SET VCLUSTER_SIZE = 1;
   ```

6. Change the maximum concurrency of the compute cluster named `sample_vc` to 4:

   ```SQL
   ALTER VCLUSTER sample_vc SET MAX_CONCURRENCY = 4;
   ```

7. Modify the scaling range of the General Purpose cluster `sample_vc` (minimum 1 CRU, maximum 4 CRU):

   ```SQL
   ALTER VCLUSTER sample_vc SET MIN_VCLUSTER_SIZE = 1 MAX_VCLUSTER_SIZE = 4;
   ```

8. Modify the cluster auto-suspend time to 300 seconds:

   ```SQL
   ALTER VCLUSTER sample_vc SET AUTO_SUSPEND_IN_SECOND = 300;
   ```

9. Disable cluster auto-suspend (never auto-suspend):

   ```SQL
   ALTER VCLUSTER sample_vc SET AUTO_SUSPEND_IN_SECOND = -1;
   ```

10. Modify the description of the compute cluster named `sample_vc`:

    ```SQL
    ALTER VCLUSTER sample_vc SET COMMENT 'This is a sample compute cluster';
    ```

^
