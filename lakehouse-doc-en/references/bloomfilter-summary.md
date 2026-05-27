# BloomFilter Index
## Introduction to the Principle of Bloom Filter Index:
1. **Data Structure**: A Bloom Filter consists of a bit array (BitSet) and multiple hash functions. Initially, all bits in the bit array are set to 0.
2. **Element Addition**: When adding an element to the set, multiple positions in the bit array are calculated using the hash functions, and the bits at these positions are set to 1.
3. **Element Query**: To check if an element exists, the hash functions are used to calculate the possible positions of the element in the bit array, and these positions are checked to see if all bits are 1. If all bits are 1, the element is considered to possibly exist in the set; if any bit is not 1, the element is definitely not in the set.
4. **Advantages**:
   * Space efficiency and query time are far superior to general algorithms, with storage space and insertion/query time being constant O(k).
   * Hash functions are independent of each other, facilitating hardware parallel implementation.
   * There is no need to store the elements themselves, which is advantageous in scenarios with strict confidentiality requirements.
5. **Disadvantages**:
   * As the number of elements increases, the false positive rate increases, i.e., the probability of false positives increases.
   * Generally, elements cannot be deleted from a Bloom Filter.
6. **Application Scenarios**:
   * Bloom Filter indexes are suitable for columns with high cardinality, such as ID columns, to quickly determine whether the data file of a table might contain the queried data, and if not, skip it, thereby reducing the amount of data scanned.
   * Suitable for equality queries (including = and IN), and effective for high cardinality fields such as USER-ID and other unique ID fields. The acceleration effect is limited for low cardinality fields, such as the "gender" field.

7. **False Positive Rate**: A Bloom Filter may falsely indicate that an element is in the set when it is not, but it will never falsely indicate that an element is not in the set when it is.

## Application of Bloom Filter in Lakehouse
A BloomFilter index is an efficient data structure used to quickly determine whether a data file contains specific data. By creating a BloomFilter index for a column, the system generates a BloomFilter for that column. During query execution, this index can be used to skip unnecessary data files, thereby reducing the amount of data scanned and improving query performance. BloomFilter is particularly suitable for columns with high cardinality.

For example, when executing a query such as `SELECT * FROM table WHERE col_name = 'xxx'`, the BloomFilter will first determine whether the target data file contains the value. If it does not, the system will skip the file, avoiding unnecessary reads. If the index indicates that the file might contain the target data, the file will be read for further querying.

The BloomFilter index is effective in the following operations: `AND`, `OR`, `IN`, `=`. It is important to note that after creating a BloomFilter index, only newly written data will include the index. For old data, it is recommended to use the `INSERT OVERWRITE` statement to rewrite the data and add the index.

### Specific Use Cases for Bloom Filter

**Scenario One: Equality Queries with Large Data Volumes**

**Case**:

Suppose there is a user table `users` containing millions of user records, with the following table structure:
```SQL
CREATE TABLE users (
    user_id INT,
    username VARCHAR(255),
    email VARCHAR(255)
);
```
In this table, the `email` field has a high cardinality, meaning most users have a unique email address. If we often need to query user information based on email addresses, we can create a Bloom Filter index for the `email` field.

**Create Index**:
```SQL
CREATE BLOOMFILTER INDEX idx_email ON TABLE users(email);
```
**Query**：

When we need to query users with a specific email, we can use the following query:
```SQL
SELECT * FROM users WHERE email = 'user@example.com';
```
* **Quick Exclusion**: Bloom Filter can help the database quickly determine whether `user@example.com` might be in the table. If the Bloom Filter determines that the email is not in the table, the related data files will be skipped, thereby reducing I/O operations and query time.
* **Performance Improvement**: For tables with large amounts of data, this quick exclusion can significantly improve query performance.

**Scenario Two: Query Optimization for High Cardinality Columns**

**Example**:

Suppose there is a product table `products`, which contains various attributes of the products. The table structure is as follows:
```SQL
CREATE TABLE products (
    product_id INT,
    category VARCHAR(100),
    price DECIMAL(10, 2)
);
```
In this table, the cardinality of the `category` field is very high because products can belong to different categories. If we often need to query products based on categories, we can create a Bloom Filter index for the `category` field.

**Create Index**:
```SQL
CREATE BLOOMFILTER INDEX idx_category ON TABLE products(category);
```
**Query**:

When we need to query a specific category of products, we can use the following query:
```SQL
SELECT * FROM products WHERE category = 'Electronics';
```
* **Reduce Scanning**: Bloom Filter can reduce the amount of data that needs to be scanned, as it can help skip data files that do not contain the target category.
* **Improve Efficiency**: For high cardinality columns, Bloom Filter can improve query efficiency, especially in cases with large amounts of data.

### Notes

* **False Positive Probability**: Bloom Filter has a defined false positive probability (FPP), which means it may incorrectly indicate that a value exists in the table. Therefore, even if the Bloom Filter suggests that a value might exist, the actual query may not find the value.
* **Write Operation Cost**: Bloom Filter may have higher costs during write operations (such as insert, update, delete) because it needs to update the Bloom Filter data structure.
* **Unsupported Data Types**: Bloom Filter does not support complex data types such as interval, struct, map, array, etc. Therefore, attention should be paid to the data type of the column when creating the index.

## Create BloomFilter Index

[Create BloomFilter Index](<CREATE-BLOOMFILTER-INDEX.md>)

To create a BloomFilter index for a column, you can use the following statement:
```
CREATE BLOOMFILTER INDEX index_name ON table_name (column_name);
```
For example, create an index named `email_bloomfilter` on the `email` column in the `employees` table:
```
CREATE BLOOMFILTER INDEX email_bloomfilter ON employees (email);
```
## View BloomFilter Index Details

[View BOOLFILTER Index Details](<DESC-INDEX.md>)

To view the BloomFilter index details on a table, you can use the `DESCRIBE INDEX` statement:
```
DESCRIBE INDEX index_name ON table_name;
```
For example, view the details of the index named `email_bloomfilter` on the `employees` table:
```
DESCRIBE INDEX email_bloomfilter ON employees;
```
## Delete BloomFilter Index

[Delete BloomFilter Index](<DROP-INDEX.md>)


To delete a BloomFilter index, you can use the `DROP INDEX` statement:
```
DROP INDEX index_name ON table_name;
```
For example, delete the index named `email_bloomfilter` on the `employees` table:
```
DROP INDEX email_bloomfilter ON employees;
```
## List BloomFilter Indexes on the Table

[List BloomFilter Indexes on the Table](<SHOW-INDEX.md>)

To view all BloomFilter indexes on the table, you can use the `SHOW INDEXES` statement:
```
SHOW INDEXES ON table_name;
```
For example, view all indexes on the `employees` table:
```
SHOW INDEXES ON employees;
```