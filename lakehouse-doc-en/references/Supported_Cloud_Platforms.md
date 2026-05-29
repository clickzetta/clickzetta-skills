# Cloud Services and Region Support

## Region Support

Singdata Lakehouse, as a SaaS-based data management and analysis service, fully leverages cloud infrastructure to provide users with an efficient and convenient service experience. We are committed to meeting the data integration and connectivity needs of customers and business systems across different cloud service providers and regions.

Currently, Singdata Lakehouse is available in the following cloud service providers and regions, with plans to expand further:

| Cloud Service Provider | Region    | Region Code             |
| ---------------------- | --------- | ----------------------- |
| Alibaba Cloud          | Singapore | ap-southeast-1-alicloud |
| Amazon Web Services    | Singapore | ap-southeast-1-aws      |

## Service Domain Names

When you register a Singdata Lakehouse account, the system will automatically assign a unique account name. You will need to use this account name to log in to the account center for account management. In the account center, administrators can enable and create Lakehouse service instances for you in the specified cloud service provider and region. Please note that the Lakehouse service instance name is globally unique.

| Service                      | Sub-service                | Domain Name                                                              |
| ---------------------------- | -------------------------- | ------------------------------------------------------------------------ |
| Account Console              | Account Management Center  | accounts.app.singdata.com&#xA;\<account\_name>.accounts.app.singdata.com |
| Account Console              | Account Management Center  | accounts.singdata.com&#xA;\<account\_name>.accounts.singdata.com         |
| Product Web Console          | Lakehouse Instance Console | \<instance\_name>.app.singdata.com                                       |
|                              | Lakehouse Workspace List   | \<instance\_name>.app.lakehouse.singdata.com/workspace                   |
| Lakehouse JDBC URL           |                            | jdbc\:clickzetta://\<instance\_name>.\<region\_code>.api.singdata.com/   |
| Lakehouse Streaming API Host |                            | \<instance\_name>.streamingapi.singdata.com                              |

**JDBC Domain Names**

| Cloud Service Provider | Region    | Region Code             | Domain Name                                                                    |
| ---------------------- | --------- | ----------------------- | ------------------------------------------------------------------------------ |
| Alibaba Cloud          | Singapore | ap-southeast-1-alicloud | jdbc\:clickzetta://\<instance\_name>.ap-southeast-1-alicloud.api.singdata.com/ |
| Amazon Web Services    | Singapore | ap-southeast-1-aws      | jdbc\:clickzetta://\<instance\_name>.ap-southeast-1-aws.api.singdata.com/      |

Note: For the creation and acquisition of account name \<account\_name> and instance name \<instance\_name>, please refer to [logging in](logging-in.md).
