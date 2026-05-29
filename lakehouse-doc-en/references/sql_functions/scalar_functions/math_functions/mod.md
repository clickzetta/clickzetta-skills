### MOD 

####  Description
The MOD function is used to calculate the remainder of the division of two numeric expressions. This function supports various data types, including integers and decimals.

#### Supported Parameter Types
* expr1: Supported data types include float, double, decimal, tinyint, smallint, int, bigint.
* expr2: Same type as expr1.

#### Return Result
The return type is the same as the input parameter type.

#### Usage Example
```sql
-- Calculate the remainder of 2 divided by 1.8
SELECT MOD(2, 1.8); -- Result is 0.2

-- Calculate the remainder of -10 divided by 3
SELECT MOD(-10, 3); -- Result is -1

-- Calculate the remainder of two integer types
SELECT MOD(17, 5); -- Result is 2

-- Calculate the remainder of decimal types
SELECT MOD(12.34, 4.56); -- Result is 3.22

-- Calculate the remainder of decimal type
SELECT MOD(10.50, 3.14); -- Result is 1.08
```
#### Notes
* When expr2 is 0, the result of the MOD function is undefined and may cause errors or exceptions.
* The result of the MOD function may be negative, depending on the signs of expr1 and expr2. If you need to ensure the result is positive, you can use the ABS function to process the result.

With the above examples and explanations, you can better understand and use the MOD function to handle your data calculation needs.