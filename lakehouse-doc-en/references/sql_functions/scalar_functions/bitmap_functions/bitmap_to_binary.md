### BITMAP_TO_BINARY 

####  Description
The BITMAP_TO_BINARY function is used to convert data of bitmap type to binary type. The binary type is typically used to store binary data, which can be conveniently transferred and processed between different systems and applications.

####  Syntax
```
BITMAP_TO_BINARY(bitmap)
```
#### Parameter Description
* bitmap: The bitmap type data that needs to be converted.

#### Return Result
* Returns the converted binary type data.

####  Example

1. Convert multiple bitmap values to binary type and store them in an array:
   ```sql
   SELECT binary_to_bitmap(BITMAP_TO_BINARY(bitmap_build(array(1, 2, 3))));
    [1,2,3]
   ```
By the above example, you can see the application of the BITMAP_TO_BINARY function in different scenarios. Using this function allows for convenient conversion between bitmap and binary types, facilitating data processing and transmission in different environments.