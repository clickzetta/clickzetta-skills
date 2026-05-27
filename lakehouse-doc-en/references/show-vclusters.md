## Overview

This command queries detailed information about all compute clusters in the current workspace.

## Syntax

```SQL
SHOW VCLUSTERS [LIKE PATTERN | WHERE expr] [LIMIT num]
```

## Parameters

1. `LIKE PATTERN` (optional): Filters by object name. SQL wildcards `%` and `_` can be used. For example, `LIKE '%testing%'`. Note that the `LIKE` clause cannot be used together with the `WHERE` clause.

2. `WHERE expr` (optional): Filters compute clusters by specific attributes. The following attributes are supported:

- `vcluster_size`: Compute cluster specification code, such as `XSMALL`, `SMALL`, etc., using uppercase letters.
- `vcluster_type`: Compute cluster type, such as `ANALYTICS`, `GENERAL`, using uppercase letters.
- `max_concurrency`: Filter by concurrency level, enter a number.
- `state`: Compute cluster state, such as `RESUMING`, `SUSPENDED`, etc., using uppercase letters.
- `creator`: Username of the compute cluster creator, using lowercase letters.
- `create_time`: Creation time, format: `"yyyy-MM-dd HH:mm:ss"`, stored as a string, supports comparison operators.
- `min_replicas`: Minimum number of compute instances, enter a number.
- `max_replicas`: Maximum number of compute instances, enter a number.
- `preload_tables`: List of table names in cache, stored as a string. You can use the `LIKE` clause to match specific table names.
- `current_replicas`: Current number of compute instances in the cluster, enter a number.
- `auto_suspend_in_second`: Number of seconds before the compute cluster auto-suspends, enter a number.

## Examples

1. Query all compute clusters in the current workspace:

   ```SQL
   SHOW VCLUSTERS;
   ```

2. Query compute clusters whose names start with "CZ":

   ```SQL
   SHOW VCLUSTERS LIKE 'CZ%';
   ```

3. Use the WHERE clause to filter compute cluster result lists:

   ```SQL
   SHOW VCLUSTERS WHERE vcluster_type = 'GENERAL';
   SHOW VCLUSTERS WHERE vcluster_size = 'SMALL';
   SHOW VCLUSTERS WHERE max_concurrency = 8;
   SHOW VCLUSTERS WHERE state = 'SUSPENDED';
   SHOW VCLUSTERS WHERE creator = 'demo_project';
   SHOW VCLUSTERS WHERE create_time > '2024-01-25';
   SHOW VCLUSTERS WHERE min_replicas = 1;
   SHOW VCLUSTERS WHERE max_replicas = 2;
   SHOW VCLUSTERS WHERE preload_tables LIKE '%sample_schema.sample_table%';
   SHOW VCLUSTERS WHERE current_replicas = 3;
   SHOW VCLUSTERS WHERE auto_suspend_in_second = 600;
   ```

With the examples above, you can flexibly query and filter compute cluster information as needed. Ensure you use the correct case and operators in the `WHERE` clause to obtain accurate query results.
