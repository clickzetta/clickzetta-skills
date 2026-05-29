# Tencent Cloud

When you need to access the Singdata Lakehouse service through the internal network within the cloud provider's VPC, you need to create an endpoint in Tencent Cloud that connects to the Singdata Lakehouse endpoint service. Then replace the domain name of the JDBC connection or API accessing Singdata Lakehouse with the domain name of the endpoint.

:-: ![](.topwrite/assets/privatelink_customer_access_LH_example.png)

## Steps

The following operations need to be completed in the Alibaba Cloud console environment.

1\. **Add to Whitelist**. First, please confirm that you have added your cloud platform account to the whitelist.

![](.topwrite/assets/image_1732869126126.png)

To ensure that Lakehouse can correctly read the status of your endpoint and enhance the security of obtaining endpoint information within your cloud service platform, please create an independent access control role within the cloud service platform, and authorize and add an external ID.

**How to query ARN and ExternalID**:

On the Tencent Cloud access control role list page, click the role name you want to add its ARN, and in the role details, select "Role Carrier", respectively copy the "RoleArn" and "External ID" from this page, and return to the Singdata Lakehouse page. In the add whitelist popup, paste the above two items into the corresponding options.

After pasting, click "OK".

:-: ![](.topwrite/assets/image_1733067670318.png =826)

:-: ![](.topwrite/assets/image_1733067744128.png =826)

^

:-: ![](.topwrite/assets/image_1733067854956.png =447)

2\. **Create a New Endpoint**. On the endpoint page, click the "New" button, select "Other Account" for "Peer Account Type". Then, in "Peer Account UIN" and "Peer Endpoint Service ID", respectively fill in the "Lakehouse UID" and "Endpoint Service ID" copied from the Lakehouse page. Click "OK".

:-: ![](.topwrite/assets/image_1733063999441.png =455)

3\. **Allow Endpoint Connection**. After creation, refresh the "Endpoint" page in Lakehouse, and you will see the endpoint you created in the list. Click "Allow Connection" to complete the network interconnection configuration based on the private connection.
