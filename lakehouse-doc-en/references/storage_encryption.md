# Data Storage Encryption

## Overview

Lakehouse supports server-side encryption (SSE) for table data stored in object storage, using the AES-256 encryption algorithm to ensure your data is securely protected at the storage layer.

You can choose to use cloud provider-managed keys or your own KMS keys for encryption, depending on your security and compliance requirements.

## Encryption Modes

Lakehouse provides two encryption modes:

| Mode         | Description                                             |
| ---------- | ---------------------------------------------- |
| Managed Encryption (Recommended)   | Uses managed keys provided by the cloud provider's object storage service for encryption, no additional configuration required                  |
| Custom KMS Encryption | Uses your own KMS keys for encryption, requires providing KMS ARN (ID) and KMS Region |

> Custom KMS encryption currently supports Alibaba Cloud and AWS platforms. Tencent Cloud only supports managed encryption mode.

## Encryption Scope

* You can enable encryption uniformly at the workspace level. After enabling, newly created data objects within the workspace will be encrypted by default.
* You can enable encryption for a workspace at any time. Enabling encryption will not affect existing tables in the workspace; it only applies encryption to newly created tables.

> ⚠️ Once a table is encrypted, it cannot be restored to a non-encrypted state. Please confirm before enabling.

## Usage

### Enable Encryption When Creating a Workspace

1. On the Create Workspace page, toggle on the "Storage Encryption" switch.

2. If you wish to use managed encryption, leave the KMS ARN blank.

3. If you wish to use a custom KMS key:

   * Enter your KMS key ARN.
   * Enter the KMS Region.

### Adjust Encryption Settings When Modifying a Workspace

* If the workspace does not use a custom KMS key, you can freely toggle the encryption switch on or off.
* If the workspace already uses a custom KMS key, the encryption settings will be locked, and you cannot disable encryption or modify the key configuration.

## Key Management

* Each data object can only use one key during its lifecycle, and the key cannot be changed.
* You can create multiple keys and select different keys when encrypting data objects in different workspaces.
* After using a custom KMS key, the KMS ARN and KMS Region become read-only and cannot be modified.

> ⚠️ After encrypting with a custom KMS key, the key configuration cannot be modified and encryption cannot be disabled. Please carefully confirm the key information before configuration.

> ⚠️ Please keep your custom KMS encryption keys secure. Once a key is lost, data encrypted with that key in Lakehouse will be permanently unreadable and unrecoverable.

## KMS Request Costs and Caching Mechanism

Since data warehouse scenarios involve frequent data reads and writes, using custom KMS keys can easily hit the QPS request limits of the cloud provider's KMS service and generate significant KMS API request costs. To address this, Lakehouse employs a key caching mechanism to reduce API calls to KMS, with a cache validity period of **5 minutes**. This means that after a KMS key is revoked or becomes invalid, there is still a window of up to 5 minutes during which encrypted data can be read and written.

> ⚠️ It is recommended to **prioritize managed encryption mode** and avoid using custom KMS keys to prevent hitting KMS request limits that affect read/write performance or generating significant KMS request costs. KMS request costs are typically incurred in the cloud account where your KMS key resides, not in your Lakehouse bill.

## FAQ

**Q: After enabling workspace encryption, will historical data be encrypted?**

No. Enabling encryption only affects data objects created thereafter. Existing data is not affected.

**Q: Can encryption be removed from an already encrypted table?**

No. Table encryption operations are irreversible.

**Q: Can custom KMS key configuration be modified after setup?**

No. Once a custom KMS key is configured, neither the key information nor the encryption toggle can be modified.

**Q: What if a custom KMS key is lost?**

Please ensure you keep your custom KMS encryption keys secure. Once a key is lost, data encrypted with that key in Lakehouse will be permanently unreadable and unrecoverable.

**Q: Does using custom KMS encryption incur additional costs?**

Yes. Each data read/write requires calling the KMS API for encryption/decryption. Although Lakehouse reduces request frequency through a 5-minute key caching mechanism, significant KMS request costs may still be incurred in high-frequency read/write scenarios. These costs are incurred in the cloud account where your KMS key resides. It is recommended to prioritize managed encryption mode to avoid such costs.
