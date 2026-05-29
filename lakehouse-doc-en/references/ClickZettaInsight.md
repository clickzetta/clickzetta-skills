## Visual Data Analysis Platform Insight

### 1. Singdata Insight Use Case Description

After using Singdata products for data integration and development, if you wish to further create data portal dashboards, you can use Singdata Insight product to create visual BI reports. With Insight, you can:

Create daily data reports

Replace the cumbersome work of traditional visual portal dashboard construction. With the help of BI tools, data developers only need to focus on underlying data development, and data analysts can build various business analysis reports based on datasets for business analysis and decision-making.

Self-service analysis

Through Singdata Insight, businesses can directly use the datasets created by data developers, and achieve self-service analysis through drag-and-drop, avoiding scenarios where data cannot be viewed due to scheduling, and improving data analysis efficiency.

### 2. User Operation Instructions

After opening a Singdata account, users can directly use several products provided by the Singdata platform, such as Lakehouse, DataGPT, Insight.

#### 2.1 Singdata User Management

Step one: Log in to the system management console with your Singdata account. (The creation process is not explained in the current operation process)

![](.topwrite/assets/image_1710730460476.png)

Step two: On the Singdata management console, click on Insight to enter the product.

![](.topwrite/assets/image_1710730582169.png)

#### 2.2 Singdata Insight Platform Operation

##### Step one: Create data connection

Enter the data connection page, click "New Data Link"

Select Spark SQL under SQL on Hadoop, and choose verify-1 for the JDBC version

Enter JDBC link information
![](.topwrite/assets/image_1710737452402.png)
![](.topwrite/assets/image_1710737482426.png)
![](.topwrite/assets/image_1710737494082.png)

##### Step two: Create dataset

Enter the data market page, create a "Blank Data Package"

Click "New Dataset" within the data package

Select data source type

Select data table
![](.topwrite/assets/image_1710737577638.png)
![](.topwrite/assets/image_1710737604349.png)
![](.topwrite/assets/image_1710737624527.png)
![](.topwrite/assets/image_1710737652216.png)

##### Step three: Create BI report

Enter the application creation page, create a "Analysis Application"

Click "New Dashboard" to enter the dashboard construction page

After successful creation, click "Publish" to publish the dashboard to the application market.

![](.topwrite/assets/image_1710737716505.png)
![](.topwrite/assets/image_1710737747103.png)
![](.topwrite/assets/image_1710737775085.png)

##### Step four: View report

Click on the application market page, click on the report to view the data
![](.topwrite/assets/image_1710737822262.png)

### QA

1. Why can't I see functions like data market, application market, etc.?
   Different user roles have different permissions, you can consult the system administrator to open the corresponding permissions.

2. Why can't I create a dataset even though I have data analysis permissions?
   Datasets need to be created under data packages, and only system administrators have the permission to create data packages.

3. How to add users for the Insight product?
   Users are managed uniformly on the Singdata management console, and there may be data synchronization delays.

^
