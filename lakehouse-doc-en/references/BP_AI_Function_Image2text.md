# Singdata Lakehouse Image Analysis Best Practices

## Introduction

In the data-driven era, image data has become an important component of enterprise data assets. Singdata Lakehouse, by integrating advanced image recognition and vector retrieval technologies, provides enterprises with a complete solution for image data management and analysis. This article will use a food image recognition practical case to introduce in detail how to build an end-to-end image analysis system in Singdata Lakehouse.

## 1. Key Product Features

* **Multi-Modal Storage**: Supports unified management of image files, vector data, and structured metadata
* **External Functions** (EXTERNAL FUNCTION): Seamlessly invoke AI models for image recognition and vectorization
* **Vector Retrieval**: Natively supports 1024-dimensional vector storage and similarity computation

## 2. Practical Case: Food Image Recognition System

### 2.1 Creating Data Table Structure

First, we need to create a table containing a vector field to store image information:

```sql
-- Create food image recognition data table
CREATE    TABLE IF NOT EXISTS dish_images (
          id BIGINT NOT NULL PRIMARY KEY IDENTITY (1),
          url STRING NOT NULL COMMENT 'Original URL address of the image',
          file_name STRING NOT NULL COMMENT 'Image file name',
          image_content STRING COMMENT 'Dish information extracted using fc_image_to_text',
          image_vector VECTOR (FLOAT, 1024) COMMENT 'Image vector generated using fc_gen_emmbeding',
          created_at TIMESTAMP DEFAULT current_timestamp() COMMENT 'Creation time'
          )
          COMMENT 'Food image recognition data table';

```

### 2.2 Batch Upload Images to VOLUME

Singdata Lakehouse's VOLUME feature provides file management capabilities. The following example shows how to batch download and upload images from URLs. You can download images from the URLs below to your local machine, and then use the [Lakehouse JDBC Client](connect-with-cli.md) to PUT files into the USER VOLUME:

[Image URL](http://viapi-test.oss-cn-shanghai.aliyuncs.com/viapi-3.0domepic/imagerecog/RecognizeFood/RecognizeFood1.jpg) (You can download more images by changing the number in the URL)

```sql
-- Note: PUT command needs to be executed via the JDBC client, cannot be run directly in the SQL editor
-- Batch download and upload images to USER VOLUME from URLs
PUT 
    '/User/Downloads/RecognizeFood1.jpg',
    '/User/Downloads/RecognizeFood2.jpg',
    '/User/Downloads/RecognizeFood3.jpg' 
TO USER VOLUME SUBDIRECTORY 'dish_images';

-- View uploaded files
LIST USER VOLUME SUBDIRECTORY 'dish_images';
```

### 2.3 Using Functions for Image Recognition

Use cloud functions to achieve automatic image recognition and vectorization:

```sql
-- Insert a single record, calling cloud functions for image recognition and vector generation
INSERT INTO dish_images (url, file_name, image_content, image_vector)
VALUES 
(
    'http://viapi-test.oss-cn-shanghai.aliyuncs.com/viapi-3.0domepic/imagerecog/RecognizeFood/RecognizeFood1.jpg',
    'RecognizeFood1.jpg',
    -- Call image recognition function
    public.fc_image_to_text('dish_recognition', 'http://viapi-test.oss-cn-shanghai.aliyuncs.com/viapi-3.0domepic/imagerecog/RecognizeFood/RecognizeFood1.jpg'),
    -- Generate image vector (note: vector dimensions must match)
    CAST(public.fc_gen_emmbeding('multimodal', '', 'http://viapi-test.oss-cn-shanghai.aliyuncs.com/viapi-3.0domepic/imagerecog/RecognizeFood/RecognizeFood1.jpg') AS VECTOR(FLOAT, 1024))
);

-- Batch insert multiple records
INSERT INTO dish_images (url, file_name, image_content, image_vector)
VALUES 
('http://viapi-test.oss-cn-shanghai.aliyuncs.com/viapi-3.0domepic/imagerecog/RecognizeFood/RecognizeFood2.jpg', 
 'RecognizeFood2.jpg',
 public.fc_image_to_text('dish_recognition', 'http://viapi-test.oss-cn-shanghai.aliyuncs.com/viapi-3.0domepic/imagerecog/RecognizeFood/RecognizeFood2.jpg'),
 CAST(public.fc_gen_emmbeding('multimodal', '', 'http://viapi-test.oss-cn-shanghai.aliyuncs.com/viapi-3.0domepic/imagerecog/RecognizeFood/RecognizeFood2.jpg') AS VECTOR(FLOAT, 1024))
),
('http://viapi-test.oss-cn-shanghai.aliyuncs.com/viapi-3.0domepic/imagerecog/RecognizeFood/RecognizeFood3.jpg', 
 'RecognizeFood3.jpg',
 public.fc_image_to_text('dish_recognition', 'http://viapi-test.oss-cn-shanghai.aliyuncs.com/viapi-3.0domepic/imagerecog/RecognizeFood/RecognizeFood3.jpg'),
 CAST(public.fc_gen_emmbeding('multimodal', '', 'http://viapi-test.oss-cn-shanghai.aliyuncs.com/viapi-3.0domepic/imagerecog/RecognizeFood/RecognizeFood3.jpg') AS VECTOR(FLOAT, 1024))
);
```

### 2.4 Vector Similarity Search

Implement image content-based similarity search:

```sql
-- Find the dishes most similar to the target image
WITH target_vector AS (
    SELECT CAST(public.fc_gen_emmbeding('multimodal', '', 'http://viapi-test.oss-cn-shanghai.aliyuncs.com/viapi-3.0domepic/imagerecog/RecognizeFood/RecognizeFood5.jpg') AS VECTOR(FLOAT, 1024)) as vec
)
SELECT 
    d.id,
    d.file_name,
    d.url,
    d.image_content,
    cosine_distance(d.image_vector, t.vec) as similarity_score
FROM dish_images d, target_vector t
ORDER BY similarity_score ASC
LIMIT 5;

-- Find similar images based on existing images
SELECT 
    d1.file_name as source_image,
    d2.file_name as similar_image,
    d2.image_content,
    cosine_distance(d1.image_vector, d2.image_vector) as similarity_score
FROM dish_images d1, dish_images d2
WHERE d1.file_name = 'RecognizeFood1.jpg'
  AND d1.id != d2.id
ORDER BY similarity_score ASC
LIMIT 5;
```

## 3. Advanced Application Scenarios

### 3.1 Multi-Dimensional Image Analysis

Combine structured queries and vector search to achieve complex analysis requirements:

```sql
-- Find images of specific categories
SELECT 
    id,
    file_name,
    image_content
FROM dish_images
WHERE image_content LIKE '%seafood%' 
   OR image_content LIKE '%fish%'
   OR image_content LIKE '%shrimp%'
   OR image_content LIKE '%crab%'
ORDER BY id;

-- Analyze the confidence distribution of dish recognition results
SELECT 
    file_name,
    image_content,
    -- Extract confidence (adjust based on actual JSON format)
    CAST(SUBSTRING(image_content, 
         POSITION('probability' IN image_content) + 15, 
         8) AS DOUBLE) as confidence
FROM dish_images
ORDER BY confidence DESC;

-- Count dishes by category
SELECT 
    CASE 
        WHEN image_content LIKE '%beef%' THEN 'Beef'
        WHEN image_content LIKE '%fish%' THEN 'Fish'
        WHEN image_content LIKE '%shrimp%' OR image_content LIKE '%crab%' THEN 'Seafood'
        WHEN image_content LIKE '%vegetable%' AND image_content NOT LIKE '%non-vegetable%' THEN 'Vegetables'
        ELSE 'Other'
    END as category,
    COUNT(*) as count
FROM dish_images
WHERE image_content NOT LIKE '%non-vegetable%'
GROUP BY 1
ORDER BY count DESC;
```

### 3.2 Creating Image Processing Pipeline

Use dynamic tables to implement automated data processing:

```sql
-- Create a dynamic table to automatically extract and aggregate dish information
CREATE OR REPLACE DYNAMIC TABLE dish_summary
REFRESH_INTERVAL = '1 HOUR'
AS
SELECT 
    file_name,
    url,
    -- Extract dish name (simplified string processing)
    SUBSTRING(image_content, 
              POSITION('name' IN image_content) + 9,
              POSITION('}' IN SUBSTRING(image_content, POSITION('name' IN image_content))) - 10
    ) as dish_name,
    -- Extract calorie information
    CASE 
        WHEN image_content LIKE '%calorie%' THEN
            SUBSTRING(image_content, 
                     POSITION('calorie' IN image_content) + 12,
                     3)
        ELSE NULL
    END as calorie,
    created_at
FROM dish_images
WHERE image_content IS NOT NULL;

-- View dynamic table data
SELECT * FROM dish_summary;
```

## Conclusion

Through the practical cases and executable code in this article, we have demonstrated the powerful capabilities of Singdata Lakehouse in image data management and analysis. From simple image recognition to complex vector search, from batch processing to real-time analysis, Singdata Lakehouse provides enterprises with a one-stop solution.

Just as embodied by the technical pursuit of MCP Server, the Singdata team's refinement of every functional detail makes this platform not just a data warehouse, but a bridge connecting AI capabilities with business needs. As technology continues to advance, we believe that Singdata Lakehouse will play an increasingly important role in the field of multi-modal data analysis.

***

*This article is written based on the latest version of Singdata Lakehouse, and all SQL code has been tested in actual environments. Specific features may change with version updates. For more technical details, please refer to the official documentation:* <https://singdata.com/documents>
