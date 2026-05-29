# Singdata Lakehouse Object Model Overview

Singdata Lakehouse adopts a layered structure to manage resources, improving the efficiency of data organization and access. Below is a detailed description and examples of the Lakehouse object model.
![](.topwrite/assets/object-hierarchy.png)

## Account

A Singdata account represents an organization or individual (usually an enterprise account) that has established a business relationship with Singdata. It is used to activate Singdata product services, make payments, obtain service support, etc. A globally unique account name is automatically generated during registration, serving as your unique identifier in Singdata products.

**Features:**
- The account is responsible for recharging, billing, payment, and ordering or changing Singdata products;
- All service instances and their resource objects activated on Singdata products by enterprises or individuals belong to a specific account.

**Example:**
Suppose you are a company named "XYZ Technology." After registering a Singdata account, the system generates an account name "xyztech0128" for you, and your account URL is "xyztech0128.accounts.clickzetta.com."

## User

After the account is successfully registered, you can create multiple users to share the resources within the same account. Different users can be assigned access to data and resources through permission control.

**Example:**
Under the "XYZ Technology" account, you can create multiple users, such as "alice" (responsible for data analysis) and "bob" (responsible for data development). You can assign different permissions based on their roles to ensure data security and efficient collaboration.

## Lakehouse Instance

A Lakehouse service instance is the carrier of Singdata Lakehouse product services. When activating the Lakehouse service, you need to create a service instance under the account based on the specified cloud service provider and region. An account can create one or more service instances (currently, only a single service instance creation is allowed by default).

**Features:**
- Service instances use unified metadata to manage data objects, computing resources, and job tasks;
- Service instances have regional attributes, with their computing, data, and other service resources located within the region of the cloud service provider;
- Different service instances are isolated from each other by default.

**Example:**
"XYZ Technology" needs to deploy Lakehouse services on Alibaba Cloud and Tencent Cloud. They can create two service instances under their account: "ali-lakehouse" and "tencent-lakehouse."

## Workspace

A workspace is a logical object used to organize Lakehouse resource objects (data objects, computing resources, users, etc.) and provide supporting data development capabilities. Multiple workspaces can be created under a service instance. Workspaces are isolated by default, and users need to join a workspace to use the objects within it. Objects in different workspaces under the same instance can be shared through cross-workspace authorization.

**Features:**
- Workspaces are used to organize and manage data development, computing resources, etc.;
- Workspaces are isolated to ensure data security and efficient collaboration.

**Example:**
Under the "ali-lakehouse" service instance, you can create two workspaces: "data-dev" (responsible for data development) and "data-ops" (responsible for data operations).

## Virtual Cluster

Computing resources consist of multi-instance virtual computing clusters and the computing services running within the clusters, providing a computing environment for user jobs, including CPU, memory, and temporary storage.

## Schema

Within a workspace, a schema is a namespace for a set of database objects. Database objects include tables, views, etc. A workspace can contain multiple schema objects with different names.

## Table

A table is a formatted two-dimensional data table.

## View

A view is a virtual table that does not actually exist in the database and is dynamically generated when used.

## Materialized View

A materialized view is a special type of view that, unlike a regular view, actually exists in the database and occupies storage resources.

## Lakehouse SQL Job

A Lakehouse SQL job refers to an SQL query task generated in the Lakehouse through web-based data development features or CLI, JDBC connections, etc.