# Drop Virtual Cluster (DROP VCLUSTER)

## Overview

The `DROP VCLUSTER` command deletes a specified compute cluster (Virtual Cluster). Once a compute cluster is deleted, it cannot be recovered. Proceed with caution.

## Syntax

```Plain
DROP VCLUSTER [ IF EXISTS ] <vc_name> [ FORCE ]
```

## Parameters

| Parameter | Required | Description |
|---|---|---|
| `IF EXISTS` | No | If the specified compute cluster does not exist, the system will not report an error and will silently skip |
| `vc_name` | Yes | Name of the compute cluster to delete |
| `FORCE` | No | Force immediate deletion of the compute cluster without waiting for currently executing jobs to complete. Without this keyword, the system waits for all running jobs to finish before deleting |

## Examples

### Example 1: Delete a compute cluster

```SQL
DROP VCLUSTER sample_vc;
```

### Example 2: Safe deletion (no error if cluster does not exist)

```SQL
DROP VCLUSTER IF EXISTS test_vc;
```

### Example 3: Force deletion (immediately terminate running jobs)

```SQL
DROP VCLUSTER sample_vc FORCE;
```

### Example 4: Safe force deletion

```SQL
DROP VCLUSTER IF EXISTS production_vc FORCE;
```

## Notes

- **Irreversible**: A deleted compute cluster cannot be recovered via `UNDROP`. Confirm the operation before deletion.

- **Running jobs**:
  - Without `FORCE`, the system waits for currently executing jobs to finish before deleting the cluster and will not interrupt running jobs.
  - With `FORCE`, the cluster is deleted immediately and running jobs will be forcibly terminated, which may cause job failures or data inconsistency.

- **Dependency Check**: Before deletion, confirm that no dynamic tables, scheduled tasks, or other objects are bound to this compute cluster; otherwise, automatic refresh of related objects will fail.

- **Required Privileges**: Executing `DROP VCLUSTER` requires management privileges on the corresponding compute cluster.

## Related Commands

- [CREATE VCLUSTER](getting_started_with_vcluster_for_processing_analytics.md): Create a compute cluster
- [ALTER VCLUSTER](alter-vcluster.md): Modify compute cluster configuration
- [SHOW VCLUSTERS](show-vclusters.md): View all compute clusters
