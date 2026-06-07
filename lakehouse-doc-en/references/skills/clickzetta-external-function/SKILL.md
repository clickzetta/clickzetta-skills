---
name: clickzetta-external-function
description: |
  Create and use External Functions (custom UDFs) in ClickZetta Lakehouse using Python or Java,
  deployed on Alibaba Cloud FC / Tencent Cloud SCF / AWS Lambda.
  Covers CREATE API CONNECTION (TYPE CLOUD_FUNCTION), CREATE EXTERNAL FUNCTION, Python/Java UDF code structure and packaging.
  Keywords: external function, UDF, Python UDF, Java UDF, custom function, cloud function
---

# ClickZetta External Function (Custom UDF)

External Functions let SQL call custom compute logic written in Python or Java, deployed on a cloud function service (Alibaba Cloud FC / Tencent Cloud SCF / AWS Lambda).

See [references/external-function-ddl.md](references/external-function-ddl.md) for the full syntax reference.

---

## Overall Flow

```
1. Enable a cloud function service (Alibaba Cloud FC / Tencent Cloud SCF / AWS Lambda)
2. Write Python/Java function code
3. Package and upload to object storage or User Volume
4. Grant Lakehouse access to the cloud function service (RAM role)
5. CREATE API CONNECTION (TYPE CLOUD_FUNCTION)
6. CREATE EXTERNAL FUNCTION
7. Call the function in SQL
```

---

## Step 1: Create a Cloud Function API Connection

```sql
-- Alibaba Cloud FC
CREATE API CONNECTION IF NOT EXISTS my_fc_conn
  TYPE CLOUD_FUNCTION
  PROVIDER = 'aliyun'
  REGION = 'cn-shanghai'
  ROLE_ARN = 'acs:ram::1234567890:role/CzUDFRole'
  NAMESPACE = 'default'
  CODE_BUCKET = 'my-oss-bucket';

-- Tencent Cloud SCF
CREATE API CONNECTION IF NOT EXISTS my_scf_conn
  TYPE CLOUD_FUNCTION
  PROVIDER = 'tencent'
  REGION = 'ap-shanghai'
  ROLE_ARN = 'qcs::cam::uin/1234567890:roleName/CzUDFRole'
  NAMESPACE = 'default'
  CODE_BUCKET = 'my-cos-bucket';
```

---

## Step 2: Write a Python UDF

```python
# upper.py
try:
    from cz.udf import annotate
except ImportError:
    annotate = lambda _: lambda _: _

@annotate("string->string")
class Upper(object):
    def evaluate(self, arg):
        if arg is None:
            return None
        return arg.upper()
```

Package and upload:
```bash
zip -rq upper.zip upper.py
```

```sql
-- Upload to User Volume (run in ClickZetta Studio or CLI; source_path must be an absolute path)
PUT '/path/to/upper.zip' TO USER VOLUME;
```

---

## Step 3: Create the External Function

```sql
-- ⚠️ CREATE EXTERNAL FUNCTION does not support OR REPLACE, only IF NOT EXISTS
-- ❌ Wrong: CREATE OR REPLACE EXTERNAL FUNCTION ...
-- ✅ Correct:

-- Using User Volume to store code (no object storage required)
CREATE EXTERNAL FUNCTION IF NOT EXISTS public.str_upper
  AS 'upper.Upper'
  USING FILE = 'volume:user://~/upper.zip'
  CONNECTION = my_fc_conn
  WITH PROPERTIES ('remote.udf.api' = 'python3.mc.v0')
  COMMENT 'Convert string to uppercase';

-- Using OSS to store code
CREATE EXTERNAL FUNCTION IF NOT EXISTS public.str_upper
  AS 'upper.Upper'
  USING FILE = 'oss://my-bucket/functions/upper.zip'
  CONNECTION = my_fc_conn
  WITH PROPERTIES ('remote.udf.api' = 'python3.mc.v0');
```

---

## Step 4: Call the Function

```sql
-- ⚠️ External functions must be called with the full schema-qualified name; the schema cannot be omitted
-- ❌ Wrong: SELECT str_upper(name) FROM my_table;
-- ✅ Correct:
SELECT id, public.str_upper(name) AS upper_name FROM my_table;
```

---

## Management

```sql
-- List all external functions
SHOW EXTERNAL FUNCTIONS;
SHOW EXTERNAL FUNCTIONS LIKE 'str_%';

-- Drop a function (use DROP FUNCTION, not DROP EXTERNAL FUNCTION)
DROP FUNCTION IF EXISTS public.str_upper;
```

> ⚠️ **Note**: `CREATE FUNCTION` (inline SQL function) only supports SQL expressions — it does not support Python, JavaScript, or other programming languages. Use `CREATE EXTERNAL FUNCTION` when you need full programming language logic.

---

## Troubleshooting

| Problem | Cause | Solution |
|---|---|---|
| Function call times out | Cloud function cold start or slow execution | Increase the timeout setting, or pre-warm the function |
| Dependency ABI incompatibility | Packaged on macOS/Windows | Use the `quay.io/pypa/manylinux2014_x86_64` container to package |
| Code package > 500 MB | Dependencies too large | Switch to container image deployment |
| ROLE_ARN permission denied | RAM role not authorized | Configure AliyunFCFullAccess + OSS permissions per the documentation |
| Function call returns "not found" | Schema prefix omitted | Always use the full path: `schema.function_name(...)` |
| CREATE OR REPLACE error | EXTERNAL FUNCTION does not support OR REPLACE | Use `CREATE EXTERNAL FUNCTION IF NOT EXISTS` instead |
