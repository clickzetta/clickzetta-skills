### MIN_BY 
```sql
min_by(expr1, expr2)
```
####  Description

The MIN\_BY function is used to find the value of expr1 associated with the minimum value in expr2 from a set of data. This function is very useful when dealing with paired data and can help you quickly find the best match for specific conditions.

#### Parameter Description

* expr1: Any data type. This is the value you want to return based on the minimum value of expr2.
* expr2: Comparable data types, including numeric types (such as tinyint, smallint, int, bigint, float, double, decimal), time types (such as date, timestamp), string types (such as char, varchar, string), and binary types (such as binary).

#### Return Result

* The type of the return result matches the type of expr1.
* If all values in expr2 are null, the return result is also null.

#### Usage Example

1. Example of numeric types:
```sql
SELECT min_by(num1, num2) FROM VALUES
  ((1, 10)),
  ((2, 20)),
  ((3, 5)),
  ((4, 30)) AS tab(num1, num2);
+--------------------+
| min_by(num1, num2) |
+--------------------+
| 3                  |
+--------------------+
```
In this example, we can see that the minimum value of num2 is 5, and the value of num1 associated with it is 3.

2. Example of time type:
```sql
SELECT min_by(date1, date2) FROM VALUES
  (('2022-01-01', '2023-01-01')),
  (('2022-02-01', '2022-12-31')),
  (('2022-03-01', '2022-01-01')) AS tab(date1, date2);
+----------------------+
| min_by(date1, date2) |
+----------------------+
| 2022-03-01           |
+----------------------+
```
In this example, we can see that the minimum value of date2 is '2022-01-01', and the value of the associated date1 is also '2022-01-01'.

3. Example of string type:
```sql
SELECT min_by(str1, str2) FROM VALUES
  (('apple', 'A')),
  (('banana', 'B')),
  (('cherry', 'C')) AS tab(str1, str2);
+--------------------+
| min_by(str1, str2) |
+--------------------+
| apple              |
+--------------------+
```
In this example, we can see that the minimum value of str2 is 'A', and the value of str1 associated with it is 'apple'.

#### Notes

* Please ensure that the data types of expr1 and expr2 are compatible, otherwise the function may fail to execute.
* If all values in expr2 are null, the function will return null.
* The MIN_BY function is suitable for comparing and filtering paired data, but not for individual data items.