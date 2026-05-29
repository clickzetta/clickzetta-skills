### BIT_AND Function
```sql
bit_and([distinct] expr)
```
#### Function Description
The BIT_AND function is used to calculate the bitwise AND result of a set of integer values. This function performs a bitwise AND operation on the input expressions and returns the result.

#### Parameter Description
* `expr`: An integer type expression, which can be of type tinyint, smallint, int, or bigint.
* `distinct`: An optional parameter used to specify whether to perform deduplication on the calculation result. If set to distinct, the function will calculate the bitwise AND result of the unique expression values.

#### Return Value
* The return value type is consistent with the input parameter type.
* If it contains null values, null does not participate in the calculation.

#### Usage Example
1. Calculate the bitwise AND result of a set of values:
```sql
SELECT bit_and(col) FROM VALUES (3), (5), (7) AS tab(col);
-- Result: 1
```
2. Calculate the bitwise AND result of the deduplicated value set:
```sql
SELECT bit_and(DISTINCT col) FROM VALUES (3), (3), (5), (7), (null) AS tab(col);
-- Result: 1
```
3. Calculate the bitwise AND result of a column in the actual data table:
```sql
SELECT bit_and(user_id) FROM user_table WHERE status = 'active';
-- Assuming the values of the user_id column are 1024, 2048, 3072, the result is 0 because there is no bit that appears in all values.
```
4. For datasets containing null values, calculate the bitwise AND result:
```sql
SELECT bit_and(score) FROM student_scores WHERE subject = 'Math';
-- Assuming the values of the score column are 75, 85, null, 95, the result is 75 because null is not included in the calculation.
```
#### Notes
* The BIT_AND function performs a bitwise AND operation on the input values, so the result may need further interpretation or conversion to a more understandable format.
* When using the distinct parameter, the function will ignore duplicate values and only calculate non-duplicate values.
* If all input values are null, the result will be null.