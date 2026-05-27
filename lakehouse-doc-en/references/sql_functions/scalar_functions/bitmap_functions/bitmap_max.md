### BITMAP_MAX
#### Description
The BITMAP_MAX function is used to extract the maximum value from a given bitmap type data. This function is very useful for processing a range of integers and can quickly find the maximum value among them.

#### Syntax
```
bitmap_max(bitmap)
```
#### Parameters
- **bitmap**: Input data of bitmap type.

#### Return Value
- Returns a value of bigint type, representing the maximum element in the input bitmap.

#### Example Usage
1. Construct a bitmap from an array and find the maximum value:
```
SELECT bitmap_max(bitmap_build(array(1, 2, 3, 4, 5)));
-- Output result: 5
```
#### Notes
- Ensure that the input bitmap data is not empty, otherwise the function will return NULL.
- The BITMAP_MAX function is suitable for handling integer ranges and may not return correct results for non-integer type data.

Through the above examples and explanations, you can better understand the purpose and usage of the BITMAP_MAX function. In practical applications, you can flexibly use this function to handle various types of bitmap data.