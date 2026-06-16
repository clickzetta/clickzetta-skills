# Installation and Configuration

This guide will help you quickly install and configure the LangChain-Singdata integration.

## Installation

### Install via pip (Recommended)

```bash
pip install langchain-clickzetta
```

### Development Installation

If you want to install from source or contribute to development:

```bash
git clone https://github.com/yunqiqiliang/langchain-clickzetta.git
cd langchain-clickzetta/libs/clickzetta
pip install -e ".[dev]"
```

## Dependency Requirements

### Python Version
- Python 3.10 or higher

### Core Dependencies
The following dependencies are installed automatically with the package:

```
langchain-core>=0.1.0
clickzetta-connector-python>=0.8.92
clickzetta-zettapark-python>=0.1.3
sqlalchemy>=2.0.0
numpy>=1.20.0
pydantic>=2.0.0
typing-extensions>=4.0.0
```

### Optional Dependencies

#### Chinese AI Optimization (Recommended)
```bash
pip install dashscope  # Alibaba Cloud DashScope platform
```

#### Development Tools
```bash
pip install langchain-clickzetta[dev]
```

Includes pytest, ruff, black, mypy, and other development tools.

## Singdata Environment Configuration

### Obtain Singdata Access

1. **Register a Singdata account**
   - Visit the [Singdata official website](https://www.singdata.com/)
   - Register and apply for a Singdata trial

2. **Obtain connection information**
   You need the following 7 connection parameters:
   - `service` - Service address
   - `instance` - Instance name
   - `workspace` - Workspace
   - `schema` - Schema name
   - `username` - Username
   - `password` - Password
   - `vcluster` - Virtual cluster name

### Environment Variable Configuration

Create a `.env` file or set environment variables:

```bash
```

Singdata connection configuration:

```bash
export CLICKZETTA_SERVICE="your-service"
export CLICKZETTA_INSTANCE="your-instance"
export CLICKZETTA_WORKSPACE="your-workspace"
export CLICKZETTA_SCHEMA="your-schema"
export CLICKZETTA_USERNAME="your-username"
export CLICKZETTA_PASSWORD="your-password"
export CLICKZETTA_VCLUSTER="your-vcluster"

```

Optional: DashScope configuration (recommended for Chinese AI):

```bash
export DASHSCOPE_API_KEY="your-dashscope-api-key"
```

### Connection Configuration File

You can also use a configuration file by creating `~/.clickzetta/connections.json`:

```json
{
  "default": {
    "service": "your-service",
    "instance": "your-instance",
    "workspace": "your-workspace",
    "schema": "your-schema",
    "username": "your-username",
    "password": "your-password",
    "vcluster": "your-vcluster"
  },
  "uat": {
    "service": "uat-service",
    "instance": "uat-instance",
    "workspace": "test",
    "schema": "test_schema",
    "username": "test-user",
    "password": "test-password",
    "vcluster": "test-cluster"
  }
}
```

## Verify Installation

### Basic Import Test

```python
```

Test basic import:

```python
try:
    from langchain_clickzetta import ClickZettaEngine
    print("✅ LangChain Singdata import successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
```

### Connection Test

```python
from langchain_clickzetta import ClickZettaEngine

```

Create engine instance:

```python
engine = ClickZettaEngine(
    service="your-service",
    instance="your-instance",
    workspace="your-workspace",
    schema="your-schema",
    username="your-username",
    password="your-password",
    vcluster="your-vcluster"
)

```

Test connection:

```python
try:
    results, columns = engine.execute_query("SELECT 1 as test")
    print("✅ Singdata connection successful")
    print(f"Test result: {results}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

### Full Feature Test

```python
from langchain_clickzetta import (
    ClickZettaEngine,
    ClickZettaVectorStore,
    ClickZettaStore
)
from langchain_community.embeddings import DashScopeEmbeddings

```

Initialize components:

```python
engine = ClickZettaEngine(
    # ... your connection parameters
)

```

Test vector store:

```python
try:
    embeddings = DashScopeEmbeddings(
        dashscope_api_key="your-api-key",
        model="text-embedding-v4"
    )

    vector_store = ClickZettaVectorStore(
        engine=engine,
        embedding=embeddings,
        table_name="test_vectors"
    )
    print("✅ Vector store initialization successful")
except Exception as e:
    print(f"⚠️  Vector store initialization failed: {e}")

```

Test key-value store:

```python
try:
    store = ClickZettaStore(engine=engine, table_name="test_store")
    print("✅ Key-value store initialization successful")
except Exception as e:
    print(f"❌ Key-value store initialization failed: {e}")
```

## FAQ

### Connection Issues

**Issue**: `Connection timeout`
```
Solution:
1. Check network connectivity
2. Confirm the Singdata service address is correct
3. Increase the connection_timeout parameter
```

**Issue**: `Authentication failed`
```
Solution:
1. Confirm username and password are correct
2. Check user permissions
3. Confirm the vcluster parameter is correct
```

### Dependency Issues

**Issue**: `ModuleNotFoundError: No module named 'clickzetta'`
```
Solution:
pip install clickzetta-connector-python
```

**Issue**: `Version conflict`
```
Solution:
pip install --upgrade langchain-clickzetta
```

### Permission Issues

**Issue**: `Insufficient permissions, unable to create table`
```
Solution:
1. Contact administrator to grant CREATE TABLE permission
2. Use an existing table name
3. Confirm workspace and schema permissions
```

## Tips

- It is recommended to use connection pools in production environments
- Regularly update to the latest version
- Use environment variables to manage sensitive information
- Enable logging for debugging
