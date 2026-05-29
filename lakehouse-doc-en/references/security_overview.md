# Singdata Lakehouse Security Features Overview

Singdata Lakehouse is committed to creating a secure and reliable cloud environment for customers, ensuring that their accounts, information, business, and data receive enterprise-level security protection. To achieve this goal, Singdata Lakehouse employs multi-layered security measures covering architecture security, network security, access control, auditing and monitoring, and data encryption. Below is a detailed analysis of these security features.

## 1. Architecture Security and Multi-Tenant Isolation

Singdata Lakehouse is deployed in a public cloud environment, using a high-availability architecture to ensure service stability and reliability. By using multi-replica redundant storage and various protection technologies (such as host security, WAF, anti-DDoS, etc.), it ensures the security of the service architecture and infrastructure.

To achieve data and computing resource isolation between different tenants, Singdata Lakehouse performs data integrity and correctness checks at the data transmission layer, ensuring data integrity and tamper resistance.

![](.topwrite/assets/Security_System_en.png)

## 2. Network Security

Singdata Lakehouse supports SSL/TLS encrypted transmission to ensure data security during transmission. Tenants can control the range of network addresses that can access their Lakehouse service instances by setting IP whitelist policies. For example, tenants can add their company's internal IP addresses to the whitelist to allow access only from these addresses.

## 3. Access Control

Singdata Lakehouse achieves further isolation of data and computing resources through workspaces. Only users who have joined a workspace can access the data and computing resources within it. Additionally, Singdata Lakehouse provides two authorization methods: ACL (Access Control List) and RBAC (Role-Based Access Control), allowing users to customize roles based on business needs and grant table-level granular permissions.

For example, an administrator can create a workspace for data analysts and assign them the appropriate roles and permissions so that they can access and process specific data tables.

## 4. Auditing and Monitoring

Singdata Lakehouse records all operations on data, with these historical records being read-only and uneditable, and retained for up to 6 months. The platform also provides monitoring and alerting functions to help users promptly detect job anomalies, data anomalies, and other situations, and send notifications based on the severity of the alerts.

For example, when a job execution fails, the system will automatically send an alert notification to the administrator so that they can take timely measures to resolve the issue.

## 5. Data Encryption

Singdata Lakehouse encrypts sensitive data (such as account information) for storage, ensuring data security throughout its lifecycle. Users can further protect their data by configuring the data encryption feature. When the data encryption feature is enabled, data will remain encrypted throughout its lifecycle after being written to Lakehouse, and will only be decrypted when processed by the tenant's dedicated computing nodes.

For example, when a company needs to store and process data involving personal privacy, it can enable the data encryption feature to ensure data security.

## 6. Data Disaster Recovery and Restoration

Singdata Lakehouse relies on the storage services of cloud service providers at the IaaS layer, built on a multi-replica, high-availability cloud infrastructure, providing extremely high service availability and data reliability. Additionally, the platform by default provides a 1-day data recovery feature, effectively reducing the risk of accidental data deletion or modification, and enhancing data integrity protection.

For example, in the event of accidental data deletion, users can use the time travel feature to restore data to any state within the past 7 days, thereby avoiding the risk of data loss.

In summary, Singdata Lakehouse provides a secure and reliable cloud environment for users through multi-layered security measures. Users can flexibly configure and use these security features according to their needs and scenarios to ensure the security of their business and data.
