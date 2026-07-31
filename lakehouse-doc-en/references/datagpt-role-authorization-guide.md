# Configure Role Authorization

Role authorization controls what features a group of users can use and what resources they can view or edit. It is suitable for configuring different permissions for different groups, such as finance staff, operations, sales, and data administrators.

## Accessing Authorization Management

1. Click "Administration" in the left navigation.
2. Go to "User Management".
3. Open "Authorization Management".
4. Select the target role from the role list on the left.

The left side of the page displays all roles. In practice, you can see built-in roles "Administrator" and "Data Analyst", as well as user-created custom roles, such as "Finance Staff".

## Creating a New Role

Click the small circle plus icon to the right of "All Roles" to open the "Create Role" drawer.

The drawer contains the following fields:

| Field | Required | Description |
| --- | --- | --- |
| Role Name | Required | Recommended to use business group names, e.g., "Finance Staff", "Operations Analyst". |
| Description | Optional | Explain the target audience, permission scope, and notes for this role. |

Bottom action buttons include:

- Cancel
- Save and Create Next
- Save

After saving, the role appears in the role list on the left.

## Editing a Role

After selecting a custom role, click "Edit" to enter edit mode.

In practice, the custom role "Finance Staff" can be edited. Built-in roles may be restricted by the system and the edit button may be unavailable or limited.

Edit mode contains:

- Cancel
- Save
- Feature & Operation Permissions
- Data Permissions

If you try to leave the page after making changes, the system will prompt "Changes not saved". Confirm before saving to avoid accidentally modifying role permissions.

## Feature & Operation Permissions

"Feature & Operation Permissions" displays module permissions in a permission tree.

In practice, visible permission nodes include:

- Answer Builder
- Data Source
- Audit Log
- Settings
- Account Management
- Authorization Management
- Knowledge
- Tables
- Analytics Domain Management
- Index Management
- Metrics
- Full Download
- Feedback
- Model Configuration

Feature permissions primarily determine whether users can see or operate on a module. For example, if you don't want business analysis users to modify model configuration or manage accounts, avoid granting the relevant feature permissions.

"Full Download" needs separate evaluation. It controls whether users can use the full data download capability, involving data export and privacy governance. For users who only view dashboards or use aggregate results, full download is generally not needed.

## Data Permissions

"Data Permissions" configures access scope by resource type.

In practice, configurable resource types include:

| Resource Type | Description |
| --- | --- |
| Answer Builder | Controls the visible and editable scope of answer builder resources. |
| Data Source | Controls the visible and editable scope of data source resources. |
| Knowledge | Controls the visible and editable scope of knowledge resources. |
| Tables | Controls the visible and editable scope of table resources. |
| Files | Controls the visible and editable scope of file resources. |
| Metrics | Controls the visible and editable scope of metric resources. |

Each resource type has an "All Data" option. When checked, it configures that resource type to cover all data scope. Actual availability also needs to be verified together with the user's role, analytics domain membership, and whether resources have been added to the domain.

After checking "All Data", an action dropdown appears. In practice, confirmed action options include:

- Can View
- Can Edit

Meanings:

| Action | Applicable Scenario |
| --- | --- |
| Can View | User can use or view resources but should not modify resource configuration. |
| Can Edit | User can modify resource configuration; suitable for administrators or domain maintainers. |

## Recommended Role Design

### Administrator

Administrators are suitable for personnel responsible for system configuration, model configuration, user and permission management.

Recommended to have:

- Account Management.
- Authorization Management.
- Audit Log viewing.
- Analytics Domain Management.
- Edit permissions for tables, knowledge, metrics, and answer builders.

### Domain Maintainer

Domain maintainers are responsible for maintaining data and Q&A quality for a specific business domain.

Recommended to have:

- Analytics Domain Management.
- Edit permissions for tables, knowledge, metrics, and answer builders.
- Audit Log viewing permission, depending on organizational requirements.

Not recommended to grant by default:

- Account Management.
- Authorization Management.
- Model Configuration.

### Business Analysis User

Business analysis users primarily use Q&A and view results.

Recommended to have:

- Target analytics domain access permission.
- View permissions for tables, files, knowledge, metrics, and answer builders.

Not recommended to grant:

- Edit metrics.
- Edit answer builders.
- Analytics Domain Management.
- Authorization Management.
- Model Configuration.

## Difference from Analytics Domain Permissions

Role authorization and analytics domain permissions are not the same thing.

| Configuration | Problem It Solves |
| --- | --- |
| Role authorization | What system features and resource access levels the user has. |
| Analytics domain permissions | Whether the user can enter a specific analytics domain. |

Having a role does not necessarily mean the user can enter a specific analytics domain; being added to an analytics domain does not mean the user can edit all resources within the domain. Both must be checked before launch.

## Validation Recommendations

After configuring roles, it is recommended to validate with a test account:

- Whether the expected menus are visible.
- Whether administration entries that should not be accessible are not visible.
- Whether the target analytics domain can be entered.
- Whether target resources can be used to answer questions.
- Whether view-only resources cannot be edited.
- Whether unauthorized full download capability cannot be used.
- Whether key operation records are visible in the audit log.

## Related Documentation

- [Analytics Agent Governance Overview](datagpt-governance-overview.md)
- [Permission Management Guide](datagpt-permission-management-guide.md)
- [Analytics Domain Resource Permission Guide](datagpt-domain-resource-permission-guide.md)
- [Audit Log Guide](datagpt-audit-log-guide.md)
- [Full Download and Data Export Governance](datagpt-data-export-governance-guide.md)
