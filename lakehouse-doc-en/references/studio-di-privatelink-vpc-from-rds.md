# Syncing RDS Data Within VPC via Private Link Combined with SSH

## 1. Applicable Scenarios

Lakehouse Studio **Data Integration** syncs RDS data through VPC networks, solving the following problems associated with public network transmission:

* High data latency
* High public network traffic costs
* Insecure/non-compliant

## 2. Summary of Previous Solutions' Pros and Cons

* **Pure Private Link Solution**: Does not support connecting to RDS instances; only supports self-managed MySQL on ECS.
* **VPC Peering Verification Passed**: However, it exposes both sides' internal network environments, posing security risks and is not recommended.
* **Via IGS SDK**: Supports pushing data to Lakehouse through Private Link, but import scheduling strategies need to be managed by the customer themselves and cannot be integrated into workflows.
* **Pure SSH TUNNEL**: The intermediate segment requires going through the public network, which can solve the security issue of exposing RDS to the public network, but cannot solve the public network traffic issue.

## 3. Introduction to This Solution

This solution combines Private Link with SSH Tunnel.

Network architecture diagram (using Alibaba Cloud as an example): The customer VPC (containing RDS and an ECS bastion host) connects to the Lakehouse VPC through a Private Link endpoint service. The ECS bastion forwards traffic via SSH tunnel to the RDS instance on port 3306, while the Private Link endpoint exposes this path securely to the Lakehouse data integration cluster without traversing the public internet.

(The customer environment may also be in other availability zones within the same Region)

By default, the **endpoint** side bears the costs. There are two billing items; for details, refer to [Billing Rules](https://help.aliyun.com/document_detail/198081.html?spm=a2c4g.120462.0.0.462f29e3tnGfMO#section-4zx-gat-sg7).

## 4. Configuration Method (Example):

### Step 1: Environment Preparation

**Customer-Side Environment**:

* VPC: Hangzhou H: Virtual Private Cloud **VPC_Customer**: [vpc-bp1qmyayneio4mlyoyeb7](https://vpc.console.aliyun.com/vpc/cn-hangzhou/vpcs/vpc-bp1qmyayneio4mlyoyeb7?type=base), CIDR: `172.16.0.0/12`
* RDS: Hangzhou H: Private network address: `` (`rm-bp15gq963ic327h8f.mysql.rds.aliyuncs.com`)
* ECS: Hangzhou H: Private network IP address `172.16.12.182`

**Lakehouse Side**:

Singdata Studio UAT environment data integration EMR cluster VPC and vSwitch: Hangzhou H

| SQL vpc-bp1jvn\*\*\*\*\*\*\*\*\*\*\*u  vsw-bp1rp\*\*\*\*\*\*\*\*\*\*\*\*cii |
| --------------------------------------------------------------------------- |

Singdata UAT environment Alibaba Cloud primary account: `138************83`

### Step 2: Create SSH Port Forwarding on ECS

In the customer network environment, create an ECS instance that can communicate with RDS. On this machine, create port forwarding: access to port 12345 on this ECS will be forwarded to port 3306 on RDS.

```Shell
ssh -CfNg -L 12345:rm-bp15gq963ic327h8f.mysql.rds.aliyuncs.com:3306 root@127.0.0.1 -p22

## Verify:
ps aux | grep ssh
```

After running the command, verify with `ps aux | grep ssh` that the SSH process is running and listening on port 12345.

---

### Step 3: Create Load Balancer CLB

* Enter SLB console -> Left sidebar **Classic Load Balancer (CLB, formerly SLB)** -> **Create Classic Load Balancer**

* Create listener as follows: set the listener protocol to TCP, the frontend port to 22, and the backend port to 12345 (the port forwarded to RDS on the ECS).

* In the **Default Server Group** tab, add the ECS from Step 2, with frontend port 22 (custom) and backend port as the port forwarded to RDS, which is 12345 in this case.

### Step 4: Customer Side: Create Endpoint Service

* Enter VPC console, select the same Region as the Singdata data integration cluster, left sidebar **Endpoint Service** -> **Create Endpoint Service**
* **Service Resource Type -> Classic Load Balancer CLB** (consistent with Step 1), select Availability Zone **Hangzhou Zone H**, choose the CLB instance created in Step 1 from the dropdown, auto-accept endpoint connections: Yes, other settings default
* Enter this endpoint service: In **Service Whitelist**, add the Singdata environment primary account: `1384322691904283`. The whitelist entry should show the account ID listed and the auto-accept setting enabled.

### Step 5: Lakehouse Side Create Endpoint

* Enter VPC console, select the same Region as the Singdata data integration cluster, select **Endpoint** in the left menu.
* On the Endpoint page, the system will automatically discover the endpoint service created in Step 4. After selecting the corresponding **VPC**, confirm creation;
* In the **Endpoint Service** and **Endpoint** connection information on both the customer side and Lakehouse side, you can obtain the domain name.

### **Verification**:

**Lakehouse Studio Data Integration**:

In the data source configuration, use the following JDBC URL: `jdbc:mysql://ep-bp1iabb21a27719ca8a2-cn-hangzhou-h.epsrv-bp1n7rvc8qbpudxk69fr.cn-hangzhou.privatelink.aliyuncs.com:22/mysql`

The connection test returns a successful status, confirming the data integration layer can reach the RDS database through the Private Link endpoint.

The CLB listener port bound to the endpoint service is 22, and the backend ECS resource port is 12345.

The MySQL console confirms the connection is active, showing the database and schema are accessible.

Data Integration verification: Import successful
