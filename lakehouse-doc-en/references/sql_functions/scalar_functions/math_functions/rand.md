### RAND
```sql
RAND()
```
####  Description
`RAND()` function is a non-deterministic function used to generate a random number in the range [0,1). Each time this function is called, it returns a uniformly distributed random floating-point number, ranging from 0 (inclusive) to 1 (exclusive).

#### Return Type
The result type returned by this function is a double-precision floating-point number (double).

####  Example
1. Generate and display a random number:
   ```sql
   SELECT RAND();
   ```
The result may look like this:
   ```
   0.1234567890123456
   ```
2. Generate a random weight for each record in a table:
   Suppose there is a table named `products` with the following columns: `id` (product ID), `name` (product name), and `weight` (product weight). You can use the `RAND()` function to generate a random weight for each product:
   ```sql
   SELECT id, name, RAND() * 100 AS random_weight
   FROM products;
   ```
The result may look like this:
   ```
   1   iPhone 52.34567890
   2   Samsung 76.78901234
   3   Huawei 23.45678901
   ```