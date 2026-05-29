# Singdata Lakehouse Unstructured ETL Python API Reference

## Architecture Overview

### System Component Relationships

The system adopts a layered architecture with clear responsibilities for each component:

```
┌──────────────────────────────────────────────────────────┐
│                    Application Layer                     │
│    RAG    KB    Search    BI    DataSci    APIs          │
└──────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────┐
│                  ETL Processing Layer                    │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐  │
│ │Unstructured │ │ DashScope   │ │   Data Pipeline     │  │
│ │             │ │             │ │                     │  │
│ │  Doc Parse  │ │  Embedding  │ │      Quality        │  │
│ │  Chunking   │ │  4 Models   │ │     Transform       │  │
│ │  Multi-Src  │ │   Batch     │ │     Metadata        │  │
│ └─────────────┘ └─────────────┘ └─────────────────────┘  │
└──────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────┐
│               Singdata Lakehouse Platform                │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐  │
│ │Compute Layer│ │Storage Layer│ │   Service Layer     │  │
│ │             │ │             │ │                     │  │
│ │ General VC  │ │ User Volume │ │     Metadata        │  │
│ │ Analytics   │ │ Table Vol   │ │   Access Ctrl       │  │
│ │ Integration │ │ Named Vol   │ │   Scheduling        │  │
│ │ Vector Idx  │ │ SQL Storage │ │   Monitoring        │  │
│ └─────────────┘ └─────────────┘ └─────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

### Data Flow Patterns

#### 1. Batch ETL Mode
```
┌─────────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│Volume Source│→ │  Index   │→ │ Download │→ │Document  │→ │ Chunk    │→ │ Vector   │→ │SQL Store │
│             │  │  Scan    │  │          │  │ Parse    │  │Process   │  │Generate  │  │          │
│ File Scan   │  │Metadata  │  │ Local    │  │ Doc      │  │ Text     │  │ Vector   │  │ Table    │
│ Recursive   │  │Extract   │  │ Cache    │  │ Split    │  │ Blocks   │  │Generate  │  │ Insert   │
└─────────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘
```
- **Use Case**: Large-scale document processing, offline data lake construction
- **Compute Resources**: General VCluster + large CRU
- **Storage Mode**: Named Volume → SQL table + vector column

#### 2. Real-Time Stream Processing Mode
```
┌─────────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│Stream Source│→ │ Receive  │→ │ Process  │→ │Vectorize │→ │ Update   │→ │ Search   │
│             │  │          │  │          │  │          │  │          │  │          │
│Stream Input │  │ Buffer   │  │Increment │  │Embedding │  │ Live     │  │ Online   │
│ Data Feed   │  │ Queue    │  │Transform │  │Generate  │  │ Sync     │  │Retrieval │
└─────────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘
```
- **Use Case**: Real-time knowledge base updates, online RAG systems
- **Compute Resources**: Analytics VCluster + multi-instance elastic scaling
- **Storage Mode**: Table Volume + real-time SQL updates

#### 3. Hybrid Processing Mode
```
┌─────────────┐
│Batch Process│ ┐
│             │ │  ┌──────────────────┐    ┌──────────────┐
│Historical   │ ├─→│ Unified Vector   │ ──→│ Hybrid       │
│Data Process │ │  │ Space            │    │ Search       │
└─────────────┘ │  │                  │    │              │
┌─────────────┐ │  │ Combined         │    │ Vector +     │
│Stream Update│ ┘  │ Vector Index     │    │ Text Search  │
│             │    │                  │    │              │
│Real-time    │    └──────────────────┘    └──────────────┘
│Process      │
└─────────────┘
```
- **Use Case**: Enterprise knowledge management, intelligent customer service systems
- **Compute Resources**: Multiple VCluster types working together
- **Storage Mode**: Multi-tier Volume + unified SQL view

## Core Classes and Interfaces

### Singdata Lakehouse SQL Connector

#### ClickzettaConnectionConfig

Database connection configuration class.

```python
class ClickzettaConnectionConfig(SqlConnectionConfig):
    """Singdata Lakehouse database connection configuration"""

    def __init__(
        self,
        service: Optional[str] = None,
        username: Optional[str] = None,
        workspace: Optional[str] = None,
        vcluster: Optional[str] = None,
        schema: Optional[str] = None,
        instance: Optional[str] = None,
        access_config: Optional[ClickzettaAccessConfig] = None
    ):
        """
        Args:
            service: Singdata Lakehouse service address
            username: Username
            workspace: Workspace name
            vcluster: Virtual cluster name
            schema: Database schema name
            instance: Instance name
            access_config: Access configuration (contains sensitive info such as password)
        """
```

**Methods:**

- `get_session() -> Session`: Create a database session
- `wrap_error(e: Exception) -> Exception`: Wrap exception information

#### ClickzettaIndexerConfig

Indexer configuration class for defining data extraction parameters.

```python
class ClickzettaIndexerConfig(SqlIndexerConfig):
    """Singdata Lakehouse indexer configuration"""

    table_name: str  # Table name
    id_column: str = "id"  # Primary key column name
    batch_size: int = 1000  # Batch processing size
    where_clause: Optional[str] = None  # WHERE clause
```

#### ClickzettaIndexer

Data indexer for fetching data in batches.

```python
class ClickzettaIndexer(SqlIndexer):
    """Singdata Lakehouse data indexer"""

    def run(self) -> Generator[FileData, None, None]:
        """
        Run the indexer, yielding data in batches

        Yields:
            FileData: File data object for each batch
        """
```

#### ClickzettaDownloaderConfig

Downloader configuration class.

```python
class ClickzettaDownloaderConfig(SqlDownloaderConfig):
    """Singdata Lakehouse downloader configuration"""

    fields: List[str]  # List of fields to download
    download_dir: Path  # Download directory
    where_clause: Optional[str] = None  # Additional WHERE condition
```

#### ClickzettaDownloader

Data downloader that downloads indexed data locally.

```python
class ClickzettaDownloader(SqlDownloader):
    """Singdata Lakehouse data downloader"""

    def run(self, file_data: FileData) -> List[Dict[str, Any]]:
        """
        Download data for the specified batch

        Args:
            file_data: File data object returned by the indexer

        Returns:
            List[Dict]: List of downloaded data records
        """

    async def run_async(self, file_data: FileData) -> List[Dict[str, Any]]:
        """Async version of the download method"""
```

#### ClickzettaUploaderConfig

Uploader configuration class.

```python
class ClickzettaUploaderConfig(SqlUploaderConfig):
    """Singdata Lakehouse uploader configuration"""

    table_name: str  # Target table name
    batch_size: int = 100  # Batch upload size
    vector_column: Optional[str] = None  # Vector column name
    vector_dimension: Optional[int] = None  # Vector dimension
    create_table_if_not_exists: bool = True  # Auto-create table
```

#### ClickzettaUploader

Data uploader that uploads processed data to Singdata Lakehouse.

```python
class ClickzettaUploader(SqlUploader):
    """Singdata Lakehouse data uploader"""

    def upload_batch(self, data: List[Dict[str, Any]]) -> None:
        """
        Batch upload data

        Args:
            data: List of data records to upload
        """

    async def upload_batch_async(self, data: List[Dict[str, Any]]) -> None:
        """Async batch upload"""

    def _upload_data_batch(
        self,
        data: List[Dict[str, Any]],
        file_data: FileData
    ) -> None:
        """Internal batch upload method"""
```

### Singdata Lakehouse Volume Connector

#### ClickzettaVolumeConnectionConfig

Volume connection configuration class.

```python
class ClickzettaVolumeConnectionConfig(FsspecConnectionConfig):
    """Singdata Lakehouse Volume connection configuration"""

    def get_client(self, protocol: str = "s3") -> Generator[Session, None, None]:
        """
        Get a Singdata Lakehouse session client

        Args:
            protocol: Protocol type (default s3)

        Yields:
            Session: Singdata Lakehouse session object
        """
```

#### ClickzettaVolumeIndexerConfig

Volume indexer configuration class.

```python
class ClickzettaVolumeIndexerConfig(FsspecIndexerConfig):
    """Singdata Lakehouse Volume indexer configuration"""

    index_volume_type: str  # Volume type: 'user', 'table', 'named'
    index_volume_name: Optional[str] = None  # Volume name
    index_remote_path: Optional[str] = None  # Remote path
    index_regexp: Optional[str] = None  # Regex filtering

    @property
    def volume(self) -> str:
        """Build the complete volume identifier"""
```

**Volume Type Descriptions:**

- `user`: User personal volume, does not require index_volume_name
- `table`: Table-associated volume, requires table name as index_volume_name
- `named`: Named volume, requires volume name as index_volume_name

#### ClickzettaVolumeIndexer

Volume file indexer.

```python
class ClickzettaVolumeIndexer(FsspecIndexer):
    """Singdata Lakehouse Volume file indexer"""

    def list_files(self) -> List[Dict[str, Any]]:
        """
        List files in the Volume

        Returns:
            List[Dict]: List of file information, including name, path, size, last_modified, etc.
        """

    def get_file_info(self) -> List[Dict[str, Any]]:
        """Get file information, alias for list_files"""
```

#### ClickzettaVolumeDownloaderConfig

Volume downloader configuration class.

```python
class ClickzettaVolumeDownloaderConfig(FsspecDownloaderConfig):
    """Singdata Lakehouse Volume downloader configuration"""

    download_volume_type: Optional[str] = None  # Volume type: 'user', 'table', 'named'
    download_volume_name: Optional[str] = None  # Volume name
    download_remote_path: Optional[str] = None  # Remote path
    remote_url: Optional[str] = None   # Remote URL
    download_regexp: Optional[str] = None       # Regex filtering

    @property
    def volume(self) -> str:
        """Build the complete volume identifier"""
        # Automatically built from download_volume_type and download_volume_name
```

#### ClickzettaVolumeDownloader

Volume file downloader with smart error handling and path repair.

```python
class ClickzettaVolumeDownloader(FsspecDownloader):
    """Singdata Lakehouse Volume file downloader"""

    def download_file(
        self,
        remote_path: str,
        local_path: str,
        file_info: Optional[Dict] = None
    ) -> None:
        """
        Download a single file

        Args:
            remote_path: Remote file path
            local_path: Local save path
            file_info: File information dictionary (used to auto-infer volume)

        Raises:
            FileNotFoundError: File does not exist in the Volume
            Exception: An error occurred during download

        Notes:
            - Automatically handles cases where Singdata creates directories instead of files
            - Intelligently detects and handles XML error responses
            - Ensures correctness of download paths
        """

    def run(
        self,
        files: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Batch download files

        Args:
            files: List of files to download

        Returns:
            List[Dict]: List of download results, containing:
                - remote_path: Remote file path
                - local_path: Local file path
                - status: 'success' or 'failed'
                - error: Error message (if failed)
        """
```

#### ClickzettaVolumeUploaderConfig

Volume uploader configuration class.

```python
class ClickzettaVolumeUploaderConfig(FsspecUploaderConfig):
    """Singdata Lakehouse Volume uploader configuration"""

    volume_type: Optional[str] = None  # Volume type: 'user', 'table', 'named'
    volume_name: Optional[str] = None  # Volume name
    remote_path: Optional[str] = None  # Remote path
    remote_url: Optional[str] = None   # Remote URL
    regexp: Optional[str] = None       # Regex filtering

    def __init__(self, **data):
        """Initialize configuration, automatically build remote_url"""
        # If remote_url is not provided, it will be auto-built from volume_type, volume_name, and remote_path

    @property
    def volume(self) -> str:
        """Build the complete volume identifier"""
        # Automatically built from volume_type and volume_name
```

#### ClickzettaVolumeUploader

Volume file uploader.

```python
class ClickzettaVolumeUploader(FsspecUploader):
    """Singdata Lakehouse Volume file uploader"""

    def upload_file(
        self,
        local_path: str,
        remote_path: Optional[str] = None
    ) -> None:
        """
        Upload a single file

        Args:
            local_path: Local file path
            remote_path: Remote save path
        """
```

#### ClickzettaVolumeDeleterConfig

Volume deleter configuration class.

```python
class ClickzettaVolumeDeleterConfig:
    """Singdata Lakehouse Volume deleter configuration"""

    delete_volume_type: Optional[str] = None  # Volume type: 'user', 'table', 'named'
    delete_volume_name: Optional[str] = None  # Volume name

    @property
    def volume(self) -> str:
        """Build the complete volume identifier"""
        # Automatically built from delete_volume_type and delete_volume_name
```

#### ClickzettaVolumeDeleter

Volume file deleter, supporting permanent file deletion.

```python
class ClickzettaVolumeDeleter:
    """Singdata Lakehouse Volume file deleter"""

    def delete_file(self, file_path: str) -> bool:
        """
        Delete a specified file

        Args:
            file_path: File path to delete

        Returns:
            bool: Whether the deletion was successful

        Notes:
            - Deletion is permanent and cannot be recovered
            - After deletion, the file will disappear from the index and can no longer be downloaded or accessed
            - Supports deleting files with various path formats
        """

    def delete_directory(self, directory_path: str) -> bool:
        """Delete a specified directory and all its contents"""

    def delete_all(self) -> bool:
        """Delete all contents in the Volume"""
```

### Volume Connector Usage Examples

#### Complete Volume Operation Workflow

The following example demonstrates how to properly use the fixed Volume connectors:

```python
import tempfile
from pathlib import Path
from unstructured_ingest.processes.connectors.fsspec.clickzetta_volume import *

```

1. Create connection configuration:

```python
config = ClickzettaVolumeConnectionConfig(
    access_config=ClickzettaVolumeAccessConfig()
)

```

2. Index operation - List files:

```python
indexer = ClickzettaVolumeIndexer(
    connection_config=config,
    index_config=ClickzettaVolumeIndexerConfig(
        index_volume_type="user",  # or "table", "named"
        index_volume_name=None,    # table/named volume requires a name
        index_remote_path="docs/", # Optional: specify subdirectory
        index_regexp=r".*\.pdf$"   # Optional: regex filtering
    )
)
files = indexer.list_files()

```

3. Download operation - Smart error handling:

```python
with tempfile.TemporaryDirectory() as temp_dir:
    downloader = ClickzettaVolumeDownloader(
        connection_config=config,
        download_config=ClickzettaVolumeDownloaderConfig(
            download_volume_type="user",
            download_dir=temp_dir,
            # Other fields will be auto-inherited or inferred
        )
    )
    results = downloader.run(files[:3])  # Download first 3 files

    for result in results:
        if result["status"] == "success":
            print(f"Download successful: {result['local_path']}")
        else:
            print(f"Download failed: {result['error']}")

```

4. Upload operation - Auto-build remote_url:

```python
test_file = Path("test.txt")
test_file.write_text("Test content")

uploader = ClickzettaVolumeUploader(
    connection_config=config,
    upload_config=ClickzettaVolumeUploaderConfig(
        volume_type="user",
        remote_path="uploaded_test.txt"
        # remote_url will be auto-built
    )
)
uploader.upload_file(str(test_file), "uploaded_test.txt")

```

5. Delete operation - Permanent deletion verification:

```python
deleter = ClickzettaVolumeDeleter(
    connection_config=config,
    deleter_config=ClickzettaVolumeDeleterConfig(
        delete_volume_type="user"
    )
)
success = deleter.delete_file("uploaded_test.txt")
print(f"Deletion result: {success}")

```

6. Verify deletion effect:

```python
files_after = indexer.list_files()
remaining = [f for f in files_after if f["name"] == "uploaded_test.txt"]
print(f"Remaining files after deletion: {len(remaining)}")  # Should be 0
```

#### Key Improvements

1. **Config Class Field Completeness**: All config classes now include necessary fields
2. **Path Handling Fix**: Fixed string and Path object concatenation issues
3. **Smart Error Handling**: Automatically detects and handles XML error responses
4. **Directory vs File Fix**: Correctly handles cases where Singdata creates directories
5. **Deletion Verification**: Ensures completeness and correctness of delete operations

### DashScope Embedding Service

#### DashScopeEmbeddingConfig

DashScope embedding configuration class.

```python
class DashScopeEmbeddingConfig(EmbeddingConfig):
    """DashScope embedding service configuration"""

    model_name: str = "text-embedding-v3"  # Model name
    api_key: Optional[str] = None  # API key
    batch_size: int = 25  # Batch processing size
    max_retries: int = 3  # Maximum retry count
    retry_delay: float = 1.0  # Retry delay (seconds)
    text_field: str = "content"  # Text field name
    dimensions: Optional[int] = None  # Vector dimensions
```

**Supported Models:**

| Model Name         | Dimensions | Max Input Length |
| ------------------ | ---------- | ---------------- |
| text-embedding-v1  | 1536       | 2048 tokens      |
| text-embedding-v2  | 1536       | 2048 tokens      |
| text-embedding-v3  | 1024       | 8192 tokens      |
| text-embedding-v4  | 1024       | 8192 tokens      |

#### DashScopeEmbedder

DashScope embedder implementation class.

```python
class DashScopeEmbedder(BaseEmbedder):
    """DashScope embedder"""

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embedding vectors for a list of documents

        Args:
            texts: List of texts to embed

        Returns:
            List[List[float]]: List of embedding vectors
        """

    def embed_query(self, text: str) -> List[float]:
        """
        Generate an embedding vector for a query text

        Args:
            text: Query text

        Returns:
            List[float]: Embedding vector
        """

    async def embed_documents_async(self, texts: List[str]) -> List[List[float]]:
        """Async version of document embedding"""

    async def embed_query_async(self, text: str) -> List[float]:
        """Async version of query embedding"""
```

## Utility Functions

### Volume Utility Functions

#### build_remote_url

```python
def build_remote_url(volume: str, remote_path: Optional[str] = None) -> str:
    """
    Build a remote URL with the Singdata Lakehouse Volume protocol

    Args:
        volume: Volume identifier
        remote_path: Remote path

    Returns:
        str: Complete Volume URL

    Examples:
        build_remote_url("user", "docs/file.txt") -> "volume:user://~/docs/file.txt"
        build_remote_url("table_docs", "images/") -> "volume:table://docs/images/"
        build_remote_url("shared_volume", "data/") -> "volume://shared_volume/data/"
    """
```

#### build_sql

```python
def build_sql(
    action: str,
    volume: str,
    file_path: Optional[str] = None,
    is_table: bool = False,
    is_user: bool = False,
    regexp: Optional[str] = None
) -> str:
    """
    Build a SQL statement for Singdata Lakehouse Volume operations

    Args:
        action: Operation type ('list', 'get', 'put', 'remove_file', 'remove_dir', 'remove_all')
        volume: Volume identifier
        file_path: File path
        is_table: Whether it is a Table Volume
        is_user: Whether it is a User Volume
        regexp: Regex filtering (only for list operation)

    Returns:
        str: SQL statement

    Examples:
        build_sql("list", "user", "docs/", is_user=True)
        -> "LIST USER VOLUME SUBDIRECTORY 'docs/'"

        build_sql("get", "table_docs", "file.txt", is_table=True)
        -> "GET TABLE VOLUME docs FILE 'file.txt' TO '{local_path}'"
    """
```

#### get_env_multi

```python
def get_env_multi(key: str) -> str:
    """
    Multi-prefix environment variable lookup

    Supported prefix order: CLICKZETTA_, CZ_, cz_, no prefix
    Supports case variations

    Args:
        key: Base name of the environment variable

    Returns:
        str: Found environment variable value, returns None if not found

    Examples:
        # Lookup order: CLICKZETTA_USERNAME, CZ_USERNAME, cz_username, USERNAME,
        #               CLICKZETTA_username, CZ_username, cz_username, username
        get_env_multi("username")
    """
```

### SQL Utility Functions

#### Data Validation Functions

```python
def validate_vector_dimension(vector: List[float], expected_dim: int) -> bool:
    """Validate whether the vector dimension is correct"""

def validate_batch_data(data: List[Dict], required_fields: List[str]) -> bool:
    """Validate whether batch data contains required fields"""

def sanitize_table_name(table_name: str) -> str:
    """Sanitize table name to comply with SQL naming conventions"""
```

## Exception Classes

### UserAuthError

```python
class UserAuthError(Exception):
    """User authentication error"""
    # Raised when Singdata Lakehouse connection authentication fails
```

### UserError

```python
class UserError(Exception):
    """User operation error"""
    # Raised when user configuration or operation is incorrect
```

## Configuration Examples

### Complete Environment Variable Configuration

```bash
```

Singdata Lakehouse connection configuration:

```bash
export CLICKZETTA_SERVICE="https://your-service.singdata.com"
export CLICKZETTA_USERNAME="your_username"
export CLICKZETTA_PASSWORD="your_password"
export CLICKZETTA_WORKSPACE="your_workspace"
export CLICKZETTA_SCHEMA="your_schema"
export CLICKZETTA_INSTANCE="your_instance"
export CLICKZETTA_VCLUSTER="your_vcluster"

```

DashScope configuration:

```bash
export DASHSCOPE_API_KEY="your_dashscope_api_key"

```

Optional performance configuration:

```bash
export CLICKZETTA_POOL_SIZE="10"
export DASHSCOPE_RATE_LIMIT="100"
export BATCH_SIZE="1000"
export MAX_WORKERS="4"

```

Logging configuration:

```bash
export UNSTRUCTURED_LOG_LEVEL="INFO"
export ENABLE_METRICS="true"
```

### Python Configuration Example

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class ETLConfig:
    """Complete ETL configuration class"""

    # Singdata Lakehouse SQL configuration
    clickzetta_service: str
    clickzetta_username: str
    clickzetta_password: str
    clickzetta_workspace: str
    clickzetta_schema: str
    clickzetta_instance: str
    clickzetta_vcluster: str

    # DashScope configuration
    dashscope_api_key: str
    dashscope_model: str = "text-embedding-v3"

    # Processing configuration
    sql_batch_size: int = 1000
    volume_batch_size: int = 100
    embed_batch_size: int = 25

    # Volume configuration
    default_volume_type: str = "named"
    default_volume_name: Optional[str] = None

    @classmethod
    def from_env(cls) -> "ETLConfig":
        """Create configuration from environment variables"""
        import os
        return cls(
            clickzetta_service=os.getenv("CLICKZETTA_SERVICE"),
            clickzetta_username=os.getenv("CLICKZETTA_USERNAME"),
            clickzetta_password=os.getenv("CLICKZETTA_PASSWORD"),
            clickzetta_workspace=os.getenv("CLICKZETTA_WORKSPACE"),
            clickzetta_schema=os.getenv("CLICKZETTA_SCHEMA"),
            clickzetta_instance=os.getenv("CLICKZETTA_INSTANCE"),
            clickzetta_vcluster=os.getenv("CLICKZETTA_VCLUSTER"),
            dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
            dashscope_model=os.getenv("DASHSCOPE_MODEL", "text-embedding-v3"),
        )
```

## Performance Tuning Parameters

### Batch Size Recommendations

```python
```

Recommended batch sizes for different scenarios:

```python
PERFORMANCE_CONFIGS = {
    "small_dataset": {
        "sql_batch_size": 500,
        "volume_batch_size": 50,
        "embed_batch_size": 10,
    },
    "medium_dataset": {
        "sql_batch_size": 1000,
        "volume_batch_size": 100,
        "embed_batch_size": 25,
    },
    "large_dataset": {
        "sql_batch_size": 5000,
        "volume_batch_size": 500,
        "embed_batch_size": 50,
    },
    "memory_constrained": {
        "sql_batch_size": 100,
        "volume_batch_size": 20,
        "embed_batch_size": 5,
    }
}
```

### Connection Pool Configuration

```python
```

Singdata Lakehouse connection pool configuration:

```python
POOL_CONFIG = {
    "max_connections": 10,
    "min_connections": 2,
    "connection_timeout": 30,
    "idle_timeout": 300,
    "retry_attempts": 3,
    "retry_delay": 1.0,
}
```

## Testing Tools

### Connection Tests

```python
def test_clickzetta_connection(config: ClickzettaConnectionConfig) -> bool:
    """Test whether the Singdata Lakehouse connection is working"""
    try:
        with config.get_session() as session:
            result = session.sql("SELECT 1 as test").collect()
            return len(result) == 1
    except Exception:
        return False

def test_dashscope_connection(config: DashScopeEmbeddingConfig) -> bool:
    """Test whether the DashScope connection is working"""
    try:
        embeddings = config.embed_documents(["test"])
        return len(embeddings) == 1 and len(embeddings[0]) > 0
    except Exception:
        return False
```

### Data Validation Tools

```python
def validate_etl_pipeline(
    source_config: Dict,
    destination_config: Dict,
    sample_size: int = 100
) -> Dict[str, bool]:
    """Validate the complete ETL pipeline"""
    results = {
        "source_connection": False,
        "destination_connection": False,
        "data_extraction": False,
        "embedding_generation": False,
        "data_upload": False
    }

    # Implement each validation check...

    return results
```
