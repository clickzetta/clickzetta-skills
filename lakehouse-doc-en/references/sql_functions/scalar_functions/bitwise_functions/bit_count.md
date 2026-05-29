### BIT_COUNT 

#### Description
The `BIT_COUNT` function is used to count the number of non-zero bits in a given integer expression. This function is very useful for analyzing data bit patterns.

#### Syntax
```
BIT_COUNT(expr)
```
#### Parameters
- `expr`: Can be any integer type expression, including `TINYINT`, `SMALLINT`, `INT`, and `BIGINT`.

#### Return Value
Returns an `INT` type value representing the number of non-zero bits in the input expression.

#### Example 
1. Calculate the number of non-zero bits in a positive integer:
```sql
SELECT BIT_COUNT(100); -- Returns 3, because the binary representation is 1100100
```
2. Calculate the number of non-zero bits in a negative integer:
   Due to different systems representing negative numbers differently (binary two's complement), the calculation results may differ from expectations. In LakeHouse, you can obtain consistent results by explicitly converting to an integer type of a specific length.
```sql
SELECT BIT_COUNT(-100), BIT_COUNT(CAST(-100 AS TINYINT)), BIT_COUNT(CAST(-100 AS SMALLINT)), BIT_COUNT(CAST(-100 AS INT)), BIT_COUNT(CAST(-100 AS BIGINT));
-- Returns 28, 4, 12, 28, 60
```
3. Calculate the number of non-zero bits for different integer types:
```sql
SELECT BIT_COUNT(CAST(123 AS TINYINT)), BIT_COUNT(CAST(123 AS SMALLINT)), BIT_COUNT(CAST(123 AS INT)), BIT_COUNT(CAST(123 AS BIGINT));
-- Returns 4, 4, 4, 4
```
4. For columns containing multiple integers, you can calculate the number of non-zero bits for each one:
   ```sql
   SELECT BIT_COUNT(col1), BIT_COUNT(col2) FROM table_name;
   ```
#### Notes
- When calculating the number of non-zero bits in a negative integer, please note that different systems may produce different results. To ensure consistency, it is recommended to explicitly specify the integer type.
- The `BIT_COUNT` function may calculate positive and negative integers differently, so special attention is needed when performing comparisons or aggregations.