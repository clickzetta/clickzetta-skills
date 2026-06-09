# Chart Auto-Refresh Settings

## Feature Overview

Charts in dashboards support setting an auto-refresh interval. The system will automatically update chart data at the set time interval, ensuring the dashboard always displays the latest information without requiring manual refresh by users.

## Applicable Scenarios

* Business daily report dashboards: Set to refresh every 24 hours, automatically updating yesterday's data each day

* Real-time monitoring dashboards: Set a shorter refresh interval to reflect business changes promptly

* Weekly/monthly report dashboards: Set a longer refresh interval to reduce unnecessary query overhead

## How to Use

| Step                  | Description                                                        | Screenshot                                          |
| --------------------- | ------------------------------------------------------------------ | --------------------------------------------------- |
| Select chart settings | Click "Dashboard" and select the chart you want to configure       | ![](/.topwrite/assets/image_1780901921376.png =241) |
| Set refresh interval  | Default refresh every 24 hours; adjustable based on business needs | ![](/.topwrite/assets/image_1780901941736.png =251) |

## **Notes**

1\. Auto-refresh is configured independently for each chart; different charts in the same dashboard can have different refresh intervals

2\. During refresh, the system re-executes the query corresponding to that chart to retrieve the latest data

3\. It is recommended to set refresh intervals reasonably based on data update frequency, avoiding excessively frequent refreshes that cause unnecessary resource consumption

## Related Documentation

* [Scheduled Tasks](scheduled_task.md) — Automatically execute analysis on a schedule and push results
* [Dashboard Version Management](dashboard-version-management-guide.md) — Manage multi-version history of dashboards
* [Conversational Data Analytics (Analytics Agent)](datagpt_introduction.md) — Return to feature overview

^
