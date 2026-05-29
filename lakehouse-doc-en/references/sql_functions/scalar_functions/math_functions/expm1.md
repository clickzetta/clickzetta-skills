### EXPM1

#### Description
The `expm1` function is used to calculate the value of `exp(expr)-1`, where `expr` is a double type parameter. This function can avoid numerical overflow or precision issues that may occur when directly calculating `exp(x)`, and is particularly suitable for calculating smaller exponential values.

#### Functionality
This function calculates the value of `e` raised to the power of `expr` minus 1, where `e` is the base of the natural logarithm (approximately equal to 2.71828). This calculation method has advantages in numerical stability, especially when dealing with exponential values close to zero.

#### Parameters
- `expr` (double type): The value for which the exponential complement needs to be calculated.

#### Return Value
Returns a double type value representing the result of `exp(expr)-1`.

#### Usage Example
Here are some examples of using the `expm1` function:

1. Calculate the value of `exp(1)-1`:
   ```sql
   SELECT expm1(1);
   ```
Result:
   ```
   1.718281828459045
   ```
2. Calculate the value of `exp(0.5)-1`:
   ```sql
   SELECT expm1(0.5);
   ```
Result:
   ```
   0.6487212707001282
   ```
3. Calculate the value of `exp(-1)-1`:
   ```sql
   SELECT expm1(-1);
   ```
Result:
   ```
   -0.6321205588285577
   ```
4. Calculate the values of a series of exponential complements:
   ```sql
   SELECT expm1(-0.1), expm1(0), expm1(0.1), expm1(1);
   ```
Result:
   ```
   -0.09516258196404043, 0, 0.10517091807564763, 1.718281828459045
   ```