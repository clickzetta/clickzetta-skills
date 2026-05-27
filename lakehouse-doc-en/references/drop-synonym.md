## Description
Delete Synonyms
##  Syntax
```SQL
DROP [TABLE|VOLUME|FUNCITON] SYNONYM [ IF EXISTS ] [ schema. ] synonym_name
```
* TABLE|VOLUME|FUNCTION: Indicates which type of object the synonym is named for,

  * **TABLE**: This is the default option. Used to name synonyms for table, table stream, materialized view, dynamic table. In these cases, the "table" keyword is optional.
  * **VOLUME**: When naming a synonym for volume, this keyword must be explicitly specified. If omitted, the system will default to looking for a table object with the same name.
  * **FUNCTION**: When naming a synonym for function, this keyword is mandatory. If not specified, the system will also default to looking for a table object with the same name.

* if exists: Optional, conditionally deletes the synonym only if it already exists.

* schema: Optional, specifies the schema where the synonym is located. If the schema is not specified, the default schema for the current session is used.

## Permissions
```SQL
grant drop synonym on all synonyms in schema <schemaname> to user uat_test_01;
```
## Example 
Create and delete synonyms for a table
```SQL
CREATE TABLE employees(id int,name string,skills array<string>);
INSERT INTO employees (id, name, skills) VALUES
(1, 'John Doe', ['Java', 'Python', 'SQL']),
(2, 'Jane Smith', ['C++', 'Hadoop', 'SQL']),
(3, 'Bob Johnson', ['Python', 'Docker']);
CREATE TABLE SYNONYM employees_syno FOR employees;
DROP SYNONYM employees_syno
```