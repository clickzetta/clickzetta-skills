### FIND_IN_SET Function

```sql
find_in_set(str, strlist)
```

#### Description

`strlist` is a string composed of N substrings separated by `,`. If the string `str` is present in `strlist`, returns the position of `str` (between 1 and N).

If `str` is not in `strlist` or `strlist` is an empty string, returns 0.

#### Parameters

* `str`: STRING type, the string to search for.
* `strlist`: STRING type, a comma-separated list of strings.

#### Returns

INT type. Returns the position of `str` in `strlist` (1-based), or 0 if not found.

#### Examples

1. Basic usage:

    ```sql
    SELECT find_in_set('b', 'a,b,c,d');
    -- Result: 2
    ```

2. Returns 0 when not found:

    ```sql
    SELECT find_in_set('d', 'a,b,c');
    -- Result: 0
    ```

3. Supports Unicode characters:

    ```sql
    SELECT find_in_set('β', 'α,β,γ');
    -- Result: 2
    ```

#### Notes

* Returns NULL when any parameter is NULL.
* This function will not work correctly when the first argument `str` contains a comma `,`.
* Returns 0 when `str` is an empty string.
