### BITMAP_OR

---

####  Description

The BITMAP_OR function is used to compute the union (OR operation) of two bitmap type data sets. This function takes two bitmap inputs as parameters and returns a new bitmap result that contains all the non-zero values from both input bitmaps.

#### Syntax 
```
bitmap_or(left, right)
```
#### Parameter Description

* **left**, **right**: These two parameters are of bitmap type, representing the two sets that need to be ORed.

#### Return Type

The function returns a result of bitmap type.

#### Usage Example

The following example demonstrates how to use the BITMAP_OR function:

1. **Basic Usage**  
   Calculate the OR set of two simple bitmaps:
   ```sql
   SELECT bitmap_or(bitmap_build(array(1, 2, 3)), bitmap_build(array(2, 3, 4)));
   ```
Expected result: `[1, 2, 3, 4]` (The result is displayed in array form, the actual client may not support bitmap type printing)

2. **Using with array functions**  
   Use the bitmap_or function to process the array and convert the result to array form:
   ```sql
   SELECT bitmap_to_array(bitmap_or(bitmap_build(array(1, 2, 3)), bitmap_build(array(2, 3, 4))));
   ```
Expected result: `[1, 2, 3, 4]`

3. **Multiple Set Operations**  
   Perform continuous OR operations on multiple bitmaps:
   ```sql
   SELECT bitmap_to_array(bitmap_or(bitmap_or(bitmap_build(array(1, 2, 3)), bitmap_build(array(2, 3, 4))), bitmap_build(array(3, 4, 5))));
   ```
Expected result: `[1, 2, 3, 4, 5]`

4. **Handling Null Values**  
   When one of the input bitmaps is null, the result will reflect the non-null bitmap:
   ```sql
   SELECT bitmap_to_array(bitmap_or(bitmap_build(array(1, 2, 3)), NULL));
   ```
Expected result: `[1, 2, 3]`

#### Notes
- The client does not support directly printing bitmap type results. If you try to view bitmap results directly, an error will occur. Therefore, in actual use, if you need to display on the screen, you need to use bitmap_to_array to convert it into an array.
* The BITMAP_OR function requires both input parameters to be of bitmap type; otherwise, an error will be returned.
* When dealing with large datasets, be mindful of memory usage, as bitmaps can consume a significant amount of memory.

Through the above examples and explanations, you can better understand the purpose and usage of the BITMAP_OR function. In practical applications, the BITMAP_OR function can effectively process and analyze bitmap type data, helping you complete complex data set operations.