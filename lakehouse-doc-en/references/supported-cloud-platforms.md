# Supported Cloud Platforms and Regions

## Region Support

Singdata Lakehouse, as a SaaS-based data management and analysis service, fully leverages cloud infrastructure to provide users with efficient and convenient service experiences. We are committed to meeting the data connectivity and integration needs of customers and business systems across different cloud service providers and regions.

Currently, Singdata Lakehouse provides services in the following cloud service providers and regions, with plans to expand further:

| Cloud Provider | Region                  | Region Code               |
| -------------- | ----------------------- | ------------------------- |
| Alibaba Cloud  | Shanghai (East China 2) | cn-shanghai-alicloud      |
| Tencent Cloud  | Shanghai (East China)   | ap-shanghai-tencentcloud  |
| Tencent Cloud  | Beijing (North China)   | ap-beijing-tencentcloud   |
| Tencent Cloud  | Guangzhou (South China) | ap-guangzhou-tencentcloud |
| AWS            | Beijing                 | cn-north-1-aws            |

## Service Domains

When you register a Singdata Lakehouse account, the system automatically assigns a unique account name. When managing your account, you need to use this account name to log in to the Account Center. In the Account Center, administrators can create and open Lakehouse service instances for you in specified cloud service providers and regions. Please note that Lakehouse service instance names are globally unique.

| Service                      | Sub-service                | Domain                                                                  |
| ---------------------------- | -------------------------- | ----------------------------------------------------------------------- |
| Account Console              | Account Management Center  | accounts.app.clickzetta.com\<account\_name>.accounts.app.clickzetta.com |
| Account Console              | Account Management Center  | accounts.clickzetta.com\<account\_name>.accounts.clickzetta.com         |
| Product Web Console          | Lakehouse Instance Console | \<instance\_name>.app.clickzetta.com                                    |
|                              | Lakehouse Workspace List   | \<instance\_name>.app.lakehouse.clickzetta.com/workspace                |
| Lakehouse JDBC URL           |                            | jdbc\:clickzetta://\<instance\_name>.\<region\_id>.api.clickzetta.com/  |
| Lakehouse Streaming API Host |                            | \<instance\_name>.streamingapi.clickzetta.com                           |

JDBC Domain & Service Endpoint Detailed List

| Cloud Provider | Region                  | region\_id                | JDBC Domain                                                                        | Endpoint                                     |
| -------------- | ----------------------- | ------------------------- | ---------------------------------------------------------------------------------- | -------------------------------------------- |
| Alibaba Cloud  | Shanghai (East China 2) | cn-shanghai-alicloud      | jdbc\:clickzetta://\<instance\_name>.cn-shanghai-alicloud.api.clickzetta.com/      | cn-shanghai-alicloud.api.clickzetta.com      |
| Tencent Cloud  | Shanghai (East China)   | ap-shanghai-tencentcloud  | jdbc\:clickzetta://\<instance\_name>.ap-southeast-1-alicloud.api.clickzetta.com/   | ap-shanghai-tencentcloud.api.clickzetta.com  |
| Tencent Cloud  | Beijing (North China)   | ap-beijing-tencentcloud   | jdbc\:clickzetta://\<instance\_name>.ap-beijing-tencentcloud.api.clickzetta.com/   | ap-beijing-tencentcloud.api.clickzetta.com   |
| Tencent Cloud  | Guangzhou (South China) | ap-guangzhou-tencentcloud | jdbc\:clickzetta://\<instance\_name>.ap-guangzhou-tencentcloud.api.clickzetta.com/ | ap-guangzhou-tencentcloud.api.clickzetta.com |
| AWS            | Beijing                 | cn-north-1-aws            | jdbc\:clickzetta://\<instance\_name>.cn-north-1-aws.api.clickzetta.com/            | cn-north-1-aws.api.clickzetta.com            |

Note: For creating and obtaining the account name \<account\_name> and instance name \<instance\_name>, please refer to [Getting Started](logging-in.md).
