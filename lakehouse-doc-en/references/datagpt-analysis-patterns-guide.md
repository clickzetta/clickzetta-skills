# Analysis Patterns Guide

This guide is intended for business users and business analysts, explaining how to ask questions about trends, comparisons, rankings, proportions, details, anomalies, and attribution.

The Analytics Agent understands natural language. Business users do not need to learn complex templates, but can express their intent using common analytical phrasings such as "look up a number", "compare by category", "view trend", "view ranking", or "view proportion". These phrasings are closer to everyday business communication and are more likely to produce stable answers.

## Analysis Pattern Overview

Common business analysis questions can be categorized as:

| Analysis Pattern | Typical Question | Recommended Output |
| --- | --- | --- |
| Lookup | What is the value of a metric | Numeric value, brief explanation |
| Group comparison | Which categories are higher or lower | Table, bar chart |
| Trend | How does a metric change over time | Line chart, trend table |
| Ranking | Top N or Bottom N | Ranking table, bar chart |
| Proportion | What is the composition | Table, pie chart, or donut chart |
| Detail | Which records meet the criteria | Detail table |
| Anomaly | Which metrics have unusual fluctuations | Table, chart, explanation |
| Attribution | Why did a change occur | Layered comparison, explanation |
| Time-series forecast | How might things change in the future | Trend chart, forecast values, confidence intervals, risk notes |

## Lookup Questions

Lookup questions are used to confirm a single metric.

Common phrasing:

```text
What is [some number] within [some scope]?
```

Example:

```text
How many active accounts are on the Basic plan?
```

If the definition might be ambiguous, you can add a clarifying sentence in business language:

```text
Using our standard active account definition, how many active accounts are on the Basic plan?
```

Suitable scenarios:

- What is today's sales revenue.
- How many new customers were added this month.
- How many active accounts are there currently.
- What is the inventory level for a specific region.

When reading the answer, focus on:

- Whether the number represents the business object you want to see.
- Whether it is constrained to the scope you care about.
- If the question is time-related, whether you need to add a time qualifier like "this month" or "year-to-date".

## Group Comparison Questions

Group comparison questions are used to compare differences across categories.

Common phrasing:

```text
Break down by category and compare key results
```

Example:

```text
Show account health overview by plan, including account count, active accounts, active rate, total seats, and active seats
```

Suitable scenarios:

- Compare sales revenue by department.
- Compare conversion rates by channel.
- Compare gross margin by product line.
- Compare account health by plan.

Question tips:

- Use business language to specify the breakdown dimension, e.g., by plan, region, channel, department.
- State the outcomes you care about, e.g., quantity, conversion rate, cancellation rate, revenue.
- If you are unsure what to look at, start with an overview and then drill down into specific metrics.

A more general phrasing:

```text
How are the different plans performing?
```

A phrasing more likely to produce stable results:

```text
Compare account count, active accounts, active rate, and cancellation rate by plan
```

## Trend Questions

Trend questions are used to see how a metric changes over time.

Common phrasing:

```text
View the change trend by day, week, month, or quarter
```

Example:

```text
View new account trends by month
```

If you know the time range, you can add it:

```text
View the trend of new accounts by month since 2025, and display as a line chart
```

Common time granularities:

- By day.
- By week.
- By month.
- By quarter.
- By year.

Trend questions should ideally include a natural language time range, such as "last 30 days", "last 12 months", or "year-to-date". If not specified, the system will use a default range, which may not match your business expectations.

Recommended questions:

```text
View daily active account trends for the last 30 days
```

```text
Compare monthly new accounts and cancelled accounts for the last 12 months
```

```text
View active rate changes by plan, broken down by quarter
```

## Time-Series Forecast Questions

Time-series forecast questions are used to predict future trends based on historical data. They go further than ordinary trend questions — not just answering "how did things change in the past" but also providing "how things may change in the future".

Common phrasing:

```text
Track a metric by time period and predict the trend for a future period
```

Example:

```text
Track changes in active player count and achievement count by month, and predict the next 3 months
```

A more complete phrasing:

```text
Based on achievement records, track changes in active player count, total achievements, and average achievements per player by month, and predict the next 3 months. Include forecast rationale, confidence level, potential risks, and a trend chart.
```

Question tips:

- Specify the metric to forecast, e.g., active user count, order count, revenue, achievement count.
- Specify the time granularity, e.g., by day, by week, by month.
- Specify the forecast period, e.g., next 7 days, next 3 months, next quarter.
- If you know the data may be incomplete, remind the system to exclude anomalous months or incomplete periods.
- Request forecast rationale, confidence intervals, or risk notes to help assess reliability.

In practice, the Analytics Agent can first aggregate historical data by month, then run a time-series forecast and generate a forecast trend chart. The system may also automatically identify incomplete data periods — for example, excluding a month where data appears significantly lower than usual from the training window.

When reading forecast results, focus on:

- Whether the training data time range is reasonable.
- Whether incomplete or anomalous data has been excluded.
- Whether the forecast model or method is clearly explained.
- Whether confidence intervals are provided.
- Whether seasonality, trend changes, and external risks are addressed.

Forecast results are useful for trend anticipation and operational monitoring, but should not be treated as definitive commitments. For critical business decisions, it is recommended that BI analysts further verify results against business events, data freshness, and SQL logs.

## Ranking Questions

Ranking questions are used to find the highest, lowest, most, or least.

Common phrasing:

```text
Which are the most? Which are the least? Who are the Top 10?
```

Examples:

```text
Top 10 countries by account count
```

```text
Plan ranking by highest cancellation rate
```

Question tips:

- Specify what to rank by, e.g., account count, revenue, cancellation rate, conversion rate.
- Specify Top N or Bottom N clearly.
- If you only care about a specific scope or time period, add the details.

A more general phrasing:

```text
Which countries have more accounts?
```

A phrasing more likely to produce stable results:

```text
Show top 10 countries by account count in descending order
```

## Proportion Questions

Proportion questions are used to understand structure and composition.

Common phrasing:

```text
What share does each category represent?
```

Examples:

```text
Account proportion by plan
```

```text
Active account proportion by source
```

Proportion questions can sometimes be misunderstood. Business users do not need to use terms like "numerator" or "denominator", but can use natural language to clarify "proportion of what".

For example:

```text
What share do active accounts from each plan represent among all active accounts?
```

versus:

```text
Within each plan, what proportion of accounts are active?
```

These two questions have different meanings. The first looks at overall composition; the second looks at the active rate within each plan.

## Detail Questions

Detail questions are used to view specific records.

Common phrasing:

```text
List records that meet the criteria and show the information I care about
```

Example:

```text
List active accounts on the Basic plan, showing account name, country, source, and seats
```

Question tips:

- Specify which objects to list.
- Specify which business information you want to see.
- Clarify sorting if necessary.
- Limit the number of records when data volume is large.

Recommended:

```text
List the 20 accounts with the highest cancellation rate, showing account name, plan, country, seat count, and cancellation date
```

Detail questions may be affected by column hiding, row-level permissions, and analytics domain permissions. Information you cannot see will not be bypassed by asking in natural language.

## Anomaly Questions

Anomaly questions are used to detect unusual metric fluctuations.

Common phrasing:

```text
Help me check for anomalies recently and where they mainly occur
```

Examples:

```text
Check whether there are anomalous fluctuations in active rate by plan over the last 30 days
```

```text
Find channels where the cancellation rate spiked this month
```

Question tips:

- Specify which business phenomenon concerns you, e.g., rising cancellation rate, falling revenue, declining conversion rate.
- Include a time range where possible, e.g., this month, last 30 days, last 12 weeks.
- If you have a threshold, include business phrasing such as "much higher than last month" or "above 10%".

A more specific phrasing:

```text
Compare cancellation rate by plan for this month and last month, and find plans where the month-over-month increase exceeds 10%
```

## Attribution Questions

Attribution questions are used to explain "why something changed".

Common phrasing:

```text
Why did it change? What dimensions should we break it down by?
```

Examples:

```text
Why is the active rate lowest for Premium plan? Break down by source, country, and seats range
```

```text
What are the main reasons for the increase in cancelled accounts this month? Analyze by plan and source
```

A more complete phrasing:

```text
Analyze the main reasons for user activity differences: what factors are most likely to affect whether users are active? Perform attribution analysis by country, game library size, game type, achievement rarity, and achievement depth, and generate charts.
```

Attribution questions often require multiple rounds of analysis. It is recommended to start with an overview and then drill into a specific anomaly.

First round:

```text
Show account health overview by plan
```

Second round:

```text
Why is the cancellation rate highest for Premium plan? Break down by source and country
```

When reading attribution results, note:

- Attribution analysis is typically multi-dimensional comparison and correlation explanation, not strict causal proof.
- If a dimension does not exist in the current analytics domain, the system may indicate it cannot analyze by that dimension, and will substitute with actually available fields.
- Results should be viewed in terms of both "difference in active rate" and "contribution share". Some factors have a high active rate but a small sample; others have an average active rate but a large scale, making their overall impact greater.
- For important conclusions, BI analysts should check SQL and logs to confirm the correct tables, fields, filters, and grouping were used.

In practice, the Analytics Agent can generate multiple charts around an attribution question, breaking down by country, game library size, achievement rarity, game type, and achievement depth, and summarize the ranking of influencing factors. For these types of questions, when data volume is large, runtime may be significantly longer than simple lookup questions.

## Chart Output Recommendations

Different analysis patterns suit different chart types:

| Analysis Pattern | Recommended Chart |
| --- | --- |
| Trend | Line chart |
| Group comparison | Bar chart, horizontal bar chart |
| Ranking | Horizontal bar chart, ranking table |
| Proportion | Pie chart, donut chart, stacked chart |
| Multi-metric comparison | Table, combo chart |
| Detail | Table |
| Attribution | Layered bar chart, comparison table |
| Time-series forecast | Forecast line chart, confidence interval chart |

If the system's automatically selected chart does not match your expectations, you can specify in the question:

```text
View new account trends by month, displayed as a line chart
```

```text
Compare active rate and cancellation rate by plan, displayed as a bar chart
```

## From Questions to Dashboards

Not all questions need to be saved to a dashboard.

Questions suitable for dashboards:

- Reviewed daily, weekly, or monthly.
- Needed for team sharing.
- Require continuous anomaly monitoring.
- Charts clearly express the business state.
- Metric definitions are stable.

Questions not suitable for dashboards:

- One-time ad hoc queries.
- Definitions not yet confirmed.
- Data still being validated.
- Question expression depends on current context.

In practice, charts and tables from Q&A results can be saved directly to a dashboard. BI analysts can first explore using natural language, then save valuable results as dashboard components.

If you already have clearly defined metrics, you can also use the "Exploration" feature on the analysis page for structured investigation. The exploration page lists queryable metrics and answer builders, supports adding comparison analysis and global filters, and returns baseline period, comparison period, and change rate after querying. It automatically suggests drill-down fields such as `plan`, `source`, and `country`. It is suitable for validating which dimensions drive metric changes before building a dashboard.

## Sample Question Library

### Business Overview

```text
View revenue, order count, and average order value trends for the last 12 months by month
```

```text
Show revenue, month-over-month growth rate, and gross margin by business line this month
```

### User Analysis

```text
Show account count, active accounts, active rate, and cancellation rate by plan
```

```text
Show new account count and trial conversion rate by source
```

```text
View monthly active user trends and predict the next 3 months
```

```text
Analyze the main reasons for differences in user activity, broken down by channel, region, plan, and usage depth
```

### Sales Analysis

```text
Show top 10 contract amounts by sales region for this quarter
```

```text
Compare lead conversion rate by channel for this month and last month
```

### Financial Analysis

```text
Summarize accounts receivable and overdue amounts by customer type
```

```text
View collection amount trends for the last 6 months
```

### Operations Analysis

```text
Find the top 10 channels with the highest cancellation rate this week
```

```text
Compare active account count and average seat count by country
```

## Related Documentation

- [Question Asking Guide](datagpt-question-asking-guide.md) — How to ask questions that are more likely to get accurate answers
- [Reading Analysis Results](datagpt-answer-reading-guide.md) — How to determine whether an answer is trustworthy
- [Using Data and Exploration](datagpt-data-exploration-guide.md) — View analytics domain data coverage and structured exploration
- [Using Dashboards](datagpt-dashboard-bi-analyst-guide.md) — Save Q&A results as shareable dashboards
- [Recommended Questions Configuration](datagpt-recommended-questions-guide.md) — Understand recommended questions for analytics domains
