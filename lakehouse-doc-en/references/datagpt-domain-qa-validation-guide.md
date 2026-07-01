# Validating Q&A Effectiveness

After completing analytics domain configuration, the effectiveness must be validated through actual Q&A. Simply checking whether tables are added, metrics are created, and the health scan is normal does not guarantee that user questions will be answered correctly.

This guide explains how to design validation questions, how to review SQL and logs, and how to determine whether knowledge, metrics, answer builders, field semantics, and table relationships are actually working.

Q&A validation is the management and maintenance side's delivery check of business usage effectiveness. Business users do not need to prove they "know how to ask" — maintainers need to prove the system can understand real business phrasings and stably answer questions within the correct permissions, correct definitions, and correct data scope.

---

## Validation Goals

Q&A validation needs to confirm four things:

1. Users can ask questions in business language.
2. The system can select the correct fields, filters, groupings, and metrics.
3. Answers can explain results using the correct business definitions.
4. The factual sources, knowledge, and data scope used by the system are trustworthy and currently valid.

These four things correspond to the responsibilities of the management and maintenance side:

| Validation Goal | Work the Management Side Needs to Do |
| --- | --- |
| Users can ask in business language | Configure field aliases, field descriptions, recommended questions, and knowledge so users don't need to say field names. |
| System can select correct fields and metrics | Configure field purposes, metrics, answer builders, indexes, and table relationships to reduce misselection. |
| Answers conform to business definitions and permission boundaries | Configure knowledge, domain permissions, role authorization, row-level permissions, and column hiding, then verify via SQL and logs. |
| Factual sources are trustworthy and not outdated | Confirm that official tables, metrics, knowledge, answer builders, and files are the current valid version. |

When validating, do not only look at the final answer. At minimum, review:

- Final text answer.
- Table or chart.
- **SQL Statements**.
- **Logs**.

---

## Preparation Before Validation

It is recommended to first prepare a fixed set of test questions covering the core business scenarios of the current analytics domain.

It is also recommended to add for each test question:

| Content | Description |
| --- | --- |
| Expected answer or judgment criteria | Can be a precise number, or the table, field, metric, or knowledge that should be found. |
| Data timestamp | Record the data date or snapshot used during validation to enable retrospective review when data changes. |
| Trusted factual source | Specify which table, metric, knowledge, or answer builder should be used as the reference. |
| Validator | Specify who confirmed the answer is correct. |
| Validation conclusion | Pass, fail, requires manual review, or not covered. |

Test questions should include:

| Type | Example |
| --- | --- |
| Simple metric | How many active accounts are there currently? |
| Filter condition | How many active accounts are on the Basic Plan? |
| Dimension grouping | Show account count by Plan. |
| Multiple metrics combined | Show account health overview by Plan. |
| Knowledge definition | How many active users are there? |
| Answer builder | Show account health overview for Google source only, display active rate and active seats by Plan. |
| Virtual column | Show a few customer names. |
| Multi-table question | Calculate sales by category. |
| Attribution analysis | Analyze the main factors affecting activity differences. |
| Time-series forecast | Track key metrics by month and forecast the next 3 months. |

If the analytics domain does not include a certain capability, skip the corresponding questions.

### Recommended: Establish Two Types of Question Sets

| Question Set | When to Use | Description |
| --- | --- | --- |
| Launch qualification question set | Before first domain launch | Covers core business metrics, core dimensions, permission boundaries, and high-frequency questions. |
| Regression validation question set | After modifying field semantics, metrics, knowledge, answer builders, table structure, or permissions | Used to confirm that old questions have not regressed due to configuration changes. |

The launch qualification question set should not be too large, but must cover the questions that matter most and have the least tolerance for error. The regression validation question set can be continuously supplemented from online feedback and historical errors.

---

## Step 1: Validate a Simple Question

Start with the simplest question with a predictable result.

Example:

> How many active accounts are there currently?

Check points:

- Whether the answer number is correct.
- Whether SQL uses the correct table.
- Whether WHERE includes the correct definition, e.g., `active_subscription = TRUE`.
- Whether logs show knowledge, metrics, or table structure was found.

In one actual validation in a test environment, this question returned 464, using `active_subscription = TRUE` to count active accounts.

After the simple question passes, then test filters, groupings, and complex definitions.

---

## Step 2: Validate Whether Knowledge Is Working

Knowledge is used to explain business terms and definitions. When validating, use real business terms that users would actually say — not field names.

Example:

> How many active accounts are there?

Check logs for:

- `search_knowledge`
- Found knowledge name, knowledge details, or Knowledge ID
- `get_knowledge_detail`
- Business definition from the knowledge

If knowledge is working, the logs show the system first searched knowledge, then continued executing based on the definition in the knowledge.

If knowledge was not found:

- Check whether the knowledge is added to the current analytics domain.
- Check whether the knowledge is enabled.
- Check whether the knowledge contains the term the user used.
- Check whether synonyms need to be added.

---

## Step 3: Validate Filter Conditions

Filter conditions validate whether the system can convert user natural language into WHERE conditions.

Example:

> How many active accounts are on the Basic Plan?

Check the SQL:

- Whether it has `plan = 'Basic'`.
- Whether the active account definition is still preserved.
- Whether the correct casing is used.

In practice, the system first confirms the actual values in the `plan` field, then uses `Basic` as the filter value.

It is recommended to also test different types of filters:

| Filter Type | Example |
| --- | --- |
| Enum filter | Only show Google source. |
| Boolean filter | Only show active subscription accounts. |
| Time filter | New accounts in the last 30 days. |
| Numeric filter | Accounts with more than 10 seats. |

If a filter fails, first check field aliases, field descriptions, field purposes, indexes, and actual values.

---

## Step 4: Validate Dimension Grouping

Dimension grouping validates whether the system can convert "by a field" into GROUP BY.

Example:

> Show account count by Plan.

Check the SQL:

- Whether SELECT includes `plan`.
- Whether GROUP BY includes `plan`.
- Whether the aggregation function is correct.

It is recommended to test:

| Dimension | Example Question |
| --- | --- |
| Categorical field | Show account count by Plan. |
| Source field | Show active rate by source. |
| Geographic field | Show account count by country. |
| Time field | Show monthly new account count. |

If grouping is wrong, check whether field purpose is set to dimension, whether the field is hidden, and whether field description is clear.

---

## Step 5: Validate Metrics

Metrics are used to lock in simple aggregation definitions.

Example:

> How many active users are there currently?

Check logs:

- Whether a metric was found.
- Whether metric calculation is being executed.
- If metric calculation fails, whether it falls back to SQL.

In actual validation, the system found the "Total Active Accounts" metric but after metric calculation failed it fell back to a SQL query. This shows metrics help the system understand definitions, but execution success still needs to be checked.

When validating metrics, confirm:

- Whether the metric is added to the current analytics domain.
- Whether the metric is enabled.
- Whether metric names and aliases can match user phrasings.
- Whether the metric definition matches the business definition.
- Whether metric calculation succeeds.

---

## Step 6: Validate Answer Builders

Answer builders validate complex definitions, multiple metrics, dynamic dimensions, and dynamic filters.

Example:

> Show account health overview by plan, including account count, active accounts, active rate, total seats, and active seats

Check logs for:

- Finding the answer builder or its output metrics.
- `metricType = SQL`.
- `dims = plan`.
- Multiple output metrics returned.
- Table or chart automatically generated.

Then test filters and output columns:

> Show account health overview for Google source only, display active rate and active seats by plan

Check logs for:

- `filters: source = Google`
- `dims = plan`
- `outputColumns = active_account_rate, active_seats`

If the answer builder was not hit:

- Check builder name, alias, and description.
- Check output metric names, aliases, and descriptions.
- Check whether `${filters}` and `${dims}` are configured.
- Check whether filter fields and dimension fields are bound.

---

## Step 7: Validate Virtual Columns

Virtual columns validate whether derived fields can be used in natural language Q&A.

Example:

> Show a few customer names.

If a name virtual column was created, such as:

```sql
concat(first_name, ' ', last_name)
```

Check:

- Whether SQL uses the virtual column or corresponding expression.
- Whether the answer shows the correct concatenated result.
- Whether the virtual column has an alias and description.
- Whether the field type and purpose are reasonable.

If Q&A did not use the virtual column, field aliases, field descriptions, and field purposes usually need to be added.

---

## Step 8: Validate Multi-Table Questions

Multi-table questions validate whether table relationships are correct.

Example:

> Calculate sales by category.

Check SQL:

- Whether the correct tables are JOINed.
- Whether the ON conditions are correct.
- Whether there is duplication or data bloat.
- Whether correct dimension fields are used.

It is recommended to ask the system in the test question to explain which table relationships were used. For example:

> Show the top 10 player counts and total achievements by game type, and explain which table relationships were used.

In a practical test in the `gaming_profiles_playstation` domain, the system generated a multi-table JOIN:

```sql
SELECT
  g.genres,
  COUNT(DISTINCT h.playerid) AS player_count,
  COUNT(*) AS achievement_count,
  ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT h.playerid), 2) AS avg_achievements_per_player
FROM
  quick_start.gaming_profiles_playstation.v_gpt_history h
  JOIN quick_start.gaming_profiles_playstation.v_gpt_achievements a ON h.achievementid = a.achievementid
  JOIN quick_start.gaming_profiles_playstation.v_gpt_games g ON a.gameid = g.gameid
GROUP BY
  g.genres
ORDER BY
  player_count DESC
LIMIT
  10
```

The path of this SQL is:

1. Start from the player achievement history table `v_gpt_history`.
2. Join the achievement definition table `v_gpt_achievements` via `achievementid`.
3. Then join the game information table `v_gpt_games` via `gameid`.
4. Finally group and count by game type `genres`.

When validating, do not just check whether the system "returned a table" — also confirm whether the JOIN path conforms to the business model. If the system selected the wrong intermediate table or wrong join key, or handled a one-to-many relationship as repeated detail counting, the final numbers may look reasonable but actually be inflated.

If auto-association has no results, it is not recommended to directly launch multi-table Q&A. Manually confirm the relationships, or limit the analytics domain to only single-table questions for now.

---

## Step 9: Validate Attribution Analysis

Attribution analysis validates whether the system can automatically select multiple possible influencing factors around a business phenomenon, and generate layered comparisons, contribution shares, and explanations.

Example:

> Analyze the main reasons for user activity differences, performing attribution analysis by country, game library size, game type, achievement rarity, and achievement depth.

Check points:

- Whether analysis is centered around a clear target metric, such as active user count, active rate, cancellation rate, or revenue change.
- Whether dimensions used actually exist in the current analytics domain.
- If users mention a non-existent dimension, whether the system clearly states it cannot analyze by that dimension rather than fabricating fields.
- Whether SQL correctly groups by dimension.
- Whether both difference metrics and contribution metrics are output, such as active rate and active user count contribution share.
- Whether charts are generated for comparison.
- Whether conclusions distinguish "correlation explanation" from "causal conclusion".

In practice, when asking about PlayStation user activity differences in the `gaming_profiles_playstation` domain, the system recognized that `plan` and `source` were not available in the current domain, and instead analyzed using actually available data, generating charts for game library size, country, achievement rarity, game type, and achievement depth.

Attribution questions typically trigger multiple SQL segments and multiple charts, and runtime may be significantly longer than simple lookups. When validating, check whether SQL is too heavy and whether optimization through answer builders, pre-aggregation tables, or limiting time ranges is needed.

---

## Step 10: Validate Time-Series Forecast

Time-series forecast validates whether the system can predict future metric changes based on historical time series.

Example:

> Track changes in active player count and achievement count by month, and predict the next 3 months.

Check points:

- Whether the correct time field is selected.
- Whether aggregation is at the appropriate granularity, such as by day, week, or month.
- Whether historical data range and forecast period are clearly stated.
- Whether incomplete periods or anomalous data are identified and handled.
- Whether forecast capability is triggered rather than just drawing historical trends.
- Whether forecast values, confidence intervals, forecast rationale, and risk notes are provided.
- Whether trend or forecast charts are generated.

In practice, in the `gaming_profiles_playstation` domain, the system aggregated achievement records by month, triggered "run time-series forecast", used Prophet for prediction, automatically excluded the incomplete December 2024 data, and output forecasts for active player count, total achievements, and average achievements per player for January to March 2025.

Time-series forecast results require careful interpretation. Forecasts can be used for trend anticipation and monitoring, but should not be treated as definitive results. For production scenarios, BI analysts should check SQL, logs, training data range, anomalous data handling, and confidence intervals.

---

## How to Read Logs

Logs help determine whether the system executed as expected.

Common log signals:

| Signal | Description |
| --- | --- |
| Knowledge base search found 0 results | Business term has no knowledge explanation. |
| Found 1 knowledge entry | Knowledge was found. |
| Found N metrics | The current analytics domain has available metrics or answer builder outputs. |
| Executing metric calculation | The system is calling a metric or answer builder. |
| Metric calculation failed | Found but execution failed; may fall back to SQL. |
| Viewing table structure | The system is relying on table fields for ad hoc inference. |
| Executing SQL query | The system is generating SQL directly. |
| Using draw_chart_plus | The system is generating a chart. |
| Using draw_table_js | The system is generating a table. |

Logs should be used as the primary evidence during validation, not just the final response.

---

## How to Determine Validation Passes

A question can be considered to have passed validation if all of the following are met:

- Answer result meets expectations.
- SQL used correct tables and fields.
- Filter conditions are correct.
- Grouping dimensions are correct.
- Aggregation logic is correct.
- Logs show expected configurations were found, or reasonable fallback occurred.
- Natural language explanation conforms to business definitions.

If only "the number looks right" but SQL or logs are wrong, it should not be considered passing.

---

## Recommended Validation Matrix

| Configuration | Validation Question | What to Check |
| --- | --- | --- |
| Field alias | Show account count by plan | Whether SQL uses `plan`. |
| Field description | How many active accounts are there | Whether the correct active definition is used. |
| Knowledge | How many active users are there | Whether logs show knowledge was found. |
| Metric | How many active users are there currently | Whether logs show metric calculation was executed. |
| Answer builder | Show account health overview by plan | Whether `dims = plan` was passed. |
| Filter field | Only show Google source | Whether `source = Google` was passed. |
| Output column | Only show active rate and active seats | Whether `outputColumns` was passed. |
| Virtual column | Show customer names | Whether virtual column was used. |
| Table relationship | Calculate sales by category | Whether JOIN is correct. |

---

## Validation Question Design Principles

Good validation questions should cover different capabilities:

- One simple total count question.
- One synonym question.
- One filter question.
- One grouping question.
- One multi-metric question.
- One complex definition question.
- One chart question.
- One boundary question.

Do not only ask questions the system can most easily answer correctly. Deliberately cover expressions that are prone to errors, such as:

- Users using business terms instead of field names.
- Users using lowercase enum values, e.g., `google`.
- Users requesting only some output metrics.
- Users requiring both filter and grouping at the same time.
- Users using concepts that are easily confused with similar fields.

---

## Common Validation Failure Handling

| Failure Symptom | Prioritize |
| --- | --- |
| SQL used wrong field | Add field aliases, descriptions, purposes; hide interfering fields if necessary. |
| Filter not applied | Check actual field values, field purpose, indexes, `${filters}` configuration. |
| Grouping not applied | Check field purpose, `${dims}` configuration. |
| Knowledge not found | Add knowledge synonyms and business definitions. |
| Metric not found | Add metric aliases; confirm it is added to the analytics domain. |
| Answer builder not found | Add builder names, aliases, descriptions, and output metric names. |
| Multi-table results wrong | Check table relationships and JOINs. |
| Explanation unclear | Add field descriptions, metric descriptions, knowledge. |

---

## Regression Validation After Configuration Changes

Analytics domain configuration is not a one-time task. Whenever fields, knowledge, metrics, answer builders, or table relationships are modified, it is recommended to re-validate related questions.

| Change Content | Must Re-validate |
| --- | --- |
| Modified field alias or description | Re-ask questions using business terms related to that field; confirm SQL did not misselect a field. |
| Modified field purpose or hidden status | Validate that filters, groupings, and metric calculations can still use the correct field. |
| Added or modified knowledge | Ask using business terms and synonyms in the knowledge; confirm logs show knowledge was found. |
| Added or modified metrics | Validate metrics are found, calculation succeeds, and conforms to definitions. |
| Added or modified answer builders | Validate builder is found; `${filters}`, `${dims}`, and output columns are passed correctly. |
| Added or modified table relationships | Validate multi-table JOINs are correct and results have no duplicates or bloat. |
| Added or deleted tables | Re-check field ambiguity, similar fields, and auto-association results. |

Even just adding descriptions may change how the system selects fields or understands business terms. Therefore, a fixed test set should be maintained for core questions and run after each major configuration change.

---

## Validation Report Recommendations

Before launch, a simple validation report can be recorded:

| Item | Content |
| --- | --- |
| Analytics Domain | Analytics domain name |
| Validation Date | Date and personnel |
| Test Questions | User's natural language question |
| Expected Result | Expected definition or number |
| Actual Result | System response |
| SQL Check | Whether it meets expectations |
| Log Check | Which configurations were found |
| Conclusion | Pass / Needs correction |
| Follow-up Actions | Which configurations need to be added |

This prevents the inability to trace back "why this analytics domain was considered ready" after launch.

---

## Minimum Validation Set Before Launch

If time is limited, validate at least these 5 questions:

1. One core total count question.
2. One core business term question.
3. One question with filter conditions.
4. One question grouped by a common dimension.
5. One complex question that hits an answer builder.

Each question must have the final answer, SQL statements, and logs reviewed.

The goal of analytics domain validation is not to prove the system "can answer" — it is to prove that the management and maintenance work is sufficient to support business users stably getting correct answers using natural language. Only when typical business questions can be answered with correct business definitions, correct fields, correct configurations, and correct permission boundaries should the domain be opened to business users.

## Related Documentation

- [Launching an Analytics Domain Health Check](datagpt-domain-health-check-and-launch-checklist.md) — Health scan and pre-launch checklist
- [Troubleshooting Q&A Accuracy Issues](datagpt-qa-accuracy-troubleshooting-guide.md) — Diagnosis and resolution for common issues
- [Configuring Analytics Domains](datagpt-domain-management-guide.md) — Creating and configuring data in analytics domains
- [Configuring Field Semantics](datagpt-field-semantic-config-guide.md) — Configuring field aliases, descriptions, and purposes
- [Configuring Knowledge](datagpt-knowledge-config-best-practices.md) — Business definitions and term explanations
- [Metrics and Answer Builders](metrics_answer_build.md) — Creating and configuring metrics and answer builders
