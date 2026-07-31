# Troubleshooting Q&A Accuracy Issues

When Analytics Agent's response does not meet expectations, do not only look at the final text answer. The correct approach is to trace through the execution pipeline step by step: how the user's question was understood, which knowledge and configurations were matched, what SQL was generated, which fields were used, and what filters, groupings, and metrics were applied.

This guide is based on actual configuration and Q&A validation, and is applicable for troubleshooting issues such as "wrong numbers, wrong fields used, missing filters, incorrect grouping, metrics or answer builders not matched, unclear definition explanation".

---

## Troubleshooting Order

The recommended troubleshooting order is:

| Step | What to Check | Purpose |
| --- | --- | --- |
| 1. Check final answer | Values, explanations, charts, tables | Identify the type of problem. |
| 2. Check SQL statement | Tables, fields, filters, groupings, aggregations, JOINs | Determine if the SQL matches the business definition. |
| 3. Check logs | Knowledge, metrics, answer builders, tool calls | Determine if the system matched the correct configurations. |
| 4. Check field semantics | Aliases, descriptions, types, usage, hidden status, virtual columns | Determine if fields are correctly understood. |
| 5. Check knowledge | Business terms, definitions, synonyms | Determine if there is an explanation basis for the user's expressions. |
| 6. Check metrics and answer builders | Existence, enabled status, definitions, parameters | Determine if calculation logic should be solidified. |
| 7. Check table relationships | Auto-association, manual relationships, JOIN paths | Determine if multi-table queries are correct. |
| 8. Check health score | Anomalies and warnings | Identify configuration gaps affecting Q&A accuracy. |

Do not immediately modify SQL or configuration. First confirm through SQL and logs which layer the error occurred at.

---

## Common Problem Types

| Problem Symptom | Typical Cause |
| --- | --- |
| Numbers are wrong | Wrong field used, missing filter, incorrect aggregation function, JOIN fan-out, metric definition error. |
| SQL uses wrong field | Missing field alias/description, similar fields exist, field usage unclear. |
| Did not filter as user requested | Filter field not configured, actual field value casing inconsistent, `${filters}` not bound. |
| Did not group as user requested | Dimension field not configured, `${dims}` not bound, field not suitable as dimension. |
| Knowledge not matched | Knowledge not configured, not enabled, or doesn't include user's common expressions. |
| Metric not matched | Metric not added to analytics domain, not enabled, name/alias doesn't match. |
| Answer builder not matched | Builder name, alias, description unclear, output metric name unclear, or parameters not configured. |
| Multi-table results anomalous | Missing table relationship, JOIN error, join field not unique. |
| Chart doesn't match expectations | SQL output columns not suitable for chart, dimension or measure selection unreasonable. |
| Explanation is unclear | Field descriptions, knowledge, metric descriptions insufficient. |

---

## Step 1: Check the Final Answer

First determine where the final answer is wrong.

Focus on:

- Whether numbers meet expectations.
- Whether the correct definition was used.
- Whether filtering was done as the user requested.
- Whether grouping was done as the user requested.
- Whether table and chart fields match the question.
- Whether the natural language explanation states the definition.

For example, the user asks:

> Show the account health overview for source = google only, show active rate and active seats by plan

If the answer only returns overall active rate without grouping by `plan`, it may indicate the dimension was not passed in or was not configured. If the answer groups by `plan` but doesn't filter `source = Google`, the filter condition may not have taken effect.

---

## Step 2: Check the SQL Statement

Click **SQL Statement** below the answer to check the actual executed SQL.

Key checks:

| Check Item | How to Determine |
| --- | --- |
| Is the table correct? | Is the table in FROM the expected table? |
| Are the fields correct? | Are fields in SELECT, WHERE, GROUP BY consistent with the business definition? |
| Is the filter correct? | Does WHERE include the conditions the user requested? |
| Is the grouping correct? | Does GROUP BY include the dimensions the user requested? |
| Is the aggregation correct? | Are COUNT, SUM, AVG, MAX, MIN consistent with the metric definition? |
| Is the JOIN correct? | In multi-table queries, are ON conditions correct? Could it cause data fan-out? |
| Are LIMIT / ORDER BY reasonable? | Do they affect detail or TopN queries? |

In practice, after an answer builder is matched, the SQL will show the template has been substituted. For example:

```sql
WHERE active_subscription = TRUE
  AND `plan` = 'Basic'
```

This shows that the user's "Basic Plan" has been converted into a filter condition.

If the SQL does not include the filter or grouping field the user requested, continue checking logs to confirm whether `filters` or `dims` were passed in.

---

## Step 3: Check the Logs

Click **Logs** below the answer to view the complete execution pipeline.

Logs are critical for troubleshooting accuracy because they show:

- Whether knowledge was searched.
- Whether knowledge was matched.
- Whether metrics were found.
- Whether an answer builder was found.
- Whether metric calculation was executed.
- Whether it fell back to table structure and SQL query.
- Whether it first queried actual field values.
- Whether a chart or table was generated.

### Common Signals in Logs

| Log Signal | Meaning |
| --- | --- |
| `search_knowledge` found 0 results | No knowledge available to explain the user's business term. |
| `get_knowledge_detail` | The system has read the knowledge details. |
| Found N metrics | Available metrics or answer builder outputs exist in the current analytics domain. |
| Execute metric calculation | The system is attempting to use a configured metric or answer builder. |
| Metric calculation failed, falling back to SQL query | The configured object was recognized but execution failed; system fell back to SQL. |
| View table structure | The system needs to rely on field structure for ad hoc inference. |
| Query DISTINCT field values | The system is confirming enumeration value casing or actual values. |

### Log Characteristics When an Answer Builder Is Matched

When an answer builder is matched, logs typically show:

- Found matching metric or answer builder.
- `metricType = SQL`.
- `metricId` pointing to the SQL metric generated by the answer builder.
- Parameters including `dims`, `filters`, or `outputColumns`.

For example:

| Parameter | Meaning |
| --- | --- |
| `dims = plan` | Group by Plan. |
| `filters: source = Google` | Filter for Google source only. |
| `outputColumns = active_account_rate, active_seats` | Return only active rate and active seats. |

If the user's question is suitable for an answer builder but logs show no builder was matched, typically check the builder's name, alias, description, and output metric names.

---

## Troubleshooting Field Semantics

Field semantic issues are one of the most common causes of Q&A errors.

### Typical Problems

| Problem | Solution |
| --- | --- |
| User says "plan", SQL doesn't use `plan` | Add "subscription plan, version" and similar aliases to `plan`. |
| User says "active accounts", SQL doesn't use `active_subscription` | Supplement field description and configure knowledge explaining the active account definition. |
| SQL uses wrong time field | Distinguish descriptions and usage for `created_at`, `trial_ends_at`, `canceled_at`. |
| Grouping by ID or email makes results very granular | Adjust field usage to avoid high-cardinality fields as default dimensions. |
| Field doesn't appear in filters or dims | Check field type, field usage, and hidden status. |

### Eliminating Field Ambiguity

When similar fields exist in one or multiple tables, prioritize supplementing field semantics.

For example, when an account table has:

- `active_subscription`
- `trial_converted`
- `canceled_at`
- `legacy_plan`

If a user asks "active accounts", use field descriptions and knowledge to clarify:

> Active accounts refer to accounts where `active_subscription = TRUE`, not equivalent to trial-converted accounts, and not equivalent to uncanceled accounts.

This reduces the model's chance of selecting the wrong field.

---

## Troubleshooting Knowledge Configuration

Knowledge is used to explain business terms, definitions, and synonyms.

### When to Check Knowledge

| Symptom | Description |
| --- | --- |
| User used a business term | Knowledge is needed to explain the term. |
| Same concept has multiple names | Knowledge needs to maintain synonyms. |
| Field description cannot fully express the definition | Knowledge needs to supplement cross-field or business rules. |
| Answer explanation is unclear | Knowledge needs to support natural language explanation. |

### Troubleshooting Methods

Check logs for:

- `search_knowledge`
- `get_knowledge_detail`
- Matched Knowledge ID

If no knowledge was matched:

- Check whether knowledge has been added to the current analytics domain.
- Check whether knowledge is enabled.
- Check whether the knowledge name and description include the user's common expressions.
- Check whether abbreviations, aliases, and English expressions need to be added to the knowledge.

In practice, after configuring "active user definition" knowledge, when a user asks "How many active accounts are there?", logs show the knowledge was matched and `active_subscription = TRUE` was used as the definition.

---

## Troubleshooting Metric Configuration

Metrics are suitable for solidifying simple aggregation definitions.

### Common Problems

| Symptom | Possible Cause | Solution |
| --- | --- | --- |
| System didn't use the metric | Metric not added to analytics domain or alias doesn't match | Check metric status, name, alias. |
| Metric calculation failed and fell back to SQL | Problem with metric definition or execution parameters | Check logs and SQL, fix metric definition. |
| Metric definition doesn't match business | Auto-generated metric not manually reviewed | Modify metric or switch to answer builder. |
| User expression doesn't match metric | Missing metric aliases | Add common business expressions. |

In practice, auto-generated metrics are only candidate suggestions, not final business definitions. The system may generate `COUNT(canceled_at)`, `MIN(created_at)`, `SUM(seats)` and similar candidate metrics — users should review before adopting them.

---

## Troubleshooting Answer Builders

Answer builders are suitable for complex SQL, multi-metrics, dynamic filters, and dynamic dimensions.

### Key Checks

| Check Item | Description |
| --- | --- |
| Does SQL include `${filters}`? | Missing this may prevent dynamic filtering; validation will report an error. |
| Does SQL include `${dims}`? | Required when dynamic grouping is needed. |
| Are filter fields bound? | Affects whether filtering works when users say "only show condition X". |
| Are dimension fields bound? | Affects whether grouping works when users say "show by field X". |
| Are output field names clear? | Affects whether Q&A can select the correct output columns. |
| Is the description clear? | Affects whether the system can select this builder. |

### Typical Matched Case

The user asks:

> Show account health overview by plan, including account count, active account count, active rate, total seats, and active seats

Logs show:

- Found answer builder "Account Health Overview".
- Passed in `dims = plan`.
- Multiple output metrics returned.
- Automatically generated table and combination chart.

The user continues:

> Show account health overview for source = google only, show active rate and active seats by plan

Logs show:

- First queried actual value of `source`, confirmed as `Google`.
- Passed in `filters: source = Google`.
- Passed in `dims = plan`.
- Passed in `outputColumns = active_account_rate, active_seats`.

This shows that answer builders can not only fix SQL but also dynamically respond to users' filter, grouping, and output column requirements.

---

## Troubleshooting Table Relationships

Multi-table Q&A errors usually come from JOIN relationships.

### Situations That Need Attention

- The user's question spans multiple tables.
- SQL contains JOINs.
- Results are significantly inflated or duplicated.
- Table relationships not configured or auto-association returned no results.
- Same-name fields exist in multiple tables.

In practice, auto-association is not available with a single table; after adding multiple tables, you can click "Auto Associate" and the system will open a confirmation window. Auto-association may return "No table associations found" — in this case you cannot assume multi-table Q&A is reliable.

Recommendations:

- Manually confirm fact table and dimension table relationships.
- Check whether JOIN fields are unique.
- Avoid confirming associations solely because field names are identical.
- Validate JOINs in SQL using typical multi-table questions.

---

## Using Health Score Scans

Analytics domain health score scans for configuration items that affect Q&A accuracy.

In practice, the health score may flag:

- Table fields missing description information.
- No metrics exist in the domain.
- Table relationship anomalies.
- Large number of null values in a field.

Health score is not a formality check. The issues it flags — missing field descriptions, no metrics, incorrect joins — can directly affect Q&A accuracy.

Before launch:

- Click "Re-scan".
- Address anomalies.
- For issues not immediately addressed, document the reason.
- After addressing, re-test with typical questions.

---

## Symptoms and Treatments

| Symptom | Priority Check | Recommended Action |
| --- | --- | --- |
| Numbers obviously wrong | SQL, metrics, answer builders | Check aggregation functions, filter conditions, and definitions. |
| Wrong field used | Field semantics | Add aliases, descriptions, field usage; hide interfering fields if necessary. |
| Missing filter | SQL, logs, field usage | Check whether filters were passed in, whether the field is filterable. |
| Missing grouping | SQL, logs, dimension configuration | Check whether dims were passed in, whether the field can serve as a dimension. |
| Knowledge not matched | Logs, knowledge configuration | Supplement knowledge synonyms and business definitions. |
| Metric not matched | Metric status, name, alias | Add to analytics domain, enable metric, add aliases. |
| Answer builder not matched | Builder name, description, output metrics | Add business-friendly name, alias, description. |
| Multi-table results inflated | Table relationships, JOINs | Check join fields and cardinality. |
| Chart unreasonable | SQL output columns | Adjust dimension and measure fields. |
| Explanation unclear | Knowledge, field descriptions, metric descriptions | Supplement business definition explanations. |

---

## Recommended Validation Question Set

After configuration is complete, prepare a fixed set of test questions.

| Validation Target | Example Question |
| --- | --- |
| Field mapping | Show account count by plan. |
| Filter condition | Show active account count for Google source only. |
| Business definition | What is the current active account count? |
| Dynamic dimension | Show account health overview by plan. |
| Dynamic output columns | Show active rate and active seats by plan. |
| Knowledge match | How many active users are there? |
| Answer builder match | Show account health overview by plan, including account count, active account count, active rate, total seats, and active seats. |
| Multi-table relationship | Show order amount by category. |

For each question, check the final answer, SQL Statement, and Logs.

---

## Pre-Launch Checklist

- Do core fields have aliases and descriptions?
- Have core business terms been configured with knowledge?
- Have commonly used metrics been created and added to the analytics domain?
- Have complex definitions been solidified using answer builders?
- Do answer builders have `${filters}` and `${dims}` configured?
- Do output metrics have business-friendly names, aliases, and descriptions?
- Have table relationships been confirmed?
- Have health score anomalies been addressed?
- Have typical questions been used for validation?
- Have SQL and logs been checked to confirm the matching path?

The core principle of Q&A accuracy troubleshooting is: don't just look at the answer — look at SQL and logs; don't just fix a single question — fix the reusable configurations like field semantics, knowledge, metrics, answer builders, and table relationships.

## Related Documentation

- [Configure Field Semantics](datagpt-field-semantic-config-guide.md) — Field alias, description, and usage configuration
- [Configure Knowledge](datagpt-knowledge-config-best-practices.md) — Business definitions and term explanations
- [Configure Virtual Columns](datagpt-virtual-column-config-guide.md) — Creating and configuring derived fields
- [Metrics and Answer Builder](metrics_answer_build.md) — Creating and configuring metrics and answer builders
- [Answer Builder Best Practices](datagpt-answer-builder-best-practices.md) — Answer builder design and validation
- [Configure Analytics Domain](datagpt-domain-management-guide.md) — Analytics domain creation and data configuration
- [Improving Q&A Accuracy](answer-accuracy-improve.md) — Overall solution for semantic layer configuration
