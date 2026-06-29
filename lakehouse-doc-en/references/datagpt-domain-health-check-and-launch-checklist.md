# Launching an Analytics Domain Health Check

After completing analytics domain configuration, a health scan and manual check should be conducted to confirm whether it has stable Q&A capability. The health scan is not a formality — it flags configuration issues that may affect Q&A accuracy, such as missing field descriptions, missing metrics, and anomalous table relationships.

This guide helps administrators complete quality checks before launching an analytics domain.

---

## Purpose of the Health Scan

The health scan checks data configurations in the analytics domain and flags anomalies or warnings that may affect Q&A accuracy.

According to the actual page description, the health scan focuses on:

- Missing field description information.
- Field control issues.
- Table relationship associations.
- Whether metrics are defined.
- Whether answer builders are defined.
- Data quality issues such as null value ratios.
- Risk of data bloat caused by incorrect join relationships.

Health scan results are typically categorized as:

| Level | Meaning | Handling Recommendation |
| --- | --- | --- |
| Normal | No obvious issues found currently | Still recommended to validate Q&A with typical questions. |
| Warning | May affect Q&A accuracy | Evaluate before launch whether it needs to be addressed. |
| Anomaly | Very likely to affect Q&A accuracy | Address before launch, or clearly explain why it is not being addressed. |

The health scan can help identify configuration gaps, but cannot replace business acceptance testing. It cannot automatically determine whether a business term's actual definition matches the company's definition, nor can it guarantee all user phrasings will match the correct field. A normal health scan only indicates that the current configuration has no obvious structural issues — typical natural language questions should still be used to check answers, SQL, and logs before launch.

---

## Health Scan Entry Point

General path to access the health scan:

1. Go to **Management** -> **Analytics Domain Management**.
2. Open the target analytics domain.
3. View **Data Health** on the **Basic Information** tab.
4. Click **Re-scan** to submit a new scan task.

Note that re-scanning may be an asynchronous task. After clicking, the page may first show "Re-scan task submitted successfully", and the health scan results may not refresh immediately. It is recommended to re-enter the page or check the update time again after a moment.

---

## Common Health Issues

### Missing Field Descriptions

In practice, the health scan has prompted:

> Table field is missing description information

Missing field descriptions affect the system's ability to understand field meanings. For example, without a description, the system may not know that `active_subscription` indicates whether the current subscription is valid, and may not be able to stably answer questions about "active accounts".

Handling recommendations:

- Prioritize adding descriptions for core fields first.
- For ambiguous fields, clearly describe applicable and non-applicable scenarios.
- For boolean fields, clearly describe the business meaning of TRUE/FALSE.
- For time fields, clearly describe the business meaning, such as creation time, cancellation time, or payment time.

### No Metrics in the Analytics Domain

The health scan may prompt:

> No metrics exist in the domain

This means the current analytics domain lacks reusable calculation definitions. Without metrics, the system may still generate SQL ad hoc, but the definitions for the same question are more likely to be inconsistent.

Handling recommendations:

- Create metrics for high-frequency, simple, stable aggregation definitions.
- Manually review auto-generated metrics rather than directly adopting all of them.
- Add business-friendly names, aliases, and descriptions to metrics.

### Missing Answer Builders

If the analytics domain contains complex definitions, multi-metric combinations, multi-table JOINs, or detail queries, but has no answer builders, the system may generate SQL ad hoc every time.

Handling recommendations:

- Lock complex SQL into answer builders.
- Use `${filters}` to support dynamic filtering.
- Use `${dims}` to support dynamic grouping.
- Add output metric names, aliases, and descriptions.

### Anomalous or Missing Table Relationships

Multi-table analysis depends on correct table relationships. If join relationships are wrong, results may be inflated, duplicated, or missing.

Handling recommendations:

- After adding multiple tables, test auto-association.
- Manually confirm auto-association results.
- If auto-association produces no results, do not assume multi-table Q&A is reliable.
- Use typical multi-table questions to check whether JOINs in the SQL are correct.

### Anomalous Field Null Values or Cardinality

When a field has many null values or excessively high cardinality, it may affect filtering, grouping, and chart display.

Handling recommendations:

- Review **Statistical Analysis** in the table details.
- Pay attention to `NULL VALUE`, `DISTINCT`, `MIN`, `MAX`.
- High-cardinality fields are not recommended as default dimensions.
- Fields with many null values are not recommended as core filter conditions unless null value logic is explicitly handled.

---

## Pre-Launch Manual Checklist

The health scan cannot replace manual checks. Before officially launching, confirm the following items one by one.

### 1. Analytics Domain Basic Information

- Whether the analytics domain name is clear.
- Whether the description explains the applicable business scope.
- Whether the data source is correct.
- Whether permissions are configured for the correct users or roles.
- Whether recommended questions can cover core use cases.

### 2. Table Configuration

- Whether only the tables needed for the current analytics domain have been added.
- Whether table display names are business-friendly.
- Whether table descriptions explain the business meaning and granularity of the table.
- Whether unrelated tables have been excluded from the domain.
- Whether grayed-out unselectable tables have been confirmed as already added via "Select Existing Tables".

### 3. Field Semantics

- Whether core fields have aliases.
- Whether core fields have descriptions.
- Whether field types are reasonable.
- Whether field purposes are reasonable.
- Whether high-cardinality fields are avoided as default dimensions.
- Whether sensitive or unrelated fields are hidden.
- Whether commonly used enumeration fields are suitable for indexing.
- Whether virtual columns have been validated and semantic configurations added.

### 4. Knowledge Configuration

- Whether core business terms have knowledge configured.
- Whether synonyms are written into knowledge.
- Whether business definitions clearly state fields and calculation rules.
- Whether knowledge is associated with the current analytics domain.
- Whether knowledge status is enabled.
- Whether logs confirm that knowledge can be found.

### 5. Metric Configuration

- Whether high-frequency simple metrics are configured.
- Whether auto-generated metrics have been manually confirmed.
- Whether metric names are business-friendly.
- Whether metric aliases cover common user phrasings.
- Whether metric descriptions clearly state the calculation definition.
- Whether metrics have been added to the current analytics domain and enabled.

### 6. Answer Builder Configuration

- Whether complex definitions are locked in answer builders.
- Whether SQL passes the run validation.
- Whether `${filters}` is configured.
- Whether `${dims}` is configured when dynamic grouping is needed.
- Whether filter fields and dimension fields are correctly bound.
- Whether output fields have business-friendly metric names, aliases, and descriptions.
- Whether validation has been done with preview and natural language questions.

### 7. Table Relationship Configuration

- Whether table relationships are configured for multi-table scenarios.
- Whether auto-association results have been manually confirmed.
- Whether join fields are unique or conform to the business granularity.
- Whether multi-table questions have been used to validate SQL.
- Whether incorrect joins that could cause data bloat have been avoided.

### 8. Q&A Validation

- Whether a fixed set of test questions has been prepared.
- Whether the final answers have been reviewed.
- Whether SQL statements have been reviewed.
- Whether logs have been reviewed.
- Whether the hit paths for knowledge, metrics, and answer builders are confirmed.
- Whether filters, grouping, and output columns match expectations.

---

## Recommended Launch Threshold

It is recommended to meet the following criteria before opening to business users:

| Check Item | Recommended Standard |
| --- | --- |
| Health scan | No unexplained anomaly items. |
| Field semantics | Core fields have aliases and descriptions. |
| Knowledge | Core business definitions have knowledge explanations. |
| Metrics | High-frequency simple metrics are configured. |
| Answer builders | Complex definitions are locked in and validated. |
| Table relationships | Multi-table JOINs have been manually confirmed. |
| Validation questions | Core questions pass testing. |
| Permissions | Users can only access data they should access. |

For non-core questions, configuration can be supplemented gradually; but core business definitions, core fields, and core metrics should be completed before launch.

---

## Health Issue Handling Priority

If the health scan or manual check finds multiple issues, it is recommended to handle them in the following order:

1. Permission and sensitive field issues.
2. Incorrect or missing table relationships.
3. Missing descriptions for core fields.
4. Missing knowledge for core business definitions.
5. Missing high-frequency metrics.
6. Missing answer builders for complex definitions.
7. Recommended questions and experience optimization.

The reason is that permission and JOIN issues can cause serious errors or data leakage; fields, knowledge, metrics, and answer builders affect Q&A accuracy; recommended questions mainly affect user experience.

---

## Common Questions

| Question | Explanation | Handling Suggestion |
| --- | --- | --- |
| Results don't update immediately after re-scan | Scan may be an asynchronous task | Refresh after a moment or re-enter the analytics domain to check. |
| Health scan says no metrics, but I just added some | Health scan may still show old results | Re-scan and confirm metrics have been added to the current analytics domain. |
| Many field descriptions — do they all need to be added? | Not necessary to complete all at once | Start with core fields, high-frequency fields, and easily ambiguous fields. |
| Can auto-generated metrics be launched directly? | Not recommended | Auto-generation is only a candidate suggestion; manual confirmation of definitions is required. |
| What if auto-association has no results? | Means the system did not identify a reliable relationship | Manually confirm the relationship, or temporarily not support that multi-table question. |
| Does a normal health scan mean Q&A is definitely correct? | No | Typical natural language questions still need to be validated. |

---

## Final Delivery Checklist

Use the following final checklist before launch:

- Analytics domain name and description are clear.
- Data table scope is correct.
- Core field semantics have been added.
- Sensitive fields are hidden or controlled via underlying permissions.
- Core knowledge is configured and validated to be found.
- Core metrics are configured and validated.
- Complex definition answer builders are configured and validated.
- Multi-table relationships are confirmed.
- Health anomalies are addressed or explained.
- Typical questions have been validated for answers, SQL, and logs.
- The applicable scope and limitations of the current analytics domain are documented.

The goal of the health scan is not to make the page look like it has "no red dots", but to give the analytics domain a stable, explainable, and reusable Q&A capability.

## Related Documentation

- [Configuring Analytics Domains](datagpt-domain-management-guide.md) — Creating and configuring data in analytics domains
- [Configuring Field Semantics](datagpt-field-semantic-config-guide.md) — Configuring field aliases, descriptions, and purposes
- [Configuring Knowledge](datagpt-knowledge-config-best-practices.md) — Business definitions and term explanations
- [Metrics and Answer Builders](metrics_answer_build.md) — Creating and configuring metrics and answer builders
- [Validating Q&A Effectiveness](datagpt-domain-qa-validation-guide.md) — Using typical questions to validate whether configurations are effective
