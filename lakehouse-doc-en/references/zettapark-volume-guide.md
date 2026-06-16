# Zettapark Volume and File Operations

Zettapark provides complete Volume file operation capabilities — upload, download, read, and export — seamlessly integrating file handling with DataFrame operations.

---

## Prerequisites

```python
from clickzetta.zettapark.session import Session
from clickzetta.zettapark import functions as F

session = Session.builder.configs({
    "username": "your_username",
    "password": "your_password",
    "service":  "cn-shanghai-alicloud.api.clickzetta.com",
    "instance": "your_instance",
    "workspace": "your_workspace",
    "schema":   "public",
    "vcluster": "DEFAULT"
}).create()
```

**Volume path format**: `volume://volume_name/path/to/file`

**Capability comparison between Volume types:**

| Operation | Named Volume (internal) | External Volume (OSS/S3/COS) |
|------|---------------------|------------------------------|
| `session.file.put` upload | ✅ (requires REFRESH after upload) | ✅ |
| `session.file.get` download | ✅ | ✅ |
| `session.file.list_` list directory | ✅ | ✅ |
| `session.file.delete` delete | ✅ | ✅ |
| `session.read.csv/parquet/json` | ✅ (requires REFRESH after upload) | ✅ |
| `df.write.copy_into_volume` export | ✅ | ✅ |

The examples in this guide use Named Volume (internal Volume), which requires no external storage mount and can be used immediately after creation:

Create a Named Volume (one-time operation)

```python
session.sql("CREATE VOLUME IF NOT EXISTS my_named_vol").collect()
```

> ⚠️ After uploading files with `session.file.put`, run `ALTER VOLUME my_named_vol REFRESH` to refresh the directory index before `session.read` methods can see the new files.
>
> 💡 To mount existing OSS/S3/COS object storage, use an External Volume. See [External Volume](external_volume.md).

---

## File Upload and Download

### Upload a Local File to a Volume

Upload a single file

```python
result = session.file.put(
    "/local/path/data.csv",
    "volume://my_named_vol/data/data.csv",
    auto_compress=False
)
print(result)
```

```Plain
[PutResult(source='/local/path/data.csv', target='/data/data.csv', source_size=1024, target_size=1024)]
```

Refresh the directory index after upload so session.read can see the new file

```python
session.sql("ALTER VOLUME my_named_vol REFRESH").collect()
```

### Download a Volume File to Local

```python
result = session.file.get(
    "volume://my_named_vol/data/data.csv",
    "/local/output/"
)
print(result)
```

```Plain
[GetResult(file='data.csv', size=1024)]
```

### List a Volume Directory

```python
files = session.file.list_("volume://my_named_vol/data/")
for f in files:
    print(f.file, f.size)
```

```Plain
data/orders.csv  2048
data/users.csv   1024
```

### Delete a Volume File

Delete a single file

```python
session.file.delete("volume://my_named_vol/data/old_file.csv")
```

Delete a directory (deletes all files under it)

```python
session.file.delete("volume://my_named_vol/archive/")
```

---

## Read Data from a Volume

### Read CSV

```python
df = session.read \
    .option("header", True) \
    .option("infer_schema", True) \
    .csv("volume://my_named_vol/data/orders.csv")

df.show()
df.printSchema()
```

### Read Parquet

Read all Parquet files in a directory

```python
df = session.read.parquet("volume://my_named_vol/data/parquet_dir/")
df.show()
```

### Read JSON (NDJSON format — one JSON object per line)

```python
df = session.read.json("volume://my_named_vol/data/events.json")
df.show()
```

---

## Export a DataFrame to a Volume

Both Named Volume and External Volume support export.

### Export as CSV

```python
df = session.table("orders")

df.write.copy_into_volume(
    "volume://my_named_vol/export/orders/",
    file_format_type="csv",
    header=True
)
```

### Export as Parquet

```python
df.write.copy_into_volume(
    "volume://my_named_vol/export/orders_parquet/",
    file_format_type="parquet"
)
```

---

## Complete Example: ETL Pipeline

Read raw files from a Volume, process them, write to a table, then export results back to a Volume:

Step 1: Upload raw data to Volume

```python
import csv

raw_data = [
    ["order_id", "user_id", "product", "amount", "status"],
    [1001, 101, "iPhone",  7999.0, "paid"],
    [1002, 102, "MacBook", 14999.0, "paid"],
    [1003, 101, "AirPods", 1799.0, "pending"],
]
with open("/tmp/raw_orders.csv", "w", newline="") as f:
    csv.writer(f).writerows(raw_data)

session.file.put(
    "/tmp/raw_orders.csv",
    "volume://my_named_vol/raw/orders.csv",
    auto_compress=False
)
```

Refresh the directory index so session.read can see the newly uploaded file

```python
session.sql("ALTER VOLUME my_named_vol REFRESH").collect()
```

Step 2: Read from Volume and clean data

```python
df = session.read \
    .option("header", True) \
    .option("infer_schema", True) \
    .csv("volume://my_named_vol/raw/orders.csv")
```

Filter and transform

```python
paid_df = df.filter(F.col("status") == "paid") \
    .with_column("amount_with_tax", F.col("amount") * 1.13)
```

Step 3: Write to a Lakehouse table

```python
paid_df.write.save_as_table("paid_orders", mode="overwrite")
print(f"Written {paid_df.count()} records")
```

Step 4: Export processed results back to Volume

```python
session.table("paid_orders") \
    .write.copy_into_volume(
        "volume://my_named_vol/processed/paid_orders/",
        file_format_type="parquet"
    )
```

Verify export results

```python
files = session.file.list_("volume://my_named_vol/processed/paid_orders/")
print(f"Exported files: {[f.file for f in files]}")
```

---

## Named Volume Operations

Named Volume is internal storage — no external dependencies required. Suitable for temporary storage and export scenarios.

Create a Named Volume

```python
session.sql("CREATE VOLUME IF NOT EXISTS my_named_vol").collect()
```

Upload a file (using SQL PUT command)

```python
session.sql("PUT '/local/path/file.csv' TO VOLUME my_named_vol FILE 'data/file.csv'").collect()
```

List files

```python
files = session.file.list_("volume://my_named_vol/")
for f in files:
    print(f.file, f.size)
```

Download a file

```python
session.file.get("volume://my_named_vol/data/file.csv", "/local/output/")
```

Delete a file

```python
session.file.delete("volume://my_named_vol/data/file.csv")
```

Export DataFrame to Named Volume

```python
df.write.copy_into_volume(
    "volume://my_named_vol/export/",
    file_format_type="csv",
    header=True
)
```

---

## User Volume Operations

User Volume is each user's personal storage space. `session.file` methods are not supported — use SQL commands instead:

Upload to User Volume

```python
session.sql("PUT '/local/path/file.csv' TO USER VOLUME FILE 'subdir/file.csv'").collect()
```

List User Volume files

```python
files = session.sql("SHOW USER VOLUME DIRECTORY").collect()
for f in files:
    print(f["relative_path"], f["size"])
```

Read from User Volume (via SQL SELECT FROM VOLUME)

```python
df = session.sql("""
    SELECT * FROM USER VOLUME
    USING CSV
    OPTIONS('header'='true')
    FILES('subdir/file.csv')
""")
df.show()
```

Download a User Volume file

```python
session.sql("GET USER VOLUME FILE 'subdir/file.csv' TO '/local/output/'").collect()
```

---

## Notes

- **Path format**: Volume paths use `volume://volume_name/path`; `@vol_name` or relative paths are not supported
- **REFRESH required after upload**: After uploading files with `session.file.put`, run `ALTER VOLUME name REFRESH` to refresh the directory index before `session.read` methods can see the new files
- **Wait after creating a new Volume**: A newly created Named Volume needs approximately 1 minute to initialize before files can be uploaded and read
- **Parquet reads**: Pass a directory path (ending with `/`) to read all Parquet files in that directory
- **Export paths**: The `copy_into_volume` target path should end with `/`; file names are auto-generated by the system (e.g., `part00001.csv`)

---

## Related Documentation

| Document | Description |
|------|------|
| [External Volume](external_volume.md) | Mount OSS/S3/COS to create an External Volume |
| [Internal Volume](internal_volume.md) | Named Volume and User Volume details |
| [Zettapark DataFrame API Guide](zettapark-dataframe-guide.md) | Complete DataFrame operations reference |
| [Zettapark Data Engineering Practice](zettapark-etl-guide.md) | Multi-table joins, window functions, and more |
| [COPY INTO](copy-into-table.md) | Import data from Volume using SQL |
