### ERF Function

#### Description

The ERF function computes the Gauss error function value. The mathematical definition of the Gauss error function is:

erf(x) = (2/√π) ∫₀ˣ e^(-t²) dt

This function is widely used in probability theory, statistics, and partial differential equations, commonly employed to describe the cumulative distribution function of the normal distribution.

#### Syntax

`erf(expr)`

#### Parameters

* `expr`: A numeric expression for which to compute the error function value. Supports numeric types (implicitly castable to DOUBLE).

#### Returns

The return type is DOUBLE, representing the error function value corresponding to the input. The return value range is [-1, 1].

#### Examples

1. Compute erf(0):

    ```sql
    SELECT erf(0) AS res;
    +-----+
    | res |
    +-----+
    | 0   |
    +-----+
    ```

2. Compute erf(1):

    ```sql
    SELECT erf(1) AS res;
    +--------------------+
    |        res         |
    +--------------------+
    | 0.8427007929497149 |
    +--------------------+
    ```

3. Compute the error function value for a negative number (erf is an odd function, erf(-x) = -erf(x)):

    ```sql
    SELECT erf(-1) AS res;
    +---------------------+
    |         res         |
    +---------------------+
    | -0.8427007929497149 |
    +---------------------+
    ```

4. When the input is NULL:

    ```sql
    SELECT erf(NULL) AS res;
    +------+
    | res  |
    +------+
    | NULL |
    +------+
    ```

#### Notes

* When the input parameter is NULL, the result is NULL.
* The return value range of erf is [-1, 1]. As x → +∞, erf(x) → 1; as x → -∞, erf(x) → -1.
* erf is an odd function, i.e., erf(-x) = -erf(x), and erf(0) = 0.
* This function is often used in conjunction with normal distribution calculations, e.g., the cumulative distribution function of the standard normal distribution Φ(x) = (1 + erf(x/√2)) / 2.
