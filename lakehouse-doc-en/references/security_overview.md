# Security Features Overview

Singdata Lakehouse provides security capabilities across five layers — identity authentication, access control, network isolation, data protection, and backup & recovery — covering mainstream compliance scenarios from enterprise security baselines to Classified Protection Level 3 and industry-specific regulations.

## Security Capability Landscape

| Security Layer | Core Capabilities | Problems Addressed |
|----------------|-------------------|--------------------|
| Identity Authentication | MFA multi-factor authentication, SSO single sign-on | Account takeover, password leaks |
| Access Control | RBAC role system, fine-grained GRANT/REVOKE | Excessive privileges, unauthorized access |
| Network Isolation | IP allowlist, Private Link, private storage BYOS | Public internet exposure, traffic egress |
| Data Protection | Dynamic data masking, AES-256 storage encryption | Sensitive column leaks, static data exposure |
| Backup & Recovery | Time Travel, RESTORE TABLE, UNDROP | Accidental deletion or modification |

## Typical Compliance Scenarios and Feature Combinations

### Enterprise Internal Security Baseline

For teams just starting to build a data platform, prioritize the following three items:

- Establish a role system and use RBAC instead of direct grants for centralized permission management → [Access Control](access-control-general.md)
- Enable MFA on administrator accounts to prevent account compromise due to password leaks → [Identity Authentication](identity-auth.md)
- Configure an IP allowlist (network policy) to restrict access to corporate network segments → [Network Policy](network_policy.md)

### Classified Protection Level 3

Level 3 has explicit technical requirements across five control domains: identity verification, access control, security auditing, data confidentiality, and communication network security. The corresponding Lakehouse features are:

| Control Domain | Lakehouse Feature | Reference |
|----------------|-------------------|-----------|
| Identity Verification (two-factor authentication) | MFA / SSO | [Identity Authentication](identity-auth.md) |
| Access Control (least privilege) | RBAC + GRANT/REVOKE | [Access Control](access-control-general.md) |
| Security Audit (operation records) | Job history query, operation logs | [Security Compliance Audit Guide](security_compliance_audit_guide.md) |
| Data Transmission Confidentiality | SSL/TLS (enabled by default) | — |
| Data Storage Confidentiality | AES-256 storage encryption | [Storage Encryption](storage_encryption.md) |
| Communication Network Security | Private network connection (Private Link) | [Private Network Connection Overview](private-link-general.md) |

### Finance, Healthcare, and Other Sensitive Industries

Scenarios handling personal information and transaction data require additional data protection measures on top of the baseline:

- **Dynamic Data Masking**: Controls the visibility of sensitive columns such as phone numbers, ID numbers, and amounts by role, without touching the original data → [Dynamic Data Masking](dynamic-mask.md)
- **Storage Encryption (Custom KMS)**: Uses your own KMS key (ARN) so that key lifecycle is under your control; currently supports Alibaba Cloud and AWS → [Storage Encryption](storage_encryption.md)
- **Private Network Connection**: All data traffic stays on the internal network, never traversing the public internet → [Private Network Connection Overview](private-link-general.md)
- **Private Storage BYOS**: Data is written to your own object storage bucket; Singdata Lakehouse holds no data copies → [Private Storage BYOS](bring_your_own_storage.md)

### Data Disaster Recovery and Business Continuity

Scenarios that must meet RPO/RTO targets or guard against accidental operations:

- **Time Travel**: Retains 1 day of historical versions by default, configurable up to 90 days per table; supports querying historical snapshots at any point in time → [Backup and Recovery](data-recover.md)
- **RESTORE TABLE**: Rolls back table data to a specified point in time to recover from accidental overwrites
- **UNDROP TABLE**: Recovers a table after an accidental `DROP TABLE`

## Security Module Overview

### Access Control

Supports both ACL (direct grants) and RBAC (role-based grants); RBAC is recommended. Assign permissions to roles, then grant roles to users. Permission changes only require modifying the role definition rather than updating each user individually. There is no superuser in the system; all operations require explicit authorization.

- [Access Control Overview](access-control-general.md)
- [Configure Access Control](access-control-configuration.md)
- [Roles](roles.md) · [Metadata Objects and Privilege Points](meta-objects-and-privileges.md)
- [Explanation of Permissions for Built-in Workspace-Level Roles](permissions-of-built-in-workspace-level-roles.md)
- [User Authorization Getting Started Guide](user_permission_grand_guide.md)

### Identity Authentication

- **MFA**: Bind a virtual MFA device (any TOTP-compatible authenticator app); a dynamic verification code is required at login to prevent single-point password compromise
- **SSO**: Integrate with enterprise IdPs (such as Okta, Azure AD) so the enterprise manages account creation, deactivation, and permission lifecycle centrally

Reference: [Identity Authentication](identity-auth.md) · [Bind a Virtual MFA Device](using-google-authenticator.md) · [SSO Configuration](sso-configuration.md)

### Network Isolation

Three methods can be layered as needed, with increasing protection depth:

| Method | Protection Scope | Applicable Scenario |
|--------|------------------|---------------------|
| Network Policy (IP allowlist) | Blocks access requests from unauthorized IPs | Restricting connections to corporate network segments |
| Private Network Connection (Private Link) | Access via cloud provider internal network; traffic stays within the VPC | Production environments that prohibit public internet access |
| Private Storage (BYOS) | Data written to your own object storage bucket | Data sovereignty requirements; data must not reside on third-party infrastructure |

- [Private Network Connection Overview](private-link-general.md) · [Alibaba Cloud Private Network Connection Configuration](private_link.md)
- [Private Storage BYOS](bring_your_own_storage.md) · [Alibaba Cloud BYOS Configuration](alicloud_byos_configuration.md) · [Tencent Cloud BYOS Configuration](byos_tencentcloud_configuration.md)

### Dynamic Data Masking

A masking function is bound to a column. At query time the system dynamically rewrites the returned values based on the current user's identity or role, while the original data is always stored in full. Applicable to sensitive columns such as phone numbers, ID numbers, bank card numbers, and salary amounts. Masking policies can be bound at table creation time or added to or removed from existing table columns.

→ [Dynamic Data Masking](dynamic-mask.md)

### Storage Encryption

Enables AES-256 server-side encryption for data in newly created tables within a workspace. Two key modes are supported:

- **Managed Encryption**: Uses managed keys from the cloud provider's object storage service; no additional configuration required
- **Custom KMS Encryption**: Uses your own KMS key (ARN); the key lifecycle is under your control. Currently supports Alibaba Cloud and AWS

> **Note**: Once encryption is enabled on a table, it cannot be reverted to an unencrypted state. Encryption only applies to tables created after it is enabled; existing tables are not affected.

→ [Storage Encryption](storage_encryption.md)

### Backup and Recovery

Data protection is provided through the Time Travel mechanism:

- Retains 1 day of historical versions by default; configurable up to 90 days per table
- Historical data snapshots at any point in time within the retention window can be queried
- `RESTORE TABLE` rolls the table back to a specified point in time, overwriting current data
- `UNDROP TABLE` recovers a table after an accidental `DROP TABLE`

→ [Backup and Recovery](data-recover.md)

## Related Documentation

- [Security and Compliance](data_security.md) — Navigate all security features by scenario
- [Security Compliance Audit Guide](security_compliance_audit_guide.md)
- [Permission System Inventory Best Practices](security-system-inventory-based-information-schema.md)
