# Flow (Composite Task) Guide

A **composite task** (Flow) is a DAG of SQL/Python/Shell nodes that run in dependency order under a single scheduling configuration. Typical use: ODS extract → DWD clean → DWS aggregate as a multi-step pipeline.

---

## Full Creation Workflow

```bash
# Step 1: Create the Flow task itself
cz-cli task create <flow_name> --type FLOW --folder <folder>

# Step 2: Add nodes (SQL / Python / Shell)
cz-cli task flow create-node <flow_name> --name <node_name> --type sql
# Returns node id — subsequent steps can use --node-id <id> or --name <node_name>

# Step 3: Write node script content
cz-cli task flow node-save <flow_name> --name <node_name> --content "SELECT ..."
# Or read from file:
cz-cli task flow node-save <flow_name> --name <node_name> --file ./node.sql

# Step 4: Configure node execution settings (VC + schema)
# ⚠️ Required for every node — flow submit fails if any node skips this step
cz-cli task flow node-save-config <flow_name> --name <node_name> --vc DEFAULT --schema public

# Step 5: Set node dependencies
# node_b waits for node_a to complete before running
cz-cli task flow bind <flow_name> --upstream <node_a> --downstream <node_b>

# Step 6: Publish the Flow
cz-cli task flow submit <flow_name>
# [Known limitation] CLI submit may not fully publish — if Studio status stays unpublished,
# go to Studio UI and click Submit manually.
```

---

## Run and Monitor

```bash
# Ad-hoc execution (does not affect the schedule)
cz-cli task flow run <flow_name>
# Returns schedule_instance_id

# View node-level run records for an instance
cz-cli task flow instances <flow_name> --flow-instance <schedule_instance_id>
# Note: use --flow-instance (not --instance, which is the global ClickZetta instance name option)

# View DAG structure (nodes + dependencies)
cz-cli task flow dag <flow_name>

# View a single node's content and config
cz-cli task flow node-detail <flow_name> --node-id <id>
```

---

## Management

```bash
# Remove a dependency edge
cz-cli task flow unbind <flow_name> --upstream <node_a> --downstream <node_b>

# Delete a node from the Flow
cz-cli task flow remove-node <flow_name> --node-id <id>
```

---

## Node Parameters

```bash
# Set node-local params (key=value)
cz-cli task flow node-save <flow_name> --name <node> --param dt=2026-01-01 --param env=prod

# Set params inherited from the parent Flow (key only, value comes from Flow-level params)
cz-cli task flow node-save <flow_name> --name <node> --flow-param dt --flow-param env

# Set Flow-level params (automatically passed to all child nodes)
cz-cli task save-schedule <flow_name> --param dt=2026-01-01

# Override params for a single ad-hoc run
cz-cli task flow run <flow_name> --param dt=2026-06-18
```

---

## Important Notes

| Issue | Detail |
|---|---|
| `node-save-config` is required | Every node must have VC + schema configured before `flow submit` |
| `flow bind` is async | API returns success before the edge is durably written; CLI auto-retries up to 3× and returns a warning if still not confirmed |
| `columnMapping` direction | For INTEGRATION nodes inside a Flow, format is `"sink_col": "source_col"` (e.g. `"id": "ID"`). Reversed direction causes Studio field-mapping switches to show as disabled |
| `flow submit` known issue | CLI may return `published: false`; the Flow can still run, but verify published status in Studio UI |
| Flow does not use `task deploy` | Use `flow submit` to publish; calling `task deploy` on a Flow returns an error |
| `task flow instances --flow-instance` | The ID is the `schedule_instance_id` returned by `flow run`, not a task ID. Use `--flow-instance`, not `--instance` (which is the global ClickZetta instance name option) |
