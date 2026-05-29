# VARCHAR(n)

The variable-length character type (VARCHAR) is a data type that can store variable-length string data. This type allocates space based on the actual content length when storing strings, thereby effectively saving storage space. The length range of VARCHAR type strings is from 1 to 65535 characters.

## Syntax
```
VARCHAR(n)
```
Among them, n represents the maximum length of the string, with a value range of 1 to 1048576.

## Example

1. Create a VARCHAR type table:
   ```
   CREATE TABLE example_table (
       id INT PRIMARY KEY,
       name VARCHAR(50),
       age INT
   );
   ```
In this example, we create a table named `example_table` with three fields: `id` (integer type, primary key), `name` (variable-length character type, maximum length of 50 characters), and `age` (integer type).

2. Insert data into a VARCHAR type field:
```
INSERT INTO example_table (id, name, age) VALUES (1, 'John', 25);
```
In this example, we insert a piece of data into the example_table, where the value of the name field is 'John', with a length of 3 characters.

3. Query data of VARCHAR type field:
   ```
   SELECT name FROM example_table;
   ```
In this example, we query the data of the name field in the example_table table.