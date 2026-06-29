## What is Data Engineering Agent

Data Engineering Agent is an AI-powered agent built on top of Singdata Lakehouse and Studio. It covers the full lifecycle of "development, operations, and governance" and implements intelligent platform upgrades through an Agentic AIOps philosophy — transforming data development from "people operating the platform" to "people directing the agent."

Data Agent is not just a tool that makes data teams more productive. It is a **data intelligence collaboration system** that enables everyone in the company to work with data.

![](.topwrite/assets/data-engineering-agent.svg)

^

## User Value

* **Higher productivity: reclaim 80% of your time for what truly matters**

From "3 days finding data, 2 days doing analysis" to "30 seconds to get data, 4 days of deep insight" — data engineers stop doing repetitive grunt work and focus on architecture design; data analysts stop pulling data and focus on business insights; business users go from waiting for reports to self-service analysis and real-time decision-making.

* **Expanded capabilities: do what you always wanted but couldn't**

Before: business users who wanted to analyze data had to depend on data engineers or analysts' schedules, waiting for data to be delivered before any analysis could begin. In exploratory analysis scenarios especially, the metrics and approach often shift constantly — by the time the data arrives, the metrics may already be obsolete.

Now: business users can create tasks and analyze data just by saying what they need — operations staff without SQL knowledge can build daily report tasks themselves, product managers without coding skills can create user analysis workflows, sales teams without technical backgrounds can generate performance dashboards. The data platform shifts from "requires specialized skills to use effectively" to "basic familiarity is enough to get full value," lowering the technical barrier.

* **Lower learning curve: get up to speed on a new data platform with ease**

You only need to focus on your goal. There's no need to learn complex product operations or underlying concepts — just ask in natural language and the agent handles the rest.

## How to Access

Click "Data Agent" at the top of the menu bar to open the feature.

Describe your needs directly to the agent in natural language and let it operate the platform for you.

![](/.topwrite/assets/DataAgent_1780918584053.svg)

For example:

* Show me what tables exist in the current schema
* What tasks do I currently have running

## Best Practice Scenarios

### Scenario 1: ETL Development

> **What engineers really say**: "I spend more time communicating and hunting down existing work than actually writing code."

**Communication overhead** Business requirements are naturally vague. A single request often takes 3–5 rounds of back-and-forth to align on metric definitions, time ranges, and filter conditions — most of the time goes to communication, not development. The root cause: translating "business language" into "development specs" is entirely manual.

**High cost of understanding standards** Each business domain has its own layering rules, naming conventions, and field standards, scattered across various documents. Engineers must "catch up" before taking on any new requirement, and even minor oversights get flagged in reviews, keeping rework costs high.

> Example prompt:
> I need to design a Medallion architecture data warehouse based on this metric requirements spec to support GMV analysis. I've already planned the tables for each layer: \[Bronze layer] xxx \[Silver layer] xxx \[Gold layer] xxx. Based on this table list, please generate a data warehouse modeling standards document.

^

### Scenario 2: Ad-hoc Data Retrieval

**Everything waits in the queue** Exploratory analysis, market research, and other ad-hoc requests are naturally lower priority and get perpetually pushed aside by formal requests. By the time the data finally arrives, the decision window has often closed and the business has already fallen behind the market. The core problem: ad-hoc analysis has no self-service path — it must go through the data team, which simply doesn't have the bandwidth to continuously handle low-priority requests.

> Example prompt:
> Query brazilianecommerce.olist\_orders and count orders by day.

^

### Scenario 3: Day-to-day Operations

Daily task operations are the most critical routine work on an enterprise data platform. Operations teams must continuously track the execution status of daily scheduled tasks and respond quickly when tasks fail or are delayed — rapidly identifying root causes, fixing tasks, and preventing failures from cascading down the dependency chain to affect business operations.

**Hard to get a full picture of tasks** The platform currently lacks an operations dashboard, so operations staff can only manually filter through lists one dimension at a time. Even with a dashboard, flexible and varied reporting needs are hard to meet. For example:

* Wanting to see "failure status of tasks containing a certain keyword" — the dashboard can't support this
* Wanting to know "which task types had the highest failure rate in the past week" — requires manually exporting data and then analyzing it
* Wanting to count "the number of unpublished SQL tasks under a specific owner" — multi-condition combinations can only be done by manually filtering one by one

**No clear path when instances fail** After discovering a failed instance, the logs don't explain the root cause; once the root cause is understood, it's unclear how to fix it. You end up asking around, the fix cycle drags on, and the business impact continues.

**Uncontrollable blast radius, chain reactions** When an upstream task fails, the chain reaction often spreads quickly, with large numbers of downstream tasks becoming blocked or failing. The platform provides a task lineage feature, but it's severely inefficient in urgent failure scenarios:

* **Cumbersome path**: requires logging into Studio → locating the task → opening the lineage graph → manually expanding layer by layer — multiple steps just to see the full chain
* **No quantification**: only a visual dependency graph, with no way to directly get key numbers like "how many downstream tasks were affected" or "how many levels were impacted"
* **Poor timeliness**: during early-morning alerts and emergency fixes, the cumbersome query steps waste precious response time that's already in short supply

> Example prompts:
> Please help me analyze which instances failed in the past week.
> For the task with instance ID xxx, what was the failure reason and which downstream tasks were affected?

^

### Scenario 4: Studio Task Development and Management

Studio tasks are the core scheduling unit of the Lakehouse data pipeline, but traditional management is cumbersome: creating a task requires entering the IDE and configuring step by step, modifying a schedule requires locating the task and opening the schedule panel, and dependency configuration requires manually maintaining task IDs.

Data Agent operates the full lifecycle of Studio tasks directly through natural language:

* **Create tasks**: describe the task logic, and the agent automatically generates SQL or Python code, creates the task, and configures the Virtual Cluster
* **Schedule configuration**: tell the agent "run at 2 AM every day" and it automatically converts this to a cron expression and applies it
* **Dependency orchestration**: describe the dependencies between tasks, and the agent automatically configures upstream and downstream dependency chains, avoiding manual task ID lookups
* **Batch operations**: publish multiple tasks or bulk-update the retry strategy for a category of tasks in a single instruction

> Example prompt:
> Create a Python task that runs at 3 AM every day, triggers after the ods\_order\_load task completes, and aggregates yesterday's order data into dws\_order\_daily.

### Scenario 5: Data Source Management

Onboarding enterprise data is the first mile of data engineering, involving connection configuration, sync strategy, status monitoring, and more — manual operations are error-prone and hard to track.

Data Agent supports the following data source management operations:

* **Quick onboarding**: describe the database type and connection details, and the agent automatically creates the data source and tests connectivity
* **Sync configuration**: specify the source and target tables, and the agent selects a full or incremental (CDC) sync strategy based on business needs
* **Status queries**: ask in a single sentence to get sync delays, recent failure records, and data volume statistics for all data sources
* **Troubleshooting**: when a sync task fails, the agent automatically pulls error logs, analyzes the root cause, and recommends fix steps

> Example prompt:
> Help me check which data sources currently have sync delays exceeding 30 minutes, and which ones had sync failures in the last 24 hours.

^
