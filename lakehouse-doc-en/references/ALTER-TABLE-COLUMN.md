# Description

This feature allows users to modify columns in a table using the ALTER statement, including adding columns, modifying columns, deleting columns, and renaming columns. It also supports changes to complex types such as struct, array, and map.

# Add Column

## Syntax
```sql
-- Add column
ALTER TABLE table_name ADD COLUMN
      column1_name_identifier data_type [COMMENT comment]
      [FIRST | AFTER column1_name_identifier]  ,....

column_name_identifier :==
    -- Ordinary field
    column_name
    -- Complex type struct representation
    -- struct type struct,<x: double, y: double>
    column_name.struct_column_name  
    -- array type nested struct representation
    -- Add field, array<struct<x: double, y: double>>
    column_name.ELEMENT.struct_column_name
    -- map type nested struct representation
    -- map key add field
    column_name.KEY.struct_column_name 
    -- map value add field
    column_name.VALUE.struct_column_name    
```
## Parameter Description

- **column_name_identifier**: Field identifier, used to specify the name of the field to be added, deleted, or renamed.
- **FIRST | AFTER column_name_identifier**: Specifies the position to add the field, either before or after the field.

## Usage Example

1. Add a regular field:
   ```sql
   ALTER TABLE my_table ADD COLUMN new_column INT;
   ```
2. Add Complex Type Fields:
```sql
CREATE TABLE my_complex_table (
    point STRUCT<x: INT, y: DOUBLE>,
    points ARRAY<STRUCT<x: DOUBLE, y: DOUBLE>>,
    points_map MAP<STRUCT<x: INT>, STRUCT<a: INT>>
);

-- Add field in struct
ALTER TABLE my_complex_table ADD COLUMN point.z DOUBLE;

-- Add field in struct within map value
ALTER TABLE my_complex_table ADD COLUMN points_map.value.b INT;

-- Add field in struct within map key
ALTER TABLE my_complex_table ADD COLUMN points_map.key.y INT;

-- Add field in struct within array
ALTER TABLE my_complex_table ADD COLUMN points.element.z DOUBLE;
```
# Delete Field

## Syntax
```sql
ALTER TABLE table_name DROP COLUMN column_name_identifier [, column_name_identifier ... ]
```
## Usage Example

1. Delete a regular field:
   ```sql
   ALTER TABLE my_table DROP COLUMN old_column;
   ```
2. Delete complex type fields:
   ```sql
   ALTER TABLE my_complex_table DROP COLUMN point.z;
   ALTER TABLE my_complex_table DROP COLUMN points.element.y;
   ALTER TABLE my_complex_table DROP COLUMN points_map.key.x;
   ```
# Rename Fields

## Syntax
```sql
ALTER TABLE table_name RENAME COLUMN column_name_identifier TO new_column_name_identifier;
```
## Usage Example

1. Rename common fields:
   ```sql
   ALTER TABLE my_table RENAME COLUMN old_name TO new_name;
   ```
2. Rename complex type fields：
   ```sql
   ALTER TABLE my_complex_table RENAME COLUMN point.x TO xx;
   ALTER TABLE my_complex_table RENAME COLUMN points.element.x TO xx;
   ALTER TABLE my_complex_table RENAME COLUMN points_map.key.x TO xx;
   ```
# Modify Fields

## Syntax
```sql
-- Modify column position
ALTER TABLE table_name CHANGE COLUMN column_name_identifier { FIRST | AFTER column_identifier }

-- Modify column type
ALTER TABLE table_name CHANGE COLUMN column_name_identifier TYPE data_type

-- Modify column comment
ALTER TABLE table_name CHANGE COLUMN column_name_identifier COMMENT 'comment'
```
## Currently Supported Type Conversions

|          |          |     |        |       |        |                 |      |         |        |        |
| -------- | -------- | --- | ------ | ----- | ------ | --------------- | ---- | ------- | ------ | ------ |
| from\to  | smallint | int | bigint | float | double | decimal         | date | varchar | char   | string |
| tinyint  | ☑️       | ☑️  | ☑️     |       |        |                 |      |         |        |        |
| smallint | ☑️       | ☑️  | ☑️     |       |        |                 |      |         |        |        |
| int      |          | ☑️  | ☑️     |       |        |                 |      |         |        |        |
| bigint   |          |     | ☑️     |       |        |                 |      |         |        |        |
| float    |          |     |        | ☑️    | ☑️     |                 |      |         |        |        |
| double   |          |     |        |       | ☑️     |                 |      |         |        |        |
| decimal  |          |     |        |       |        | Supports increasing precision for both integer and decimal places |      |         |        |        |
| Date     |          |     |        |       |        |                 | ☑️   |         |        |        |
| Varchar  |          |     |        |       |        |                 |      | Allowed to become longer  |        | ☑️     |
| Char     |          |     |        |       |        |                 |      |         | Allowed to become longer | ☑️     |
| String   |          |     |        |       |        |                 |      |         |        |        |