### RIGHT
```sql
right(str, len)
```

#### Function
Returns the rightmost `len` characters of the string str.

#### Parameters
* `str`: string type
* `len`: int type, the number of characters to return

#### Returns
* string type, returns the rightmost `len` characters of the string.
* If `len` is less than or equal to 0, returns an empty string.
* If `len` is greater than the string length, returns the full string.

#### Examples
```sql
SELECT right('hello-world', 7);
-- Result: o-world
```

```sql
SELECT right('hello-world', 0);
```

```sql
SELECT right('hello-world', 99);
-- Result: hello-world
```

```sql
SELECT right('hellcaféworld', 7);
-- Result: féworld
```

#### Notes
* Supports Unicode characters, counting by character (not by byte).
