### STRPOS
```sql
strpos(str, substr [, instance])
```

#### Function
Returns the position of the first occurrence (or the instance-th occurrence) of the substring substr in the string str.

#### Parameters
* str: string type
* substr: string type, the substring to search for
* instance: int type (optional), specifies which occurrence to find, defaulting to 1

#### Returns
* int type, returns the position of the substring occurrence (1-based indexing)
* Returns 0 if the substring is not found
* Returns NULL if any parameter is NULL
* Returns 0 if instance is less than or equal to 0

#### Examples
```sql
SELECT strpos('high', 'ig');
-- Result: 2
```

```sql
SELECT strpos('high', 'igx');
-- Result: 0
```

```sql
SELECT strpos('Quadratically', 'a');
-- Result: 3
```

```sql
SELECT strpos('abc/xyz/foo/bar', '/', 1);
-- Result: 4
```

```sql
SELECT strpos('abc/xyz/foo/bar', '/', 2);
-- Result: 8
```

```sql
SELECT strpos('abc/xyz/foo/bar', '/', 3);
-- Result: 12
```

```sql
SELECT strpos('abc/xyz/foo/bar', '/', 4);
-- Result: 0
```

```sql
SELECT strpos('Belief,Love,Hope', 'Love');
-- Result: 8
```

```sql
SELECT strpos('Belief,Love,Hope', 'Hope');
-- Result: 14
```

```sql
SELECT strpos('', '');
-- Result: 1
```

```sql
SELECT strpos(null, '');
-- Result: NULL
```

#### Notes
* Position indexing starts at 1 (not 0).
* Supports Unicode strings.
* Returns 0 when the instance parameter exceeds the actual number of occurrences.
* When substr is an empty string, returns 1 if str is non-empty; returns 1 if both str and substr are empty.
