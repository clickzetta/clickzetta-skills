### IS_UTF8
```sql
is_utf8(str)
```

#### Function
Determines whether the string `str` contains only characters encoded in UTF-8.

#### Parameters
- `str`: string

#### Return Value
- boolean

#### Example
```sql
> SELECT a, is_utf8(a)
FROM VALUES
  (""),
  ("abcd"),
  ("café"),
  ("©®") AS t(a);
        true
abcd    true
café    true
©®      true
```