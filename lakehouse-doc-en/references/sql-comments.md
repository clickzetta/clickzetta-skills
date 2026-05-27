# SQL Comments

SQL statements support two types of comments:

## Single-line Comments

Starting with `--`, everything until the end of the line is ignored.

```sql
-- This is a single-line comment
SELECT 1; -- Inline comment
```

## Multi-line Comments

Starting with `/*` and ending with `*/`, everything in between is ignored. Multi-line comments support nesting.

```sql
/* This is a
   multi-line comment */
SELECT /* Inline comment */ 1 + 2;

/* Nested comment /* inner */ outer */
SELECT 1;
```

## Notes

- Comments can appear anywhere in a SQL statement.
- Single-line comments start with `--` and end at the line break; no closing marker is needed.
- Multi-line comments must have matching `/*` and `*/`.
