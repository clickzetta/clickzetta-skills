# Data Storage Encryption

## Overview

Lakehouse supports server-side encryption (SSE) for table data stored in object storage, using the AES-256 encryption algorithm to ensure your data is protected at the storage layer.

You can choose to encrypt data using either the cloud provider's managed key or your own KMS key, depending on your security and compliance requirements.

## Encryption Modes

Lakehouse offers two encryption modes:

| Mode                         | Description                                                                                 |
| ---------------------------- | ------------------------------------------------------------------------------------------- |
| Managed Encryption (Default) | Encrypts data using the cloud provider's managed key. No additional configuration required. |
| Custom KMS Encryption        | Encrypts data using your own KMS key. Requires a KMS ARN and KMS Region.                    |

> Custom KMS encryption (BYOK) is currently in limited release and supported on Alibaba Cloud and AWS only. Tencent Cloud regions only support managed encryption.

## Encryption Scope

* You can enable encryption at the workspace level. Once enabled, all newly created data objects within the workspace will be encrypted by default.
* You can enable encryption on a workspace at any time. Enabling it will not affect existing tables — encryption will only apply to newly created tables.

> ⚠️ Once a table is encrypted, it cannot be reverted to an unencrypted state. Please confirm before enabling.

## How to Use

### Enable Encryption When Creating a Workspace

1. On the Create Workspace page, turn on the "Storage Encryption" toggle.

2. To use managed encryption, simply leave the KMS ARN field empty.

3. To use a custom KMS key:

   * Enter your KMS key ARN.
   * Enter the KMS Region.

### Adjust Encryption Settings When Modifying a Workspace

* If the workspace does not use a custom KMS key, you can freely enable or disable the encryption toggle.
* If the workspace already uses a custom KMS key, the encryption settings will be locked — encryption cannot be disabled and the key configuration cannot be changed.

## Key Management

* Each data object uses exactly one key throughout its lifecycle. The key cannot be changed.
* You may create multiple keys and assign different keys to data objects in different workspaces.
* Once a custom KMS key is applied, the KMS ARN and KMS Region become read-only and cannot be modified.

> ⚠️ Once a custom KMS key is configured, the key settings cannot be changed and encryption cannot be disabled. Please verify your key information carefully before configuring.

> ⚠️ Please safeguard your custom KMS encryption key. If the key is lost, data encrypted with that key in Lakehouse will become permanently unreadable and cannot be recovered.

## KMS Request Costs and Caching

Data warehouse workloads involve frequent data reads and writes, which can quickly reach the cloud provider's KMS QPS limits and generate significant KMS API request costs when using a custom KMS key. To mitigate this, Lakehouse employs a key caching mechanism that reduces KMS API calls. The cache has a validity period of 5 minutes, meaning that after a KMS key is revoked or invalidated, there may be a window of up to 5 minutes during which encrypted data can still be read or written.

> ⚠️ We recommend using managed encryption whenever possible. Avoid custom KMS keys unless strictly required, to prevent hitting KMS request limits (which may impact read/write performance) and incurring excessive KMS API request fees. KMS request costs are billed to the cloud account where your KMS key resides, not to your Lakehouse bill.

## FAQ

**Q: Will existing data be encrypted after I enable workspace encryption**?

No. Encryption only applies to data objects created after the setting is enabled. Existing data is not affected.

**Q: Can I remove encryption from an already encrypted table**?

No. Table encryption is irreversible.

**Q: Can I modify the custom KMS key configuration after it is set**?

No. Once a custom KMS key is configured, both the key information and the encryption toggle are locked and cannot be modified.

**Q: If I lose my custom KMS key, what happens**?

Please safeguard your custom KMS encryption key at all times. If the key is lost, data encrypted with that key in Lakehouse will become permanently unreadable and cannot be recovered.

**Q: Does using a custom KMS key incur additional costs**?

Yes. Each data read/write operation requires a KMS API call for encryption or decryption. Although Lakehouse reduces the number of requests through a 5-minute key caching mechanism, high-frequency workloads may still generate considerable KMS request fees. These fees are billed to the cloud account where your KMS key resides. We recommend using managed encryption to avoid such costs.
