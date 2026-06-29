# Tencent Cloud BYOS Configuration

This guide will help you configure BYOS (Private Storage) on Tencent Cloud Object Storage (COS), enabling the Singdata Lakehouse to use your COS bucket as a data storage location.

## Prerequisites

* Have a Tencent Cloud account with COS service enabled
* Know the cloud platform and region of your Singdata Lakehouse instance
* Have administrative permissions for COS buckets

## Step 1: Prepare a COS Bucket

### Create a New Bucket (Recommended)

If you choose to create a new bucket dedicated to the Singdata Lakehouse:

1. **Log in to the Tencent Cloud COS Console**

   Visit: <https://console.cloud.tencent.com/cos/bucket>

2. **Click "Create Bucket"**

**Configure Bucket Basic Information**

| Item                     | Setting                                         | Description                                                                                   |
| ------------------------ | ----------------------------------------------- | --------------------------------------------------------------------------------------------- |
| **Region**               | Same as the Lakehouse instance                  | :warning: **Critical Requirement**: Must be the same region as the Singdata Lakehouse instance. |
| **Name**                 | Custom (e.g., `my-company-lakehouse`)           | Globally unique; recommend including a usage identifier.                                      |
| **Access Permission**    | Private read/write                              | Ensure data security.                                                                         |
| **Multi-AZ Feature**     | Disabled                                        | Can be enabled based on data availability and reliability requirements. Enabling will increase storage costs charged by the cloud provider. |
| **Versioning**           | Disabled                                        | Avoid additional costs.                                                                       |
| **Server-Side Encryption** | No encryption                                 | The Lakehouse manages encryption on its own; global encryption may affect performance.        |

Other configurations can be left disabled.

### Use an Existing Bucket

If you choose to use an existing bucket:

#### Verify Region Configuration

The bucket must be in the same Region as the Singdata Lakehouse instance. For example:

\- Lakehouse instance in: Tencent Cloud - Shanghai

\- COS Bucket must be in: China - Shanghai

Your service instance's "Cloud Provider and Region" information can be found on the service instance homepage:

:-: ![](/.topwrite/assets/image_1760270239517.png =747)

#### Choose a Storage Path

You can choose one of the following:

**Option 1: Use the Entire Bucket (Recommended)**

Applicable scenario: Bucket dedicated to the Lakehouse.

**Option 2: Use a Specific Directory Under the Bucket**

Applicable scenario: Need to isolate data for different purposes within the same bucket.

***

**Data Security Warning**:

1. Ensure the selected path is not shared with other business systems;

2. The Singdata Lakehouse will perform read, write, and delete operations on files under this path;

3. Sharing paths may lead to:

* Data being accidentally deleted or overwritten
* Impact on the normal operation of other business systems
* Data consistency issues

Recommendation: Create a dedicated bucket or use a dedicated directory for the Lakehouse.

###

### Record Required Information

Please record the following information, which will be needed for subsequent configuration:

* **Bucket Name**
* **Bucket Region**
* **Your Tencent Cloud Root Account ID**

How to view the root account ID:

1. Log in to the Tencent Cloud console
2. Click the avatar in the upper right corner
3. In "Account Information", view the "Account ID"

## Step 2: Configure Bucket Access Policy

**1. Go to the Bucket Management Page**

* Find your bucket in the COS console and click the bucket name to enter the details page

**2. Go to the Permission Management Page**

:-: ![](/.topwrite/assets/39c3600e-2652-4475-a7fa-f2f40bac51e3.jpeg =772)

* Click "Permission Management" in the left menu.
* In the "Policy Permission Settings" section, click "Add Policy".

**3. Configure the Authorization Policy**

Select "Custom Authorization" and fill in the following information:

| **Item**              | **Setting**                                                                                                                                                  |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Authorized User**   | Specified User                                                                                                                                               |
| **Resource Scope**    | When the bucket is dedicated to Singdata: select the entire bucket&#xA;When Singdata uses a specific directory: select specified directory                      |
| **Select Template**   | Custom Policy                                                                                                                                                |
| **Effect**            | Allow                                                                                                                                                        |
| **User**              | Select "Root Account" and enter Singdata Lakehouse's root account on Tencent Cloud: 100029595716                                                             |
| **Resource**          | When the bucket is dedicated to Singdata: select the entire bucket&#xA;When Singdata uses a specific directory: select specified resource path and enter the path. Note: append /\* after the subdirectory. |
| **Action**            | Select "All Actions".                                                                                                                                        |
| **Condition**         | Do not add any conditions.                                                                                                                                   |

### :-: ![](/.topwrite/assets/image_1760273495375.png =647)

### :-: ![](/.topwrite/assets/image_1760273408668.png =653)

^

**Why are all operation permissions required?**

The Singdata Lakehouse needs all operation permissions under this path to ensure normal data addition, deletion, and read/write functionality.

^

After completing the above configuration, you can use your private storage path and cloud platform root account ID when creating a new private storage.
