# Create Tencent Cloud Storage Connection

The goal of this step is to allow the Lakehouse cluster to access the object storage COS on Tencent. To achieve this goal, you can use two authentication methods provided by Tencent Cloud **Access Management**: **Access Key** and **Role Authorization**.

## Based on Access Key

```sql
CREATE STORAGE CONNECTION my_conn 
  TYPE COS
  ACCESS_KEY = '<access_key>'
  SECRET_KEY = '<secret_key>'
  REGION = 'ap-shanghai'
  APP_ID = '1310000503';
```

### Parameters:

* **TYPE**: This is the object storage type. For Tencent Cloud, fill in `COS` (case insensitive).

* **ACCESS\_KEY / SECRET\_KEY**: These are the access keys for Tencent Cloud. Refer to [Access Keys](https://cloud.tencent.com/document/product/598/40488) for how to obtain them.

* **REGION**: This refers to the region where the Tencent Cloud Object Storage (COS) data center is located. When Singdata Lakehouse accesses Tencent Cloud COS within the same region, the COS service will automatically route to internal network access. For specific values, please refer to the Tencent Cloud documentation: [Regions and Access Domains](https://cloud.tencent.com/document/product/436/6224).

* **APP\_ID**: The naming of Tencent Cloud storage buckets consists of the bucket name (BucketName) and APPID, connected by a hyphen "-". For example, `examplebucket-1310000503`, where `examplebucket` is user-defined, and `1310000503` is a system-generated numeric string (APPID).

## Role-Based Authorization

### STEP1: Create Data Permission Policy (LakehouseAccess):

* Log in to Tencent Cloud and go to the **Access Management** product console.
* In the **Access Management** page, navigate to **Policies** on the left sidebar, then select **Create Custom Policy** -> **Create by Policy Generator** -> **Visual Policy Generator**.
* In the **Visual Policy Generator** tab: **Service**: Select **Object Storage (cos**); **Action**: Select **All Actions** (you can make more granular selections based on actual needs); **Resource**: Select **All Resources** or **Specific Resources** as needed. In this example, select specific resources for the Shanghai region `cz-volume-sh-1311343935`![](.topwrite/assets/20250219-173802.jpeg =785)
* Click **Next**, fill in the **Policy Name** as LakehouseAccess and description, then click **Finish**.

### STEP2: Create Role on Client Side (LakehouseRole)

* Go to the Tencent Cloud **Access Management** product console.
* In the **Access Management** page, navigate to **Roles** on the left sidebar -> **Create Role** -> **Tencent Cloud Account**, select **Other Main Account**, and enter `100029595716` (Singdata's Tencent Cloud main account) in the **Account ID** field. Keep other options as default, then click **Next**.
* In the **Configure Role Policy** configuration, authorize the newly created LakehouseAccess custom policy to the current role. Click **Next**, fill in the **Role Name** as `LakehouseRole` to complete the creation.
* After successful creation, go to the details page of the role `LakehouseRole` in the role list to obtain the RoleARN information: `qcs::cam::uin/1000*******:roleName/LakehouseRole`.

### STEP3: Create Connection on Lakehouse Side

* Execute the following command in Studio or Lakehouse JDBC client:

```
CREATE STORAGE CONNECTION my_tx_connection_arn
   TYPE cos
   REGION = 'ap-shanghai'
   ROLE_ARN = 'qcs::cam::uin/1000********:roleName/LakehouseRole'
   APP_ID = '131****35';
```

^

> Note: To prevent the ROLE\_ARN from being obtained by third parties for unauthorized data access, you can use `EXTERNAL ID` as an additional verification layer to ensure that access is only allowed when the request contains the preset `EXTERNAL ID`. This means that even if a third party knows some other access information (such as the role ARN), they cannot access the resources without the correct `EXTERNAL ID`.

* During the process of creating a storage connection, Lakehouse will generate this EXTERNAL ID, which can be configured into the role verification of the COS account to achieve access control:

```
-- View EXTERNAL ID 
DESC CONNECTION my_tx_connection_arn ;
```

![](.topwrite/assets/20250219-181858.jpeg)

^

* Client Side: Enter the Tencent Cloud **Access Management** console, **Role** -> **LakehouseRole** -> **Role Carrier** -> **Manage Carrier**, select **Add Account** -> select **Current Main Account**, and fill in the main account ID: `100029595716` (Singdata's Tencent Cloud main account), and check **Enable Verification**, enter the EXTERNAL\_ID from the previous DESC result, click **Confirm** -> **Update**

***

^
