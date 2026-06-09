# Trial Account Quotas and Limitations Description

## Introduction to Trial Accounts

Trial accounts are a free experience form provided by Singdata Lakehouse to help new users experience the platform's features and performance at zero cost.

Each account, when newly created, will first become a "trial" status user. You can see the "trial" status identifier on the left side of the management center. After creating a service instance, the account will receive a voucher with a total amount of 200 yuan, valid for 30 days, for product experience.

![](.topwrite/assets/image_1740710821088.png =189)

To ensure the overall operational efficiency of the platform and fair resource allocation, trial users will be subject to certain restrictions during use. The specific limitations are as follows.

##

## Quotas and Usage Limitations Overview

| **Feature**           | **Limitation Description**                                                                                | **Limit Value / Rules**                                                                                                                                                                                                                 | **Quota Upgrade Method**         |
| --------------------- | --------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| Global                | Maximum number of users that can be created under a single tenant                                         | Maximum 500                                                                                                                                                                                                                             | Non-changeable                   |
|                       | Number of instances that can be created under a single tenant                                             | Instances can be opened in any region, with a total not exceeding 1                                                                                                                                                                     | Upgrade to formal account        |
|                       | Number of workspaces that can be created under a single instance                                          | No more than 100                                                                                                                                                                                                                        | Non-changeable                   |
| Data Integration      | Offline synchronization tasks:                                                                            | The concurrency limit for a single task is less than 10; the number of tasks running simultaneously does not exceed 2. Task execution time does not exceed 30 minutes.                                                                  | Upgrade to formal account        |
|                       | Real-time integration tasks                                                                               | The number of tasks running simultaneously does not exceed 2. Task running time does not exceed 2 hours.                                                                                                                                | Upgrade to formal account        |
|                       | Multi-table real-time synchronization tasks                                                               | During the multi-table real-time synchronization task, offline integration tasks and real-time integration tasks will be used separately, occupying the quotas of offline tasks and real-time tasks respectively.                       | Upgrade to formal account        |
| Data Development      | Maximum number of lines in SQL/Python/Shell/JDBC task files                                               | Maximum 5000 lines of code                                                                                                                                                                                                              | Non-changeable                   |
|                       | SQL query result return row limit                                                                         | Default 1000 rows, user adjustable up to a maximum of 10000 rows                                                                                                                                                                        | Non-changeable                   |
|                       | SQL query result download limit                                                                           | Maximum support for downloading 4GiB data                                                                                                                                                                                               | Immutable                        |
|                       | Temporary query run history retention time                                                                | Retained for up to 7 days                                                                                                                                                                                                               | Immutable                        |
|                       | Historical version and commit version retention time                                                      | Permanently retained                                                                                                                                                                                                                    | Immutable                        |
| Task Scheduling       | Limit on the number of task instances started concurrently by a single tenant                             | Offline sync task instances: 20 SQL task instances: Unlimited Python task instances: 5 Shell task instances: 5 JDBC task instances: 20                                                                                                  | Upgrade to formal account        |
|                       | Maximum system fallback runtime timeout for a single task instance                                        | Minimum: 1 minute Maximum: 168 hours (7 days)                                                                                                                                                                                           | Immutable                        |
|                       | Instance auto-retry interval                                                                              | Minimum: 1 minute Maximum: 1 day                                                                                                                                                                                                        | Immutable                        |
|                       | Scheduling wait time                                                                                      | Minimum: 1 minute Maximum: 168 hours (7 days)                                                                                                                                                                                           | Immutable                        |
| Operations Center     | Task instance history retention time                                                                      | Periodic instances: 32 days Supplementary instances: 32 days Temporary instances: 8 days                                                                                                                                                | Immutable                        |
|                       | Query task instance list limit                                                                            | Display results are subject to instance retention time limit, up to 6 months                                                                                                                                                            | Immutable                        |
|                       | Task operation log query time range limit                                                                 | 6 months                                                                                                                                                                                                                                | Immutable                        |
|                       | Task operation log history retention time limit                                                           | 6 months                                                                                                                                                                                                                                | Immutable                        |
| Compute Cluster       | Maximum total specification of compute cluster instances that can be created under a single instance      | Total specification of all VCs does not exceed 28 CRU: of which the default usage in the sys workspace is 9 CRU quota, and the remaining total specification of all other workspaces under the service instance does not exceed 19 CRU. | Upgrade to formal account        |
|                       | Concurrent Compilation Jobs                                                                               | No more than 2                                                                                                                                                                                                                          | Contact Singdata for adjustments |
| Data Objects          | Maximum number of data objects (e.g., tables, views, etc.) that can be created under a single instance    | 1000                                                                                                                                                                                                                                    | Upgrade to a formal account      |
| Stream Writing        | Maximum number of Stream objects that can be created under a single instance                              | 10                                                                                                                                                                                                                                      | Upgrade to a formal account      |
| Job History           | Limitations on querying job list                                                                          | Time range: maximum 7 days; number of job history records returned: up to 10,000; job history records exceeding the above quota can be queried using SQL in the sys.information\_schema.job\_history view.                              | Cannot be changed                |
|                       | Daily SMS sending limit                                                                                   | **Verification code**: Up to 1 per minute; up to 20 per hour; up to 40 per natural day. **Alert notifications, etc**.: Up to 50 per natural day.                                                                                        | Cannot be changed                |
| Monitoring and Alerts | Limit on the number of monitoring rules                                                                   | No more than 5 monitoring rules can be enabled simultaneously                                                                                                                                                                           | Contact Singdata for adjustments |
|                       | Time range for querying alert events                                                                      | Maximum 7 days                                                                                                                                                                                                                          | Cannot be changed                |
|                       | Maximum number of notifications in notification policy configuration                                      | Up to 12 times                                                                                                                                                                                                                          | Cannot be changed                |
| Data Directory        | File upload size limit                                                                                    | Maximum 2 GiB                                                                                                                                                                                                                           | Cannot be changed                |
| Data Quality          | Time limit for querying validation results                                                                | Validation results are retained for 3 months                                                                                                                                                                                            | Cannot be changed                |
| Security Center       | Limit on the number of network policies that can be created under a single instance                       | Up to 20                                                                                                                                                                                                                                | Cannot be changed                |
|                       | Limit on the number of whitelist and blacklist entries that can be recorded under a single network policy | Up to 100,000 IPs                                                                                                                                                                                                                       | Cannot be changed                |

##

## Trial Period and Data Processing

**Limitations**:

The trial period for new accounts is until 30 natural days after the service instance is activated or until the 200 yuan voucher is used up.

**Post-expiration processing**:
During the trial period, you can apply to upgrade to a formal account at any time, or you can apply to upgrade to a formal account after the trial period ends. After the trial period ends, you will not be able to access or continue using the service instances created during the trial. The resource configurations and data within the service instances will be retained for 7 calendar days, after which the resource configurations and data within the service instances will be cleared and cannot be recovered.

If you need to continue using the service, please contact Singdata business within 7 calendar days after the trial period ends to apply for an upgrade to a formal account.

***

## Handling Exceeding Quotas

When your usage exceeds the quota limit, your operations will receive a system error message indicating the exceeded quota limit. Please clean up unnecessary resources or handle it according to the corresponding quota increase method in the second section "Quota and Usage Limit Overview."

***

## Temporary Disablement or Suspension

If you occupy too many system resources through abnormal usage, Singdata Lakehouse may temporarily disable your trial account or restrict the usage permissions of certain functions to ensure the normal use of other users. If such restrictions are applied, you will be notified through the phone number reserved in your account.

***

^

* **Email**: <<service@singdata.com>>

^
