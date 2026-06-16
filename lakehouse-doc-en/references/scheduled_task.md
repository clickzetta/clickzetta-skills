# Scheduled Tasks

## Feature Overview

The Scheduled Tasks feature allows users to create periodic data analysis tasks using natural language. The system will automatically execute analysis and push results at the scheduled time. It can be used for daily anomaly detection, business data monitoring, trend insights, and other scenarios, helping users automatically discover abnormal changes in data and receive analysis recommendations.

## Creating a Scheduled Task

**Method 1: ASK AI Conversational Creation**

| Step                                              | Demo                                                | Content                                                                                                                                                                                                                                                                                                                                                                                                              |
| ------------------------------------------------- | --------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. User asks a question                           | ![](/.topwrite/assets/image_1780906950414.png =200) | "Help me analyze whether yesterday's business data has any anomalies?"                                                                                                                                                                                                                                                                                                                                               |
| 2. Auto-monitoring suggestion                     | ![](/.topwrite/assets/image_1780907011715.png =261) | The system recognizes the user's anomaly monitoring intent and proactively recommends at the end of the analysis result, e.g.: "If such anomalies can be detected earlier, it can help the operations team intervene faster. I can help you set up daily automatic detection. Once a store rating falls below 3.0 or negative reviews exceed 20, I will notify you immediately and automatically analyze the cause." |
| 3. User confirms intent                           | ![](/.topwrite/assets/image_1780906845499.png =126) | Reply "OK, set it up for me"                                                                                                                                                                                                                                                                                                                                                                                         |
| 4. Recommend monitoring metrics and configuration | ![](/.topwrite/assets/image_1780906880578.png =255) | Based on the metrics and data distribution the user cares about, suggestions are provided: monitoring metrics (rating, negative review count, order volume, revenue), thresholds, execution frequency (daily at 09:00), push strategy (only push on anomalies), and the user is asked to confirm execution time, notification email, and monitoring metric scope                                                     |
| 5. User confirms configuration                    | ![](/.topwrite/assets/image_1780906924308.png =176) | Confirm or adjust monitoring metrics, execution time, notification email, etc.                                                                                                                                                                                                                                                                                                                                       |

**Method 2: Manual Creation**

1\. Go to the "Scheduled Tasks" page

2\. Click the "+ Scheduled Task" button in the upper right corner

3\. Describe the task requirements through conversation; you can specify the email address directly

## Result Notification

### Email Push

* Enter the recipient email address in the task configuration
* After the task execution is complete, the system will automatically send the analysis results to the specified email address

### Manual Viewing

* Go to the "Scheduled Tasks" page to view the task list
* Click on a specific task to view historical execution records and analysis results
  ![](/.topwrite/assets/image_1780907163189.png =557)

## Task Details Page

* The task details page displays basic information and execution records:
  ![](/.topwrite/assets/image_1780907206681.png =730)

## Notes

1\. Scheduled tasks are suitable for scenarios with high data update frequency (real-time or T+1); scenarios with slower data updates (e.g., monthly reports) are not recommended at this time

2\. Ensure the email address entered is correct; otherwise, you will not receive push results

3\. Task execution results are automatically generated by the Agent; it is recommended to manually verify key conclusions

4\. You can enable or disable tasks in the task list at any time

## Related Documentation

* [Chart Auto-Refresh Settings](chart-auto-refresh-guide.md) — Automatically update dashboard chart data without manual triggers
* [Answer Accuracy Improvement](answer-accuracy-improve.md) — Improve the accuracy of scheduled task analysis results
* [Conversational Data Analytics (Analytics Agent)](datagpt_introduction.md) — Return to feature overview

^
