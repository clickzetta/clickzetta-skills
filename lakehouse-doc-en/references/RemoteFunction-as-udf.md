# Developing Custom Functions (External Function)

An External Function (also called a Remote Function) is a user-defined function (UDF) created in Singdata Lakehouse using Python or Java. The function logic runs in a cloud function compute service (supports Alibaba Cloud FC and Tencent Cloud SCF) and interacts with Lakehouse via HTTP.

This lets you call capabilities not natively supported by Lakehouse from SQL:

- **Online services**: Large language model APIs, cloud platform AI services (image recognition, OCR, translation, etc.)
- **Offline capabilities**: Custom algorithms packaged for deployment, Hugging Face models, etc.

---

## How It Works

A user calls an External Function in SQL → Lakehouse sends an HTTP request to the external function compute service → retrieves the result and returns it.

The creation process has four steps:
1. Enable a cloud function compute service (Alibaba Cloud FC or Tencent Cloud SCF) and object storage
2. Package and upload function code, dependency libraries, and model files to object storage
3. Grant Lakehouse permission to access the function service and file packages
4. Execute DDL to create the External Function and call it in SQL

---

## Supported Function Types and Runtime Environments

| Function Type | Python | Java |
|---------|--------|------|
| UDF (single row in, single row out) | ✅ | ✅ |
| UDAF (multiple rows in, single row out) | ❌ | ✅ |
| UDTF (single row in, multiple rows out) | ❌ | ✅ |

Runtime environments: Java 8 / Python 3.10. When compressed dependencies exceed 500 MB, use container image deployment instead — see [Using Hugging Face Image Recognition Model to Process Image Data](remotefunction-on-acr.md).

---

## This Section

| Page | Description |
|------|------|
| [Introduction: External Function](remotefunction-intro.md) | Concepts, architecture, advantages, usage limits, and billing |
| [Development Guide: Python3](remotefunction-dev-guide-python3.md) | Environment setup, code structure, dependency packaging, deployment to Alibaba Cloud FC |
| [Development Guide: Java](external-function-dev-guide-java.md) | Java 8 function development, packaging, UDF/UDAF/UDTF implementation |
| [Usage Guide: External Function](remotefunction-best-practice.md) | Complete workflow: authorization, creating connections, registering functions, calling in SQL |