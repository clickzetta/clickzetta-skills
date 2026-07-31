# Data Engineering Agent Scheduling and Publishing Guide

This guide covers how to use the Data Engineering Agent to configure Studio task scheduling, publish tasks to the scheduling system, and unpublish after publishing. It focuses on the distinction between "save scheduling configuration" and "publish to the scheduling system."

## When to Use This

When a Studio task has completed draft development and is ready to run automatically on a schedule, use the Data Engineering Agent to help check, configure, or prepare for:

- Configuring cron scheduling intervals
- Configuring failure retry count and timeout
- Configuring or checking upstream/downstream dependencies
- Publishing tasks to the scheduling system
- Checking whether a task is published
- Querying the next scheduled run time
- Pausing or unpublishing tasks

Scheduling and publishing affect whether a task runs automatically — these are change operations. Whether they can be executed directly depends on current permissions, open tool capabilities, and workspace configuration. Before executing, have the Agent explain the impact scope and confirm with you.

## Explore First, Then Enter Scheduling and Publishing

Scheduling and publishing are not suited to immediate execution.

The more natural approach is:

- Confirm whether the task already meets publishing conditions
- Determine whether what's missing is scheduling parameters, dependencies, or the actual publishing action
- Once configuration and impact scope are clear, actually save the schedule or publish

Better exploratory opening questions:

- Help me check whether this task currently meets publishing conditions.
- Help me check what this task is currently missing: cron, dependencies, VCluster, or retry and timeout config.
- Help me check whether this task is currently a draft, has saved scheduling, or is already published.

When these states are clear, saving the schedule, publishing, or unpublishing is more stable.

## Three Phases of Scheduling and Publishing

### Task Draft

A task draft is a task file in the Studio IDE. Drafts can contain SQL, Python, Shell, and other code, but they do not enter the scheduling system automatically.

A draft typically means:

- The task appears in the specified task directory
- Task code is saved
- Task is not published
- Will not run automatically on schedule
- Creating a draft does not produce run instances

### Save Scheduling Configuration

Saving scheduling configuration writes cron, retry, timeout, compute cluster, and other settings into task metadata — but this does not mean the task is published. After saving, the task has scheduling parameters but still does not run automatically.

Only after the publishing action will the task enter the scheduling system.

### Publish Task

Publishing submits the task to the scheduling system. After publishing, the task typically waits for subsequent cron triggers. Whether it runs immediately depends on the frontend response and scheduling system feedback.

Before publishing, confirm the SQL type, target table, compute cluster, scheduling time, retry strategy, timeout, and upstream/downstream dependencies.

## Recommended Workflow

### Confirm the Task Draft First

Before publishing, have the Agent check the task content.

Recommended question:

> Please check the SQL content of task `{task_id}`. Describe whether it is a read-only query, CREATE TABLE, INSERT, or overwrite write. List which tables will be affected when it runs, and identify risks to check before publishing.

Key checks:

- Whether the task is in the correct directory
- Whether the SQL matches expectations
- Whether SQL will write or overwrite data
- Whether the schema is correct
- Whether the compute cluster is correct
- Whether upstream/downstream dependencies are needed

If this information is not yet clear, ask first:

> Please first check whether this task currently meets the conditions to enter the scheduling phase, without modifying any configuration.

### Save Scheduling Configuration Without Publishing

Configure scheduling parameters first, then check the configuration result.

Recommended question:

> Please configure scheduling parameters for task `{task_id}`, but do not publish the task yet. Requirements: run daily at 23:59, 1 retry on failure, 10-minute timeout, no upstream/downstream dependencies configured. Do not execute the task, do not publish, do not run immediately. Before configuring, explain what will be changed, whether it will enter the scheduling system, and whether it will produce run instances — and request my confirmation.

The Agent should explain:

- Which task will be modified
- The cron expression
- Failure retry count
- Timeout
- VCluster
- Whether there are upstream/downstream dependencies
- Whether saving the configuration enters the scheduling system
- Whether run instances will be produced

After saving, confirm again:

> Please return the current task status, cron, retry, timeout, VCluster, whether published, and whether there is a next scheduled run time.

### Confirm Impact Before Publishing

Before publishing, have the Agent do one dedicated confirmation.

Recommended question:

> Please now publish task `{task_id}` to the scheduling system. Before publishing, explain: which task will be published, the current cron, retry, timeout, VCluster, whether it will run immediately after publishing, the next scheduled run time, and how to unpublish. Request my confirmation first; do not publish directly.

Key checks in the pre-publishing confirmation:

- Whether the publish target is correct
- Whether the task SQL still matches expectations
- Whether the VCluster is correct
- Whether the cron matches expectations
- Whether it will run immediately
- Whether the next scheduled run time is reasonable
- How to pause or unpublish

### Confirm and Publish

After confirming everything, have the Agent publish.

Recommended question:

> Confirmed — publish task `{task_id}`. After publishing, return the publish state, current version, and next scheduled run time (if available). Do not manually run the task.

After publishing, the task typically enters the scheduling system and waits for subsequent cron triggers. Whether run instances are immediately produced depends on the frontend response and scheduling system feedback. Confirm:

- Whether the task publish state has been updated
- Whether the next scheduled run time was returned

### Unpublish or Pause Scheduling

After publishing, if subsequent automatic runs need to stop, choose to pause or unpublish.

Common operations:

| Operation | Typical meaning | When to use |
|---|---|---|
| pause | Typically pauses subsequent schedule triggers; actual state change depends on product feedback | Temporarily stop automatic runs |
| undeploy | Typically removes from the scheduling system; how to resume depends on product feedback | Cleaning up test tasks, taking tasks offline |

Recommended question:

> Please unpublish task `{task_id}` using `undeploy` to remove it from the scheduling system. Do not delete the task draft. Do not execute the task. Do not affect other tasks. Before the operation, explain the action and its impact, and request my confirmation.

After confirmation:

> Confirmed — execute `undeploy` on task `{task_id}` only. Do not delete drafts, do not execute tasks, do not affect other tasks. After completion, return the current publish state and whether the next scheduled run has been cancelled.

After unpublishing, whether the task has been removed from the scheduling system, whether it will still trigger automatically, and whether drafts and configuration are preserved — rely on backend return results and interface state, not just the action name.

## FAQ

### I saved a cron, but why isn't the task running?

Saving a cron only writes it into task configuration. The task must be published to the scheduling system before it runs automatically per the cron.

### Will the task run immediately after publishing?

Typically not, but rely on the frontend response and scheduling system feedback. If you need immediate validation, execute the task separately or use a read-only query to verify — these are separate actions from publishing.

### Can I unpublish a task after publishing?

Typically yes. You can confirm whether `pause` is supported to pause scheduling, or use `undeploy` to unpublish. The specific state changes and what is preserved depend on backend results and interface state.

### Does unpublishing delete the task?

Typically it does not directly delete the task draft, but rely on backend results and interface state. Deleting a draft should be treated as a separate operation — do not conflate it with unpublishing.

### Why should I verify the VCluster?

A scheduled task actually uses the compute cluster in its task configuration. Before publishing, verify the VCluster in both the task details returned by the Agent and the current Studio configuration, to avoid running the task on the wrong compute cluster.

### How should test tasks be cleaned up?

For test tasks, follow this order:

- If published, unpublish first (`undeploy`)
- Confirm the task has been removed from the scheduling system and the next scheduled run is cancelled
- Then delete the draft from the task tree
- After deletion, confirm the task node no longer appears in the task directory

## Recommended Prompt Templates

### Configure scheduling without publishing

> Please configure scheduling parameters for task `{task_id}`, but do not publish the task yet. Requirements: `{schedule interval}`, `{count}` retries on failure, `{minutes}` minute timeout, depend on `{dependency task}`. Do not execute the task, do not publish, do not run immediately. Before configuring, explain what will be changed, whether it will enter the scheduling system, and whether it will produce run instances — and request my confirmation.

### Pre-publishing confirmation

> Please prepare to publish task `{task_id}` to the scheduling system. Before publishing, describe the task name, task directory, SQL type, cron, retry, timeout, VCluster, dependencies, whether it will run immediately after publishing, the next scheduled run time, and how to unpublish. Request my confirmation first.

### Publish task

> Confirmed — publish task `{task_id}`. After publishing, return the publish state, current version, and next scheduled run time. Do not manually run the task.

### Unpublish

> Please unpublish task `{task_id}` using `undeploy` to remove it from the scheduling system. Do not delete the task draft. Do not execute the task. Do not affect other tasks. Before the operation, explain the action and its impact, and request my confirmation.

### Clean up test tasks

> Please check whether task `{task_id}` is published. If it is, unpublish it first; after confirming the task has been removed from the scheduling system, tell me I can delete the draft from the interface. Do not delete other tasks.

## Related Documentation

- [Data Engineering Agent](dataagent.md)
- [Basic Usage Scenarios](dataagent-basic-usage-scenarios.md)
- [Task Development Guide](dataagent-task-development-guide.md)
- [Data Pipeline and Warehouse Modeling Guide](dataagent-data-pipeline-guide.md)
- [Job Diagnosis Guide](dataagent-job-diagnosis-guide.md)
- [Prompt Examples](dataagent-prompt-examples.md)
