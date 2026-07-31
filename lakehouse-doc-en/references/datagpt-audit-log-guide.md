# Viewing Audit Logs

The audit log records key operations performed by users in the system, helping administrators track logins, configuration changes, resource additions, deletions, and exports.

Once an analytics domain is live, the audit log is an essential part of the governance loop. It can help answer:

- Who modified the analytics domain configuration.
- Who created or updated an answer builder.
- Who added, deleted, or exported resources.
- Whether a certain account has logged into the system.

## Accessing the Audit Log

1. Click "Management" in the left navigation.
2. Open "Audit Log".
3. Go to "Operation Records".

Confirmed in practice, the page URL is:

```text
/dataai/settings/audit-log/operation
```

## Page Structure

The "Operation Records" page includes a filter area, a log table, and pagination.

### Filter Options

The following filters are supported on the page in practice:

| Filter | Description |
| --- | --- |
| Operator | The page shows "Select operator" — choose from the user account list. |
| Operation Type | Filter logs by operation type. |
| Time Range | Some versions or filter panels support filtering by start date and end date. |

The operator dropdown lists system user accounts. Examples seen in practice include:

- test04
- test03
- test02
- test01
- tester
- qiliang

### Operation Types

Confirmed in practice, the operation type dropdown includes:

| Operation Type | Description |
| --- | --- |
| Login | Records related to user login. |
| Create | Creating a resource or configuration. |
| Modify | Modifying an existing resource or configuration. |
| Delete | Deleting a resource or configuration. |
| Export | Used to filter export-type operation records; actual log content depends on what was generated. |

### Table Fields

The audit log table includes:

| Field | Description |
| --- | --- |
| Username | Display name of the operator. |
| User Account | Account name of the operator. |
| Time | Time when the operation occurred. |
| Operation Type | Operation category. |
| Operation Details | Details of the operation. |

## Sample Log Entries

In practice, the audit log recorded the following types of content:

| Operation Type | Sample Operation Details | Description |
| --- | --- | --- |
| Account Login | Login successful | Records account login events. |
| Domain Modification | Added domain relationship, domain: doc_ops_test_domain_20260608 | Records analytics domain relationship changes. |
| Domain Modification | Updated domain, domain: doc_ops_test_domain_20260608 | Records analytics domain configuration updates. |
| Analytics Creation | Answer builder name: test_answer_builder_account_health_overview_20260609 | Records creation of analytics-related resources. |

These records help administrators confirm whether a configuration change actually occurred and which account executed it.

## Difference Between Audit Logs and Message Notifications

Both audit logs and message notifications can help with troubleshooting, but they focus on different things.

| Feature | Focus | Example |
| --- | --- | --- |
| Audit Log | Who did what and when. | User login, modifying analytics domain, creating answer builder, exporting data. |
| Message Notification | Whether a background task succeeded, failed, or is running. | File import, table import, file parsing failure. |

Use the audit log to track "who changed a configuration"; use message notifications to confirm "whether an import task succeeded". Both can be used together when investigating a complete issue.

## Pagination

Audit logs support paginated viewing. In practice, the page displays:

- Total count, e.g., "303 records total".
- Page numbers.
- Records per page, e.g., "10 records/page".
- Jump to page.

When investigating earlier operations, combine time range filtering with pagination to locate records.

## Common Investigation Scenarios

### Investigating Who Modified an Analytics Domain

1. Open "Audit Log > Operation Records".
2. Select the target time range.
3. Set operation type to "Modify".
4. Review records in the operation details that contain the target analytics domain name.

If you know who might have made the change, also filter by operator to narrow down the results.

### Investigating Who Created an Answer Builder

1. Open "Operation Records".
2. Select a time range around the creation time.
3. Set operation type to "Create".
4. Search for the answer builder name in the operation details.

In practice, creating an answer builder produces a record similar to "Answer builder name: test_answer_builder_account_health_overview_20260609".

### Investigating Whether an Account Logged In

1. Select the target operator.
2. Set operation type to "Login".
3. Check whether a "Login successful" record exists.

This is useful when a user reports "I can't see the analytics domain" — first confirm whether the user actually logged into the system.

### Investigating Whether an Export Occurred

1. Select the target time range.
2. Set operation type to "Export".
3. Review the related operation details.

For sensitive data domains, it is recommended to periodically check export records.

If your organization has enabled the "bulk download" permission, export auditing should be incorporated into regular governance. The bulk download permission controls whether users can use the export feature; the audit log tracks whether an export actually occurred.

## Launch Governance Recommendations

- After a key analytics domain goes live, periodically check the audit log for modification, deletion, and export records.
- After adjusting roles, row-level permissions, or domain permissions, verify whether corresponding operation records exist.
- Use clear names for important resources so they can be identified in operation details.
- When troubleshooting changes in Q&A effectiveness, first check whether anyone recently modified tables, metrics, knowledge, or answer builders.
- Do not rely only on verbal confirmation of configuration changes — use the audit log as the tracking basis.

## Related Documentation

- [Analytics Agent Governance Overview](datagpt-governance-overview.md)
- [Permission Management Guide](datagpt-permission-management-guide.md)
- [Role Authorization Guide](datagpt-role-authorization-guide.md)
- [Validating Q&A Effectiveness After Domain Configuration](datagpt-domain-qa-validation-guide.md)
- [Message Notifications](datagpt-notification-guide.md)
- [Bulk Download and Data Export Governance](datagpt-data-export-governance-guide.md)
