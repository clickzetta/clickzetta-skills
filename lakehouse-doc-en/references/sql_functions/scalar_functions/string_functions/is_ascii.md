### IS_ASCII
```sql
is_ascii(str)
```

#### Function
Determines whether the string `str` contains only ASCII-encoded characters.

#### Parameters
- `str`: string

#### Return Value
- boolean

#### Example
```sql
> SELECT a, is_ascii(a)
FROM VALUES
  (""),
  ("abcd"),
  ("café"),
  ("©®") AS t(a);
        true
abcd    true
café    false
©®      false
```