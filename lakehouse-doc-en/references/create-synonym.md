## Description

Create synonyms. A synonym is a database object, similar to giving an object an alias. It supports creating synonyms for the following objects: table, table stream, dynamic table, materialized view, volume, function.

##  Syntax
```SQL
CREATE  [TABLE|VOLUME|FUNCITON] SYNONYM [schema_name.] synonym_name FOR object COMMENT''
object ::=
workspace_name.schema_name.object_name|schema_name.object_name｜object_name
```
* TABLE|VOLUME|FUNCTION: Indicates the type of object for which the synonym is being created,

  * **TABLE**: This is the default option. Used to create synonyms for tables, table streams, materialized views, and dynamic tables. In these cases, the "table" keyword is optional.
  * **VOLUME**: When creating a synonym for a volume, this keyword must be explicitly specified. If omitted, the system will default to looking for a table object with the same name.
  * **FUNCTION**: When creating a synonym for a function, this keyword is mandatory. If not specified, the system will also default to looking for a table object with the same name.

* synonym\_name: The name of the synonym, following metadata conventions.

* object: Specifies the name of the base object. Supports formats like workspace\_name.schema\_name\_2.object\_name and schema\_name\_2.name. If the schema is omitted, the object in the current schema will be used.

## Permissions

* Creating a synonym requires create synonym permission.
```SQL
grant create synonym  on schema  scname to user uat_test_01;
```
## Usage

1. For specific usage, refer to [Synonym Usage](synonym.md)
2. When a synonym reference (such as TABLE, TABLE STREAM, MATERIALIZED VIEW, DYNAMIC TABLE, VOLUME, FUNCTION, etc.) is deleted, and a new reference with the same name is subsequently created, the system will automatically point to and use the new reference. This means that any reference to the original object will automatically apply to the new object after it is created, without the need to change existing queries or code.

## Example

Case 1: Creating a synonym for a table
```SQL
CREATE TABLE employees(id int,name string,skills array<string>);
INSERT INTO employees (id, name, skills) VALUES
(1, 'John Doe', ['Java', 'Python', 'SQL']),
(2, 'Jane Smith', ['C++', 'Hadoop', 'SQL']),
(3, 'Bob Johnson', ['Python', 'Docker']);
CREATE TABLE SYNONYM employees_syno FOR employees;
-- Query synonym
SELECT * FROM employees_syno;
+----+-------------+-------------------------+
| id |    name     |         skills          |
+----+-------------+-------------------------+
| 1  | John Doe    | ["Java","Python","SQL"] |
| 2  | Jane Smith  | ["C++","Hadoop","SQL"]  |
| 3  | Bob Johnson | ["Python","Docker"]     |
+----+-------------+-------------------------+

```
Case 2: Create a synonym for table stream, the syntax for creating a synonym for table stream is the same as for table
```SQL
CREATE  SYNONYM employees_stream_synonym FOR public.employees_stream;
-- Delete synonym
DROP SYNONYM employees_stream_synonym;
```
Case 3: Create a synonym for DYNAMIC TABLE, the syntax for creating a synonym for DYNAMIC TABLE is the same as for TABLE

```
CREATE SYNONYM dt\_synonym for public.my_dt;
DROP SYNONYM dt_synonym;
```