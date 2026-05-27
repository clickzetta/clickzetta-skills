# Singdata Lakehouse Permission System Inventory and Optimization Best Practices Guide

## Document Information
- **Target Audience**: System administrators, security administrators, data governance teams

---

## 1. Overview

In Singdata Lakehouse, users and roles are important digital assets. As the business grows, the permission system may become complex, leading to issues such as permission redundancy and idle roles. This guide will help you:

- ✅ Understand Singdata Lakehouse's dual-layer permission system
- ✅ Master permission management via the Studio Web interface and SQL
- ✅ Differentiate between workspace-level and instance-level permission inventory perspectives
- ✅ Identify and clean up permission redundancy
- ✅ Establish a continuous permission governance mechanism

## 2. Understanding the Singdata Lakehouse Permission System

### 2.1 Dual-Layer Permission Architecture

Singdata Lakehouse employs an **Instance-Workspace** dual-layer permission system:

```
Singdata Lakehouse Instance
├── Instance-Level Resources
│   ├── Instance Users (instance user pool)
│   │   ├── Regular Users (synced from the global platform)
│   │   └── Service Users (for API/automation use)
│   └── Instance Roles (instance-level roles)
│       ├── instance_admin (instance administrator)
│       ├── instance_sre (instance operations)
│       ├── instance_datasource_admin (data source management)
│       └── ...other instance-level roles
│
└── Workspace Layer
    ├── Workspace A
    │   ├── Workspace Users (users authorized from the instance user pool)
    │   └── Workspace Roles (workspace-level roles)
    │       ├── workspace_admin
    │       ├── workspace_dev
    │       └── Custom roles
    ├── Workspace B
    │   ├── Workspace Users
    │   └── Workspace Roles
    └── Workspace C
        ├── Workspace Users
        └── Workspace Roles
```

**Key Understanding**:
- Users first exist in the instance-level user pool
- Use the `CREATE USER` command to add instance users to specific workspaces
- Instance-level roles have cross-workspace permissions
- Workspace-level roles are only effective within a specific workspace

### 2.2 Role Type Classification

| Role Type | Scope | Assignment Location | Examples | Description |
|-----------|-------|---------------------|----------|-------------|
| **Instance-Level Roles** | Across all Workspaces | Assigned at the instance level | `instance_admin`<br>`system_admin`<br>`instance_sre`<br>`instance_datasource_admin` | Have cross-workspace management permissions<br>Managed uniformly at the instance level |
| **Workspace-Level System Roles** | Single Workspace | Assigned within the workspace | `workspace_admin`<br>`workspace_dev`<br>`workspace_analyst`<br>`workspace_sre`<br>`workspace_user` | System presets; permissions limited to a specific workspace<br>Managed independently per workspace |
| **Workspace-Level Custom Roles** | Single Workspace | Created and assigned within the workspace | User-defined role names | Created based on business needs<br>Only effective within the workspace where created |

> **Important Notes**:
> - Among system preset roles, the permissions of `workspace_admin` and `instance_admin` cannot be modified
> - Permissions for other preset roles can be adjusted as needed
> - Currently, custom roles can only be created within workspaces; instance-level custom roles are not supported

### 2.3 User Management Flow

Understanding how users flow through Singdata Lakehouse:

```
1. Global Platform Users (registered at accounts.yunqi.com)
         ↓ Auto-sync
2. Instance User Pool (exists within the Lakehouse instance)
         ↓ CREATE USER command
3. Workspace Users (authorized to access a specific workspace)
         ↓ GRANT ROLE command
4. Users with Roles (with actual operational permissions)
```

> **Important Concept**: Executing `CREATE USER` in a workspace actually adds a user already existing in the instance user pool to the current workspace. This is why specifying a password is not required.

### 2.4 Role Permission Scope Description

> **Note**:
> - Permission inheritance relationships between different roles need to be verified based on the actual environment, as different versions may vary
> - The `system_admin` role is being deprecated; it is recommended to use `instance_admin` as the instance-level management role
> - It is recommended to confirm the specific permission scope of each role through actual testing

## 3. Key Concept: Two Inventory Perspectives (Must Read)

### 3.1 Workspace-Level Inventory vs Instance-Level Inventory

| Comparison Dimension | Workspace-Level Inventory | Instance-Level Inventory |
|----------------------|---------------------------|--------------------------|
| **Data Source** | information_schema (filtered) | Global metadata (requires special permissions) |
| **SQL Filter Condition** | `WHERE workspace_id = current_workspace_id()` | No filter; all data visible |
| **Visible Scope** | Current workspace only | All workspaces |
| **Applicable Scenario** | Daily permission management | Global security audits |
| **Limitations** | ❌ Cannot see other workspaces<br>❌ May misjudge permission redundancy | ❌ Requires elevated permissions<br>❌ Higher operational complexity |

### 3.2 Important Note

> ⚠️ **Key Distinction**:
> - Inventories conducted using `information_schema` are all **workspace-level inventories**, which can only see a "local view" of the current workspace
> - To perform an instance-level inventory, you need to access global data through the Studio management console or special permissions
> - How to tell: if your query is based on `information_schema` tables, you are performing a workspace-level inventory

## 5. Permission Inventory Practice Steps

### Step 1: Clarify the Inventory Level

```sql
-- Confirm the current inventory environment and level
SELECT 
    'Current Inventory Level' as check_item,
    'Workspace-Level Inventory' as level,
    current_workspace() as workspace_scope,
    'Only current workspace data is visible' as visibility_limit,
    'Use the management console for a global view if needed' as suggestion;
```

### Step 2: User Role Distribution Analysis

```sql
-- Analyze user role assignments (masked)
SELECT 
    CASE 
        WHEN user_name LIKE 'admin%' THEN 'admin_user_' || ROW_NUMBER() OVER (ORDER BY user_name)
        WHEN user_name LIKE 'dev%' THEN 'dev_user_' || ROW_NUMBER() OVER (ORDER BY user_name)
        ELSE 'user_' || ROW_NUMBER() OVER (ORDER BY user_name)
    END as masked_user,
    role_names,
    LENGTH(role_names) - LENGTH(REPLACE(role_names, ',', '')) + 1 as role_count,
    CASE 
        WHEN role_names LIKE '%system_admin%' THEN 'Contains instance-level role'
        WHEN role_names LIKE '%workspace_admin%' THEN 'Workspace Administrator'
        WHEN role_names LIKE '%workspace_dev%' THEN 'Developer'
        ELSE 'Regular User'
    END as user_category
FROM information_schema.users
ORDER BY role_count DESC;
```

### Step 3: Role Usage Analysis

```sql
-- Analyze role assignment and usage
SELECT 
    role_name,
    CASE 
        WHEN role_name LIKE 'instance_%' THEN 'Instance-Level Role (in workspace-level view)'
        WHEN role_name = 'system_admin' THEN 'Instance-Level Role (being deprecated)'
        WHEN role_name LIKE 'workspace_%' THEN 'Workspace-Level - System Preset'
        ELSE 'Workspace-Level - Custom'
    END as role_classification,
    CASE 
        WHEN user_names IS NULL OR user_names = '' THEN '⚠️ Unassigned'
        ELSE '✅ Assigned'
    END as assignment_status,
    CASE 
        WHEN user_names IS NOT NULL THEN 
            LENGTH(user_names) - LENGTH(REPLACE(user_names, ',', '')) + 1
        ELSE 0
    END as assigned_user_count,
    comment as description
FROM information_schema.roles
ORDER BY 
    CASE WHEN user_names IS NULL THEN 0 ELSE 1 END DESC,
    role_name;
```

> **Note**: Although roles like `instance_admin` are instance-level roles, they also appear in the workspace-level `information_schema.roles` view because there are users in the current workspace who have been granted that role.

### Step 4: Permission Redundancy Detection

```sql
-- Detect potential permission redundancy (must verify whether inheritance relationships truly exist between roles)
WITH permission_check AS (
    SELECT 
        CASE 
            WHEN user_name LIKE 'admin%' THEN 'admin_user'
            WHEN user_name LIKE 'dev%' THEN 'dev_user'
            ELSE 'regular_user'
        END as user_type,
        role_names,
        CASE 
            WHEN role_names LIKE '%system_admin%' 
                 AND role_names LIKE '%workspace_%'
            THEN 'Possible cross-level redundancy (needs verification)'
            WHEN role_names LIKE '%workspace_admin%' 
                 AND role_names LIKE '%workspace_user%'
            THEN 'Possible same-level redundancy (needs verification)'
            ELSE 'No apparent redundancy'
        END as redundancy_check,
        'Suggestion: actually test each role's permissions to confirm true redundancy' as action_needed
    FROM information_schema.users
)
SELECT * FROM permission_check
WHERE redundancy_check != 'No apparent redundancy';
```

### Step 5: Generate Inventory Report

```sql
-- Generate workspace-level permission inventory summary
WITH summary AS (
    SELECT 
        COUNT(DISTINCT user_name) as total_users,
        COUNT(DISTINCT role_name) as total_roles,
        SUM(CASE WHEN user_names IS NOT NULL THEN 1 ELSE 0 END) as assigned_roles,
        SUM(CASE WHEN user_names IS NULL THEN 1 ELSE 0 END) as unassigned_roles
    FROM information_schema.users
    CROSS JOIN information_schema.roles
)
SELECT 
    '===== Workspace-Level Permission Inventory Report =====' as report_header,
    current_workspace() as workspace_name,
    total_users || ' users' as user_summary,
    total_roles || ' roles (' || assigned_roles || ' assigned, ' || unassigned_roles || ' unassigned)' as role_summary,
    ROUND(assigned_roles * 100.0 / total_roles, 1) || '%' as role_utilization,
    'Note: This report only contains data from the current workspace' as important_notice
FROM summary;
```

## 6. Best Practice Recommendations

### 6.1 Tiered Permission Management Strategy

#### Workspace-Level Management (Daily Operations)
- **Frequency**: Monthly
- **Scope**: Current workspace
- **Focus**:
  - Clean up obvious role redundancy within the workspace
  - Handle custom roles that have been unassigned for a long time
  - Optimize role combinations for users within the workspace

#### Instance-Level Management (Periodic Audits)
- **Frequency**: Quarterly
- **Scope**: All workspaces
- **Focus**:
  - Audit global assignment of system_admin
  - Check cross-workspace permission consistency
  - Identify cross-workspace account duplication

### 6.2 Permission Assignment Decision Tree

```
User needs cross-workspace management?
├─ Yes → Consider assigning system_admin (requires instance-level approval)
└─ No → Only assign roles within the current workspace
        │
        Need to manage the workspace?
        ├─ Yes → Assign workspace_admin
        └─ No → Need development permissions?
                ├─ Yes → Assign workspace_dev
                └─ No → Assign workspace_user or other roles
```

### 6.3 Avoiding Common Pitfalls

| Pitfall | Correct Approach |
|---------|------------------|
| Thinking users only exist in workspaces | Understand that users first exist in the instance user pool, then are added to workspaces |
| Judging instance-level role redundancy based solely on workspace-level view | Need instance-level view to confirm global usage |
| Assuming inheritance relationships definitely exist between roles | Actually test and verify the specific permissions of each role |
| Deleting all unused roles at once | Understand the purpose of roles first; process in batches |
| Confusing the management location of instance-level and workspace-level roles | Instance-level roles managed at the instance level; workspace-level roles managed within the workspace |
| Using deprecated roles in SQL | Use `instance_admin` instead of the soon-to-be-deprecated `system_admin` |

### 6.4 Management Tool Selection Recommendations

| Management Task | Recommended Tool | Reason |
|-----------------|------------------|--------|
| Daily user authorization | Studio Web Interface | Intuitive operations, less error-prone |
| Batch permission changes | SQL Scripts | High efficiency, repeatable execution |
| Permission audit reports | SQL queries + Studio | Best results when combined |
| Instance-level management | Studio Management Console | Visual global view |
| Automated monitoring | API + SQL | Suitable for integration into monitoring systems |

### 6.5 Monitoring Metric Recommendations

1. **Workspace-Level Metrics** (directly monitorable)
   - Role usage rate = Number of assigned roles / Total roles in workspace
   - Average roles per user = Total role assignments / Number of users
   - Custom role ratio = Number of custom roles / Total roles

2. **Instance-Level Metrics** (require global permissions)
   - system_admin distribution = Number of system_admin users per workspace
   - Cross-workspace user duplication rate = Duplicate users / Total users
   - Global role standardization level = Number of workspaces using system roles / Total workspaces

## 7. Automation and Continuous Improvement

### 7.1 Create Monitoring View

```sql
-- Create workspace-level permission monitoring view
CREATE  VIEW workspace_permission_monitor AS
SELECT 
    current_date() as monitor_date,
    current_workspace() as workspace,
    'Workspace-Level Monitoring' as monitor_level,
    COUNT(DISTINCT u.user_name) as user_count,
    COUNT(DISTINCT r.role_name) as role_count,
    SUM(CASE WHEN r.user_names IS NOT NULL THEN 1 ELSE 0 END) as active_roles,
    ROUND(
        SUM(CASE WHEN r.user_names IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / 
        COUNT(DISTINCT r.role_name), 
        1
    ) as role_usage_percentage,
    COUNT(DISTINCT CASE WHEN u.role_names LIKE '%system_admin%' THEN u.user_name END) as admin_users
FROM information_schema.users u
CROSS JOIN information_schema.roles r
GROUP BY workspace;
```

### 7.2 Periodic Check Script

```sql
-- Monthly permission health check
WITH health_check AS (
    -- Check 1: Unused roles
    SELECT 
        'unused_roles' as check_type,
        COUNT(*) as issue_count,
        'Unassigned roles exist' as description
    FROM information_schema.roles
    WHERE user_names IS NULL OR user_names = ''
    
    UNION ALL
    
    -- Check 2: Potential permission redundancy
    SELECT 
        'potential_redundancy' as check_type,
        COUNT(*) as issue_count,
        'Users may have role redundancy' as description
    FROM information_schema.users
    WHERE LENGTH(role_names) - LENGTH(REPLACE(role_names, ',', '')) + 1 > 2
    
    UNION ALL
    
    -- Check 3: High-privilege users
    SELECT 
        'high_privilege_users' as check_type,
        COUNT(*) as issue_count,
        'Users with admin permissions' as description
    FROM information_schema.users
    WHERE role_names LIKE '%admin%'
)
SELECT 
    check_type,
    issue_count,
    description,
    CASE 
        WHEN issue_count > 0 THEN 'Needs attention'
        ELSE 'Normal'
    END as status
FROM health_check
ORDER BY issue_count DESC;
```

## 8. Summary and Recommendations

### 8.1 Core Takeaways

1. **Clarify the inventory level**: Always be aware of whether you are performing a workspace-level or instance-level inventory
2. **Understand limitations**: Workspace-level inventories cannot see the global picture; major decisions require an instance-level perspective
3. **Verify assumptions**: Do not assume inheritance relationships between roles; actual verification is needed
4. **Use the right tools**: Prioritize the Studio Web interface for daily management; use SQL for batch operations
5. **Continuous optimization**: Establish a regular audit mechanism and continuously improve permission management

### 8.2 Action Recommendations

- **Immediate Actions**:
  - Log into Studio to view the current permission distribution
  - Use the queries in this guide to perform the first workspace-level inventory
- **Short-Term Plans**:
  - Set up a permission change approval process in Studio
  - Establish a monthly permission audit mechanism
- **Long-Term Goals**:
  - Achieve automated permission monitoring and optimization
  - Establish a cross-workspace permission standardization system

### 8.3 Getting Help

If you need to perform an instance-level permission audit or have other questions, please:
1. View the help documentation in Studio
2. Contact your Singdata Lakehouse administrator
3. Consult the official Singdata Lakehouse documentation
4. Submit a technical support ticket

---

**Appendix: Quick Reference Card**

| Task | Workspace-Level Method | Instance-Level Method |
|------|------------------------|------------------------|
| View all users | Studio -> Workspace -> Users<br>or `SELECT * FROM information_schema.users` | Studio -> Management -> Security -> Users |
| View all roles | Studio -> Workspace -> Roles<br>or `SHOW ROLES` | Studio -> Management -> Security -> Roles |
| User authorization | Studio interface operations<br>or `GRANT ROLE ... TO USER ...` | Studio Management Console |
| Calculate role usage rate | SQL queries in this guide | Studio reporting features |
| Discover permission redundancy | Judgment based on current workspace | Comprehensive cross-workspace analysis |
| Clean up unused roles | Custom roles only | Global standardization possible |

***

**Note**: This document is compiled based on the Lakehouse product documentation as of June 2025. It is recommended to periodically check the official documentation for the latest updates. Before using in a production environment, be sure to verify the correctness and performance impact of all operations in a test environment.
