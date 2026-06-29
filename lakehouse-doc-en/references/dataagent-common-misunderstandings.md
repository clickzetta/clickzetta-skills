# Data Engineering Agent Common Misunderstandings

This guide covers the most common misunderstandings when using the Data Engineering Agent, with a focus on "looks like it's done, but actually isn't" scenarios.

## Misunderstanding 1: Creating a Draft Means It Has Already Run

Creating a Studio draft task only saves the object and code to the task tree or IDE. It does not automatically execute SQL or create the target table. Draft, run, and publish are three separate stages: a draft means metadata has been created, running means the code has actually executed, and publishing means the task has entered the scheduling system.

## Misunderstanding 2: Saving a Schedule Means It Has Already Been Published

Saving a schedule configuration only writes parameters such as Cron, retry, timeout, and dependencies into the task metadata. It does not mean the task has entered the scheduling system. Only after the publish operation is executed will the task trigger on a periodic basis.

## Misunderstanding 3: A Composite Task Created Successfully Means Node Dependencies Are in Place

When a composite task or Flow object is created successfully, it only means the container object was created. You still need to confirm whether the nodes exist, whether the DAG is empty, whether the dependency edges are connected, and whether the node content has actually been written inside the composite task. Always verify the DAG in the Studio canvas; do not rely solely on the Agent's verbal response.

## Misunderstanding 4: An Empty Monitoring Page Means a System Error

An empty monitoring view typically means there are no run instances within the recent time range, or the current workspace is only a development or test workspace, or the task has never been published or executed. First expand the time range and confirm whether the task has any run history — do not jump straight to concluding it is a system error.

## Misunderstanding 5: DQC Created Successfully Means the Rule Has Already Run

Creating a DQC rule only means the governance rule metadata has been created. It does not mean the rule has been triggered or executed. This is especially important when the trigger method is `REST` (manual trigger) — "rule created" should never be interpreted as "validation completed."

## Misunderstanding 6: If the Agent Can Query an Object, It Can Always Delete It

Some objects can be queried, but deletion may not have a corresponding API capability. In practice, the Agent may be able to confirm an object's status but still require the user to delete it manually through the Studio UI. In such cases, first ask the Agent whether it can delete directly. If not, ask the Agent to help confirm the scope of impact, then perform the operation in the UI.

## Misunderstanding 7: Metadata Changes Are Not Real Changes

Creating draft tasks, composite tasks, DQC rules, and saving schedule configurations all change Studio or governance metadata — even if they do not write to business tables. For this reason, you should still verify the results: check whether the object was created in the correct directory, whether rules and configurations are correct, and whether the DAG matches expectations.

## Related Guides

* [Data Engineering Agent](dataagent.md)
* [Safe Operation Guide](dataagent-safe-operation-guide.md)
* [Task Development Guide](dataagent-task-development-guide.md)
* [Task Group and Composite Task Guide](dataagent-task-group-guide.md)
* [DQC Data Quality Rules Guide](dataagent-dqc-guide.md)
* [Run Monitoring Guide](dataagent-monitoring-guide.md)
