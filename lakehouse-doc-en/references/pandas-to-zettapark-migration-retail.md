# pandas → ZettaPark Migration in Practice: Retail Data Analysis

GitHub: [pandas2lakehouse-retail](https://github.com/clickzetta/pandas2lakehouse-retail)

## Original Project

Data source: [UCI Online Retail II Dataset](https://archive.ics.uci.edu/dataset/502/online+retail+ii) — real transaction records from a UK retailer covering 2009–2011.

| Metric | Value |
|--------|-------|
| Raw rows | 1,067,371 |
| Rows after cleaning | 805,549 |
| Customers | 5,878 |
| Time span | Dec 2009 – Dec 2011 (25 months) |
| Key fields | Invoice, StockCode, Quantity, InvoiceDate, Price, Customer ID, Country |

The pandas scripts implement three analysis scenarios:

1. **Extended RFM**: Purchase interval P25/P50/P75, longest churn period, days from first to repeat purchase
2. **Weekly cohort retention**: Group by first-purchase week, track retention rate for each subsequent week
3. **Market basket analysis**: Find product pairs frequently purchased together in the same order, compute support and lift

## Conclusion First

You don't need to learn a new toolset or rewrite existing scripts from scratch. pandas code serves directly as the migration blueprint — analytical logic, metric definitions, and segmentation rules are all preserved. Only the data reading method and a handful of APIs need replacing.

| Scenario | pandas time | pandas peak memory | ZettaPark time | ZettaPark local memory |
|----------|------------|-------------------|----------------|------------------------|
| Extended RFM | 8.2s | 203 MB | 3.2s | 0 |
| Weekly cohort | 9.4s | 236 MB | 5.9s | 0 |
| Market basket analysis (self-join) | 9.3s | 2203 MB | 3.2s | 0 |

The market basket analysis is the scenario that best illustrates the difference: the self-join produces intermediate results that push pandas peak memory to **2203 MB** — doubling the data volume would cause OOM. ZettaPark processes everything server-side, keeping local memory at 0 throughout.

## Technology Stack Comparison

| | pandas | ZettaPark |
|---|---|---|
| Runtime | Local Python process | Singdata Lakehouse (cloud) |
| Data reading | `pd.read_csv(path)` | `FROM VOLUME ... USING CSV OPTIONS` |
| Compute engine | Single-machine in-memory | Distributed SQL engine |
| Memory usage | Peak 203–2203 MB (1M rows) | 0 locally (data never lands locally) |
| Result output | `to_csv()` / `to_parquet()` | `write.save_as_table()` |
| Scale limit | Constrained by local memory (self-join scenario 2 GB+, OOM-prone) | Unlimited |

## Project Background

pandas is the tool of choice for data scientists, but it hits two bottlenecks in production:

1. **Memory bottleneck**: 1M rows peaks at 200 MB+; 10M rows easily causes OOM
2. **Scale bottleneck**: Operations like `groupby().apply(shift())` are extremely slow on large datasets

ZettaPark provides a DataFrame API similar to pandas while also supporting `session.sql()` for writing SQL directly, making the migration path very smooth.

## Migration Steps

### Step 1: Replace Data Reading

pandas reads local files directly; ZettaPark reads from a Volume and does not support `inferSchema` — columns must be specified explicitly in SQL.

The raw data has `Customer ID` (with a space). Rename it once in the initial SQL to avoid needing backticks in every subsequent operation.

```python
# pandas
df = pd.read_csv("online_retail_II.csv", parse_dates=["InvoiceDate"])
df = df[~df["Invoice"].astype(str).str.startswith("C")]
df = df.dropna(subset=["Customer ID"])
df = df[df["Quantity"] > 0]
df["Revenue"] = df["Quantity"] * df["Price"]
```

```python
# ZettaPark — reading + cleaning combined into one SQL
df = session.sql("""
    SELECT
        Invoice, StockCode, Description, Quantity, InvoiceDate, Price,
        `Customer ID` AS CustomerID,
        Country
    FROM VOLUME retail_schema.retail_vol
    USING CSV OPTIONS ('header' = 'true', 'nullValue' = '')
    FILES ('raw/online_retail_II.csv')
    WHERE Invoice NOT LIKE 'C%'
      AND `Customer ID` IS NOT NULL
      AND Quantity > 0 AND Price > 0
""")
df = df.with_column("Revenue", F.col("Quantity") * F.col("Price"))
```

### Step 2: Replace Window Functions (Extended RFM)

pandas uses `shift()` to compute intervals between adjacent orders, requiring multiple `groupby + merge` passes with memory peaks 3–4× the data size. ZettaPark uses the `LAG()` window function, completing everything in a single SQL scan.

```python
# pandas — multiple groupby + merge passes
orders["prev_date"] = orders.groupby("Customer ID")["InvoiceDate"].shift(1)
orders["gap_days"] = (orders["InvoiceDate"] - orders["prev_date"]).dt.days
gap_stats = gaps.groupby("Customer ID")["gap_days"].agg(
    gap_p25=lambda x: np.percentile(x, 25),
    gap_p50=lambda x: np.percentile(x, 50),
    gap_p75=lambda x: np.percentile(x, 75),
)
```

```sql
-- ZettaPark — single SQL with LAG + PERCENTILE
WITH with_gaps AS (
    SELECT
        customerid,
        order_date,
        DATEDIFF(DAY,
            LAG(order_date) OVER (PARTITION BY customerid ORDER BY order_date),
            order_date
        ) AS gap_days
    FROM order_level
),
gap_percentiles AS (
    SELECT
        customerid,
        PERCENTILE(gap_days, 0.25) AS gap_p25,
        PERCENTILE(gap_days, 0.50) AS gap_p50,
        PERCENTILE(gap_days, 0.75) AS gap_p75,
        MAX(gap_days)              AS max_gap
    FROM with_gaps
    WHERE gap_days IS NOT NULL
    GROUP BY customerid
)
```

> ⚠️ **Note**: `COUNT(DISTINCT ...)` and `PERCENTILE(...)` cannot coexist in the same `GROUP BY`. Split them into two CTEs (`customer_stats` and `gap_percentiles`).

### Step 3: Replace Self-Join (Market Basket Analysis)

The core of market basket analysis is finding product pairs within the same order, which requires a self-join on `invoice_products`. pandas' `merge(df, df, on="Invoice")` loads all intermediate results into local memory — 1M rows produces about 7.6M intermediate rows, peaking at **2203 MB**. ZettaPark processes everything server-side, keeping local memory at 0.

```python
# pandas — self-join intermediate results all in local memory
invoice_products = df[["Invoice", "StockCode"]].drop_duplicates()
pairs = invoice_products.merge(invoice_products, on="Invoice", suffixes=("_a", "_b"))
pairs = pairs[pairs["StockCode_a"] < pairs["StockCode_b"]]
pair_counts = pairs.groupby(["StockCode_a", "StockCode_b"]).size().reset_index(name="co_count")
# Peak memory 2203 MB — doubling the data volume causes OOM
```

```sql
-- ZettaPark — self-join executes server-side, local memory 0
WITH invoice_products AS (
    SELECT DISTINCT invoice, stockcode FROM retail_clean
),
pairs AS (
    SELECT
        a.stockcode AS stockcode_a,
        b.stockcode AS stockcode_b,
        COUNT(*)    AS co_count
    FROM invoice_products a
    JOIN invoice_products b
      ON a.invoice = b.invoice
     AND a.stockcode < b.stockcode
    GROUP BY a.stockcode, b.stockcode
    HAVING COUNT(*) >= 10
)
```

### Step 4: Replace Date Operations

| pandas | ZettaPark SQL |
|--------|---------------|
| `dt.to_period("W").dt.start_time` | `DATE_TRUNC('week', CAST(col AS DATE))` |
| `(date_a - date_b).dt.days` | `DATEDIFF(DAY, date_b, date_a)` |
| `(week_a - week_b).dt.days // 7` | `DATEDIFF(WEEK, week_b, week_a)` |

> ⚠️ **Note**: In `DATEDIFF(WEEK, ...)`, `WEEK` has no quotes; in `DATE_TRUNC('week', ...)`, `'week'` is quoted.

## What Requires No Changes

The analytical logic itself needs no modification:

- RFM metric definitions (Recency = days since last purchase, Frequency = distinct order count, Monetary = total spend)
- Customer segmentation rules (Champions / Recent Customers / At Risk / Lost)
- Cohort analysis logic (first-purchase week, retention rate = active customers / initial cohort size)
- All aggregation logic (SUM, COUNT DISTINCT, AVG, MIN, MAX)
- Conditional logic (`np.where` → `F.when().otherwise()`, semantically identical)

## Pitfalls Encountered

### 1. inferSchema Not Supported

**Symptom**: `session.read.option("inferSchema", "true").csv(...)` throws an error.

**Cause**: ZettaPark does not support `inferSchema` — columns must be specified explicitly.

**Fix**: Use `session.sql("SELECT ... FROM VOLUME ... USING CSV OPTIONS ...")` and write column names directly in SQL.

### 2. Column Names with Spaces

**Symptom**: `Customer ID` becomes `customer id` (lowercase + space) in the ZettaPark DataFrame, and `F.col("CustomerID")` can't find the column.

**Cause**: ZettaPark converts all column names to lowercase; column names with spaces can't be referenced directly as identifiers.

**Fix**: Use backticks in the initial SQL `SELECT` to reference and rename the column:

```sql
`Customer ID` AS CustomerID
```

### 3. COUNT(DISTINCT) and PERCENTILE Conflict

**Symptom**: Writing both `COUNT(DISTINCT invoice)` and `PERCENTILE(gap_days, 0.5)` in the same `GROUP BY` throws an error.

**Fix**: Split into two CTEs and compute them separately.

### 4. Encoding Issues in the Original Excel File

**Symptom**: The UCI dataset's original format is Excel (`.xlsx`); the `Description` field contains special characters like `£`, which produce invalid UTF-8 after CSV conversion.

**Fix**: Use `errors='replace'` when converting to replace unencodable characters:

```python
df.to_csv("online_retail_II.csv", index=False, encoding="utf-8", errors="replace")
```

## End-to-End Validation

`03_lakehouse/e2e.py` runs 5 automated checks on the full dataset (1.06M rows):

| Check | Expected | Result |
|-------|----------|--------|
| Rows after cleaning | 805,549 | ✓ |
| Customer count | 5,878 | ✓ |
| Segment total = customer count | 5,878 | ✓ |
| Top country | United Kingdom | ✓ |
| Month count | 25 | ✓ |

Actual result: **5/5 passed**, total runtime 12.8s.

## Migration Conclusions

### API-Level Benefits

- `groupby().apply(shift())` → `LAG() OVER (PARTITION BY ...)`: cleaner code, no repeated merges
- `rolling(4).sum()` → `ROWS BETWEEN 3 PRECEDING AND CURRENT ROW`: standard SQL, no set_index needed
- `np.percentile()` → `PERCENTILE(col, 0.25)`: computed directly in SQL, no apply needed
- Multiple groupby + merge passes → single SQL WITH chain: memory peak drops from 200 MB+ to 0

### Deployment-Level Benefits

Migrating from local pandas scripts to Singdata Lakehouse SaaS brings more than just performance gains:

| | pandas (local) | ZettaPark (SaaS) |
|---|---|---|
| Data scale limit | Constrained by local memory (~10M rows OOM) | Unlimited — same code handles PB-scale data |
| Runtime | Requires local Python environment | Cloud execution, no local resources needed |
| Collaboration | Share script files | Results written to shared tables, team queries directly |
| Scheduling | Manual or cron | Built-in platform task scheduling |
| Version management | Manual | Managed automatically by the platform |

After migration, data scientists can shift their focus from "getting pandas to finish" to "making analysis deliver value."

## References

- GitHub: [pandas2lakehouse-retail](https://github.com/clickzetta/pandas2lakehouse-retail)
- [pandas → ZettaPark API Mapping](https://github.com/clickzetta/pandas2lakehouse-retail/blob/main/02_migration/02_api_mapping.md)
- [ZettaPark Developer Guide](lakehousepython-zettapark.md)
