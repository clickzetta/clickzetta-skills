# EXTERNAL FUNCTION

## Overview

EXTERNAL FUNCTION (REMOTE FUNCTION) is a user-defined function (UDF) created in Singdata Lakehouse using Python or Java, executed via a remote service (supported remote services include: Alibaba Cloud Function Compute FC, Tencent Cloud SCF). During execution, it can call:

* Online services: online services exposed as APIs, such as AI online model services (e.g., large language model APIs, online AI API services provided by cloud platforms).
* Offline capabilities: offline service packages that bundle specific function code, dependency libraries, models, and data files, such as image recognition models downloaded from Hugging Face.

Singdata Lakehouse creates an API CONNECTION to store the connection and access information for the external function compute service in its metadata. EXTERNAL FUNCTION calls the external function compute service via the HTTP protocol for data processing and returns the results.
![](.topwrite/assets/a7546df1-be39-41e9-9c80-e0e90ce3d353.svg)
Through pre-authorization by the user, the Singdata Lakehouse platform automatically creates the corresponding function in the user's cloud account function compute service when an external function is created. When a user invokes an external function in a SQL query, the external function establishes a secure connection with the external compute service, processes the data, and returns the query results.

## EXTERNAL FUNCTION Creation Process

* Enable the cloud function compute service (e.g., Alibaba Cloud Function Compute FC) and object storage service.
* Package and upload the function execution code, executables, dependency libraries, models, and data files to object storage.
* Grant Singdata Lakehouse permission to operate the above services and access the function file packages.
* Execute the connection and external function DDL statements to generate the UDF and use it in queries.

## EXTERNAL FUNCTION Execution Process

* The user calls an External Function in a Singdata Lakehouse SQL statement.
* Singdata Lakehouse sends an HTTP request using the provided service address and authentication information to invoke and run the function.
* Singdata Lakehouse retrieves the response and returns the result.

## EXTERNAL FUNCTION Advantages

* External Functions can be used to call rich external data processing capabilities to supplement the traditional SQL computing model. For example, you can call large language model (LLM) services, image processing, audio/video processing, and other services to extend SQL's capabilities for unstructured data processing.
* External Functions can directly access external networks, unconstrained by the Singdata Lakehouse network.

## Usage Restrictions

* Currently only Java and Python programming languages are supported, with supported runtime environments of Java 8 and Python 3.10.
* If native libraries are required (e.g., libraries containing .so files), they must be compatible with the Python 3.10 ABI.
* When the program and its dependencies exceed 500 MB after compression, the function must be created using a container image. See [Practice: Using Hugging Face Image Recognition Models to Process Image Data](RemoteFunction-on-acr.md).

## EXTERNAL FUNCTION Pricing

* Supports custom function types: UDF, UDAF, UDTF (UDAF and UDTF are Java-only; Python supports UDF only)
* Remote service call fees: refer to the cloud provider's function compute service pricing (Alibaba Cloud: [link](https://help.aliyun.com/zh/fc/product-overview/billing-overview?spm=a2c4g.11186623.0.0.4d5b19b3rrOy7Y), Tencent Cloud: [link](https://cloud.tencent.com/document/product/583/17299)).
* Compute fees incurred by using Singdata Lakehouse compute resources.
* Data transfer fees: any fees related to public network data egress. Intranet transfers are free.

## Developing UDF Functions with External Function

See: [Workflow: External Function](RemoteFunction-best-practice.md)

Refer to the following development guides:

* [External Function (Java)](external-function-dev-guide-java.md)
* [External Function (Python3)](RemoteFunction-dev-guide-python3.md)
