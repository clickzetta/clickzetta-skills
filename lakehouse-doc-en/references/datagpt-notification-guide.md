# Notifications

Notifications provide a centralized view of the execution status of asynchronous tasks in Analytics Agent, such as file imports, table imports, and file Q&A parsing. They help users determine whether background tasks have succeeded, are still running, or have failed and why.

## Entry Point

Click the following in the top or left main navigation:

```text
Notifications
```

In practice, clicking "Notifications" does not navigate to a new standalone page — it opens the notification list as an overlay on the current page. The notification list can be opened from any page, such as Analytics, Data, Dashboard, Scheduled Tasks, or Administration.

## Page Content

The notification panel contains status statistics and a notification list.

Statuses include:

| Status | Description |
| --- | --- |
| All | Shows all notifications. |
| Succeeded | Background task completed. |
| Running | Background task is still executing. |
| Failed | Background task failed; review the reason. |
| Pending | Task submitted but not yet started. |

The notification list shows:

- Task object name, e.g., file name or table file name.
- Task type, e.g., file import, table import.
- Execution time.
- Created by.
- Failure reason, e.g., field mismatch.

## Common Notification Types

### File Import

File import notifications track the processing status of uploaded files.

Key things to check:

- Whether the file was imported successfully.
- Whether file parsing failed.
- Whether the file can continue to be used for document Q&A or knowledge configuration.

### Table Import

Table import notifications track the process of converting CSV, Excel, or compressed archive files into tables.

Key things to check:

- Whether the table was imported successfully.
- Whether there are field mismatches.
- Whether you need to re-upload or adjust the file structure after a failed import.

## Handling Failed Notifications

If a notification shows a failed status, handle it in the following order:

1. Check the failed object name to identify which file or table failed.
2. Check the task type to determine whether it was a file import or table import.
3. Review the failure reason, e.g., field mismatch.
4. Return to the data import or file upload entry point and check the source file structure, field names, format, and encoding.
5. If the failure occurs before the analytics domain goes live, fix the issue and re-import. Do not ignore failed notifications and open the domain to business users as-is.

## Relationship with Other Features

| Related Feature | Relationship |
| --- | --- |
| Data Import | Successful or failed table imports appear in notifications. |
| File & Document Q&A | File import and parsing status affects availability of document Q&A. |
| Data Source Management | Import failures may relate to data sources, table structures, or field types. |
| Audit Log | Audit logs track user actions; notifications track task execution results. The two can be used together to troubleshoot issues. |

## Usage Recommendations

- After uploading files or importing tables, check notifications first to confirm the task has completed.
- If a file or table does not appear in the data list, check notifications for any failure records.
- Administrators or maintainers should regularly monitor failed notifications to avoid incomplete data preparation work in the analytics domain.
- Before opening an analytics domain to business users, confirm that core table, file, and knowledge-related import tasks have not failed.

## Related Documentation

- [Data Source Management](datagpt_data_source.md)
- [File & Document Q&A](datagpt-file-knowledge-qa-guide.md)
- [Configure Analytics Domain](datagpt-domain-management-guide.md)
- [View Audit Logs](datagpt-audit-log-guide.md)
