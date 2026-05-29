### MASK_OUTER Function

#### Overview

The MASK_OUTER function masks the outer characters of a string, replacing the specified number of characters at the left and right ends with a mask character, while preserving the middle portion. This function is commonly used in data masking scenarios, such as hiding the beginning and ending portions of sensitive information like phone numbers, ID numbers, and credit card numbers.

#### Syntax

`mask_outer(str, left_margin, right_margin [, mask_char])`

#### Parameters

* `str`: STRING type, the original string to be masked.
* `left_margin`: INT type, the number of characters on the left to be replaced by the mask.
* `right_margin`: INT type, the number of characters on the right to be replaced by the mask.
* `mask_char` (optional): STRING type, the mask character used to replace the outer characters, defaulting to `'X'`.

#### Returns

Returns a STRING type value where the leftmost `left_margin` characters and rightmost `right_margin` characters are replaced by `mask_char`, with the middle portion preserved.

#### Examples

1. Basic usage, using the default mask character `'X'`:

    ```sql
    SELECT mask_outer('This is a string', 1, 5);
    +-------------------------------------------+
    | mask_outer('This is a string', 1, 5)      |
    +-------------------------------------------+
    | Xhis is a sXXXXX                          |
    +-------------------------------------------+
    ```

2. Specifying a custom mask character `'*'`:

    ```sql
    SELECT mask_outer('This is a string', 1, 5, '*');
    +------------------------------------------------+
    | mask_outer('This is a string', 1, 5, '*')      |
    +------------------------------------------------+
    | *his is a s*****                               |
    +------------------------------------------------+
    ```

3. Masking the first 3 and last 4 digits of a phone number:

    ```sql
    SELECT mask_outer('13812345678', 3, 4);
    +----------------------------------+
    | mask_outer('13812345678', 3, 4)  |
    +----------------------------------+
    | XXX1234XXXX                      |
    +----------------------------------+
    ```

4. When the input is NULL:

    ```sql
    SELECT mask_outer(NULL, 2, 3);
    +------------------------+
    | mask_outer(NULL, 2, 3) |
    +------------------------+
    | NULL                   |
    +------------------------+
    ```

#### Notes

* When the input string `str` is NULL, the result is NULL.
* The default mask character is `'X'`, which can be customized via the fourth parameter.
* `left_margin` and `right_margin` are based on character count (not byte count), so multi-byte characters (such as Chinese) are also counted by character.
* When `left_margin + right_margin` is greater than or equal to the string length, all characters will be replaced by the mask.
* This function complements the `mask_inner` function: `mask_outer` masks the ends and preserves the middle portion, while `mask_inner` masks the middle portion and preserves the ends.
