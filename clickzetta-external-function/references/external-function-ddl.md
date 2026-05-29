# External Function DDL Reference

> Source: https://www.yunqi.tech/documents/CREATE_EXTERNATL_FUNCTION

## Concepts

An External Function is a custom UDF written in Python or Java and executed on a cloud function service (Alibaba Cloud FC / Tencent Cloud SCF / AWS Lambda). It can call:
- **Online services**: image recognition APIs, custom REST services, etc.
- **Offline models**: Hugging Face models packaged and uploaded

Supported function types: UDF (scalar), UDAF (aggregate, Java only), UDTF (table function, Java only)

> For built-in LLM functions (AI_COMPLETE, AI_EMBEDDING), see the `clickzetta-ai-function` skill.

---

## CREATE API CONNECTION (Cloud Function)

```sql
CREATE API CONNECTION IF NOT EXISTS my_fc_conn
  TYPE CLOUD_FUNCTION
  PROVIDER = 'aliyun'           -- 'aliyun' | 'tencent' | 'aws'
  REGION = 'cn-shanghai'
  ROLE_ARN = 'acs:ram::1234567890:role/CzUDFRole'
  NAMESPACE = 'default'         -- Required for Tencent Cloud; use 'default' for others
  CODE_BUCKET = 'my-oss-bucket';
```

| Parameter | Description |
|---|---|
| PROVIDER | `'aliyun'` / `'tencent'` / `'aws'` |
| REGION | Alibaba Cloud: `cn-shanghai`; Tencent Cloud: `ap-beijing`; AWS: `cn-northwest-1` |
| ROLE_ARN | RAM role ARN granted to Lakehouse |
| NAMESPACE | Tencent Cloud namespace (required); use `'default'` for others |
| CODE_BUCKET | OSS/COS/S3 bucket name where the function code package is stored |

---

## CREATE EXTERNAL FUNCTION

```sql
CREATE EXTERNAL FUNCTION IF NOT EXISTS my_schema.my_udf
  AS 'module_name.ClassName'
  USING FILE = 'oss://my-bucket/functions/code.zip'
  CONNECTION = my_fc_conn
  WITH PROPERTIES (
      'remote.udf.api' = 'python3.mc.v0'   -- Python: python3.mc.v0 | Java: java8.hive2.v0
  )
  COMMENT 'Custom function description';
```

### Resource File Path Formats

```
-- OSS/COS/S3
oss://bucket-name/path/to/code.zip
cos://bucket-name/path/to/code.zip
s3://bucket-name/path/to/code.zip

-- User Volume (no object storage required)
volume:user://~/code.zip

-- External Volume
volume://workspace.schema.volume_name/code.zip
```

### WITH PROPERTIES Parameters

| Parameter | Value | Description |
|---|---|---|
| `remote.udf.api` | `python3.mc.v0` | Python 3.10 runtime |
| `remote.udf.api` | `java8.hive2.v0` | Java 8 Hive-style UDF |
| `remote.udf.protocol` | `http.arrow.v0` | Default protocol for accessing the cloud function |

---

## Python UDF Code Structure

```python
#!/usr/bin/env python
try:
    from cz.udf import annotate
except ImportError:
    annotate = lambda _: lambda _: _

@annotate("string->string")   # Function signature: input_type->return_type
class Upper(object):
    def evaluate(self, arg):
        if arg is None:
            return None
        return arg.upper()
```

### Function Signature Format

```
"input_type1,input_type2->return_type"

# Examples
"string->string"           # String in, string out
"string,int->double"       # Two inputs, returns double
"string->array<string>"    # Returns an array
```

Supported types: `string`, `int`, `bigint`, `double`, `float`, `boolean`, `array<T>`, `map<K,V>`

### Packaging and Upload

```bash
# Install dependencies into the current directory
pip3 install httpx pydantic -t .

# Package (must be < 500 MB)
zip -rq code.zip ./*
```

```sql
-- Upload to User Volume (run in ClickZetta Studio or CLI; source_path must be an absolute path)
PUT '/path/to/code.zip' TO USER VOLUME;
```

---

## Management

```sql
-- List external functions
SHOW EXTERNAL FUNCTIONS;
SHOW EXTERNAL FUNCTIONS LIKE 'my_%';

-- Drop an external function
DROP FUNCTION IF EXISTS my_schema.my_udf;
```
