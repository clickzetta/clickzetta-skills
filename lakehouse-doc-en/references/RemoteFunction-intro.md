# EXTERNAL FUNCTION

## Overview

EXTERNAL FUNCTION (REMOTE FUNCTION) is a custom function (UDF) created in Singdata Lakehouse using Python and Java languages, executed through remote services (supported remote services include: Alibaba Cloud Function Compute FC, Tencent Cloud Serverless Cloud Function SCF). During execution, it can call:

* Online Services: Online services provided externally in the form of APIs, such as AI online model services (e.g., large language model APIs, online AI API services provided by cloud platforms).
* Offline Functions: Offline service packages bundling specific function code, dependency libraries, models, and data files, such as image recognition models downloaded from Hugging Face.

Singdata Lakehouse stores the connection and access information for external function compute services in metadata by creating an API CONNECTION. EXTERNAL FUNCTION calls external function compute services via the HTTP protocol for data processing and returns results.
![](.topwrite/assets/a7546df1-be39-41e9-9c80-e0e90ce3d353.svg)
Through pre-authorization by the user, the Singdata Lakehouse platform automatically creates the corresponding function in the function compute service under the customer's account when creating an external function. When users use external functions in SQL queries, the external function establishes a secure connection to the external compute service, processes data, and returns query results.

## EXTERNAL FUNCTION Creation Flow

Please refer to: [Usage Workflow: External Function](RemoteFunction-best-practice.md)

* Enable cloud Function Compute services (such as Alibaba Cloud FC) and Object Storage services.
* Package the function execution code, executable files, dependency libraries, models, and data files, and upload them to object storage.
* Grant Singdata Lakehouse the permissions to operate the above services and access function files (packages).
* Execute connection and external function DDL statements to generate UDFs and use them in queries.

## EXTERNAL FUNCTION Execution Process

* Users invoke External Functions in Singdata Lakehouse SQL statements.
* Singdata Lakehouse sends HTTP requests based on the provided service address and authentication information to invoke and run the function.
* Singdata Lakehouse retrieves the response and returns the result.

## Advantages of EXTERNAL FUNCTION

* Remote Functions can be used to invoke rich external data processing capabilities, supplementing the traditional SQL computation model. For example, large language models (LLMs), image processing, audio/video processing, and other services or capabilities can be invoked to supplement SQL's capabilities in unstructured data processing.
* Direct access to external networks, unrestricted by Singdata Lakehouse network constraints.

## Usage Limitations

* Currently, only Java and Python programming languages are supported, with supported runtime environments being Java 8 and Python 3.10.
* If native libraries are required (e.g., libraries containing .so files), they must be compatible with the Python 3.10 ABI.
* When the program and its dependency files, after compression, exceed 500 MB, the function must be created using the container image approach. Please refer to [Practice: Processing Image Data Using Hugging Face Image Recognition Models](RemoteFunction-on-acr.md).

## EXTERNAL FUNCTION Billing

* Supported custom function types: UDF, UDAF, UDTF
* Remote service invocation costs: Refer to the cloud service provider's Function Compute billing information (Alibaba Cloud: [link](https://help.aliyun.com/zh/fc/product-overview/billing-overview?spm=a2c4g.11186623.0.0.4d5b19b3rrOy7Y); Tencent Cloud: [link](https://cloud.tencent.com/document/product/583/17299)).
* Compute costs incurred by using Singdata Lakehouse compute resources.
* Data transfer costs: Any costs related to public network data egress. Internal network transfers incur no cost.

## Developing UDF Functions Using REMOTE FUNCTION

Please refer to the following development guides:

* [External Function(Java)](external-function-dev-guide-java.md)
* [External Function(Python3)](RemoteFunction-dev-guide-python3.md)

^
