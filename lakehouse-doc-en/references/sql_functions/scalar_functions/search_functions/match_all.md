## MATCH\_ALL

```SQL
MATCH_ALL(inverted_column,query, option) 
```
###  Description

This function can only be used on columns that have an inverted index built. It matches all, first analyzing the query string, ignoring case. Then, the query is constructed based on the tokenization, and the query results are returned. For example, if the query string is "Microsoft Azure Party", the analyzer will tokenize it into three lowercase words: microsoft, azure, and party. Based on the analysis results, a boolean query is constructed. By default, the query logic executed internally by the engine is: as long as the eventname field value contains all of microsoft, azure, or party, the row data is returned.

### Parameter Description

* **inverted\_column**: The column used to build the inverted index.
* **query**: The text string you want to search for.
* **option**: This parameter is required to specify the tokenization settings. It must use the same tokenization method as the column used to build the inverted index. The `auto` parameter is supported, which will automatically match the tokenization settings in `inverted_column`, for example: `map('analyzer', 'auto')`.

### Return Result

boolean type

### Example

* Example One
```SQL
 select match_all('a b c', 'b a', map('analyzer', 'english')) as res;
 +------+
| res  |
+------+
| true |
+------+
 select match_all('a b c', 'b a d', map('analyzer', 'english')) as res;
 +-------+
|  res  |
+-------+
| false |
+-------+
 
```
* Query data containing Elfriede Heaney, requiring both Elfriede and Heaney, order not required
```SQL
--Query data containing Elfriede Heaney
select * from bulkload_data where match_all(data,'Elfriede Heaney',map('analyzer', 'auto'));
+------------------------------------------------------------------------------------------------------------------------------------------+
|                                                                   data                                                                   |
+------------------------------------------------------------------------------------------------------------------------------------------+
| {"address":"Apt. 423 78018 Wisozk Meadow, West Marge, WV 16958","name":"Elfriede Heaney","email":"jamar.schoen@gmail.com"}               |
| {"address":"Suite 654 89305 Dan Drive, Haiview, AZ 55461","name":"Elfriede Heaney","email":"kristofer.upton@yahoo.com"}                  |
| {"address":"1133 Cartwright Orchard, Port Jonathon, UT 71589-4026","name":"Elfriede Heaney","email":"douglass.nitzsche@yahoo.com"}       |
| {"address":"115 Avery Mountains, New Elfriede, TN 83686-3466","name":"Clarence Heaney","email":"emmanuel.lockman@yahoo.com"}             |
| {"address":"Suite 342 631 Konopelski Hollow, East Chingview, UT 79212","name":"Elfriede Heaney DDS","email":"mikel.keebler@hotmail.com"} |
| {"address":"415 Elfriede Row, New Adriene, SC 90250","name":"Jefferson Heaney","email":"len.price@yahoo.com"}                            |
+------------------------------------------------------------------------------------------------------------------------------------------+
```