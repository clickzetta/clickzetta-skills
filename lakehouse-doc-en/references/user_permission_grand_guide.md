# Lakehouse User Authorization Getting Started Guide

## 1. Introduction

Singdata Lakehouse adopts a flexible and powerful permission management system, implementing fine-grained data access management through Role-Based Access Control (RBAC). This guide combines theoretical knowledge with practical operations to detail the user authorization management process in Lakehouse, helping administrators efficiently manage data resource access permissions.

This guide also validates the process through a hands-on experiment.

^

:-: ![](.topwrite/assets/image_1747735632210.png =796)

^

## 2. User Management System Architecture

### 2.1 User Hierarchy

The Singdata Lakehouse user management system is divided into two levels:

* **Global Users**: Users managed globally on the Singdata platform. Each user has an independent identity with a unique username and password.
* **Workspace Users**: Users within a specific workspace in a specific Lakehouse service instance, who can only be granted corresponding roles and permissions within the workspace.

> **Important Concept**: Global users are automatically synced to each service instance, becoming service instance users and supplying user identities for all workspaces, but further authorization within the workspace is required. Therefore, when we create a user within a workspace using SQL, we are essentially adding a user already present in the service instance to the current workspace. This is a workspace-level authorization operation, not actual user creation. This is why no password is required when creating a user with SQL in a workspace.

### 2.2 User Types

* **Regular Users**: Represent actual personnel within the enterprise, used for daily data query, analysis, and management operations.
* **Service Users**: Special users that serve automation processes or system-level operations. Web login is not allowed, but they can be used for JDBC connections or scheduled tasks.

## 3. Role Management Basics

### 3.1 Role Definition and Types

A role is an authorization management tool that consolidates multiple permission points together and then grants them to one or more users. Roles in Lakehouse are divided into two types:

* **Built-in Roles**: System-automatically configured roles that cannot be deleted, can have their permissions modified\*, and can be directly granted to users.
* **Custom Roles**: Roles created by users based on business needs, with flexible permission configuration and maintenance.

\*Note: Among built-in roles, workspace_admin and instance_admin do not allow permission modification. Other built-in roles can have their permissions modified.

### 3.2 Role Levels

* **Instance Role**: Used for global governance of instance-level resources and operations, or permission grants across multiple workspaces.
* **Workspace Role**: Acts on objects within a specific workspace, such as schemas, tables, virtual clusters, etc.

## 4. Practical Operation Steps

### 4.1 User Management Operations

**1. Add a User to a Workspace**

```sql
-- Add a user already existing in the service instance to the current workspace
CREATE USER username;
```

**2. View Users in the Workspace**

```sql
-- Show all users in the current workspace
SHOW USERS;
```

**3. Remove a User from the Workspace**

```sql
-- Remove a user from the current workspace (does not affect the user in the service instance)
DROP USER username;
```

### 4.2 Role Management Operations

**1. Create a Custom Role**

```sql
-- Create a workspace-level custom role
CREATE ROLE role_name;
```

**2. View Roles**

```sql
-- View all roles in the current workspace
SHOW ROLES;
```

**3. Delete a Role**

```sql
-- Delete a custom role
DROP ROLE role_name;
```

### 4.3 Permission Granting Operations

**1. Grant Schema-level Permissions**

```sql
-- Grant a role the permissions to create tables and views on a schema
GRANT CREATE TABLE, CREATE VIEW ON SCHEMA schema_name TO ROLE role_name;
```

**2. Grant Table-level Permissions**

```sql
-- Grant a role permissions such as query, modify on a table
GRANT SELECT, INSERT, UPDATE, DELETE, ALTER ON TABLE schema_name.table_name TO ROLE role_name;
```

**3. Grant View Permissions**

```sql
-- Grant a role query permission on a view
GRANT SELECT VIEW schema_name.view_name TO ROLE role_name;
```

**4. Grant a Role to a User**

```sql
-- Grant a role to a user
GRANT ROLE role_name TO USER username;
```

### 4.4 Permission Revocation Operations

**1. Revoke Object Permissions**

```sql
-- Revoke SELECT permission on a table
REVOKE SELECT ON TABLE schema_name.table_name FROM ROLE role_name;
```

**2. Revoke a Role from a User**

```sql
-- Revoke a role from a user
REVOKE ROLE role_name FROM USER username;
```

## 5. Permission Verification and Auditing

### 5.1 Query User Permissions

```sql
-- View the roles and permissions granted to a user
SHOW GRANTS TO USER username;
```

### 5.2 Query Role Permissions

```sql
-- View the specific permissions granted to a role
SHOW GRANTS TO ROLE role_name;
```

### 5.3 Query Granted Permissions on an Object

```sql
-- View the specific permissions granted on a table and to which role/user
SHOW GRANTS ON table schema_name.table_name;
```

### 5.3 Query Current User

```sql
-- Get the current logged-in user
SELECT CURRENT_USER();
```

##

## 6. Complete Lab Case

The following is a complete user authorization management practice case, covering the full workflow from creating users to cleaning up the environment:

### 6.1 Create Test Users

```sql
-- Create test users (add service instance users to the workspace)
CREATE USER test01;
CREATE USER test02;

-- Verify user creation was successful
SHOW USERS;
```

### 6.2 Create Test Environment

```sql
-- Create test Schema and table
CREATE SCHEMA IF NOT EXISTS permission_test_schema;

CREATE TABLE IF NOT EXISTS permission_test_schema.permission_test_sales_data (
    id INT,
    product_name VARCHAR(100),
    sale_date DATE,
    amount DECIMAL(10,2)
);

-- Insert test data
INSERT INTO permission_test_schema.permission_test_sales_data VALUES 
    (1, 'Product A', date '2025-01-15', 1500.00),
    (2, 'Product B', date '2025-01-20', 2300.50),
    (3, 'Product C', date '2025-02-05', 800.75);
```

### 6.3 Create and Grant Roles

```sql
-- Create roles
CREATE ROLE permission_test_developer_role;
CREATE ROLE permission_test_analyst_role;

-- Configure role permissions
-- Grant developer role more permissions
GRANT CREATE TABLE, CREATE VIEW ON SCHEMA permission_test_schema TO ROLE permission_test_developer_role;
GRANT SELECT, INSERT, UPDATE, DELETE, ALTER ON TABLE permission_test_schema.permission_test_sales_data TO ROLE permission_test_developer_role;

-- Grant analyst role read-only permission
GRANT SELECT ON TABLE permission_test_schema.permission_test_sales_data TO ROLE permission_test_analyst_role;

-- Grant roles to users
GRANT ROLE permission_test_developer_role TO USER test01;
GRANT ROLE permission_test_analyst_role TO USER test02;
```

### 6.4 Verify Permission Configuration

```sql
-- View user permissions
SHOW GRANTS TO USER test01;
SHOW GRANTS TO USER test02;

-- View role permissions
SHOW GRANTS TO ROLE permission_test_developer_role;
SHOW GRANTS TO ROLE permission_test_analyst_role;
```

### 6.5 Environment Cleanup

```sql
-- Revoke role permissions
REVOKE ROLE permission_test_developer_role FROM USER test01;
REVOKE ROLE permission_test_analyst_role FROM USER test02;

-- Delete views and tables
DROP VIEW IF EXISTS permission_test_schema.permission_test_sales_view;
DROP TABLE IF EXISTS permission_test_schema.permission_test_sales_data;

-- Delete roles
DROP ROLE permission_test_developer_role;
DROP ROLE permission_test_analyst_role;

-- Delete Schema
DROP SCHEMA IF EXISTS permission_test_schema;

-- Remove users
DROP USER test01;
DROP USER test02;

-- Verify users have been removed
SHOW USERS;
```

## 7. Best Practices and Notes

### 7.1 User Management Best Practices

* **Understand User Hierarchy**: Distinguish between global account users and service instance users, and clearly understand the actual role of `CREATE USER` in a workspace.
* **Check Before User Creation**: Use `SHOW USERS` to confirm whether a user already exists in the workspace to avoid redundant operations.
* **Standardized Naming for Service Users**: For service users of automation processes, it is recommended to use specific prefixes for naming, such as `svc_`, for easy distinction.

### 7.2 Role Management Best Practices

* **Follow the Principle of Least Privilege**: Role permission design should follow the principle of least privilege, granting only necessary permissions.
* **Hierarchical Role Design**: Design a hierarchical role structure to facilitate permission management and maintenance.
* **Role Naming Conventions**: Use standardized naming conventions, such as `[business_domain]_[function]_role` format.

### 7.3 Permission Auditing and Maintenance

* **Regular Auditing**: Regularly review user permissions and role assignments to ensure compliance with security requirements.
* **Permission Change Records**: Record important permission change operations for traceability.
* **Test Verification**: After permission changes, use the relevant user identity to test and verify that permissions have taken effect correctly.

## 8. FAQ

**Q1: Why is no password required when creating a user in a workspace?**

A1: This is because when the `CREATE USER` command is executed in a workspace, it actually adds a user already existing in the service instance to the current workspace. It is an authorization operation, not actual user creation. The user's identity verification information (such as password) is managed at the global account level.

**Q2: After a user is removed from one workspace, does it affect their access in other workspaces?**

A2: No. The `DROP USER` command only removes the user from the current workspace. It does not affect the user's permissions and access in other workspaces, nor does it delete the user's information in the service instance.

**Q3: How to view all authorization details for a specific object (such as a table)?**

A3: Use the `SHOW GRANTS ON <object_name>` statement. You can also query the information schema.

**Q4: What is the difference between built-in roles and custom roles?**

A4: Built-in roles are automatically configured by the system, cannot be deleted, and are suitable for common scenarios. Custom roles are created by users with flexibly configurable permissions, suitable for specific business needs.

**Q5: Can a user have multiple roles simultaneously?**

A5: Yes. A user can be granted multiple roles and will obtain the union of all permissions from those roles.

## 9. Summary

The Singdata Lakehouse user authorization management system is both powerful and flexible. Through the Role-Based Access Control model, fine-grained permission management can be achieved. This guide combines theoretical explanations with practical operations, comprehensively introducing the complete workflow from user management to permission auditing, helping administrators manage data access security more efficiently.

In practice, you should fully understand the user hierarchy, properly plan role and permission architectures, and conduct regular permission audits to ensure data security while improving authorization management efficiency.

***

*Reference Documents*

* [Lakehouse User Identity Management Document](user-identification.md)
* [Lakehouse Role and Permission Management Document](role-privlilige-manage.md)
* [Security Feature Overview](security_overview.md)

^
