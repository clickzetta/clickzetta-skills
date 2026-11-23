# Column-Level Permissions

When multiple departments or roles share the same data table, some columns should be available only to specific people. For example, salary data should be visible only to authorized HR staff. Column-level permissions let you protect sensitive columns without splitting the table: define the sensitive columns, associate the permission point with authorized roles, and grant access through those roles.

## Feature Overview

Column-level permissions use an **allowlist authorization** model. Administrators first define a column-level permission point that identifies sensitive columns in specific tables, then associate that permission point with roles allowed to access them. Only users with an associated role can access these sensitive columns; other users cannot see their data.

Row-level permissions control which data rows can be viewed, while column-level permissions control which data columns can be accessed. Both are configured on tables and are independent of analysis domain configuration.

## Configuration Process

| Step | Demo | Description |
| --- | --- | --- |
| 0. Feature entry | ![](.topwrite/assets/datagpt-列权限-功能入口.png =250) | Go to **Management → User Management → Permission Rules**, then select **Column-Level Permission Points**. |
| 1. Define sensitive columns | ![](.topwrite/assets/datagpt-列权限-定义权限规则.png =250) | **Use a permission point to specify the tables and sensitive columns to protect**.&#xA;1. Enter a permission point name, such as “Salary Access”.&#xA;2. Select the target table in the permission mappings.&#xA;3. Select the sensitive column to protect.&#xA;4. Click **Add Mapping** to include additional tables or columns.&#xA;5. Save the permission point. |
| 2. Associate authorized roles | ![](.topwrite/assets/datagpt-列权限-配置权限范围.png =250) | **Associate the column-level permission point with roles allowed to access sensitive columns**.&#xA;1. Select the target role under **User Management → Authorization Management**.&#xA;2. Open **Associate Column Permission Point**, select an existing permission point, confirm the association, and save the role configuration.&#xA;3. Under **Account Management**, assign this role to the users who need access to the sensitive columns. |

## Permission Effects

| Role | Data Visibility Scope |
| :--------------------: | --- |
| Associated with the permission point | Users obtain access through the role and can access the sensitive columns protected by the permission point. |
| Not associated with the permission point | Users who have not obtained access through a role cannot access the sensitive columns protected by the permission point. They can still access other columns for which they have permission. |

### Example

Consider a brand mini app's visit-session details table.

Before configuration: Visitor ID, Entry Channel, and Campaign Tag have not been designated as sensitive columns, so all columns are accessible.

![](.topwrite/assets/datagpt-列权限-配置前.png)

After configuration: Add these columns to a column-level permission point and associate it with roles allowed to access them. The screenshot below shows the view of a user who has not obtained this permission through a role. Sensitive column data is not visible; authorized users can still view it.

![](.topwrite/assets/datagpt-列权限-配置后.png)

## Notes

1. **Define columns, then associate roles**: Use a permission point to identify the target tables and sensitive columns, then associate it with authorized roles. Users obtain access through their roles.
2. **Confirm the configuration scope**: Column-level permissions are configured on tables and are independent of analysis domain configuration.
3. **Check column dependencies**: Before designating columns as sensitive, check whether common filters, groupings, metric calculations, or Answer Builders depend on them, and review the permissions granted to the roles of the people using them.
4. **Distinguish permissions from masking**: Column-level permissions control who can access sensitive columns. To display masked values, such as partially hidden phone numbers, configure an appropriate masking solution separately.
5. **Verify authorization**: Check question-and-answer results using accounts with and without authorized roles to confirm that sensitive columns are available only to those granted access through a role.
6. **Review the allowlist regularly**: When responsibilities, table schemas, or sensitive columns change, review the roles associated with each permission point and the users assigned to those roles.

> 💡 **Tip**: Permission points define sensitive columns, roles are associated with permission points, and users obtain access through roles. Only associated roles can view the columns defined by a permission point.

## Related Documentation

- [Configure Role Authorization](datagpt-role-authorization-guide.md) — Manage roles and their permissions
- [Row-Level Permissions](row_level_permission.md) — Control which data rows different users can view
- [Data Export Governance](datagpt-data-export-governance-guide.md) — How column hiding, row-level permissions, and export governance relate
