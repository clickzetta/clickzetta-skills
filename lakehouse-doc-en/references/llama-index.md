# Introduction to LlamaIndex

LlamaIndex is an application data framework based on large language models (LLM), designed for context-enhanced applications. This type of LLM system is known as a RAG system, or "Retrieval-Augmented Generation". LlamaIndex provides the necessary abstractions to more easily ingest, construct, and access private or domain-specific data, so that this data can be securely and reliably injected into the LLM for more accurate text generation.

The key to data ingestion in LlamaIndex lies in loading and transforming. After loading documents, you can process them through transformation and output nodes. LlamaIndex can load data stored in cloud data warehouse Lakehouse through the Database Reader.

## Example Code
```
from llama_index.readers.database import DatabaseReader

import streamlit as st

username = st.secrets.lakehouse.username
password = st.secrets.lakehouse.password
account = st.secrets.lakehouse.account
endpoint = st.secrets.lakehouse.endpoint
workspace = st.secrets.lakehouse.workspace
schema = st.secrets.lakehouse.schema
virtualcluster = st.secrets.lakehouse.virtualcluster

CONNECTION_STRING = (
    f"clickzetta://{username}:{password}@"
    f"{account}.{endpoint}/{workspace}?schema={schema}&virtualcluster={virtualcluster}"
)

db = DatabaseReader(uri=CONNECTION_STRING, schema=schema)
```
## Available Methods for SQLDatabase
```
print(type(db.sql_database.from_uri))
print(type(db.sql_database.get_single_table_info))
print(type(db.sql_database.get_table_columns))
print(type(db.sql_database.get_usable_table_names))
print(type(db.sql_database.insert_into_table))
print(type(db.sql_database.run_sql))
```
```
query = f"""
    SELECT
        CONCAT(name, ' is ', age, ' years old.') AS text
    FROM public.users
    WHERE age >= 18
    """

documents = db.load_data(query=query)

index = VectorStoreIndex.from_documents(documents)

```
### Reference Documentation

[Llama-Index Database Reader](https://docs.llamaindex.ai/en/stable/examples/data_connectors/DatabaseReaderDemo.html)