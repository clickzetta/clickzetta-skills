# Managing Files on Lakehouse Volume with Zettapark

## 1. Overview

Singdata Lakehouse provides unified management of data lake files and data warehouse tables through its abstract storage layer ([Volume](datalake_volume.md), [Schema](SCHEMA.md), and [Table](TABLE.md)) and Python API. This guide demonstrates how to perform file management operations in the data lake, including uploading (PUT), downloading (GET), and listing (LIST) files.

**Key Concepts**:

* **Volume Storage Abstraction**: All data lake storage is mapped to Volume objects.
  * [External Volume](external_volume.md): Managed by the customer, supporting integration with cloud storage such as AWS S3 and Alibaba Cloud OSS.
  * [Internal Volume](internal_volume.md): Managed by Singdata, divided into USER VOLUME and TABLE VOLUME.
* [Zettapark](zettapark-quick-start.md) **Python API**: Provides a unified interface for file and table integration.

You can get the [source code from the GitHub repository (Jupyter Notebook ipynb file)](https://github.com/yunqiqiliang/clickzetta_quickstart/blob/main/Zettapark/Managing%20Files%20on%20Datalake%20Volume%20with%20Zettapark.ipynb).

## 2. Environment Setup

### 1. Install Dependencies

```bash
pip install clickzetta_zettapark_python -U -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. Import Libraries and Create a Session

```python
from clickzetta.zettapark.session import Session
import json

# Load connection parameters from configuration file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Create session
session = Session.builder.configs(config).create()
print("Session created successfully!")
```

## 3. File Operations

### 1. Clean Up USER VOLUME

Before starting, clean up the USER VOLUME to ensure a clean environment:

```python
session.sql("REMOVE USER VOLUME SUBDIRECTORY '/'").show()
```

### 2. List Files in USER VOLUME

Confirm that the user volume is empty:

```python
session.sql("LIST USER VOLUME").show(10)
```

### 3. Upload Files to USER VOLUME

Upload local files to different directories in the user volume based on file type:

```python
import os

# Iterate through the local directory and upload files
for filename in os.listdir("data/"):
    if filename.endswith("csv.gz"):
        file_path = os.path.join("data/", filename)
        session.file.put(file_path, "volume:user://~/csvgz/")
    elif filename.endswith(".csv"):
        file_path = os.path.join("data/", filename)
        session.file.put(file_path, "volume:user://~/csv/")
    elif filename.endswith(".json"):
        file_path = os.path.join("data/", filename)
        session.file.put(file_path, "volume:user://~/json/")
    elif filename.endswith(".png"):
        file_path = os.path.join("data/", filename)
        session.file.put(file_path, "volume:user://~/png/")
    elif filename.endswith(".jpg"):
        file_path = os.path.join("data/", filename)
        session.file.put(file_path, "volume:user://~/jpg/")
    elif filename.endswith(".pdf"):
        file_path = os.path.join("data/", filename)
        session.file.put(file_path, "volume:user://~/pdf/")
```

### 4. Verify Upload Results

Confirm that the files were uploaded successfully:

```python
session.sql("LIST USER VOLUME").show(100)
```

## 4. View and Download Files

### 1. Download Image Files

Download images from the user volume and display them:

```python
from PIL import Image

# Download image to local directory
source_path = "volume:user://~/png/unstructured_tables.png"
dest_path = "tmp/png/"
session.file.get(source_path, dest_path)

# Open and display the image
try:
    img = Image.open(dest_path + "unstructured_tables.png")
    img.show()  # Display the image
except FileNotFoundError:
    print(f"Error: File {dest_path} does not exist. Please check the path.")
except Exception as e:
    print(f"Unable to open image: {str(e)}")
```

## 5. Close the Session

After completing operations, close the session to release resources:

```python
session.close()
print("Session closed.")
```

## 6. Summary

Through this guide, you have learned how to:

1. Manage files in the user volume using the Python API.
2. Upload, download, and list files in the data lake.
3. View image files and verify operation results.

**Next Steps**:

* Explore Volume usage to achieve seamless integration of files and tables.
* Try running federated queries on files and tables to experience the advantages of a unified Lakehouse.

## Appendix

* [Get the source code from the GitHub repository](https://github.com/yunqiqiliang/clickzetta_quickstart/blob/main/Zettapark/Managing%20Files%20on%20Datalake%20Volume%20with%20Zettapark.ipynb)
* [Get more Zettapark Python API examples](https://github.com/yunqiqiliang/clickzetta_quickstart/tree/main/Zettapark-examples/Notebook)

^
