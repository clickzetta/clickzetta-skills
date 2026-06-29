# Reading Analysis Results

This guide is for business users and business analysts. It explains how to read responses from the Analytics Agent, how to determine whether an answer is trustworthy, and what to do when an answer does not meet expectations.

An Analytics Agent response is usually more than the final text. A complete response may include values, text explanations, tables, charts, SQL statements, execution logs, knowledge references, automatic monitoring suggestions, and feedback entry points. Reading all of this correctly helps you judge whether an answer can be used for business decisions.

![](.topwrite/assets/anim-38-answer-reading.svg)

## Read the Conclusion First, Then the Evidence

The recommended reading order is: start with the final conclusion and charts, then examine SQL statements and logs. Ordinary business users focus on the first 3 items; BI analysts or domain maintainers review SQL statements and logs only when investigating important issues.

1. Check whether the final conclusion answers your question.
2. Check whether the chart or table is consistent with the conclusion.
3. Check whether the business objects, scope, time, and breakdown approach match your question.
4. For important answers, have a BI analyst or maintainer review the SQL statements.
5. For anomalous answers, have a BI analyst or maintainer review the logs.
6. If the answer is wrong, submit calibration feedback.

Do not rely solely on the final natural language summary. The natural language summary may be an interpretation of query results — business users should first confirm whether the answer aligns with business intuition. When tracing the data source and execution process, BI analysts or maintainers should then verify using SQL statements and logs.

## Common Content in Results

### Values

When you ask "how many", "what is", or "what is the proportion", the system may return a single value directly.

Practical example:

```text
How many active accounts are on the Basic plan?
```

System returns:

```text
445
```

And explains that the result is based on the active account definition and the `plan = 'Basic'` condition.

When reading this type of answer, focus on:

- What unit is the value in.
- Whether any filter conditions were applied.
- Whether the expected business definition was used.
- Whether knowledge or metrics were referenced.

### Tables

When a question involves details, Top N, or group comparisons, the system may return a table.

Tables are suitable for answering:

- What is the value for each dimension.
- Which records meet the criteria.
- Top N or detail lists.
- Side-by-side comparison between metrics.

When reading a table, focus on:

- What business objects the rows represent.
- What metrics or attributes the columns represent.
- Whether there is any sorting.
- Whether only part of the data is displayed.
- Whether you need to download the full dataset.

### Charts

When a question is suitable for comparison, trends, or proportions, the system generates a chart. In practice, when asking "show account health overview by plan", the system generated a comparison chart displaying active rate, cancellation rate, and trial conversion rate for different plans.

Charts help you quickly see:

- Which category is highest or lowest.
- Whether a trend is rising, falling, or fluctuating.
- Whether there are obvious differences between metrics.
- Whether anomalous values exist.

Charts are not the final authority. Important analysis should first be verified against tables and business definitions; if it will be used for reporting or decision-making, BI analysts should further verify using SQL statements and logs.

## Operations on Charts and Tables

There are action buttons in the upper right corner of tables and charts in Q&A results. Verified in practice:

- Tables can be saved to a dashboard.
- Charts can be saved to a dashboard.
- Table menu includes full-screen view and download full data.
- Chart menu includes full-screen view, download as PNG, view as table, and download full data.

If a result needs to be reviewed continuously, save it to a dashboard for BI analysts to maintain.

## Saving to a Dashboard

Charts and tables from Q&A results can be saved directly to a dashboard.

Practical flow:

1. Find the chart or table in the Q&A result.
2. Click the "Save to Dashboard" icon.
3. In the popup, choose to create a new dashboard or save to an existing one.
4. Enter the dashboard name when creating a new one.
5. Select visibility: only visible to me, or shared.
6. Click confirm.

After saving, you can see the new dashboard in the dashboard list. In practical validation, a newly created dashboard shows:

- Dashboard name.
- Number of charts.
- Associated domain.
- Update time.

This means a Q&A result can become a persistent analysis asset for ongoing viewing.

## SQL Statements

Below the answer there is a "SQL Statements" entry. It is used to view the data query logic the system generated or executed for this question.

SQL statements are primarily intended for BI analysts, data engineers, and domain maintainers. Ordinary business users do not need to be able to read SQL as a prerequisite for using the Analytics Agent.

When to review SQL:

- The answer will be used for reporting or decision-making.
- The value does not match expectations.
- You suspect filter conditions are wrong.
- You suspect the system selected the wrong field.
- You need to confirm whether the correct dimensions were used for grouping.
- You need to communicate issues with a data engineer or analyst.

BI analysts or maintainers should focus on:

- Whether the table name looks like the correct business table.
- Whether the WHERE clause includes your specified filter conditions.
- Whether GROUP BY includes the dimensions you requested.
- Whether the metric calculation conforms to the business definition.
- Whether LIMIT or ordering is appropriate for Top N questions.

If business users cannot read SQL, there is no need to judge independently — submit the question, screenshot, or feedback to a BI analyst or domain maintainer.

## Logs

Below the answer there is a "Logs" entry. Logs are used to view the Analytics Agent's execution process.

In practice, logs can show:

- Execution status.
- Execution time.
- Timestamp.
- Knowledge retrieval steps.
- Document retrieval steps.
- Table discovery process.
- Metric calculation process.
- Tool call process.

Logs are useful for answering "why did the system respond this way".

When an answer is inaccurate, logs are more valuable for troubleshooting than the final text. They help maintainers determine whether the issue is:

- Knowledge was not found.
- The wrong knowledge was found.
- The wrong table was selected.
- The wrong field was selected.
- Filter conditions were misunderstood.
- Metric or answer builder configuration is inappropriate.
- Chart generation did not match expectations.

## Retry

Below the answer there is a "Retry" entry. Suitable for the following scenarios:

- Network or execution anomaly.
- Results were not returned completely.
- You just adjusted the question phrasing and want to regenerate.
- An administrator just corrected a configuration and you need to re-validate.

If the same question remains incorrect after repeated retries, relying solely on retry is not recommended. Business users should submit feedback; BI analysts or maintainers should then review SQL statements and logs.

## Automatic Monitoring Suggestions

When a question has ongoing monitoring value, automatic monitoring suggestions may appear in the answer.

In practice, after answering the account health overview question, the system provided an automatic monitoring suggestion: set up daily automatic checks so that when a plan's active rate fluctuates abnormally or the cancellation rate spikes, the user is notified and the reason is analyzed.

This type of suggestion is suitable for:

- Metrics that require periodic attention.
- Anomalies that need prompt detection.
- Questions that are not one-time queries but ongoing operational monitoring.
- BI analysts who want to convert Q&A into dashboards or scheduled tasks.

Business users can respond to the suggestion by choosing whether to enable it. Whether a task can actually be created depends on system configuration and permissions.

## Feedback Entry Points

There is a feedback entry point on the right side of the answer. Two actions have been verified in practice:

- Positive feedback: the page shows "Well done, encouraging!".
- Calibration feedback: the page shows "Submit calibration feedback".

When an answer is correct and helpful, submit positive feedback.

When an answer is wrong, submit calibration feedback and use business language to describe:

- Which question's answer is wrong.
- What is wrong.
- What the expected answer or correct definition is.
- Whether it is a chart error, value error, scope error, time error, or explanation error.

These feedbacks go into the management-side feedback list for maintainers to handle in bulk.

## How to Determine Whether an Answer Is Trustworthy

### Answers That Can Be Used Directly

Typically have the following characteristics:

- Question is clearly expressed.
- Answer explicitly addresses the question.
- Chart or table is consistent with the text conclusion.
- Business objects, scope, time, and breakdown approach match expectations.
- Business definition matches the team's common understanding.
- If reviewed by a BI analyst or maintainer, SQL statements and logs also show no anomalies.

### Answers That Require Caution

If any of the following occur, it is not recommended to use the answer directly for reporting:

- The answer does not explain its definition.
- Chart and text conclusion are inconsistent.
- The breakdown was not done as requested.
- Time range is different from expected.
- Used data objects that are unfamiliar or inconsistent with business knowledge.
- The maintainer found in the logs that no relevant knowledge or configuration was found.
- Results clearly violate business intuition.

### Answers Where Feedback Should Be Submitted

Submit calibration feedback in the following situations:

- Analysis is inaccurate.
- Chart is displayed incorrectly.
- Metric definition is wrong.
- Field meaning was misunderstood.
- Unrelated data was returned.
- Key filter conditions were missing.
- The correct answer depends on business knowledge that has not been configured.

## Division of Responsibilities Between Business Users and Maintainers

Business users are responsible for:

- Expressing questions clearly.
- Judging whether the answer matches business intuition.
- Describing which business objects, scope, time, or definition does not match expectations.
- Submitting feedback for incorrect answers.

BI analysts are responsible for:

- Translating business feedback into reviewable issues.
- Reviewing SQL statements and logs for important results.
- Judging whether dashboards, recommended questions, or standard phrasings need adjustment.

Maintainers are responsible for:

- Reviewing the feedback list.
- Correcting field semantics, metrics, knowledge, answer builders, or permission configurations.
- Re-validating typical questions.
- Converting high-value questions into recommended questions or dashboards.

## Related Documentation

- [Question Asking Guide](datagpt-question-asking-guide.md) — How to ask questions that are more likely to get accurate answers
- [Analysis Patterns Guide](datagpt-analysis-patterns-guide.md) — Common analysis patterns such as trends, comparisons, rankings, and proportions
- [Using Dashboards](datagpt-dashboard-bi-analyst-guide.md) — Save Q&A results as shareable dashboards
- [Handling Feedback](datagpt-feedback-loop-guide.md) — Submit feedback to help improve the system
- [Troubleshooting Q&A Accuracy Issues](datagpt-qa-accuracy-troubleshooting-guide.md) — Diagnostic methods when answers are inaccurate
