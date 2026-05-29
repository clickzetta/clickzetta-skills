# Description

This feature allows users to modify columns in a table using the ALTER statement, including adding columns, modifying columns, deleting columns, and renaming columns. It also supports changes to complex types such as struct, array, and map.

# Add Column

## Syntax

```sql
-- Add column
ALTER TABLE table_name ADD COLUMN
      column1_name_identifier data_type [COMMENT comment]
      [FIRST | AFTER column1_name_identifier | BEFORE column1_name_identifier]  ,....

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

## Usage Examples

1. Add a regular field:

   ```sql
   ALTER TABLE my_table ADD COLUMN new_column INT;
   ```

2. Add complex type fields:

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

   -- Add multiple fields and specify positions at the same time
   CREATE TABLE test (a string);
   ALTER TABLE test ADD COLUMN b string, c string, CHANGE COLUMN a AFTER c;
   ```

# Delete Field

## Syntax

```sql
ALTER TABLE table_name DROP COLUMN column_name_identifier [, column_name_identifier ... ]
```

## Usage Examples

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

**Note**: When dropping a column, if there are indexes on that column (such as inverted indexes, bloom filter indexes, etc.), the system automatically cascades and drops those indexes.

# Rename Fields

## Syntax

```sql
ALTER TABLE table_name RENAME COLUMN column_name_identifier TO new_column_name_identifier;
```

## Usage Examples

1. Rename a regular field:

   ```sql
   ALTER TABLE my_table RENAME COLUMN old_name TO new_name;
   ```

2. Rename complex type fields:

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

DECIMAL type conversion **only supports scenarios where both precision (integer digits) and scale (decimal digits) increase simultaneously**.

**The two parameters of DECIMAL type**

```
DECIMAL(P, S)  ├─ P (Precision): total number of digits (integer digits + decimal digits)  └─ S (Scale): number of decimal digits
```

For example: `DECIMAL(10, 2)` means

* 10 total digits
* 2 of which are decimal digits

**Scenario 1: Both parameters increase**

```sql
-- Source table definition
CREATE TABLE test_alter(a DECIMAL(10,2));
-- Correct: both integer digits and decimal digits increase
ALTER TABLE test_alter CHANGE COLUMN a TYPE DECIMAL(12,2);
-- Note: total digits increase from 10 to 12, scale unchanged
ALTER TABLE test_alter CHANGE COLUMN a TYPE DECIMAL(13,3);
-- Note: total digits increase from 10 to 13, scale increases from 2 to 3
```

**Scenario 2: Only integer digits increase, scale unchanged**

```sql
ALTER TABLE test_alter CHANGE COLUMN a TYPE DECIMAL(15,2);
-- From DECIMAL(10,2) to DECIMAL(15,2)
-- Integer digits: increase from 8 (10-2) to 13 (15-2)
```

**Scenario 3: Both integer digits and scale increase**

```sql
ALTER TABLE test_alter CHANGE COLUMN a TYPE DECIMAL(20,5);
-- From DECIMAL(10,2) to DECIMAL(20,5)
-- Integer digits increase, scale also increases
-- This is the safest conversion
```

Invalid type conversions:

**Error 1: Scale only increases, total digits unchanged**

```sql
-- Error
ALTER TABLE test_alter CHANGE COLUMN a TYPE DECIMAL(10,3);
-- Reason: total digits unchanged, only the scale ratio changes
-- Result: system raises an error or data may be lost
```

**Error 2: Either parameter decreases**

```sql
-- Error: reduce total digits
ALTER TABLE test_alter CHANGE COLUMN a TYPE DECIMAL(8,2);
-- Error: reduce scale
ALTER TABLE test_alter CHANGE COLUMN a TYPE DECIMAL(12,1);
-- Error: both decrease
ALTER TABLE test_alter CHANGE COLUMN a TYPE DECIMAL(8,1);
```

**Error 3: Only scale increases**

```sql
-- Error
ALTER TABLE test_alter CHANGE COLUMN a TYPE DECIMAL(10,3);
-- Problem: total digits stay at 10, but scale increases from 2 to 3
-- Result: integer digits decrease from 8 to 7, may cause data overflow or precision loss
```

## Currently Supported Type Conversions

|          |          |     |        |       |        |                                                                                      |      |         |        |        |
| -------- | -------- | --- | ------ | ----- | ------ | ------------------------------------------------------------------------------------ | ---- | ------- | ------ | ------ |
| from \\ to | smallint | int | bigint | float | double | decimal                                                                              | date | varchar | char   | string |
| tinyint  | ☑️       | ☑️  | ☑️     |       |        |                                                                                      |      |         |        |        |
| smallint | ☑️       | ☑️  | ☑️     |       |        |                                                                                      |      |         |        |        |
| int      |          | ☑️  | ☑️     |       |        |                                                                                      |      |         |        |        |
| bigint   |          |     | ☑️     |       |        |                                                                                      |      |         |        |        |
| float    |          |     |        | ☑️    | ☑️     |                                                                                      |      |         |        |        |
| double   |          |     |        |       | ☑️     |                                                                                      |      |         |        |        |
| decimal  |          |     |        |       |        | DECIMAL type conversion is supported when: P' ≥ P and (P' - S') ≥ (P - S) |      |         |        |        |
| Date     |          |     |        |       |        |                                                                                      | ☑️   |         |        |        |
| Varchar  |          |     |        |       |        |                                                                                      |      | Allowed to become longer |        | ☑️     |
| Char     |          |     |        |       |        |                                                                                      |      |         | Allowed to become longer | ☑️     |
| String   |          |     |        |       |        |                                                                                      |      |         |        |        |
