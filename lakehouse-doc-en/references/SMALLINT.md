# SMALLINT

16-bit signed integer (SMALLINT) is an integer data type used to store integer values ranging from -32,768 to 32,767. This data type occupies two bytes (16 bits) of storage space and is suitable for storing smaller integer values to save storage space.

## Syntax
```
SMALLINT
```
## Example
1. Create a table with a SMALLINT type column:
   ```sql
   CREATE TABLE example_table (
       id INT,
       name VARCHAR(50),
       smallint_value SMALLINT
   );
   ```
2. Insert SMALLINT type data into the table:
```sql
INSERT INTO example_table (id, name, smallint_value)
VALUES (1, 'John Doe', -32768);
```
3. Query SMALLINT type data in the table:
   ```sql
   SELECT * FROM example_table;
   ```
```markdown
4. Using SMALLINT Type Data for Conditional Filtering:
```
   ```sql
   SELECT * FROM example_table WHERE smallint_value > 0;
   ```
```markdown
5. Perform mathematical operations on SMALLINT type data:
```
   ```sql
   SELECT smallint_value + 1 FROM example_table;
   ```
## Notes
- Please ensure that the inserted data is within the valid range of the SMALLINT type, otherwise it may cause data overflow or truncation.
- When performing mathematical operations, please be aware of implicit conversions between data types to avoid unexpected results.