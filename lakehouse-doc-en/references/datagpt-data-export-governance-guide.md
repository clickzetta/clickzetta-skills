# Bulk Download and Data Export Governance

Bulk download is used to export complete data from Q&A results, tables, or chart-related data. It has significant value for business analysis, but can also lead to sensitive data leakage, permission bypass, and audit tracking pressure. Therefore, it should be managed as a governance capability rather than treated as just a front-end download button.

## Why Governance Is Needed

The Analytics Agent supports generating tables and charts from natural language, and users may see a "download full data" option in the results. For ordinary analysis, downloading allows users to further process data; for sensitive analytics domains, downloading also means users may take detailed data out of the system.

Therefore, bulk download involves at least three types of controls:

| Control | Role |
| --- | --- |
| Feature permission | Controls whether users have the bulk download capability. |
| Data permission | Controls what resource scope users can download data from. |
| Audit log | Tracks whether any export-type operations have occurred. |

## Permission Entry Point

In practice, "bulk download" is a feature permission point in role authorization.

Entry path:

```text
Management > User Management > Authorization Management
```

After selecting a role, the "bulk download" permission point can be found under "Feature & Operation Permissions". This permission point is visible in administrator roles.

This shows that bulk download is not purely determined by a button on the results page — it should be uniformly controlled by role permissions.

## Recommended Authorization Principles

### Not Recommended to Grant to Everyone by Default

Business users can view answers, charts, and tables, but do not necessarily all need to download full data.

Not recommended to grant by default to:

- Temporary access users.
- Users who only need to view dashboards.
- Business staff who only need aggregated results.
- Regular users accessing sensitive analytics domains.

### Who It Is Appropriate to Grant

Consider granting to:

- BI analysts.
- Data analysts.
- Data operations staff.
- Department data managers who have gone through an approval process.
- Users who need to do offline verification or secondary processing.

Before granting, confirm the user also meets:

- Has been added to the relevant analytics domain.
- Role data permission scope is correct.
- Row-level permissions are in effect.
- Sensitive fields are hidden or masked.

## Relationship with Analytics Domain Permissions

Bulk download permission should not replace analytics domain permissions.

Even if a user has the bulk download feature, they can only download data within their accessible data scope. The downloadable scope should still be jointly constrained by:

- Analytics domain membership permissions.
- Role data permissions.
- Row-level permissions.
- Field hiding.
- The data scope of the current Q&A result or chart.

If users should not see certain detailed data, restrictions should first be applied at the analytics domain, role, row-level permission, and field hiding levels — not relying solely on an operational constraint of "don't download".

## Relationship with Column Hiding and Row-Level Permissions

### Column Hiding

Column hiding can reduce the exposure of sensitive fields in Analytics Agent Q&A and results. For fields such as ID numbers, phone numbers, emails, internal IDs, and salaries, it is recommended to first evaluate whether they need to be hidden.

Column hiding can achieve an effect similar to column-level visibility control, but it is still recommended to combine it with underlying data permissions and organizational security policies.

### Row-Level Permissions

Row-level permissions control which rows different users can see in the same table. For example, a regional manager can only see data for their own region.

If row-level permissions are correctly configured, the full data a user downloads should also only include data within their permission scope. This should be verified using test users before launch.

## Auditing and Investigation

For sensitive analytics domains, it is recommended to periodically check the audit log for export-type operations.

Entry path:

```text
Management > Audit Log > Operation Records
```

Investigation steps:

1. Select the target time range.
2. Set operation type to export-related types.
3. Review the operator, time, and operation details.
4. If anomalous exports are found, investigate in conjunction with role authorization, analytics domain permissions, row-level permissions, and field hiding.

## Pre-Launch Checklist

Before enabling bulk download, check:

- Whether it is clear which roles can use bulk download.
- Whether bulk download is avoided for ordinary dashboard viewers.
- Whether sensitive fields are hidden or masked.
- Whether row-level permissions have been verified with test users.
- Whether the analytics domain only includes data needed for the current business scenario.
- Whether the audit log can track export-type operations.
- Whether there is an internal process specifying when users may export data.

## Common Questions

### With Bulk Download Permission, Can All Data Be Downloaded?

This should not be the understanding. Bulk download permission only allows users to use the download feature. The actual data that can be downloaded should still be jointly constrained by analytics domain permissions, role data permissions, row-level permissions, and field hiding.

### Do Users Who Only View Aggregated Charts Need Bulk Download?

Generally no. Users who only view dashboards or aggregated charts can be granted access without bulk download permission.

### What Is the Relationship Between Download Governance and Data Privacy?

Data privacy focuses on whether sensitive data should be accessed, displayed, or exported; download governance focuses on whether users can bulk export data they can already see. Both should be designed together.

## Related Documentation

- [Configuring Role Authorization](datagpt-role-authorization-guide.md)
- [Managing Permissions](datagpt-permission-management-guide.md)
- [Configuring Row-Level Permissions](datagpt-row-level-permission-guide.md)
- [Configuring Field Semantics](datagpt-field-semantic-config-guide.md)
- [Viewing Audit Logs](datagpt-audit-log-guide.md)
- [Data Privacy](data_privacy.md)
