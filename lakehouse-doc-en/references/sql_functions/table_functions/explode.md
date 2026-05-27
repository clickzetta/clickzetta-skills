### EXPLODE 

#### Description

The EXPLODE function is used to expand an array or map type expression into multiple rows. For array type inputs, the elements are expanded into individual rows one by one; for map type inputs, the keys and values are expanded into multiple rows respectively. This function can be used directly or in conjunction with LATERAL VIEW for more complex data processing.

#### Parameters

* expr: The input array (`array<T>`) or map (`map<K, V>`) expression.

#### Return Results

* For array type inputs, the type of each element in the returned result is `T`.
* For map type inputs, the returned result contains two columns representing the key (`key`) and value (`value`), with their types being `K` and `V` respectively.

#### Usage Example

1. Expand an array type expression into multiple rows:
```sql
SELECT explode(array(1, 2, 3));
+-----+
| col |
+-----+
| 1   |
| 2   |
| 3   |
+-----+
```

2. Expand the mapping type expression into multiple lines:
```sql
SELECT explode(map("a", 1, "b", 2, "c", 3));
+-----+-------+
| key | value |
+-----+-------+
| a   | 1     |
| b   | 2     |
| c   | 3     |
+-----+-------+
```
3. Using in conjunction with LATERAL VIEW, expand the array type expression into multiple rows and associate it with the original data:
```sql
SELECT vt.word, lv.ex
FROM VALUES ('hello') AS vt(word) LATERAL VIEW explode(array(5, 6)) lv AS ex;
+-------+----+
| word  | ex |
+-------+----+
| hello | 5  |
| hello | 6  |
+-------+----+
```
4. Using in conjunction with LATERAL VIEW, expand the expression of the map type into multiple rows and associate it with the original data:
```sql
SELECT vt.word, lv.key, lv.value
FROM VALUES ('hello') AS vt(word) LATERAL VIEW explode(map("a", 1, "b", 2, "c", 3)) lv AS key, value;
+-------+-----+-------+
| word  | key | value |
+-------+-----+-------+
| hello | a   | 1     |
| hello | b   | 2     |
| hello | c   | 3     |
+-------+-----+-------+
```
Through the above example, you can see the flexibility and practicality of the EXPLODE function when dealing with array and map type data. In practical applications, you can perform expansion operations on the input data as needed for more in-depth data analysis and processing.