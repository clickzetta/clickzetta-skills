### MAX\_BY 
```sql
max_by(expr1, expr2)
```
#### Description

The MAX\_BY function is used to return the value of the expr1 expression associated with the maximum value of the expr2 expression from a set of data. This function is particularly useful when dealing with paired data, helping you quickly find the data item corresponding to the maximum value.

#### Parameter Description

* expr1: An expression of any data type.
* expr2: A comparable data type expression, including numeric types (such as tinyint, smallint, int, bigint, float, double, decimal), time types (such as date, timestamp), and string types (such as char, varchar, string, binary).

#### Return Result

Returns the value of the expr1 expression associated with the maximum value of the expr2 expression. The result type matches the type of expr1. If all values in expr2 are null, null is returned.

#### Usage Example

1. Find the string associated with the maximum integer value from a set of string and integer data:
   ```sql
   SELECT max_by(str, num) FROM VALUES ('apple', 1), ('banana', 3), ('cherry', 2) AS tab(str, num);
   +------------------+
   | max_by(str, num) |
   +------------------+
   | banana           |
   +------------------+
   ```
2. Find the string associated with the latest date from a set of dates and string data:
   ```sql
   SELECT max_by(str, date) FROM VALUES ('event1', '2022-01-01'), ('event2', '2022-02-01'), ('event3', '2022-01-15') AS tab(str, date);
   +---------------------+
   | max_by(str, `date`) |
   +---------------------+
   | event2              |
   +---------------------+
   ```
3. Find the employee name associated with the highest salary from a set of employee names and salary data:
   ```sql
   SELECT max_by(name, salary) FROM VALUES ('Alice', 5000), ('Bob', 6000), ('Charlie', 4500) AS tab(name, salary);
   +----------------------+
   | max_by(name, salary) |
   +----------------------+
   | Bob                  |
   +----------------------+
   ```