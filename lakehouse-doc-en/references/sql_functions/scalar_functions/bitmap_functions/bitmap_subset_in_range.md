### BITMAP_SUBSET_IN_RANGE 
``` sql
bitmap_subset_in_range(bitmap, range_start, range_end)
```
####  Description
The BITMAP_SUBSET_IN_RANGE function is used to extract a subset from a given bitmap within a specified range. The range starts from range_start (inclusive) and ends at range_end (exclusive). The current version only supports int type range values.

#### Parameter Description
- bitmap: Input data of bitmap type.
- range_start: The starting point of the range, int type data. The starting value is 1.
- range_end: The endpoint of the range, int type data.

#### Return Type
Returns data of bitmap type, containing elements within the specified range.

#### Usage Example

1. Extract the subset in the range [1, 3):
``` sql
SELECT bitmap_subset_in_range(bitmap_build(array(2, 1, 3, 4)), 1, 3);
```
Results:
```
[1, 2]
```
2. Extract the subset of the interval [5, 7) (the result is empty because there are no elements in the interval):
``` sql
SELECT bitmap_subset_in_range(bitmap_build(array(1, 3, 5, 7, 9)), 5, 7);
```
Results:
```
[]
```

3. Extract a subset from a bitmap containing multiple elements in the range [2, 5):

``` sql
SELECT bitmap_subset_in_range(bitmap_build(array(1, 2, 3, 4, 5, 6, 7, 8, 9)), 2, 5);
```
Results:
```
[2, 3, 4]
```
#### Notes
- Please ensure that the input bitmap type data is valid.
- When the range is empty, the returned result will be an empty bitmap type data.
- Please ensure that the values of range_start and range_end are valid int type values.
- The client does not support directly printing bitmap type results. If you directly view the bitmap results, an error will occur. Therefore, in actual use, if you need to display the screen, you need to use bitmap_to_array to convert it into an array.