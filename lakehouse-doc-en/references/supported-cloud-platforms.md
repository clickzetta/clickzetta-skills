# Supported Cloud Platforms and Regions

## Region Support

Singdata Lakehouse, as a SaaS-based data management and analysis service, fully leverages cloud infrastructure to provide users with efficient and convenient service experiences. We are committed to meeting the data connectivity and integration needs of customers and business systems across different cloud service providers and regions.

Currently, Singdata Lakehouse provides services in the following cloud service providers and regions, with plans to expand further:

| Cloud Provider | Region                   | Region Code             |
| -------------- | ------------------------ | ----------------------- |
| Alibaba Cloud  | Singapore (Singapore)    | ap-southeast-1-alicloud |
| AWS            | Asia Pacific (Singapore) | ap-southeast-1-aws      |

## Service Domains

When you register a Singdata Lakehouse account, the system automatically assigns a unique account name. When managing your account, you need to use this account name to log in to the Account Center. In the Account Center, administrators can create and open Lakehouse service instances for you in specified cloud service providers and regions. Please note that Lakehouse service instance names are globally unique.

| Service             | Sub-service                | Domain                                                               |
| ------------------- | -------------------------- | -------------------------------------------------------------------- |
| Account Console     | Account Management Center  | \<account\_name>.\<region\_id>.accounts.singdata.com                 |
| Product Web Console | Lakehouse Instance Console | \<instance\_name>.\<region\_id>.app.singdata.com                     |
|                     | Lakehouse Workspace List   | \<instance\_name>.app.lakehouse.singdata..com/workspace              |
| Lakehouse JDBC URL  |                            | jdbc\:clickzetta://\<instance\_name>.\<region\_id>.api.singdata.com/ |

JDBC Domain & Service Endpoint Detailed List

| Cloud Provider | Region                   | region\_id           | JDBC Domain                                                                                                                                                               | Endpoint                                 |
| -------------- | ------------------------ | -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| Alibaba Cloud  | Singapore (Singapore)    | cn-shanghai-alicloud | jdbc\:clickzetta://\<instance\_name>.ap-southeast-1-alicloud.api.singdata.com/\<workspace\_name>?username=\<user\_name>\&password=\&schema=public\&virtualCluster=DEFAULT | ap-southeast-1-alicloud.app.singdata.com |
| AWS            | Asia Pacific (Singapore) | cn-north-1-aws       | jdbc\:clickzetta://\<instance\_name>.ap-southeast-1-aws.api.singdata.com/\<workspace\_name>?username=\<user\_name>\&password=\&schema=public\&virtualCluster=DEFAULT      | cn-north-1-aws.api.clickzetta.com        |

Note: For creating and obtaining the account name \<account\_name> and instance name \<instance\_name>, please refer to [Getting Started](logging-in.md).
