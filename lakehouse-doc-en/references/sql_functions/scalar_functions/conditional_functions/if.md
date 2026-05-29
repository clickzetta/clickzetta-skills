### IF 

####  Description

The IF function is a conditional judgment function that returns expr1 or expr2 based on the provided conditional expression (cond). When the result of the conditional expression is true, the IF function returns the value of expr1; when the result of the conditional expression is false, it returns the value of expr2.

#### Parameter Description

* cond (conditional expression): An expression that returns a boolean value (true or false).
* expr1 (expression 1): When cond is true, the IF function returns the value of this expression.
* expr2 (expression 2): When cond is false, the IF function returns the value of this expression.

#### Return Result

The return type of the IF function is the same as the type of expr1 and expr2.

####  Example

1. Example 1: Compare values and return results
```sql
SELECT IF(a > 10, 'Greater than 10', 'Less than or equal to 10') AS result FROM VALUES(5), (15), (10) AS t(a);

 result    
+-----------+
 Less than or equal to 10 
 Greater than 10     
 Less than or equal to 10 

```
```markdown
2. Example 2: Determine if a string is empty
```
```sql
SELECT IF(name = '', 'Empty String', 'Non-Empty String') AS result FROM VALUES('Zhang San'), (''), ('Li Si') AS t(name);
result
+-----------+
Non-Empty String
Empty String
Non-Empty String

```


3. Example 4: Determine Grade Based on Score
```sql
SELECT IF(score >= 90, 'Excellent', IF(score >= 60, 'Pass', 'Fail')) AS grade FROM VALUES(85), (95), (55) AS t(score);
grade
+-----------+
Pass
Excellent
Fail

```