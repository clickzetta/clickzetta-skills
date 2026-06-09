# Obtain Tencent Cloud ARN and ExternalID

When configuring Private Link to access the Lakehouse network, to ensure that the Lakehouse can normally read the endpoint status within your cloud platform account and enhance the security of this access method, please create an independent access control role in the cloud service platform and authorize and add an external ID. The specific operations are as follows.

^

## Tencent Cloud

**How to obtain ARN**:

You need to click "Create Role" on the Tencent Cloud Access Control page (<https://console.cloud.tencent.com/cam/role>) and select the role carrier as: Tencent Cloud Account:


Select "Other Main Account" for "Account Type";

Fill in the UID displayed on the Lakehouse page in the "Account ID";

Check "Enable Verification" in the "External ID" option, and customize a string of characters for subsequent verification use.



In the "Configure Role Policy", find and check the "Private Network (VPC) Read-Only Access" policy (Lakehouse needs to call the DescribeVpcEndPoint and DescribeVpcEndPointService interfaces through this role);


Define the role name and click the "Complete" button to complete the role creation.
