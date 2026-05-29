## Description
This command is used to delete one or more views from the current schema or a specified schema. It is important to note that once a view is deleted, the related data will not be accessible through that view unless the view is recreated.

## Syntax
```
DROP VIEW [ IF EXISTS ] view_name;
```
## Parameter Description

- `IF EXISTS`: Optional parameter used to avoid errors if the view does not exist.
- `view_name`: Specifies the name of the view to be deleted. It can be a single view name or use the <schema_name>.<view_name> format to specify the schema and view name.

##  Example

**Example 1: Delete a view under the current schema**

Suppose we need to delete a view named `myview`, we can use the following command:
```
DROP VIEW myview;
```
**Example 2: Delete a view under a specified schema**

If we want to delete the `myview` view under the `my_schema` schema, we can use the following command:
```
DROP VIEW my_schema.myview;
```