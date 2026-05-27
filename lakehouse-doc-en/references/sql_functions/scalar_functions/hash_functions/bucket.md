### BUCKET
```sql
bucket(numBuckets, col)
```
#### Description
Computes a hash bucket number based on a specified number of buckets and a column value. This function uses a hash algorithm to map the input value to an integer within the range [0, numBuckets), commonly used in data partitioning and distributed computing scenarios.

#### Parameters
* `numBuckets`: int type, the number of buckets, must be greater than 0
* `col`: any type, the column value for which to compute the hash bucket

#### Return Result
* int type
* The return value range is [0, numBuckets)
* Returns NULL if the input value is NULL

#### Examples
```sql
SELECT bucket(10, 'test');
-- result: 4
```

```sql
SELECT bucket(10, 123);
-- result: 4
```

#### Notes
* The `BUCKET` function uses a hash algorithm to ensure the same input value is always mapped to the same bucket
* Commonly used in scenarios such as data partitioning, sampling, and load balancing
* The returned bucket number starts from 0, with a maximum value of numBuckets - 1
* The same value of different types (e.g., the integer 1 and the string '1') may be mapped to different buckets
* This function is deterministic: the same input always produces the same output.
