# External Function Overview

Singdata Lakehouse supports user-defined functions (UDF/UDAF/UDTF) via the **External Function** mechanism. Unlike built-in SQL functions, External Function execution logic runs in a cloud function compute service (Alibaba Cloud FC, Tencent Cloud SCF, or AWS Lambda); Lakehouse calls them via HTTP and retrieves the result — **you write the function call in SQL, and the function body runs in Python or Java code on the cloud**.

The advantage of this mechanism is that you can introduce any third-party library (scikit-learn, jieba, PyTorch, etc.) to implement logic that native SQL functions cannot handle, while still calling them from SQL.

---

## How It Works

A user calls an External Function in SQL → Lakehouse sends an HTTP request to the external function compute service → retrieves the result and returns it.

The creation process has four steps:

1. Enable a cloud function compute service (Alibaba Cloud FC / Tencent Cloud SCF / AWS Lambda) and object storage (OSS / COS / S3)
2. Create a Storage Connection and External Volume, then package and upload function code and dependencies
3. Create an API Connection to grant Lakehouse permission to call the function compute service
4. Execute `CREATE EXTERNAL FUNCTION` to register the function and call it in SQL

---

## Supported Function Types and Runtime Environments

| Function Type | Python | Java |
|---------|--------|------|
| UDF (single row in, single row out) | ✅ | ✅ |
| UDAF (multiple rows in, single row out) | ❌ | ✅ |
| UDTF (single row in, multiple rows out) | ❌ | ✅ |

Runtime environments: Java 8 / Python 3.10. When compressed dependencies exceed 500 MB, use container image deployment instead — see [Using Hugging Face Image Recognition Model to Process Image Data](RemoteFunction-on-acr.md).

---

## This Section

| Page | Description |
|------|------|
| [Introduction: External Function](RemoteFunction-intro.md) | Concepts, architecture, advantages, usage limits, and billing |
| [Development Guide: Python3](RemoteFunction-dev-guide-python3.md) | Environment setup, code structure, dependency packaging, deployment to Alibaba Cloud FC |
| [Development Guide: Java](external-function-dev-guide-java.md) | Java 8 function development, packaging, UDF/UDAF/UDTF implementation |
| [Usage Guide: External Function](RemoteFunction-best-practice.md) | Complete workflow: authorization, creating connections, registering functions, calling in SQL |
| [CREATE EXTERNAL FUNCTION](create_external_function.md) | Complete DDL syntax and parameter reference |
| [Storage Connection + API Connection + External Function Combo Practice](external-function-combo-practice.md) | End-to-end examples for three cloud environments (Alibaba Cloud / Tencent Cloud / AWS), including Python ML functions, 30 AI functions, and Java UDF/UDAF/UDTF |