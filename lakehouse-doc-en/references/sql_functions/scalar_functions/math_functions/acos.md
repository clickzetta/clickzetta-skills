### ACOS

```sql

acos(expr)

```
#### Function

Calculate the arc cosine value of expr

#### Parameters

* expr: double type, value range is [-1,1], other types will be implicitly converted

#### Return Result

double type

#### Example
```sql
> SELECT acos(-1);
0.0
> SELECT acos(2);

NaN

```