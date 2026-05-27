### TGAMMA Function

#### Description

The TGAMMA function computes the value of the Gamma function (Γ function). The mathematical definition of the Gamma function is:

Γ(x) = ∫₀^∞ t^(x-1) e^(-t) dt

The Gamma function is the generalization of the factorial to the real and complex number domains. For positive integers n, Γ(n) = (n-1)!. This function is widely used in probability theory, statistics, combinatorics, and physics.

#### Syntax

`tgamma(expr)`

#### Parameters

* `expr`: A numeric expression for which to compute the Gamma function value. Supports numeric types (implicitly castable to DOUBLE).

#### Returns

The return type is DOUBLE, representing the Gamma function value corresponding to the input.

#### Examples

1. Compute the Gamma value for a positive integer (Γ(5) = 4! = 24):

    ```sql
    SELECT tgamma(5) AS res;
    +-----+
    | res |
    +-----+
    | 24  |
    +-----+
    ```

2. Compute Γ(1):

    ```sql
    SELECT tgamma(1) AS res;
    +-----+
    | res |
    +-----+
    | 1   |
    +-----+
    ```

3. Compute the Gamma value for a non-integer argument (Γ(0.5) = √π):

    ```sql
    SELECT CAST(tgamma(0.5) AS decimal(18, 10)) AS res;
    +--------------+
    |     res      |
    +--------------+
    | 1.7724538509 |
    +--------------+
    ```

4. When the input is NULL:

    ```sql
    SELECT tgamma(NULL) AS res;
    +------+
    | res  |
    +------+
    | NULL |
    +------+
    ```

#### Notes

* When the input parameter is NULL, the result is NULL.
* For zero and negative integers (0, -1, -2, ...), the Gamma function is undefined, and the return value is Infinity or NaN (CASTing such results to decimal yields NULL).
* For positive integers n, Γ(n) = (n-1)!, e.g., Γ(5) = 24, Γ(1) = 1.
* Γ(0.5) = √π ≈ 1.7724538509, a classic special value of the Gamma function.
* When the input value is very large, the result may overflow to Infinity.
