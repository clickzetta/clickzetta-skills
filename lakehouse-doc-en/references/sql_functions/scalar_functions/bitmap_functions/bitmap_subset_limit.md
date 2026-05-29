### BITMAP_SUBSET_IN_RANGE 

#### Description
The BITMAP_SUBSET_IN_RANGE function is used to extract a specified range subset from the given bitmap type data. The function determines the specific content of the subset based on the two parameters range_start (range start value) and cardinality_limit (range size limit). Currently, this function only supports int type interval values.

#### Parameters
* bitmap: Input bitmap type data.
* range_start: int type, representing the start value of the range.
* cardinality_limit: int type, representing the size limit of the range.

#### Return Value
Returns a bitmap type data containing elements within the specified range.

#### Example Usage
The following example demonstrates how to use the BITMAP_SUBSET_IN_RANGE function to extract a subset of bitmap data:

1. Extract a subset consisting of two elements starting from the second element:
```sql
SELECT BITMAP_SUBSET_IN_RANGE(bitmap_build(array(2, 1, 3)), 1, 2);
```
Results:
```
[1]
```
2. Convert the extracted subset to an array format:
```sql
SELECT BITMAP_TO_ARRAY(BITMAP_SUBSET_IN_RANGE(bitmap_build(array(2, 1, 3)), 1, 2));
```
Results:
```
[ 1]
```
Through the above examples, you can see the application of the BITMAP_SUBSET_IN_RANGE function in different scenarios. Using this function can help you handle and analyze bitmap type data more conveniently.