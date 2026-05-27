## JOIN

Join refers to the operation of using the JOIN clause in an SQL statement to merge data from two or more tables based on certain conditions. It allows you to retrieve related information from different data sources and can perform some transformations or processing on the data before or after merging. The syntax of Join is as follows:

```SQL
left_table_reference { 
[ join_type ] JOIN right_table_reference join_criteria |
 NATURAL  JOIN right_table_reference | 
 CROSS JOIN right_table_reference } 
 --join type
join_type::= 
     { [ INNER ] | LEFT [ OUTER ] | [ LEFT ] SEMI | RIGHT [ OUTER ] | FULL [ OUTER ] | [ LEFT ] ANTI | CROSS } 
--join criteria
join_criteria::=
     { ON boolean_expression | USING ( column_name [, ...] ) }
```

`left_table_reference` refers to the left table of the join, `right_table_reference` refers to the right table of the join, `join_type` refers to the type of join, and `join_criteria` refers to the condition of the join.

## Types of Join

The types of join are as follows:

* **INNER JOIN**: Returns the rows from both tables that satisfy the join condition, which is the intersection of the two tables. This is the default join type.
* **LEFT \[OUTER] JOIN**: Returns all rows from the left table and the rows from the right table that satisfy the join condition. If there are no matching rows in the right table, NULL is used to fill in. This is also called a left outer join.
* **RIGHT \[OUTER] JOIN**: Returns all rows from the right table and the rows from the left table that satisfy the join condition. If there are no matching rows in the left table, NULL is used to fill in. This is also called a right outer join.
* **FULL \[OUTER] JOIN**: Returns all rows from both tables. If there are no matching rows in one of the tables, NULL is used to fill in. This is also called a full outer join.
* \[**LEFT] SEMI JOIN**: Returns the rows from the left table that satisfy the join condition, without returning the rows from the right table. This is also called a left semi join.
* \[**LEFT] ANTI JOIN**: Returns the rows from the left table that do not satisfy the join condition, without returning the rows from the right table. This is also called a left anti join.
* **CROSS JOIN**: Returns the Cartesian product of the two tables, which is all possible combinations of the two tables.
* **NATURAL JOIN**: Performs an implicit equi-join based on columns with the same name in both tables, without needing to specify the join condition.

## Join Conditions

The join conditions are as follows:

* **ON boolean\_expression**: Specifies an expression that returns a boolean value to determine if the rows from the two tables match. If the result is true, they are considered a match. The join condition does not support subqueries.
* **USING (column\_name** \[, …]): Specifies one or more column names to perform an equi-join. These column names must exist in both tables. The join condition does not support subqueries.

## Example

Below are some examples of SQL statements using join and their output results. Suppose we have the following two tables:

```SQL
create table students(name string,class string);
INSERT INTO students (name, class) VALUES
('Alice', 'A'),
('Bob', 'B'),
('Carol', 'A'),
('David', 'C');
create table scores(name string,score int);
INSERT INTO scores (name, score) VALUES
('Alice', 90),
('Bob', 80),
('Carol', 85),
('David', 95);
```

### INNER JOIN

* Query: Use INNER JOIN to merge the data of two tables, match by name, and display each student's name, class, and grade.

```SQL
SELECT students.name, students.class, scores.score
FROM students
INNER JOIN scores
ON students.name = scores.name;

+-------+-------+-------+
| name  | class | score |
+-------+-------+-------+
| Carol | A     | 85    |
| Bob   | B     | 80    |
| David | C     | 95    |
| Alice | A     | 90    |
+-------+-------+-------+
```

### LEFT \[OUTER] JOIN

* Query: Use LEFT JOIN to merge the data of two tables, match by name, display each student's name, class, and grade. If a student does not have a grade, fill it with NULL.

```SQL
SELECT students.name, students.class, scores.score
FROM students
LEFT JOIN scores
ON students.name = scores.name;
+-------+-------+-------+
| name  | class | score |
+-------+-------+-------+
| Carol | A     | 85    |
| Bob   | B     | 80    |
| David | C     | 95    |
| Alice | A     | 90    |
+-------+-------+-------+
```

### RIGHT \[OUTER] JOIN

* Query: Use RIGHT JOIN to merge data from two tables, matching by name, displaying each student's name, class, and grade. If a student does not have a class, fill with NULL.

```SQL
SELECT students.name, students.class, scores.score
FROM students
RIGHT JOIN scores
ON students.name = scores.name;

+-------+-------+-------+
| name  | class | score |
+-------+-------+-------+
| Carol | A     | 85    |
| Bob   | B     | 80    |
| David | C     | 95    |
| Alice | A     | 90    |
+-------+-------+-------+
```

### FULL \[OUTER] JOIN

* Query: Use FULL JOIN to merge the data of two tables, matching by name, and display each student's name, class, and grade. If a student does not have a class or grade, fill it with NULL.

```SQL
SELECT students.name, students.class, scores.score
FROM students
FULL JOIN scores
ON students.name = scores.name;


+-------+-------+-------+
| name  | class | score |
+-------+-------+-------+
| Carol | A     | 85    |
| Bob   | B     | 80    |
| David | C     | 95    |
| Alice | A     | 90    |
+-------+-------+-------+
```

### \[LEFT] SEMI JOIN

* Query: Use SEMI JOIN to merge data from two tables, matching by name, and only display the names and classes of students who have grades.

```SQL
SELECT students.name, students.class
FROM students
SEMI JOIN scores
ON students.name = scores.name;
+-------+-------+
| name  | class |
+-------+-------+
| Carol | A     |
| Bob   | B     |
| David | C     |
| Alice | A     |
+-------+-------+
```

### \[LEFT] ANTI JOIN

* Query: Use ANTI JOIN to merge data from two tables, match by name, and only display the names and classes of students who do not have grades.

```SQL
SELECT students.name, students.class
FROM students
ANTI JOIN scores
ON students.name = scores.name;

+------+-------+
| name | class |
+------+-------+
```

### CROSS JOIN

* Query: Use CROSS JOIN to combine the data of two tables, displaying all possible combinations of each student's name, class, and grades.

```SQL
SELECT students.name, students.class, scores.score
FROM students
CROSS JOIN scores;

+-------+-------+-------+
| name  | class | score |
+-------+-------+-------+
| Alice | A     | 90    |
| Bob   | B     | 90    |
| Carol | A     | 90    |
| David | C     | 90    |
| Alice | A     | 80    |
| Bob   | B     | 80    |
| Carol | A     | 80    |
| David | C     | 80    |
| Alice | A     | 85    |
| Bob   | B     | 85    |
| Carol | A     | 85    |
| David | C     | 85    |
| Alice | A     | 95    |
| Bob   | B     | 95    |
| Carol | A     | 95    |
| David | C     | 95    |
+-------+-------+-------+
```

^
