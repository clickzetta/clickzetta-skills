### CASE Expression

#### 1. Overview

The CASE expression is a conditional selection structure in SQL that allows returning different results based on a series of conditions. There are two forms of CASE expressions: expression-based CASE and condition-based CASE. Both can be used to implement branching logic in queries.

#### 2. Expression-based CASE

Syntax:
```sql
CASE expr {WHEN opt1 THEN res1} [...] [ELSE def] END
```
Features:

- Returns the corresponding result `resN` when the expression `expr` is equal to `optN`.
- If `expr` is not equal to any `optN`, returns the default value `def`. If `def` is not specified, returns `null`.

Parameters:

- `expr`: An expression of any type to be compared.
- `optN`: A conditional expression of the same type as `expr` for comparison.
- `resN`: The result expression returned when the condition matches.
- `def`: The default result expression when no conditions match.

Example:
```sql
SELECT
  CASE col
    WHEN 1 THEN 'a'
    WHEN 2 THEN 'b'
    ELSE 'c'
  END AS result
FROM VALUES(1), (2), (3) AS t(col);
```
Result:
```
result
a
b
c
```
#### 3. CASE Based on Conditions

Syntax:
```sql
CASE {WHEN cond1 THEN res1} [...] [ELSE def] END
```
Functionality:

- When the condition `condN` is `true`, the corresponding result `resN` is returned.
- If none of the conditions are met, the default value `def` is returned. If `def` is not specified, `null` is returned.

Parameters:

- `condN`: Boolean expression used to determine if the branch condition is met.
- `resN`: The result expression returned when the condition is met.
- `def`: The default result expression when no conditions are met.

Example:
```sql
SELECT
  CASE
    WHEN col = 1 THEN 'a'
    WHEN col = 2 THEN 'b'
    ELSE 'c'
  END AS result
FROM VALUES(1), (2), (3), (4) AS t(col);
```
Result:
```
result
a
b
c
null
```
#### 4. Application Scenarios

- Data Transformation: Transform or map data based on different conditions.
- Group Statistics: Classify and summarize data based on certain conditions during group statistics.
- Query Optimization: Filter or select the required data based on conditions during the query process.

#### 5. Precautions

- Ensure that the data types of `resN` and `def` are consistent.
- When using condition-based CASE expressions, ensure that all conditions are mutually exclusive to avoid ambiguity.
- In practical applications, choose the appropriate form of CASE expression based on specific needs.