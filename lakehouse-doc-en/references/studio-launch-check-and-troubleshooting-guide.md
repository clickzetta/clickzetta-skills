# Studio Launch Check and Troubleshooting Guide

This document is for users who have finished developing tasks in Studio and are preparing to go live, or who have just started running a pipeline. It helps you avoid common pitfalls at two critical stages: before launch, review the most important items; when an issue occurs, follow a more stable troubleshooting path.

This document does not replace specific feature documentation. Instead, it connects the checkpoints and troubleshooting entry points that are scattered across different modules in Studio into a path that is closer to day-to-day work.

## When to Read This First

This document is a good starting point if: your task draft is ready and you are configuring scheduling and preparing to publish; your composite task has been created and you want to confirm whether the DAG is complete; your sync task has been set up and you want to observe whether it will run stably; your task has been published but you want to do a pre-launch review; or a task's run results are not what you expected and you want to know where to start troubleshooting.

## Five Things to Confirm Before Launch

**Whether the object is in the right place.** First confirm that the current workspace is correct, that the task is in the right directory, that no test objects have been accidentally placed in the production directory, and that there are no similarly named objects that could cause confusion. This step looks simple, but it often helps you catch problems very early. If an object is already in the wrong workspace or directory, everything that follows — scheduling, publishing, and monitoring — becomes unreliable.

**What stage the object is currently at.** Before launch, it is worth confirming exactly which layer the current object is at: is it just a draft, have the draft and content been saved, has the scheduling configuration been saved, has it been published, or have run instances already been generated? Many misunderstandings come from conflating these layers — seeing a task object does not mean it is running, saving a Cron does not mean it has been published, and publishing a task does not mean run instances have been created yet.

**Whether all content and configuration is complete.** The focus varies by object type, but it is generally worth confirming at a minimum that: task content has been saved, parameters are complete, the VCluster is correct, the scheduling time matches expectations, failure retry and timeout settings are reasonable, and upstream/downstream dependencies exist. For composite tasks, also confirm that all subtask nodes exist, that node content has been completed, that dependency edges exist, and that the DAG is not empty.

**Whether this change will affect other objects.** Before launch, assess the scope of impact: will it write or overwrite data, will it affect upstream or downstream tasks, will it affect existing scheduling pipelines, and will it conflict with existing rules or instances? This step is especially relevant before publishing, modifying dependencies, backfilling, deleting, or unpublishing.

**What you plan to use to verify after the run.** Before actually going live, think through which monitoring entry point to check first, how to interpret a missing instance, whether to look at logs or configuration first if something fails, and whether to look at link status or target table results first for sync tasks. Much of the difference in troubleshooting efficiency comes not from the problem itself, but from whether you prepared a verification path before going live.

## Studio Pre-Launch Checklist

**General checks:** Workspace is correct, directory is correct, object name or ID is unambiguous, test and production objects are not mixed.

**Task object checks:** Content has been saved, parameters have been confirmed, cluster has been confirmed, scheduling configuration has been confirmed.

**Composite task checks:** Composite task object exists, node count matches expectations, subtask content has been completed, DAG dependency edges exist.

**Governance object checks:** DQC rule object exists, rule type and check target are correct, trigger method is understood.

**Pre-publish checks:** Whether publishing is actually needed right now, what the expected state is after publishing, and how to roll back or stop subsequent automated runs if something goes wrong.

## Recommended Troubleshooting Path When Issues Occur

Many anomalies in Studio can be investigated by following the same path, without needing to jump between many pages right away.

**Step 1: Confirm the object state first.** Ask whether the object still exists, which workspace it is in, which directory, and whether it is in draft, configured, or published status. If this is not yet clear, any monitoring or run results you look at next will likely be misinterpreted.

**Step 2: Then check whether there are any run instances.** If the current issue is related to "why hasn't it run" or "why are there no results," start by checking whether there are any instances in the last 24 hours. If not, check the last 30 days, and then determine whether an empty monitor is a normal empty state or needs further investigation. For new workspaces, test workspaces, and unpublished tasks, an empty state is usually not unusual.

**Step 3: If instances exist, look at logs and error summaries.** If run instances already exist, the next most useful step is to look at the run status, error summary, start and end times, log entry points, and whether re-run or backfill options are available. The goal at this step is not to explain every problem at once, but to first understand what stage the failure occurred at.

**Step 4: Then go back and review configuration and dependencies.** Many instance anomalies ultimately trace back to configuration or dependencies. Review whether the Cron is correct, the cluster is correct, retry and timeout settings are reasonable, parameters are complete, dependency relationships are correct, and the composite task DAG is complete. For sync tasks, also check the data source status, whether the sync method is correct, and whether the target table or target pipeline is landing data as expected.

## Common High-Frequency Issues and Where to Start

**Task was created but has not run:** First check whether it is only a draft or has been published, then check whether the scheduling configuration has been saved, then check whether there are any instances in the current time range, and finally determine whether an empty monitor is a normal empty state.

**Composite task was created but results are still wrong:** First check whether the composite task object exists, then check whether the DAG is empty, then check whether all node content has been completed, and finally check whether the dependency edges exist.

**Rule was created but no results are visible yet:** First distinguish whether you are looking at the rule object or whether there are already rule execution results, then confirm the current trigger method.

**Monitor page is empty — how to interpret this:** First determine whether this is a new workspace or test workspace, then confirm whether the current object has never been published or run, then check whether the last 24 hours and 30 days are both empty.

## More Reliable Phrasing When Using the Agent for Launch and Troubleshooting

**Pre-launch check:**
> Please do a read-only check of the launch readiness for `{object}`. Return the current workspace, directory, object status, whether content has been saved, whether the scheduling configuration has been saved, whether it has been published, and any items that still need to be confirmed before publishing. Do not make any changes.

**Composite task review:**
> Please do a read-only review of the actual DAG for composite task `{object}`. Return the node count, node names, node types, and dependency edges. Please explicitly state whether the DAG is empty. Do not modify any configuration.

**Run anomaly troubleshooting:**
> Please do a read-only investigation of recent run activity for `{object}`. First confirm the current status and whether there are any instances in the last 24 hours and 30 days; if there are, return the run status, error summary, and recommended next steps. Do not re-run, do not backfill, do not modify configuration.

**Check impact scope before a high-impact operation:**
> Please first do a read-only analysis of which objects will be affected by `{publish / unpublish / delete / backfill / re-run / modify dependencies}`, and describe what I should focus on verifying after execution. Do not execute.

## Related Documentation

* [Studio](studio_manual.md)
* [Studio Object Relationships and Lifecycle](studio-object-lifecycle-guide.md)
* [How to Get the Agent to Operate Studio Accurately](studio-agent-operation-guide.md)
* [Task Development and Scheduling](task-develop.md)
* [Composite Tasks](composite_task.md)
* [Task Scheduling and Instance Execution](f6fc6447ee.md)
* [Task Scheduling Dependencies](task_scheduling_dependency.md)
* [Task and Instance Operations](task-instance-maintenance.md)
* [Backfilling Tasks](backfilling_data.md)
* [Monitoring and Alerting](monitoring_and_alerting.md)
* [Data Quality](data-quality.md)
