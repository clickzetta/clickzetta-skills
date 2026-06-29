# Scheduled Tasks

Scheduled Tasks allow you to turn a one-time natural language analysis into a periodically executed analysis task. The system automatically runs the task at the configured time, retaining execution records and analysis results upon completion. This is suitable for daily anomaly detection, business monitoring, trend reviews, and periodic reports.

Scheduled Tasks are not simple reminders. They invoke the Analytics Agent to complete an analysis according to the task description. The clarity of the task description, the quality of the analysis domain configuration, the data update frequency, and the notification address all affect the final outcome.

## Use Cases

Appropriate uses for Scheduled Tasks:

- Checking the same set of business metrics every day or week.
- Automatically detecting anomalies and providing analytical explanations.
- Sending analysis results to a fixed set of recipients.
- Retaining historical execution records so you can review results from a specific day.

Not appropriate for Scheduled Tasks:

- One-off ad-hoc questions.
- Monthly or quarterly analyses where data is updated infrequently.
- Questions where the metric definition has not yet been confirmed.
- Questions where the scope of analysis must be determined by human judgment first.

## How to Create

### Method 1: Automatic suggestion from a Q&A session

When a Q&A session has ongoing monitoring value, the Analytics Agent may suggest automatic monitoring after providing an answer.

For example, when a user asks about account health, business anomalies, score declines, or rising cancellation rates, the system may suggest setting up daily automatic detection. The user can then confirm the execution time, notification email, monitoring scope, and anomaly conditions.

This method is suitable for business users naturally extending a single analysis into periodic monitoring.

### Method 2: Managing tasks via the Scheduled Tasks page

Entry point:

```text
Scheduled Tasks
```

In practice, the Scheduled Tasks list shows existing tasks. In the current validation environment, a prominent "New" button may not be visible, but existing tasks can be opened to view details, execution records, and edit the task. Whether a "New" entry is shown depends on the version or permissions — refer to the actual page.

Therefore, if a user does not see a standalone "New" entry, they can start from a Q&A session with ongoing monitoring value and let the system suggest scheduled monitoring based on the answer. Administrators or maintainers primarily use the Scheduled Tasks page to manage existing tasks, view execution records, and handle failed tasks.

## Task List

In practice, the Scheduled Tasks list contains:

| Field | Description |
| --- | --- |
| Task Name | The name of the scheduled task. |
| Analysis Domain | The analysis domain associated with the task. |
| Notification Address | The address to which analysis results are sent. |
| Created By | The user who created the task. |
| Latest Execution Time | The time the most recent execution completed. |
| Next Run Time | The next planned run time. |
| Updated At | The most recent time the task configuration was updated. |
| Status | The current task status, e.g., Disabled. |

Example task seen in practice:

```text
Daily Business Anomaly Detection
Analysis Domain: gaming_profiles_steam
Notification Address: qiliang@clickzetta.com
Status: Disabled
```

## Filtering Tasks

Click "Filter" to filter tasks by the following criteria:

| Filter | Description |
| --- | --- |
| Task Name | Search by task name. |
| Status | Filter by task status. |
| Analysis Domain | Filter by associated analysis domain. |
| Created At | Filter by task creation time range. |

The filter panel includes "Reset" and "Confirm" buttons.

## Task Detail Page

Click a task name to enter the detail page.

The detail page contains two tabs:

- Basic Information
- Execution Records

### Basic Information

Basic information displays:

| Field | Description |
| --- | --- |
| Task Name | The current task name. |
| Status | Whether the task is currently enabled or disabled. |
| Latest Execution Time | The most recent execution end time. |
| Next Run Time | The next planned execution time. |
| Updated At | The most recent time the task configuration was updated. |
| Created At | The task creation time. |
| Notification Address | The address to receive results. |
| Task Analysis | The natural language analysis task description executed periodically. |

In practice, the "Daily Business Anomaly Detection" task analysis content is very detailed, including review anomaly detection, player activity anomaly detection, new player growth anomaly detection, anomaly determination criteria, output requirements, and visualization requirements.

This shows that the quality of a Scheduled Task depends heavily on the task analysis description. The more specific the description, the more consistently the system can execute it.

## Editing a Task

Clicking "Edit" on the detail page opens an edit task dialog.

In practice, the edit dialog contains:

| Field | Description |
| --- | --- |
| Task Name | The name displayed in the list and detail page. |
| Notification Address | The address to which analysis results are sent. |
| Description | A brief explanation of the task's purpose. |
| Detailed Task Analysis Content | The specific analysis requirements to be completed on each scheduled execution. |

Bottom actions include:

- Cancel
- Confirm

When editing a task, avoid writing only "check for anomalies daily". Instead, specify:

- Which business objects to check.
- Which metrics to calculate.
- What the anomaly thresholds are.
- Whether year-over-year, month-over-month, or comparison to historical averages is needed.
- How to output results when there are no anomalies.
- Whether charts or detail tables are required.

## Execution Records

The "Execution Records" tab shows the historical run history.

In practice, the execution records table contains:

| Field | Description |
| --- | --- |
| Execution Time | The start and end time of this task run. |
| Execution Status | SUCCEED or failed. |
| Notification Address | The address to which this execution's results were sent. |
| View Details | Opens the complete analysis result for this execution. |

Execution records help determine:

- Whether the task ran as scheduled.
- Which dates had failed executions.
- Which execution results were sent to the notification address.
- What the anomaly analysis result was for a specific day.

## Execution Details

Clicking "View Details" in the execution records opens the execution detail page.

In practice, the execution detail page shows a complete analysis result, for example:

- Review anomaly detection results.
- Player activity anomaly detection results.
- New player growth anomaly detection results.
- Data limitation notes.
- Overall assessment.

The page also provides a "Continue Analysis" button. Users can continue asking follow-up questions or conduct deeper analysis based on a scheduled task result.

This means a scheduled task execution result is not a static log — it is a result asset that can continue into the Analytics Agent analysis chain.

## Result Notifications

Scheduled Tasks can be configured with a notification address. After task execution completes, the system sends the analysis results to the specified address. The execution record also shows the notification address used for that execution.

If the notification address is empty or shows `-`, it indicates that execution may not have sent results to the address, or the address was not recorded. Investigate by reviewing the task configuration and execution status.

## Relationship with Message Notifications

Message Notifications are used to view the overall status of background tasks, such as file imports and table imports. Scheduled Tasks have their own task list and execution records.

The difference between the two:

| Feature | Primary Purpose |
| --- | --- |
| Message Notifications | View whether background async tasks succeeded, failed, or are running. |
| Scheduled Tasks | Manage periodic analysis tasks and view each analysis result. |

If the data ingestion that a Scheduled Task depends on fails, first investigate the data preparation issue in Message Notifications.

## Relationship with Q&A Accuracy

Each Scheduled Task execution invokes the Analytics Agent for analysis. To ensure task stability, you must first ensure:

- The analysis domain boundaries are clear.
- Relevant tables, metrics, knowledge, and answer builders are configured.
- The metric definitions referenced in the task description have been confirmed.
- Data updates daily as expected.
- Similar analyses have been validated via typical questions and return correct answers.

If a task frequently fails or produces unstable conclusions, do not only adjust the execution time or notification address. Return to the analysis domain configuration, field semantics, metrics, knowledge, and answer builders to investigate.

## Pre-Launch Checklist

Before creating or enabling a Scheduled Task, it is recommended to check:

- Whether the task name clearly conveys the business purpose.
- Whether the notification address is correct.
- Whether the task description clearly specifies the business objects, metrics, scope, anomaly criteria, and output requirements.
- Whether the associated analysis domain is correct.
- Whether the analysis domain data updates at the task's frequency.
- Whether similar questions have been validated in the analysis page.
- Whether there is a recipient responsible for reviewing and handling anomaly results.
- Whether audit logs and message notifications should be used to investigate failures.

## Related Documentation

- [Message Notifications](datagpt-notification-guide.md)
- [Reading Analysis Results](datagpt-answer-reading-guide.md)
- [Using Dashboards](datagpt-dashboard-bi-analyst-guide.md)
- [Chart Auto-Refresh Configuration](chart-auto-refresh-guide.md)
- [Validating Q&A Quality](datagpt-domain-qa-validation-guide.md)
- [Troubleshooting Q&A Accuracy Issues](datagpt-qa-accuracy-troubleshooting-guide.md)
