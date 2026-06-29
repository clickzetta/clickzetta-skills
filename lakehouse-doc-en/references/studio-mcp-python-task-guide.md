# Studio MCP: Working with Python Tasks

In an ELT workflow, SQL handles the main data transformation work, but some steps are not well suited for SQL — file processing, external API calls, scripted pre-processing, and tasks involving control flow. That work typically falls to Python tasks.

The Studio-hosted MCP Server can independently complete the core workflow for Python tasks. For script validation, lightweight data processing, and task prototype development, you can ask the Agent directly to create a Python task in Studio, write code, trigger execution, and read back run results.

The point of this is not to treat the Agent as a pure code generator — it is to bring it into the task development and validation workflow.

In the context of ELT, Python tasks are well suited for logic that SQL cannot express directly: scripted data processing, external API calls, file I/O, lightweight control flow, and task prototype experiments.

In the Lakehouse, Python tasks are not just "running a generic Python script." They can work with two native capabilities for handling Lakehouse data:

* **Python Connector**: suited for executing fixed SQL queries, scripted reads and writes, or accessing the Lakehouse via SQLAlchemy or PEP 249.
* **ZettaPark DataFrame API**: suited for processing data in a DataFrame style similar to PySpark, where the system translates DataFrame logic into SQL to execute in the Lakehouse.

## When to Use This

Typical scenarios well suited for Python tasks through MCP include:

* Creating a temporary Python task for quick validation.
* Having the Agent write Python code directly into a Studio task.
* Triggering an execution immediately after a script is saved.
* Reading task instances and run state directly after execution.
* Using a Python task to handle a lightweight data processing step or build a development prototype.

If your goal is to have the Agent not just "suggest code" but actually participate in creating and validating task objects, Python tasks are a good starting point.

## How to Prompt the Agent

In Python task scenarios, specify the task catalog, task goal, and the technical path you want to use all at once when prompting.

If you have not yet decided whether to create a new task, or have not decided between SQL and Python, explore first:

* Check the current catalog for any existing order cleaning tasks to reuse.
* I want to build an order data cleaning task — help me decide whether SQL or Python is more suitable.

If the catalog, task type, and technical path are confirmed, execute directly:

* Create a Python task named `Order Cleaning Script Validation` in the `Temp Dev` catalog.
* Write a script using the Python Connector to query `public.orders` and save it to this task.
* Write a ZettaPark DataFrame API script draft to aggregate order data by day and save it to this task.

If you already have the code:

* Save the Python script I'm about to give you to that task.
* After saving, run it once temporarily to see if it works.

The most helpful information here is usually:

* Which catalog the task should be in
* Whether the task is for querying, cleaning, or prototype validation
* Whether to use the Python Connector or ZettaPark DataFrame API

This helps the Agent align with the development path you actually want.

## Actions Suited for MCP End-to-End

For Python tasks, MCP can handle the following actions end-to-end:

* Creating a Python task
* Saving Python code based on the Python Connector or ZettaPark
* Saving basic execution configuration
* Triggering a temporary execution
* Reading task instance details

This lets the Agent chain "write code" with "run and validate" into a continuous workflow rather than stopping at handing you an undeployed script.

## Creating and Saving the Task

Python tasks typically start with a new task in a catalog.

After creating the task, the Agent can write Python code directly into the task content and then read back the task details to confirm:

* Task ID
* Task name
* Current code content
* Catalog
* Studio link to open the task

This matters because it moves from "generated code" to "generated and saved task object." For Python tasks that need repeated modification and validation, this has more practical value than just providing code snippets in the conversation.

## Python Connector vs. ZettaPark DataFrame API

Use the **Python Connector** path when your Python task mainly:

* Executes a set of fixed SQL queries
* Does scripted reads and writes
* Accesses the Lakehouse or an external database through a connection object

Use the **ZettaPark DataFrame API** path when your Python task mainly:

* Organizes transformation logic in a DataFrame style
* Does multi-step cleaning, joining, and aggregation
* Needs to keep a development style similar to PySpark
* Uses Python for control flow while letting the Lakehouse handle distributed execution

A simple way to remember:

* **Python Connector** is "calling a database from inside Python."
* **ZettaPark** is "writing DataFrames in Python, then handing them to the Lakehouse to execute."

## What Saving Code Means

Once code is saved into a task object, many subsequent actions can continue around the same object:

* Continue modifying the code
* Adjust basic execution configuration
* Execute directly
* Review task instances

This lets the Agent participate in a more complete development workflow rather than generating a new script from scratch each time.

## Basic Execution Configuration

Python tasks need a layer of basic execution configuration in addition to code content.

This configuration controls the task's run behavior, including:

* Retry count
* Retry interval
* Timeout
* Re-run strategy

These determine how the script behaves as a task object, not whether the script itself is correct.

For temporary validation tasks, this configuration can stay minimal. For Python tasks intended for long-term retention, add the basic configuration after saving the code.

## Temporary Execution

One of the most valuable actions for a Python task is running a temporary execution immediately after saving.

This step is best for answering:

* Can the code run successfully?
* Is the current run environment available?
* How long will the script approximately take?
* Has the current task object entered a verifiable state?

Compared to just reviewing the script content, temporary execution exposes problems faster and lets the Agent collect structured run results directly.

## Run Diagnosis

After a Python task executes, MCP can return directly:

* `task_instance_id`
* Execution state
* Execution duration
* VCluster used
* Task instance details
* Link to the operations page

This means the Agent is not just responsible for "submitting code" — it can also "collect the results of that execution."

For many prototype development and temporary script tasks, this already delivers a complete, valuable loop:

* Create task
* Write code based on Connector or ZettaPark
* Trigger execution
* Read back state

## How to Bring Python Tasks into Daily Workflows

A natural order for bringing Python tasks into a regular MCP workflow:

* Have the Agent create a temporary task.
* Have the Agent write an initial version of the script.
* Save the basic execution configuration.
* Trigger a temporary execution.
* Read the task instance and execution state.

This approach is well suited for starting small:

* Running a script validation
* Running a lightweight data processing experiment
* Having the Agent quickly build a task prototype

Once this workflow is running smoothly, gradually extend to more stable, longer-term Python task management.

## Practical Value

For Python tasks, the value MCP can most readily deliver falls into three areas:

* Writing Python code directly into a task object
* Chaining code saving and execution validation into a continuous action
* Having the Agent return task instances and run state directly after execution

This makes Python tasks not just "support a script type," but a real entry point for the Agent to participate in task development.

If your team needs both SQL main-trunk transformations and some scripted processing in an ELT flow, Python tasks and SQL tasks form a natural division of labor:

* SQL tasks handle steps with clear rules and in-database transformations.
* Python tasks handle Connector queries, ZettaPark DataFrame processing, and scripted logic that SQL cannot express directly.

## Related Documents

- [Studio-Hosted MCP Server Setup Guide](studio-mcp-setup-guide.md) — How to complete the integration
- [Studio MCP Capabilities Overview](studio-mcp-capabilities-overview.md) — What objects this MCP can cover
- [Studio MCP Task Development and Run Diagnosis Guide](studio-mcp-task-development-and-diagnosis-guide.md) — Complete task development workflow
- [Studio MCP: Working with SQL Tasks](studio-mcp-sql-task-guide.md) — SQL task development and validation
- [ZettaPark Guide](LakehousePython-zettapark.md) — ZettaPark DataFrame API details
- [Studio MCP Best Practices](studio-mcp-best-practices.md) — Day-to-day usage principles
