### CBRT 
#### Description
The CBRT function is used to calculate the cube root of a given value. This function accepts a parameter of type double and returns a calculation result of type double.

#### Syntax
```
CBRT(expr)
```
#### Parameters
- `expr`: The double type value for which the cube root needs to be calculated.

#### Return Result
Returns the cube root of the parameter `expr`, with the result type being double.

#### Example Usage
1. Calculate the cube root of 27:
```
SELECT CBRT(27.0);
```
Results:
```
3.0000000000000004
```
2. Calculate the cube root of a negative number (e.g., -8):
```
SELECT CBRT(-8.0);
```
Results:
```
-2.0
```
3. Calculate the cube root of a decimal number (e.g., 0.027):
```
SELECT CBRT(0.027);
```
Results:
```
0.29999999999999993
```
4. Calculate the cube root of a larger number (for example, 1000000):
```
SELECT CBRT(1000000);
```
Results:
```
100.0
```
5. Calculate the cube roots of multiple values in a single query:
```
SELECT CBRT(27.0), CBRT(64.0), CBRT(-125.0);
```
Results:
```
3.0000000000000004, 4.0, -5.0
```
From the above example, it can be seen that the CBRT function can be flexibly applied to various scenarios, helping users quickly calculate the cube root of the required value.