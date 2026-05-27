# AI Functions

## Overview

In Singdata Lakehouse, AI functions are implemented **based on** the External Function framework. External functions (also known as Remote Functions) are a special type of user-defined function (UDF) that allows users to define function logic using Python or Java, but the core computational tasks are **offloaded** to external remote services for execution (supported remote services include Alibaba Cloud Function Compute FC and Tencent Cloud SCF). During execution, the following can be called:

* **Online Services**: Online services provided externally in the form of APIs, such as AI online model services (e.g., large language model APIs, online AI API services provided by cloud platforms).
* **Offline Features**: Offline service packages that bundle specific function code, dependency libraries, models, and data files, such as image recognition models downloaded from Hugging Face.

Singdata Lakehouse stores the connection and access information for external function compute services in metadata by creating API Connections. External functions call external function compute services via HTTP protocol, processing data and returning results.
![](.topwrite/assets/a7546df1-be39-41e9-9c80-e0e90ce3d353.svg)
Upon receiving prior user authorization, the Lakehouse platform will automatically deploy the function to the function compute service under the customer's account when creating the external function. When users use external functions in SQL queries, the external function handles secure connection to external compute services, data processing, and returns query results.

## Main Process for Creating External Functions

Please refer to: [Usage Process: External Function](RemoteFunctionBestPractice.md)

## Developing AI Functions Using External Functions

Please refer to the following development guides:

* [External Function(Python3)](RemoteFunctionDevGuidePython3.md)
* [External Function(Java)](ExternalFunctionDevGuideJava.md)

^
