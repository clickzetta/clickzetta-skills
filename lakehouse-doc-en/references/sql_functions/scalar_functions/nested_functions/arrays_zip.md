### ARRAYS_ZIP

`arrays_zip(a1, a2, ... aN)` is a powerful array processing function that can merge multiple arrays a1, a2 to aN into a new array. Each element in the new array is a struct, which contains N fields corresponding to the k-th element in the input arrays. If the k-th element of a certain array does not exist, a null value is filled in the struct.

####  Description

The main purpose of this function is to merge multiple arrays according to the same index position to generate a new array. Each element of the new array is a struct, and the number of fields in the struct is the same as the number of input arrays. This merging method is very suitable for data integration when processing multidimensional data.

#### Parameter Description

* `a1 ~ aN`: Arrays to be merged, the array type is `array<T>`, where T can be any data type.

#### Return Result

Returns a new array, each element of which is a struct. The struct contains N fields, corresponding to the k-th element in the input arrays. The field names are `0`, `1` to `N-1`.

#### Usage Example

1. Basic usage:
   ```sql
   SELECT arrays_zip(array(1, 2), array(4));
   ```
Result: 
   ```json
   [{"0":1,"1":4},{"0":2,"1":null}]
   ```
In the above example, the two arrays have the same length and are directly merged to generate a new array.

2. Merging arrays of different lengths:
   ```sql
   SELECT arrays_zip(array(1, 2, 3), array(4, 5));
   ```
Result:
   ```json
    [{"0":1,"1":4},{"0":2,"1":5},{"0":3,"1":null}]
   ```
In this example, the two arrays have different lengths, and the elements after the shorter array will be filled with null when merged.

3. Multiple array merging:
   ```sql
   SELECT arrays_zip(array(1, 2), array(4, 5), array('a', 'b'));
   ```
Result: 
   ```json
    [{"0":1,"1":4,"2":"a"},{"0":2,"1":5,"2":"b"}]
   ```
In this example, three arrays are merged into a new array, with each element being a structure containing three fields.