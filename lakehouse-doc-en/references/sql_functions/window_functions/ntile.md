### NTILE 
```sql
ntile(n) over ([partition_clause] [orderby_clause])
```
#### Description

The NTILE function is used to divide a dataset into n equal parts (buckets) in order and assign a bucket number to each data item. When the dataset cannot be evenly divided into n equal parts, the earlier buckets will be given extra data items preferentially. This function is commonly used in data analysis and data grouping.

#### Parameter Description

* n (bigint type constant): The number of buckets to divide into.

#### Return Result

* Returns a bigint type bucket number.

#### Usage Example

1. Simple usage:
```sql
SELECT name, dep_no,salary,NTILE(4) OVER (ORDER BY salary) AS quartile
 FROM VALUES
  ('Eric', 1, 28000),
  ('Alex', 1, 32000),
  ('Felix', 2, 21000),
  ('Frank', 1, 30000),
  ('Tom', 2, 23000),
  ('Jane', 3, 29000),
  ('Jeff', 3, 35000),
  ('Paul', 2, 29000),
  ('Charles', 2, 23000),
  ('Charles F', 2, 23000),
  ('null',4,null),
  ('NotNull',4,23000)
  AS tab(name, dep_no, salary);
+-----------+--------+--------+----------+
|   name    | dep_no | salary | quartile |
+-----------+--------+--------+----------+
| null      | 4      | null   | 1        |
| Felix     | 2      | 21000  | 1        |
| Tom       | 2      | 23000  | 1        |
| Charles   | 2      | 23000  | 2        |
| Charles F | 2      | 23000  | 2        |
| NotNull   | 4      | 23000  | 2        |
| Eric      | 1      | 28000  | 3        |
| Jane      | 3      | 29000  | 3        |
| Paul      | 2      | 29000  | 3        |
| Frank     | 1      | 30000  | 4        |
| Alex      | 1      | 32000  | 4        |
| Jeff      | 3      | 35000  | 4        |
+-----------+--------+--------+----------+
```
This example divides employees into 4 quartiles based on their salaries in ascending order and assigns each employee a corresponding quartile number.