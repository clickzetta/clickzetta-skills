# Studio High-Impact Operations Guide

In Studio, some operations directly affect task execution, upstream and downstream pipelines, historical instances, or objects that other team members are actively using. This document is useful when you are preparing to publish or unpublish a task, delete a task or dependency, run backfills or re-runs, adjust scheduling cycles or dependency configurations, or asking the Agent to help with high-impact operations.

## What Counts as a High-Impact Operation

Publishing a task, unpublishing a task, deleting a task, deleting dependencies, backfilling, re-running, modifying a scheduling cycle, and modifying task dependencies all share one characteristic: they do not just change a configuration field — they often affect subsequent runs, instance generation, upstream and downstream pipelines, or team collaboration.

## A Common Processing Sequence

When handling high-impact operations, the typical flow involves five steps: first confirm who the object is, then confirm its current state, then confirm which other objects will be affected, then decide whether to proceed, and after execution do a second review. This sequence applies equally when the Agent is assisting.

## First, Confirm the Object

One of the more common risk points in high-impact operations is object identification errors. It helps to first confirm the workspace, the task directory, the task name or ID, and the target object type (regular task, composite task, task group, dependency relationship, or instance). If the object came from a search result or a list view, it is usually worth going into the detail page for a second confirmation.

## Then, Confirm the Current State

The same task may call for different actions depending on its current state. It is worth checking whether it is currently in draft status, whether it has been published, whether a scheduling configuration exists, whether there are any instances currently running or queued, and whether upstream or downstream dependencies already exist. This step mainly helps determine whether it is appropriate to proceed with the next action.

## Then, Confirm Which Objects Will Be Affected

High-impact operations rarely affect only the current object. It is worth checking whether downstream tasks depend on it, whether it is referenced by a composite task or task group, whether adjusting the scheduling cycle will affect upstream or downstream alignment, whether deletion will impact alerting and operational troubleshooting, and whether backfilling or re-running will overwrite or duplicate downstream results. If this layer of information is still unclear, it is usually worth waiting before proceeding.

## Then Decide Whether to Execute

Before actually executing, you can express the action as one complete sentence: "In such-and-such workspace, in such-and-such directory, perform such-and-such action on such-and-such task, with the expected impact being such-and-such." This makes it easier to spot object or scope errors, reduces ambiguity when the Agent is assisting, and makes team review more straightforward.

## After Execution, Do a Second Review

After the operation completes, it is usually worth confirming: whether the operation actually succeeded, whether the object state has changed, whether the scheduling or dependency changes have taken effect as expected, whether new instances have been created or existing ones have stopped, and whether you need to continue monitoring run results and alerts. This step helps catch the situation where "the action succeeded but the result was not what was expected" earlier.

## Publishing a Task

Before publishing, it is common to confirm: whether the current edits have been saved, whether task parameters, resource configuration, and dependencies are complete, whether the scheduling cycle matches expectations, and whether the task is ready to enter live running. After publishing, verify that the publish status has updated, that the scheduling configuration is still correct, and that subsequent instances are generated as expected. For important tasks, it is usually worth reviewing alongside the [Launch Check and Troubleshooting Guide](studio-launch-check-and-troubleshooting-guide.md).

## Unpublishing a Task

Before unpublishing, check whether the task is still being depended on, whether there is still a business-side dependency on its output, and whether this is a temporary suspension or a permanent decommission. After unpublishing, confirm that the task status has changed, that future instances will stop being generated as expected, whether you need to communicate with upstream and downstream owners, and whether alerts or on-call information need to be updated.

## Deleting a Task

Deletion is generally a high-scope operation. Before deleting, confirm that the task is no longer in use, that all dependencies have been removed, whether the object still needs to be retained for historical troubleshooting, and whether there are better alternatives (such as first disabling, first unpublishing, or first moving to a different directory). If other team members might still query this task, direct deletion is usually not the first approach.

## Deleting a Dependency

Before deleting a dependency, first confirm the role that dependency plays: is it controlling scheduling order, ensuring data readiness, or enforcing pipeline governance constraints? After deletion, confirm whether downstream tasks will still run at the correct time, whether the change introduces early runs, empty runs, or missed runs, and whether additional triggers or constraints need to be added.

## Backfilling and Re-running

Backfills and re-runs are common but can easily cause cascading effects. Before executing, check the time range for the backfill or re-run, the target instances or target partitions, whether upstream and downstream tasks need to be coordinated, whether existing results will be overwritten, and whether duplicate writes could occur. After execution, continue monitoring whether instances reach the expected state, whether the data results match expectations, and whether downstream tasks are correctly triggered or remain stable.

## Using the Agent to Assist with High-Impact Operations

For high-impact operations, a common approach is to use the Agent in two rounds: in the first round, do a read-only confirmation (confirm the object location and current state, list upstream and downstream dependencies and potential impacts, and identify any missing information before executing); in the second round, execute the action (perform the publish, delete, backfill, or re-run after confirmation, and return the results, state changes, and points that need continued monitoring). This two-round approach is generally better suited to team collaboration and scenarios with higher review requirements.

## Related Documentation

- [Studio Object Relationships and Lifecycle](studio-object-lifecycle-guide.md)
- [How to Get the Agent to Operate Studio Accurately](studio-agent-operation-guide.md)
- [Launch Check and Troubleshooting Guide](studio-launch-check-and-troubleshooting-guide.md)
