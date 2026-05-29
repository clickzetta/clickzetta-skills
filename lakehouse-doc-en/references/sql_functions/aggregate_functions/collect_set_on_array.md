### COLLECT_SET_ON_ARRAY
```
collect_set_on_array([distinct] expr)
```
####  Description

The `collect_set_on_array` function is used to extract unique elements from the input array expression and form a new array with these elements. When the `distinct` keyword is specified, the function will perform deduplication on the result. However, please note that even if `distinct` is not specified, the function itself has the deduplication feature, so the `distinct` keyword will not have any additional effect in this scenario.

#### Parameter Description

* `expr`: The input array type expression.

#### Return Result

Returns an array where the element type is the same as the input array's element type. The order of elements in the result array is not guaranteed to be the same as the input array, and `null` values in the array will not be included in the calculation.

####  Example

The following example demonstrates how to use the `collect_set_on_array` function to process different input arrays and return the deduplicated result array.

Example 1:

```sql
select
    array_sort(collect_set_on_array(a)) as result
from values
    (array(3, 3, 4)),
    (null),
    (array(2, 2, 3)),
    (array(null)),
    (array(1, null, 2)),
    (array(1, 2, 2))
as t(a);
+-----------+
|  result   |
+-----------+
| [1,2,3,4] |
+-----------+
```
Example 2:
```sql
select
    array_sort(collect_set_on_array(distinct a)) as result
from values
    (array(1, 1, 2)),
    (array(2, 3, 3)),
    (array(4, 5, 5))
as t(a);
+-------------+
|   result    |
+-------------+
| [1,2,3,4,5] |
+-------------+
```
#### Notes

* When the input array is entirely `null`, the `collect_set_on_array` function will return an empty array.