## Description

This command is used to view the structure of a materialized view, similar to the command for viewing table structures. By using the DESC command, users can easily obtain detailed information about the materialized view, including field names, data types, constraints, etc., to better understand the structure and characteristics of the materialized view.

For more detailed information, please refer to [Materialized View](<MATERIALIZEDVIEW.md>).

## Syntax

DESC [materialized view name];

Parameter description:
- Materialized view name: Specifies the name of the materialized view whose structure needs to be viewed.

[Refer to DESC Table](DESCTABLE.md)

## Example

The following is an example of using the DESC command to view the structure of a materialized view:

Example 1: View the structure of the materialized view named mv_inventory_refresh
```
DESC mv_inventory_refresh;
```
Example 2: View the structure of the materialized view named mv_sales and display detailed information
```
DESC EXTENDED mv_inventory_refresh;
```
![](.topwrite/assets/image_1735201877904.png)
