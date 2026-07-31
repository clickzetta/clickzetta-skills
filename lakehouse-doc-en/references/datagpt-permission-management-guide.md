# Permission Management

Permission management controls which pages, analytics domains, and data resources users can access in Analytics Agent, as well as what data scope they can see during Q&A.

This document explains the boundaries between "Account Management", "Authorization Management", "Row-level Permissions", and "Analytics Domain Permissions" from a practical operations perspective, to avoid mixing different permission layers in configuration.

## Permission Entry Overview

| Entry | Location | Management Object | Typical Operations |
| --- | --- | --- | --- |
| Account Management | Administration > User Management > Account Management | User accounts | View users, edit users, configure row-level permissions for users. |
| Authorization Management | Administration > User Management > Authorization Management | Roles | Create roles, configure feature permissions and resource data permissions. |
| Row-level Permissions | Administration > User Management > Row-level Permissions | Row-level permission points | Define permission points and table field mappings. |
| Analytics Domain Permissions | Analytics domain configuration > Permissions | Analytics domain members | Add users to an analytics domain. |

These entries each address different problems. Do not confuse "adding a user to an analytics domain" with "assigning a role to a user", and do not confuse "role data permissions" with "row-level permissions".

## Account Management

Account Management is used to manage system users.

In practice, the More menu in a user row includes:

- Edit
- Row-level Permissions

The "Row-level Permissions" entry is used to bind predefined row-level permission rules to specific users. This is not where permission points are created — permission points must first be defined on the "Row-level Permissions" page.

## Authorization Management

Authorization Management is used to manage role permissions.

In practice, the Authorization Management page displays a role list on the left, including:

- Administrator
- Data Analyst
- Custom roles, such as "Finance Staff"

Built-in roles may not be editable; custom roles can be edited. After selecting the user-created "Finance Staff" role, the "Edit" button on the page becomes available.

Role editing contains two tabs:

| Tab | Role |
| --- | --- |
| Feature & Operation Permissions | Controls which feature modules the role can view and operate. |
| Data Permissions | Controls which resource types the role can access, and whether access is "can view" or "can edit". |

In practice, a "Full Download" permission point is visible in feature permissions. This permission point controls whether users have the capability to download full data. For sensitive analytics domains, it is not recommended to grant this to all roles by default — it should be governed together with data privacy, row-level permissions, field hiding, and audit logs.

## Row-level Permissions

Row-level permissions control which data rows different users can see in the same table.

Configuration involves two layers:

1. Define permission points in "Administration > User Management > Row-level Permissions".
2. Configure permission point rule values for specific users in "Account Management".

In practice, defining a permission point requires configuring:

- Permission point name.
- Permission application mapping.
- Target data table.
- Target column.
- Description.

When authorizing a user, you need to select:

- Row-level permission point.
- Rule type: enumeration value or expression.
- Rule value.

## Analytics Domain Permissions

Analytics domain permissions control which users can access the current analytics domain.

When adding users in "Analytics domain configuration > Permissions", in practice the dialog only selects "Users", not roles. After adding, the list displays users and their existing roles.

For example, after adding `tester` to an analytics domain, the list shows the user's role as "Administrator, Data Analyst". This confirms that analytics domain permissions add users to the domain, while roles come from the user's own global authorization.

## Permission Configuration Order

The recommended configuration order is:

1. Create or confirm user accounts.
2. Configure roles in Authorization Management.
3. Confirm users have appropriate roles.
4. Add users to the analytics domains they need to access.
5. Configure domain resources: tables, files, knowledge, metrics, answer builders, etc.
6. Configure field hiding or adjust field semantics for sensitive fields.
7. If data row isolation is needed, define row-level permission points and bind them to users.
8. Use a test user to validate Q&A results and page access scope.
9. Use audit logs to check key configuration change records.

## Common Misconceptions

| Misconception | Correct Understanding |
| --- | --- |
| Roles can be selected when adding users in analytics domain permissions | In practice, only users can be selected; roles come from the user's existing global roles. |
| Authorization Management is for directly authorizing individual users | Authorization Management manages role permissions, not individual user permissions. |
| Row-level permissions are configured in the analytics domain | Permission points are defined on the Row-level Permissions page in User Management, then bound to users in Account Management. |
| Field hiding equals bottom-level database permissions | Field hiding affects Analytics Agent Q&A visibility, achieving column-level governance, but is not equivalent to bottom-level database authorization. |
| Joining a domain means access to all resources | You also need to check role data permissions, whether domain resources have been added, whether fields are hidden, and whether row-level permissions impose restrictions. |

## Validation Methods

After completing permission configuration, it is recommended to use a test user to verify:

- Whether the user can log in.
- Whether the user can see the target analytics domain.
- Whether the user can enter "Start Analysis".
- Whether the user can use target tables, files, knowledge, metrics, and answer builders.
- Whether the user cannot access administration entries they should not access.
- Whether the user can only see data within the row-level permission scope.
- Whether only authorized roles can use the full download capability.
- Whether login, modification, and export operations are recorded in the audit log.

## Related Documentation

- [Analytics Agent Governance Overview](datagpt-governance-overview.md)
- [Role Authorization Guide](datagpt-role-authorization-guide.md)
- [Row-Level Permission Configuration Guide](datagpt-row-level-permission-guide.md)
- [Audit Log Guide](datagpt-audit-log-guide.md)
- [Full Download and Data Export Governance](datagpt-data-export-governance-guide.md)
