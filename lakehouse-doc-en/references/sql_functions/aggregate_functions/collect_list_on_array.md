### Collect List on Array Function: COLLECT_LIST_ON_ARRAY

```
collect_list_on_array([DISTINCT] array [, limit])
```

#### Description

This function collects elements from the input arrays (`ARRAY`) into a new array and returns that new array. If the `DISTINCT` parameter is specified, it deduplicates the **input array rows** (i.e., identical arrays are collected only once), rather than deduplicating elements within the arrays.

#### Parameters

* `array`: Input array (`ARRAY`) type data.
* `limit`: Optional parameter, integer type, specifying the maximum number of elements to collect. If not specified, all elements are collected.

#### Return Results

* Returns an array (`ARRAY`) type, with element types matching those of the input array elements.
* If the `DISTINCT` parameter is specified, input array rows are deduplicated before collection; identical arrays are taken only once.
* If the `limit` parameter is specified, the returned array contains at most `limit` elements.
* The function does not guarantee the order of elements in the result array.
* `NULL` values in the input arrays do not affect the calculation of the result array.

#### Examples

The following examples demonstrate how to use the `collect_list_on_array` function to collect array elements and return a new array.

Example 1: Basic usage

```sql
SELECT collect_list_on_array(a)
FROM VALUES
  (ARRAY(3, 3, 4)),
  (NULL),
  (ARRAY(2, 2, 3)),
  (ARRAY(NULL)),
  (ARRAY(1, NULL, 2)),
  (ARRAY(1, 2, 2))
AS t(a);
+--------------------------+
| collect_list_on_array(a) |
+--------------------------+
| [3,3,4,2,2,3,1,2,1,2,2]  |
+--------------------------+
```

Example 2: Use the limit parameter to restrict the number of returned elements

```sql
SELECT collect_list_on_array(a, 5)
FROM VALUES
  (ARRAY(3, 3, 4)),
  (NULL),
  (ARRAY(2, 2, 3)),
  (ARRAY(NULL)),
  (ARRAY(1, NULL, 2)),
  (ARRAY(1, 2, 2))
AS t(a);
+-----------------------------+
| collect_list_on_array(a, 5) |
+-----------------------------+
| [3,3,4,2,2]                 |
+-----------------------------+
```

Example 3: Use DISTINCT to deduplicate input array rows

The `DISTINCT` keyword deduplicates **entire array rows**, meaning identical arrays are collected only once; it does not affect elements within the arrays.

```sql
SELECT collect_list_on_array(DISTINCT a)
FROM VALUES
  (ARRAY(1, 2)),
  (ARRAY(1, 2)),
  (ARRAY(3))
AS t(a);
+-----------------------------------+
| collect_list_on_array(DISTINCT a) |
+-----------------------------------+
| [1,2,3]                           |
+-----------------------------------+
```
