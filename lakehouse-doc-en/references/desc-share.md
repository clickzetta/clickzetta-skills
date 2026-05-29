# View Shared Data Object Information

##  Description

The `DESC SHARE` statement is used to query the specific data objects contained in a specified shared data object (share), such as tables, views, and schemas. Through this statement, users can understand the detailed information of the shared data objects, including object type, name, sharing time, etc.

## Syntax
```
DESC SHARE <share_name>;
```
## Parameter Description

- **share_name**: The name of the shared data object to query.

## Return Description

- **kind**: The type of data object added to the shared data object, usually including schema, table, and view.
- **name**: The name of the shared data object. For schema type, it directly returns its name; for table and view types, the format is `<schema_name>.<table_name>` or `<schema_name>.<view_name>`.
- **shared_on**: The time when the data object was added to the shared data object.

## Usage Example

Here are some examples of using the `DESC SHARE` statement:

1. Query the information of data objects contained in the shared data object named `customer_data`:
   ```
   DESC SHARE customer_data;
   ```
Possible return results:
   ```
   kind | name               | shared_on
   -----|--------------------|----------
   schema | customer           | 2022-01-01 10:00:00
   table  | customer.orders     | 2022-01-02 14:30:00
   view   | customer.order_summary | 2022-01-03 09:20:00
   ```
2. Query the table and view information contained in the shared data object named `financial_data`:
   ```
   DESC SHARE financial_data;
   ```
Possible return results:
   ```
   kind | name                  | shared_on
   -----|-----------------------|----------
   table  | financial.transactions  | 2022-02-01 11:15:00
   view   | financial.revenue_summary | 2022-02-02 16:45:00
   ```
By the above example, users can understand how to use the `DESC SHARE` statement to query detailed information about shared data objects and perform corresponding operations based on actual needs.