# Studio MCP: Working with Offline Sync Tasks

In an ELT workflow, offline sync tasks handle the "stable data loading into the Lakehouse" step. Many downstream SQL transformations, metric calculations, and analytics tasks depend on this step being complete.

The Studio-hosted MCP Server can independently handle the core workflow for offline sync tasks. For standard source-to-target load scenarios, you can ask the Agent directly to create tasks, save sync configuration, trigger runs, and read back run results and instance information.

The value here is not just "having the Agent click through the configuration for you" — it is bringing data load tasks into a queryable, executable, and diagnosable structured workflow.

## When to Use This

Typical scenarios well suited for using offline sync tasks through MCP include:

* Periodically loading single-table data from an external data source into the Lakehouse
* Creating a standard source-to-target sync task
* Quickly validating whether the source, target, and sync rules are functional
* Reading records, dirty data, and instance information directly after a run
* Chaining "create sync task," "run once to check," and "view results" into a continuous operation

If your goal is to have the Agent participate in upstream data loading — not just downstream SQL development — offline sync tasks are a natural object to start with.

## How to Prompt the Agent

In offline sync task scenarios, the most important thing when prompting is to clarify the source, target, and intended operation.

If the source table, target table, or catalog location is not fully confirmed, explore first:

* Show me which tables in `aliyun_mysql` are suitable for this sync.
* Check the current catalog for any existing offline sync tasks to reuse.

If the source, target, and intent are confirmed, execute directly:

* Create an offline sync task to sync `test_mysql_sink2` from `aliyun_mysql` to the target Lakehouse table.
* Save this sync task to the `Temp Dev` catalog.
* After saving, run it once and check whether the read and write are normal.

If you care more about the validation result, follow up with:

* Show me how many records this sync read and wrote.
* If there is dirty data, include that too.

The key in these prompts is not asking the Agent to "create an integration task," but clearly stating the source table, target table, and the goal of "run once to check."

## What a Complete Workflow Includes

For an offline sync task, MCP can handle the following actions end-to-end:

* Creating the offline sync task
* Saving the source, target, and sync configuration
* Opening and identifying the task object
* Triggering a run
* Reading the run result
* Navigating to the task instance operations page
* Reading back task instance details

This means the Agent can go from "knowing there is a source table" all the way to "having a real, runnable data load task."

## Where Offline Sync Tasks Fit in ELT

In a typical ELT workflow, an offline sync task is closer to the load layer:

* The upstream source system produces data.
* The offline sync task loads the data into the Lakehouse.
* Downstream SQL or Python tasks then perform transformations and produce outputs based on those tables.

The problem it solves is therefore not metric computation, but:

* Whether data was loaded as expected
* Whether source and target are connected
* Whether the sync configuration is valid
* What the result of this load run looks like

Without this load layer, downstream SQL tasks — no matter how well written — lack a stable data input.

## Saving Sync Configuration

Unlike SQL and Python tasks, an offline sync task saves structured configuration rather than script content.

This configuration typically covers three things:

* Source object
* Target object
* Sync rules

After saving, the task is no longer just an empty shell — it has a runnable load definition.

For the Agent, this matters because it shows MCP can operate not just on code-type tasks, but also on real Data Integration objects.

## What Run Results Show

After an offline sync task runs, the most important results include:

* Records read
* Records written
* Dirty records read
* Dirty records written
* Log entry point
* Instance operations entry point

This information is more valuable than a simple "success" or "failure," because it directly answers:

* Whether source data was actually read
* Whether the target received a successful write
* Whether any anomalous records appeared at the data quality level

For load tasks, these are the results to read back first.

## Post-Run Diagnosis

After an offline sync task executes, MCP can chain the run information further, including:

* Task instance ID
* Run state
* Run duration
* Result summary
* Link to the instance operations page

This matters because the Agent is not just responsible for creating and running the task — it can also handle the first round of run confirmation:

* Whether an instance was successfully created
* Whether actual reading and writing started
* Whether further inspection of instance details is needed

This gives offline sync tasks the same "read back immediately after execution" experience as SQL tasks.

## How to Bring This into Daily Workflows

If you plan to bring offline sync tasks into a regular MCP-only workflow, the natural order is typically:

* Confirm the source and target tables.
* Have the Agent create the sync task.
* Save the sync configuration.
* Trigger a run.
* Read back the record counts, state, and instance information.

This approach is especially well suited for:

* Creating new standard load tasks
* Running a connectivity and load validation
* Confirming that sync configuration actually works before going to production

## Practical Value

For offline sync tasks, the value MCP can most readily deliver falls into three areas:

* Bringing data load tasks into the set of objects the Agent can operate on in a structured way
* Chaining configuration, execution, and result reading into a continuous workflow
* Letting you complete a load validation without switching tabs

If your team wants the Agent to extend from downstream analytics tasks up into upstream data loading, offline sync tasks are a natural expansion point.
