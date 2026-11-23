# AI Insight

AI Insight helps users quickly understand overall dashboard performance, changes in key metrics, and what individual charts show, reducing the time spent on manual analysis and summaries. Use it to review a dashboard, analyze several charts, or explore a single chart in more depth with a preset or custom analysis approach.

> ⚠️ **Note:** Make sure the dashboard or chart is configured and displaying data correctly. AI-generated insights are for reference only; verify them against your business context.

## What can AI Insight help with?

* **Get a quick business overview**: See the overall picture in large datasets and avoid missing changes in key metrics, anomalies, or risks.
* **Understand metric changes**: When chart data fluctuates or looks unusual, use AI Insight to explore possible causes and reduce manual analysis and troubleshooting time.
* **Receive business briefs on a schedule**: Reduce manual checking and preparation by receiving regular business summaries and risk alerts.

## Before you begin

Make sure you have access to the target dashboard and its analytics domain, and that the dashboard and charts are configured and displaying data correctly. If you plan to use a custom analysis approach or business template, prepare the analysis points or confirm that a suitable template is available.

## Steps

### Step 1

Open the target dashboard, select **Edit dashboard**, then select **AI Insight** in the upper-left corner to open the insight configuration dialog.

### Step 2

Choose the insight scope in the dialog: the entire dashboard or a specific chart. To analyze an individual chart, you can also select **Add AI Insight** in the chart's upper-right corner to include it in the scope.

### Step 3

Choose a built-in template or a custom analysis approach, then generate the insight as needed.

**Optional:** Import your own report template. AI identifies the fields to populate and leaves them blank (`${undefined}`), while preserving existing content and fixed text. These placeholders are linked to dashboard data, so the insight report refreshes when the data changes.

![](.topwrite/assets/datagpt-AI-insight-template-management.png)
![](.topwrite/assets/datagpt-AI-insight-new-template.png)
![](.topwrite/assets/datagpt-AI-insight-report-skeleton.png)

### Step 4

Select the bell icon in the upper-right corner of the insight card to open **Subscription settings**. Choose the delivery frequency, time, and one or more channels. After saving, send a preview to confirm that the insight arrives through the selected channel.

> ⚠️ **Note:** Only channels enabled by your organization are available. If the channel you need is not listed, contact your administrator.

## View the results

* **Where to find insights:** Insights appear in the corresponding dashboard or chart. You can also receive them automatically through linked delivery channels, such as email or an IM group.
* **How to confirm setup:** The insight card appears on the dashboard, and the selected channel successfully receives a preview or scheduled notification.

## Frequently asked questions

### 1. How do I open AI Insight?

Open the dashboard in edit mode and select **AI Insight** in the upper-left corner. To analyze a single chart, you can also add AI Insight from the chart.

### 2. Can I analyze only some of the charts?

Yes. Choose specific charts in the insight scope, or add multiple charts to the scope.

### 3. What should I do if an insight is inaccurate?

First, confirm that the dashboard data is correct. Then adjust the analysis approach or template and generate the insight again. AI-generated insights are for reference only; verify them against your business context.

### 4. How can I receive insights on a schedule?

Select the bell icon in the upper-right corner of the insight card, then set the delivery frequency, time, and channels. You can send a preview first to test the delivery.

### 5. Why can't I see the delivery channel I need?

Available channels are controlled by your organization. If the channel you need is not listed, contact your administrator.

## Related documentation

* [DataGPT Dashboard User Guide](datagpt-dashboard-guide.md) — Learn how to create, edit, view, and refresh dashboards.
* [Analysis Patterns Guide](datagpt-analysis-patterns-guide.md) — Learn about trends, comparisons, anomalies, and attribution to help choose or write an insight template.
* [Usage Guide](datagpt-role-based-usage-guide.md) — Learn how to use dashboards and scheduled tasks to deliver analysis results periodically.
* [Managing Analytics Domain Resource Permissions](datagpt-domain-resource-permission-guide.md) — Learn about analytics domain resources and permissions, and troubleshoot access issues.
