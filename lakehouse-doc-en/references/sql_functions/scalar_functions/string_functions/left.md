### LEFT
```sql
left(str, len)
```

#### Function
Returns the leftmost `len` characters of the string `str`.

#### Parameters
* str: string type
* len: int type, the number of characters to return

#### Returns
* string type, returns the leftmost `len` characters of the string.
* If `len` is less than or equal to 0, returns an empty string.
* If `len` is greater than the string length, returns the full string.

#### Examples
```sql
SELECT left('hello-world', 7);
-- Result: hello-w
```

```sql
SELECT left('hello-world', 0);
```

```sql
SELECT left('hello-world', 99);
-- Result: hello-world
```

```sql
SELECT left('hellocaféworld', 7);
-- Result: helloca
```

#### Notes
* Supports Unicode characters, counting by character (not by byte).
* Returns an empty string when the `len` parameter is negative.
