# Studio Task Development and Operations

cz-cli can manage tasks in Singdata Studio, suitable for data development and daily operations.

## Creating a SQL Task

```bash
cz-cli -p prod task create daily_order_summary --type SQL --description "Daily order summary"
```

## Saving Task SQL

```bash
cz-cli -p prod task save-content daily_order_summary  --content "INSERT INTO public.order_summary SELECT current_date(), COUNT(*) FROM public.orders"
```

## Configuring a Schedule

The example below runs every day at 02:00:

```bash
cz-cli -p prod task save-cron daily_order_summary --cron "0 0 2 * * ? *"
```

## Deploying a Task

```bash
cz-cli -p prod task deploy daily_order_summary
```

## Manually Executing a Task

```bash
cz-cli -p prod task execute daily_order_summary --max-wait-seconds 300
```

## Viewing Run History and Logs

### View Recent Runs

```bash
cz-cli -p prod runs list --task daily_order_summary --limit 5
```

### View Run Details

```bash
cz-cli -p prod runs detail <run_id>
```

### View Run Logs

```bash
cz-cli -p prod runs logs <run_id>
```

### Wait for a Run to Complete

```bash
cz-cli -p prod runs wait <run_id>
```

***

## Advanced Task Operations (Full runs Commands)

`cz-cli runs` supports the following operations beyond the basic list / detail / logs / wait:

### Stop a Running Instance

```bash
cz-cli -p prod runs stop <run_id>
```

### Rerun a Failed Instance

```bash
cz-cli -p prod runs rerun <run_id>
```

### Backfill

Backfill scheduled instances for a task within a specified time range. **This is irreversible — confirm before executing**:

```bash
cz-cli -p prod runs refill <task_name> \
  --from "2026-05-01T00:00:00" \
  --to "2026-05-07T23:59:59" \
  --vc DEFAULT
```

Add `-y` to skip the confirmation prompt (for CI/CD scenarios):

```bash
cz-cli -p prod runs refill <task_name> --from ... --to ... -y
```

### View Run Dependencies

Default view shows 1 level upstream and 1 level downstream:

```bash
cz-cli -p prod runs deps <run_id>
```

Specify depth:

```bash
cz-cli -p prod runs deps <run_id> --parent-level 2 --child-level 2
```

### Run Statistics Summary

```bash
cz-cli -p prod runs stats --task <task_name> --from "2026-05-01" --to "2026-05-07"
```

***

## Runs vs Attempts

| Concept | Description |
| --- | --- |
| **run** | One scheduling trigger corresponds to one run with a unique run_id; a run may be automatically retried multiple times on failure |
| **attempt** | Each actual execution within a run corresponds to one attempt; if a run fails and retries 3 times, there are 3 attempts |

**Typical troubleshooting workflow**:

1. Find the failed run:

```bash
cz-cli -p prod runs list --task daily_order_summary --from "2026-05-26"
```

2. View run details (including all attempt summaries):

```bash
cz-cli -p prod runs detail <run_id>
```

3. View all attempts under the run:

```bash
cz-cli -p prod attempts list <run_id>
```

4. View detailed logs for a specific attempt:

```bash
cz-cli -p prod attempts log <attempt_id>
```

***

## Advanced Task Configuration (task save-config)

`task save-config` configures retry policies, dependencies, compute clusters, and timeouts. **It does not affect the configured cron schedule**:

```bash
cz-cli -p prod task save-config <task_name> \
  --retry-count 3 \
  --retry-interval 5 \
  --retry-unit m \
  --timeout 60 \
  --timeout-unit m \
  --vc DEFAULT
```

**Parameter reference**:

| Parameter | Description | Example |
| --- | --- | --- |
| `--retry-count` | Maximum retry count | `3` |
| `--retry-interval` | Retry interval value | `5` |
| `--retry-unit` | Retry interval unit (`m`=minutes, `s`=seconds) | `m` |
| `--timeout` | Execution timeout value | `60` |
| `--timeout-unit` | Timeout unit (`m`=minutes, `s`=seconds) | `m` |
| `--rerun-property` | Backfill policy: `1`=any time, `2`=failed only, `3`=not allowed | `2` |
| `--self-depends` | Self-dependency: `0`=off, `1`=on (next cycle triggers only after previous completes) | `1` |
| `--vc` | VCluster code for execution | `DEFAULT` |
| `--deps` | Dependency operation: `keep`=retain existing, `replace`=replace, `clear`=clear all | `replace` |
| `--dep-tasks` | Upstream dependency tasks as JSON array | `'[{"taskId":123,"taskName":"upstream"}]'` |

***

## Workflow Tasks (task flow)

A workflow (Flow) is a composite task type that orchestrates multiple sub-tasks as a DAG:

View the workflow DAG structure:

```bash
cz-cli -p prod task flow dag <flow_task_name>
```

Add a node:

```bash
cz-cli -p prod task flow create-node <flow_task_name> --node-name etl_step1 --type SQL
```

Set dependencies between nodes (step2 depends on step1):

```bash
cz-cli -p prod task flow bind <flow_task_name> --from etl_step1 --to etl_step2
```

Save node SQL content:

```bash
cz-cli -p prod task flow node-save <flow_task_name> --node-name etl_step1 \
  --content "INSERT INTO dwd.orders SELECT * FROM ods.raw_orders"
```

Deploy the workflow:

```bash
cz-cli -p prod task flow submit <flow_task_name>
```

View workflow node run instances:

```bash
cz-cli -p prod task flow instances <flow_task_name>
```

## Related Documentation

**cz-cli Documentation**

* [Installation and Configuration Guide](setup_cz_cli.md) — Installation, Profile configuration, basic usage
* [AI Agent Integration](cz-cli-agent.md) — Agent LLM configuration, natural language operations
* [External Data Source Management](cz-cli-datasource.md) — Data source browsing and testing

**Lakehouse Related Documentation**

* [Task Development and Scheduling](task-develop.md) — Studio SQL task development, schedule configuration (web interface)
* [Real-time Sync Tasks](realtime_sync.md) — CDC real-time sync task configuration and management
* [Offline Sync Tasks](batch_sync.md) — Batch offline sync task configuration and management
* [Composite Tasks](composite_task.md) — Workflow DAG orchestration (web interface)
* [Compute Clusters](virtual-cluster.md) — VCluster types and sizing
