### LOG10 
```sql
LOG10(expr)
```
####  Description
The LOG10 function is used to calculate the base-10 logarithm of a given numerical expression `expr`. This function is very useful when dealing with exponential data, as it can help quickly understand the growth rate and scale of the data.

#### Parameter Description
* expr (double type): The numerical expression for which the logarithm needs to be calculated.

#### Return Result
Returns the calculation result as a double type.

#### Usage Example
1. Calculate the base-10 logarithm of 100:
```sql
SELECT LOG10(100);
```
Results:
```
2.0
```
2. Calculate the base-10 logarithm of 1000 and compare it with common logarithms:
```sql
SELECT LOG10(1000);
```
Results:
```
3.0
```
3. Calculate the base-10 logarithm of different values and observe the changes in the logarithm values:
```sql
SELECT LOG10(1), LOG10(10), LOG10(100), LOG10(1000);
```
Results:
```
0.0 1.0 2.0 3.0
```
4. Calculate the base-10 logarithm of consecutive integers to understand the rate of numerical growth:
```sql
SELECT LOG10(1), LOG10(10), LOG10(100), LOG10(1000), LOG10(10000);
```
Results:
```
0.0 1.0 2.0 3.0 4.0
```
By the above example, it can be observed that as the value increases, the logarithm base 10 of the value also increases. The LOG10 function has a wide range of applications in data analysis and processing, helping users quickly understand the scale and growth rate of the data.