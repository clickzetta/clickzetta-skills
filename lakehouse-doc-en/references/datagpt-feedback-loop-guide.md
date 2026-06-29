# Handling Feedback

This document explains how business users submit feedback in the Analytics Agent, how to view feedback centrally on the management side, and how maintainers can use feedback to improve Q&A accuracy.

Feedback is not simply a "thumbs up / thumbs down". In enterprise scenarios, feedback is an important loop that connects business users, BI analysts, semantic layer maintainers, and administrators. It can help teams identify field ambiguity, metric definition errors, missing knowledge, inaccurate charts, unreasonable permission configurations, and other issues.

## Applicable Users

- Business users: Submit feedback when answers are inaccurate or charts are wrong.
- BI analysts: Improve question design, dashboards, and charts based on feedback.
- Semantic layer maintainers: Correct field semantics, metrics, knowledge, and answer builders based on feedback.
- Administrators: Review feedback on the management side, drive issue assignment and governance.

## Feedback Entry Points

Two feedback entry points have been validated in practice.

### Instant Feedback Next to the Answer

There is a feedback icon on the right side of Q&A answers.

In practice:

- After clicking positive feedback, the page shows "Well done, encouraging!".
- After clicking the other feedback entry, the page shows "Submit calibration feedback".

Business users can use this entry to express:

- The answer is helpful.
- The answer is inaccurate.
- The chart is displayed incorrectly.
- The metric definition is wrong.
- The system misunderstood the question.

### Feedback Under the Management Menu

Expanding "Management" in the left navigation shows a "Feedback" menu.

Path:

```text
Management > Feedback
```

Page URL:

```text
/dataai/feedback
```

This is the page where feedback from users is centrally viewed on the management side.

## Management-Side Feedback Page

In practice, the feedback page contains:

- Page title: Feedback.
- Search input box: Search by question text.
- Filter buttons.
- Feedback list table.

Table fields include:

- Question text.
- Creator.
- Creation time.
- Description.

Sample feedback already in the system in practice:

```text
Question: Which games have the highest player achievements? Top 10 achievements
Creator: qiliang
Creation time: 2026-02-27 10:54:53
Description: Analysis inaccurate, chart displayed incorrectly
```

This shows that issues submitted by business users are captured on the management side in the form of question text and descriptions for subsequent investigation.

## How Business Users Submit Effective Feedback

The more specific the feedback, the easier it is for maintainers to locate the problem. Business users do not need to judge whether SQL, fields, or configurations are wrong — they only need to describe what is wrong from a business perspective.

Not recommended:

```text
The answer is wrong
```

Recommended:

```text
The chart for this question is wrong. The Top 10 should be ordered by achievement count descending, but the current chart doesn't seem to be sorted by achievement count.
```

Recommended to include:

- The original question.
- Type of error.
- Where you think it is wrong.
- The correct definition or expected result.
- Whether it affects the chart, table, text explanation, value, or business scope.
- If you know the correct example, include it.

## Common Feedback Types

### Inaccurate Analysis

Symptoms:

- Values are inconsistent with the business system.
- Trend direction does not match reality.
- Ranking result is clearly wrong.
- Unrelated objects were returned.

Possible causes:

- Field semantics are unclear.
- Metric definition is not configured.
- Knowledge was not found.
- SQL filter conditions are wrong.
- Too many tables in the analytics domain; system selected the wrong table.

Handling direction (executed by BI analysts, semantic layer maintainers, or administrators):

- Review SQL statements.
- Review logs.
- Check field semantics.
- Check metrics and answer builders.
- Add knowledge if necessary.

### Chart Display Error

Symptoms:

- Chart type is unsuitable for the question.
- Sorting does not match expectations.
- Chart and table are inconsistent.
- Wrong chart dimensions or metrics selected.

Possible causes:

- Question did not specify the output method.
- System-selected chart does not match business expectations.
- Metric fields or dimension fields are not configured clearly.
- Answer builder output fields lack business-friendly names.

Handling direction (executed by BI analysts or semantic layer maintainers):

- Specify chart type in the question.
- Optimize answer builder output field names.
- Consolidate standard phrasings in recommended questions.
- If necessary, save the correct chart to a dashboard.

### Definition Error

Symptoms:

- Active users, revenue, conversion rates, and other metric definitions do not match business definitions.
- Wrong numerator or denominator selected.
- Deduplication behavior does not match expectations.

Possible causes:

- Metric is not configured.
- No definition explanation in knowledge.
- Too many same-name fields.
- Different departments use different definitions.

Handling direction (executed by semantic layer maintainers):

- Add metric configuration.
- Add knowledge.
- Clearly state business meaning in field semantics.
- Split conflicting definitions into different analytics domains.

### Wrong Field Selected

Symptoms:

- System used a similar but wrong field.
- Multiple tables have the same field name; system selected the wrong one.
- Business term mapped to the wrong field.

Possible causes:

- Field names are similar.
- Field semantics are missing.
- Field purpose is not clearly configured.
- Fields that should not be exposed are not hidden.

Handling direction (executed by semantic layer maintainers):

- Add field semantics, aliases, and descriptions.
- Hide fields that are prone to misuse.
- Configure field purpose as a more accurate type.
- Apply column-level hiding to sensitive or deprecated fields.

### Permission or Data Scope Issue

Symptoms:

- User cannot see expected data.
- User's visible data scope differs from colleagues.
- Detail query returns fewer results than expected.

Possible causes:

- Analytics domain permissions differ.
- Row-level permissions are in effect.
- Column hiding is in effect.
- User role authorization differs.

Handling direction (executed by administrators or permission maintainers):

- Check analytics domain access permissions.
- Check role authorization.
- Check row-level permissions.
- Check column hiding configuration.

## Feedback Handling Process

It is recommended to establish the following closed loop:

1. Business users submit feedback next to the answer.
2. Administrator or operations staff reviews feedback in Management > Feedback.
3. Determine the issue type based on question text, creator, creation time, and description.
4. Assign the issue to a BI analyst, semantic layer maintainer, or administrator.
5. BI analyst or maintainer reviews SQL statements and logs for the original question.
6. Modify field semantics, metrics, knowledge, answer builders, recommended questions, or permission configurations.
7. Re-validate using the original question.
8. If the issue is widespread, consolidate it as a recommended question, dashboard, or troubleshooting case.

## How Different Roles Handle Feedback

### Business Users

Responsible for:

- Explaining where the answer does not match business expectations.
- Providing the correct definition or reference result.
- Re-validating the answer after it is fixed.

### BI Analysts

Responsible for:

- Determining whether the issue is due to an unclear question phrasing.
- Optimizing recommended questions.
- Adjusting dashboard charts.
- Consolidating high-frequency questions as dashboards or standard analysis questions.

### Semantic Layer Maintainers

Responsible for:

- Correcting field semantics.
- Configuring metrics.
- Configuring answer builders.
- Adding knowledge.
- Investigating SQL and logs.

### Administrators

Responsible for:

- Viewing the feedback list.
- Assigning issues.
- Checking permissions and audits.
- Driving governance closure.

## Mapping Between Feedback and Configuration Items

| Feedback Symptom | Prioritize Checking |
| --- | --- |
| Wrong field selected | Field semantics, field aliases, field purposes, column hiding |
| Metric calculated incorrectly | Metric configuration, answer builders, knowledge definitions |
| Chart wrong | Output field names, chart type, sorting, answer builders |
| Wrong table selected | Analytics domain table scope, table descriptions, table relationships |
| Data scope wrong | Analytics domain permissions, role authorization, row-level permissions |
| Explanation does not match business | Knowledge configuration, recommended questions, answer builder descriptions |
| Question frequently misunderstood | Recommended questions, field semantics, knowledge, analytics domain boundaries |

## Feedback Handling Priority

It is recommended to order by impact scope:

### P0

- Permission escalation or sensitive data exposure.
- Core business metrics clearly wrong.
- Key charts in shared dashboards are wrong.

### P1

- High-frequency questions have unstable answers.
- Important department feedback on definition errors.
- Chart display errors affecting understanding.
- Field misselection causing conclusion bias.

### P2

- Individual temporary question phrasing is unclear.
- Chart type is not ideal but data is correct.
- Explanatory text is not business-friendly enough.
- Recommended questions need optimization.

## How to Verify Feedback Has Been Fixed

After fixing, do not just check whether the configuration page saved successfully. It is recommended to re-run the original question.

Validation steps:

1. Re-ask the original question.
2. Review the final answer.
3. Business users confirm whether the result matches business expectations.
4. BI analyst or maintainer reviews SQL statements and logs.
5. Compare results before and after the fix.
6. Have the user who submitted the feedback confirm.
7. If it affects a dashboard, enter the dashboard to check whether the chart refreshed correctly.

## Relationship with Audit Logs

Feedback tells you "what users think is wrong"; audit logs tell you "who did what and when".

When feedback involves permissions, configuration changes, or dashboard changes, use the audit log together to investigate:

- Whether anyone modified the analytics domain.
- Whether anyone adjusted roles or authorization.
- Whether anyone modified the data source.
- Whether anyone adjusted the dashboard.

Only by combining feedback and audit logs can a complete governance loop be formed.

## Related Documentation

- [Reading Analysis Results](datagpt-answer-reading-guide.md) — How to determine whether an answer is trustworthy and submit feedback
- [Question Asking Guide](datagpt-question-asking-guide.md) — How to ask questions that are more likely to get accurate answers
- [Configuring Field Semantics](datagpt-field-semantic-config-guide.md) — Field semantics corrections pointed to by feedback
- [Answer Builder Best Practices](datagpt-answer-builder-best-practices.md) — Answer builder optimization pointed to by feedback
- [Troubleshooting Q&A Accuracy Issues](datagpt-qa-accuracy-troubleshooting-guide.md) — Systematic diagnostic methods
- [Viewing Audit Logs](datagpt-audit-log-guide.md) — Using audit logs to investigate configuration changes
