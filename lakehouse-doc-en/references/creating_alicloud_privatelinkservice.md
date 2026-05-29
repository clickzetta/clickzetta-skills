# Create Alibaba Cloud Endpoint Service

When you need to use Singdata Lakehouse to access services within your cloud vendor's VPC (such as a self-built MySQL database), you first need to create an endpoint service on Alibaba Cloud and configure the service to be accessed as the service resource of the endpoint service.

:-: ![](.topwrite/assets/private_link_access_customer_example.png)

## Steps

The following operations need to be completed in the Alibaba Cloud console environment.

1\. Please refer to https\://help.aliyun.com/zh/privatelink/user-guide/create-and-manage-endpoint-services? to complete the prerequisites, including "Enable PrivateLink Service" and "Create Load Balancer Instance".

2\. In the Alibaba Cloud console, click PrivateLink - Endpoint Services in the left navigation bar, and select the same region as the current Lakehouse service instance to create the endpoint service. You can find the region and availability zone of the current service instance at the top of the "Create Endpoint Service" popup in the Lakehouse service. Please create the endpoint service according to the region and availability zone of the current service instance, otherwise, Lakehouse will not be able to create the corresponding endpoint and establish PrivateLink.

:-: ![](.topwrite/assets/image_1733063729452.png =381)

3\. Configure other options for creating the endpoint service according to the actual situation of your service on Alibaba Cloud. Please note, select "Service Provider" for the "Service Payer" option, otherwise, it will affect the normal creation of the connection.

:-: ![](.topwrite/assets/image_1733063748752.png =791)

4\. After the endpoint service is created, click the name of the endpoint to enter the endpoint service details page, and add the Singdata cloud account ID to the whitelist.

:-: ![](.topwrite/assets/image_1733063764046.png =757)

^

:-: ![](.topwrite/assets/image_1733063781421.png =367)

5\. After completing the above operations, return to the Lakehouse page. In the "Create Endpoint Service" popup, fill in the endpoint service instance ID (found on the Alibaba Cloud endpoint service details page) and name created in the above steps, and click "OK".

:-: ![](.topwrite/assets/image_1733063795296.png =557)