### MASK_INNER Function

#### Overview

The MASK_INNER function masks the inner characters of a string, preserving the specified number of characters at the left and right ends, and replacing the middle portion with a specified mask character. This function is commonly used in data masking scenarios, such as hiding the middle portion of sensitive information like phone numbers, ID numbers, and credit card numbers.

#### Syntax

`mask_inner(str, left_margin, right_margin [, mask_char])`

#### Parameters

* `str`: STRING type, the original string to be masked.
* `left_margin`: INT type, the number of characters to preserve on the left (not replaced by the mask).
* `right_margin`: INT type, the number of characters to preserve on the right (not replaced by the mask).
* `mask_char` (optional): STRING type, the mask character used to replace the middle portion, defaulting to `'X'`.

#### Returns

Returns a STRING type value where the leftmost `left_margin` characters and rightmost `right_margin` characters are preserved, and each character in the middle portion is replaced by `mask_char`.

#### Examples

1. Basic usage, using the default mask character `'X'`:

    ```sql
    SELECT mask_inner('This is a string', 1, 5);
    +-------------------------------------------+
    | mask_inner('This is a string', 1, 5)      |
    +-------------------------------------------+
    | TXXXXXXXXXXtring                          |
    +-------------------------------------------+
    ```

2. Specifying a custom mask character `'*'`:

    ```sql
    SELECT mask_inner('This is a string', 1, 5, '*');
    +------------------------------------------------+
    | mask_inner('This is a string', 1, 5, '*')      |
    +------------------------------------------------+
    | T**********tring                               |
    +------------------------------------------------+
    ```

3. Processing multibyte character strings:

    ```sql
    SELECT mask_inner('abc Hello, World end', 1, 5);
    +------------------------------------------------+
    | mask_inner('abc Hello, World end', 1, 5)       |
    +------------------------------------------------+
    | aXXXXXXXXXXXXXXd end                           |
    +------------------------------------------------+
    ```

4. When the input is NULL:

    ```sql
    SELECT mask_inner(NULL, 2, 3);
    +------------------------+
    | mask_inner(NULL, 2, 3) |
    +------------------------+
    | NULL                   |
    +------------------------+
    ```

#### Notes

* When the input string `str` is NULL, the result is NULL.
* The default mask character is `'X'`, which can be customized via the fourth parameter.
* `left_margin` and `right_margin` are based on character count (not byte count), so multi-byte characters (such as Chinese) are also counted by character.
* When `left_margin + right_margin` is greater than or equal to the string length, no masking is performed and the original string is returned.
* This function complements the `mask_outer` function: `mask_inner` masks the middle portion and preserves the ends, while `mask_outer` masks the ends and preserves the middle portion.
