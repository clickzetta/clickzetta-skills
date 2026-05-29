# ilike Operator Usage Guide

The ilike operator is a tool used in SQL query statements for string matching. It can help you determine whether a string matches a specific pattern without considering case sensitivity. The usage of the ilike operator is similar to the like operator, but it is more flexible and convenient, allowing you to handle string matching issues more easily.

## Syntax

The basic syntax of the ilike operator is as follows:
```SQL
str [ NOT ] ilike pattern
```
In which, `str` is the string expression to be matched, and `pattern` is the pattern expression to be matched. You can also use the `NOT` keyword to reverse the matching condition.
In addition, the ilike operator also supports the use of `ANY`, `SOME`, or `ALL` keywords to match multiple patterns. When using `ALL`, `str` must match all given patterns; when using `ANY` or `SOME`, `str` only needs to match at least one pattern.

### Wildcards in Patterns
The ilike operator's pattern contains the following two special characters to represent wildcard matching:
* `_`: Matches any single character (similar to `.` in POSIX regular expressions).
* `%`: Matches any number of characters (similar to `.*` in POSIX regular expressions).


##  Example
Suppose we have a table named `students` that contains the names and class information of students, as shown below:
```SQL
CREATE TABLE students (
  name STRING,
  class STRING
);

INSERT INTO students (name, class) VALUES
  ('Alice', 'A'),
  ('Bob', 'B'),
  ('Carol', 'A'),
  ('David', 'C');
```
Here are some query examples using the ilike operator and their output results:

1. Query students whose names contain the letter "a" (case-sensitive):
```SQL
SELECT name, class
FROM students
WHERE class like '%a%';

+------+-------+
| name | class |
+------+-------+
```
2. Query students whose names start with "a" or "b" (case-sensitive):
```SQL
SELECT name, class
FROM students
WHERE name like ANY ('a%', 'b%');

+------+-------+
| name | class |
+------+-------+
```
```markdown
3. Query students whose names contain both the letters "a" and "l":
```
```SQL
SELECT name, class
FROM students
WHERE name like ALL ('%a%', '%l%');

+-------+-------+
| name  | class |
+-------+-------+
| Carol | A     |
+-------+-------+
```

^
