## Function Description

Revokes previously granted privileges from a role or user. The `REVOKE` statement can revoke permissions at various levels, including workspace, workspace object, Schema, and Schema object levels.

## Workspace User and Role Permission Management Syntax

```Plain
REVOKE workspacePrivileges ON WORKSPACE workspace_name
    | workspaceObjectPrivileges ON { ROLE | SCHEMA | VCLUSTER | DATALAKE | FUNCTION } workspace_object_name
    | schemaPrivileges ON SCHEMA schema_name
    | schemaObjectPrivileges ON { TABLE | VIEW | MATERIALIZED VIEW } schema_object_name
FROM { ROLE role_name | USER user_name };
```

### Privilege Type Description

| Privilege Type | Description | Example |
|----------------|-------------|---------|
| `workspacePrivileges` | Privileges to create objects in a workspace | `CREATE SCHEMA`, `CREATE VCLUSTER` |
| `workspaceObjectPrivileges` | Privileges to modify workspace objects and view metadata | `ALTER`, `DROP`, `READ METADATA`, `ALL [PRIVILEGES]` |
| `schemaPrivileges` | Privileges to create objects in a Schema | `CREATE TABLE`, `CREATE VIEW`, `CREATE MATERIALIZED VIEW` |
| `schemaObjectPrivileges` | Privileges to modify, drop, and query Schema objects | `ALTER`, `DROP`, `SELECT`, `INSERT`, `READ METADATA`, `ALL` |

## Usage Examples

1. Revoke from role `simple_role` the privilege to create VCLUSTERs in the workspace:

   ```SQL
   REVOKE CREATE VCLUSTER ON WORKSPACE lakehouse_public FROM ROLE simple_role;
   ```

2. Revoke from role `simple_role` the `ALTER` privilege on the VCLUSTER named `default`:

   ```SQL
   REVOKE ALTER VCLUSTER ON VCLUSTER default FROM ROLE simple_role;
   ```

3. Revoke from role `uat_demo` the privilege to create tables and views in the `public` Schema:

   ```SQL
   REVOKE CREATE VIEW, CREATE TABLE ON SCHEMA public FROM ROLE uat_demo;
   ```

4. Revoke from role `reporting_role` the `READ METADATA` privilege on the DATALAKE named `sales_data`:

   ```SQL
   REVOKE READ METADATA ON DATALAKE sales_data FROM ROLE reporting_role;
   ```

5. Revoke from role `admin_role` the `ALTER` and `DROP` privileges on the FUNCTION named `order_summary`:

   ```SQL
   REVOKE ALTER, DROP ON FUNCTION order_summary FROM ROLE admin_role;
   ```

6. Revoke from role `analyst_role` the `SELECT` and `INSERT` privileges on the table `customer_orders` in the `public` Schema:

   ```SQL
   REVOKE SELECT, INSERT ON TABLE public.customer_orders FROM ROLE analyst_role;
   ```

7. Revoke role `test_readonly_role` from user `tester`:

   ```SQL
   REVOKE ROLE test_readonly_role FROM USER tester;
   ```

## Notes

- Executing this command requires the `workspace_admin` or `security_admin` role.
- After revocation, the revoked party will immediately lose the ability to access the corresponding resource.
- You can verify the revocation result using `SHOW GRANTS TO ROLE role_name` or `SHOW GRANTS TO USER user_name`.

## Instance Role Permission Management

LakeHouse supports fine-grained revocation of cross-workspace permissions for Instance Roles, ensuring flexibility and security in permission control.

### Syntax

```SQL
-- Revoke an Instance Role's permissions on a workspace
REVOKE <privilege> ON WORKSPACE <workspace_name> FROM INSTANCE ROLE <role_name>;

-- Revoke an Instance Role's permissions on a table
REVOKE <privilege> ON TABLE <workspace>.<schema>.<table> FROM INSTANCE ROLE <role_name>;

-- Revoke an Instance Role's permissions on a Schema
REVOKE <privilege> ON DATABASE <workspace>.<schema> FROM INSTANCE ROLE <role_name>;

-- Remove a user's Instance Role membership
REVOKE INSTANCE ROLE <role_name> FROM USER <user_name>;
```

### Examples

```SQL
-- Revoke all permissions on a workspace
REVOKE ALL ON WORKSPACE ws1 FROM INSTANCE ROLE inst_role;

-- Verify the revocation result (expected: no ALL privilege)
SHOW GRANTS TO INSTANCE ROLE inst_role;

-- Revoke all permissions on a single table
REVOKE ALL ON TABLE ws1.public.sales FROM INSTANCE ROLE inst_role;

-- Remove a user's Instance Role
REVOKE INSTANCE ROLE inst_role FROM USER lh_engine_test_01;
```
