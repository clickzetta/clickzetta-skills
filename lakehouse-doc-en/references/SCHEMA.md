# SCHEMA

In database design, SCHEMA is a key concept for organizing and managing data. It provides users with a flexible way to define the structure and relationships of data. By using SCHEMA, related database objects (such as tables, views, etc.) can be logically grouped, making the data structure clearer and easier to maintain and expand.

## Main Functions of SCHEMA

1. **Logical Grouping**: SCHEMA allows users to logically group database objects based on business functions, data types, or other criteria, thereby achieving orderly organization of data.
2. **Permission Management**: Through SCHEMA, more granular permission control can be implemented on database objects. Users can set corresponding access permissions for different SCHEMAs to achieve secure management.
3. **Namespace**: SCHEMA provides namespace functionality, which helps avoid object name conflicts. This is especially important in large projects or multi-user environments.
4. **Simplified Operations**: Users can quickly switch the current operating SCHEMA using the `USE` command, simplifying daily database operations and improving work efficiency.

## SCHEMA Management Commands

Singdata Lakehouse provides a series of commands to manage schemas, including creating, deleting, viewing details, switching, and listing.

* [Create SCHEMA](CREATESCHEMA.md): Use the `CREATE SCHEMA` command to create a new schema. For example, `CREATE SCHEMA myschema;` will create a schema named `myschema`.
* [Delete SCHEMA](DROPSCHEMA.md): If a SCHEMA is no longer needed, you can use the `DROP SCHEMA` command to delete it. Before performing the deletion, ensure that the relevant data has been backed up or migrated to prevent data loss.
* [View SCHEMA Details](DESCSCHEMAS.md): Using the `DESC SCHEMAS` command, users can view detailed information about all schemas in the current space, including creation time, number of objects, etc.
* [Switch SCHEMA](USESCHEMA.md): Use the `USE SCHEMA` command to switch the default schema of the current session. For example, `USE SCHEMA myschema;` will set `myschema` as the default SCHEMA for the current session.
* [List All SCHEMAs in the Current Space](show-schemas.md): Using the `SHOW SCHEMAS` command, users can list all schemas in the current space for easier management and selection.
* [Modify SCHEMA](<ALTER-SCHEMA.md>): Supports modifying schema properties and renaming schemas.

##  Example

The following is an application example demonstrating how to create and switch SCHEMA:
```sql
-- Create a new SCHEMA
CREATE SCHEMA myschema;

-- Specify SCHEMA when creating a table
CREATE TABLE myschema.mytable (
    id INT PRIMARY KEY,
    name VARCHAR(50)
);

-- Switch to the newly created SCHEMA
USE SCHEMA myschema;

-- Query the table structure in the current SCHEMA
DESC TABLE mytable;

-- Insert data into the table
INSERT INTO myschema.mytable (id, name) VALUES (1, 'John Doe');

-- Query data from the table
SELECT * FROM myschema.mytable;
```