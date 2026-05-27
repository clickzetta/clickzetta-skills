# Configuring Singdata Lakehouse as a Vector Database in Dify

## Overview

Singdata Lakehouse is a unified lakehouse platform that supports vector data storage and high-performance search. This guide will help you configure Singdata as a vector database in [Dify](https://dify.ai/), replacing the default vector database option and enabling knowledge base management with both full-text and vector retrieval.

## Prerequisites

### 1. System Requirements

* Dify V1.7.2+ platform deployed
* Accessible Singdata Lakehouse instance

### 2. Required Connection Information

Before starting configuration, ensure you have the following Singdata Lakehouse connection information and have created the corresponding `vcluster` and `schema` in advance:

| Parameter    | Description              | Example                                    |
| ----------- | ----------------------- | ----------------------------------------- |
| `username`  | Singdata username       | `your_username`                           |
| `password`  | Singdata password       | `your_password`                           |
| `instance`  | Singdata instance ID    | `your_instance_id`                        |
| `service`   | Service endpoint        | `cn-shanghai-alicloud.api.singdata.com` |
| `workspace` | Workspace name          | `quick_start`                             |
| `vcluster`  | Virtual cluster name    | `default_ap`                              |
| `schema`    | Database schema         | `dify`                                    |

## Dify Configuration File Setup

If using the configuration file approach, add the following to the Dify configuration file (.env):

```
 # ... other configurations

      # Vector database configuration
      VECTOR_STORE=clickzetta

      # Singdata connection configuration
      CLICKZETTA_USERNAME=your_username
      CLICKZETTA_PASSWORD=your_password
      CLICKZETTA_INSTANCE=your_instance_id
      CLICKZETTA_SERVICE=region_id.api.singdata.com
      CLICKZETTA_WORKSPACE=quick_start
      CLICKZETTA_VCLUSTER=default_ap
      CLICKZETTA_SCHEMA=dify

      # Advanced configuration
      CLICKZETTA_BATCH_SIZE=100
      CLICKZETTA_ENABLE_INVERTED_INDEX=true
      CLICKZETTA_ANALYZER_TYPE=chinese
      CLICKZETTA_ANALYZER_MODE=smart
      CLICKZETTA_VECTOR_DISTANCE_FUNCTION=cosine_distance
```

## Verification

### 1. Connection Test

After starting Dify, you can verify the Singdata connection using the following methods:

1. **Check Logs**:

   ```bash
   # View Dify API logs
   docker logs dify-api

   # Find Singdata related logs
   docker logs dify-api | grep -i clickzetta
   ```

2. **Create Knowledge Base Test**:

   * Log in to the Dify admin interface
   * Create a new knowledge base
   * Upload a test document
   * Observe whether the vector index is created successfully

### 2. Feature Verification

Verify the following features in Dify:

* ✅ **Knowledge Base Creation**: Whether a knowledge base can be created successfully
* ✅ **Document Upload**: Whether documents can be uploaded and processed
* ✅ **Vectorized Storage**: Whether documents are correctly vectorized and stored
* ✅ **Similarity Search**: Whether the search function works properly
* ✅ **Q&A Function**: Whether knowledge base-based Q&A is accurate

## Usage Guide

### 1. Knowledge Base Management

#### Creating a Knowledge Base

1. Log in to the Dify admin interface
2. Click "Knowledge Base" → "Create Knowledge Base"
3. Fill in the knowledge base name and description
4. Select an embedding model (recommended to use a model that supports Chinese)
5. Click "Save and Process"

:-: ![](.topwrite/assets/image_1756869694621.png =720)

#### Uploading Documents

1. Click "Upload Document" in the knowledge base
2. Select supported file formats (PDF, Word, TXT, etc.)
3. Configure document chunking rules
4. Click "Save and Process"
5. Wait for document processing to complete

:-: ![](.topwrite/assets/image_1756869771135.png =772)

^

Note: Configuring unstructured.io as the ETL engine in Dify supports additional formats such as PPT files.

^

Singdata Lakehouse supports hybrid retrieval based on inverted index and vector index:

:-: ![](.topwrite/assets/image_1756869923166.png =663)

#### Managing Vector Data

* **View Statistics**: View vector count and storage statistics on the knowledge base details page
* **Update Documents**: Update or delete uploaded documents
* **Search Testing**: Use the search function to test vector retrieval effectiveness

:-: ![](.topwrite/assets/image_1756870050101.png =729)

^

### 2. Application Development

#### Using in Chat Applications

1. Create a new chat application

:-: ![](.topwrite/assets/image_1756870253742.png =701)

1. Associate a knowledge base in "Prompt Orchestration"

2. Configure retrieval settings:

   * **TopK Value**: Recommended 3-5
   * **Similarity Threshold**: Recommended 0.3-0.7
   * **Re-ranking**: Optionally enabled

3. Test Q&A effectiveness

#### Using in Workflows

1. Create a workflow application

2. Add a "Knowledge Retrieval" node

3. Configure retrieval parameters:

   * **Query Variable**: `{{sys.query}}`
   * **Knowledge Base**: Select the target knowledge base
   * **Retrieval Settings**: TopK and similarity threshold

4. Pass retrieval results to the LLM node

## Performance Optimization

### 1. Vector Index Optimization

Singdata Lakehouse automatically creates HNSW indexes for vector fields. You can optimize through the following methods:

```python
# Adjust index parameters in configuration
CLICKZETTA_VECTOR_DISTANCE_FUNCTION = "cosine_distance"  # suitable for text embeddings
# or
CLICKZETTA_VECTOR_DISTANCE_FUNCTION = "l2_distance"      # suitable for image embeddings
```

### 2. Batch Processing Optimization

```python
# Adjust batch processing size
CLICKZETTA_BATCH_SIZE = 200  # increasing batch size improves throughput
```

### 3. Full-Text Search Optimization

```python
# Enable inverted index to support full-text search
CLICKZETTA_ENABLE_INVERTED_INDEX = true
CLICKZETTA_ANALYZER_TYPE = "chinese"  # Chinese word segmentation
CLICKZETTA_ANALYZER_MODE = "smart"    # smart segmentation mode
```

## Monitoring and Maintenance

### 1. Performance Monitoring

Monitor the following key metrics:

* **Connection Status**: Whether the database connection is normal
* **Query Latency**: Vector search response time
* **Throughput**: Number of vector queries processed per second
* **Storage Usage**: Vector data storage space usage

### 2. Log Analysis

Pay attention to the following log information:

```bash
# Connection log
INFO - Singdata connection established successfully

# Vector operation log
INFO - Vector insert completed: 1000 vectors in 2.3s
INFO - Vector search completed: 5 results in 120ms

# Error log
ERROR - Singdata connection failed: ...
WARNING - Vector search timeout: ...
```

### 3. Data Backup

Regularly back up important vector data:

```sql
-- View vector collections
SHOW TABLES IN dify;

-- Back up vector data
CREATE TABLE dify.backup_vectors AS 
SELECT * FROM dify.knowledge_base_vectors;

-- View data statistics
SELECT COUNT(*) FROM dify.knowledge_base_vectors;
```

## Troubleshooting

### Common Issues

#### Q1: Connection Failed

**Symptoms**: Singdata connection error when Dify starts. **Solution**:

1. Check network connectivity
2. Verify username and password
3. Confirm instance ID is correct
4. Check firewall settings

#### Q2: Poor Vector Search Performance

**Symptoms**: Search response time is too long. **Solution**:

1. Check if vector indexes have been created
2. Adjust TopK value
3. Optimize query conditions
4. Consider increasing compute resources

#### Q3: Document Processing Failed

**Symptoms**: Document processing fails after upload. **Solution**:

1. Check if the document format is supported
2. Verify document size limits
3. Check detailed error logs
4. Check vectorization model status

#### Q4: Poor Chinese Search Results

**Symptoms**: Chinese document search results are inaccurate. **Solution**:

1. Enable the Chinese tokenizer
2. Adjust the similarity threshold
3. Use an embedding model that supports Chinese
4. Check document chunking settings

### Useful Resources

* **Dify Official Documentation**: [https://docs.dify.ai](https://docs.dify.ai/)
* **Singdata Documentation**: [https://singdata.com/documents](https://singdata.com/documents)
* **GitHub Issues**: [https://github.com/langgenius/dify/issues](https://github.com/langgenius/dify/issues)
* **Community Forum**: [https://community.dify.ai](https://community.dify.ai/)

***

\*This guide is based on Dify V1.7.2+ and Singdata Lakehouse SaaS version
