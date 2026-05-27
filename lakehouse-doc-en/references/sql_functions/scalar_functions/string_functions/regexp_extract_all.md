##  Description

The `REGEXP_EXTRACT_ALL` function is used to extract all substrings that match a regular expression from a string.

## Syntax
```SQL
REGEXP_EXTRACT_ALL(string, pattern)
```
## Parameter Description

* **string**: The original string to search.
* **pattern**: The regular expression with the matching pattern.

## Return Results

Returns an array containing all matching substrings.

## Example
```SQL
SELECT regexp_extract_all('100-200, 300-400',r'(\d+)-(\d+)', 1);
+---------------+
|      res      |
+---------------+
| ["100","300"] |
+---------------+
```