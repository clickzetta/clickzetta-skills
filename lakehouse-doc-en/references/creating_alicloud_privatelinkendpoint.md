# Alibaba Cloud

When you need to access the Singdata Lakehouse service through the internal network within the cloud provider's VPC, you need to create an endpoint in Alibaba Cloud that connects to the Singdata Lakehouse endpoint service. Then replace the domain name of the JDBC connection or API accessing Singdata Lakehouse with the domain name of the endpoint.



## Steps

The following operations need to be completed in the Alibaba Cloud console environment.

1\. **Add to Whitelist**. First, please confirm that you have added your cloud platform account to the whitelist.


To ensure that Lakehouse can normally read the status of your endpoint and enhance the security of obtaining endpoint information within your cloud service platform, please create an independent access control role in the cloud service platform, and authorize and add the external ID.

^

On the Alibaba Cloud "RAM Access Control" - "Roles" page, select the access control role whose ARN you want to add, copy the values of ARN and externalID respectively, return to the Singdata Lakehouse page, and in the add whitelist popup, copy the above two items into the corresponding options.



^


2\. **Create Endpoint**. On the "Endpoints" page of the Alibaba Cloud console, click the "Create Endpoint" button. Select the same region as Lakehouse in the "Region" field, and select "Other Endpoint Services" on the page. Copy the endpoint service name of the region from the Lakehouse service and fill it in on this page.



^



3\. **Allow Endpoint Connection**. After creation, refresh the "Endpoints" page in Lakehouse, and you will see the endpoint you created in the list. Click "Allow Connection" to complete the network interconnection configuration based on the private network connection.

^