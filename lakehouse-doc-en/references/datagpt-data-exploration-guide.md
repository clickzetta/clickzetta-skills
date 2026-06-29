# Using Data and Exploration

This guide is for business users, business analysts, and BI analysts. It explains how to use the "Data" and "Exploration" features on the analysis page, and how they relate to natural language Q&A and dashboards.

In the analytics domain page of the Analytics Agent, there are three tabs at the top:

- Analysis
- Data
- Exploration

"Analysis" is for natural language Q&A; "Data" is for understanding what data is available in the current analytics domain; "Exploration" is for structured data investigation around configured metrics and answer builders.

Ordinary business users can treat the "Data" tab as the data catalog for the current analytics domain to determine "what this domain can roughly answer". "Exploration" is better suited for BI analysts or business analysts to validate metric changes, do comparison analysis, and find drill-down directions.

## Applicable Users

- Business users: Confirm which business objects the current analytics domain covers; no need to memorize field names.
- Business analysts: Review the data scope of the analytics domain before asking questions, to reduce ambiguity.
- BI analysts: Use the Exploration feature to quickly view metric changes, comparison analysis, and drill-down dimensions.
- Semantic layer maintainers: Verify whether field semantics, metrics, and answer builders can be understood by business users.

## What the Data Tab Is For

The "Data" tab shows the data resources that have been added to the current analytics domain. It is not a full data modeling page or a back-end table configuration page — it is the data catalog entry point within the analytics domain.

In practice, after entering the "Data" tab, you can see the tables in the current analytics domain, for example:

```text
ns227206.public.accounts
quick_start.cat_litter.category_mapping
```

Clicking a table name expands the field list.

For example, expanding `ns227206.public.accounts` shows fields including:

```text
id
email
first_name
last_name
plan
source
seats
created_at
trial_ends_at
canceled_at
trial_converted
active_subscription
legacy_plan
latitude
longitude
country
account_name
```

Expanding `quick_start.cat_litter.category_mapping` shows more business-oriented fields and descriptions, such as:

```text
Competitor category master data
Level 1 category code
Level 1 category
Level 1 category description
Level 2 category code
Level 2 category
Level 2 category description
Level 3 category code
Level 3 category
Level 3 category description
Level 4 category code
Level 4 category
Level 4 category description
```

## Typical Uses of the Data Tab

### Confirming Available Data Before Asking

If you do not know what the current analytics domain can answer, first open the "Data" tab to see which business objects and information it covers.

For example, after seeing information related to plan, source, country, and active status, you can ask more specific questions:

```text
Show active account count by plan
```

```text
Compare active account count by source and country
```

```text
Count only active accounts, broken down by plan
```

Business users do not need to write `active_subscription = TRUE` as a raw field condition. The definition of active accounts should be configured by the domain maintainer through field semantics, metrics, or knowledge.

### Determining Whether a Question Is Outside the Current Domain

If you want to ask about "contract amount" but cannot see related tables or fields in the "Data" tab, it means the current analytics domain may not be suitable for answering this question.

In this case, you should:

- Switch to the correct analytics domain.
- Contact the domain maintainer to add the relevant data resources.
- Or ask the maintainer to add field semantics, metrics, and knowledge.

### Reducing Field Ambiguity

When multiple business time fields or business objects have similar meanings, first check in the "Data" tab what related information is available in the current domain.

For example, in an account analysis there may be:

- `created_at`
- `trial_ends_at`
- `canceled_at`

Business users can use business language to specify which time to use:

```text
Count monthly new accounts by account creation time
```

```text
View cancellation account trends by account cancellation time
```

This is more stable than simply asking "view trend over time". If BI analysts or maintainers need to investigate further, they can then confirm which specific field matches.

## Relationship Between the Data Tab and Permissions

The "Data" tab shows the data resources and fields visible to the current user in the current analytics domain.

If certain tables or fields are hidden, or the user does not have the relevant permissions, business users should not be able to bypass these restrictions through natural language Q&A.

Therefore, the "Data" tab also helps users understand:

- What data the current analytics domain covers.
- What fields the current user can see.
- Which questions might be outside the permission or domain scope.

## What the Exploration Tab Is For

The "Exploration" tab enters the data exploration page. It is not ordinary conversational Q&A — it is structured exploration around configured metrics and answer builders, primarily for BI analysts and business analysts.

In practice, after clicking "Exploration", the page URL becomes:

```text
/dataai/dataGPT/exploration/{domainId}
```

The page title is:

```text
Data Exploration
```

The left side shows explorable objects, for example:

```text
test_answer_builder_active_account_count_20260609
test_answer_builder_account_health_overview_20260609
Total Active Accounts
```

These objects come from the metrics or answer builders configured in the analytics domain.

## Main Areas of the Exploration Page

After selecting a metric or answer builder, the right side shows:

- Current exploration object name.
- Comparison analysis.
- Add.
- Global filter.
- Add.
- Query.
- Clear.

When no conditions are set, the page shows:

```text
Set conditions and query
```

This indicates the core usage of the exploration page: select a configured analysis object, set comparison conditions or global filters, and then query results. Ordinary business users do not need to understand how these objects are configured; if the exploration page does not have the object you want, contact a BI analyst or domain maintainer.

## Comparison Analysis

In practice, after selecting "Total Active Accounts" and clicking "Add" under "Comparison Analysis", the system automatically generated a comparison condition based on `created_at`:

```text
created_at
1 Baseline period filter
VS
Fixed time
2 Comparison period filter
```

This can be understood as:

- Baseline period: The current time range to observe.
- Comparison period: Another time range to compare against.
- VS: The two time periods are being compared.
- Fixed time: One way to set the comparison period.

This capability is suitable for analyzing:

- How much has the current period changed compared to the previous period.
- Whether a metric is growing or declining.
- Whether an anomaly occurred within a certain time window.

## Query Results

In practice, after clicking "Query", the exploration page returned a comparison result table and chart.

The result table contains:

```text
Name
Baseline period
Comparison period
Change
```

Example result:

```text
Total Active Accounts    3    1    200%
```

This means the metric value for the baseline period is 3, the comparison period value is 1, and the change is 200%.

The page also generates charts to display the comparison results.

## Auto Drill-Down Fields

After querying, the page shows fields that can be used for further breakdown.

In practice, visible fields include:

```text
plan
source
country
last_name
trial_ends_at
first_name
canceled_at
email
created_at
id
trial_converted
active_subscription
legacy_plan
```

These fields help analysts continue to determine "where the change comes from". For ordinary business users, these can be understood as the system's suggested breakdown directions.

For example, after comparing total active accounts, you can further explore:

- By plan: which plan changed the most.
- By source: which source changed the most.
- By country: which country changed the most.
- By active status.

In practice, the results below already showed a breakdown by `plan`:

```text
Basic       3    1    200%
Business    0    -    -%
```

This shows the exploration page can not only view overall changes but also provide dimension breakdown leads.

## Global Filter

The exploration page also has a "Global Filter" area.

Global filter is used to restrict the data scope before querying, such as only viewing a specific plan, source, country, or time range.

Suitable scenarios:

- View only a specific business line.
- View only a specific region.
- View only a specific customer source.
- Exclude test data.
- Limit to a specific time period.

If query results do not match expectations, first check whether the global filter is set correctly.

## Difference Between Exploration and Natural Language Q&A

| Capability | Analysis Q&A | Data | Exploration |
| --- | --- | --- | --- |
| Main purpose | Ask questions in natural language and get answers | View what data is covered in the current domain | Structured exploration around metrics |
| Suitable users | Business users | Business users, analysts | BI analysts, business analysts |
| Input method | Natural language | Click tables and fields | Select metrics, add comparison or filters |
| Output | Text, tables, charts, SQL, logs | Table list, field list | Comparison tables, change rates, drill-down fields, charts |
| Typical question | "How many active accounts are on the Basic plan?" | "What fields can be queried in the current domain?" | "How much did this metric change this period vs. the last period?" |

## Relationship Between Exploration and Answer Builders

The exploration page shows configured metrics and answer builders.

This means:

- If a metric is not configured, it may not appear on the exploration page.
- If an answer builder is well-configured, the exploration page can explore directly based on it.
- If field semantics or answer builder descriptions are unclear, business users may not understand the exploration objects.

Therefore, semantic layer maintainers should add clear names, aliases, and descriptions to metrics and answer builders, so that BI analysts and business users can understand what they represent when they see the names.

## When to Use Exploration Instead of Asking Directly

Use exploration when:

- You already know which metric to view.
- You want to do baseline period and comparison period analysis.
- You want to quickly see change rates.
- You want to find which dimensions the change comes from.
- You want to break down a single metric across multiple fields.

Ask directly when:

- You are not sure yet which metric to view.
- You want to describe an open question in business language.
- You need the system to automatically generate an explanation.
- You want the system to generate charts and text insights.
- You need to continue asking follow-up questions about causes.

Recommended flow:

1. First use "Data" to understand the data scope of the current analytics domain.
2. Use "Analysis" to ask natural language questions.
3. For stable metrics, use "Exploration" for structured comparison.
4. Save charts with long-term value to a dashboard.

## BI Analyst Usage Recommendations

BI analysts can use the exploration page as a validation tool before building a dashboard.

Recommended approach:

- First confirm whether the metric appears on the exploration page.
- Add comparison analysis to observe baseline vs. comparison period changes.
- Review the auto-generated drill-down fields.
- Identify dimensions worth displaying on the dashboard.
- Return to the analysis Q&A to generate cleaner charts.
- Save stable charts to the dashboard.

## Common Questions

### Why Can't I See the Metric I Want on the Exploration Page?

Possible reasons:

- The metric has not been configured.
- The answer builder has not been configured.
- The current analytics domain has not added the relevant resources.
- The current user does not have permission.

You need to contact the domain maintainer to add the configuration.

### Why Is There No Obvious Change After Clicking Add?

Possible reasons:

- The current exploration object does not support the corresponding comparison or filter.
- No available fields.
- A default condition already exists.
- A metric or answer builder needs to be selected first.

Try switching to another metric to verify, or use natural language Q&A to confirm whether the metric is available.

### Can Exploration Results Be Saved Directly to a Dashboard?

The main verification in this practice was that charts and tables from Q&A results can be saved to a dashboard. Whether charts generated on the exploration page support the same save operation needs to be verified against the actual page buttons.

If exploration results have long-term value, it is recommended to return to the "Analysis" page, generate stable charts using natural language, and then save to a dashboard.

## Related Documentation

- [Question Asking Guide](datagpt-question-asking-guide.md) — How to ask questions that are more likely to get accurate answers
- [Reading Analysis Results](datagpt-answer-reading-guide.md) — How to determine whether an answer is trustworthy
- [Analysis Patterns Guide](datagpt-analysis-patterns-guide.md) — Common analysis patterns such as trends, comparisons, rankings, and proportions
- [Using Dashboards](datagpt-dashboard-bi-analyst-guide.md) — Save Q&A results as shareable dashboards
- [Answer Builder Best Practices](datagpt-answer-builder-best-practices.md) — Answer builder configuration that the exploration page depends on
