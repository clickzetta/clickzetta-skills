# External Function Overview

Singdata Lakehouse supports User-Defined Functions (UDF/UDAF/UDTF) through the **External Function** mechanism. Unlike built-in SQL functions, the execution logic of an External Function runs in a cloud-based function compute service (Alibaba Cloud FC, Tencent Cloud SCF, or AWS Lambda). Lakehouse calls the function over HTTP and retrieves the result — **you write a function call in SQL, but the function body runs as Python or Java code in the cloud**.

The benefit of this approach is that you can bring in any third-party library (scikit-learn, jieba, PyTorch, etc.), implement logic that native SQL functions cannot handle, while still enjoying the experience of calling it directly from SQL.

---

## How It Works

A user calls an External Function in SQL → Lakehouse sends an HTTP request to the external function compute service → the result is processed and returned.

The creation process has four steps:

1. Enable cloud function compute services (Alibaba Cloud FC / Tencent Cloud SCF / AWS Lambda) and object storage (OSS / COS / S3)
2. Create a Storage Connection and External Volume, then package and upload the function code and dependencies
3. Create an API Connection to grant Lakehouse permission to invoke the function compute service
4. Execute `CREATE EXTERNAL FUNCTION` to register the function and call it from SQL

---

## Supported Function Types and Runtimes

| Function Type | Python | Java |
|---------|--------|------|
| UDF (single-row input, single-row output) | ✅ | ✅ |
| UDAF (multi-row input, single-row output) | ❌ | ✅ |
| UDTF (single-row input, multi-row output) | ❌ | ✅ |

Runtime environments: Java 8 / Python 3.10. If compressed dependencies exceed 500 MB, you must deploy using a container image instead — see [Processing Image Data with a Hugging Face Image Recognition Model](RemoteFunction-on-acr.md).

---

## Contents of This Chapter

| Page | Description |
|------|------|
| [Introduction: External Function](RemoteFunction-intro.md) | Concepts, architecture, benefits, usage limitations, and billing |
| [Development Guide: Python3](RemoteFunction-dev-guide-python3.md) | Environment setup, code structure, dependency packaging, deployment to Alibaba Cloud FC |
| [Development Guide: Java](external-function-dev-guide-java.md) | Java 8 function development, packaging, UDF/UDAF/UDTF implementation |
| [Usage Guide: External Function](RemoteFunction-best-practice.md) | Complete workflow: authorization, creating connections, registering functions, and calling from SQL |
| [CREATE EXTERNAL FUNCTION](create_external_function.md) | Full DDL syntax and parameter reference |
| [Storage Connection + API Connection + External Function: End-to-End Practice](external-function-combo-practice.md) | Complete examples running from scratch in three cloud environments (Alibaba Cloud / Tencent Cloud / AWS), including Python ML functions, 30 AI functions, and Java UDF/UDAF/UDTF |
