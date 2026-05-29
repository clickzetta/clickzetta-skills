###  COLLECT_LIST
```
collect_list([distinct] expr)
```
####  Description

The collect\_list function is used to collect and return an array from a set of input data. Users can optionally use the distinct keyword to return a set without duplicate elements.

#### Parameter Description

* expr: An expression of any type, used to collect elements from the input data.

#### Return Result

* Returns an array where the element type is the same as the input parameter type.
* If the distinct keyword is set, a deduplicated set is returned.
* The function does not guarantee the order of elements in the return result.
* If the input data contains null values, null will not be included in the calculation.

#### Usage Example

1. Return an array containing non-duplicate elements:
   ```sql
   SELECT collect_list(DISTINCT col) FROM VALUES (1), (2), (1), (null) AS tab(col);
   +----------------------------+
   | collect_list(DISTINCT col) |
   +----------------------------+
   | [2,1]                      |
   +----------------------------+
   ```
2. Return an array containing duplicate elements:
   ```sql
   SELECT collect_list(col) FROM VALUES (1), (2), (1), (null) AS tab(col);
   +-------------------+
   | collect_list(col) |
   +-------------------+
   | [1,2,1]           |
   +-------------------+
   ```
3. Collecting Characters from String Data: 

   ```sql
   SELECT collect_list(col) FROM VALUES ("apple"), ("banana"), ("cherry"), (null) AS tab(col);
   +-----------------------------+
   |      collect_list(col)      |
   +-----------------------------+
   | ["apple","banana","cherry"] |
   +-----------------------------+
   ```
4. Collect and return an array containing null values:
   ```sql
   SELECT collect_list(col) FROM VALUES (true), (false), (null) AS tab(col);
   +-------------------+
   | collect_list(col) |
   +-------------------+
   | [true,false]      |
   +-------------------+
   ```