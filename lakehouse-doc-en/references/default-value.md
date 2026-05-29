## Default Values

## Syntax
```SQL
CREATE TABLE [ IF NOT EXISTS ] table_name
(
    column_definition DEFAULT default\_expression, [column_definition,...]
)
[ PARTITIONED BY (column_name column_type | column_name ) ];
```
* **DEFAULT default\_expression**: Defines a default value for a newly added column. If the value of this column is not specified in INSERT, UPDATE, or MERGE operations, this default value will be used automatically. For data rows that existed before the column was added, the column will be filled with null. Supports non-deterministic functions such as (current\_date\random\current\_timestamp\context functions) and constant values.

### Difference Between Generated Columns and Default Values

1. **Partition Column Support**:

   1. **Default Values**: Currently, setting default values for partition columns is not supported.
   2. **Generated Columns**: Supports generating values for partition columns.

2. **Function Support**:

   1. **Default Values**: Supports the use of non-deterministic functions, such as `current_timestamp()`.
   2. **Generated Columns**: Does not support non-deterministic functions, only deterministic scalar functions can be used.

3. **Value Specification in Insert Operations**:

   1. **Default Values**: When inserting data, a static value can be specified for the column. If not specified, the default value is used.
   2. **Generated Columns**: When inserting data, values cannot be specified for generated columns; their values are entirely determined by the generation expression.

4. **Source of Column Values**:

   1. **Default Values**: Does not support column values derived from the transformation of other columns.
   2. **Generated Columns**: Supports column values derived from the transformation of other columns, i.e., values can be calculated based on other columns.

5. **Handling of Existing Data Rows**:

   1. **Default Values**: When adding a column with a default value to an existing table, the column in existing data rows will be filled with null.
   2. **Generated Columns**: For existing data rows, the value of the generated column will be converted according to the generation expression and display the converted data.

### Usage Restrictions

* Setting default values for partition columns is not supported.
* Supports batch interface writing, including batch import in Studio data integration. Default values will not take effect when writing through real-time interfaces, as all columns must be specified when calling real-time interfaces.
* Does not support functions similar to generated columns that can reference other columns.

### Inserting Data
```SQL
CREATE TABLE t_default
(
    id   int,
    col1 string DEFAULT current_timestamp (),
    col2 string DEFAULT '1',
    col3 int    DEFAULT 1,
    clo4 json   DEFAULT '1',
    col5 DOUBLE DEFAULT random(),
    col6 date   DEFAULT current_date()
);
INSERT INTO t_default (id) VALUES (1);
```

# Specify Default Values When Adding Fields

## Syntax
```SQL
-- Add column
ALTER TABLE table_name ADD COLUMN
      column1_name_identifier data_type [column_properties]
      [FIRST | AFTER column1_name_identifier]  ,....

column_properties:==
    DEFAULT default_expression |
    COMMENT column_comment 
```
* **DEFAULT default\_expression**: Defines a default value for the newly added column. If the value of this column is not specified in INSERT, UPDATE, or MERGE operations, this default value will be automatically used. For data rows that existed before the column was added, the column will be filled with null.

## Usage Restrictions

* Adding a default value to an existing column is not supported

## Examples

### Add a column and specify a default value
```SQL
ALTER TABLE my_table ADD COLUMN
    new_col INT DEFAULT 0 AFTER existing_col;
```
In this example, `new_col` will be added after `existing_col`, and `new_col` for all existing data rows will be set to the default value null.