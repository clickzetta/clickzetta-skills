# From PoC to Production: Analytics Agent Deployment Guide

Many enterprises have validated the demonstration value of Data Agents: users ask questions in natural language, the system automatically generates SQL, and returns charts and answers. But when moving from PoC to a production environment, the challenges change completely.

PoC focuses on "can it answer a question?"; production focuses on "can it reliably, consistently, controllably, and trustworthily serve real business users?"

Deploying Analytics Agent in production is not about attaching a chat box to a database — it's about organizing data, semantics, permissions, knowledge, models, and operational mechanisms so that the large model performs analysis within the enterprise's controllable boundaries.

Production Q&A accuracy is also not purely an SQL generation problem. Many errors are not because the model cannot write SQL, but because the system lacks sufficiently clear context: it doesn't know which entity the user is really asking about, it doesn't know which fact source to trust, it doesn't know if a metric definition is outdated, and it doesn't know what analysis process should be followed for certain question types.

Therefore, the focus of Analytics Agent deployment should shift from "can the model generate an answer" to "has the enterprise provided the Agent with the correct context, trusted fact sources, procedural analysis methods, and continuous validation mechanisms".

## Why Data Agents Often Stop at PoC

The PoC phase usually has several favorable conditions:

- Very small datasets with tables and fields pre-screened.
- Limited question scope, often around a few demonstration questions.
- The demonstrator knows the correct answers and how to follow up.
- Permissions and auditing are not main concerns.
- Errors can be explained in real time or manually corrected.

In production, these conditions no longer apply:

| PoC Environment | Production Environment |
| --- | --- |
| A few tables, limited fields | Thousands to tens of thousands of tables, complex and repetitive field naming |
| Fixed demonstration questions | Business users will ask a large number of open-ended questions |
| Definitions can be explained on the fly | Core metrics must be stable, consistent, and verifiable |
| Simple demonstration user permissions | Multi-department, multi-role, multi-region, multi-level permissions |
| Errors can be caught manually | Answers must be verifiable, traceable, and continuously improvable |
| Only looking at generation results | Also need to look at audit, export, task runs, and feedback loops |

Therefore, the key to Data Agents moving into production is not a single improvement in model capability, but whether the product provides a complete production-grade mechanism.

## Why Production Accuracy Is Difficult

Common accuracy problems with Data Agents in production environments can generally be classified into three types.

### Entity and Field Ambiguity

When users say "customer", "account", "order", "revenue", "active users", the system needs to know which tables, fields, and metrics these terms correspond to in the current business domain. If multiple tables have similar fields, or the same field means different things in different business contexts, the model is prone to selecting the wrong field.

Analytics Agent reduces this ambiguity through analytics domains, field aliases, field descriptions, column types, field usage, recommended questions, and knowledge.

### Unclear Fact Sources

Enterprises commonly have multiple data sources coexisting: raw tables, wide tables, temporary tables, historical reports, Excel files, business documents, historical SQL. They are not all equally trustworthy, nor are they all equally current.

Production environments need to explicitly establish fact source priority:

| Fact Source | Usage Recommendation |
| --- | --- |
| Governed formal tables, metrics, and answer builders | Use as the priority source for production Q&A. |
| Knowledge documents added to analytics domains | Use for explaining business terminology, metric definitions, and analysis rules. |
| Files and temporary data | Suitable for ad hoc analysis or supplemental explanation; confirm data source and update method before going into production. |
| Historical SQL and historical Q&A | Can serve as reference for understanding business intent, but should not become standard definitions without review. |

Analytics Agent helps maintainers configure "what to trust" through analytics domain resource management, metrics, knowledge, and answer builders.

### Expired or Missing Context

Business rules, organizational structure, product names, metric definitions, and data tables all change. If knowledge and semantic configuration are not updated accordingly, the model may continue using old interpretations.

Production environments require continuous maintenance of:

- Whether tables and fields are still the versions currently used in the business.
- Whether metric definitions have changed.
- Whether knowledge documents are outdated.
- Whether SQL in answer builders still matches the latest table structure.
- Whether recommended questions still cover the current high-frequency business questions.
- Whether the typical question validation set is updated as the business changes.

This is also why Data Agents require ongoing operations after launch, rather than being configured once and left alone.

## What Capabilities Are Needed for Production Deployment

### 1. Clear Data Boundaries

Enterprises cannot let Agents freely choose among all tables. The more tables there are, the higher the probability the model will select the wrong table, join tables incorrectly, or use temporary tables.

Production environments need to first answer:

- Which business scenarios are suitable to be in the same analysis scope?
- Which tables are formal tables, and which are temporary, historical, or test tables?
- Should different departments use different analytics domains?
- After a user enters an analytics domain, which resources can the model use?

### 2. Stable Business Semantics

The model sees field names; business users speak business language. Without a semantic layer between them, the model can only guess.

Production environments need to maintain:

- Field aliases.
- Field descriptions.
- Column types.
- Field usage.
- Hidden fields.
- Commonly used derived fields.

When similar fields exist in one or multiple tables, field semantics are an important means of eliminating ambiguity.

### 3. Controllable Metric Definitions

Core metrics cannot be freely generated by the model each time. Otherwise, the same "active users", "revenue", and "conversion rate" might be calculated differently in different questions.

Production environments need to solidify high-frequency metrics into:

- Metric definitions.
- Business knowledge.
- Answer builders.
- Standard SQL templates.
- Typical question validation sets.

### 4. Permission and Security Boundaries

In enterprise analysis scenarios, users' concerns are not just "can they log in" — they also include:

- Can they enter a specific analytics domain?
- Can they see a specific table, file, or metric?
- Can they see specific rows?
- Can they see sensitive fields?
- Can they download full data?
- Are their operations audited?

Permission governance is the baseline capability for Data Agent production readiness.

### 5. Verifiable Answers

Business users can look at conclusions directly, but production environments cannot rely solely on conclusions. Key answers need to be reviewable by BI analysts or maintainers.

Production environments need to provide:

- SQL viewing.
- Execution logs.
- Data and exploration entry points.
- Typical question validation.
- Q&A accuracy troubleshooting paths.

During validation, distinguish between two types of issues:

| Validation Target | Description |
| --- | --- |
| Whether the result is correct | Whether numbers, charts, groupings, filters, and definitions meet expectations. |
| Whether the generation process is correct | Whether the correct tables, fields, metrics, knowledge, answer builders, and permission scope were selected. |

Looking only at the final answer is not enough. Production validation should simultaneously look at the answer, SQL, logs, matched knowledge, and data scope used.

### 6. Feedback and Fix Loop

In production environments, answers cannot always be correct. The key is whether an error can enter a governance process after it occurs.

You need to define:

- How business users provide feedback.
- Who is responsible for handling feedback.
- Whether feedback should be addressed in field semantics, metrics, knowledge, answer builders, or permission configuration.
- How to validate after fixing.
- Whether configuration changes can be tracked.

Feedback should not just record "got it wrong". High-quality feedback should include:

- What was the original user question.
- What is the expected answer or correct definition.
- Whether the current answer is wrong in terms of numbers, fields, filters, groupings, explanations, or permission scope.
- Whether there is a reference standard report, metric definition, or business document.

Maintainers then convert feedback into improvements to field semantics, metrics, knowledge, answer builders, permissions, or analytics domain boundaries.

### 7. Runtime and Operations Mechanisms

Production environments are not just Q&A — there are also imports, parsing, scheduled tasks, chart refresh, exports, and configuration changes.

You need visibility into:

- Whether background tasks succeeded.
- Whether file or table imports failed.
- Whether scheduled tasks executed as planned.
- Whether task results were sent.
- Who modified configuration.
- Who exported data.

### 8. Scalable Organization Methods

If an enterprise has tens of thousands of tables, hundreds of business departments, and thousands of users, you cannot put all tables and users into one large "catch-all" analytics domain.

Production environments need to organize analytics domains by business topic, organizational boundaries, permission boundaries, and metric definitions. Analytics domains should serve as the first layer of governance boundary, layered with role authorization, resource permissions, row-level permissions, field hiding, and auditing.

## How Analytics Agent Solves These Problems

| Production Problem | Analytics Agent's Solution |
| --- | --- |
| Uncontrolled data scope | Use analytics domains to define business boundaries, letting the model only use data, knowledge, metrics, and answer builders within the current domain. |
| Table and field ambiguity | Use field semantics, aliases, descriptions, column types, and field usage to help the model select the right fields. |
| Repeated derived definitions | Use virtual columns to solidify commonly used derived fields, reducing repeated explanation and ad hoc calculation. |
| Unstable metric definitions | Use metrics, knowledge, and answer builders to lock in standard definitions. |
| Unstable complex analysis | Use answer builders to handle complex JOINs, fixed SQL logic, and standard output structures. |
| Permission risks | Use role authorization, analytics domain resource permissions, row-level permissions, field hiding, and full download permissions to control access and export. |
| Unverifiable answers | Support BI analyst review through SQL, logs, data, and exploration capabilities. |
| Cannot close error loop | Form an improvement loop using feedback, audit logs, validation checklists, and accuracy troubleshooting. |
| Production operations not visible | Support operations using notifications, scheduled tasks, execution logs, and audit logs. |
| Uncontrollable model connections | Uniformly manage model connections, routing, calls, and usage through AI Gateway. |

In one sentence:

Analytics Agent does not let a large model directly access all enterprise data — it constrains and enhances the large model into a production-ready enterprise analysis Agent through analytics domains, semantic layers, metric definitions, knowledge, answer builders, permission governance, and audit mechanisms.

## Recommended Deployment Path

### Phase 1: Sample Validation

The goal is to help users understand product capabilities, not to validate production readiness.

Recommendations:

- Use sample analytics domains to experience natural language Q&A.
- Experience charts, tables, follow-up questions, and saving to dashboards.
- Observe how the system generates recommended questions and analysis results.
- Do not equate sample performance with production performance.

### Phase 2: Select a Real but Clearly Bounded Pilot Scenario

Do not try to cover all departments and all data at the start.

Scenarios suitable for piloting typically have:

- A manageable number of data tables.
- Relatively clear metric definitions.
- Business users with high-frequency data inquiry needs.
- A BI analyst or data maintainer available for validation.
- Controllable permission scope.

### Phase 3: Plan Analytics Domains

Plan analytics domains first, then add data.

Recommended segmentation dimensions:

- Business topic.
- Department boundaries.
- Permission boundaries.
- Metric definitions.
- Data sensitivity.
- Q&A complexity.

Bigger is not better for analytics domains. Clearer boundaries mean more stable model data selection, easier permission governance, and simpler troubleshooting.

### Phase 4: Configure the Semantic Layer

Configure for the pilot scenario:

- Table and field descriptions.
- Field aliases.
- Column types and field usage.
- Hide sensitive fields.
- Virtual columns.
- Metrics.
- Knowledge.
- Answer builders.

The goal of configuration is not to "explain every field" — prioritize solving high-frequency questions, similar fields, core metrics, and easily misunderstood business terms.

At the same time, establish "fact source" rules:

- Which tables are formal production tables.
- Which metrics are standard definitions.
- Which knowledge documents are currently valid.
- Which historical SQL is for reference only and should not be directly reused.
- Which files are for temporary analysis only and should not serve as long-term fact sources.

This reduces the space for the model to make its own judgments among multiple similar sources.

### Phase 5: Configure Permissions and Governance

Before launch, at minimum confirm:

- Who can enter the analytics domain.
- Who can view or edit domain resources.
- Whether row-level permissions are needed.
- Whether sensitive fields need to be hidden.
- Who can download full data.
- Whether administrators can view audit logs.

### Phase 6: Validate with Typical Questions

Do not only ask one demonstration question. Build a typical question set covering:

- Looking up numbers.
- Comparisons.
- Trends.
- Rankings.
- Proportions.
- Details.
- Anomalies.
- Attribution.
- Permission boundaries.
- Sensitive fields.

Validate each question's answer, chart, SQL, logs, and permission results to confirm they meet expectations.

A typical question set is recommended to have two layers:

| Question Set | Purpose |
| --- | --- |
| Launch qualification question set | Must pass before launch, covering core metrics, core dimensions, permission boundaries, and high-frequency business questions. |
| Regression validation question set | Re-validate after configuration changes, table structure changes, metric adjustments, or knowledge updates. |

If possible, preserve the data timestamp, expected answer, and judgment basis at validation time. Otherwise, after data changes daily, it becomes difficult to determine whether the system answered incorrectly or the underlying data changed.

### Phase 7: Small-Scale Business Rollout

First let a small number of real business users use the system and ask them to submit feedback.

Key observations:

- Whether users can naturally ask questions.
- Whether recommended questions are helpful.
- Whether field misselection occurs frequently.
- Whether there are definition disputes.
- Whether dashboards and scheduled tasks can consolidate high-frequency needs.

### Phase 8: Continuous Operations

After production launch, continuously maintain:

- Whether new business tables need to be added to analytics domains.
- Whether new fields need semantic supplementation.
- Whether new metrics need to be solidified.
- Whether error feedback has been addressed.
- Whether audit logs show unusual modifications or exports.
- Whether scheduled tasks are running stably.
- Whether dashboards still meet business needs.

## Pre-Launch Checklist

| Check Item | Description |
| --- | --- |
| Are analytics domain boundaries clear? | Has the "catch-all" analytics domain been avoided? |
| Have core tables been screened? | Have temporary, test, and irrelevant tables been excluded? |
| Are fact sources clearly defined? | Is it known which tables, metrics, knowledge, and answer builders are trusted production sources? |
| Has data freshness been confirmed? | Are core tables and knowledge documents updating as expected? |
| Do field semantics cover key fields? | Have aliases, descriptions, types, and usage been supplemented? |
| Has ambiguity between similar fields been eliminated? | Can the model distinguish between similar fields? |
| Have metric definitions been solidified? | Are high-frequency metrics configured as metrics, knowledge, or answer builders? |
| Have permissions been validated? | Have test users been used to validate domain permissions, row-level permissions, and field hiding? |
| Is download controlled? | Have full download rights been granted only to necessary roles? |
| Have typical questions passed? | Do they cover looking up numbers, trends, comparisons, anomalies, and attribution scenarios? |
| Are SQL and logs reviewable? | Can BI analysts validate key answers? |
| Is the feedback loop defined? | Do users know how to report errors, and do maintainers know how to fix them? |
| Is auditing traceable? | Can key configuration changes and export records be viewed? |
| Is operational status visible? | Is it known where to check notifications, scheduled tasks, and execution logs? |
| Has a regression validation mechanism been established? | After configuration or data structure changes, will key questions be re-validated? |

## Common Misconceptions

### Misconception 1: Putting All Tables in One Analytics Domain

This exposes the model to too large a candidate pool, increasing the probability of selecting wrong tables, joining tables incorrectly, and complicating permission governance. A better approach is to split analytics domains by business topic and permission boundaries.

### Misconception 2: Relying Only on Model Capability, Not Configuring the Semantic Layer

Models can understand natural language, but cannot automatically know enterprise-internal fields, definitions, and terminology. Field semantics, metrics, knowledge, and answer builders are an important foundation for production quality.

### Misconception 3: Only Looking at Demonstration Questions, Not Doing Typical Question Validation

Demonstration questions passing does not mean production readiness. Before launch, build a typical question set and validate answers, SQL, charts, permissions, and logs.

### Misconception 4: Treating Historical SQL as Inherently Correct Fact Sources

Historical SQL can help understand business analysis habits, but it may be outdated or contain ad hoc definitions. Before going into production, maintainers should confirm whether it should be solidified into metrics, knowledge, or answer builders.

### Misconception 5: Training Business Users to Be Data Engineers

Do not require business users to memorize field names, table names, or SQL logic. The easier it is for business users to use the product, the better the backend semantic and governance configuration needs to be.

### Misconception 6: Ignoring Permission and Export Governance

Being able to ask for an answer does not mean being able to export details. Production environments should separately evaluate full download, field hiding, row-level permissions, and audit logs.

### Misconception 7: No Feedback and Operations Mechanism

Data Agent launch is not the end. Business changes, field changes, and definition changes all affect Q&A quality, requiring continuous operations.

## Related Documentation

- [Conversational Data Analytics (Analytics Agent)](datagpt_introduction.md)
- [Analytics Domain Planning Guide](datagpt-domain-planning-guide.md)
- [Configure Analytics Domain](datagpt-domain-management-guide.md)
- [Configure Field Semantics](datagpt-field-semantic-config-guide.md)
- [Metrics and Answer Builder](metrics_answer_build.md)
- [Answer Builder Best Practices](datagpt-answer-builder-best-practices.md)
- [Governance Overview](datagpt-governance-overview.md)
- [Validate Q&A Effectiveness](datagpt-domain-qa-validation-guide.md)
- [Analytics Domain Health Check and Launch Checklist](datagpt-domain-health-check-and-launch-checklist.md)
- [Troubleshooting Q&A Accuracy Issues](datagpt-qa-accuracy-troubleshooting-guide.md)
