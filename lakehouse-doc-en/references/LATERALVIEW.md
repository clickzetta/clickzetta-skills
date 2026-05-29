## LATERAL VIEW

The `LATERAL VIEW` clause is used in conjunction with generator functions (such as `EXPLODE`, `POSEXPLODE`, etc.) to expand array or MAP type columns into multiple rows, generating a virtual table that is joined with the original table.

## Syntax

```Plain
SELECT ...
FROM table_reference
LATERAL VIEW [OUTER] generator_function [table_alias] AS column_alias [, ...]
[LATERAL VIEW ...]
```

## Parameter Description

- `OUTER`: Optional. When the input array or MAP is empty or NULL, the original row is preserved and the expanded columns are filled with NULL (similar to LEFT JOIN semantics). Without `OUTER`, empty array/NULL rows are filtered out.
- `generator_function`: The generator function, commonly `EXPLODE` (expands arrays or MAPs) and `POSEXPLODE` (expands arrays with position index).
- `table_alias`: Optional. Specifies an alias for the virtual table.
- `column_alias`: Specifies column aliases for the output of the generator function. The number of aliases must match the number of output columns of the generator function.

## Examples

### Prepare Test Data

```SQL
CREATE TABLE emp_skills (
    id     INT,
    name   STRING,
    skills ARRAY<STRING>
);

INSERT INTO emp_skills (id, name, skills) VALUES
(1, 'John Doe',    ARRAY('Java', 'Python', 'SQL')),
(2, 'Jane Smith',  ARRAY('C++', 'Hadoop', 'SQL')),
(3, 'Bob Johnson', ARRAY('Python', 'Docker')),
(4, 'Alice Wang',  NULL);
```

### Example 1: EXPLODE -- Expand an Array into Multiple Rows

Split each employee's skills array into individual rows.

```SQL
SELECT e.id, e.name, s.skill
FROM emp_skills e
LATERAL VIEW EXPLODE(e.skills) s AS skill
ORDER BY e.id, s.skill;
```

Result:

```
+----+-------------+--------+
| id | name        | skill  |
+----+-------------+--------+
|  1 | John Doe    | Java   |
|  1 | John Doe    | Python |
|  1 | John Doe    | SQL    |
|  2 | Jane Smith  | C++    |
|  2 | Jane Smith  | Hadoop |
|  2 | Jane Smith  | SQL    |
|  3 | Bob Johnson | Docker |
|  3 | Bob Johnson | Python |
+----+-------------+--------+
```

Note: The row with `id=4` (Alice Wang, skills is NULL) is filtered out.

### Example 2: LATERAL VIEW OUTER -- Preserve Empty Array/NULL Rows

```SQL
SELECT e.id, e.name, s.skill
FROM emp_skills e
LATERAL VIEW OUTER EXPLODE(e.skills) s AS skill
ORDER BY e.id, s.skill;
```

Result:

```
+----+-------------+--------+
| id | name        | skill  |
+----+-------------+--------+
|  1 | John Doe    | Java   |
|  1 | John Doe    | Python |
|  1 | John Doe    | SQL    |
|  2 | Jane Smith  | C++    |
|  2 | Jane Smith  | Hadoop |
|  2 | Jane Smith  | SQL    |
|  3 | Bob Johnson | Docker |
|  3 | Bob Johnson | Python |
|  4 | Alice Wang  | NULL   |
+----+-------------+--------+
```

With `OUTER`, the `id=4` row is preserved, with the `skill` column set to NULL.

### Example 3: POSEXPLODE -- Expand Array with Position Index

`POSEXPLODE` expands the array and returns the position index (starting from 0) of each element.

```SQL
SELECT e.id, e.name, ps.pos, ps.skill
FROM emp_skills e
LATERAL VIEW POSEXPLODE(e.skills) ps AS pos, skill
ORDER BY e.id, ps.pos;
```

Result:

```
+----+-------------+-----+--------+
| id | name        | pos | skill  |
+----+-------------+-----+--------+
|  1 | John Doe    |   0 | Java   |
|  1 | John Doe    |   1 | Python |
|  1 | John Doe    |   2 | SQL    |
|  2 | Jane Smith  |   0 | C++    |
|  2 | Jane Smith  |   1 | Hadoop |
|  2 | Jane Smith  |   2 | SQL    |
|  3 | Bob Johnson |   0 | Python |
|  3 | Bob Johnson |   1 | Docker |
+----+-------------+-----+--------+
```

### Example 4: Multiple LATERAL VIEW -- Expand Multiple Array Columns

You can chain multiple `LATERAL VIEW` clauses in a single query to expand different array columns.

```SQL
-- Assume the table has both skills and languages as array columns
SELECT e.id, e.name, s.skill, l.lang
FROM emp_skills e
LATERAL VIEW EXPLODE(e.skills) s AS skill
LATERAL VIEW EXPLODE(ARRAY('Chinese', 'English')) l AS lang
ORDER BY e.id, s.skill, l.lang
LIMIT 6;
```

### Example 5: Expand MAP Type

`EXPLODE` also supports MAP types, generating two columns: `key` and `value`.

```SQL
-- Assume the scores column is of type MAP<STRING, INT>
SELECT id, name, kv.subject, kv.score
FROM student_scores
LATERAL VIEW EXPLODE(scores) kv AS subject, score
ORDER BY id, subject;
```

## Notes

- `LATERAL VIEW` must immediately follow the table reference in the `FROM` clause and cannot be placed after `WHERE`.
- Without `OUTER`, rows with empty arrays (`ARRAY()`) or NULL are filtered out, behaving like an INNER JOIN.
- `POSEXPLODE` outputs two columns (position index and value), so two column aliases must be provided after `AS`.
- Multiple `LATERAL VIEW` clauses produce a Cartesian product relationship, meaning the number of result rows multiplies when expanding multiple arrays. Use with caution regarding data volume.
