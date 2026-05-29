# MATCH_PHRASE

```SQL
MATCH_PHRASE(inverted_column,query, option) 
```
###  Description

This function can only be used on columns that have an inverted index built. Based on match\_all, the order of the matching results must be consistent and continuous with the query tokenization results, ignoring case. Then, the query is constructed based on the tokenization, and the final query results are returned. For example, if the query string is "Microsoft Azure Party", the analyzer tokenizes it into three lowercase words: microsoft, azure, and party. Then, a boolean query is constructed based on the analysis results. By default, the query logic executed internally by the engine is: as long as the eventname field value contains all of microsoft, azure, or party, and the order is microsoft, azure, or party, then that row of data is returned.

### Parameter Description

* **inverted\_column**: The column used to build the inverted index.
* **query**: The text string you want to search for.
* **option**: This parameter is required to specify the tokenization settings. It must use the same tokenization method as the column used to build the inverted index. The `auto` parameter is supported, which will automatically match the tokenization settings in `inverted_column`, for example: `map('analyzer', 'auto')`.

### Return Result

boolean type

### Example

1. Example One
```SQL
select match_phrase('a b c', 'a b', map('analyzer', 'english')) as res;
+------+
| res  |
+------+
| true |
+------+
select match_phrase('a b c', 'a c', map('analyzer', 'english')) as res;
+-------+
|  res  |
+-------+
| false |
+-------+
```

2. Query data containing 'Elfriede Heaney', requiring both words in order and consecutive:

```SQL
select * from bulkload_data where match_phrase(data,'Elfriede Heaney',map('analyzer', 'unicode'));
+------------------------------------------------------------------------------------------------------------------------------------------+
|                                                                   data                                                                   |
+------------------------------------------------------------------------------------------------------------------------------------------+
| {"address":"Apt. 423 78018 Wisozk Meadow, West Marge, WV 16958","name":"Elfriede Heaney","email":"jamar.schoen@gmail.com"}               |
| {"address":"Suite 654 89305 Dan Drive, Haiview, AZ 55461","name":"Elfriede Heaney","email":"kristofer.upton@yahoo.com"}                  |
| {"address":"1133 Cartwright Orchard, Port Jonathon, UT 71589-4026","name":"Elfriede Heaney","email":"douglass.nitzsche@yahoo.com"}       |
| {"address":"Suite 342 631 Konopelski Hollow, East Chingview, UT 79212","name":"Elfriede Heaney DDS","email":"mikel.keebler@hotmail.com"} |
+------------------------------------------------------------------------------------------------------------------------------------------+
```