# AI Function

## Overview

In Singdata Lakehouse, AI Functions are built **on top of** the External Function framework. An External Function (also called a Remote Function) is a special type of User-Defined Function (UDF) that allows users to define function logic in Python or Java, while its core computation is **offloaded** to an external remote service (supported remote services include: Alibaba Cloud Function Compute (FC) and Tencent Cloud Serverless Cloud Function (SCF)). During execution, the function can invoke:

* **Online services**: Online services exposed via API, such as AI online model services (e.g., large language model APIs, online AI API services provided by cloud platforms).
* **Offline services**: Offline service packages that bundle specific function code, dependency libraries, models, and data files — for example, image recognition models downloaded from Hugging Face.

Singdata Lakehouse creates an API Connection to store the connection and access information for the external function compute service in metadata. External Functions call the external function compute service over HTTP to process data and return results.
![](.topwrite/assets/a7546df1-be39-41e9-9c80-e0e90ce3d353.svg)
After obtaining prior authorization from the user, the Lakehouse platform automatically deploys the function in the function compute service under the customer's account at the time the External Function is created. When a user invokes an External Function in a SQL query, the External Function handles the secure connection to the external compute service, performs data processing, and returns the query result.

## Main Steps for Creating an External Function

See: [Workflow: External Function](RemoteFunction-best-practice.md)

## Developing AI Functions with External Functions

Refer to the following development guides:

* [External Function (Python3)](RemoteFunction-dev-guide-python3.md)
* [External Function (Java)](external-function-dev-guide-java.md)
