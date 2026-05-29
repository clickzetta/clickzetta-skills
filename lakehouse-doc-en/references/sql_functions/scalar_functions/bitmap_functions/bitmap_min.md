### BITMAP_MIN

#### Description
The BITMAP_MIN function is used to find the smallest element from the input bitmap object and return its value. This function is very useful for processing and analyzing bitmap type data.

#### Syntax
```
bitmap_min(bitmap)
```
#### Parameters
- bitmap: bitmap type, representing the input bitmap object.

#### Return Result
- Returns a value of bigint type, representing the maximum element in the input bitmap.

#### Usage Example

1. Find the smallest element from a bitmap object containing multiple elements:
```sql
SELECT bitmap_min(bitmap_build(array(1, 2, 3)));
```
Results:
```
1
```
#### Notes
- If the input bitmap object is empty, the BITMAP_MIN function will return 0.
- The BITMAP_MIN function is only applicable to bitmap type data. For other types of data, it may cause errors or incorrect results.