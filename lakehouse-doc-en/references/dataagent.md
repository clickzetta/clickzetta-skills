## What is Data Agent

Data Agent is an AI-powered agent built on top of Singdata Lakehouse and Studio. It covers the full lifecycle of "development, operations, and governance" and implements intelligent platform upgrades through an Agentic AIOps philosophy — transforming data development from "people operating the platform" to "people directing the agent."

Data Agent is not just a tool that makes data teams more productive. It is a **data intelligence collaboration system** that enables everyone in the company to work with data.

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

For example:

* Show me what tables exist in the current schema
* What tasks do I currently have running

## Best Practice Scenarios

### Scenario 1: ETL Development

> **What engineers really say**: "I spend more time communicating and hunting down existing work than actually writing code."

**Communication overhead** Business requirements are naturally vague. A single request often takes 3–5 rounds of back-and-forth to align on metric definitions, time ranges, and filter conditions — most of the time goes to communication, not development. The root cause: translating "business language" into "development specs" is entirely manual.

**High cost of understanding standards** Each business domain has its own layering rules, naming conventions, and field standards, scattered across various documents. Engineers must "catch up" before taking on any new requirement, and even minor oversights get flagged in reviews, keeping rework costs high.

> Example prompt:
> I need to design a Medallion architecture data warehouse based on this metric requirements spec to support GMV analysis. I've already planned the tables for each layer: [Bronze layer] xxx [Silver layer] xxx [Gold layer] xxx. Based on this table list, please generate a data warehouse modeling standards document.

![](/.topwrite/assets/image_1779715425568.png)

### Scenario 2: Ad-hoc Data Retrieval

**Everything waits in the queue** Exploratory analysis, market research, and other ad-hoc requests are naturally lower priority and get perpetually pushed aside by formal requests. By the time the data finally arrives, the decision window has often closed and the business has already fallen behind the market. The core problem: ad-hoc analysis has no self-service path — it must go through the data team, which simply doesn't have the bandwidth to continuously handle low-priority requests.

> Example prompt:
> Query brazilianecommerce.olist_orders and count orders by day.

![](/.topwrite/assets/image_1779715858474.png)

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

![](/.topwrite/assets/image_1779715663695.png)
