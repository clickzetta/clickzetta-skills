# Data Source Management

## Introduction

This document aims to guide users on how to configure and manage data sources to achieve efficient data synchronization tasks in the Lakehouse product. Through this document, you will learn how to add different types of data sources and connect to data sources within a VPC via SSH Tunnel.

## Steps

1. **Log in and Access the Data Source Management Page**

   First, log in to the Lakehouse product console. On the console homepage, select the "Management" module and click to enter the "Data Source" page. You will see a list of data sources showing all currently configured data sources.

   ![](.topwrite/assets/image_1740137071389.png =640)

2. **Create a New Data Source**

   On the data source list page, click the "New Data Source" button in the upper right corner. At this point, you need to select the data source type. Lakehouse supports multiple data source types, including but not limited to MySQL, Oracle, SQL Server, etc.

   ![](.topwrite/assets/image_1740137096346.png =640)


3. **Fill in the Data Source Definition and Test Connectivity**

   Based on the data source type you selected, fill in the corresponding connection information. For example, for a MySQL data source, you need to provide the database address, port, username, password, etc. After filling in, click the "Test Connection" button to ensure the information provided is correct.

   ![](.topwrite/assets/image_1740137122891.png =640)

## Connect to Data Sources within a VPC via SSH Tunnel

### Prerequisites

1. **VPC Data Source Access Restrictions**

   Ensure that your VPC data source (such as Alibaba Cloud RDS for MySQL database) only provides internal network access. This means the data source is not publicly accessible, thereby enhancing data security.

2. **SSH Tunnel Server Preparation**

   Prepare an ECS server located within the VPC that has public network access capabilities and supports SSH login. Additionally, ensure that the data synchronization service can access this ECS server via the public network.

3. **VPC Network Access Configuration**

   Ensure that the ECS server within the VPC can access the data source within the VPC via internal network IP or domain name. This will facilitate the data synchronization service to connect to the data source smoothly when establishing the SSH Tunnel.

### Configure Data Source Connection Parameters

On the new data source page, enable the "Connect via SSH Tunnel" option. Fill in the following information as prompted:

* **SSH Tunnel Server Public Address**: Enter the public IP address or domain name of the ECS server within the VPC.
* **SSH Port**: Enter the port number of the SSH service on the ECS server (default is 22).
* **SSH Username**: Enter the username for SSH login.
* **SSH Password**: Enter the corresponding SSH login password.

  ![](.topwrite/assets/image_1740137146102.png =640)


After completing the above configuration, click the "Test Connection" button. If the connection is successful, you will see a green checkmark prompt. This means that the data synchronization service can establish a network connection with the data source within the VPC via SSH Tunnel when the task starts.

## Usage Examples

### Example 1: Connect to Alibaba Cloud RDS for MySQL Database

1. On the data source type selection page, select "MySQL" as the data source type.
2. On the data source definition page, fill in the following information:
   * Hostname: Enter the internal IP address of Alibaba Cloud RDS for MySQL.
   * Port: Enter the port number of the MySQL database (default is 3306).
   * Username: Enter the database access username.
   * Password: Enter the corresponding user password.
3. Enable the "Connect via SSH Tunnel" option and fill in the relevant information of the ECS server within the VPC.
4. Click "Test Connection". After confirming the connection is successful, click the "Save" button to complete the data source configuration.

### Example 2: Connect to Oracle Database

1. On the data source type selection page, select "Oracle" as the data source type.
2. On the data source definition page, fill in the following information:
   * Hostname: Enter the internal IP address of the Oracle database.
   * Port: Enter the port number of the Oracle database (default is 1521).
   * Username: Enter the database access username.
   * Password: Enter the corresponding user password.
3. Enable the "Connect via SSH Tunnel" option and fill in the relevant information of the ECS server within the VPC.
4. Click "Test Connection". After confirming the connection is successful, click the "Save" button to complete the data source configuration.

^