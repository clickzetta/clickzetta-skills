# Trial Account Quotas and Limits

## Trial Account Overview

Singdata Lakehouse provides trial accounts so new users can evaluate platform features and performance at no cost.

New accounts start in trial status. You can see the **Trial** status label on the left side of the Management Center. After you create a service instance, the account receives a **$50 USD voucher** that is valid for 30 days.


![](.topwrite/assets/image_1740710821088.png =189)

To maintain platform stability and fair resource allocation, trial accounts are subject to the following quotas and limits.

## Quotas and Usage Limits

| Feature | Limit | Limit Value / Rule | How to Increase the Quota |
| --- | --- | --- | --- |
| Global | Maximum number of users under a single tenant | 500 | Cannot be changed |
| Global | Number of instances under a single tenant | You can create instances in any region, but the total number cannot exceed 1. | Upgrade to a production account |
| Global | Number of Workspaces under a single instance | No more than 100 | Cannot be changed |
| Data Integration | Offline sync tasks | The concurrency limit for a single task is 10. No more than 2 tasks can run at the same time. Each task can run for up to 6 hours. | Upgrade to a production account |
| Data Integration | Real-time integration tasks | No more than 2 tasks can run at the same time. Each task can run for up to 6 hours. | Upgrade to a production account |
| Data Integration | Multi-table real-time sync tasks | A multi-table real-time sync task uses offline sync task quota and real-time integration task quota separately. | Upgrade to a production account |
| Data Development | Maximum number of lines in SQL / Python / Shell / JDBC task files | 5,000 lines of code | Cannot be changed |
| Data Development | SQL query result row limit | 1,000 rows by default. You can adjust the limit up to 10,000 rows. | Cannot be changed |
| Data Development | SQL query result download limit | Up to 4 GiB | Cannot be changed |
| Data Development | Temporary query run history retention | Up to 7 days | Cannot be changed |
| Data Development | Historical version and commit version retention | Permanently retained | Cannot be changed |
| Task Scheduling | Number of task instances that can start concurrently under a single tenant | Offline sync task instances: 20; SQL task instances: unlimited; Python task instances: 5; Shell task instances: 5; JDBC task instances: 20. | Upgrade to a production account |
| Task Scheduling | Maximum system fallback timeout for a single task instance | Minimum: 1 minute. Maximum: 168 hours (7 days). | Cannot be changed |
| Task Scheduling | Instance auto-retry interval | Minimum: 1 minute. Maximum: 1 day. | Cannot be changed |
| Task Scheduling | Scheduling wait time | Minimum: 1 minute. Maximum: 168 hours (7 days). | Cannot be changed |
| Operations Center | Task instance history retention | Periodic instances: 32 days; backfill instances: 32 days; temporary instances: 8 days. | Cannot be changed |
| Operations Center | Task instance list query limit | Displayed results are limited by instance retention time, up to 6 months. | Cannot be changed |
| Operations Center | Task operation log query time range | 6 months | Cannot be changed |
| Operations Center | Task operation log history retention | 6 months | Cannot be changed |
| Compute Cluster | Maximum total compute specification under a single instance | The total specification of all VClusters cannot exceed 28 CRU. The `sys` Workspace uses 9 CRU by default, and all other Workspaces under the service instance can use up to 19 CRU in total. | Upgrade to a production account |
| Compute Cluster | Concurrent compilation jobs | No more than 2 | Contact Singdata Sales |
| Data Objects | Maximum number of data objects, such as tables and views, under a single instance | 1,000 | Upgrade to a production account |
| Stream Writing | Maximum number of Stream objects under a single instance | 10 | Upgrade to a production account |
| Stream Writing | Data write QPS under a single instance | 5 | Upgrade to a production account |
| Job History | Job list query limits | Time range: up to 7 days. Number of job history records returned: up to 10,000. Job history records above this quota can be queried with SQL from the `sys.information_schema.job_history` view. | Cannot be changed |
| Job History | Daily SMS sending limit | **Verification codes**: up to 1 per minute, 20 per hour, and 40 per calendar day. **Alert notifications and similar messages**: up to 50 per calendar day. | Cannot be changed |
| Monitoring and Alerts | Number of monitoring rules | No more than 5 monitoring rules can be enabled at the same time. | Contact Singdata Sales |
| Monitoring and Alerts | Alert event query time range | Up to 7 days | Cannot be changed |
| Monitoring and Alerts | Maximum sends in a notification policy | Up to 12 | Cannot be changed |
| Data Directory | File upload size | Up to 2 GiB | Cannot be changed |
| Data Quality | Validation result query time limit | Validation results are retained for 3 months. | Cannot be changed |
| Security Center | Number of Network Policies under a single instance | Up to 20 | Cannot be changed |
| Security Center | Number of allowlist and blocklist entries under a single Network Policy | Up to 100,000 IP addresses | Cannot be changed |

## Trial Period and Data Handling

**Limit**:

The trial period for a new account ends 30 calendar days after the service instance is activated, or when the CNY 200 voucher is used up, whichever comes first.

**After expiration**:

During the trial period, you can apply to upgrade to a production account at any time. You can also apply after the trial period ends. After the trial period ends, you cannot access or continue using the service instance created during the trial. Resource configurations and data in the service instance are retained for 7 calendar days. After 7 calendar days, they are deleted and cannot be recovered.

To continue using the service, contact Singdata Sales within 7 calendar days after the trial period ends and apply to upgrade to a production account.

***

## Handling Quota Exceeded Errors

When your usage exceeds a quota, the system returns an error message that identifies the exceeded quota. Clean up unnecessary resources, or follow the quota increase method listed in [Quotas and Usage Limits](#quotas-and-usage-limits).

***

## Temporary Disablement or Suspension

If abnormal usage consumes excessive system resources, Singdata Lakehouse may temporarily disable your trial account or restrict some features to protect other users' access. If these restrictions are applied, Singdata will notify you through the phone number reserved in your account.

***

## Contact

* **Email**: <service@singdata.com>
