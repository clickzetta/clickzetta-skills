### FLATTEN 

### Description

The `FLATTEN` function is used to convert a two-dimensional array (i.e., an array of arrays) into a one-dimensional array. This function can handle complex structures containing multiple sub-arrays and flatten their elements into a continuous sequence.

### Syntax
```sql
flatten(array<array>)
```
### Parameter Description

- `array<array>`: A two-dimensional array containing multiple sub-arrays. Each sub-array can contain elements of any type.

### Return Value

Returns a one-dimensional array containing all the elements of the sub-arrays.

### Usage Example

**Example 1: Basic Usage**

Suppose we have a two-dimensional array and we want to flatten it into a one-dimensional array.
```sql
SELECT FLATTEN(
  ARRAY(
    ARRAY(1, 2),
    ARRAY(3, 4)
  )
);
```
Return results:
```
[1, 2, 3, 4]
```
**Example 2: Nested Arrays**

If our two-dimensional array contains nested deeper level arrays, the `FLATTEN` function can also handle it.
```sql
SELECT FLATTEN(
  ARRAY(
    ARRAY(ARRAY(1), ARRAY(2, 3)),
    ARRAY(ARRAY(4), ARRAY(5, 6))
  )
);
```
Return results:
```
[[1],[2,3],[4],[5,6]]
```