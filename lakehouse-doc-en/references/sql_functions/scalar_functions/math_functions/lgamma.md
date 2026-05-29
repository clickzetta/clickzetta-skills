### LGAMMA Function

#### Description

The LGAMMA function computes the natural logarithm of the absolute value of the Gamma function (Log-Gamma function). Its mathematical definition is:

lgamma(x) = ln(|Γ(x)|)

where Γ(x) is the Gamma function. The Log-Gamma function is very useful for computations involving large-number factorials, because directly computing the Gamma function value may cause numeric overflow, whereas taking the logarithm allows safe computation over a much larger numeric range.

#### Syntax

`lgamma(expr)`

#### Parameters

* `expr`: A numeric expression for which to compute the Log-Gamma function value. Supports numeric types (implicitly castable to DOUBLE).

#### Returns

The return type is DOUBLE, representing the ln(|Γ(x)|) value corresponding to the input.

#### Examples

1. Compute lgamma(1) (ln(|Γ(1)|) = ln(1) = 0):

    ```sql
    SELECT lgamma(1) AS res;
    +-----+
    | res |
    +-----+
    | 0   |
    +-----+
    ```

2. Compute lgamma(5) (ln(|Γ(5)|) = ln(4!) = ln(24) ≈ 3.178):

    ```sql
    SELECT CAST(lgamma(5) AS decimal(18, 10)) AS res;
    +--------------+
    |     res      |
    +--------------+
    | 3.1780538303 |
    +--------------+
    ```

3. Compute the Log-Gamma value for a non-integer argument (lgamma(0.5) = ln(√π)):

    ```sql
    SELECT CAST(lgamma(0.5) AS decimal(18, 10)) AS res;
    +--------------+
    |     res      |
    +--------------+
    | 0.5723649429 |
    +--------------+
    ```

4. When the input is NULL:

    ```sql
    SELECT lgamma(NULL) AS res;
    +------+
    | res  |
    +------+
    | NULL |
    +------+
    ```

#### Notes

* When the input parameter is NULL, the result is NULL.
* For zero and negative integers (0, -1, -2, ...), the Gamma function is undefined (tends to infinity), and lgamma returns Infinity (CASTing such results to decimal yields NULL).
* For positive integers n, lgamma(n) = ln((n-1)!), e.g., lgamma(5) = ln(24) ≈ 3.178, lgamma(1) = 0, lgamma(2) = 0.
* Relationship between lgamma and tgamma: lgamma(x) = ln(|tgamma(x)|). When the result of tgamma(x) is very large (e.g., for large arguments), using tgamma directly may overflow to Infinity, whereas lgamma can still return a valid result, making it suitable for large-number factorial computations.
* lgamma(0.5) = ln(√π) ≈ 0.5724, a classic special value of the Log-Gamma function.
