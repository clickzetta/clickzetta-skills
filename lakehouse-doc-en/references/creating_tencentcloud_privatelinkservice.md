# Tencent Cloud

When you need to use Singdata Lakehouse to access services within your cloud vendor's VPC (such as a self-built MySQL database), you first need to create an endpoint service on Tencent Cloud and configure the service to be accessed as a service resource for that endpoint service.



## Steps

1\. On the Tencent Cloud Network Connection - Endpoint Service page, select the same region as the current Lakehouse service instance to create an endpoint service. You can find the region and availability zone of the current service instance at the top of the "Create Endpoint Service" popup in the Lakehouse service. Please create the endpoint service according to the region and availability zone of the current service instance, otherwise, Lakehouse will not be able to create the corresponding endpoint and establish PrivateLink.


2\. After completing the creation of the endpoint service, click on the endpoint service name to enter the details page. Switch to the "Whitelist" tab, click the "Add" button, and add the UIN of the Lakehouse service. You can copy the "Lakehouse UID" from the information popup of the newly created endpoint service in the Lakehouse service and fill it in.


3\. After completion, please copy your endpoint service ID and paste it into the Lakehouse creation page, then click "Confirm" to complete the creation of the endpoint service.
