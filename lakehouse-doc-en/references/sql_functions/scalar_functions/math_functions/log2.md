### LOG2 
```sql
log2(expr)
```
#### Function Description
The LOG2 function is used to calculate the base-2 logarithm of a given value expr. This function has wide applications in computer science, information theory, and other fields, such as calculating the number of bits in a binary number or evaluating information entropy.

#### Parameter Description
* expr (double type): The value for which the logarithm needs to be calculated.

#### Return Result
Returns the base-2 logarithm of expr, with the result being of double type.

####  Example
1. Calculate the base-2 logarithm of 2:
```sql
SELECT log2(2); -- Result is 1.0
```
2. Calculate the base-2 logarithm of 8:
```sql
SELECT log2(8); -- Result is 3.0
```
3. Calculate the base-2 logarithm of 1024:
```sql
SELECT log2(1024); -- Result is 10.0
```
#### Notes
* When expr is a negative number or non-numeric, the LOG2 function will return NULL.