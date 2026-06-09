# Storage Connection + API Connection + External Function: Combined Practice

External Functions can look daunting at first — you need to configure an OSS Bucket, a serverless function runtime, a RAM role, write Python code, build a zip, and write DDL... three separate objects, many concepts, many steps, easy to get discouraged.

Once you get everything running, you'll find that the complexity is mostly concentrated in **one-time environment setup**. After that initial setup, the cost of adding new functions is extremely low: write Python logic → package → one DDL, done in three minutes. This guide walks you through four progressive scenarios to cover the full workflow across Alibaba Cloud, Tencent Cloud, and AWS.

**By the end you'll realize**: External Functions are not complex. You just configure "where to store code" and "where to run code" once, and every new function after that is just code + one SQL statement.

Full code on GitHub: [clickzetta_external_function](https://github.com/clickzetta/clickzetta_external_function)

---

## The Iron Triangle: How the Three Objects Work Together

An External Function is not just one object — it is the result of three objects working together. Understanding their roles makes the entire mechanism clear:

![](.topwrite/assets/external-function-iron-triangle.svg)


| Object | Analogy | What it does | How often configured |
|------|------|----------|--------|
| **Storage Connection** | Parking lot | Authenticates object storage (OSS/COS/S3), allows Lakehouse to read and write code packages | Once per Schema |
| **API Connection** | Workshop | Authenticates cloud function runtime (FC/SCF/Lambda), defines where code runs | Once per Region |
| **External Volume** | Shelf | Mounts the object storage Bucket to the Schema, enabling the PUT command to upload files | Once per Bucket |
| **CREATE EXTERNAL FUNCTION** | Registry | Maps a function name → entry class → zip package | Once per function |

The first three are one-time setups — once you configure Storage Connection + API Connection + External Volume, all functions share them. Adding a new function afterwards only requires one `CREATE EXTERNAL FUNCTION` statement.

---

## Prerequisites (One-time, Shared Across All Four Scenarios)

All four scenarios share the same cloud environment configuration. **This step is done only once**, and all four scenarios can use it directly.

### Step 1: Choose your cloud, configure config.json

Confirm which cloud your Lakehouse is on. The external function runtime (FC/SCF/Lambda) must be on the same cloud and in the same region:

```bash
cz-cli profile list
# service column:
#   alicloud.api.clickzetta.com    → Alibaba Cloud
#   tencentcloud.api.clickzetta.com → Tencent Cloud
#   aws.api.clickzetta.com          → AWS
```

```bash
git clone https://github.com/clickzetta/clickzetta_external_function.git
cd clickzetta_external_function
cp config.example.json config.json
```

Open `config.json` and change only the `platform` field:

```json
"platform": "aliyun"   // or "tencent" or "aws"
```

Then follow SETUP.md to complete the cloud-specific environment setup (OSS/COS/S3 Bucket, FC/SCF/Lambda, RAM/CAM/IAM role, Bailian API Key) and fill in the details in config.json.

### Step 2: Install cz-cli and verify

```bash
cz-cli profile use <your-profile>
cz-cli sql "SELECT current_schema()"
# Fill the output schema name into config.json → schema field
```

### Step 3: Universal steps for all four scenarios

The execution flow for all four scenarios is identical:

```
Fill config.json → check (validate config) → package (build code) → render (generate SQL) → deploy (execute deployment) → verify (call and verify)
```

Corresponding commands:

```bash
python ../1-check-config.py    # ① Validate configuration
python 2-package.py            # ② Package code (add --deps for AI functions)
python ../3-render-sql.py      # ③ Replace placeholders, generate SQL
cz-cli sql -f dist/4-deploy_generated.sql --write  # ④ Deploy
```

---

## Scenario 1: Python External Function Quick Start

> One function, zero dependencies, up and running in 5 minutes. Understand how Storage Connection + API Connection + External Function work together.

### Deploy

```bash
cd python_quickstart
python ../1-check-config.py
python 2-package.py
python ../3-render-sql.py
cz-cli sql -f dist/4-deploy_generated.sql --write
```

What `4-deploy_generated.sql` does:

```sql
-- 1. Storage Connection (OSS authentication)
CREATE STORAGE CONNECTION IF NOT EXISTS oss_sh_conn
TYPE OSS
access_id = '<your-id>' access_key = '<your-key>'
ENDPOINT = 'oss-cn-shanghai.aliyuncs.com';

-- 2. API Connection (Function Compute FC authentication)
CREATE API CONNECTION IF NOT EXISTS shanghai_func_conn
TYPE CLOUD_FUNCTION PROVIDER = 'aliyun'
REGION = 'cn-shanghai' ROLE_ARN = '<your-role-arn>'
CODE_BUCKET = '<your-bucket>';

-- 3. External Volume (mount Bucket)
CREATE EXTERNAL VOLUME IF NOT EXISTS external_functions_prod
LOCATION 'oss://<bucket>/' USING CONNECTION oss_sh_conn;

-- 4. Upload zip
PUT '<project>/dist/my_upper.zip' TO VOLUME external_functions_prod FILE 'my_upper.zip';

-- 5. Register function
CREATE EXTERNAL FUNCTION IF NOT EXISTS <schema>.my_upper
AS 'my_upper.my_upper'
USING ARCHIVE 'volume://external_functions_prod/my_upper.zip'
CONNECTION shanghai_func_conn
WITH PROPERTIES ('remote.udf.api'='python3.mc.v0','remote.udf.protocol'='http.arrow.v0');

-- 6. Verify
SELECT <schema>.my_upper('hello');  -- returns HELLO
```

### Function Source Code

`src/my_upper.py` — one class, one `evaluate` method:

```python
@annotate("*->string")
class my_upper(object):
    def evaluate(self, s):
        return s.upper() if s else s
```

### Local Testing

FC environments have no stdout and no stack traces. **Always test locally before each deployment**:

```bash
python3 -c "
import sys; sys.path.insert(0, 'src')
from my_upper import my_upper
print(my_upper().evaluate('hello'))  # HELLO
"
```

### Key Takeaways

- `remote.udf.api='python3.mc.v0'` specifies the Python 3.10 runtime for FC
- Calling the function **requires the schema prefix**: `SELECT <schema>.my_upper('hello')` — omitting it results in `function not found`
- The first call may take 5-10 seconds (FC cold start); subsequent calls are normal

---

## Scenario 2: Python ML Functions + Third-Party Dependency Packaging

> 5 ML/PII functions based on scikit-learn + jieba. Demonstrates how to correctly package third-party dependencies that include C extensions.

### Function List

| Function | Libraries used | Purpose |
|------|---------|------|
| `pii_mask` | re | Phone/email/ID masking |
| `feature_normalize` | numpy + sklearn | Numeric column normalization (minmax/zscore) |
| `anomaly_detect` | numpy + sklearn | Isolation Forest anomaly detection |
| `sentiment_score` | jieba | Chinese sentiment scoring (0-1) |
| `tfidf_keywords` | sklearn | TF-IDF keyword extraction |

### The Core Problem: FC Runs Linux, macOS Packages Won't Work

The FC runtime is **Linux x86_64 + Python 3.10**. Running `pip install scikit-learn` on macOS produces `.dylib` files that cannot be loaded on FC.

Solution: use two separate requirements files with two different install methods.

| File | Contents | Install method |
|------|--------|---------|
| `requirements.txt` | Packages with C extensions (scikit-learn, numpy) | `pip install --platform manylinux2014_x86_64 --only-binary :all:` |
| `requirements_pure.txt` | Pure Python packages (jieba) | Normal `pip install` |

**Why can't they be in the same file?** Putting jieba (pure Python) into `requirements.txt` with `--only-binary :all:` causes pip to throw `No matching distribution found` — pure Python packages don't have binary wheels.

### Deploy

```bash
cd python_advanced
python 2-package.py          # dual-mode packaging (~100 MB)
python ../1-check-config.py
python ../3-render-sql.py
cz-cli sql -f dist/4-deploy_generated.sql --write
```

### Local Testing

```bash
pip install -r requirements.txt -r requirements_pure.txt
python3 -c "
import sys; sys.path.insert(0, 'src')
from ml_toolkit import pii_mask, feature_normalize, sentiment_score
print(pii_mask().evaluate('My phone is 13812345678'))
print(feature_normalize().evaluate('[1,2,3,4,5]', 'minmax'))
print(sentiment_score().evaluate('The product quality is excellent'))
"
```

### Using in SQL

```sql
SELECT <schema>.pii_mask('Phone 13812345678, email alice@example.com');
SELECT <schema>.feature_normalize('[10,20,30,40,50]', 'minmax');
SELECT <schema>.anomaly_detect('[1,2,3,4,100]');
SELECT <schema>.sentiment_score('The product quality is excellent, shipping was fast, very satisfied!');
SELECT <schema>.tfidf_keywords('["AI and machine learning are the future","Deep learning achieves breakthroughs in image recognition"]', 3);
```

### Key Takeaways

- **C extension packages require Linux binary wheels** — macOS `.dylib` files cannot run on FC
- **Pure Python packages must be separated** — they cannot be mixed with binary packages in the same requirements file
- **Zip size determines cold start time**: scikit-learn + numpy is about 100MB; the first call takes 5-10 seconds

---

## Scenario 3: 30 AI SQL Functions — Package Once, Call Anywhere

> 30 AI functions share a single zip. Perform summarization, translation, sentiment analysis, OCR, and vector similarity search directly in SQL.

### Design Highlights

**One zip, 30 functions**: All 30 functions share a single `clickzetta_ai_functions_full.zip`. The DDL only differs in the class name `AS 'ai_functions_complete.ai_xxx'`. Packaging and uploading a separate zip for each function would mean 30 zip files and exploding management complexity.

**API Key as a SQL parameter**: The Bailian API Key is not hardcoded in the source code or bundled into the zip — it is passed as a function parameter:

```sql
SELECT <schema>.ai_text_summarize('Artificial intelligence is changing the world.', '<your-api-key>');
```

If the API Key were hardcoded in the zip, a zip leak would mean a Key leak. Passing it as a parameter lets callers manage their own keys.

### Function Categories

| Category | Count | Typical functions |
|------|------|---------|
| Text processing | 8 | Summarization, translation, sentiment analysis, entity extraction, keywords, classification, cleaning, tagging |
| Vector processing | 5 | Embedding, similarity, clustering preparation, similar search, document search |
| Multimodal | 8 | Image description, OCR, image analysis, image embedding, image similarity, video summarization, chart analysis, document parsing |
| Business scenarios | 9 | Customer intent, sales scoring, review analysis, risk detection, contract extraction, resume parsing, customer segmentation, product description, industry classification |

### Deploy

```bash
cd python_ai_function
pip install -r requirements.txt    # for local testing only
python 2-package.py --deps         # package code + dashscope Linux dependencies
python 1-check-config.py           # standalone validation (different config structure)
python 3-render-sql.py
cz-cli sql -f dist/4-deploy_generated.sql --write
```

### Local Testing

FC has no logs and no stdout. **Test locally before deploying to save a lot of time:**

```bash
python3 -c "
import sys; sys.path.insert(0, 'src')
from ai_functions_complete import ai_text_summarize, ai_text_translate
print(ai_text_summarize().evaluate('Hello world', '<your-api-key>'))
print(ai_text_translate().evaluate('Hello', 'Chinese', '<your-api-key>'))
"
```

### Using in SQL

```sql
-- Summarization
SELECT <schema>.ai_text_summarize('Artificial intelligence is changing the world...', '<key>');

-- Translation
SELECT <schema>.ai_text_translate('Hello, how are you?', 'Chinese', '<key>');

-- Sentiment analysis
SELECT <schema>.ai_text_sentiment_analyze('The product quality is excellent!', '<key>');

-- Embedding + similarity search
SELECT <schema>.ai_semantic_similarity('Apples are tasty', 'Apples are a healthy fruit', '<key>');

-- Image description
SELECT <schema>.ai_image_describe('<image-url>', '<key>');

-- Contract extraction
SELECT <schema>.ai_contract_extract('<contract text>', '<key>');
```

Returns JSON; use `JSON_EXTRACT` to retrieve values:

```sql
SELECT JSON_EXTRACT(
    <schema>.ai_text_summarize('Artificial intelligence is changing the world...', '<key>'),
    '$.summary'
);
```

### Key Takeaways

- **30 functions share one zip** — adding a new function = 20 lines of prompt + one DDL
- **API Key is not hardcoded** — passed as a SQL parameter, so a zip leak does not compromise security
- **config.json serves dual roles**: embedded in the zip at build time (for runtime model config), and used to replace SQL placeholders at render time

---

## Scenario 4: Java UDF/UDAF/UDTF

> Java external functions support three types: UDF (one row in, one row out), UDAF (multiple rows in, one row out), UDTF (one row in, multiple rows out).

### Quick Overview of the Three Types

| Type | Base class | Input → Output | DDL special property | Example function |
|------|------|-------------|-------------|---------|
| **UDF** | `GenericUDF` | 1 row → 1 row | — | `pii_mask` PII masking |
| **UDAF** | `GenericUDAFResolver2` | Multiple rows → 1 row | `AGGREGATOR` | `agg_stats` SUM/AVG/MIN/MAX/COUNT |
| **UDTF** | `GenericUDTF` | 1 row → N rows | `TABLE_VALUED` | `log_explode` log row expansion |

### Differences from Python External Functions

| | Python | Java |
|------|--------|------|
| Runtime | Python 3.10 | **Java 8** (Java 9+ not supported) |
| DDL property | `python3.mc.v0` | `java8.hive2.v0` |
| Function types | UDF | UDF / UDAF / UDTF |
| Packaging | zip | Maven `jar-with-dependencies` → zip |
| Dependencies | pip `--platform manylinux` | Maven `scope=provided` (Hive runtime included) |

### Deploy

```bash
cd java_udf
python 2-package.py           # Maven compile + zip packaging
python ../1-check-config.py
python ../3-render-sql.py
cz-cli sql -f dist/4-deploy_generated.sql --write
```

### UDF Example

```sql
SELECT <schema>.pii_mask('My phone is 13812345678, email alice@example.com');
```

### UDAF Example

```sql
INSERT INTO <schema>.java_udf_test_scores VALUES (3.5), (4.2), (2.8), (5.0), (3.9);
SELECT <schema>.agg_stats(val) FROM <schema>.java_udf_test_scores;
-- → [sum, avg, min, max, count]
```

### UDTF Example

UDTF requires the `LATERAL` syntax and cannot be used with `SELECT func(x)`:

```sql
SELECT t.ts, t.event
FROM (
    SELECT '[2025-01-15 10:30:00] User login
[2025-01-15 10:35:00] Query order' AS log
) s, LATERAL <schema>.log_explode(s.log) t;
-- → each log line is expanded into one row
```

### Key Takeaways

- **Java version must be 8** — FC only has a Java 8 runtime
- **Hive dependency scope=provided**: FC includes `hive-exec.jar`; do not bundle it in the zip to avoid conflicts
- **UDAF DDL must include `AGGREGATOR`**, UDTF must include `TABLE_VALUED` — omitting them causes creation to succeed but calls to fail
- **UDTF must use `LATERAL`** syntax; `SELECT func(x)` directly is not supported

---

## Function Quick Reference

### Python (quickstart + advanced + AI function)

| Function | Purpose | Source |
|------|------|------|
| `my_upper` | String to uppercase | quickstart |
| `pii_mask` | Phone/email/ID masking | advanced |
| `feature_normalize` | Numeric column normalization | advanced |
| `anomaly_detect` | Isolation Forest anomaly detection | advanced |
| `sentiment_score` | Chinese sentiment scoring | advanced |
| `tfidf_keywords` | TF-IDF keyword extraction | advanced |
| `ai_text_summarize` | Text summarization | AI function |
| `ai_text_translate` | Text translation | AI function |
| `ai_text_sentiment_analyze` | Sentiment analysis | AI function |
| `ai_text_extract_entities` | Entity extraction | AI function |
| `ai_text_extract_keywords` | Keyword extraction | AI function |
| `ai_text_classify` | Text classification | AI function |
| `ai_text_clean_normalize` | Text cleaning | AI function |
| `ai_auto_tag_generate` | Auto tagging | AI function |
| `ai_text_to_embedding` | Text embedding | AI function |
| `ai_semantic_similarity` | Semantic similarity | AI function |
| `ai_text_clustering_prepare` | Clustering preparation | AI function |
| `ai_find_similar_text` | Similar text search | AI function |
| `ai_document_search` | Document search | AI function |
| `ai_image_describe` | Image description | AI function |
| `ai_image_ocr` | Image OCR | AI function |
| `ai_image_analyze` | Image analysis | AI function |
| `ai_image_to_embedding` | Image embedding | AI function |
| `ai_image_similarity` | Image similarity | AI function |
| `ai_video_summarize` | Video summarization | AI function |
| `ai_chart_analyze` | Chart analysis | AI function |
| `ai_document_parse` | Document parsing | AI function |
| `ai_customer_intent_analyze` | Customer intent analysis | AI function |
| `ai_sales_lead_score` | Sales lead scoring | AI function |
| `ai_review_analyze` | Review analysis | AI function |
| `ai_risk_text_detect` | Risk text detection | AI function |
| `ai_contract_extract` | Contract extraction | AI function |
| `ai_resume_parse` | Resume parsing | AI function |
| `ai_customer_segment` | Customer segmentation | AI function |
| `ai_product_description_generate` | Product description generation | AI function |
| `ai_industry_classification` | Industry classification | AI function |

### Java

| Function | Type | Purpose |
|------|------|------|
| `pii_mask` | UDF | PII masking |
| `agg_stats` | UDAF | SUM/AVG/MIN/MAX/COUNT |
| `log_explode` | UDTF | Log row expansion |

---

## Troubleshooting

| Error | Cause | Solution |
|------|------|------|
| `function not found` | Missing schema prefix | Add `<schema>.` prefix when calling |
| `HTTP_GENERAL_ERROR(640)` | RAM trust policy not configured / Bucket in a different region | Check RAM role trust policy (must include `1384322691904283`); confirm Bucket and FC are in the same region |
| `AccessDenied` | RAM role missing OSS permissions | Add `AliyunOSSFullAccess` or a custom OSS policy |
| `ImportError: No module named 'sklearn'` | Dependencies not packaged in zip | Re-run `python 2-package.py` (advanced) / `python 2-package.py --deps` (AI function) |
| `OSError: cannot open shared object file` | macOS `.dylib` was packaged | Confirm `--platform manylinux2014_x86_64` was used |
| `ClassNotFoundException` | Wrong Java class name or package name | Check that the `AS` path matches the actual class name inside the jar |
| UDAF created successfully but call fails | DDL missing `AGGREGATOR` | Check `WITH PROPERTIES ('remote.udf.category'='AGGREGATOR')` |
| UDTF created successfully but `not a table function` | DDL missing `TABLE_VALUED` | Check `WITH PROPERTIES ('remote.udf.category'='TABLE_VALUED')` |
| First call takes a long time to return | FC cold start | Wait 5-10 seconds; it has not hung |
| Changes to `config.json` not reflected after deployment | Forgot to re-render | Re-run `python ../3-render-sql.py` |

---

## Related Documentation

- [External Function Introduction](RemoteFunction-intro.md)
- [Development Guide: External Function (Python3)](RemoteFunction-dev-guide-python3.md)
- [Development Guide: External Function (Java)](external-function-dev-guide-java.md)
- [CREATE EXTERNAL FUNCTION](create_external_function.md)
- [GitHub: clickzetta_external_function](https://github.com/clickzetta/clickzetta_external_function)
