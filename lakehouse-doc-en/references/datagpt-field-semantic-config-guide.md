# Configure Field Semantics

Field semantic configuration tells Analytics Agent what each field in a table represents in business terms, how it should be used by the Q&A system, whether it can serve as a filter or grouping dimension, and whether it should participate in indexing and analysis.

Natural language Q&A does not rely solely on field names to generate SQL. Field aliases, field descriptions, field types, field usage, hidden status, virtual columns, and table relationships all affect how the system understands questions, selects fields, generates SQL, and interprets results.

---

## Why Field Semantic Configuration Matters

After adding a table to an analytics domain, the system automatically reads the table structure. However, database field names are often designed for development or modeling purposes and may not be directly understandable by business users.

For example:

| Field Name | What Users Might Say | Potential Issues Without Configuration |
| --- | --- | --- |
| `active_subscription` | Active account, valid subscription, current active user | The system may not know which field to use to determine "active". |
| `plan` | Subscription plan, version, plan type | When users say "by plan", the system may not consistently map to `plan`. |
| `seats` | Number of seats, seat count, account count | The system may treat it as a dimension rather than a measure. |
| `created_at` | Creation time, account opening time, registration time | The system may not understand the time semantics and default analysis granularity. |

In practice, the analytics domain health check flags missing field descriptions. If table fields lack descriptions, the health check will report issues, indicating that field semantics are not optional decorations — they are foundational configurations that affect Q&A accuracy.

---

## Using Field Semantics to Eliminate Field Ambiguity

When generating SQL, large language models often need to choose one field from multiple candidates. If a table contains similar fields, or if multiple tables have fields with the same or similar names, the model may select the wrong field due to ambiguity.

An important function of field semantic configuration is to reduce this probability of misselection.

Common types of ambiguity include:

| Ambiguity Type | Example | Possible Misselection |
| --- | --- | --- |
| Similar fields in same table | `created_at`, `trial_ends_at`, `canceled_at` | When users say "time", the system doesn't know which to use. |
| Status fields in same table | `active_subscription`, `trial_converted`, `legacy_plan` | When users say "active users", the system may mistakenly use trial conversion or legacy plan fields. |
| Same-name fields across tables | Multiple tables all have `id`, `name`, `created_at` | May select wrong table's field in multi-table queries. |
| Ambiguous business terms | "User count" may mean account count, customer count, or subscription count | System may use a counting field that doesn't match the business definition. |
| Mixed technical and business fields | `source`, `channel`, `utm_source` | When users say "channel", the system may not know which field to use. |

Therefore, field semantic configuration is not just "adding comments to fields" — it tells the system which field to prioritize when a user uses a certain business term, and which fields should not be selected.

Recommended ways to eliminate ambiguity:

| Configuration Method | Effect |
| --- | --- |
| Field alias | Binds common business expressions to the correct field, e.g., binding "plan" to `plan`. |
| Field description | Explains the business meaning and applicable scenarios of the field, e.g., `active_subscription` represents the current active subscription. |
| Field usage | Marks whether the field is suitable for dimension, filter, or measure, reducing the chance of misusing measure fields as dimensions. |
| Hidden fields | Hides technical fields or interfering fields that should not be used in Q&A. |
| Knowledge configuration | Provides explicit explanation of complex business definitions, e.g., "active account count refers to accounts where active_subscription = TRUE". |
| Table relationship configuration | In multi-table scenarios, clarifies which table a field belongs to and how to join, reducing cross-table misselection. |

For example, if an account table contains `active_subscription`, `trial_converted`, and `canceled_at`, and a user asks "active account count", the recommended configuration is:

| Field | Recommended Semantics |
| --- | --- |
| `active_subscription` | Alias configured as "active subscription, is active, valid subscription"; description states that TRUE means the current subscription is valid and can be used to count active accounts. |
| `trial_converted` | Description states it indicates whether a trial converted to paid, not equivalent to the current active account. |
| `canceled_at` | Description states it represents the cancellation time and cannot be used alone as the criterion for active accounts. |

This way, when a user says "active accounts", the system is more likely to select `active_subscription` rather than mistakenly using `trial_converted` or `canceled_at`.

---

## Typical Use Cases for Field Semantics

The value of field semantic configuration is not just in field descriptions — it is also reflected in actual Q&A and analysis pipelines. The following scenarios all rely on field semantics to improve accuracy and control.

| Use Case | Value of Field Semantics | Example |
| --- | --- | --- |
| Mapping business terms to technical fields | Users don't need to know the actual field names to get correct results. | User says "plan", system maps to `plan`; user says "acquisition channel", system maps to `source`. |
| Resolving similar field ambiguity | Helps the system choose the correct field from multiple candidates. | "Active account" should prioritize `active_subscription`, not `trial_converted` or `canceled_at`. |
| Specifying a field's role in SQL | Determines whether a field should appear in `WHERE`, `GROUP BY`, aggregate functions, or SELECT detail. | `plan` is suitable for grouping and filtering; `seats` for summing; `created_at` for time filtering. |
| Supporting answer builder parameters | Determines which fields can be used by `${filters}` and `${dims}`. | When users say "only Google source", `source` needs to be a filterable field; when users say "by Plan", `plan` needs to be a dimension. |
| Improving auto-generated metric quality | Helps the system determine whether a field is suitable for COUNT, SUM, AVG, MAX, MIN metrics. | After configuring `seats` as a continuous measure, it is better suited for generating total seats, average seats, and similar metrics. |
| Improving natural language explanations | Answers can include not just numbers but also explanations of the definition. | After writing that `active_subscription = TRUE` in the field description, answers can state "based on accounts with active subscriptions". |
| Reducing misuse of high-cardinality fields | Prevents the system from using IDs, emails, and names as default grouping dimensions. | It is not recommended to group by `email` or `account_name` by default when analyzing account health. |
| Controlling sensitive field visibility | Reduces the chance of sensitive columns being used or displayed in Q&A by hiding fields. | Phone numbers, emails, ID numbers, and internal cost fields can be hidden. |
| Supporting virtual columns as business fields | Gives derived expressions a business-understandable semantic. | After configuring `concat(first_name, ' ', last_name)` as "customer name", users can ask about it naturally. |
| Supporting multi-table Q&A | Helps the system determine field ownership and join relationships. | When multiple tables have `created_at`, the field descriptions should distinguish order creation time, customer registration time, and payment time. |
| Supporting health checks and launch checks | Missing field descriptions and unclear usage affect analytics domain health. | When health check flags missing field descriptions, prioritize filling in core field descriptions. |
| Lowering the barrier for users | Lets users ask in business language without memorizing field names. | "Show active rate by plan", "only Google source", "new accounts in the last month". |

From a usage perspective, the more complete the field semantic configuration, the easier it is for Analytics Agent to accomplish three things:

1. Understand the business terms the user mentions.
2. Select the correct fields and SQL roles.
3. Explain results in a way that matches the business definition.

---

## Configuration Entry Point

The general path to field configuration:

1. Go to **Administration** -> **Analytics Domain Management**.
2. Open the target analytics domain.
3. Go to the **Data** tab.
4. Click **Tables**.
5. Click the table display name to enter the table detail page.
6. Configure fields in the **Table Schema** tab.

The table detail page usually contains three tabs:

| Tab | Purpose |
| --- | --- |
| Table Schema | View and configure field semantics, indexes, hidden status, field types, field usage, table relationships, and more. |
| Data Preview | View sample data to help understand the actual values and business meaning of fields. |
| Statistical Analysis | View field statistics: COUNT, NULL VALUE, DISTINCT, MIN, MAX, AVERAGE, SUM, etc. |

It is recommended to first review **Data Preview** and **Statistical Analysis** before configuring field semantics. Do not guess business meaning based solely on field names.

---

## Field Configuration Options

Common field configuration options in the table schema:

| Configuration | Purpose | Impact on Q&A |
| --- | --- | --- |
| Field Name | The actual column name in the database | The field ultimately used in SQL. |
| Field Alias | Business names for the field | Helps the system map user natural language to the field. |
| Field Type | Semantic type of the field | Affects whether the field is suitable as a dimension, measure, time field, or other usage. |
| Field Description | Business explanation of the field | Helps the system understand the field's meaning and usage boundaries. |
| Index Management | Controls whether a field is indexed or participates in retrieval | Affects field value retrieval, enumeration matching, and Q&A efficiency. |
| Hidden | Controls whether the field is visible to Q&A | Hides irrelevant or sensitive fields to reduce misuse. |
| Field Usage | Specifies whether the field is suitable as a dimension, filter, or measure | Affects field selection in answer builder and Q&A. |
| Table Relationship | Configures the field's join relationship with fields in other tables | Affects whether JOINs are correct in multi-table Q&A. |
| Updated Time | When the field configuration was last updated | Used to determine if the configuration is up to date. |
| Actions | Edit, view, or configure the field | Manage field semantics. |

---

## Field Aliases

Field aliases connect database field names to the natural language expressions used by business users.

It is recommended to configure one or more common business names for important fields:

| Field Name | Suggested Aliases |
| --- | --- |
| `plan` | subscription plan, version, plan type |
| `source` | source, channel, acquisition source |
| `country` | country, region |
| `seats` | number of seats, seat count |
| `active_subscription` | active subscription, is active, valid subscription |
| `created_at` | creation time, registration time, account opening time |

Aliases should use the actual expressions business users would say, not just copies of the field name.

Not recommended:

- Only filling in the English column name for all fields.
- Configuring the same alias for multiple different fields.
- Using overly broad aliases, such as calling multiple fields "status".

---

## Field Descriptions

Field descriptions explain the business meaning, value rules, and notes for a field. They are more detailed than aliases and are an important configuration for reducing field misuse.

Examples:

| Field | Not Recommended Description | Recommended Description |
| --- | --- | --- |
| `active_subscription` | Is active | Indicates whether the account currently has an active subscription. TRUE means the subscription is currently valid and can be used to count active accounts. |
| `seats` | Seats | The number of seats purchased or configured by the current account. Can be used to calculate total seats, active seats, and similar metrics. |
| `canceled_at` | Cancellation time | The time the account canceled its subscription. Null means not canceled; should not be used directly as the criterion for active accounts. |
| `trial_converted` | Is converted | Indicates whether a trial account has completed a paid conversion. |

Descriptions should answer three questions:

- What does this field represent?
- When should it be used?
- What is the difference between this and similar fields?

---

## Field Types

In practice, available field types include:

| Field Type | Applicable Fields | Description |
| --- | --- | --- |
| `CATEGORICAL` | `plan`, `source`, `country`, status fields | Categorical fields, suitable for grouping, filtering, and enumeration value matching. |
| `CONTINUOUS` | `seats`, amounts, quantities, scores | Continuous numeric fields, suitable for sum, average, max, min, and other measure calculations. |
| `DATE_AND_TIME` | `created_at`, `canceled_at`, timestamp fields | Time fields, suitable for time filtering, trend analysis, and time grouping. |
| `PARTITION` | Partition fields | Partition filter fields, commonly used for query scope control. |
| `OTHER` | Fields that are hard to classify or temporarily not involved in analysis | Not recommended as core Q&A fields. |

Field type affects how the system determines what a field is suitable for. For example, `seats` is better configured as a continuous numeric field rather than a categorical dimension; `plan` is better configured as a categorical field.

---

## Field Usage

In practice, available field usage options include:

| Field Usage | Meaning | Typical Fields |
| --- | --- | --- |
| `DIM` | Dimension field, suitable for grouping display | `plan`, `source`, `country`, date fields |
| `FILTER` | Filter field, suitable as a filter condition | `plan`, `source`, `active_subscription`, `created_at` |
| `MEASURE` | Measure field, suitable for aggregate calculation | `seats`, amounts, quantities, durations |

A field may be suitable for multiple usages. For example, `plan` can be both a dimension and a filter condition; `created_at` can be filtered by time or grouped by time.

Configuration recommendations:

| Field Type | Recommended Usage |
| --- | --- |
| Categorical fields | `DIM`, `FILTER` |
| Boolean fields | `FILTER`, optionally also `DIM` |
| Numeric measure fields | `MEASURE`, optionally also `FILTER` |
| Date/time fields | `FILTER`, `DIM` |
| ID, email, name | Generally not recommended as default `DIM` unless used for detail queries |

---

## Hidden Fields

Hiding fields reduces the chance of the Q&A system misusing them and can prevent sensitive or technical fields from being exposed to business users. In natural language Q&A scenarios, hiding columns can achieve an effect similar to column-level permissions: hidden fields should not be prioritized by the model for understanding, SQL generation, or result display.

Note that hiding fields is more about field visibility control at the Analytics Agent Q&A layer; underlying Lakehouse table permissions should still be managed through the data platform's permission system. For truly sensitive data, both underlying permission controls and field hiding should be configured.

Recommended to hide:

- Pure technical fields, such as internal processing identifiers and sync batch numbers.
- Sensitive fields that users should not query directly.
- Fields that may cause ambiguity but are not commonly used in business.
- Intermediate calculation fields or temporary fields.
- Columns you do not want exposed in natural language Q&A, such as phone numbers, emails, ID numbers, and internal cost fields.

Not recommended to hide:

- Commonly used filter fields.
- Commonly used grouping fields.
- Fields that metric calculations depend on.
- Fields needed in answer builder SQL.

Before hiding a field, confirm whether any metrics, answer builders, or common Q&A queries depend on it.

Field hiding can be understood as "semantic visibility" configuration within the analytics domain:

| Purpose | Example |
| --- | --- |
| Reducing misuse | Hide internal IDs and sync batch numbers to prevent the model from incorrectly grouping or filtering. |
| Reducing ambiguity | Among multiple similar status fields, only keep the ones business users should use. |
| Controlling visible Q&A fields | Hide phone numbers, emails, ID numbers, and other fields that should not appear in Q&A. |
| Simplifying user experience | Let users see only fields relevant to business analysis. |

---

## Index Configuration

Index management affects field value retrieval and enumeration matching. For natural language Q&A, indexes are often used to help the system identify specific values mentioned by users.

Fields suitable for indexing:

| Field Type | Example | Reason |
| --- | --- | --- |
| Enumeration fields | `plan`, `source`, `country` | Users frequently filter by specific values, e.g., "Basic Plan", "Google source". |
| Name fields | Product name, customer name, region name | Users may directly mention names that need to match field values. |
| Categorical hierarchy fields | Level-1 category, level-2 category, industry classification | Users commonly filter or group by category. |

Fields not necessarily suitable for indexing:

- High-cardinality IDs that are not commonly retrieved by value.
- Continuous numeric fields.
- Long text note fields.
- Fields that change frequently and whose Q&A does not depend on enumeration matching.

If users frequently mention a field value but the system recognition is unstable, check whether that field has been properly configured with aliases, descriptions, and indexes.

---

## Virtual Columns

Virtual columns allow you to add a derived field more suitable for Q&A to Analytics Agent without modifying the underlying table structure.

In practice, you can create virtual columns like the following:

```sql
concat(first_name, ' ', last_name)
```

This concatenates `first_name` and `last_name` into a complete name field.

Virtual columns are suitable for the following scenarios:

| Scenario | Example |
| --- | --- |
| Field concatenation | Concatenating names, region hierarchies, codes, and names. |
| Business labels | Generating labels such as "active/inactive" or "high value/regular" based on conditions. |
| Format standardization | Converting case, null values, and encoding into formats more suitable for Q&A. |
| Simplifying common expressions | Encapsulating complex expressions into a single semantic field. |

When creating a virtual column, run validation first to confirm the SQL expression is executable and review sample results to ensure they meet expectations. After creating the virtual column, supplement it with aliases, field type, field usage, and field description.

---

## Table Relationship Fields

If an analytics domain contains multiple tables, field relationships affect whether JOINs in multi-table Q&A are correct.

In practice, auto-association is not available with a single table; after adding multiple tables, you can click "Auto Associate" and the system will open a confirmation window showing source table, source column, target table, and target column.

Table relationships appear not only in the analytics domain table list but also in field-level configurations within table details. In practice, the `gaming_profiles_playstation` domain's table list shows:

- `history` is associated with `players`, joined on `playerid`.
- `purchased_games` is associated with `players`, joined on `playerid`.
- `purchased_games` is associated with `games.gameid` via the game library field.
- `achievements` is associated with `games`, joined on `gameid`.

In the table detail view, the field list also shows table associations for specific fields. For example, the `playerid` field in `purchased_games` is associated with the player table, and the `library` field is associated with the game table. Field-level table relationships affect how Analytics Agent selects JOIN paths in multi-table queries.

In one actual multi-table Q&A, a user asked "Top 10 by game type — player count who earned achievements and total achievement count". When generating SQL, the system used:

- `v_gpt_history.achievementid = v_gpt_achievements.achievementid`
- `v_gpt_achievements.gameid = v_gpt_games.gameid`

This shows that table relationships and field semantics enable the system to follow the chain "what achievement did the player earn" all the way to "which game does that achievement belong to, and what is the game type". Without these relationships, the system might not be able to reliably find the intermediate table, or might need to guess JOINs based on field names.

Important notes:

- Auto-association may not find relationships; do not assume the system can always auto-detect them.
- Incorrect associations can cause data fan-out or incorrect results.
- Health checks treat incorrect join relationships as serious anomalies that directly affect Q&A accuracy.

Recommendations:

- Manually confirm primary and foreign key relationships between fact tables and dimension tables.
- Avoid confirming associations solely because field names are identical.
- After configuration, validate JOINs in SQL using typical multi-table questions.

---

## How to Use Data Preview and Statistical Analysis

Before configuring field semantics, it is recommended to first review data preview and statistical analysis.

### Data Preview

Data preview is used to confirm actual field values. For example:

- The actual value in the `source` field might be `Google`, not the `google` that users say.
- The `plan` field might have `Basic`, `Business`, `Premium`.
- Boolean fields might use `TRUE/FALSE`.

When executing queries, the Q&A system may first query the actual field values, then use the correct casing for filtering.

### Statistical Analysis

Statistical analysis is used to determine whether a field is suitable as a dimension, filter, or measure.

Key items to observe:

| Statistic | Purpose |
| --- | --- |
| COUNT | Assess the scale of field data. |
| NULL VALUE | Determine whether the field has many null values. |
| DISTINCT | Assess field cardinality; high cardinality is not suitable as a default dimension. |
| MIN / MAX | Assess the range of numeric or time values. |
| AVERAGE / SUM | Determine whether a numeric field is suitable as a measure. |

For example, `id` typically has a very high DISTINCT count and is not suitable as a default grouping dimension; `plan` has fewer DISTINCT values and is more suitable as a dimension and filter.

---

## Relationship with Metrics and Answer Builders

Field semantic configuration directly affects metrics and answer builders.

| Configuration | Impact on Metrics | Impact on Answer Builder |
| --- | --- | --- |
| Field alias | Helps users find metrics using business terms | Helps users specify filters and dimensions in natural language |
| Field description | Helps the system understand metric definitions | Helps the system determine whether a field is suitable as an SQL template parameter |
| Field type | Affects auto-generated metric suggestions | Affects the selectable fields for `${filters}` and `${dims}` |
| Field usage | Affects aggregation, filtering, and grouping decisions | Determines whether a field is more suitable as a filter, dimension, or measure |
| Hidden fields | Prevents metrics from misusing fields | Prevents builder parameters from incorrectly selecting fields |

In practice, the `${filters}` field range in an answer builder is usually wider than `${dims}`; `${dims}` tends to favor categorical, enumeration, date, and boolean fields that are suitable for grouping.

---

## Configuration Recommendations

### Prioritize Core Fields

Do not try to configure all fields comprehensively at the start. Prioritize:

- Business fields that users ask about most often.
- Fields that metric calculations depend on.
- Commonly used filter fields.
- Commonly used grouping fields.
- Multi-table join fields.
- Fields prone to ambiguity.

### Avoid High-Cardinality Fields as Default Dimensions

Fields like IDs, emails, names, and order numbers can be grouped, but are generally not suitable as business analysis dimensions. They produce overly granular results that are difficult to interpret in charts and tables.

Unless users explicitly want a detail query, it is not recommended to use these fields as default recommended dimensions.

### Specify Granularity for Time Fields

Date/time fields are commonly used for trend analysis, but the granularity must be specified:

- By day
- By week
- By month
- By quarter
- By year

If you only configure "creation time" without explaining the business meaning and common granularity, the system may generate time groupings that are too fine or don't match business expectations.

### Clarify TRUE/FALSE Meaning for Boolean Fields

Boolean fields are especially prone to misinterpretation. The description should clarify:

- What does TRUE represent?
- What does FALSE represent?
- Are null values possible?
- Can it be used directly as a business definition?

For example:

> `active_subscription`: TRUE means the account currently has an active subscription and can be used to count active accounts; FALSE means no active subscription currently.

---

## How to Validate After Configuration

After completing field semantic configuration, do not only check whether the page saved successfully — validate the effectiveness through Q&A.

It is recommended to validate at least three types of questions:

| Validation Question | Purpose |
| --- | --- |
| "Show account count by plan" | Validate whether the field can serve as a dimension. |
| "Show active account count for Google source only" | Validate whether the field can serve as a filter and match actual values. |
| "How many active accounts are there?" | Validate whether the business definition field is correctly understood. |

During validation, pay attention to:

- Whether the final answer is correct.
- Whether the **SQL Statement** uses the correct fields.
- Whether the **Logs** show that knowledge, metrics, or answer builders were matched.
- Whether filter conditions use actual field values with correct casing.
- Whether grouping fields match the user's question.

---

## Common Issues

| Issue | Possible Cause | Recommended Action |
| --- | --- | --- |
| User says "plan", system didn't use `plan` | Field alias or description not configured | Add "subscription plan, version" and similar aliases to `plan`. |
| User says "active accounts", system doesn't know which field to use | Missing business definition description or knowledge | Add a description to `active_subscription` and configure knowledge explaining the active account definition. |
| System groups by ID, results are very granular | High-cardinality field treated as dimension | Adjust field usage to avoid using ID as a default dimension. |
| Filter value casing is incorrect | System doesn't know the actual enumeration values | Check data preview; if necessary, configure index or let system first query DISTINCT. |
| A dimension field is not visible in answer builder | Field type or usage is not suitable as dimension | Check field type, field usage, and hidden status. |
| Health check flags missing field descriptions | Field semantics are incomplete | Prioritize filling in core field descriptions, then re-run health scan. |
| Virtual column can be saved but Q&A doesn't use it | Missing aliases, descriptions, or usage configuration | Continue supplementing semantic configuration after saving the virtual column, and validate with questions. |

---

## Pre-Launch Checklist

- Do core fields all have business-friendly aliases?
- Do core fields all have clear descriptions?
- Are categorical fields configured as suitable for dimension or filter?
- Are numeric fields configured as suitable for measure?
- Do time fields explain business meaning and common granularity?
- Do boolean fields clarify TRUE/FALSE meanings?
- Are high-cardinality fields avoided as default dimensions?
- Are sensitive or irrelevant fields hidden?
- Are commonly used enumeration fields configured with appropriate indexes?
- Have virtual columns been validated and supplemented with semantic configuration?
- Have multi-table join fields been manually confirmed?
- Have typical questions been used to validate SQL and logs?

The goal of field semantic configuration is not to fill in every page item, but to enable Analytics Agent to reliably understand business questions and generate SQL that matches business definitions.

## Related Documentation

- [Configure Analytics Domain](datagpt-domain-management-guide.md) — Creating and configuring the analytics domain that field semantics belong to
- [Configure Virtual Columns](datagpt-virtual-column-config-guide.md) — Creating and configuring derived fields
- [Configure Knowledge](datagpt-knowledge-config-best-practices.md) — Business definitions and term explanations, complementary to field semantics
- [Metrics and Answer Builder](metrics_answer_build.md) — Field semantics directly affect metric and answer builder parameter selection
- [Answer Builder Best Practices](datagpt-answer-builder-best-practices.md) — How field configuration affects `${filters}` and `${dims}`
