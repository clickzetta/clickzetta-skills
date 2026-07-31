# Data Engineering Agent Task Directory and Governance Guide

The Studio task tree is the organizational entry point for data engineering tasks. As the number of tasks grows, without a directory structure, tasks end up scattered across default or personal directories, making it much harder to find tasks, publish them, configure dependencies, manage permissions, and clean up tests.

The goal of task directory governance is to ensure that from the moment a task is created, it is locatable, maintainable, publishable, and cleanable.

## Directory Management Capabilities

The Studio task tree supports the following directory management operations:

* Create a directory
* Rename a directory
* Move a directory
* Delete a directory
* Create tasks in a specified directory

Tasks can also be opened, copied by name, renamed, moved, copied, deleted, and added to task groups via the task tree menu. A confirmation prompt appears before deletion.

## Why Govern Task Directories

Task directories are not just visual groupings — they affect downstream engineering management:

* Tasks have a clear home when created, making them easy to find
* Multiple tasks can be managed together by pipeline, project, or layer
* It is easier to review tasks in the same chain before publishing
* Test tasks can be cleaned up in bulk to avoid polluting production directories
* Production and temporary tasks can be isolated
* Teams can more easily establish consistent conventions for collaboration

If a task is created in the wrong directory from the start, moving it later is possible but often causes confusion in dependencies, documentation, and communication.

## Recommended Directory Organization Approaches

| Organization approach | Applicable scenario | Example |
| --- | --- | --- |
| By business domain | Multiple business teams sharing a workspace | `Sales Domain/Daily Aggregation`, `Finance Domain/Reconciliation` |
| By project | Project-based development or dedicated delivery | `Member Growth Project/Data Preparation` |
| By data warehouse layer | Large number of warehouse tasks | `ODS`, `DWD`, `DWS`, `ADS` |
| By environment | Test and production coexist | `Test Tasks/Temp Development`, `Production Tasks/Sales Report` |
| By lifecycle | Temporary queries or short-term validation | `Temp Queries/2026Q2` |

Organizations can combine approaches. For example:

```text
Sales Domain/
  Test Tasks/
  DWD/
  DWS/
  ADS/
```

Or:

```text
Member Growth Project/
  01_Data Exploration/
  02_Metric Validation/
  03_Data Warehouse Modeling/
  04_Production Release/
```

## Confirm the Directory Before Creating a Task

When creating tasks through the Data Engineering Agent, specify the target directory in the prompt.

Suggested prompt:

> Please create the task in the Studio task directory `{task directory}`. If the directory does not exist, please tell me first so I can create it in Studio — do not create to a default or other directory.

Do not just say:

> Help me create a SQL task.

This prompt provides no directory information. The task may end up in the current directory, default directory, or most recently used directory, making it hard to find and govern later.

## Test Task Directory

Test tasks should be concentrated in a cleanable directory, for example:

```text
Test Tasks/Temp Development
```

Test task names should convey purpose and date, for example:

```text
test_failure_diagnosis_20260610
sales_summary_draft_20260610
```

After testing is complete, clean up promptly: cancel publishing if the task has been published, confirm there are no downstream dependencies, confirm no run records need to be kept, then delete the draft task from the Studio UI.

## Production Task Directory

Production task directories should be more stable — avoid frequent renames and moves. Directory names should include the business domain or project name, data warehouse layer, or task type. Task names should be clear. Necessary dependency relationships and launch check records should also be maintained. Do not place production tasks and temporary test tasks in the same directory — mixing them makes it easy to accidentally affect the wrong tasks during publishing, re-running, taking offline, or batch cleanup.

## Directory Change Considerations

### Renaming a Directory

Before renaming, confirm whether team members rely on the original directory name to find tasks, whether documents or work orders reference the original directory, and whether renaming will affect operational troubleshooting.

### Moving a Directory

Before moving, confirm whether the directory contains production tasks, whether task groups or upstream/downstream dependencies exist, and whether the move still complies with business domain and environment conventions.

### Deleting a Directory

Before deleting, confirm whether the directory is empty, whether it contains published tasks, whether it contains test records that still need to be kept, and whether downstream tasks have dependencies. Delete operations should be carefully confirmed in the UI — do not treat directory cleanup as a routine tidying task.

## Recommended Prompt Templates

### Create a task in a specified directory

> Please create SQL draft task `{task_name}` in the Studio task directory `{task directory}`. If the directory does not exist, please tell me first so I can create it in Studio — do not create to a default directory.

### Check a task's directory

> Please check the directory where task `{task_id}` is currently located, the task type, whether it has been published, and whether it has downstream dependencies. Do not modify the task.

### Clean up test tasks

> Please check whether task `{task_id}` has been published, whether it has downstream dependencies, and whether it has run history. If it can be cleaned up, tell me what confirmations should be done first. Do not delete directly.

### Plan the directory structure

> I am about to build a set of data engineering tasks for `{business domain or project}`. Based on the business domain, environment, data warehouse layer, and lifecycle, design a Studio task directory structure. Only output the recommendations; do not create directories.

## Related Guides

* [Data Engineering Agent](dataagent.md)
* [Safe Operation Guide](dataagent-safe-operation-guide.md)
* [Task Development Guide](dataagent-task-development-guide.md)
* [Scheduling and Release Guide](dataagent-scheduling-and-release-guide.md)
