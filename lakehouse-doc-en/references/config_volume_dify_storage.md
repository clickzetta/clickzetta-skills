# Configuring Singdata Lakehouse Volume as a File Storage Service in Dify

## 📋 Overview

Singdata Lakehouse Volume storage provides [Dify](https://dify.ai/) with an enterprise-grade file storage backend, supporting three Volume types:

* **Table Volume** - Knowledge base file management (not currently recommended)
* **User Volume** - Knowledge base file storage (recommended)
* **External Volume** - Enterprise data lake integration

## 🚀 Quick Start

### Environment Requirements

* Singdata Lakehouse instance
* Dify 1.7.2+

### Basic Configuration

Configure in the Dify `.env` file:

```bash
# Use Singdata Volume as storage backend
STORAGE_TYPE=singdata-volume

# Singdata connection configuration
CLICKZETTA_VOLUME_USERNAME=your_username
CLICKZETTA_VOLUME_PASSWORD=your_password
CLICKZETTA_VOLUME_INSTANCE=your_instance
CLICKZETTA_VOLUME_SERVICE=region_id.api.singdata.com
CLICKZETTA_VOLUME_WORKSPACE=your_workspace
CLICKZETTA_VOLUME_VCLUSTER=default_ap
CLICKZETTA_VOLUME_SCHEMA=dify

# Volume type configuration
CLICKZETTA_VOLUME_TYPE=table  # table|user|external
CLICKZETTA_VOLUME_TABLE_PREFIX=dataset_
CLICKZETTA_VOLUME_DIFY_PREFIX=dify_km    # directory prefix, isolated from other applications
CLICKZETTA_VOLUME_NAME=  # only required for External Volume
```

## 📂 Volume Type Detailed Configuration

### Volume Type Selection

Singdata Lakehouse Volume supports three types, each suitable for different scenarios:

| Type           | Use Case             | Config Complexity | Permission Control        |
| -------------- | -------------------- | ----------------- | ------------------------- |
| **user**       | Knowledge base mgmt  | Simple            | User-level                |
| **table**      | Enterprise multi-tenant | Medium         | Table-level + User-level  |
| **external**   | Data lake integration | Complex           | Volume-level + Storage-level |

> 💡 **Selection Suggestions**:
>
> * Personal use or small teams → Choose `user`
> * Enterprise environments requiring permission control → Choose `table`
> * Data lake integration needed → Choose `external`

### 1. Table Volume Configuration

```bash
# Table Volume configuration
CLICKZETTA_VOLUME_TYPE=table
CLICKZETTA_VOLUME_TABLE_PREFIX=dataset_

# Knowledge base file organization structure
# dataset_{dataset_id}/
# ├── raw/           # original uploaded documents
# ├── processed/     # processed files  
# ├── metadata/      # metadata files
# └── exports/       # exported files
```

**Features**:

* ✅ Permission inheritance from table, high security
* ✅ Tightly coupled with knowledge base data
* ✅ Supports multi-tenant isolation
* ✅ Automatic table name mapping

**Use Cases**:

* Knowledge base document storage
* Vector database associated files
* Multi-tenant file isolation

### 2. User Volume Configuration (Recommended for Knowledge Base)

```bash
# User Volume configuration
CLICKZETTA_VOLUME_TYPE=user
CLICKZETTA_VOLUME_DIFY_PREFIX=dify_km    # directory prefix, defaults to dify_km

# User file organization structure (prefix added automatically)
# dify_km/
# ├── upload_files/  # user uploaded files
# ├── tools/         # tool files
# ├── website_files/ # website files
# ├── temp/          # temporary files
# └── cache/         # cache files
```

**Features**:

* ✅ User-level isolation
* ✅ Automatic directory prefix, isolated from other applications
* ✅ All permissions granted by default
* ✅ Simple configuration
* ✅ Suitable for personal files

**Use Cases**:

* User personal file storage
* Temporary file processing
* User configuration files
* Small team file sharing

### 3. External Volume Configuration

```bash
# External Volume configuration
CLICKZETTA_VOLUME_TYPE=external
CLICKZETTA_VOLUME_NAME=your_external_volume_name

# Requires pre-created Storage Connection and External Volume
# CREATE STORAGE CONNECTION s3_conn TYPE S3 ...
# CREATE EXTERNAL VOLUME enterprise_data LOCATION 's3://bucket/' ...
```

**Features**:

* ✅ Enterprise data lake integration
* ✅ Supports S3/OSS/COS
* ✅ Large capacity storage
* ✅ Cross-platform access

**Use Cases**:

* Enterprise data lake integration
* Large file storage
* Cross-cloud platform data sharing

**Permission Management**: External Volume requires special permission configuration since it connects to external storage systems. Permission management includes:

* **CREATE Permission**: Creating External Volume requires administrator privileges
* **USAGE Permission**: Using External Volume requires explicit USAGE privilege
* **File Operation Permissions**: Controlled through the access policies of the underlying storage system (S3/OSS, etc.)

```sql
-- Create External Volume example
CREATE STORAGE CONNECTION s3_conn TYPE S3 
PROPERTIES (
    'access_key_id'='your_access_key',
    'secret_access_key'='your_secret_key',
    'region'='us-west-2'
);

CREATE EXTERNAL VOLUME enterprise_data 
LOCATION 's3://your-bucket/dify-data/' 
STORAGE_CONNECTION=s3_conn;

-- Grant permissions example
GRANT USAGE ON EXTERNAL VOLUME enterprise_data TO dify_user;
GRANT CREATE ON EXTERNAL VOLUME enterprise_data TO dify_admin;
```

**Permission Check Flow**:

1. Verify the user's USAGE permission on the External Volume
2. Check if the file path is within the allowed Volume scope
3. Verify access permissions through the underlying storage connection
4. Perform final permission confirmation based on the operation type (read/write)

## 🚨 Troubleshooting

### Common Issues

#### 1. Connection Failed

```bash
Error: user:username login to singdata failed
```

**Solution**:

* Check username and password
* Confirm instance and service address
* Verify network connectivity

#### 2. Insufficient Permissions

**Table Volume Permission Error**:

```bash
Error: Permission denied for operation 'save' on table volume
```

**Solution**:

* Check table permissions: `SHOW GRANTS ON TABLE dataset_xxx`
* Grant appropriate permissions: `GRANT INSERT,UPDATE,DELETE ON TABLE dataset_xxx TO user`
* Clear permission cache

**User Volume Permission Error**:

```bash
Error: Permission denied for user volume access
```

**Solution**:

* Check schema permissions: `SHOW GRANTS ON SCHEMA dify TO current_user`
* Grant schema permissions: `GRANT USAGE,CREATE ON SCHEMA dify TO user`
* Verify workspace permissions

**External Volume Permission Error**:

```bash
Error: Permission denied for external volume 'enterprise_data'
```

**Solution**:

* Check External Volume permissions: `SHOW GRANTS ON EXTERNAL VOLUME enterprise_data`
* Grant USAGE permission: `GRANT USAGE ON EXTERNAL VOLUME enterprise_data TO user`
* Verify underlying storage connection permissions

#### 3. Volume Not Found

```bash
Error: volume not found - quick_start.dify.dataset_xxx
```

**Solution**:

* Confirm volume existence: `SHOW VOLUMES`
* Check table name prefix configuration
* Verify schema and workspace configuration

#### 4. File Operation Failed

```bash
Error: File not found or access denied
```

**Solution**:

* Check file path format
* Verify permission settings
* Confirm Volume type configuration

**Updated Date**: 2025-09-03
**Applicable Version**: Dify 1.7.2+
