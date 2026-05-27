### ANY_VALUE Function
```
any_value(expr) [FILTER (WHERE condition)]
```
#### Description
The `ANY_VALUE` function randomly selects and returns a value from a set of data. When processing multiple data rows, this function can simplify queries and improve efficiency.

#### Parameter Description
* `expr`: An expression of any numeric type (such as `TINYINT`, `SMALLINT`, `INT`, `BIGINT`, `FLOAT`, `DOUBLE`, `DECIMAL`) or string type (such as `STRING`, `CHAR`, `VARCHAR`) or complex type.

#### Return Result
* Returns a value of the same type as the input parameter `expr`.
* If the input parameter contains `NULL` values, `NULL` values will also be included in the calculation.

#### Usage Examples
1. Randomly select a value from a set of integers:
```sql
SELECT any_value(col) FROM VALUES (1), (2), (3), (4), (NULL) AS tab(col);
+------------------+
| any_value(`col`) |
+------------------+
| 1                |
+------------------+
```

2. Randomly select a value from a set of strings:
```sql
SELECT any_value(col) FROM VALUES ('apple'), ('banana'), ('cherry') AS tab(col);
+------------------+
| any_value(`col`) |
+------------------+
| apple            |
+------------------+
```

3. Use the `ANY_VALUE` function in complex queries:
```sql
SELECT any_value(city) FROM customers WHERE country = 'China';
+--------------------+
| any_value(`city`)  |
+--------------------+
| Beijing            |
+--------------------+
```

4. Randomly select a value from data containing `NULL` values:
```sql
SELECT any_value(col) FROM VALUES (CAST(NULL AS INT)), (5), (6) AS tab(col);
+------------------+
| any_value(`col`) |
+------------------+
| NULL             |
+------------------+
```

> Note: `ANY_VALUE` is a non-deterministic function. The return value may be `NULL`, `5`, or `6` — any of these. The result may differ each time it is executed.

5. Use the FILTER clause to conditionally select a value:
```sql
SELECT any_value(col) FILTER (WHERE col > 2) FROM VALUES (1), (2), (3), (4) AS tab(col);
+-------------------------------------------+
| any_value(`col`) FILTER (WHERE (col > 2)) |
+-------------------------------------------+
| 3                                         |
+-------------------------------------------+
```
