### COUNT_IF 

####  Description

The COUNT\_IF function is used to count the number of rows where the expression evaluates to true. This function can handle any expression that returns a boolean value and returns a bigint type result. It is important to note that null values do not affect the count result.

#### Syntax Format
```sql
COUNT_IF([DISTINCT] expr1)
```
#### Parameter Description

* `expr1`: The Boolean expression to be evaluated. The return value is any expression that is either true or false.

#### Return Result

* The return value is of bigint type, representing the number of rows where the expression is true.
* If the `DISTINCT` keyword is used, only distinct true values are counted, with duplicate true values counted only once.

#### Usage Example

**Example 1**: **Calculate the number of distinct true values**
```sql
SELECT count_if(col % 2 = 0) FROM VALUES (NULL), (0), (1), (2), (2), (3) AS tab(col);
+-----------------------+
| count_if(col % 2 = 0) |
+-----------------------+
| 3                     |
+-----------------------+
```
^

**Example 2**: Using with DISTINCT
```sql
SELECT count_if(DISTINCT col % 2 = 0) FROM VALUES (NULL), (0), (1), (2), (2), (3) AS tab(col);
+--------------------------------+
| count_if(DISTINCT col % 2 = 0) |
+--------------------------------+
| 1                              |
+--------------------------------+
```
^

**Example 3: Calculate the number of null values**
```sql
SELECT count_if(col IS NULL) FROM VALUES (NULL), (0), (1), (2), (3) AS tab(col);
+-------------------------+
| count_if((col) IS NULL) |
+-------------------------+
| 1                       |
+-------------------------+
```
#### Notes

* The COUNT\_IF function only applies to expressions that return boolean values.
* When using the `DISTINCT` keyword, ensure that the values returned by the expression can distinguish between duplicate true values.
* Null values do not affect the count result.