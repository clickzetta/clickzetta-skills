## MATCH_ANY

```SQL
MATCH_ANY(inverted_column,query, option) 
```
###  Description

This function can only be used on columns that have an inverted index built. It matches any tokenized string within the column, ignoring case. First, the query string is analyzed, and then the query is constructed based on the tokens, ultimately returning the query results. For example, if the query string is "Microsoft Azure Party", the analyzer will tokenize it into three lowercase words: microsoft, azure, and party. Then, a boolean query is constructed based on the analysis results. By default, the query logic executed internally by the engine is: as long as the eventname field contains any of the words microsoft, azure, or party, the row of data will be returned.

### Parameter Description

* **inverted\_column**: The column used to build the inverted index.
* **query**: The text string you want to search for.
* **option**: This parameter is required to specify the tokenization settings. It must use the same tokenization method as the column used to build the inverted index. The `auto` parameter is supported, which will automatically match the tokenization settings in `inverted_column`, for example: `map('analyzer', 'auto')`.

### Return Result

boolean type

### Example

1. Example One

<Notes>

[permalink]: #description
```SQL
 select match_any('a b c', 'd a', map('analyzer', 'english')) as res;
 +------+
| res  |
+------+
| true |
+------+
 select match_any('a b c', 'b a d', map('analyzer', 'english')) as res;
  +------+
| res  |
+------+
| true |
+------+
```

2. Query data containing Elfriede Heaney, requiring both Elfriede and Heaney to be present, but not necessarily in order.

```SQL
--Query data containing any of the two words Elfriede Heaney
select count(*) from bulkload_data where match_any(data,'Elfriede Heaney',map('analyzer', 'auto'));
+------------+
| `count`(*) |
+------------+
| 33614      |
+------------+
```