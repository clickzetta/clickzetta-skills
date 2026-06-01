# RDD → ZettaPark Migration in Practice: Web Log Analysis

If your Spark code is still in the RDD era, the benefits of migrating to ZettaPark are greater than you might expect. It's not just an API swap — the imperative style of RDD (telling Spark how to do it) is replaced by a declarative style (telling Lakehouse what you want), resulting in less code, better execution efficiency, and improved readability.

This article validates this with a real project: migrating a PySpark RDD-based web log analysis project to Singdata Lakehouse, covering 9 migration patterns, verified by 18 automated checks — all passing.

Full code on GitHub: [spark2lakehouse-weblog](https://github.com/clickzetta/spark2lakehouse-weblog)

---

## The Original Project

[spark2lakehouse-weblog](https://github.com/clickzetta/spark2lakehouse-weblog) is forked from [XD-DENG/Spark-practice](https://github.com/XD-DENG/Spark-practice) (272 stars), a classic PySpark RDD introductory tutorial. It uses real download logs from the RStudio CRAN mirror as the dataset, demonstrating core RDD operations including `map`, `filter`, `reduceByKey`, `sortBy`, `join`, and `aggregateByKey`.

Dataset: R package download records from December 12, 2015 — 421,969 rows, 8,659 unique package names, 237 countries.

| Field | Description |
|------|------|
| date / time | Download timestamp |
| size | File size (bytes) |
| r_version / r_arch / r_os | R runtime environment |
| package / version | R package name and version |
| country / ip_id | Source country and anonymized IP |

---

![](.topwrite/assets/anim-07-rdd-migration.svg)

---

## Why RDD Code Is Worth Migrating

RDD is Spark's earliest programming model and was the mainstream approach before the DataFrame API appeared (Spark 1.x era). A large amount of legacy RDD code is still running in production environments.

**The problem with RDD is not functionality, but expression.** Writing "count downloads per package" in RDD requires:

```python
content.map(lambda x: (x[6], 1)).reduceByKey(lambda a, b: a + b)
```

This code tells Spark how to do it (map to key-value pairs, then reduce), rather than what you want (group by package name and count). As logic grows more complex, RDD code becomes increasingly hard to read and optimize.

The declarative ZettaPark equivalent:

```python
df.group_by("package").agg(F.count("*").alias("downloads"))
```

This directly expresses intent, and the execution plan is determined by the Lakehouse optimizer.

---

## Migration Conclusions Up Front

You won't lose any analytical capability — your code will actually get shorter. RDD requires telling the engine *how* to do it; ZettaPark only needs you to say *what* you want. The business logic stays the same, but a 6-step secondary sort becomes a single window function, and a hand-written cogroup iterator becomes a HAVING clause.

| RDD Operation | ZettaPark Equivalent | Code Volume Change |
|---------|---------------|-----------|
| `sc.textFile` + `map(split)` | `session.read.csv()` | Reduced |
| `map(lambda x: (x[6], 1)).reduceByKey(+)` | `group_by().agg(F.count("*"))` | Comparable |
| `aggregateByKey((0,0), seq_op, comb_op)` | `group_by().agg(F.avg())` | Greatly reduced |
| `rdd1.join(rdd2)` | `group_by().agg(count, avg)` | Reduced (merged into a single scan) |
| `.filter(lambda x: x[3] != "NA")` | `.filter(F.col("r_version") != "NA")` | Comparable |
| `.distinct().count()` | `F.count_distinct("package")` | Reduced |
| `.sortBy(lambda x: x[1], ascending=False)` | `.sort(F.col("downloads").desc())` | Comparable |
| `mapPartitions` + `accumulator` | `COUNT(CASE WHEN ...)` | Reduced (no partition awareness needed) |
| `cogroup` + hand-written iterator filter | `GROUP BY ... HAVING` | Greatly reduced |
| 6-step secondary sort (groupByKey + flatMap) | `RANK() OVER (PARTITION BY ...)` | Greatly reduced |
| `sc.broadcast(dict)` + `.value.get()` | `LEFT JOIN` small table | Reduced (optimizer auto-broadcasts) |

---

## 9 Migration Patterns

### Pattern 1: Data Loading

RDD requires manually reading the file, skipping the header, and splitting each line:

RDD version:
```python
raw_content = sc.textFile("2015-12-12.csv")
header = raw_content.first()
content = (
    raw_content
    .filter(lambda x: x != header)
    .map(lambda x: [field.strip('"') for field in x.split(",")])
)
```

ZettaPark has built-in CSV parsing with automatic header handling:

ZettaPark version:
```python
df = session.read.option("header", "true").csv("vol://public.weblog_vol/2015-12-12.csv")
```

### Pattern 2: Count Aggregation (reduceByKey)

This is the most common pattern in RDD code — map to `(key, 1)` pairs, then reduceByKey to sum:

RDD version:
```python
package_count = (
    content
    .map(lambda x: (x[6], 1))
    .reduceByKey(lambda a, b: a + b)
    .sortBy(lambda x: x[1], ascending=False)
)
top10 = package_count.take(10)
```

ZettaPark expresses this directly with `group_by().agg()`:

ZettaPark version:
```python
top10 = (
    df
    .group_by("package")
    .agg(F.count("*").alias("downloads"))
    .sort(F.col("downloads").desc())
    .limit(10)
)
top10.show()
```

### Pattern 3: Average Aggregation (aggregateByKey → F.avg)

This is where **code volume is reduced the most** in RDD migration. RDD has no built-in avg, so you have to write an accumulator manually:

RDD version:
```python
def seq_op(acc, val):
    return (acc[0] + int(val), acc[1] + 1)

def comb_op(a, b):
    return (a[0] + b[0], a[1] + b[1])

pkg_avg_size = (
    content
    .filter(lambda x: x[2].isdigit())
    .map(lambda x: (x[6], x[2]))
    .aggregateByKey((0, 0), seq_op, comb_op)
    .map(lambda x: (x[0], x[1][0] // x[1][1]))
    .sortBy(lambda x: x[1], ascending=False)
)
```

ZettaPark uses the built-in `F.avg()` — done in one line:

ZettaPark version:
```python
top10_by_size = (
    df
    .filter(F.col("size").is_not_null())
    .group_by("package")
    .agg(F.avg("size").alias("avg_size_bytes"))
    .sort(F.col("avg_size_bytes").desc())
    .limit(10)
)
```

### Pattern 4: Two RDD Joins → Single GROUP BY

The original code splits counting and summing into two RDDs and then joins them, to demonstrate RDD join:

RDD version:
```python
pkg_count_rdd = content.map(lambda x: (x[6], 1)).reduceByKey(lambda a, b: a + b)
pkg_size_rdd  = (
    content
    .filter(lambda x: x[2].isdigit())
    .map(lambda x: (x[6], int(x[2])))
    .reduceByKey(lambda a, b: a + b)
)
pkg_joined = pkg_count_rdd.join(pkg_size_rdd)
pkg_summary = pkg_joined.map(lambda x: (x[0], x[1][0], x[1][1] // x[1][0]))
```

ZettaPark completes this with a single GROUP BY, scanning the data once:

ZettaPark version:
```python
pkg_summary = (
    df
    .filter(F.col("size").is_not_null())
    .group_by("package")
    .agg(
        F.count("*").alias("downloads"),
        F.avg("size").alias("avg_size_bytes"),
    )
    .sort(F.col("downloads").desc())
    .limit(5)
)
```

### Pattern 5: Distinct Count

RDD version:
```python
unique_packages = content.map(lambda x: x[6]).distinct().count()
```

ZettaPark version:
```python
unique_count = df.select(F.count_distinct("package").alias("unique_packages"))
unique_count.show()
```

### Pattern 6: mapPartitions + accumulator → COUNT(CASE WHEN)

`mapPartitions` is RDD's batch processing primitive: it receives an iterator for an entire partition at once, reducing function call overhead compared to row-by-row `map`. It is suitable for batch validation. `accumulator` is a shared counter on the driver side — executors can only `.add()`, and the driver reads `.value`. **Note: accumulators are only guaranteed to be accurate after an action is triggered.**

RDD version:
```python
bad_row_acc = sc.accumulator(0)

def validate_partition(rows):
    for row in rows:
        size_ok    = row[2].isdigit() and int(row[2]) > 0
        country_ok = len(row) > 8 and row[8].strip() != ""
        if size_ok and country_ok:
            yield row
        else:
            bad_row_acc.add(1)

valid_content = content.mapPartitions(validate_partition)
valid_count   = valid_content.count()   # accumulator is accurate only after action is triggered
bad_count     = bad_row_acc.value
```

ZettaPark uses `COUNT(CASE WHEN ...)` in a single scan — no partition awareness needed, no accumulator:

ZettaPark version:
```python
session.sql("""
    SELECT
        COUNT(CASE WHEN size > 0
                        AND country IS NOT NULL
                        AND country != ''
                   THEN 1 END)                                      AS valid_rows,
        COUNT(*) - COUNT(CASE WHEN size > 0
                               AND country IS NOT NULL
                               AND country != ''
                          THEN 1 END)                               AS invalid_rows
    FROM weblog.cran_downloads
""").show()
```

| Dimension | RDD | ZettaPark |
|------|-----|-----------|
| Partition awareness | Required (mapPartitions receives partition iterator) | Not needed (optimizer determines execution plan) |
| Bad row count | accumulator (driver/executor separation) | COUNT(*) - COUNT(CASE WHEN ...) |
| Code volume | ~15 lines (including accumulator declaration) | ~8 lines of SQL |

### Pattern 7: cogroup → HAVING Multi-Condition Aggregation

`cogroup` is a generalization of RDD join: it does not drop keys even when one side has no data (similar to full outer join). Both side iterators are lazy — **you must `list()` them to iterate more than once**. The scenario here is finding packages with "downloads ≥ 100 and average size ≥ 1MB".

RDD version:
```python
pkg_count_for_cg = content.map(lambda x: (x[6], 1)).reduceByKey(lambda a, b: a + b)
pkg_sizes_for_cg = (
    content
    .filter(lambda x: x[2].isdigit())
    .map(lambda x: (x[6], int(x[2])))
    .groupByKey()
)

def is_high_traffic_high_volume(item):
    pkg, (count_iter, size_iter) = item
    counts = list(count_iter)   # lazy iterator must be list() to iterate more than once
    sizes  = list(size_iter)
    if not counts or not sizes:
        return False
    total_count = counts[0]
    all_sizes   = [s for sublist in sizes for s in sublist]
    if total_count < 100 or not all_sizes:
        return False
    avg_size = sum(all_sizes) / len(all_sizes)
    return avg_size >= 1_048_576

high_vol_pkgs = (
    pkg_count_for_cg
    .cogroup(pkg_sizes_for_cg)
    .filter(is_high_traffic_high_volume)
    .map(lambda item: item[0])
    .collect()
)
```

ZettaPark uses `HAVING` to constrain both COUNT and AVG simultaneously, and the optimizer merges them into a single aggregation. The "two-sided data structure" of cogroup naturally disappears in SQL:

ZettaPark version:
```python
session.sql("""
    SELECT package, COUNT(*) AS downloads, AVG(size) AS avg_size_bytes
    FROM weblog.cran_downloads
    WHERE size IS NOT NULL
    GROUP BY package
    HAVING COUNT(*) >= 100
       AND AVG(size) >= 1048576
    ORDER BY downloads DESC
""").show()
```

Result: 102 packages meet the criteria (downloads ≥ 100 and average size ≥ 1MB).

### Pattern 8: Secondary Sort → Window Functions

This is the most compelling migration case in this article. Scenario: find the Top 3 most downloaded packages per country.

RDD has no "sort within group" primitive and requires 6 manual steps:

RDD version (6 steps):
```python
def top3_with_rank(item):
    country, pkg_counts = item
    sorted_pkgs = sorted(pkg_counts, key=lambda x: x[1], reverse=True)[:3]
    return [(country, pkg, rank, count)
            for rank, (pkg, count) in enumerate(sorted_pkgs, start=1)]

top3_per_country = (
    content
    .map(lambda x: ((x[8], x[6]), 1))           # Step 1: key=(country,pkg)
    .reduceByKey(lambda a, b: a + b)              # Step 1: count downloads
    .map(lambda x: (x[0][0], (x[0][1], x[1])))   # Step 2: rekey → country
    .groupByKey()                                  # Step 2: aggregate all (pkg,count) for same country
    .flatMap(top3_with_rank)                       # Step 3: Top 3 within group + rank
    .sortBy(lambda x: (x[0], x[2]))               # Step 4: sort by (country, rank)
)
```

`groupByKey` pulls all values for the same key into a single executor's memory. For very large datasets, you can use `repartitionAndSortWithinPartitions` instead — constructing a composite key `(country, -count)`, partitioning by country, sorting within partitions by `-count` ascending (i.e., count descending), and then still needing to write rank logic manually. This is exactly why RDD secondary sort is so cumbersome: there is no `PARTITION BY` semantics, and everything must be implemented by hand.

ZettaPark uses 2-layer CTE + `RANK() OVER (PARTITION BY ...)` to express this directly:

ZettaPark version:
```python
session.sql("""
    WITH pkg_country_counts AS (
        SELECT country, package, COUNT(*) AS downloads
        FROM weblog.cran_downloads
        GROUP BY country, package
    ),
    ranked AS (
        SELECT country, package, downloads,
               RANK() OVER (PARTITION BY country ORDER BY downloads DESC) AS rnk
        FROM pkg_country_counts
    )
    SELECT country, package, downloads, rnk
    FROM ranked
    WHERE rnk <= 3
    ORDER BY country, rnk
""").show(20)
```

Comparison:

| Dimension | RDD | ZettaPark |
|------|-----|-----------|
| Steps | 6 steps: map / reduceByKey / map / groupByKey / flatMap / sortBy | 2-layer CTE + WHERE rnk <= 3 |
| Memory pressure | groupByKey pulls all data for the same country to a single executor | Optimizer decides — no manual control needed |
| Large dataset approach | repartitionAndSortWithinPartitions (requires manual rank logic) | Same SQL, optimizer handles automatically |
| Code volume | ~15 lines (including helper function) | ~10 lines of SQL |

Result: 1,255 rows (including RANK ties), US Top 1 is Rcpp (2,042 downloads).

### Pattern 9: Broadcast Variable → JOIN Small Table

`sc.broadcast()` serializes a small table once and sends it to each executor node's cache, avoiding per-task serialization overhead. Suitable for tables up to a few MB. Call `.unpersist()` afterward to proactively release executor memory.

RDD version:
```python
import csv as csv_module

region_map_data = {}
with open("sample_data/country_region.csv") as f:
    reader = csv_module.DictReader(f)
    for row in reader:
        region_map_data[row["country"]] = row["region"]

region_bc = sc.broadcast(region_map_data)

region_count = (
    content
    .map(lambda x: (region_bc.value.get(x[8], "Other"), 1))
    .reduceByKey(lambda a, b: a + b)
    .sortBy(lambda x: x[1], ascending=False)
)

for region, cnt in region_count.collect():
    print(f"  {region}: {cnt:,}")

region_bc.unpersist()
```

ZettaPark uses `LEFT JOIN` on the small table, and the optimizer automatically identifies the small table and performs a broadcast join (equivalent to manual RDD broadcast). `COALESCE` handles unmatched country codes, equivalent to `.get(key, "Other")`:

ZettaPark version:
```python
session.sql("""
    SELECT
        COALESCE(cr.region, 'Other') AS region,
        COUNT(*)                     AS downloads
    FROM weblog.cran_downloads d
    LEFT JOIN weblog.country_region cr ON d.country = cr.country
    GROUP BY COALESCE(cr.region, 'Other')
    ORDER BY downloads DESC
""").show()
```

Result: Americas 164,615 downloads (Top 1), Asia 153,772 downloads.

---

## RDD Operations That Are Not Worth Migrating

The original project contains several RDD operations that demonstrate API features without corresponding real business queries. These do not need equivalent implementations in the ZettaPark version:

| RDD Operation | Reason | ZettaPark Handling |
|---------|------|------------------|
| `raw_content.union(raw_content)` | Demonstrates union semantics, no business meaning | Not migrated |
| `raw_content.intersection(raw_content)` | Demonstrates intersection, no business meaning | Not migrated |
| `cache()` / `persist()` | ZettaPark execution plans are managed by the optimizer | Manual caching not needed |
| `cartesian()` | Cartesian product demonstration, no corresponding business need | Not migrated |

**Decision criterion**: If an RDD operation corresponds to a real business question ("how many times was each package downloaded"), migrate it. If it only demonstrates an API feature ("union an RDD with itself"), don't migrate it.

---

## End-to-End Validation

After migration, use 18 automated checks to verify data correctness:

```bash
python e2e.py
```

Validation coverage:

1. **Total row count**: 421,969 rows
2. **Top package name**: Rcpp (4,783 downloads)
3. **Top package download count**: 4,783
4. **Top country**: US
5. **Top R version**: 3.2.3
6. **Unique package count**: 8,659
7. **Average size > 0**: Business reasonableness check
8. **OS type count**: 20 non-NA operating systems
9. **Join result top package**: Consistent with Q1
10. **Q8 valid row count**: 421,969 (no bad rows in full dataset)
11. **Q8 invalid row count**: 0
12. **Q9 high-traffic high-volume package count**: 102 (downloads ≥ 100 and average size ≥ 1MB)
13. **Q10 US Top 1 package name**: Rcpp
14. **Q10 US Top 1 download count**: 2,042
15. **Q10 total result rows**: 1,255 (including RANK ties)
16. **Q11 top region**: Americas
17. **Q11 Americas download count**: 164,615
18. **Q11 Asia download count**: 153,772

Actual run result: **18/18 all passed**.

---

## Full Compatibility Comparison

| Operation | RDD | ZettaPark | Status |
|------|-----|-----------|------|
| Data loading | `sc.textFile` + `map(split)` | `session.read.csv()` | ✅ More concise |
| Count aggregation | `map(k,1).reduceByKey(+)` | `group_by().agg(count)` | ✅ Fully equivalent |
| Average | `aggregateByKey` + manual accumulator | `group_by().agg(F.avg())` | ✅ Greatly simplified |
| Filter | `.filter(lambda x: x[3] != "NA")` | `.filter(F.col("r_version") != "NA")` | ✅ Fully equivalent |
| Sort | `.sortBy(lambda x: x[1], False)` | `ORDER BY ... DESC` | ✅ Fully equivalent |
| Distinct count | `.distinct().count()` | `F.count_distinct()` | ✅ More concise |
| Join | `rdd1.join(rdd2)` | `group_by().agg(count, avg)` | ✅ Merged into single scan |
| Take top N | `.take(10)` | `.limit(10).collect()` | ✅ Fully equivalent |
| Print results | `print(rdd.take(10))` | `df.show()` | ✅ More user-friendly |
| Batch validation | `mapPartitions` + `accumulator` | `COUNT(CASE WHEN ...)` | ✅ Single scan, no partition awareness needed |
| Multi-condition aggregation filter | `cogroup` + hand-written iterator | `GROUP BY ... HAVING` | ✅ Greatly simplified |
| Sort within group | 6 steps (groupByKey + flatMap + sortBy) | `RANK() OVER (PARTITION BY ...)` | ✅ 60% less code |
| Small table broadcast | `sc.broadcast(dict)` + `.value.get()` | `LEFT JOIN` small table | ✅ Optimizer auto-broadcasts |

---

## Migration Conclusions

The core change in migrating from RDD to ZettaPark is **from imperative to declarative**: instead of telling the engine how to do it, you tell it what you want.

**Where code volume is reduced the most**:
- `aggregateByKey` replaced by `F.avg()`
- Two RDD joins merged into a single `group_by().agg()`
- 6-step secondary sort replaced by `RANK() OVER (PARTITION BY ...)`
- `cogroup` + hand-written iterator replaced by `HAVING` multi-condition aggregation

**Fully equivalent operations**: `filter`, `sortBy`, `take`, `distinct` — these operations are semantically identical, just with more concise syntax.

**Advanced patterns yield greater migration benefits**: Advanced RDD operations like `mapPartitions`, `cogroup`, secondary sort, and broadcast variables all have more direct SQL equivalents, and you no longer need to manually manage partitions, iterators, or broadcast lifecycles.

**Operations that don't need to be migrated**: Demonstrative set operations (union/intersection with self), manual caching (cache/persist) — these are either unnecessary in ZettaPark or handled automatically by the optimizer.

This project passed 18/18 validations, proving that RDD business logic can be fully migrated to ZettaPark with cleaner code and better execution efficiency.

---

## References

- GitHub project: [spark2lakehouse-weblog](https://github.com/clickzetta/spark2lakehouse-weblog)
- Original project: [XD-DENG/Spark-practice](https://github.com/XD-DENG/Spark-practice)
- PySpark DataFrame migration: [PySpark → ZettaPark Migration in Practice: F1 Racing Data Engineering Project](pyspark-to-zettapark-migration-f1.md)
- Medallion architecture migration: [Building a Medallion Lakehouse from Scratch](medallion-lakehouse-from-scratch.md)
- ZettaPark API reference: [ZettaPark DataFrame API Guide](zettapark-dataframe-guide.md)
- Spark SQL syntax migration: [Spark SQL Syntax Migration Guide](migration-spark-sql.md)
- Volume usage guide: [Volume Usage Guide](zettapark-volume-guide.md)
