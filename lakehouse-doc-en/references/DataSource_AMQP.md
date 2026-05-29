# AMQP Data Source Configuration Guide

## Overview

AMQP (Advanced Message Queuing Protocol) is an asynchronous messaging protocol widely used in IoT, microservice architecture, and enterprise system integration due to its high reliability and flexibility. By configuring an AMQP data source, you can achieve efficient data exchange with systems such as Alibaba Cloud IoT Platform.

## Parameter Configuration

When configuring an AMQP data source, you need to provide the following information to ensure a successful connection to the AMQP service:

* Data Source Name: Specify a unique and easily recognizable name for your AMQP data source.
* Host: The access domain name of the AMQP service, usually in the format `${uid}.iot-amqp.${YourRegionId}.aliyuncs.com`. For details, please refer to [Alibaba Cloud Manage Instance Endpoint](https://help.aliyun.com/zh/iot/user-guide/manage-the-endpoint-of-an-instance#task-1545804)
* Authentication Method: Currently supports authentication via RAM account and role-based authentication based on RAM account. Please choose the appropriate authentication method.
* IOT INSTANCE ID: The ID of the IoT instance. You can view the current instance ID on the instance overview page of the [Alibaba Cloud IoT Platform Console](https://iot.console.aliyun.com/).
* Data Source Description: (Optional) Add descriptive information to the data source to help you or other administrators understand the purpose or characteristics of the data source.

## Authentication Method Configuration

Choose the authentication method that suits you and configure the following parameters according to the actual situation:

* Connect via RAM Account: This mode directly uses the RAM account for connection and requires the following parameters:
  * AccessKey ID: The AccessKey ID and AccessKey Secret of the Alibaba Cloud main account or the corresponding RAM user. Log in to the Alibaba Cloud IoT Platform Console, move the mouse over the account avatar, and then click AccessKey Management to obtain the AccessKey ID and AccessKey Secret.
  * AccessKey Secret: The AccessKey ID and AccessKey Secret of the Alibaba Cloud main account or the corresponding RAM user. Log in to the Alibaba Cloud IoT Platform Console, move the mouse over the account avatar, and then click AccessKey Management to obtain the AccessKey ID and AccessKey Secret.
* RAM User Authorized by RAM Role: This mode is used to authorize another RAM account to access the data source through a RAM role and requires the following parameters:
  * STS Endpoint: The access point for the STS Token acquisition service. For specific information, please refer to [Alibaba Cloud Service Endpoint](https://www.alibabacloud.com/help/zh/ram/developer-reference/api-sts-2015-04-01-endpoint)
  * STS AccessKey ID: The AccessKey ID and AccessKey Secret of the RAM user who assumes the RAM role under the Alibaba Cloud account of the data-holding enterprise.
  * STS Role ARN: The ARN of the RAM role to be assumed under the Alibaba Cloud account of the data-holding enterprise, in the format `acs:ram::<account-id>:role/<role-name>`

## Notes

* Ensure the security and stability of the AMQP server, and configure authentication and authorization mechanisms reasonably.
* Protect your credential information to avoid leakage to unauthorized personnel.
* When configuring, please refer to the relevant documentation and support resources of the AMQP server to ensure correctness.
* After configuration, you can use the "Test Connectivity" function to verify the accessibility of the data source and the correctness of the configuration information.
* After verification, you can select this AMQP data source in the data synchronization task to perform data reading and exporting.

Please ensure that you have read and followed the above guidelines to successfully complete the configuration of the AMQP data source. If you need further assistance, please refer to the relevant documentation or contact technical support.