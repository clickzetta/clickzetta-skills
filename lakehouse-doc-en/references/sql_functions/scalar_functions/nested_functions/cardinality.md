### CARDINALITY

####  Description
The `CARDINALITY` function is used to calculate the number of elements in an array and the number of key-value pairs in a map.

#### Syntax
```
CARDINALITY(array)
CARDINALITY(map)
```
#### Parameter Description
- `array`: The input array, with elements of type `T`.
- `map`: The input map, consisting of key type `K` and value type `V`.

#### Return Type
- Returns an integer (`int`), representing the number of elements in the array or the number of key-value pairs in the map.

####  Example
1. Calculate the number of elements in the array:
```
SELECT CARDINALITY(ARRAY(1, 2, 3, 4, 5)); -- Returns 5
```
2. Calculate the number of key-value pairs in the map:
```
SELECT CARDINALITY(MAP("a", 1, "b", 2, "c", 3)); -- Returns 3
```
3. Combine with actual data table operations:
Suppose there is a data table named `students`, with the following table structure:
```
CREATE TABLE students (
  id INT,
  name VARCHAR,
  hobbies ARRAY<VARCHAR>
);
```
To insert a data entry into the `students` table:
```
INSERT INTO students (id, name, hobbies) VALUES (1, 'Alice', ARRAY('reading', 'swimming', 'traveling'));
```
Using the `CARDINALITY` function to calculate the number of hobbies of the student:
```
SELECT CARDINALITY(hobbies) FROM students WHERE id = 1; -- Returns 3
```