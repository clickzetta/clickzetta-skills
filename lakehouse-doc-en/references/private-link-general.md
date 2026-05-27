# Private Link Overview

## What is Private Link?

**Private Link** (AWS PrivateLink, Alibaba Cloud Private Link, Tencent Cloud Private Link, etc.) is a secure, private network connection method provided by cloud vendors. It allows different VPCs (Virtual Private Clouds) to interconnect through an internal network without being exposed to the public internet, significantly reducing the security risks of data transmission.

In the **Lakehouse** platform, the application scenarios of Private Link mainly fall into two categories:

**1. User VPC → Lakehouse (Inbound)**
Within the same region and availability zone of the cloud vendor, access Lakehouse (JDBC gateway, IGS, etc.) services from the user's VPC through the cloud vendor's Private Link service.

:-: ![](.topwrite/assets/Unnamed_Drawing.drawio.png)

For example:

A company has built its business systems (e-commerce platform, settlement system, etc.) on the cloud, and these systems are deployed in its private VPC, not allowing public internet access. This company stores sales transaction data and inventory data in Lakehouse. When creating data visualizations, real-time analysis, and reports, due to internal compliance and security requirements, it cannot access the data in Lakehouse through the public internet.

At this time, the Lakehouse Private Link feature is needed to establish an endpoint for the customer VPC to access Lakehouse. The company's access to Lakehouse is all within its private VPC, using the domain name of the endpoint.

^

**2. Lakehouse → User VPC (Outbound)**
When it is necessary to connect from Lakehouse (located in Singdata VPC) to user-defined services (such as a self-built MySQL database within the user VPC), Private Link is also used for private network access.

:-: ![](.topwrite/assets/private_link_access_customer.png)

For example:
A financial company chooses to use Lakehouse for unified data storage and analysis, but its core business database is stored within a private VPC and has strict security policies prohibiting the exposure of database ports to the public internet. Lakehouse needs to read data in real-time for subsequent analysis and risk control model training.

At this time, the customer first needs to establish an endpoint service within the private VPC, and then use the Lakehouse Private Link feature to establish an endpoint from Lakehouse to the customer VPC. After that, all operations to [create data sources](config-datasource.md) in Lakehouse use the domain name and port of this endpoint for configuration.

^

## Preparations and Considerations

1. **Network Interconnection and DNS Configuration**

   * If you need to access the Private Link Endpoint through a custom domain name (CNAME), you need to point the internal DNS resolution to the private IP within the VPC.

2. **Security Group and Port Allowance**

   * When using Lakehouse to access the customer VPC, the services within the customer's private VPC need to allow the relevant internal IP and port of the endpoint service's LB service.

3. **Default Bandwidth Limit**

   * The default bandwidth for the endpoint service provided by Lakehouse is **5 Mbps**;
   * If there is a need for large data transmission, please contact the Lakehouse support team to increase the bandwidth limit.

4. **Number of Endpoints and Account Control**

   * To prevent abuse or disorderly creation, each cloud vendor account ID can create a maximum of **5 endpoints**; when the limit is exceeded, the Lakehouse platform will issue an alert.

5. **Billing Method**

   * Private Link traffic fees are paid directly by the customer to the cloud vendor and are not measured by Lakehouse.

6. **Multi-Account Scenarios**

   * If the customer has multiple cloud vendor accounts, they need to add each account ID to the whitelist in Lakehouse;
   * Correspondingly create multiple Private Link Endpoints and manage them separately.

7. **Public Network Blocking (Optional)**

   * If you want to completely block user access to Lakehouse from the public internet after completing the private network connection, you can enable **network access policies** (or cloud vendor network policies) in Lakehouse to only allow connections from the VPC IP range.

^