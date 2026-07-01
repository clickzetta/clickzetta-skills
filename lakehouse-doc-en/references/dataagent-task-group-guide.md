# Data Engineering Agent Task Group and Composite Task Guide

This guide covers the practical usage of task groups, composite tasks, and Flow-type objects in the Data Engineering Agent, focusing on creation entry points, key fields, DAG review methods, and commonly misunderstood aspects.

## Explore First, Then Operate Orchestration Objects

Task groups, composite tasks, and Flow-type objects depend more on context than ordinary SQL or Python tasks.

The more natural approach is usually not to immediately ask the Agent to create or modify a DAG, but to explore first:

- Whether the current directory already has relevant composite tasks
- Whether the current object is a task group, composite task, or subtask inside a composite task
- Whether the DAG already has nodes and dependency edges

Better opening questions:

- Help me check whether there are existing composite tasks in the current directory that can be reused.
- Help me determine whether this object is a task group, composite task, or regular task.
- Help me first check this composite task's actual DAG before modifying nodes or dependencies.

Once object type, directory location, and DAG state are clear, creating nodes, binding dependencies, or joining task groups is more stable.

## Clarify Concepts First

In Studio, multi-task orchestration involves at least three different actions:

- Create a composite task
- Treat a task as a task group
- Add a task to an existing task group

These three are not the same action and cannot all be described vaguely as "create a task group."

## Actual Entry Points

In the new task menu in the IDE's left-side task tree, the composite task entry is:

```text
Other → Composite Task
```

This is not the same entry as regular SQL, Python, or Shell tasks — it is a separate task type.

## Composite Task Creation Dialog

The actual creation dialog includes at least these fields:

- `Task name`
- `Folder`
- `Task group`

The `task group` field may default to `No`. When switched to `Yes`, the interface additionally shows:

```text
Please select a task group
```

This shows that the interface distinguishes two cases:

- The current object is just a composite task
- The current object needs to be attached to a task group relationship

When requesting Agent operations, specify clearly which one you want.

## Recommended Prompt Approaches

To create a composite task:

> Please create a composite task draft under `{task_directory}`. Only create the object; do not execute, do not publish. After creation, return the task ID, directory, current DAG node count, and whether it is published.

To add a task to an existing task group:

> Please add task `{task_id or task_name}` to existing task group `{task_group_name or ID}`. Before adding, describe the current task group state, existing node count, and the relationship to be added. Do not execute; do not publish.

To create nodes in a composite task and bind dependencies:

> Please add two nodes to composite task `{task_id or task_name}` and configure the second node to depend on the first. After completion, return the node list and dependency edges — do not return only the task creation result.

## What to Review After Creation

Multi-node tasks most commonly have the issue of "object created but DAG not set up correctly." After creation, review:

- Whether the composite task object actually appears in the task tree
- Whether nodes actually appear on the canvas
- Whether the node count matches expectations
- Whether node names match expectations
- Whether dependency edges exist between nodes
- Whether the DAG is empty
- Whether node content belongs inside the composite task rather than as scattered standalone tasks

Recommended question:

> Please check the actual DAG of composite task `{task_id}`. Return node count, node names, node types, a content summary for each node, and dependency edges between nodes. Explicitly state whether the DAG is empty. Do not execute, do not publish, do not modify configuration.

## An Important Operational Conclusion

In actual validation, the following situation occurred:

- The Flow/composite task object itself was created successfully
- The Agent's read-only return said the DAG was empty
- But the Studio canvas actually showed two nodes and one dependency edge

This shows that documentation and operational standards must emphasize:

- Do not rely solely on the Agent's verbal response
- Do not rely solely on "creation successful" notifications
- The actual objects in the task tree and canvas are the source of truth

## Difference Between Composite Tasks and Regular Tasks

| Object | Key things to check |
|---|---|
| Regular SQL/Python/Shell task | Task directory, code content, scheduling config, publish state |
| Composite task / Flow | Task directory, canvas nodes, dependency edges, node content, publish state |

For regular tasks, check code and scheduling. For composite tasks, also check the canvas structure.

## Risks and Important Notes

- Creating a composite task does not mean its nodes have been created
- Creating nodes does not mean dependencies have been bound
- Binding dependencies does not mean subsequent scheduling relationships have been published
- Before deleting a composite task, confirm whether it is published, has run records, or is still associated with other tasks

For testing purposes, put composite tasks in a test directory and delete them promptly after validation.

## Related Documentation

- [Data Engineering Agent](dataagent.md)
- [Task Development Guide](dataagent-task-development-guide.md)
- [Scheduling and Publishing Guide](dataagent-scheduling-and-release-guide.md)
- [Safe Operation Guide](dataagent-safe-operation-guide.md)
- [Prompt Examples](dataagent-prompt-examples.md)
