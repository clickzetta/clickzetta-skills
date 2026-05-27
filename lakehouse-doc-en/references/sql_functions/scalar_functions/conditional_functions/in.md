### IN 

#### Description
The IN operator is used to check whether a specified value (elem) is in a given list of expressions (expr1, expr2, ...) or query results. If elem is equal to any value in the list or any value in the query results, it returns true; otherwise, it returns false.

#### Parameter Description
- `elem`: An expression that returns a comparable type.
- `exprN`: Expressions of the same type as elem, can be multiple, separated by commas.
- `query`: A query statement that returns the same type as elem. The current version only supports queries that return a single column result.

#### Return Type
The return type is a boolean.

#### Usage Example

1. Check if the number 1 is in the given list (1, 2, 3):
Sure, here is the translated content:

```sql
2. Check if the string "apple" is in the fruit list:
```sql
SELECT 'apple' IN ('banana', 'apple', 'orange'); -- The result is true
```
```markdown
3. Get whether a student's score is passing through a query (assuming a score of 60 or above is passing):
```
```sql
SELECT student_id IN (SELECT student_id FROM scores WHERE score >= 60); -- The result depends on the students' score data
```
#### Notes
- Please ensure that the types returned by elem and exprN or query match, otherwise it may lead to comparison failure.
- When using the IN operator with subqueries, please ensure that the subquery returns only one column of results.