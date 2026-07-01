# Using Dashboards

This guide is for BI analysts and business analysts. It explains how to save Analytics Agent Q&A results into dashboards and maintain sustainable business analysis assets. Ordinary business users primarily view dashboards, ask follow-up questions around them, and submit feedback — they do not need to directly maintain dashboard configurations.

Dashboards are not a daily work object for administrators. Administrators are responsible for users, roles, permissions, audits, and governance; BI analysts are responsible for organizing business questions, metric definitions, and charts into dashboards that can be continuously viewed by the team.

![](.topwrite/assets/anim-39-question-to-dashboard.svg)

## What Problems Dashboards Solve

Dashboards are suitable for locking in business questions that need to be viewed repeatedly, such as:

- Daily business overview.
- Sales funnel monitoring.
- User activity and churn monitoring.
- Financial collections monitoring.
- Operations campaign effectiveness review.
- Account health overview.

One-time questions can be completed directly in Q&A; high-value, periodic, team-shared questions are suitable for consolidation into dashboards.

## Role Responsibilities

### BI Analysts / Business Analysts

Responsible for:

- Designing dashboard themes.
- Selecting valuable charts and tables from Q&A results.
- Saving charts/tables to dashboards.
- Maintaining dashboard names, layouts, and sharing status.
- Explaining metric changes.
- Adjusting questions, charts, and metric definitions based on feedback.

### Business Users

Responsible for:

- Viewing shared dashboards.
- Making business judgments around dashboards.
- Submitting feedback on inaccurate or hard-to-understand results.
- Raising new analysis needs with BI analysts.

### Administrators

Responsible for:

- Configuring users, roles, and permissions.
- Managing analytics domain access scope.
- Reviewing audit logs.
- Handling governance boundary issues.

Administrators should not take on daily dashboard content development work.

## Saving Charts/Tables from Q&A to a Dashboard

In practical validation, both charts and tables from Analytics Agent Q&A results can be saved directly to a dashboard.

Process:

1. Ask a question on the analysis page.
2. Wait for the system to generate a table or chart.
3. Click the "Save to Dashboard" icon in the upper right corner of the chart or table.
4. In the popup, choose to create a new dashboard or add to an existing one.
5. Enter the dashboard name when creating a new one.
6. Select visibility: visible only to me, or shared.
7. Click confirm.

After saving successfully, the system shows a save success notification. Go to the dashboard list to see the new dashboard.

In practice, a dashboard saved from a Q&A chart shows:

- 1 chart.
- Associated domain as the current analytics domain.
- Update time as the time of saving.

This confirms that dashboard components inherit the Q&A result and analytics domain context.

## How to Name a Dashboard When Creating One

Dashboard names should reflect the business theme, not a one-time question.

Not recommended:

```text
Test Q&A chart dashboard
```

Recommended:

```text
Account Health Monitoring Dashboard
```

```text
Sales Conversion Analysis Dashboard
```

```text
Financial Collections Tracking Dashboard
```

Naming recommendations:

- Include the business object.
- Include the analysis purpose.
- Avoid temporary, test, or personal naming.
- If it is a topic-specific dashboard, include the topic name.

## Visibility Selection

When saving to a dashboard, you can choose:

- Visible only to me.
- Shared.

Recommendations:

- Use "visible only to me" during the draft phase.
- Share only after metric definitions are confirmed.
- Do not arbitrarily share dashboards containing sensitive data.
- Before sharing, confirm that analytics domain permissions and row-level permissions align with business boundaries.

Sharing is not a substitute for permission governance. Whether a user can view dashboard content should still be constrained by analytics domain, resource permissions, row-level permissions, and column hiding configurations.

## Dashboard List

The dashboard entry is in the "Dashboards" menu in the left navigation.

In practice, the dashboard list contains:

- My Dashboards.
- Shared Dashboards.
- Create New Dashboard.

Visible fields in My Dashboards include:

- Name.
- Number of charts.
- Associated domain.
- Update time.

Shared Dashboards show the creator, so business users can know the source of the dashboard.

Row actions include:

- Share or unshare.
- Delete.

Delete is a destructive operation and should be used with caution.

## Dashboard Detail Page

After entering the dashboard detail page, you can see:

- Dashboard name.
- ASK AI.
- Version history.
- Chart titles.
- Chart update times.
- Next update time hints.

In practice, charts saved from Q&A showed an update time, and indicated the next update would be approximately 24 hours later. This shows dashboards are not simple screenshots but analysis components that can continuously refresh data.

## Chart Operations

Charts in a dashboard support full-screen viewing.

Practical notes:

- Clicking the full-screen icon on a chart enters full-screen mode.
- After entering full-screen, click the close button in the upper right corner to exit.
- Pressing Esc does not close a full-screen chart.

This should be noted in user training to prevent users from not knowing how to return after entering full-screen.

## ASK AI

The dashboard detail page has an ASK AI button.

In practice, clicking it opens a question input area on the right side of the page associated with the current dashboard, showing:

```text
Associated dashboard: dashboard name
```

ASK AI also shows popular question searches and question history.

This means BI analysts and business users can continue asking follow-up questions around the current dashboard. For example:

```text
Why is the active rate lowest for Premium plan?
```

```text
Show account health overview for Google source only
```

```text
Break down the metrics in the current dashboard by country
```

Usage recommendations:

- Viewers can continue exploring around the dashboard.
- BI analysts can discover new dashboard components from follow-up questions.
- If follow-up questions produce stable value, they can continue to be saved to the dashboard.

## Version History

The dashboard detail page has a version history entry.

In practice, version history shows:

- Version numbers, e.g., V1, V2.
- Current version marker.
- Operator.
- Operation time.
- Change description, e.g., dashboard layout change.

Version history answers:

- When the dashboard was changed.
- Who changed the dashboard.
- Whether the current version is the latest.
- Whether a layout change occurred.

If a business user reports "the dashboard looks different from yesterday", the BI analyst should first check the version history before judging whether the difference is a data refresh, a layout adjustment, or a chart configuration change.

## Advanced Edit

The more menu in the upper right corner of the dashboard detail page has "Advanced Edit".

In practice, clicking it opens a "Configure Dashboard" dialog containing:

- Dashboard name.
- JSON configuration editor.
- Cancel.
- Confirm.

Visible fields in the JSON configuration include:

```json
{
  "charts": ["48"],
  "chartTabs": null,
  "layout": {
    "chartPositions": [
      {
        "x": 0,
        "y": 0,
        "w": 6,
        "h": 9,
        "i": "48"
      }
    ]
  },
  "globalParams": [],
  "crossFilters": null
}
```

The fields can be understood as:

- `charts`: Which chart components the dashboard contains.
- `layout.chartPositions`: Position and size of charts in the dashboard.
- `globalParams`: Global parameters.
- `crossFilters`: Cross-filter configuration for interactions between charts.

Advanced edit is suitable for BI analysts familiar with the configuration structure. Ordinary business users should not modify it directly.

Usage recommendations:

- Confirm the current version before making changes.
- Do not save if you are unsure about the JSON meaning.
- Test complex layout adjustments in a test dashboard first.
- Check version history after making changes.
- Have business users re-verify key questions after changes.

## Dashboard Development Methodology

### Start from Questions, Not from Charts

First clarify the questions the dashboard should answer:

```text
Is account health normal?
```

Then break it down into metrics:

- Total account count.
- Active account count.
- Active rate.
- Cancellation rate.
- Trial conversion rate.
- Average seat count.

Then select charts:

- Overview metric cards.
- Bar chart comparing by plan.
- Line chart showing trend over time.
- Anomaly detail table.

### Explore First, Then Consolidate

Recommended process:

1. Explore using natural language on the analysis page.
2. Review answers, charts, tables, and business definitions.
3. When needed for sharing or decision-making, have BI analysts review SQL statements and logs.
4. For stable metrics, use the "Exploration" page to validate baseline and comparison period.
5. Check change rates and auto-drill-down fields to confirm which breakdown dimensions are worth displaying.
6. Confirm reusable questions.
7. Save charts/tables to a private dashboard.
8. Adjust the dashboard organization.
9. Have business stakeholders validate.
10. Share with the team.

Do not share unvalidated one-time charts directly with the business team.

### Control Dashboard Complexity

A dashboard should not try to cover all questions.

Recommendations:

- One dashboard for one stable business topic.
- Place the most important metrics on the first screen.
- Do not include too many charts.
- Keep metrics with the same definition together.
- Split different topics into different dashboards.

## When Not to Build a Dashboard

The following situations are not suitable for immediately building a dashboard:

- Metric definitions not yet confirmed.
- Q&A results still unstable.
- Data source still being adjusted.
- Only one-time analysis value.
- Sensitive data involved but permissions not confirmed.
- Business users do not yet have a clear use case.

## Pre-Launch Checklist

Before sharing a dashboard, check:

- Dashboard name is clear.
- Associated domain is correct.
- Core charts can refresh correctly.
- Chart titles are understandable by business users.
- Metric definitions are confirmed.
- Important charts have been reviewed by BI analysts (SQL statements and logs).
- Typical business questions have been validated.
- Visibility is confirmed.
- Sensitive fields are confirmed to not be exposed.
- Version history is preserved.

## Related Documentation

- [Question Asking Guide](datagpt-question-asking-guide.md) — How to ask questions that are more likely to get accurate answers
- [Reading Analysis Results](datagpt-answer-reading-guide.md) — How to determine whether an answer is trustworthy
- [Analysis Patterns Guide](datagpt-analysis-patterns-guide.md) — Common analysis patterns such as trends, comparisons, rankings, and proportions
- [Using Data and Exploration](datagpt-data-exploration-guide.md) — View analytics domain data coverage and structured exploration
- [Handling Feedback](datagpt-feedback-loop-guide.md) — Collect user feedback and improve
- [Analytics Domain Planning Guide](datagpt-domain-planning-guide.md) — Enterprise-level analytics domain planning methodology
