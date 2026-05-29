# Based on Octoparse and Singdata DataGPT, Achieve Simplified Web Data Acquisition and Conversational Data Analysis

:-: ![](.topwrite/assets/image_1734329097397.png =447)

## From Simple to Simpler

The importance of data is self-evident. It is not only the foundation of enterprise decision-making but also the driving force for innovation and development. However, traditional data collection and analysis methods are often complex and time-consuming, often requiring users to have coding (SQL/Python) skills, which limits the rapid application and maximization of data value. Therefore, we propose a solution concept—"from simple to simpler." Whether it is data acquisition or data analysis, we adopt a no-code approach, aiming to simplify the data collection and analysis process, allowing more people to quickly and intuitively obtain the information they need, thereby improving data processing efficiency and gaining deep insights through data. Every report is unique because of your unique data content! Every PPT page impresses because of your deep insights!

## Solution Components

:-: ![](.topwrite/assets/image_1734329112134.png =485)

Among them, Octoparse is a powerful and easy-to-use data collection tool that allows users to collect website data without writing code. No need to learn complex programming techniques, easy to get started, and you can get web data in just three simple steps.

Singdata DataGPT is an innovative conversational AI data analysis tool that leads the transition from traditional dashboards and complex reports to conversational analysis. Similarly, no coding skills are required, no installation or deployment is needed, ready to use, and you can visualize and analyze the acquired data through popular natural language Q&A in just three simple steps.

Singdata Lakehouse is the underlying data storage and processing platform for Singdata DataGPT. For Singdata DataGPT users, there is no need to focus on the underlying complexity, and they can enjoy the convenience of unlimited storage and fast data processing.

## Solution Guide

### Method 1: Use Excel files as the data exchange format, suitable for users without a database background. The specific implementation steps are as follows:

:-: ![](.topwrite/assets/image_1734329129548.png =514)

#### Octoparse:

#####   01. Create Task    Configure page data capture method by clicking the mouse.

:-: ![](.topwrite/assets/image_1734329148588.png =700)

#####   02. Start Collection    

Start the collection, wait for the collection to complete, and check whether the collected data meets expectations. Pay attention to the differences between local collection and cloud collection in exporting data. Since Method 2 supports exporting to MySQL, while local collection does not, the cloud collection method was chosen.

:-: ![](.topwrite/assets/image_1734329171687.png =700)

Check whether the collected data meets expectations:    
First, a comprehensive review and analysis of the collected data are required. This includes the accuracy, completeness, and consistency of the data. Accuracy refers to whether the data accurately reflects the actual situation; completeness refers to whether the data covers all expected information; consistency refers to whether the data remains consistent across different sources or time points.    
Next, compare the collected data with the expected standards and specifications. For example, whether the data format meets the requirements, whether the data value range is within a reasonable range, and whether the logical relationship of the data is correct.   
 Then, check the reasonableness of the data. By observing the data, determine whether there are any anomalies or unreasonable fluctuations.

:-: ![](.topwrite/assets/image_1734329188223.png =700)

#####   03. Data Export    

Export the data as an Excel file. The data collected by Octoparse supports automatic export to local files, including Excel, CSV, html, json, Xml formats. Note that this feature is only supported in the team and enterprise versions. To automatically export to local files, please upgrade your account to the corresponding package version.

:-: ![](.topwrite/assets/image_1734329204072.png =700)

#### Singdata DataGPT:

#####   04. Import Data    

Import the data from the downloaded Excel file

:-: ![](.topwrite/assets/image_1734329222963.png =700)

:-: ![](.topwrite/assets/image_1734329229933.png =700)

#####   05. Data Annotation    

Add necessary descriptions and aliases to the fields to facilitate the large model's understanding of the data and improve the consistency between natural language and data definitions during the Q&A process. Singdata DataGPT will automatically generate field descriptions and aliases based on the provided information, requiring only user selection and confirmation, greatly reducing the workload of data annotation.

:-: ![](.topwrite/assets/image_1734329251329.png =700)

#####   06. Data Analysis    Conduct data analysis through natural language Q&A.   

 **Ask: The number of majors in different categories**?

:-: ![](.topwrite/assets/image_1734329262043.png =700)
**Ask: What majors are set up in management?**

:-: ![](.topwrite/assets/image_1734329282295.png =700)

**Ask: The top 10 most popular major categories, excluding those with type 0**

:-: ![](.topwrite/assets/image_1734329294818.png =700)

**Ask: The average salary after graduation for different major categories**

:-: ![](.topwrite/assets/image_1734329304049.png =700)

**Ask: Which majors offer sketching courses?**

:-: ![](.topwrite/assets/image_1734329315980.png =700)

It looks like there are many interesting questions in the newly downloaded data waiting for you to explore!

### Method 2: Use the MySQL protocol to directly synchronize data from Octoparse to Singdata Lakehouse, suitable for users without a database background. The specific implementation steps are as follows:

:-: ![](.topwrite/assets/image_1734329328797.png =700)

Octoparse:

  01. Create a task: Configure the data capture method on the page by clicking the mouse

  02. Start collection: Wait for the collection to complete and check if the collected data meets expectations

  03. Data export: Configure the MySQL connection to Singdata Lakehouse

  Singdata DataGPT:

  04. Import data: Create a Lakehouse target table and add it to DataGPT

  05. Data annotation: Add necessary descriptions and aliases to the fields to facilitate the large model's understanding of the data

  06. Data analysis: Perform data analysis through natural language Q&A

The difference from Method 1 is the configuration of the MySQL database, introduced as follows:

The data collected by Octoparse supports export to a MySQL database. It can be exported manually or automatically according to the set scheduled export plan.

Singdata Lakehouse supports MySQL access, allowing data to be directly imported into Singdata Lakehouse via the MySQL protocol. This eliminates the need for Singdata Lakehouse's own JDBC driver and directly adapts to the existing MySQL JDBC driver, greatly improving convenience.

Select "Export to Database" as the data export method and choose MySQL (Singdata Lakehouse supports the MySQL protocol):

:-: ![](.topwrite/assets/image_1734329339603.png =700)

Configure the database information:

:-: ![](.topwrite/assets/image_1734329350652.png =700)

[For the configuration of connecting to Singdata Lakehouse via MySQL, please refer to](https://www.singdata.com/documents/use-mysql-client):

<https://www.singdata.com/documents/use-mysql-client>

## Summary

This article introduces a solution based on Octoparse and Singdata DataGPT, aiming to simplify the process of web data acquisition and conversational data analysis, improving efficiency and response speed. The solution includes three parts: Octoparse collector, Singdata DataGPT, and Singdata Lakehouse, used for data collection, analysis, and storage processing, respectively. The solution provides two methods: one uses Excel files as the data exchange format, suitable for users without a database background; the other uses the MySQL protocol to directly synchronize data from Octoparse to Singdata Lakehouse, suitable for users with a database background.

In daily work, study, and research, there is an increasing need to speak through data. Whether it is enterprise decision-making, in-depth academic research, or personal learning data analysis, data plays a crucial role.

In work, accurate market research data can help enterprises accurately grasp market demand, optimize product strategies, and thus remain invincible in fierce competition; detailed sales data analysis can reveal potential customer needs and consumption trends, providing strong support for business expansion.

In learning, through the analysis of students' academic performance and behavior data, teachers can teach according to their aptitude, formulate more targeted teaching plans, and improve teaching effectiveness; students can also use their learning data to understand their strengths and weaknesses, adjust learning strategies in time, and improve learning efficiency.

In the field of scientific research, a large amount of experimental data and observation results are important bases for drawing scientific conclusions and promoting the development of disciplines. Researchers need to organize, analyze, and interpret massive amounts of data to discover patterns and explore the unknown.

Therefore, start your data journey now! Let data become a powerful assistant for your operation, management, and decision-making, bringing new breakthroughs and development to your work, study, and research.

All of this is made simple by the perfect integration of Octoparse and Singdata DataGPT, keeping your practice simple from start to finish, from data acquisition to data analysis. Come and experience the journey from simplicity to simplicity!

^

Here is also the [download link for Octoparse](https://www.bazhuayu.com/) for your convenience: <https://www.bazhuayu.com/>
and [Singdata Lakehouse and DataGPT activation address](https://accounts.singdata.com/register): <https://accounts.singdata.com/register> and [Quick Start](datagpt_quickstart.md)

 

Data expert, you are the one!