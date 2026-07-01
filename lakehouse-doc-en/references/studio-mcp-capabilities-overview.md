# Studio MCP Capabilities Overview

The Studio-hosted MCP Server gives AI Agents a set of Lakehouse and Studio operations they can call directly. It supports more than querying data and generating SQL — it also covers structured operations around task objects, run states, and complex data-engineering objects.

In terms of scope, these capabilities span several object layers:

* Lakehouse metadata and object browsing
* Studio catalogs, tasks, and task configuration
* Publishing, execution, instances, logs, and statistics
* Multi-table real-time sync, Data Integration, backfill, and task dependencies
* Flow orchestration, VCluster, knowledge retrieval, and some governance operations

In terms of usage, not all capabilities suit the same interaction style.

The more natural approach is usually:

* When objects are not yet clear, let the Agent do exploratory queries first.
* When objects are already clear, let the Agent perform structured execution.

For example, information such as catalogs, tasks, data sources, tables, and the most recent run state is better explored first. Creation, saving, execution, and publishing — where the catalog, task, parameters, and execution target are already confirmed — are better handled as direct execution.

## Environment and Metadata Capabilities

These capabilities are mainly used to confirm the current environment and the objects available for operations:

* Which region, Workspace, VCluster, and Schema the current connection points to
* Which data sources, Schemas, Tables, Views, and task objects exist in the current environment

Typical uses include:

* Checking which data sources are available
* Checking which Schemas are under a given data source
* Checking which tables are in `public`
* Surveying the environment before deciding which object to operate on next

These capabilities are naturally the best starting point for entering a Studio workflow with an Agent. Surveying the Workspace, data sources, and object scope first makes subsequent development and operations more reliable.

This layer is best suited for exploratory questions, such as:

* What catalogs, tasks, and data sources are currently available?
* Which catalog is better suited for a new experimental task?
* Which tables can serve as inputs for future sync or SQL modeling work?

In addition to data sources, Schemas, and Tables within the Workspace, this layer also covers Workspaces, namespaces, and some metadata objects — helping you confirm what you can currently operate on.

## Lakehouse Query and Object-Browsing Capabilities

Beyond viewing metadata, this MCP also supports direct Lakehouse queries and object browsing.

This part goes beyond listing objects. You can also:

* Execute Lakehouse queries
* Browse Schema-level objects
* Browse Workspace-level objects
* View functions, Dynamic Tables, External Tables, Materialized Views, VClusters, and other objects
* View object-level detail information

This means an Agent can start from the Studio task system, or from Lakehouse objects, and then connect the two.

## Studio Catalog and Task-Development Capabilities

These capabilities allow an Agent to participate directly in task development.

Typical operations covered include:

* Creating catalogs
* Creating tasks
* Reading task details
* Saving task content
* Reading and saving task configuration

For day-to-day development, this means the Agent is not just generating content in the conversation — it can also persist that content into real task objects, for example:

* Creating a new task in the appropriate catalog
* Writing SQL, Shell, Python, or JDBC content into a task
* Adding execution parameters, retry policies, and timeout settings to the configuration

This workflow is useful for bridging "generated content" with "saved Studio task objects," reducing the back-and-forth between conversation output and page-level objects.

These capabilities are generally best used as direct execution once the catalog and task object have been confirmed.

## Scheduling and Task-Configuration Capabilities

These capabilities move a task from "has content" to "has run constraints and scheduling semantics."

They cover more than cron, including:

* Retry policy
* Timeout policy
* Dependencies
* Execution VCluster and Schema
* Schedule preview
* Reading scheduling information from published tasks
* Non-cron execution configuration

For regular batch tasks, this layer determines whether the task meets the baseline requirements for going to production. The focus here is no longer the content itself, but scheduling, dependencies, execution environment, and run policies.

If you are not sure whether your task is missing parameters, non-cron configuration, or the schedule itself, this layer is also well suited for exploration before execution.

## Publishing and Execution Capabilities

These capabilities move an existing task into a runnable state and trigger actual execution.

Two actions need to be clearly distinguished here.

### Publish

Publishing means handing the task over to the scheduling system for management. It answers the question: "Is this task live and part of the official scheduling object set?"

### Execute

Execution means running the task once immediately. It answers the question: "Can this content run successfully right now, and what is the result and run state?"

These two actions serve different purposes:

* Publishing is oriented toward production management.
* Execution is oriented toward verification, debugging, and diagnosis.

If these two actions are conflated, users can easily mistake "publishing for running once" or "running once for going live."

This layer is therefore best used as direct execution once the object and intended action are clear. If you are not sure whether publishing is appropriate, having the Agent check the current state first is usually more reliable.

## Run-Diagnosis Capabilities

This set of capabilities is mainly used for quick diagnosis and investigation after a task has run.

Once a task has run, the Agent can go beyond "succeeded/failed" and drill further:

* Task instance details
* Attempt list
* Attempt logs
* Task-level run statistics
* Task run dependency relationships
* Information associated with a single run

It is well suited for chaining a diagnosis flow together, such as:

* First confirming whether the task instance was created successfully
* Then confirming how many attempts this run produced
* Then reading specific logs to see the actual execution content, execution duration, and underlying job identifiers

This set is especially well suited for:

* A quick post-execution self-check
* Locating failure points
* Narrowing down the investigation scope before returning to the page

These capabilities are naturally best suited for exploratory questions, because the first time a user enters an investigation scenario, they often do not know which instance or log entry to start from.

## Statistics, Dependencies, and Backfill Capabilities

Beyond viewing tasks and instances one by one, this MCP also provides tools with a management perspective for answering "What is the overall run status right now?"

These capabilities typically include:

* Task statistics
* Task run statistics
* Published task dependency relationships
* Task run dependency relationships
* Backfill tasks and backfill instances
* Creating backfill tasks with downstream impact scope

An Agent is therefore well suited not just for point operations, but also for doing an overall survey first and then moving into specific investigation.

## Data Integration and Real-Time Sync Capabilities

Data Integration and real-time sync are an important layer of objects in this capability set.

The Studio-hosted MCP Server supports not only regular code-type tasks, but also Data Integration and real-time sync tasks, including:

* Regular Data Integration tasks
* Multi-table real-time sync tasks
* Continuously running CDC task configuration
* Integration task configuration saving

These differ from regular batch tasks in several ways:

* The configuration structure is more complex.
* They depend more heavily on source, target, and mapping relationships.
* The run model is not "run once to completion" — it may run continuously.

This set of capabilities corresponds not just to "one more task type," but to a data engineering workflow that is closer to real-world practice.

For objects such as multi-table real-time sync, the focus is no longer on "writing code," but on organizing operations around the source, target, sync objects, startup mode, and continuous run state.

## Flow, Composite Tasks, and More-Complex Orchestration Capabilities

The Studio-hosted MCP Server also covers composite task capabilities, such as:

* Viewing a Flow DAG
* Creating and managing nodes
* Binding and unbinding node dependencies
* Viewing node details
* Saving node content and node configuration
* Submitting a Flow
* Viewing Flow node run status

It supports not just single task objects, but also more complex task-orchestration scenarios.

However, Flow objects inherently depend more on page semantics and node context. They are generally better introduced as an advanced capability rather than as an entry point for a first-time MCP integration.

## Data Quality and Governance-Assistance Capabilities

This MCP also covers some data quality and governance-assistance capabilities.

This typically includes:

* Data quality rule creation
* VCluster listing and creation
* Structured observation of tasks and run states
* Supporting governance and troubleshooting through logs, statistics, and dependency relationships

This does not equal a full governance system, but it can serve as a callable operations surface within a governance workflow.

## Knowledge, Skills, and Product-Knowledge Capabilities

This set of capabilities is easy to overlook, but it matters significantly for a continuous Agent work experience.

The Studio-hosted MCP Server is not just a collection of operations tools — it also integrates knowledge capabilities, including:

* Skill retrieval
* Skill documentation reading
* Product knowledge queries
* Manual knowledge writing and retrieval
* Analytics memory retrieval

With these capabilities, an Agent can consult platform-specific skills, knowledge, and memory before taking actions — making its operations more aligned with product semantics.

## Extended Object Capabilities

Beyond general catalog, task, execution, and log capabilities, the Studio-hosted MCP Server also provides tools for complex objects, such as:

* Semantic Views
* Dynamic Tables
* External Tables
* Materialized Views
* VClusters
* Connections and some run-environment objects
* Backfill task objects

It covers not just simple SQL tasks, but a wider range of Studio objects.

That said, these extended objects are generally more complex than regular SQL tasks and more dependent on context. They are better introduced gradually into daily use after the basic workflow has been mastered.

## How to Read This Capabilities Overview

When reading this overview, focus on three judgments:

* Which objects can already be handed to the Agent for structured operations?
* Which objects have tools available but are better used in combination with the page?
* Which capabilities are worth bringing into daily workflows first, and which are better introduced gradually as advanced capabilities?

If the goal is to start using these capabilities as quickly as possible, begin with catalogs, tasks, publishing, execution, logs, and statistics. If the goal is to bring the Agent into more complex data-engineering objects, continue extending to Data Integration, CDC, backfill, and Flow.

## MCP Capability Boundaries

From a usage perspective, this MCP is better suited for structured operations.

### Better suited to MCP

* Structured queries
* Structured creation and modification
* Chaining task object development, configuration, publishing, execution, and diagnosis into a callable workflow
* Having the Agent perform an informed operation first, then letting a person review it
* Surveying the environment, objects, and state first, then narrowing down what requires manual handling

### Better suited to the page

* Complex page configuration that requires heavy visual judgment
* Complex flow design that requires graphical drag-and-drop confirmation
* Large-scale information browsing that relies purely on human visual scanning

The more common combination is:

* Use MCP to quickly perform structured actions.
* Return to the page for visual confirmation and final adjustments.

## Recommended Starting Path

Work through the following steps progressively:

* Have the Agent survey the environment and metadata first.
* Have the Agent participate in catalog, task, and content-level development.
* Have the Agent participate in scheduling configuration, publishing, execution, and log investigation.
* Then gradually extend to more complex objects such as Data Integration, CDC, Flow, backfill, and data quality.

This approach gets the most value in place quickly while avoiding handing all complex objects to the Agent at the outset, which can distort expectations.

## Related Documents

- [Studio-Hosted MCP Server Setup Guide](studio-mcp-setup-guide.md) — How to complete the integration
- [Studio MCP Task Development and Run Diagnosis Guide](studio-mcp-task-development-and-diagnosis-guide.md) — The complete development workflow for SQL/Shell/Python tasks
- [Studio MCP: Working with Multi-Table Real-Time Sync Tasks](studio-mcp-cdc-realtime-sync-guide.md) — CDC task configuration and operations
- [Studio MCP: Working with Data Integration Tasks](studio-mcp-integration-task-guide.md) — Data Integration task configuration and execution
- [Studio MCP Best Practices](studio-mcp-best-practices.md) — Day-to-day usage principles
