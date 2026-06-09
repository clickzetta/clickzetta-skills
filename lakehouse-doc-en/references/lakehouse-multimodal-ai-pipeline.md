# AI Gateway in Action: Analyzing Images in SQL to Build a Multimodal AI Pipeline

The image mode of `AI_COMPLETE` allows SQL to handle not just text, but also directly analyze image content—product image classification, document OCR recognition, monitoring screenshot anomaly detection, all completed in a single SQL query. Combined with **Volume storage + presigned URLs**, it forms a fully managed pipeline from image upload to AI analysis.

This article uses the Kimi K2.6 multimodal model as an example to demonstrate how to build an end-to-end multimodal AI pipeline in Singdata Lakehouse.

---

## Pipeline Architecture

![](.topwrite/assets/12-multimodal-ai-pipeline.svg)

Three key steps:
1. **`PUT`** uploads images to User Volume (internal storage, user-isolated)
2. **`GET_PRESIGNED_URL`** generates a time-limited OSS signed URL so the LLM can access it
3. **`AI_COMPLETE` image mode** sends the image URL + Prompt to get analysis results

---

## Upload Images to Volume

```sql
-- Upload a single image to User Volume
PUT '/path/to/product.jpg' TO USER VOLUME FILE 'images/product.jpg';

-- Upload to a subdirectory
PUT '/path/to/screenshot.png' TO USER VOLUME FILE 'screenshots/error_001.png';
```

> User Volume is private to the user; other users cannot access it. For team-shared images, use an External Volume mounting OSS/COS/S3.

---

## Generate Presigned URL

`GET_PRESIGNED_URL` generates a time-limited OSS signed URL for files in the Volume, which the LLM uses to download the image.

```sql
-- ⚠️ Must enable external mode first, otherwise an internal URL is generated (LLM cannot access)
SET cz.sql.function.get.presigned.url.force.external = true;

-- Generate a presigned URL valid for 1 hour
SELECT GET_PRESIGNED_URL(USER VOLUME, 'images/product.jpg', 3600) AS url;
```

Example return value:
```
http://cz-lh-sh-system-prod.oss-cn-shanghai.aliyuncs.com/.../product.jpg
  ?Expires=1780392774&OSSAccessKeyId=...&Signature=...
```

Parameter descriptions:
- First parameter: Volume type and name (`USER VOLUME` / `VOLUME my_vol`)
- Second parameter: File path within the Volume
- Third parameter: Validity period (seconds), recommended 3600 (1 hour), maximum 7 days

---

## AI_COMPLETE Image Mode

Image mode uses the **row value syntax** `(prompt AS prompt, image_url AS image)` to pass both the Prompt and image URL together:

```sql
SET cz.sql.function.get.presigned.url.force.external = true;

SELECT AI_COMPLETE('ai_gateway_conn:moonshotai/kimi-k2.6',
    ('Describe this image in one sentence' AS prompt,
     GET_PRESIGNED_URL(USER VOLUME, 'ai_test/test_icon.png', 3600) AS image)
);
```

Output (1.3 seconds):

> The image is completely black, showing nothing visible.

### Syntax Details

| Parameter | Format | Description |
|---|---|---|
| model | `'ai_gateway_conn:moonshotai/kimi-k2.6'` | Must use a model that supports multimodal capabilities |
| prompt | `'Describe this image' AS prompt` | Text prompt; `AS prompt` cannot be omitted |
| image | `GET_PRESIGNED_URL(...) AS image` | Image URL; `AS image` cannot be omitted |

### Supported Models

Image mode requires a model with multimodal (vision) support, such as `moonshotai/kimi-k2.6` (confirmed working, 1.3s response). Text-only models will not throw an error when passed an image URL but cannot recognize image content.

---

## In Practice: Batch Image Analysis

### Scenario: Automatic Product Image Classification

Suppose an e-commerce system uploads thousands of product images to OSS daily and needs to automatically identify the product type in each image.

```sql
-- 1. Create table to store analysis results
CREATE TABLE product_image_analysis (
    image_path  STRING  COMMENT 'Image path',
    category    STRING  COMMENT 'AI-recognized category',
    description STRING  COMMENT 'AI description',
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- 2. Read image list from External Volume, analyze in batch
SET cz.sql.function.get.presigned.url.force.external = true;

INSERT INTO product_image_analysis (image_path, category, description)
SELECT
    relative_path AS image_path,
    -- Classification
    AI_COMPLETE('ai_gateway_conn:moonshotai/kimi-k2.6',
        ('Classify the product into one of the following categories: electronics/clothing/food/furniture. Reply with the category name only.'
         AS prompt,
         GET_PRESIGNED_URL(VOLUME product_images_vol, relative_path, 3600) AS image)
    ) AS category,
    -- Description
    AI_COMPLETE('ai_gateway_conn:moonshotai/kimi-k2.6',
        ('Describe this product in one sentence' AS prompt,
         GET_PRESIGNED_URL(VOLUME product_images_vol, relative_path, 3600) AS image)
    ) AS description
FROM DIRECTORY(VOLUME product_images_vol)
WHERE relative_path LIKE '%.jpg'
    AND last_modified_time > CURRENT_TIMESTAMP() - INTERVAL 1 DAY;
```

### Query Results

```sql
SELECT category, COUNT(*) AS cnt
FROM product_image_analysis
GROUP BY category
ORDER BY cnt DESC;
```

### Dynamic Table for Automatic Incremental Analysis

Wrap the above logic in a Dynamic Table so new images are automatically analyzed after upload:

```sql
SET cz.sql.function.get.presigned.url.force.external = true;

CREATE OR REPLACE DYNAMIC TABLE gold.product_image_tags
REFRESH INTERVAL 1 HOUR vcluster DEFAULT
COMMENT 'Product image AI tags — auto incremental update'
AS
SELECT
    relative_path AS image_path,
    AI_COMPLETE('ai_gateway_conn:moonshotai/kimi-k2.6',
        ('Classify the product as electronics/clothing/food/furniture, reply with category name only.'
         AS prompt,
         GET_PRESIGNED_URL(VOLUME product_images_vol, relative_path, 3600) AS image)
    ) AS category,
    last_modified_time
FROM DIRECTORY(VOLUME product_images_vol)
WHERE relative_path LIKE '%.jpg';
```

> ⚠️ **Note**: DT re-calls AI_COMPLETE for all rows on every REFRESH, which can be costly. It is recommended to use a regular table + scheduled INSERT instead, analyzing only newly added images.

---

## Applicable Scenarios

| Scenario | Implementation |
|---|---|
| Automatic product image classification | AI_COMPLETE image mode + classification Prompt |
| Document OCR extraction | "Extract all text from the image" |
| Monitoring screenshot anomaly detection | "Determine if there is an anomaly in the image, reply normal/abnormal only" |
| Social media image content moderation | "Determine if the image content violates rules, reply safe/unsafe only" |
| Invoice/document information extraction | "Extract the amount, date, and company name from the image" |
| Preliminary medical imaging screening | "Determine if there is an abnormal area in the image, reply yes/no only" |

---

## Notes

| Note | Description |
|---|---|
| **Presigned URL must use force.external** | `SET cz.sql.function.get.presigned.url.force.external = true`, otherwise generates internal URL |
| **Image formats** | Supports PNG, JPG, JPEG. SVG has a null MIME type, causing `Invalid image MIME type` error |
| **Model selection** | Must use a multimodal (vision) model. Text-only models won't error but cannot recognize image content |
| **URL validity** | Presigned URL default recommendation is 3600 seconds (1 hour), maximum 7 days |
| **DT cost** | AI_COMPLETE in DT fully recomputes on every REFRESH; use regular table + manual INSERT instead |
| **Concurrency limits** | For large-scale concurrent image analysis, watch AI Gateway TPM/RPM quota limits |
| **File size** | Images recommended to be < 10MB; oversized images may time out or consume too many tokens |
| **User Volume isolation** | User Volume is private; other users cannot see images you upload |

---

## Related Documents

- [AI_COMPLETE documentation](ai_complete.md) — Image mode parameters, options configuration
- [AI-Enhanced Data Analysis](lakehouse-ai-sql-analysis.md) — AI_COMPLETE text mode in practice
- [Volume Overview](volume-overview.md) — User Volume and External Volume concepts
- [GET_PRESIGNED_URL](put_get_volume.md) — Presigned URL generation
- [AI Gateway Product Overview](AI_Gateway.md) — Endpoint management, quota control
- [Multi-Cloud Unified Data Lake Acceleration](lakehouse-multi-cloud-acceleration.md) — Volume + Pipe cross-cloud approach
