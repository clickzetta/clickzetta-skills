# MAP

`MAP` is a key-value pair data type used to store and retrieve data associated with specific keys. Each key in a MAP uniquely corresponds to one value.

## Syntax

**Type Declaration**

```Plain
MAP<keyType, valueType>
```

**Constructor**

```SQL
MAP(key1, value1, key2, value2, ...)
```

## Parameter Description

- `keyType`: The data type of the key, supporting basic data types (such as `STRING`, `INT`, `BIGINT`, etc.).
- `valueType`: The data type of the value, supporting basic data types and complex types.
- `key1, value1, key2, value2, ...`: One or more key-value pairs, with keys and values alternating; the number of arguments must be even.

## Accessing MAP Elements

Use bracket syntax to access the value corresponding to a key:

```SQL
map_expr[key]
```

If the key does not exist, `NULL` is returned.

## Usage Examples

### 1. Constructing a MAP

```SQL
SELECT MAP('red', 1, 'green', 2);
```

```
+---------------------------+
| MAP('red', 1, 'green', 2) |
+---------------------------+
| {"red":1,"green":2}       |
+---------------------------+
```

Map employee names to departments:

```SQL
SELECT MAP('Alice', 'HR', 'Bob', 'Sales', 'Charlie', 'IT');
```

```
+-----------------------------------------------------+
| MAP('Alice', 'HR', 'Bob', 'Sales', 'Charlie', 'IT') |
+-----------------------------------------------------+
| {"Alice":"HR","Bob":"Sales","Charlie":"IT"}         |
+-----------------------------------------------------+
```

### 2. Accessing MAP Elements

```SQL
SELECT MAP('red', 1, 'green', 2)['red'];
```

```
+----------------------------------+
| MAP('red', 1, 'green', 2)['red'] |
+----------------------------------+
| 1                                |
+----------------------------------+
```

### 3. Using MAP Columns in a Table

Create a table and insert data:

```SQL
CREATE TABLE map_test (id INT, attrs MAP<STRING, INT>);

INSERT INTO map_test VALUES
  (1, MAP('age', 25, 'score', 90)),
  (2, MAP('age', 30, 'score', 85));
```

Access values in the MAP column by key:

```SQL
SELECT id, attrs['age'] AS age FROM map_test;
```

```
+----+-----+
| id | age |
+----+-----+
| 1  | 25  |
| 2  | 30  |
+----+-----+
```

### 4. MAP-Related Functions

**MAP_KEYS** — Returns an array of all keys in the MAP:

```SQL
SELECT MAP_KEYS(MAP('a', 1, 'b', 2));
```

```
+-------------------------------+
| MAP_KEYS(MAP('a', 1, 'b', 2)) |
+-------------------------------+
| ["a","b"]                     |
+-------------------------------+
```

**MAP_VALUES** — Returns an array of all values in the MAP:

```SQL
SELECT MAP_VALUES(MAP('a', 1, 'b', 2));
```

```
+---------------------------------+
| MAP_VALUES(MAP('a', 1, 'b', 2)) |
+---------------------------------+
| [1,2]                           |
+---------------------------------+
```

**CARDINALITY / SIZE** — Returns the number of key-value pairs in the MAP:

```SQL
SELECT CARDINALITY(MAP('a', 1, 'b', 2));
SELECT SIZE(MAP('a', 1, 'b', 2));
```

```
+----------------------------------+
| CARDINALITY(MAP('a', 1, 'b', 2)) |
+----------------------------------+
| 2                                |
+----------------------------------+
```

## Notes

- Key types must be comparable basic data types (such as `STRING`, `INT`, `BIGINT`, `DOUBLE`, etc.); complex types (such as `ARRAY`, `MAP`) are not supported as keys.
- All keys within the same MAP must be of the same type, and all values must also be of the same type.
- The number of arguments to the constructor `MAP(key1, value1, ...)` must be even; otherwise, an error is raised.
- If the same key appears multiple times, the later value overwrites the earlier one.
- Accessing a non-existent key returns `NULL` without raising an error.
- The order of arrays returned by `MAP_KEYS` and `MAP_VALUES` matches the insertion order, but cross-version stability is not guaranteed.
