# Studio MCP: Working with SQL Tasks

In an ELT workflow, SQL tasks are usually the core layer. Data enters the Lakehouse first, then SQL handles cleaning, joining, aggregation, metric computation, and result table generation. Most day-to-day data development work is essentially organized around SQL tasks.

The Studio-hosted MCP Server can independently complete a full workflow for SQL tasks. For daily development, temporary validation, and pre-publish checks, you can have the Agent complete task creation, content saving, parameter configuration, scheduling configuration, temporary execution, and run diagnosis without switching to the Studio page.

The core value here is not "having the Agent replace you in writing a SQL query" — it is moving a SQL task from a draft to a verifiable, reusable, and diagnosable task object.

In the context of ELT, SQL tasks are well suited for work with clear rules and in-database transformations: scheduled report generation, metric computation, detail-to-summary data processing, result table refresh, data validation, and pre-publish verification.

In a typical data development workflow, SQL tasks often sit in the main ELT position:

* Upstream loads data into the Lakehouse.
* SQL tasks in the middle handle cleaning, joining, aggregation, and result output.
* Downstream provides these results to reports, analytics domains, application queries, or subsequent tasks.

If ELT is viewed as a continuously operating data production line, SQL tasks are usually the most common, most stable, and most reusable transformation unit.

## When to Use This

Typical scenarios well suited for SQL tasks through MCP include:

* Creating a temporary validation task to quickly run a SQL query.
* Adding parameters and execution configuration to an existing SQL task.
* Running a temporary execution before publishing to confirm results.
* Reading task instances and run state directly after execution.
* Chaining "write SQL," "save task," and "view run results" into a single continuous operation.

If your goal is to have the Agent participate in the most common and most stable Studio workflow, SQL tasks are usually the best starting point.

## How to Prompt the Agent

In SQL task scenarios, the more natural prompting style is not to reference a tool name directly, but to state the task goal, catalog location, and subsequent actions all at once.

If the catalog or whether a task already exists is not clear, explore first:

* Check the current catalog for any existing order daily report SQL tasks to reuse.
* Show me which catalogs are suitable for a temporary SQL task.

If the catalog and goal are confirmed, execute directly:

* Create a SQL task named `Order Daily Report Validation` in the `Temp Dev` catalog.
* Save the SQL I'm about to give you into that task.
* Read back the task details to confirm the content was saved.

If you want to continue pushing further, include the next steps:

* Turn the `biz_date` in this SQL into a parameter.
* Run it once temporarily with `biz_date=2026-06-12`.
* If the execution result is normal, publish it.

The key in these prompts is chaining "create," "save," "execute," and "publish" into a continuous task flow rather than stopping at a single step.

## What a Complete Workflow Includes

For a SQL task, MCP can handle the following actions end-to-end:

* Creating a SQL task
* Saving SQL content
* Saving task parameters
* Saving non-cron configuration
* Previewing the schedule
* Saving scheduling configuration
* Temporary task execution
* Reading task instance details

This means the Agent is not just generating a SQL text string — it can persist it into a Studio task object and continue pushing it to a runnable state.

## Creating and Saving the Task

A SQL task typically starts with creating a task in a specified catalog and then writing the SQL content.

This step is well suited for:

* Creating a one-time validation task
* Creating a parameterized template task
* Adding an experimental task to an existing catalog

After saving content, read back the task details to confirm:

* Task ID
* Task name
* Current content
* Catalog
* Studio link to open the task

The significance is that the SQL the Agent generates does not stay in the conversation — it becomes a task object that can continue to be managed.

## Parameterized SQL Tasks

SQL tasks are well suited for parameterization, for example:

* Querying by date
* Switching filter conditions by business definition
* Reusing the same task logic across different environments

Through MCP, you can save both:

* `${variable}` references in the SQL content
* The corresponding parameter definitions

At execution time, pass the actual values for that run separately.

This separates "task template" from "execution parameters":

* The template itself stays stable.
* Parameter values change based on the run scenario.

This is useful for day-to-day validation, scheduled runs, and cross-environment reuse.

## Non-Cron Configuration

After saving the SQL content, a layer of execution configuration usually needs to be added for the task to enter a more stable state.

Common non-cron configuration for SQL tasks includes:

* Retry count
* Retry interval
* Timeout
* Self-dependency
* Re-run strategy

These do not address "whether the SQL is correct" — they address "what happens if the task fails," "what to do if it runs too long," and "what constraints govern re-runs."

For tasks intended for long-term retention and repeated execution, add this configuration immediately after saving content.

## Scheduling Configuration

If a SQL task is not just for temporary validation but needs to become a scheduled task, scheduling configuration must be added.

The more reliable approach is:

* Preview the future trigger times for the cron expression.
* Confirm the schedule is as expected.
* Then save the scheduling configuration.

This prevents writing an incorrect scheduling plan directly into the task configuration.

For SQL tasks, this step is especially valuable because what many users actually care about is not "how to write cron" but "what time does this task actually trigger."

## Temporary Execution

Before deciding whether to publish, running a temporary execution first is usually more reliable.

Temporary execution is best for answering:

* Can this SQL run successfully right now?
* Does parameter expansion produce the expected result?
* Is the current VCluster and run environment available?
* How long does this run take roughly?

For SQL tasks, temporary execution is a very natural intermediate action:

* It is closer to actual run results than just reviewing SQL text.
* It is lighter and more validation-appropriate than publishing directly.

## Run Diagnosis

After a SQL task executes, MCP can return a set of structured results, including:

* `task_instance_id`
* Execution state
* Execution duration
* Execution parameters
* VCluster used
* Task instance details
* Link to the operations page

This lets the Agent handle the first round of run confirmation and the first round of investigation without requiring the user to manually look through the task instance list.

For many day-to-day SQL tasks, this is already enough to complete a minimum viable loop:

* Create
* Save
* Configure
* Execute
* Read back results

## Division of Labor with Python Tasks

In ELT, SQL tasks and Python tasks are not replacements for each other — they divide labor naturally.

Better suited to SQL tasks:

* Data transformation with clear rules
* Joins and aggregations between tables
* Metric computation
* Result table generation and periodic refresh

Better suited to Python tasks:

* Scripted logic that SQL cannot express directly
* File processing, API calls, and control flow
* Connector-based queries and writes
* ZettaPark DataFrame API-based data processing

From a collaboration perspective, the more common pattern is:

* SQL tasks handle ELT main-trunk transformations.
* Python tasks handle supplementary logic outside SQL.

Combining both types is more aligned with real data development workflows than emphasizing only one.

## Recommended Usage

A natural order for bringing SQL tasks into a regular MCP workflow:

* Have the Agent create or read the target SQL task.
* Have the Agent save the content and parameters.
* Add non-cron configuration and scheduling configuration.
* Trigger a temporary execution.
* Read back task instances and execution state.

The benefits:

* Every step has a structured result to read back.
* Well suited for temporary validation and pre-publish checks.
* Compresses many repetitive page-clicking actions into a single continuous conversation.

## Practical Value

For SQL tasks, the value MCP can most readily deliver falls into three areas:

* Moving SQL from conversation output to task objects
* Chaining parameters, configuration, execution, and diagnosis into a continuous workflow
* Reducing the cost of repeatedly switching between task catalogs, configuration panels, and operations pages

If your team is ready to start with one task type, SQL tasks are usually the easiest way to bring the Agent into the development workflow.

## Related Documents

- [Studio-Hosted MCP Server Setup Guide](studio-mcp-setup-guide.md) — How to complete the integration
- [Studio MCP Capabilities Overview](studio-mcp-capabilities-overview.md) — What objects this MCP can cover
- [Studio MCP Task Development and Run Diagnosis Guide](studio-mcp-task-development-and-diagnosis-guide.md) — Complete task development workflow
- [Studio MCP: Working with Python Tasks](studio-mcp-python-task-guide.md) — Python task development and validation
- [Studio MCP Best Practices](studio-mcp-best-practices.md) — Day-to-day usage principles
