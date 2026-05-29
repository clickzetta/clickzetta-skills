## MATCH_REGEXP

```SQL
MATCH_REGEXP(inverted_column,query, option) 
```
###  Description

Only columns that build an inverted index can use this function. It matches the regular expression, using the query's regular expression to match the tokenized results of the inverted\_column, with any match being sufficient. First, the query is tokenized to construct the search. For example, if there is a field in the inverted\_column with data "a b cd" and the input query is "c.\*", the query is tokenized by the analyzer into two lowercase letters: b and c. Then, a boolean query is constructed based on the analysis results. By default, the query logic executed internally by the engine is: c.\* matches cd in the inverted\_column, resulting in true.

### Parameter Description

* **inverted\_column**: The column used to build the inverted index.
* **query**: The text string you want to search for.
* **option**: This parameter is required and specifies the tokenization settings. It must use the same tokenization method as the column used to build the inverted index. The `auto` parameter is supported, which will automatically match the tokenization settings in `inverted_column`, for example: `map('analyzer', 'auto')`.

### Return Result

boolean type

### Example
```SQL
select match_regexp('a b dc', '.*c', map('analyzer', 'english'))as res;
+------+
| res  |
+------+
| true |
+------+
```