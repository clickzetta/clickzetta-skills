# CHAR
`CHAR` is a fixed-length character type with a maximum length of 255. When the character length is less than the specified maximum length, the system does not automatically use spaces to fill to the maximum length. Spaces are not considered during string comparison.

## Syntax
```
CHAR(N)
```
Among them` N 'represents the maximum length of the character type' CHAR ', ranging from 1 to 255.



## Example
1. Create a `CHAR` type with a fixed length of 5:
```
CREATE TABLE char_t(col CHAR(5));
```
2. Insert a string that is not long enough:
```
SELECT CHAR(10) 'abcd';
```
The result will return a string with a length of 10, for example: `'abcd'`

3. Insert a string that exceeds the specified length:
```
SELECT cast( 'abcdef' as char(3))
```
The result will return a string of length 3, for example: `'abc'` (only the first 3 characters are taken)

4. When comparing char, ignore trailing spaces:
```
SELECT cast('abc' as char(5)) = cast('abc' as char(10));
```
The result will return `true` because trailing spaces are ignored during comparison.

## Notes
- When performing string comparisons, consider the characteristic that trailing spaces in the `CHAR` type are ignored.
- Depending on actual needs, choose between the `CHAR` type and the `VARCHAR` type appropriately. If the data length is fixed or varies within a small range, using the `CHAR` type can improve performance; conversely, if the data length varies greatly, it is recommended to use the `VARCHAR` type to save storage space.