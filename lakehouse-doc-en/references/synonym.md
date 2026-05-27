# Synonyms
## Overview

A synonym is a database object, similar to giving an object an alias, and has the following uses:

* When you need to query table t in schema01 from schema02 but do not want to duplicate the data, you can create a synonym sy\_t for table t in schema02. This way, you can directly query sy\_t in schema02, and the data will remain consistent with table t in schema01 in real-time. This is an efficient data management strategy that ensures data consistency while avoiding unnecessary data duplication.
* Provides an abstraction layer that protects client applications from changes to the name or location of the underlying objects.

Synonyms belong to a schema, and like other objects in the schema, the name of a synonym must be unique under that type of object. Synonyms can be created for the following objects: table, table stream, dynamic table, materialized view, volume, function.

## Operation Management
### Creation
```SQL
CREATE  [TABLE|VOLUME|FUNCITON] SYNONYM [schema_name.] synonym_name FOR object COMMENT''
object ::=
workspace_name.schema_name.object_name|schema_name.object_name｜object_name
```
* TABLE|VOLUME|FUNCTION: Indicates the type of synonym object.

  * **TABLE**: This is the default option. Used to name synonyms for table, table stream, materialized view, dynamic table. In these cases, the "table" keyword is optional.
  * **VOLUME**: When naming a volume synonym, this keyword must be explicitly specified. If omitted, the system will default to looking for a table object with the same name. FUNCTION, if naming a function synonym, this keyword must be filled in. If not filled in, it will look for a table object with the same name.
  * **FUNCTION**: When naming a function synonym, this keyword is mandatory. If not specified, the system will also default to looking for a table object with the same name.

* synonym\_name: The name of the synonym, following metadata specifications.

* object: Specifies the name of the base object, supports workspace\_name.schema\_name\_2.object\_name, schema\_name\_2.name format. If the schema is omitted, the object in the current schema is used.

### Delete
```SQL
DROP [TABLE|VOLUME|FUNCITON] SYNONYM [ IF EXISTS ] [ schema. ] synonym_name
```
* TABLE|VOLUME|FUNCTION: Indicates which type of object the synonym is being named for,

  * **TABLE**: This is the default option. Used to name synonyms for table, table stream, materialized view, dynamic table. In these cases, the "table" keyword is optional.
  * **VOLUME**: When naming a volume synonym, this keyword must be explicitly specified. If omitted, the system will default to looking for a table object with the same name.
  * **FUNCTION**: When naming a function synonym, this keyword is mandatory. If not specified, the system will also default to looking for a table object with the same name.

* if exists: Optional, conditionally deletes the synonym only if it already exists.

* schema: Optional, specifies the schema where the synonym is located. If the schema is not specified, the default schema of the current session is used.

### Permissions

Creating a synonym requires create synonym permission.
```SQL
grant create synonym  on schema  scname to user uat_test_01;
```
## Delete Synonyms

Deleting synonyms requires drop permission
```SQL
grant drop synonym on all synonyms in schema <schemaname> to user uat_test_01;
grant create synonym  on schema  scname to user uat_test_01;
```
Synonym Query Permissions

**Synonym** permissions are the same as the permissions for the base table object. Granting permissions on a synonym is equivalent to granting permissions on the corresponding base table object. Similarly, granting permissions on the base table object is equivalent to granting permissions on all synonyms for that object. If a user is granted permissions on a synonym, the user can use either the synonym name or the base table object name in SQL statements exercising those permissions.

### List SYNONYM
```SQL
SHOW SYNONYMS [IN {SCHEMA scname | WORKSPACE wbname}] [WHRERE <expr>]
```
## Usage Example

Create a synonym for the table
```SQL
-- Create table
CREATE TABLE `public`.students(
  `name` string,
  `class` string);
-- Create synonym for the table
CREATE SYNONYM students_sy for `public`.students;
-- Query synonym
select * from students_sy;
-- Drop synonym
drop synonym students_sy;
```
Creating a synonym for a table stream, the syntax for creating a synonym for a table stream is the same as for a table
```SQL
create  synonym students_stream_synonym for public.students_stream;
-- Delete synonym
drop synonym students_stream_synonym;
```
To create a synonym for a dynamic table, the syntax for creating a synonym for a dynamic table is the same as for a table.
Sure, here is the translated content:

```SQL
create synonym event_group_minute_sy for public.event_group_minute;
-- Delete synonym
Creating a synonym for a materialized view follows the same syntax as creating a synonym for a table.
```SQL
create SYNONYM event_group_mv_sy for event_group_mv;
-- Delete synonym
drop synonym event_group_mv_sy;
```
Here is the translated content:

Create a synonym for volume, where volume is required. If not specified, it will automatically search for objects with the same name as table, materialized view, table stream, and dynamic table.
```SQL
create volume synonym hz_csv_volume_sy for public.hz_csv_volume;
--Delete synonym
drop volume synonym hz_csv_volume_sy;
```
Here is the translated content:

Create a synonym for the function, where the function is required. If not specified, it will automatically search for objects with the same name as table, materialized view, table stream, dynamic table.
```SQL
create function synonym s_swu_udf_upper_aliyun_java_upper for public.swu_udf_upper_aliyun_java_upper;
-- Delete synonym
drop function synonym s_swu_udf_upper_aliyun_java_upper;
```
## Get Synonyms
```SQL
show synonyms in  public where synonym_name='students_sy';
+--------------+-------------------------+-------------+-----------------------+
| synonym_name |       create_time       | target_type |       target_name     |
+--------------+-------------------------+-------------+-----------------------+
| students_sy  | 2024-06-14 10:21:00.504 | TABLE       | ql_ws.`public`.studen |
+--------------+-------------------------+-------------+-----------------------+
```