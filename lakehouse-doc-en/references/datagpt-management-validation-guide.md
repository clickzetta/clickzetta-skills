# How Administrators Validate That Analytics Agent Configuration Is Production-Ready

A common challenge for administrators in Analytics Agent is knowing how to judge whether work on analytics domains, field semantics, metrics, knowledge, Answer Builders, permissions, and audit is sufficient to support real business use.

Simply checking "are all configuration fields filled in" cannot answer this question. The goal of Analytics Agent is not to complete back-end configuration — it is to give business users stable, trustworthy answers through natural language. Therefore, evaluating administrative work is better anchored to a set of repeatable business questions rather than a configuration-completeness checklist:

- Can business users ask the high-frequency questions they need?
- Will the system misinterpret key business terms?
- Can complex questions be handled consistently?
- Are the data boundaries each role sees correct?
- Can key answers be verified, traced, and continuously improved?

This guide focuses not on "how to configure" but on "how to verify that the current configuration is production-ready." It helps administrators accomplish two things:

- Build a repeatable acceptance method.
- Judge whether the current analytics domain is still at the demo stage or is close to production-ready.

## Why Use Questions to Validate Administrative Work

The front-end experience of Analytics Agent is Q&A; the back-end is governance. Business users will not evaluate the system against your configuration checklist — they will evaluate it against these criteria:

- Can they ask their questions?
- Are the answers accurate?
- Is the system consistent?
- Are the permissions correct?
- Can problems be traced and resolved?

This means whether administrative work is production-ready is better validated through real business questions in reverse, rather than by going through back-end fields one by one.

Validation typically follows this chain:

```text
Business question
→ Is the answer, chart, or table correct?
→ Did the SQL, records, knowledge, metrics, and Answer Builder hit the right targets?
→ Have the analytics domain, field semantics, permissions, and definition configuration absorbed the question?
```

If this chain cannot be completed, the current administrative work is not yet sufficient to support stable business use. If it can be completed consistently, the analytics domain is closer to having a clear basis for a production launch decision.

## What Administrators Are Validating

Administrators are not validating "how smart is the model" — they are validating whether the current analytics domain has the five categories of capability needed for production use.

| Capability to validate | Validation focus | Corresponding administrative work |
| --- | --- | --- |
| Question absorption | Can high-frequency business questions be asked directly? | Domain planning, table inclusion scope, recommended questions |
| Semantic absorption | Does the system understand business terms rather than misselecting fields? | Field semantics, knowledge, field hiding, field purpose |
| Definition absorption | Are core metrics and complex analyses consistent? | Metrics, Answer Builders, table relationships, knowledge |
| Permission absorption | Does each user see data within the correct boundaries? | Role grants, domain permissions, row-level permissions, field hiding |
| Operational absorption | Can questions be verified, traced, and fixed? | SQL, records, feedback, audit, validation question set |

These five capabilities together determine whether an analytics domain is closer to "demo-ready" or already ready for sustained business use.

## Build a Fixed Validation Question Set First

If administrators generate test questions ad hoc each time, it is hard to compare configuration quality across different points in time. A more reliable approach is to build a fixed validation question set for each analytics domain.

Prepare at least four categories of questions per analytics domain.

### High-Frequency Questions

Used to verify whether the primary business value of this analytics domain has been established.

Examples:

- `How many active accounts are currently on the Basic plan?`
- `How many new customers were added per channel in the last 30 days?`
- `Show the current active rate by subscription plan.`

If these questions cannot be answered consistently, this usually means the domain scope, field semantics, or baseline metric preparation is insufficient.

### Ambiguous Questions

Used to verify that the system can distinguish key business terms and does not make wrong selections among similar fields or similar definitions.

Examples:

- `Using the active account definition, show the active rate by plan.`
- `Show the trend for the last three months using the finance-confirmed revenue definition.`
- `Customer count here means paying customers — show by region.`

If these questions frequently drift to the wrong answer, this usually means field aliases, field descriptions, knowledge, and metric definitions are not yet absorbing the business language well enough.

### Complex Questions

Used to verify whether multi-metric, multi-condition, multi-table, or fixed analytical logic scenarios already have a standard way to handle them.

Examples:

- `For the Google channel only, show active rate and active seats by plan.`
- `Show new customers, converted customers, and renewed customers by month.`
- `Show an account health overview by channel and plan.`

If these questions are inconsistent, the priority is usually to revisit Answer Builders, table relationships, and complex definition design.

### Permission Questions

Used to verify whether the data boundaries for different roles and scopes are correct.

Examples:

- `For the same question, do a regional manager and a headquarters manager see different data ranges?`
- `Do business users fail to see sensitive fields?`
- `Can a user only access the analytics domains they have permission for?`

These questions must be validated separately with different role accounts — they cannot be judged using only an admin account.

## Standards for Judging "Production-Ready"

Validation is not just checking "was it answered?" — it requires a layer-by-layer judgment.

### Layer 1: Can the question be asked directly?

Administrators should first check whether business users can ask the question in business language without needing to know underlying field names, table names, or SQL logic.

If a high-frequency question can only be answered correctly when rewritten in highly technical terms, this usually means:

- Analytics domain boundaries are unclear.
- Recommended questions are not serving their guidance function.
- Field alias, field description, or knowledge configuration is insufficient.

In these cases, the right response is to revisit semantic and governance preparation — not to attribute the cause primarily to business users not knowing how to ask questions.

### Layer 2: Does the system answer incorrectly?

Incorrect answers typically manifest as:

- Wrong numbers.
- Missing filter conditions.
- Wrong grouping fields.
- Wrong time field used.
- Wrong definition applied.

This usually means:

- Insufficient field semantics.
- Metrics and knowledge not sufficiently fixed.
- Answer Builders not handling complex scenarios.
- Unreasonable table relationship or field purpose configuration.

If high-frequency questions are frequently answered incorrectly, the current administrative work has not moved from "data is accessible" to "results can be delivered consistently."

### Layer 3: Are complex questions consistent?

The maturity of an analytics domain is measured not only by whether simple questions can be answered, but also by whether complex questions have a standard handling path.

If every complex question relies on the model constructing SQL from scratch each time, results tend to fluctuate. A stable state typically means:

- The correct Answer Builder is hit.
- Correct filters and dimensions are applied automatically.
- Expected metric combinations are returned consistently.
- Records show a standard hit path.

Passing this layer means the analytics domain is beginning to have more stable production handling capability.

### Layer 4: Are permissions not bleeding through?

This layer of validation is easy to overlook, but it directly determines whether the system can enter real business scenarios.

Key things to verify:

- Can different roles only access the analytics domains they are authorized for?
- Do row-level permissions actually narrow the result scope?
- Do hidden fields fail to appear in Q&A results and priority explanation paths?
- Are roles with and without export permissions correctly differentiated?

If results are correct but permission boundaries are wrong, administrative work still cannot be considered production-ready.

### Layer 5: Can results be verified?

An administrator's confidence in a launch decision comes from verifiability — not from an answer that looks reasonable.

Key questions should at minimum satisfy:

- The SQL can be viewed.
- The records can be viewed.
- It can be determined whether knowledge, metrics, or an Answer Builder was hit.
- It can be explained why the system gave this answer.

If the system provides a plausible-looking answer but there is no clear verification path, administrators will still find it hard to treat it as a business capability that can be delivered consistently.

## Validate in Four Steps

### Step 1: Accept high-frequency questions first

Select 5 to 10 questions that business users ask most often and that can least afford to be wrong. If these pass, the basic value of this analytics domain has started to take shape.

At this step, confirm:

- Can business users ask the question exactly as stated?
- Do these questions cover the main purpose of this domain?
- If these questions still cannot be answered consistently, is the right response to reduce the domain scope rather than continue adding more tables?

### Step 2: Accept ambiguous questions next

Design questions specifically for the most commonly confused business terms:

- Active accounts
- Revenue
- Customer count
- Valid orders
- New users

If these terms have multiple candidate interpretations across different tables, fields, or teams, you must verify the system selects the correct one.

This step is a better test of the quality of field semantics, knowledge, and metrics configuration.

### Step 3: Accept complex questions

Complex questions typically better reflect the maturity of administrative work.

If all complex questions in an analytics domain depend entirely on ad hoc reasoning, the system may seem usable but is hard to stabilize. Once complex questions are handled by Answer Builders, standard metrics, and relationship configuration, the domain is more suitable for opening to a broader set of business users.

### Step 4: Accept permission questions last

Walk through core questions with different role accounts — do not rely only on back-end configuration.

At minimum, verify:

- One admin account
- One ordinary business user account
- One account subject to row-level permission restrictions

The same question returning different results under different accounts is not necessarily wrong; the key is whether the difference matches the expected boundaries.

## What Evidence to Look At During Validation

Do not only look at the text answer. Administrators should look at several types of evidence together.

| Evidence | What to use it for |
| --- | --- |
| Final answer | Whether numbers, definition notes, and conclusions match expectations |
| Charts and tables | Whether groupings, sorting, and display structure fit the question |
| SQL statement | Whether tables, fields, filters, groupings, aggregations, and JOINs are correct |
| Records | Whether knowledge, metrics, or Answer Builders were hit; whether fallback occurred |
| Data and exploration | Whether the current analytics domain actually provides the data and metrics the question requires |
| Audit and feedback | Whether issues can be traced, fixed, and re-verified after they appear |

SQL and records are the more critical evidence, because administrative validation is concerned not just with "does the answer look correct" but also "why was this answer produced."

## How to Determine What to Fix Based on Observed Symptoms

The most common challenge for administrators is not spotting "there is a problem" — it is not knowing which layer to fix next.

The mapping table below can serve as a daily diagnostic framework.

| Observed symptom | More likely action to take |
| --- | --- |
| High-frequency questions cannot be asked at all | Revisit domain scope, recommended questions, whether correct tables are included |
| Users must say field names to get the right answer | Revisit field aliases, field descriptions, knowledge |
| The same business term is frequently misunderstood | Revisit field semantics, knowledge, metric naming and definitions |
| Simple metric questions have inconsistent definitions | Revisit metric configuration, metric aliases, knowledge |
| Complex questions return different results each time | Revisit Answer Builders, table relationships, output metric design |
| Multi-table questions show obvious duplication or inflation | Revisit JOIN relationships, table granularity, Answer Builder SQL |
| Some users can see results they should not see | Revisit role grants, domain permissions, row-level permissions, field hiding |
| Fixed questions recur after being fixed | Revisit whether a fixed validation question set, feedback loop, and regression validation are in place |

Without this "symptom to action" mapping, administrative work easily becomes scattered configuration patching with no clear sense of root cause or priority.

## When Is "Production-Ready"?

An analytics domain does not need to answer every question perfectly before launching. But it should meet at minimum the following conditions.

| Condition to meet before launch | Evaluation standard |
| --- | --- |
| High-frequency questions answered consistently | Core business questions have passed the fixed validation question set |
| Key business terms no longer drift noticeably | Core ambiguous questions have passed validation |
| Complex high-value questions have a standard handling path | At minimum, key complex questions have an Answer Builder or standard definition |
| Permission boundaries verified as correct | Validated with different role accounts |
| Key answers are verifiable | Answer sources can be explained through SQL and records |
| Issues can be closed | Feedback, fix, and regression validation mechanisms are in place |

If these conditions are not yet met, it is more appropriate to define the current phase as "pilot validation" or "PoC extension" rather than opening to a wider user base.

## Build a Continuous Validation Mechanism

Administrative work is not a one-time delivery. After an analytics domain launches, fields, knowledge, table structure, definitions, and permissions can all change, so validation should continue on an ongoing basis.

Maintain at least two question sets:

| Question set | Purpose |
| --- | --- |
| Launch acceptance question set | Determine whether an analytics domain is ready to open to business teams |
| Regression validation question set | Re-validate after each change to field semantics, metrics, knowledge, Answer Builders, or permissions |

Prioritize collecting the following for the regression validation question set:

- Questions that have produced errors in the past.
- Questions most prone to ambiguity.
- Highest-value questions.
- Questions with the most sensitive permission boundaries.

This allows administrators to gradually build a stable evaluation method rather than relying on judgment by instinct each time.

## The Measure of Administrative Work Is Questions Passing, Not Configuration Complete

This is the core judgment of this guide.

In Analytics Agent, an administrator's deliverable is not:

- How many analytics domains were built.
- How many field descriptions were filled in.
- How many metrics were configured.
- How many Answer Builders were created.

It is:

- Whether the questions business users ask most often can now be answered consistently.
- Whether key business definitions no longer drift.
- Whether complex questions have a standard handling path.
- Whether permission boundaries have been validated through Q&A.
- Whether there is a clear mechanism for fixing and re-verifying issues.

When administrative work can be continuously validated against these questions, administrators can more easily build a stable acceptance method and judge whether the current analytics domain is ready for production.

## Related Documentation

- [Validate Q&A Quality](datagpt-domain-qa-validation-guide.md) — how to design test questions and review SQL and records
- [Launch an Analytics Domain](datagpt-domain-health-check-and-launch-checklist.md) — health scan and pre-launch manual checks
- [Troubleshoot Q&A Accuracy Issues](datagpt-qa-accuracy-troubleshooting-guide.md) — trace the root cause from answer, SQL, and records
- [Governance Overview](datagpt-governance-overview.md) — analytics domains, permissions, audit, and governance boundaries
- [From PoC to Production: Analytics Agent Adoption Guide](datagpt-production-adoption-guide.md) — the path from pilot to production
