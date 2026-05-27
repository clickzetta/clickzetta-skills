### CHR
```sql
chr(n)
```

#### Function
Returns the ASCII character corresponding to the given integer.

#### Parameters
* `n`: int type, the ASCII code of the character, range 0-127.

#### Returns
* string type, returns the corresponding character.
* If the input is NULL, returns NULL.

#### Examples
```sql
> SELECT chr(100);
d

> SELECT chr(65);
A

> SELECT chr(null);
NULL
```
