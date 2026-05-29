### APPROX_HISTOGRAM

####  Description

The `approx_histogram` function is used to generate an approximate histogram based on a given numeric column `col` and the number of buckets `n`. This function returns an array where each element is a structure (STRUCT) containing three fields: minimum value (min), maximum value (max), and count. This function is very useful for statistical data distribution, especially when dealing with large amounts of data, as it allows for a quick understanding of the data distribution.

#### Parameter Description

* `col`: The numeric column for which the histogram needs to be generated.
* `n`: The number of buckets in the histogram, which must be a positive integer constant.

#### Return Result

The function returns an array of structures, each containing three fields:

* `min`: The minimum value of the histogram bucket.
* `max`: The maximum value of the histogram bucket.
* `count`: The number of data points falling within the bucket.

#### Usage Example

The following examples demonstrate how to use the `approx_histogram` function to generate histograms with different numbers of buckets.

**Example 1: Generating a histogram with 2 buckets**
```sql
SELECT approx_histogram(col, 2) FROM VALUES (0), (1), (2), (3), (4) AS t(col);
+-------------------------------------------------------------------+
|                     approx_histogram(col, 2)                      |
+-------------------------------------------------------------------+
| [{"min":0.0,"max":0.5,"count":1},{"min":0.5,"max":4.0,"count":4}] |
+-------------------------------------------------------------------+
```
**Example 2: Generate a Histogram with 5 Buckets**
```sql
SELECT approx_histogram(col, 5) FROM VALUES (0), (1), (2), (3), (4) AS t(col);
+-------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                                                                     approx_histogram(col, 5)                                                                      |
+-------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| [{"min":0.0,"max":0.0,"count":1},{"min":0.0,"max":1.0,"count":1},{"min":1.0,"max":2.0,"count":1},{"min":2.0,"max":3.0,"count":1},{"min":3.0,"max":4.0,"count":2}] |
+-------------------------------------------------------------------------------------------------------------------------------------------------------------------+
```
**Example 3: Generate a Histogram with 10 Buckets**
```sql
SELECT approx_histogram(col, 10) FROM VALUES (0),(0.1), (0.2), (0.3), (0.4), (0.5), (0.6), (0.7), (0.8), (0.9) AS t(col);
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                                                                                                                                                    approx_histogram(col, 10)                             |
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| [{"min":0.0,"max":0.0,"count":1},{"min":0.0,"max":0.1,"count":1},{"min":0.1,"max":0.2,"count":1},{"min":0.2,"max":0.3,"count":1},{"min":0.3,"max":0.4,"count":1},{"min":0.4,"max":0.5,"count":1},{"min": |
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
```