### BITMAP_XOR_CARDINALITY 

#### Description
The `BITMAP_XOR_CARDINALITY` function is used to calculate the number of elements in the result set after performing a set exclusive OR (XOR) operation on two bitmap type parameters. This function is highly efficient in data deduplication and set operations.

#### Syntax
```
bitmap_xor_cardinality(left, right)
```
#### Parameters
- `left` and `right`: Both are bitmap type parameters, representing the two sets to perform the XOR operation on.

#### Return Result
- Returns a bigint type value, representing the number of elements in the XOR operation result set.

####  Example
1. Calculate the number of elements in the XOR operation result of two simple sets:
```sql
SELECT bitmap_xor_cardinality(bitmap_build(array(1, 2, 3)), bitmap_build(array(2, 3, 4)));
```
Results:
```
2
```
In this example, after performing the XOR operation on the sets {1, 2, 3} and {2, 3, 4}, the resulting set is {1, 4}, with the number of elements being 2.

#### Notes
- Ensure that the input parameters are of the bitmap type, otherwise, it will cause the function to execute incorrectly.
- When handling large amounts of data, please be aware of the impact on memory and performance.