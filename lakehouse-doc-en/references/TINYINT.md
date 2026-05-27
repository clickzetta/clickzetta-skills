# TINYINT

`TINYINT` is an 8-bit signed integer data type used to store integer values ranging from -128 to 127. It can efficiently save storage space as it only uses one byte to represent the value.

## Syntax
```
TINYINT
```
## Example

1. Create a table with a `TINYINT` type column:
   ```sql
   CREATE TABLE example_table (
       id TINYINT
   );
   ```
```markdown
2. Insert data into a column of type `TINYINT`:
```
   ```sql
   INSERT INTO example_table (id) VALUES (-100);
   INSERT INTO example_table (id) VALUES (100);
   ```
3. Query data from a `TINYINT` type column:
   ```sql
   SELECT id FROM example_table;
   ```
4. Using `TINYINT` type columns for conditional queries:
   ```sql
   SELECT id FROM example_table WHERE id > -50;
   ```
```markdown
5. Create a table with a `TINYINT` type column (specify the maximum display width):
```
   ```sql
   CREATE TABLE example_table2 (
       age TINYINT
   );
   ```
```markdown
6. Insert data into a `TINYINT` type column (specify maximum display width):
```
   ```sql
   INSERT INTO example_table2 (age) VALUES (25y);
   ```
7.  `TINYINT` constant format:
   ```sql
    SELECT 11y
   ```
## Notes

- The `TINYINT` type is only suitable for storing smaller integer values. For larger values, it is recommended to use the `INT` or `BIGINT` type.
- When using the `TINYINT` type to store negative numbers, the range is -128 to -1. Attempting to insert a negative number outside this range will result in an overflow error.
- When using the `TINYINT` type to store positive numbers, the range is 1 to 127. Attempting to insert a positive number outside this range will result in an overflow error.