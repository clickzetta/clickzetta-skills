# Introduction to LangChain Framework

LangChain is an open-source framework designed to help developers build applications based on large language models (LLM). It makes the development process more efficient and convenient through the following core advantages:

1. Data Source Integration: LangChain can seamlessly integrate LLM with real-time databases, APIs, and other multi-source data, ensuring that the generated content is both accurate and contextual.
2. Componentized Process Design: By flexibly configuring task chains, it clearly connects preprocessing, model invocation, and post-processing steps, improving execution efficiency.
3. Simplified Large Model Access: Provides a simple interface, lowering the threshold for technical development using LLM, and quickly realizing complex NLP functions.
4. Highly Extensible Customization: With good scalability, it can meet the needs of different business scenarios, helping developers fully leverage the potential of LLM.

# Basic Development Process

This section will demonstrate, through an example, how to use LangChain and clickzetta-sqlalchemy together to implement a simple application that queries a Lakehouse and displays the results.

## Environment Preparation

To interface LangChain with different data sources, you need to install `clickzetta-sqlalchemy` in your Python environment. The installation method is as follows:

```shell
pip install langchain clickzetta-sqlalchemy
```

## Example Code

First, create a file named `demo.py` and edit the code as follows:

```python
from langchain_community.utilities import SQLDatabase
import streamlit as st

```

Get Lakehouse authentication information from the Streamlit secret manager:

```python
username = st.secrets.lakehouse.username
password = st.secrets.lakehouse.password
account = st.secrets.lakehouse.account
endpoint = st.secrets.lakehouse.endpoint
workspace = st.secrets.lakehouse.workspace
schema = st.secrets.lakehouse.schema
virtualcluster = st.secrets.lakehouse.virtualcluster

```

Create the connection string:

```python
CONNECTION_STRING = (
    f"clickzetta://{username}:{password}"
    f"@{account}.{endpoint}/{workspace}?schema={schema}&virtualcluster={virtualcluster}"
)

```

Create a SQLDatabase instance from the connection string:

```python
db = SQLDatabase.from_uri(CONNECTION_STRING, schema=schema)
```

Next, execute the query and return the query results:

```python
```

Execute the query:

```python
result = db.run("SELECT * FROM Artist LIMIT 12;", fetch="cursor")
```

Print the result type:

```python
print(type(result))
```

Display the query results:

```python
pprint(list(result.mappings()))
```

To bind query parameters, use the optional `parameters` parameter.

```
result = db.run("SELECT * FROM Artist WHERE Name LIKE :search;",parameters={"search": "p%"},fetch="cursor",)
pprint(list(result.mappings()))
```

## Reference

[langchain Official Documentation](https://python.langchain.com/docs/get_started/introduction)

[SQLDatabase Development Guide](https://python.langchain.com/docs/integrations/tools/sql_database)
