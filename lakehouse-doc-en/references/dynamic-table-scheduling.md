# Dynamic Table Scheduling and Deployment Specification

## Scheduling Method Selection

For production environments, prioritize using Studio Task to schedule REFRESH:
- Can orchestrate dependencies with upstream and downstream tasks
- Unified monitoring and alerting
- Flexible control over refresh timing and retry strategies

## Scheduling Configuration Requirements

### Self-Dependency (Required)

- Tasks must configure self-dependency to ensure only one REFRESH instance runs at a time
- Avoid write conflicts or data inconsistency caused by concurrent REFRESH

### Upstream Dependencies

- If the source table data needs to be synchronized and ready before refresh, the DT's REFRESH Task should depend on the source table's output task
- If source table data does not require synchronization, upstream dependencies may be omitted

## Task Content

### Non-Partitioned DT

```sql
REFRESH DYNAMIC TABLE schema.dt_name;
```

### Partitioned DT (with Parameters)

```sql
SET dt.args.pt = '2024-11-13';
REFRESH DYNAMIC TABLE schema.dt_name PARTITION (pt = '2024-11-13');
```

The value of `dt.args.pt` is replaced by the Studio scheduling engine with the specific business date at each execution.

## Notes

- REFRESH for different partitions can execute in parallel (assigned to different Tasks or different instances of the same Task)
- Concurrent REFRESH of the same partition or non-partitioned DT is prohibited
