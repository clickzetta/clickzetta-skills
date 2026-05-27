### MAKE_DATE
```sql
make_date(year, month, day)
```
#### Description
Constructs a date value from year, month, and day.

#### Parameters
* `year`: int
* `month`: int
* `day`: int

#### Returns
date type

#### Examples
```sql
> SELECT make_date(2000, 2, 28);
2000-02-28
```
