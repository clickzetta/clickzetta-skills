### Mask 
```sql
mask_inner(str, margin1, margin2 [, mask_char]) 
mask_outer(str, margin1, margin2 [, mask_char]) 
```
#### Function 
The `mask_inner` and `mask_outer` functions are used to replace parts of a string, typically to hide sensitive information such as passwords, phone numbers, etc. The `mask_inner` function retains the characters at both ends of the string with lengths `margin1` and `margin2`, while replacing the middle part with a specified mask character (default is 'X'). The `mask_outer` function masks the characters at both ends of the string with lengths `margin1` and `margin2`, retaining the middle part.

#### Parameter Description
* `str`: The original string to be processed.
* `margin1`: The number of characters to retain or mask on the left end.
* `margin2`: The number of characters to retain or mask on the right end.
* `mask_char` (optional): The mask character used to replace the middle part of the string, default is 'X'.

#### Return Value
Returns the processed string.

#### Usage Example
```sql
-- Example 1: Hide the middle four digits of a phone number
SELECT mask_inner('13812345678', 3, 4);
-- Return result: 135XXXXX876

-- Example 2: Retain the front and back parts of an email address, hide the username part
SELECT mask_outer('alice@example.com', 5, 0);
-- Return result: XXXXX@example.com

-- Example 3: Hide the middle eight digits of a credit card number
SELECT mask_inner('1234 5678 9012 3456', 4, 4, '*');
-- Return result: 1234 **** 9012 3456

-- Example 4: Hide the middle ten digits of an ID card number
SELECT mask_inner('11010519850605003X', 2, 10);
-- Return result: 11XXXXXXXXX03X
```
By the above example, you can flexibly use the `mask_inner` and `mask_outer` functions according to actual needs to protect users' privacy information.