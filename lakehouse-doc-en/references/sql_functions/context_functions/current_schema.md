# CURRENT_SCHEMA 

####  Description
The `CURRENT_SCHEMA` function is used to obtain the name of the schema currently being used by the session. This function does not require any parameters and returns a string representing the name of the current session's schema.

#### Usage Scenarios
- When you need to dynamically execute SQL statements based on the current session's schema.
- In a multi-schema environment, to determine the schema of the current session.

#### Return Result
The `CURRENT_SCHEMA` function returns a string representing the name of the current session's schema.

####  Example

**Example 1: Get the current schema**
```sql
SELECT CURRENT_SCHEMA();
```
After executing this statement, if the current session is using the default schema, it returns "default".

**Example 2: Get the current schema after switching schema**
```sql
-- Switch to the specified schema
USE SCHEMA schema1;

-- Get the current schema
SELECT CURRENT_SCHEMA();
```
After executing this statement, it returns "schema1", indicating that the current session has switched to "schema1".