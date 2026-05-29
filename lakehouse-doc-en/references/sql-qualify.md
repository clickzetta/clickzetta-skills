# QUALIFY


## Feature Introduction


The QUALIFY clause is used to filter the results of window functions in a SELECT statement. QUALIFY acts on window functions just like HAVING acts on aggregate functions and GROUP BY clauses. In the query execution order, QUALIFY is evaluated after window functions are calculated.


QUALIFY simplifies queries that need to filter window function results, eliminating the need for nested subqueries. This greatly improves the readability and conciseness of SQL statements.


### QUALIFY Execution Order


The typical execution order of clauses in a SELECT statement is as follows:


1. FROM
2. WHERE
3. GROUP BY
4. HAVING
5. Window Functions
6. **QUALIFY** ⭐
7. DISTINCT
8. ORDER BY
9. LIMIT




## Syntax


```sql
SELECT <column_list>, <window_function> AS <alias>
FROM <data_source>
[WHERE ...]
[GROUP BY ...]
[HAVING ...]
QUALIFY <predicate>
[ORDER BY ...]
[LIMIT ...]
```


### Parameter Description


* **column_list**: List of columns specified in the SELECT clause
* **window_function**: Window function expression that must be given an alias for reference in QUALIFY
* **alias**: Alias of the window function, used in the QUALIFY predicate
* **data_source**: Data source, typically a table
* **predicate**: Predicate expression used for filtering, using the alias of the window function




## Usage Instructions


### Prerequisites


The QUALIFY clause requires that a window function be specified in the SELECT statement and given an alias


### Key Characteristics


* When defining a window function in the SELECT clause, **an alias must be provided**
* Use the alias in the QUALIFY clause for condition evaluation
* Supports all standard window functions
* Supports various comparison operators (=, !=, <, >, <=, >=, IN, etc.)
* QUALIFY is a reserved word




## Usage Examples


### Example 1: Get the First Record of Each Group


**Scenario Description**: Use ROW_NUMBER to get records with row number 1 in each group


**Test Table**:


```sql
CREATE TABLE qualify_test (
    i INT,
    p CHAR(1),
    o INT
);

INSERT INTO qualify_test VALUES 
(1, 'A', 1),
(2, 'A', 2),
(3, 'B', 1),
(4, 'B', 2);
```


**SQL Statement**:


```sql
SELECT i, p, o, ROW_NUMBER() OVER (PARTITION BY p ORDER BY o) as flag
FROM qualify_test 
QUALIFY flag = 1;
```


**Result**:


```
i | p | o | flag
--|---|---|-----
1 | A | 1 |  1
3 | B | 1 |  1
```




### Example 2: Get Records with Row Number Greater Than 1


**SQL Statement**:


```sql
SELECT i, p, o, ROW_NUMBER() OVER (PARTITION BY p ORDER BY o) as row_num
FROM qualify_test 
QUALIFY row_num > 1;
```


**Result**:


```
i | p | o | row_num
--|---|---|--------
2 | A | 2 |   2
4 | B | 2 |   2
```




### Example 3: Use RANK Function to Get Top 2 Rankings


**SQL Statement**:


```sql
SELECT i, p, o, RANK() OVER (ORDER BY o DESC) as rnk
FROM qualify_test 
QUALIFY rnk <= 2;
```


**Result**:


```
i | p | o | rnk
--|---|---|----
4 | B | 2 |  1
2 | A | 2 |  1
```




### Example 4: Use DENSE_RANK Function


**SQL Statement**:


```sql
SELECT i, p, o, DENSE_RANK() OVER (PARTITION BY p ORDER BY o) as dense_rnk
FROM qualify_test 
QUALIFY dense_rnk = 1;
```


**Result**:


```
i | p | o | dense_rnk
--|---|---|----------
1 | A | 1 |    1
3 | B | 1 |    1
```




### Example 5: Use Aggregate Window Functions


**Scenario Description**: Get all rows where the group sum is greater than or equal to 3


**SQL Statement**:


```sql
SELECT i, p, o, SUM(o) OVER (PARTITION BY p) as total
FROM qualify_test 
QUALIFY total >= 3;
```


**Result**:


```
i | p | o | total
--|---|---|-----
1 | A | 1 |  3
2 | A | 2 |  3
3 | B | 1 |  3
4 | B | 2 |  3
```




## Comparison with Traditional Subqueries


### Traditional Method (Using Subqueries)


```sql
SELECT * FROM (
    SELECT i, p, o, ROW_NUMBER() OVER (PARTITION BY p ORDER BY o) as row_num 
    FROM qualify_test
) t
WHERE row_num = 1;
```


### QUALIFY Method (Recommended)


```sql
SELECT i, p, o, ROW_NUMBER() OVER (PARTITION BY p ORDER BY o) as row_num
FROM qualify_test 
QUALIFY row_num = 1;
```


### Comparison of Advantages


| Aspect | Traditional Method | QUALIFY Method |
| -------- | -------- | ---------- |
| Code Complexity | High (Nested Subqueries) | Low (Flat)      |
| Readability | Average | Excellent ✓ |
| Lines of Code | 4-5 Lines | 3 Lines |
| Performance | Equivalent | Equivalent |
| Maintenance Cost | High | Low ✓ |




## Important Notes


### Rules That Must Be Followed


* Window functions must be defined in the SELECT clause and given an alias
* Use the alias of the window function in QUALIFY for condition evaluation
* QUALIFY must reference at least one window function