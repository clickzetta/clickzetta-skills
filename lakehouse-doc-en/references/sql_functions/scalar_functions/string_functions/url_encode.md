### URL_ENCODE
```sql
url_encode(str)
```

#### Function
Performs URL encoding on a string.

#### Parameters
* str: string type, the string to encode

#### Returns
* string type, returns the URL-encoded string.
* Special characters are converted to `%XX` format.
* Spaces are encoded as `+`.

#### Examples
```sql
SELECT url_encode('http://yunqi.tech/path?query=&key=2');
-- Result: http%3A%2F%2Fyunqi.tech%2Fpath%3Fquery%3D%26key%3D2
```

```sql
SELECT url_encode('http://yunqi.tech/path?query=&key= 2');
-- Result: http%3A%2F%2Fyunqi.tech%2Fpath%3Fquery%3D%26key%3D+2
```

```sql
SELECT url_encode('http://yunqi.tech/path?query=1#ref');
-- Result: http%3A%2F%2Fyunqi.tech%2Fpath%3Fquery%3D1%23ref
```

#### Notes
* This is the inverse of the `URL_DECODE` function.
* Spaces are encoded as `+`.
* Supports standard URL percent-encoding.
* Commonly used for constructing URL query parameters.
