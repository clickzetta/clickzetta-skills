## ELEMENT_AT 

##  Description

The `ELEMENT_AT` function is used to extract elements from an array or a map based on a specified index or key. It supports two usages: extracting elements from an array by index and extracting values from a map by key.

## Syntax

### Extracting Elements from an Array

```sql
ELEMENT_AT(arrayExpr, index)
```

### Extracting Values from a Map

```sql
ELEMENT_AT(mapExpr, key)
```

## Parameters

- `arrayExpr`: An array expression representing the array from which elements need to be extracted.
- `index`: An integer expression representing the position of the element in the array. Indexing starts from 1, and negative numbers are supported (counting from the end of the array).
- `mapExpr`: A map expression representing the map from which values need to be extracted.
- `key`: An expression matching the key type of the map, specifying the key for which the value needs to be extracted.

## Return Values

- **Extracting Elements from an Array**:
  - The return type matches the type of the array elements.
  - If `abs(index)` exceeds the array length, an error will be raised (unless the `TRY_ELEMENT_AT` function is used).
  - If `index` is negative, it counts backward from the end of the array.
- **Extracting Values from a Map**:
  - If the key exists in the map, the corresponding value is returned; otherwise, `NULL` is returned.

## Examples

Example 1: Extracting an element from an array

```sql
SELECT ELEMENT_AT(ARRAY[1, 2, 3], 2);
+--------------------------+
| ELEMENT_AT([1, 2, 3], 2) |
+--------------------------+
| 2                        |
+--------------------------+
```

Example 2: Using a negative index to extract an element from an array

```sql
SELECT ELEMENT_AT(ARRAY[1, 2, 3], -1);
+---------------------------+
| ELEMENT_AT([1, 2, 3], -1) |
+---------------------------+
| 3                         |
+---------------------------+
```