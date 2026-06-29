# Merge Task

## Overview

A Merge Task **consolidates the run state of upstream nodes** into a single, definitive final state, solving the problem of **dependency attachment and run triggering for downstream nodes of branch tasks**.

In branch scenarios, each run of a Branch Task triggers only one branch path; all other branches are skipped because "the branch condition was not met." If a downstream task depends on multiple branch outputs simultaneously, it can never satisfy the "all upstream succeeded" condition under standard dependency logic, preventing it from triggering.

A Merge Task resolves this by applying custom merge logic (such as "any branch completing counts as success"), consolidating the states of multiple branches into a single unified final state so that downstream tasks can be triggered normally or skipped as intended.

## When to Use a Merge Task

The core value of a Merge Task is **handling downstream dependency triggering after branches**. Use a Merge Task in the following situations:

1. **Downstream needs "any branch completing continues"**

   A Branch Task triggers only one branch path per run; all other branches are skipped. If a downstream task depends on output from multiple branches simultaneously, standard dependency would prevent triggering because "not all upstream succeeded."

   Use a Merge Task with **OR** logic to consolidate these branch states — any branch completing counts as satisfied, and the downstream can be triggered normally.

   > Example: based on data volume, the flow takes either a "full sync branch" or an "incremental sync branch," both writing to the same table. The downstream cleaning/aggregation task must proceed regardless of which branch runs.

2. **Multiple branches converging into unified downstream processing**

   Multiple branches handle data from different sources or different logic (e.g., multiple channels or business lines), all flowing into the same downstream task (unified reporting, aggregated wide tables, unified ingestion). Use a Merge Task to unify these branch states into a single final state, serving as a single dependency entry for downstream and avoiding downstream needing to depend on multiple branch outputs that can never all be satisfied simultaneously.

3. **Downstream trigger condition is a logical combination, not "all succeeded"**

   When whether a downstream task runs depends on a **combined judgment** of multiple upstream states (e.g., "A succeeded OR B succeeded," "A succeeded AND B branch was not triggered"), not simply "all upstream succeeded" — use a Merge Task's AND/OR combination with multiple final states (success / failure / branch condition not met) to express this trigger logic precisely.

4. **Need fault tolerance / fallback for branch results**

   When you want downstream to process things as expected even when a branch **fails or is not triggered** (for example, take a fallback path, or explicitly skip), select the corresponding final state in the merge condition to converge uncertain branch results into a definite downstream trigger signal.

### When Not to Use

- **No branches upstream; a standard linear dependency**: use standard scheduling dependencies. No need for a Merge Task.
- **Downstream depends on only one upstream and the condition is simply "run when upstream succeeds"**: standard dependencies are simpler and clearer.
- **Tasks that need ad-hoc runs or backfill**: Merge Tasks do not currently support ad-hoc runs or backfill (see Limitations).

## Core Concepts

### Final State (Execution State)

Merge conditions evaluate based on the **terminal state** of upstream nodes. Three states are supported:

| Execution state | Description |
|---|---|
| Success | Node ran to normal completion |
| Failure | Node run failed |
| Branch condition not met | Upstream is a Branch node; this run did not trigger that branch, so the branch logic did not execute |

## Create and Configure a Merge Task

After adding a Merge Task, configure the merge logic through **visual drag-and-drop**.

![](/.topwrite/assets/image_1781664036042.png =733)

### Merge Condition Settings

Each merge condition has two configuration parts:

1. **Select upstream task** — consistent with task scheduling dependencies; select the upstream task by **task name, output name, or output table name**.

   > Note: if the upstream is a Branch Task, further select the **specific branch output name under that branch task**.

2. **Select the execution state of that task** — the terminal state of the upstream node: success, failure, or branch condition not met (see the Final State section above).

Multiple merge conditions can be added and combined using AND/OR logic.

**Logic operators**:

When multiple merge conditions are configured, AND/OR operations are supported:

- **AND**: all upstream branch nodes must be in a terminal state (i.e., finished), **and all** must satisfy their respective configured execution states, for the run state configured in "execution result settings" to take effect.
- **OR**: all upstream nodes must be in a terminal state (i.e., finished), **and any one** branch node satisfying its configured execution state is sufficient for the run state configured in "execution result settings" to take effect.

### Relationship Between Merge Conditions and Scheduling Dependencies

Merge conditions are essentially "select upstream dependency tasks and consolidate their states," so there is a **one-way automatic sync** between merge conditions and scheduling dependency configuration:

> **"Merge conditions" → "Scheduling config": one-way save**

- When the user clicks save, the system automatically **adds the upstream tasks in the merge conditions to the "scheduling dependencies" configuration**.
- Conversely, task dependencies manually added in "scheduling dependencies" are **not** automatically backfilled into merge conditions.

**Example**: A Merge Task consolidates the states of "branch downstream 1" and "branch downstream 2," and additionally depends on "report 2" in scheduling dependencies. The run condition for the Merge Task is: "branch downstream 1" and "branch downstream 2" satisfy the merge condition, **and then** it must also **wait for "report 2" to finish executing** before the Merge Task actually runs.
