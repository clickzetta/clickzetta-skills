# Analyst Guide

Choose your path by role to quickly find the documentation you need.

***



## Business Users

**Goal: Ask questions in natural language, understand answers, and submit feedback**

**Step 1 — Understand what you can ask in an analytics domain** (2 minutes)
[Using Data and Exploration](datagpt-data-exploration-guide.md) — See what tables and fields are available in the current domain

**Step 2 — Learn how to ask questions**

[Question Asking Guide](datagpt-question-asking-guide.md) — Structure of good questions and how to ask more precisely
[Analysis Patterns Guide](datagpt-analysis-patterns-guide.md) — Lookups, comparisons, trends, rankings, proportions

**Step 3 — Understand your answers**

[Reading Analysis Results](datagpt-answer-reading-guide.md) — How to interpret values, tables, and charts

**Step 4 — Dashboards, feedback, and personalization**

[DataGPT Dashboard User Guide](datagpt-dashboard-guide.md) — View shared dashboards and ask follow-up questions around them
[Handling Feedback](datagpt-feedback-loop-guide.md) — Submit calibration feedback when answers are inaccurate or charts are wrong
[User Settings](datagpt-user-settings-guide.md) — Change logo, theme, and chart color scheme



## BI Analysts / Business Analysts

**Goal: Explore data, validate results, build dashboards, and consolidate analysis assets**

**Step 1 — Explore and validate**

[Using Data and Exploration](datagpt-data-exploration-guide.md) — Do baseline/comparison time analysis and drill-down based on configured metrics
[Reading Analysis Results](datagpt-answer-reading-guide.md) — View SQL statements and logs to determine whether answers are trustworthy

**Step 2 — Build dashboards**

[DataGPT Dashboard User Guide](datagpt-dashboard-guide.md) — Save charts/tables to dashboards, manage layout and sharing
[Table Rendering](table_rendering.md) — Adjust table styles and layout
[Dashboard Version Management](dashboard-version-management-guide.md) — Manage multiple versions and change history

**Step 3 — Continuous monitoring and operations**

[Chart Auto-Refresh Configuration](chart-auto-refresh-guide.md) — Set up scheduled data updates for dashboards
[Scheduled Tasks](scheduled_task.md) — Configure scheduled analysis and report delivery
[Message Notifications](datagpt-notification-guide.md) — View status of background tasks such as imports and parsing

**Step 4 — Feedback**
[Handling Feedback](datagpt-feedback-loop-guide.md) — Improve questions and dashboard design based on feedback



***

## If Answers Are Inaccurate

Handle in the following order:

1. Check whether the correct analytics domain is selected
2. Confirm that the business objects, scope, and time range in the question are clearly stated
3. Open the "Data" tab to confirm whether the current domain covers the relevant business data
4. Submit calibration feedback explaining where the answer does not match business expectations
5. BI analysts or maintainers review SQL statements and logs to determine whether the wrong fields were used or the configuration is incomplete

See [Troubleshooting Q\&A Accuracy Issues](datagpt-qa-accuracy-troubleshooting-guide.md) for details.
