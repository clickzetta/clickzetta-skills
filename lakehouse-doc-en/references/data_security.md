# Security

Singdata Lakehouse security capabilities cover six areas: user permissions, data masking, network access control, audit compliance, identity authentication, and data recovery.

---

## I Want to Manage Users and Permissions

| Scenario | Reference |
|------|---------|
| Onboard a new colleague, add them to a workspace | [User Authorization Getting Started Guide](user_permission_grand_guide.md) · [Quick Start: Manage Users](quick_start_user_management.md) |
| Design a role system (RBAC) | [Access Control Overview](access-control-general.md) · [Role Management](roles.md) |
| View what permissions built-in roles have | [Built-in Role Permission List](permissions-of-built-in-workspace-level-roles.md) |
| Grant / revoke permissions for a user | [GRANT Privileges](grant-privileges.md) · [REVOKE Privileges](revoke-privileges.md) |
| Audit and clean up the permission system | [Permission System Inventory Best Practices](security-system-inventory-based-information-schema.md) |

---

## I Want to Protect Sensitive Data

| Scenario | Approach | Reference |
|------|------|---------|
| Mask specific columns (phone numbers / ID numbers / amounts) | Dynamic Data Masking policy | [Dynamic Data Masking](dynamic-mask.md) |
| Encrypt data at rest | Storage encryption | [Storage Encryption](storage_encryption.md) |
| Use your own encryption keys (BYOK) | BYOK | [BYOK Model Integration](byok.md) |

---

## I Want to Control Network Access

| Scenario | Approach | Reference |
|------|------|---------|
| Restrict access to company IP addresses only | Network Policy (IP allowlist) | [Network Policy](network_policy.md) |
| Connect via private network (no public internet) | Private Link | [Private Network Connection Overview](private-link-general.md) · [Alibaba Cloud Configuration](private_link.md) · [Tencent Cloud Configuration](creating_tencentcloud_privatelinkendpoint.md) |
| Use your own object storage (BYOS) | Private Storage | [Private Storage Overview](byos_general.md) · [Alibaba Cloud Configuration](alicloud_byos_configuration.md) |

---

## I Want to Meet Audit and Compliance Requirements

| Scenario | Reference |
|------|---------|
| View who did what and when | [Job History Analysis](job_history_analysis_with_information_schema.md) |
| Complete security compliance audit guide | [Security Compliance Audit Guide](security_compliance_audit_guide.md) |
| Overview of all security features | [Security Features Overview](security_overview.md) |

---

## I Want to Strengthen Identity Authentication

| Scenario | Reference |
|------|---------|
| Enable multi-factor authentication (MFA) | [Bind a Virtual MFA Device](using-google-authenticator.md) |
| Configure Single Sign-On (SSO) | [SSO Configuration](sso-configuration.md) |

---

## I Want to Recover Accidentally Deleted or Modified Data

| Scenario | Reference |
|------|---------|
| View historical versions of a table | [Time Travel Concept](time-travel-concept.md) |
| Restore to a specific point in time | [RESTORE TABLE](restore.md) |
| Recover a dropped table | [UNDROP TABLE](undrop-table.md) |
| Data backup and recovery overview | [Backup and Recovery](data-recover.md) |
