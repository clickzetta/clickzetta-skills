# ilike Operator Usage Guide

The ilike operator is a tool used in SQL statements to determine string matching patterns. It can ignore case differences, making string matching more flexible and convenient. Compared to the traditional like operator, the ilike operator is more efficient in handling case inconsistencies.

## Syntax

The basic syntax of the ilike operator is as follows:
```SQL
str [ NOT ] ilike pattern [ escape escape_char ]
str [ NOT ] ilike { ANY | SOME | ALL } ( [ pattern [, ...] ] ) [ escape escape_char ]
```
In this context, `str` represents the string expression to be matched, `pattern` represents the pattern expression to be matched, and `escape escape_char` is a single-character string literal used to escape special characters. `ANY`, `SOME`, and `ALL` are used to specify the logical relationship between multiple patterns. When using `ALL`, it means that `str` must match all patterns; whereas using `ANY` or `SOME` means that `str` only needs to match at least one pattern.

### ilike Pattern

The ilike pattern can contain the following special characters:

- `_`: Matches any single character (similar to `.` in POSIX regular expressions).
- `%`: Matches any number of characters (similar to `.*` in POSIX regular expressions).

## Usage Example

Suppose we have a table named students that contains the names and class information of students, as shown below:
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
Here are some query examples using the ilike operator:

1. Query students whose names contain "a" (case insensitive):
```SQL
SELECT name, class
FROM students
WHERE name ILIKE '%a%';

+-------+-------+
| name  | class |
+-------+-------+
| Alice | A     |
| Carol | A     |
| David | C     |
+-------+-------+
```
```markdown
2. Query students whose names start with "a" or "b" (case insensitive):
```
```SQL
SELECT name, class
FROM students
WHERE name ILIKE ANY ('a%', 'b%');

+-------+-------+
| name  | class |
+-------+-------+
| Alice | A     |
| Bob   | B     |
+-------+-------+
```
```markdown
3. Query students whose names contain both "a" and "l" (case insensitive):
```
```SQL
SELECT name, class
FROM students
WHERE name ILIKE ALL ('%a%', '%l%');

+-------+-------+
| name  | class |
+-------+-------+
| Alice | A     |
| Carol | A     |
+-------+-------+
```
## Precautions
- When using the ilike operator, if the pattern contains special characters, it is recommended to use the `escape` clause to escape these special characters to avoid ambiguity.