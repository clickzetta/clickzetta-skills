# Singdata Lakehouse Unstructured ETL Pipeline Construction Guide

## Overview

This document introduces a complete ETL (Extract, Transform, Load) pipeline solution based on Singdata Lakehouse, DashScope, and Unstructured Ingest, supporting unstructured data processing, vector embedding generation, and knowledge base construction.

## System Architecture

### Unstructured Ingest Framework

Unstructured Ingest is an enterprise-grade document processing and ETL framework with a plugin-based architecture design, supporting connectors for multiple data sources and destinations.

#### Core Design Concepts

```
Data Source → Index → Download → Parse → Chunk → Embed → Stage → Upload → Target Storage
```

**Framework Features**

* **Plugin-based Architecture**: Supports multiple data sources through a connector registration mechanism
* **Pipeline Processing**: Each step is independent, supporting asynchronous and multi-process parallel execution
* **Extensibility**: Supports custom connectors and processors
* **Fault Tolerance**: Built-in retry, error handling, and state management

#### Processing Steps in Detail

1. **Indexer**
   * Connects to data sources, retrieves document metadata
   * Supports incremental updates and change detection
   * Generates processing task queues

2. **Downloader**
   * Downloads documents from data sources to local storage
   * Supports resumable downloads and batch downloading
   * Handles file format conversion

3. **Partitioner**
   * Parses document content and extracts structured information
   * Supports multiple document formats (PDF, DOCX, HTML, etc.)
   * Identifies elements such as headings, paragraphs, tables, and images

4. **Chunker**
   * Splits documents into semantic units
   * Supports multiple chunking strategies (by title, by character count, by semantics)
   * Maintains contextual relevance

5. **Embedder**
   * Generates text vector representations
   * Supports multiple embedding models and services
   * Batch processing for optimized performance

6. **Stager**
   * Data format conversion and preprocessing
   * Adapts to target storage format requirements
   * Data validation and cleansing

7. **Uploader**
   * Uploads processing results to target storage
   * Supports batch uploading and transaction processing
   * Handles conflicts and duplicate data

### Singdata Lakehouse Platform

Singdata Lakehouse is a cloud-native Lakehouse data platform with a compute-storage separation architecture, designed for big data analytics and AI applications.

#### Object Model Architecture

Singdata Lakehouse uses a hierarchical structure to manage resources:

```
Account
 └── User
 └── Lakehouse Instance
     └── Workspace
         ├── Schema
         │   ├── Table
         │   │   └── Table Volume (Bound to Table)
         │   ├── View
         │   ├── Materialized View
         │   └── Named Volume (Schema-level)
         │
         ├── Virtual Cluster
         │   ├── GENERAL (ETL/Batch)
         │   ├── ANALYTICS (Query/BI)
         │   └── INTEGRATION (DataSync)
         │
         └── User Volume (Workspace-level)
```

#### Core Components

1. **Virtual Cluster (VCluster)**

   Provides elastic, scalable compute resources, measured in CRU (Compute Resource Unit):

   | Cluster Type         | Use Case                | Characteristics                          |
   | -------------------- | ----------------------- | ---------------------------------------- |
   | GENERAL              | ETL, batch jobs         | Fair scheduling, resource sharing        |
   | ANALYTICS            | Online queries, BI reports | Multi-instance elastic scaling, high concurrency support |
   | INTEGRATION          | Data integration tasks  | Optimized for ETL pipelines              |

2. **Storage System (Volume)**

   Three Volume types and their hierarchical relationships:

   ```
   User Volume            Table Volume           Named Volume
   ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
   │ Personal Files   │   │ Table-bound      │   │ Schema-scoped    │
   │                  │   │ Files            │   │ Shared Files     │
   │ Protocol:        │   │                  │   │                  │
   │ volume:user://   │   │ Protocol:        │   │ Protocol:        │
   │ ~/filename       │   │ volume:table://  │   │ volume://         │
   │                  │   │ table/filename   │   │ volume/filename  │
   │ Level: Workspace │   │                  │   │                  │
   │ Scope: User      │   │ Level: Table     │   │ Level: Schema    │
   │ Access: User R/W │   │ Bound: Specific  │   │ Access: Custom   │
   │                  │   │ Table            │   │ Cross-team       │
   └──────────────────┘   └──────────────────┘   └──────────────────┘
   ```

3. **Unified Data Interface**

   * **SQL Interface**: Standard SQL queries and management
   * **Python API**: Programmatic access and automation
   * **JDBC/ODBC**: Enterprise application integration
   * **REST API**: Cloud-native application access

#### Volume Types in Detail

**User Volume**

* **Level**: Workspace level, user personal storage space
* **Binding**: Bound to a user, similar to an operating system user home directory
* **Permissions**: User has read/write permissions by default
* **Protocol**: `volume:user://~/filename`
* **Operations**: PUT, GET, LIST, REMOVE, SELECT FROM VOLUME

**Table Volume**

* **Level**: Table level, bound to a specific data table
* **Binding**: Each table is automatically associated with a dedicated Volume
* **Permissions**: Inherits table permissions (SELECT/INSERT/UPDATE/DELETE)
* **Protocol**: `volume:table://table_name/filename`
* **Typical Scenarios**: COPY INTO data import, ETL temporary file storage

**Named Volume**

* **Level**: Schema level, explicitly created named storage volume
* **Binding**: Belongs to a specific Schema, supports cross-table sharing
* **Permissions**: Supports custom permission assignment and cross-team collaboration
* **Protocol**: `volume://volume_name/path`
* **Typical Scenarios**: Data sharing within a Schema, batch data processing

#### Vector Capabilities

Singdata Lakehouse has built-in vector processing capabilities, optimized for RAG (Retrieval-Augmented Generation) applications:

* **Vector Index**: Supports HNSW efficient indexing algorithm
* **Multi-Dimensional Support**: 512/768/1024/1536 and other multi-dimensional vectors
* **Hybrid Search**: Vector similarity + full-text search + traditional SQL queries
* **Real-Time Updates**: Supports real-time insertion and updating of vector data

#### Compute Resource Specifications

| Type        | Min Spec (CRU) | Max Spec (CRU) | Step Rule                |
| ----------- | -------------- | -------------- | ------------------------ |
| GENERAL     | 1              | 256            | 1 CRU step              |
| ANALYTICS   | 1              | 256            | Powers of 2 CRU         |
| INTEGRATION | 0.25           | 256            | 0.25/0.5/1+ CRU steps  |

#### Workspace Isolation

* **Multi-Tenant Architecture**: Account → Instance → Workspace multi-layer isolation
* **Permission Control**: Fine-grained permission management based on users and roles
* **Resource Isolation**: Compute and storage resources isolated between different workspaces
* **Cross-Space Sharing**: Supports secure data sharing across workspaces

### DashScope Embedding Service

DashScope is a large model service platform provided by Alibaba Cloud, offering high-quality text embedding capabilities.

#### Model Architecture

DashScope text embedding processing flow:

```
Input Text → Tokenizer → Transformer → Pooling → Normalize → Vector Output
    │            │            │           │          │           │
 CN/EN Text   Subword     Multi-Head    Average    L2 Norm    1024-dim
               Split      Attention     Pooling              Vector
```

### Integration Architecture

The system adopts a three-layer architecture to achieve a complete data processing lifecycle:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Application Layer                            │
│  RAG | Knowledge Base | Search | BI Analytics | API Services    │
└─────────────────────────────────────────────────────────────────┘
                                ↑
┌─────────────────────────────────────────────────────────────────┐
│                     ETL Processing Layer                        │
│                                                                 │
│  Data Source      Framework       Embedding       Target        │
│ ┌─────────┐     ┌─────────────┐   ┌─────────────┐ ┌─────────┐   │
│ │ Volume  │────▶│Unstructured │──▶│ DashScope   │▶│ SQL     │   │
│ │ Files   │     │• Doc Parse  │   │• v1/v2/v3/v4│ │ Tables  │   │
│ │ SQL     │     │• Chunking   │   │• Batch      │ │• Vector │   │
│ └─────────┘     │• Multi-Src  │   │• Vectorize  │ │• Meta   │   │
│                 └─────────────┘   └─────────────┘ └─────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                ↑
┌─────────────────────────────────────────────────────────────────┐
│                    Singdata Lakehouse Platform                   │
│                                                                 │
│  Compute Layer      Storage Layer       Service Layer           │
│ ┌─────────────┐   ┌─────────────────┐  ┌─────────────────┐      │
│ │ General VC  │   │ User Volume     │  │ Metadata Mgmt   │      │
│ │ Analytics   │◀─▶│ Table Volume    │◀▶│ Access Control  │      │
│ │ Integration │   │ Named Volume    │  │ Task Scheduling │      │
│ │ Vector Idx  │   │ SQL Storage     │  │ Monitoring      │      │
│ └─────────────┘   └─────────────────┘  └─────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

#### Data Flow

**Typical ETL Flow**:

1. **Source Data** → Volume file volumes or SQL tables
2. **Index Scan** → Unstructured framework identifies documents to process
3. **Smart Parsing** → Document partitioning, structured extraction
4. **Vectorization** → DashScope generates text embeddings
5. **Storage** → Singdata Lakehouse SQL tables (with vector columns)
6. **Application** → RAG retrieval, knowledge Q&A, data analysis

### Core Components

1. **Singdata Lakehouse SQL Connector** - For relational database operations and RAG retrieval systems
2. **Singdata Lakehouse Volume Connector** - For file system operations (user volumes, table volumes, named volumes)
3. **DashScope Embedding Service** - Supports text vectorization across 4 model versions
4. **Unstructured Data Processing** - Document parsing, partitioning, and structuring

## Quick Start

### Environment Setup

```bash
# Install dependencies
pip install unstructured-ingest-clickzetta

# Configure environment variables
export CLICKZETTA_SERVICE="your-service-url"
export CLICKZETTA_USERNAME="your-username"
export CLICKZETTA_PASSWORD="your-password"
export CLICKZETTA_WORKSPACE="your-workspace"
export CLICKZETTA_SCHEMA="your-schema"
export CLICKZETTA_INSTANCE="your-instance"
export CLICKZETTA_VCLUSTER="your-vcluster"

# DashScope configuration
export DASHSCOPE_API_KEY="your-dashscope-api-key"
```

### Verify Installation

```python
from unstructured_ingest.processes.connectors.sql.clickzetta import ClickzettaConnectionConfig
from unstructured_ingest.embed.dashscope import DashScopeEmbeddingConfig

# Test Singdata Lakehouse connection
config = ClickzettaConnectionConfig()
with config.get_session() as session:
    result = session.sql("SELECT 1").collect()
    print("Singdata Lakehouse connection successful")

# Test DashScope connection
embed_config = DashScopeEmbeddingConfig(model_name="text-embedding-v3")
print("DashScope configuration ready")
```

## Usage Scenarios

### Scenario 1: Singdata Lakehouse SQL Data Processing

Suitable for batch processing and vectorization of relational database tables.

#### Basic Indexing and Downloading

```python
from unstructured_ingest.processes.connectors.sql.clickzetta import (
    ClickzettaConnectionConfig,
    ClickzettaIndexer,
    ClickzettaIndexerConfig,
    ClickzettaDownloader,
    ClickzettaDownloaderConfig
)

# Connection configuration
connection_config = ClickzettaConnectionConfig()

# Indexer configuration - process table data in batches
indexer = ClickzettaIndexer(
    connection_config=connection_config,
    index_config=ClickzettaIndexerConfig(
        table_name="documents",
        id_column="id",
        batch_size=1000,
        # Optional: add WHERE clause to filter data
        # where_clause="created_at > '2024-01-01'"
    )
)

# Downloader configuration
downloader = ClickzettaDownloader(
    connection_config=connection_config,
    download_config=ClickzettaDownloaderConfig(
        fields=["id", "title", "content"],
        download_dir="/path/to/download"
    )
)

# Execute data processing
for file_data in indexer.run():
    downloaded_files = downloader.run(file_data=file_data)
    print(f"Processing complete: {len(downloaded_files)} files")
```

#### Vector Embedding Processing

```python
from unstructured_ingest.embed.dashscope import DashScopeEmbeddingConfig
from unstructured_ingest.processes.connectors.sql.clickzetta import (
    ClickzettaUploader,
    ClickzettaUploaderConfig
)

# DashScope embedding configuration
embed_config = DashScopeEmbeddingConfig(
    model_name="text-embedding-v3",  # Supports v1/v2/v3/v4
    batch_size=25,
    text_field="content",
    # Dimensions for different versions:
    # v1: 1536-dim, v2: 1536-dim, v3: 1024-dim, v4: 1024-dim
)

# Uploader configuration - supports vector fields
uploader = ClickzettaUploader(
    connection_config=connection_config,
    upload_config=ClickzettaUploaderConfig(
        table_name="document_vectors",
        # Vector field configuration
        vector_column="embedding",
        vector_dimension=1024,  # Corresponds to v3/v4 models
        batch_size=100
    )
)

# Process documents and generate vectors
processed_data = []
for file_data in indexed_files:
    # Generate embeddings using DashScope
    embeddings = embed_config.embed_documents([file_data['content']])

    processed_data.append({
        'id': file_data['id'],
        'content': file_data['content'],
        'embedding': embeddings[0]
    })

# Batch upload to Singdata Lakehouse
uploader.upload_batch(processed_data)
```

### Scenario 2: Singdata Lakehouse Volume File Processing

Suitable for file-system-level data processing, supporting three volume types.

#### Volume Type Descriptions

1. **User Volume** -- User personal file space
2. **Table Volume** -- File storage associated with a data table
3. **Named Volume** -- Named shared file volume

#### File Indexing and Downloading

```python
from unstructured_ingest.processes.connectors.fsspec.clickzetta_volume import (
    ClickzettaVolumeConnectionConfig,
    ClickzettaVolumeIndexer,
    ClickzettaVolumeIndexerConfig,
    ClickzettaVolumeDownloader,
    ClickzettaVolumeDownloaderConfig
)

# Connection configuration
connection_config = ClickzettaVolumeConnectionConfig()

# Index different volume types
configs = [
    # User Volume
    ClickzettaVolumeIndexerConfig(
        index_volume_type="user",
        index_remote_path="documents/"  # Optional: specify subdirectory
    ),
    # Table Volume
    ClickzettaVolumeIndexerConfig(
        index_volume_type="table",
        index_volume_name="document_table",
        index_remote_path="images/"
    ),
    # Named Volume
    ClickzettaVolumeIndexerConfig(
        index_volume_type="named",
        index_volume_name="shared_data_volume",
        index_regexp=r".*\.pdf$"  # Optional: regex filtering
    )
]

# Process each volume type
for config in configs:
    indexer = ClickzettaVolumeIndexer(
        connection_config=connection_config,
        index_config=config
    )

    # Get file list
    files = indexer.list_files()
    print(f"Found {len(files)} files in volume {config.volume_type}")

    # Download files
    downloader = ClickzettaVolumeDownloader(
        connection_config=connection_config,
        download_config=ClickzettaVolumeDownloaderConfig(),
        index_config=config
    )

    downloaded = downloader.run(files=files)
    print(f"Download complete: {len(downloaded)} files")
```

#### File Upload

```python
from unstructured_ingest.processes.connectors.fsspec.clickzetta_volume import (
    ClickzettaVolumeUploader,
    ClickzettaVolumeUploaderConfig
)

# Uploader configuration
uploader = ClickzettaVolumeUploader(
    connection_config=connection_config,
    upload_config=ClickzettaVolumeUploaderConfig(
        volume_type="named",
        volume_name="processed_documents",
        remote_path="output/"
    )
)

# Upload processed files
local_files = ["/path/to/processed1.json", "/path/to/processed2.json"]
for local_file in local_files:
    uploader.upload_file(local_file, "processed/" + os.path.basename(local_file))
```

### Scenario 3: Complete ETL Pipeline

Combine SQL and Volume connectors to build an end-to-end ETL pipeline.

#### Data Flow Architecture

```
Raw Documents → Singdata Lakehouse Volume → Processing → DashScope Embeddings → Singdata Lakehouse SQL → Retrieval System
```

#### Complete Example

```python
import asyncio
from pathlib import Path
from unstructured_ingest.interfaces import PartitionConfig
from unstructured_ingest.embed.dashscope import DashScopeEmbeddingConfig

async def complete_etl_pipeline():
    """Complete ETL pipeline example"""

    # Step 1: Read raw documents from Volume
    volume_indexer = ClickzettaVolumeIndexer(
        connection_config=ClickzettaVolumeConnectionConfig(),
        index_config=ClickzettaVolumeIndexerConfig(
            index_volume_type="named",
            index_volume_name="raw_documents",
            index_regexp=r".*\.(pdf|docx|txt)$"
        )
    )

    # Step 2: Download and parse documents
    volume_downloader = ClickzettaVolumeDownloader(
        connection_config=volume_indexer.connection_config,
        download_config=ClickzettaVolumeDownloaderConfig(),
        index_config=volume_indexer.index_config
    )

    raw_files = volume_indexer.list_files()
    downloaded = volume_downloader.run(files=raw_files)

    # Step 3: Document partitioning and structuring
    partition_config = PartitionConfig(
        strategy="hi_res",
        pdf_infer_table_structure=True,
        chunking_strategy="by_title",
        max_characters=1000,
        overlap=100
    )

    processed_documents = []
    for file_info in downloaded:
        # Process each document
        from unstructured.partition.auto import partition

        elements = partition(
            filename=str(file_info['local_path']),
            **partition_config.dict()
        )

        # Convert to document chunks
        for element in elements:
            processed_documents.append({
                'source_file': file_info['remote_path'],
                'content': str(element),
                'element_type': element.category,
                'metadata': element.metadata.to_dict() if element.metadata else {}
            })

    # Step 4: Generate vector embeddings
    embed_config = DashScopeEmbeddingConfig(
        model_name="text-embedding-v3",
        batch_size=25
    )

    # Batch generate embeddings
    contents = [doc['content'] for doc in processed_documents]
    embeddings = embed_config.embed_documents(contents)

    # Add vectors to documents
    for doc, embedding in zip(processed_documents, embeddings):
        doc['embedding'] = embedding
        doc['vector_model'] = "text-embedding-v3"
        doc['vector_dimension'] = 1024

    # Step 5: Store in Singdata Lakehouse SQL table
    sql_uploader = ClickzettaUploader(
        connection_config=ClickzettaConnectionConfig(),
        upload_config=ClickzettaUploaderConfig(
            table_name="document_knowledge_base",
            vector_column="embedding",
            vector_dimension=1024,
            batch_size=100
        )
    )

    # Batch upload
    await sql_uploader.upload_batch_async(processed_documents)

    print(f"ETL pipeline complete: processed {len(processed_documents)} document chunks")
    return processed_documents

# Run the pipeline
if __name__ == "__main__":
    results = asyncio.run(complete_etl_pipeline())
```

## CLI Command Reference

### Singdata Lakehouse SQL Connector

```bash
# Basic data extraction
unstructured-ingest \
    clickzetta \
    --table-name documents \
    --id-column id \
    --batch-size 1000 \
    --fields id,title,content \
    --output-dir ./output

# Extraction with filter conditions
unstructured-ingest \
    clickzetta \
    --table-name documents \
    --where-clause "created_at > '2024-01-01'" \
    --id-column id \
    --fields id,content \
    --output-dir ./filtered_output

# Vectorization processing
unstructured-ingest \
    clickzetta \
    --table-name source_docs \
    --embed-provider dashscope \
    --embedding-model-name text-embedding-v3 \
    --output-dir ./vectorized
```

### Singdata Lakehouse Volume Connector

```bash
# User Volume processing
unstructured-ingest \
    clickzetta-volume \
    --volume-type user \
    --remote-path documents/ \
    --output-dir ./user_docs

# Table Volume processing
unstructured-ingest \
    clickzetta-volume \
    --volume-type table \
    --volume-name document_table \
    --remote-path images/ \
    --output-dir ./table_files

# Named Volume processing (with regex filtering)
unstructured-ingest \
    clickzetta-volume \
    --volume-type named \
    --volume-name shared_data \
    --regexp ".*\.pdf$" \
    --output-dir ./pdf_files

# Document partitioning configuration
unstructured-ingest \
    clickzetta-volume \
    --volume-type named \
    --volume-name documents \
    --partition-strategy hi_res \
    --chunking-strategy by_title \
    --max-characters 1000 \
    --overlap 100 \
    --additional-partition-args '{"split_pdf_page": true}' \
    --output-dir ./chunked_docs
```

### Upload to Singdata Lakehouse

```bash
# Upload processed data to SQL table
unstructured-ingest \
    local \
    --input-path ./processed_docs \
    --output-dir ./staging \
    --destination clickzetta \
    --table-name processed_documents \
    --batch-size 100

# Upload files to Volume
unstructured-ingest \
    local \
    --input-path ./files_to_upload \
    --output-dir ./staging \
    --destination clickzetta-volume \
    --volume-type named \
    --volume-name output_volume \
    --remote-path processed/
```

## DashScope Embedding Models in Detail

### Supported Model Versions

| Model Version       | Dimensions | Max Input Length | Use Case                       |
| ------------------- | ---------- | ---------------- | ------------------------------ |
| text-embedding-v1   | 1536       | 2048 tokens      | General text embedding         |
| text-embedding-v2   | 1536       | 2048 tokens      | Improved semantic understanding |
| text-embedding-v3   | 1024       | 8192 tokens      | Optimized for long text        |
| text-embedding-v4   | 1024       | 8192 tokens      | Latest version, best performance |

#### Embedding Configuration Examples

```python
# Configuration for different versions
configs = {
    "v1": DashScopeEmbeddingConfig(
        model_name="text-embedding-v1",
        batch_size=20,
        max_retries=3,
        dimensions=1536
    ),
    "v3": DashScopeEmbeddingConfig(
        model_name="text-embedding-v3",
        batch_size=25,
        max_retries=3,
        dimensions=1024
    ),
    "v4": DashScopeEmbeddingConfig(
        model_name="text-embedding-v4",
        batch_size=30,
        max_retries=3,
        dimensions=1024
    )
}

# Choose the appropriate model
embed_config = configs["v4"]  # Recommended: use the latest version
```

## Best Practices

### Performance Optimization

1. **Batch Processing Sizes**
   * SQL Connector: 1000-5000 rows/batch
   * Volume Connector: 100-500 files/batch
   * DashScope Embedding: 20-30 documents/batch

2. **Memory Management**
   ```python
   # For large datasets, use streaming processing
   for batch in indexer.run():
       processed = downloader.run(file_data=batch)
       # Process immediately to avoid memory accumulation
       process_batch(processed)
       del processed  # Explicitly free memory
   ```

3. **Error Handling**
   ```python
   import time
   from unstructured_ingest.errors_v2 import UserAuthError, UserError

   def robust_processing(files, max_retries=3):
       for file_data in files:
           for attempt in range(max_retries):
               try:
                   result = process_file(file_data)
                   break
               except UserAuthError:
                   # Authentication error, do not retry
                   raise
               except UserError as e:
                   if attempt == max_retries - 1:
                       raise
                   time.sleep(2 ** attempt)  # Exponential backoff
   ```

### Data Quality Assurance

1. **Input Validation**
   ```python
   def validate_input_data(data):
       required_fields = ['id', 'content']
       for item in data:
           if not all(field in item for field in required_fields):
               raise ValueError(f"Missing required fields: {required_fields}")
           if not item['content'].strip():
               raise ValueError("Content cannot be empty")
   ```

2. **Output Validation**
   ```python
   def validate_embeddings(embeddings, expected_dimension):
       for i, embedding in enumerate(embeddings):
           if len(embedding) != expected_dimension:
               raise ValueError(f"Embedding {i} dimension error: {len(embedding)} != {expected_dimension}")
   ```

### Monitoring and Logging

```python
import logging
from unstructured_ingest.logger import logger

# Configure detailed logging
logging.getLogger("unstructured_ingest").setLevel(logging.DEBUG)

# Add performance monitoring
import time
from contextlib import contextmanager

@contextmanager
def timer(description):
    start = time.time()
    yield
    elapsed = time.time() - start
    logger.info(f"{description} took: {elapsed:.2f} seconds")

# Usage example
with timer("Document processing"):
    processed = process_documents(documents)
```

## Troubleshooting

### Common Issues

1. **Connection Failure**
   ```
   Error: Failed to create clickzetta session
   Solution: Check environment variable configuration and ensure network connectivity
   ```

2. **Embedding Generation Failure**
   ```
   Error: DashScope API key invalid
   Solution: Verify the DASHSCOPE_API_KEY environment variable
   ```

3. **File Download Failure**
   ```
   Error: No matching files found in Volume 'xxx'
   Solution: Check whether the volume name and path are correct
   ```

### Debugging Tips

1. **Enable Detailed Logging**
   ```python
   import os
   os.environ["UNSTRUCTURED_LOG_LEVEL"] = "DEBUG"
   ```

2. **Test Connections**
   ```python
   # Test Singdata Lakehouse connection
   with ClickzettaConnectionConfig().get_session() as session:
       result = session.sql("SELECT CURRENT_TIMESTAMP()").collect()
       print("Connection OK")

   # Test DashScope
   from unstructured_ingest.embed.dashscope import DashScopeEmbeddingConfig
   config = DashScopeEmbeddingConfig(model_name="text-embedding-v3")
   embeddings = config.embed_documents(["test text"])
   print(f"Embedding dimension: {len(embeddings[0])}")
   ```

3. **Verify Data Flow**
   ```python
   # Output sample data at each stage
   logger.info(f"Index stage: found {len(indexed_files)} files")
   logger.info(f"Download stage: processed {len(downloaded_files)} files")
   logger.info(f"Embedding stage: generated {len(embeddings)} vectors")
   ```

## Enterprise Deployment

### Dockerized Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV UNSTRUCTURED_LOG_LEVEL=INFO

# Run ETL pipeline
CMD ["python", "etl_pipeline.py"]
```

### Kubernetes Configuration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: lakehouse-config
data:
  CLICKZETTA_SERVICE: "your-service-url"
  CLICKZETTA_WORKSPACE: "your-workspace"

---
apiVersion: v1
kind: Secret
metadata:
  name: lakehouse-secrets
type: Opaque
stringData:
  CLICKZETTA_PASSWORD: "your-password"
  DASHSCOPE_API_KEY: "your-api-key"

---
apiVersion: batch/v1
kind: CronJob
metadata:
  name: etl-pipeline
spec:
  schedule: "0 2 * * *"  # Runs daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: etl
            image: your-registry/lakehouse-etl:latest
            envFrom:
            - configMapRef:
                name: lakehouse-config
            - secretRef:
                name: lakehouse-secrets
          restartPolicy: OnFailure
```

### Production Configuration

```python
# production_config.py
import os
from dataclasses import dataclass

@dataclass
class ProductionConfig:
    # Singdata Lakehouse configuration
    clickzetta_service: str = os.getenv("CLICKZETTA_SERVICE")
    clickzetta_pool_size: int = int(os.getenv("CLICKZETTA_POOL_SIZE", "10"))

    # DashScope configuration
    dashscope_api_key: str = os.getenv("DASHSCOPE_API_KEY")
    dashscope_rate_limit: int = int(os.getenv("DASHSCOPE_RATE_LIMIT", "100"))

    # Processing configuration
    batch_size: int = int(os.getenv("BATCH_SIZE", "1000"))
    max_workers: int = int(os.getenv("MAX_WORKERS", "4"))

    # Monitoring configuration
    enable_metrics: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    metrics_port: int = int(os.getenv("METRICS_PORT", "9090"))

config = ProductionConfig()
```

## Reference Links

* [Singdata Lakehouse Official Documentation](https://www.singdata.com/)
* [unstructured-ingest-clickzetta Project](https://github.com/yunqiqiliang/unstructured-ingest-clickzetta)
* [Unstructured Project](https://github.com/Unstructured-IO/unstructured)
