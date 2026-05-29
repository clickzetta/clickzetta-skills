# Bring Your Own Storage (BYOS)

> **Private Preview**: This feature is currently in private preview. To enable it for your account, please contact your sales representative to request access through the feature gating process.

## 1. Overview

Bring Your Own Storage (BYOS) allows you to use your own cloud object storage as the data storage location for Lakehouse workspaces. With BYOS, you can:

* Configure private storage through the web console without complex technical setup.
* Store workspace data in object storage buckets managed under your own cloud platform account.
* Maintain full control over storage costs and storage policies.

## 2. Use Cases

BYOS is designed for the following scenarios:

* **Data Compliance**: Your organization requires data to reside in object storage under your own cloud account to meet regulatory or compliance requirements.
* **Data Sovereignty**: You need complete control over where data is stored and who can access it.
* **Hybrid Deployment**: Some workspaces use Lakehouse-managed storage, while others with stricter compliance needs use your own storage.

## 3. Prerequisites

### 3.1 Create a Storage Bucket

Before configuring BYOS, create a storage bucket on your cloud platform that meets the following requirements:

**Required settings**:

| Setting        | Requirement                                                    | Reason                                                                                   |
| -------------- | -------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| Region         | Same cloud provider and same region as your Lakehouse instance | Avoids cross-region data transfer fees                                                   |
| Storage Class  | Standard                                                       | Do not use infrequent access or archive classes, as they incur additional access charges |
| Access Control | Private (private read/write)                                   | Ensures data security                                                                    |
| Dedicated Use  | Exclusive to Lakehouse                                         | Do not share the bucket with other applications to avoid data conflicts                  |

**Recommended settings**:

| Setting                | Recommended Value          | Reason                                                                                                                                             |
| ---------------------- | -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Storage Redundancy     | Choose based on your needs | Locally redundant storage is sufficient for most cases; zone-redundant storage is available for higher availability requirements                   |
| Versioning             | Disabled                   | Lakehouse manages data versioning internally. Enabling bucket-level versioning may incur additional storage costs                                  |
| Server-Side Encryption | Disabled                   | Lakehouse handles encryption for specific data based on workspace configuration. Enabling bucket-wide encryption may impact read/write performance |
| Lifecycle Rules        | Do not configure           | Lakehouse manages file lifecycle internally                                                                                                        |

### 3.2 Create an Access Policy

You must grant the Lakehouse service account full control over your storage bucket (or a dedicated path within it).

**Best practice**: Designate a dedicated bucket — or a specific path prefix within a bucket — exclusively for Lakehouse use, then grant the Lakehouse service account full control permissions on that bucket or path. This ensures clean isolation and avoids permission conflicts with other workloads.

**Getting the Lakehouse Account ID**: The Lakehouse service operates under a cloud-provider-specific account ID in your region. To obtain this account ID, please contact your sales representative or technical support team.

Once you have the Lakehouse account ID, configure the access policy on your cloud platform. The exact steps vary by cloud provider, but the general approach is:

1. Create an IAM or bucket policy that grants the Lakehouse account ID full control over the designated bucket or path.

2. If your cloud provider requires cross-account authorization (e.g., through a role trust relationship), configure the trust policy to allow the Lakehouse account to assume the role.

**Example (AWS)**: Create an S3 bucket policy that grants the Lakehouse account ID `s3:*` permissions on the designated bucket or path prefix, and ensure the IAM trust policy allows the Lakehouse account to assume the role. Other cloud providers follow a similar pattern using their respective IAM and policy mechanisms.

For provider-specific instructions, refer to your cloud provider's documentation on cross-account access or contact the Lakehouse technical support team.


## 4. Configuration Steps

### Step 1: Navigate to Private Storage Management

1. Log in to the Lakehouse web console.
2. Go to **Management** → **More** → **Private Storage**.
3. Click the + **New** button.

### Step 2: Fill in Storage Information

In the configuration dialog, provide the following details:

1. **Name** (required): Must start with a letter (A-Z, a-z) or underscore (`_`), and be 3–28 characters long. The name must be unique within your Lakehouse service instance. It cannot be changed after creation.

2. **Primary Account ID** (required): Enter your cloud platform account ID. Lakehouse uses this to assume the authorized role and access your bucket. You can find your account ID in your cloud provider's management console, typically under account settings or account information.


3. **Bucket Name** (required): Enter the name of your storage bucket. You can optionally include a path prefix. For example:
   * Bucket only: `my-lakehouse-bucket`
   * Bucket with path: `my-lakehouse-bucket/data/lakehouse`

4. **Description** (optional): A description of the private storage to help users understand its business purpose and avoid accidental misuse.

After filling in all fields, click **OK** to create the private storage configuration.

> You can create multiple private storage configurations under a single Lakehouse service instance.

### Step 3: Verify Connectivity

After creation, the private storage connection status defaults to **Failed**. You need to verify connectivity:

1. In the private storage list, locate your newly created entry.
2. Click the **Test Connectivity** button on the right side of the entry.

During the connectivity test, Lakehouse performs the following checks using its service account on the same cloud provider and region:

* Whether the storage bucket exists.
* Whether the bucket is in the correct region.
* Whether the access permissions are configured correctly.

Once verification passes, the connection status changes to **Success**.

> If the test fails, double-check your bucket name, region, account ID, and access policy configuration.

### Step 4: Associate with a Workspace

You can associate a private storage location with a workspace only during workspace creation:

1. When creating a new workspace, click to expand the **Advanced Settings** section.
2. Enable the **Private Storage** toggle.
3. Select an existing private storage configuration from the dropdown list.
4. Click **OK** to complete workspace creation.

Key points:

* A single private storage configuration can be associated with multiple workspaces.
* Data from different workspaces is stored under separate sub-paths within the same bucket, so workspaces do not interfere with each other.

## 5. Important Limitations

### 5.1 Functional Limitations

* A workspace's storage location cannot be changed after creation.
* A private storage configuration cannot be deleted while it is still associated with any workspace. You must delete the workspace first.

### 5.2 Region Limitations

* Only storage buckets in the same cloud provider and same region as your Lakehouse instance are supported.
* For AWS environments, ensure the bucket is in the same availability zone to avoid cross-zone traffic charges.

### 5.3 Responsibility Boundaries

* When using BYOS, you are responsible for the availability and reliability of the storage bucket referenced by the private storage configuration.
* Any data issues not caused by Lakehouse operations are your responsibility.

### 5.4 Billing

When using BYOS:

* Lakehouse does not charge storage capacity fees for data in your private storage. Standard billing continues for any data in Lakehouse-managed storage locations.
* You pay your cloud provider directly for:
  * Storage capacity
  * API access fees
  * Public network egress fees (if applicable)
* Logs and temporary files generated by Lakehouse will consume space in your storage bucket.

### 5.5 Performance Considerations

* Storage performance directly affects Lakehouse query and processing efficiency.
* Ensure your storage service meets the required QPS (queries per second) and bandwidth for your workload.
* Avoid sharing the bucket with other applications that may compete for storage I/O resources.

## 6. FAQ

**Q1: Can I migrate an existing workspace to BYOS**?
No. A workspace's storage location is fixed at creation time and cannot be changed afterward.

**Q2: Can one storage bucket be used by multiple workspaces**?
Yes. A single BYOS configuration can be associated with multiple workspaces. However, plan your bucket usage carefully based on your actual needs.

**Q3: After enabling BYOS, what data does Lakehouse still store in my bucket**?
Query cache, temporary files, and other operational data will be stored in your bucket and will consume some storage capacity.
