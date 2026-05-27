### URL_DECODE
```sql
url_decode(str)
```

#### Function
Decodes a URL-encoded string.

#### Parameters
* `str`: string type, the URL-encoded string

#### Returns
* **string type**: Returns the decoded string.
* Converts `%XX` encoded sequences to the corresponding characters.
* Converts `+` to space.

#### Examples
```sql
SELECT url_decode('http%3A%2F%2Fyunqi.tech%2Fpath%3Fquery%3D%26key%3D2');
-- Result: http://yunqi.tech/path?query=&key=2
```

```sql
SELECT url_decode('http%3A%2F%2Fyunqi.tech%2Fpath%3Fquery%3D%26key%3D+2');
-- Result: http://yunqi.tech/path?query=&key= 2
```

```sql
SELECT url_decode('http%3A%2F%2Fyunqi.tech%2Fpath%3Fquery%3D1%23ref');
-- Result: http://yunqi.tech/path?query=1#ref
```

#### Notes
* This is the inverse of the `URL_ENCODE` function.
* `+` is decoded to a space.
* Supports standard URL percent-encoding decoding.
