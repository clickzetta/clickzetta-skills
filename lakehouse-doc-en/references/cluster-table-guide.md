# Bucketing (Clustered Key) and Sorting Key

In the field of big data storage and analysis, the way data is organized has a significant impact on query performance and storage efficiency. This article will provide a detailed introduction to the concepts of Clustered Key and Sorted Key, their usage, and practical application examples to help you better optimize your data organization structure.

## Clustered Key

The Clustered Key is the core of table data distribution. By specifying the column's Hash Key, Lakehouse will perform a hash operation on the data based on these keys and distribute the data into different data buckets. This dispersion helps to avoid data skew and hotspot issues while improving parallel processing capabilities.

### Criteria for Selecting Clustered Keys

- Choose columns with a wide range of values and few duplicate values as Clustered Keys to achieve uniform data distribution.
- When performing `JOIN` operations, if the join key is consistent with the Clustered Key, it can significantly improve performance.
- Suitable for scenarios with large amounts of data, the recommended data bucket size is about 128MB to 1GB, depending on the data compression rate and access pattern.
- If no Clustered Key is specified, 256 buckets are used by default.

### Precautions

- Avoid specifying too small a number of Clustered Keys to prevent generating a large number of small files, which can affect metadata management and I/O operation efficiency.
- Too many small files can lead to poor data locality, increased task scheduling overhead, and reduced processing efficiency.

## Sorted Key

The Sorted Key is used for the sorting method of file fields. For queries that need to sort the query results, sorting the data by the Sorted Key can improve performance.

### Precautions for Using Sorted Keys

- You can specify ascending (ASC) or descending (DESC) order for the Sorted Key.
- Although Sorted Keys can improve query performance, sorting a large amount of data during insertion may consume considerable resources.

## Practical Application Examples

### Example 1: Create a Table and Specify Clustered Key and Sorted Key
```sql
CREATE TABLE sales_data (
    sale_id INT,
    product_id INT,
    quantity_sold INT,
    sale_date DATE,
    ...
) CLUSTERED BY (product_id)
SORTED BY (sale_date DESC)
INTO 50 BUCKETS;
```
In this example, a table named `sales_data` is created, and the data will be distributed into 50 buckets based on the Hash value of the `product_id` column. At the same time, the data within each bucket will be sorted in descending order by the `sale_date` column.

### Example 2: Optimizing Data Warehouse Query Performance

Suppose you are dealing with a data warehouse containing a large number of transaction records. You can optimize query performance in the following way:
```sql
CREATE TABLE transaction_records (
    transaction_id INT,
    customer_id INT,
    transaction_date DATE,
    amount DECIMAL(10,2),
    ...
) CLUSTERED BY (customer_id)
SORTED BY (transaction_date ASC)
INTO 128 BUCKETS;
```
In this example, the `transaction_records` table is bucketed by `customer_id`, and the data within each bucket is sorted by `transaction_date`. This design helps improve the efficiency of querying transaction records by customer.

## Conclusion

Using bucket keys and sort keys appropriately can effectively optimize the physical storage structure of data and improve query performance, especially when dealing with large-scale datasets. This method is particularly suitable for data warehousing and big data analysis scenarios, significantly enhancing data processing efficiency and speed. I hope this article helps you better understand and apply bucket keys and sort keys to optimize your data organization methods.