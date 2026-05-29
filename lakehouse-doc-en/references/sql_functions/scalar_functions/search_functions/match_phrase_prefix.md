## MATCH\_PHRASE\_PREFIX

```SQL
MATCH_PHRASE_PREFIX(inverted_column,query, option) 
```
###  Description

This function can only be used on columns that have an inverted index built, matching phrase prefixes. The tokenization result of the inverted\_column, the first n-1 match rules are the same as match\_phrase. First, the query is tokenized to construct the query. For example, if the data in the inverted\_column contains a field "a b cd" and the input query is "b c", the query is tokenized by the analyzer into two lowercase letters: b and c. Then, based on the analysis results, a boolean query is constructed. By default, the query logic executed internally by the engine is: b first matches the b in the inverted\_column, then c can match the prefix of cd, thus returning the row data.

### Parameter Description

* **inverted\_column**: The column used to build the inverted index.
* **query**: The text string you want to search for.
* **option**: This parameter is required to specify the tokenization settings. It must use the same tokenization method as the column used to build the inverted index. The `auto` parameter is supported, which will automatically match the tokenization settings in `inverted_column`, for example: `map('analyzer', 'auto')`.

### Return Result

boolean type

### Example

```SQL
select match_phrase_prefix('a b cd', 'b c', map('analyzer', 'english'))as res;
+------+
| res  |
+------+
| true |
+------+
select match_phrase_prefix('a b dc', 'b c', map('analyzer', 'english'))as res;
+-------+
|  res  |
+-------+
| false |
+-------+
```