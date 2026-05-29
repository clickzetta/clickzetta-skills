### MAKE_DATE
```sql
make_date(year, month, day)
```

#### Function
Constructs a date type from the given year, month, and day.

#### Parameters
- `year`: int
- `month`: int
- `day`: int

#### Return Value
- `date`

#### Example
```sql
> SELECT make_date(2000, 2, 28);
2000-02-28
```