### GENERAL_HASH

####  Description
This section introduces two general hash functions, `general_complexhash2` and `general_murmurhash3`, which can be used to perform hash calculations on data of any type. `general_complexhash2` automatically selects a more efficient calculation method based on the type of input data, while `general_murmurhash3` uses the well-known MurmurHash3 algorithm for hash calculation.

#### Usage
* **general_complexhash2(expr)**: Performs a hash calculation on input data `expr` of any type and returns an integer result.
* **general_murmurhash3(expr)**: Uses the MurmurHash3 algorithm to perform a hash calculation on input data `expr` of any type and returns an integer result.

#### Parameters
* **expr**: Input data of any type.

#### Return Results
* Returns an integer value representing the hash value of the input data.

#### Examples
```sql
-- Use general_complexhash2 to calculate the hash value of a string
> SELECT general_complexhash2('hello');
-- Result: -5436999610281751320

-- Use general_murmurhash3 to calculate the hash value of a string
> SELECT general_murmurhash3('hello');
-- Result: -8014657081559513573

-- Calculate the hash value for different data types
> SELECT general_complexhash2(123);
-- Result: 9208534749291869864

> SELECT general_murmurhash3(123);
-- Result: 5808450433748234714

-- Calculate the hash value for floating-point numbers
> SELECT general_complexhash2(3.14);
-- Result: -3844631488065270338

> SELECT general_murmurhash3(3.14);
-- Result: 9195935839840165100

-- Calculate the hash value for date types
> SELECT general_complexhash2(date'2022-01-01');
-- Result: -8898766858233323866

-- Calculate the hash value for timestamp types
> SELECT general_complexhash2(timestamp'2022-01-01 10:00:00');
-- Result: 1671608758248121621
```