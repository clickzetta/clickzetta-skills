# ILIKE Operator Usage Guide

The ILIKE operator is a tool used in SQL statements to check whether a string matches a pattern, with the ability to ignore case differences, making string matching more flexible and convenient. Compared to the traditional LIKE operator, the ILIKE operator is more convenient when dealing with inconsistent casing.

## Syntax

The basic syntax of the ILIKE operator is as follows:

```SQL
str [ NOT ] ilike pattern [ escape escape_char ]
str [ NOT ] ilike { ANY | SOME | ALL } ( [ pattern [, ...] ] ) [ escape escape_char ]
```

Here, `str` represents the string expression to match, `pattern` represents the pattern expression to match against, and `escape escape_char` is a single-character string literal used to escape special characters. `ANY`, `SOME`, and `ALL` are used to specify the logical relationship between multiple patterns. When using `ALL`, it means `str` must match all patterns; when using `ANY` or `SOME`, it means `str` only needs to match at least one pattern.

### ILIKE Patterns

ILIKE patterns can contain the following special characters:

- `_`: Matches any single character (similar to `.` in POSIX regular expressions).
- `%`: Matches any number of characters (similar to `.*` in POSIX regular expressions).

## Examples

Assume there is a table named `students` that contains student names and class information, as shown below:

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

Below are query examples using the ILIKE operator:

1.  Find students whose name contains "a" (case-insensitive):

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

2.  Find students whose name starts with "a" or "b" (case-insensitive):

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

3.  Find students whose name contains both "a" and "l" (case-insensitive):

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

## Notes
- When using the ILIKE operator, if the pattern contains special characters, it is recommended to use the `escape` clause to escape these special characters to avoid ambiguity.
