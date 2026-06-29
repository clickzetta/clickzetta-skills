# Configure Row-Level Permissions

Row-level permissions control which data rows different users can see in the same table. They are suitable for scenarios where multiple departments share the same analytics domain, but each department can only see data within its own scope.

For example:

- North China sales can only view North China regional orders.
- Store managers can only view their own store data.
- Finance staff can only view data within their authorized entity or organizational scope.

## Purpose of Row-Level Permissions

Row-level permissions constrain the data scope when users initiate natural language Q&A in Analytics Agent. After configuration, use restricted users to validate Q&A results and the generated SQL to confirm the rules are working as expected.

For example, when both users ask "what is this year's order amount?", they may see different results:

| User | Row-level Permission | Q&A Result Scope |
| --- | --- | --- |
| Headquarters administrator | Unrestricted or full access | All orders. |
| North China sales | Region = North China | North China orders. |
| South China sales | Region = South China | South China orders. |

## Configuration Entry Points

Row-level permissions involve two entry points:

| Entry Point | Location | Purpose |
| --- | --- | --- |
| Define permission points | Administration > User Management > Row-level Permissions | Define which table and field a permission point maps to. |
| Authorize users | Administration > User Management > Account Management > More menu in user row > Row-level Permissions | Configure permission point rule values for specific users. |

Note: Permission point definition and user authorization are done on different pages.

## Step 1: Define Row-Level Permission Points

Go to "Administration > User Management > Row-level Permissions" to create or edit permission points.

In practice, the page contains the following configurations:

| Configuration Item | Description |
| --- | --- |
| Permission Point Name | The name of the permission point used when authorizing users. |
| Permission Application Mapping | Indicates which data mappings this permission point applies to. |
| Target Data Table | The data table that needs row-level control. |
| Target Column | The field used to filter the data scope. |
| Add Mapping | A permission point can be configured with mapping relationships. |
| Description | Explains the purpose and applicable scope of the permission point. |

In practice, a sample permission point `test` maps to:

```text
quick_start.gaming_profiles_steam.players.playerid
```

This means the permission point will apply to the `playerid` field in the `players` table.

## Step 2: Configure Row-Level Permissions for a User

Go to "Administration > User Management > Account Management" and find the target user.

1. Click the More menu on the right of the user row.
2. Select "Row-level Permissions".
3. On the "Edit Row-level Permissions" page, click "Add Row-level Permission".
4. Select the predefined row-level permission point.
5. Select the rule type.
6. Enter the rule value and press Enter to confirm.
7. Save.

In practice, the Add Row-level Permission form contains:

| Configuration Item | Description |
| --- | --- |
| Row-level Permission | Select a predefined permission point, e.g., `test`. |
| Type | Supports "Enumeration Value" or "Expression". |
| Rule Value | Enter the data scope this user can access. The page prompts to press Enter to confirm. |

## Enumeration Values vs. Expressions

| Type | Applicable Scenario | Example |
| --- | --- | --- |
| Enumeration Value | The user's accessible data scope is a clear list of values. | Region is "North China" or "East China"; store is 1001 or 1002. |
| Expression | The data scope needs to be described by a conditional expression. | Organizational hierarchy, dynamic ranges, complex conditions. |

If the business rule is simple, prefer enumeration values for clarity and ease of maintenance. If the rule involves organizational hierarchy or dynamic mapping, consider expressions.

## Difference from Column Hiding

Row-level permissions control "which rows are visible"; column hiding controls "which fields are not exposed to Q&A".

| Capability | Control Target | Example |
| --- | --- | --- |
| Row-level permissions | Data rows | Can only see North China regional orders. |
| Column hiding | Field columns | Don't expose ID numbers, phone numbers, or internal notes to users. |

Both can be used together. For example, finance staff can only see data rows in their own organization, while sensitive fields that should not be exposed are hidden.

## Difference from Role Data Permissions

Role data permissions control resource access scope; row-level permissions control data range within a table.

| Configuration | Problem It Solves |
| --- | --- |
| Role data permissions | Whether this role can view or edit resources such as tables, files, knowledge, metrics, and answer builders. |
| Row-level permissions | When this user queries a specific table, which rows can they see. |

For example, a user may have view permission for a table, but row-level permissions still restrict them to seeing only a subset of the data.

## Validation Methods

After configuration, it is recommended to validate with a restricted user:

1. Enter the target analytics domain.
2. Ask a question without filter conditions, e.g., "What is the total order count?".
3. Check if the result includes only data within the authorized scope.
4. Ask a question that attempts to access data beyond the scope, e.g., "View all regional orders".
5. Check whether the result is still restricted by row-level permissions.
6. If necessary, view the generated SQL or Q&A logs to confirm the system automatically appended permission conditions.

## Maintenance Recommendations

- Permission point names should use business-meaningful names, e.g., "Sales Region Permission", "Store Data Permission".
- Target columns should be stable, low-ambiguity permission fields.
- Do not use frequently changing, ambiguous, or null-heavy fields as permission columns.
- When a user's role changes, promptly update their row-level permission rules.
- After important permission changes, check operation records in audit logs.

## Related Documentation

- [Analytics Agent Governance Overview](datagpt-governance-overview.md)
- [Permission Management Guide](datagpt-permission-management-guide.md)
- [Field Semantic Configuration Guide](datagpt-field-semantic-config-guide.md)
- [Audit Log Guide](datagpt-audit-log-guide.md)
