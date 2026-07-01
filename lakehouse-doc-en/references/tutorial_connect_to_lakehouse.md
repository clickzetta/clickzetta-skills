# Tutorial: Connect to Lakehouse

Singdata Lakehouse supports multiple connection methods, from command-line tools to programming interfaces, meeting the access needs of different scenarios. Based on your role and technical preference, choose the most suitable connection method below.

---

## Connection Methods at a Glance

| Connection Method | Best For | Recommended Users |
|---------|---------|---------|
| **cz-cli Command-Line Tool** | Terminal SQL operations, task management, Agent integration | Data engineers, AI Agent developers |
| **JDBC Driver** | Java/Scala applications, direct BI tool connections | Application developers, BI engineers |
| **Command-Line Client (sqlline)** | Java-based interactive SQL terminal | Technical users familiar with traditional database terminals |
| **MySQL Protocol** | MySQL-compatible tools (Navicat, DataGrip, etc.) | Data analysts, DBAs |
| **SQLAlchemy** | Python data applications, Jupyter Notebooks | Python developers, data scientists |

---

## Choose by Role

### Data Engineer / Terminal User

Recommended: **cz-cli** — configure a Profile once, and all subsequent SQL and task operations automatically use the same connection parameters, no need to enter a JDBC URL each time.

→ [Connect with cz-cli Command-Line Tool](connect-with-cz-cli.md)

### Java/Scala Application Developer

Recommended: **JDBC Driver** — standard database connection interface that integrates directly into frameworks like Spring and Flink.

→ [JDBC Driver](jdbc-driver.md)

### Python Developer / Data Scientist

Recommended: **SQLAlchemy** — the standard database abstraction layer in the Python ecosystem, supporting both ORM and native SQL, suitable for Jupyter Notebook analysis scenarios.

→ [Connect with SQLAlchemy](sqlalchemy.md)

### BI Tool / Database Management Tool User

Lakehouse is compatible with the **MySQL protocol**. Tools like Navicat, DataGrip, and DBeaver can connect directly and operate Lakehouse just like MySQL.

→ [Connect with MySQL Protocol](use-mysql-client.md)

### Technical Users Familiar with Traditional Database Terminals

**sqlline** is a Java-based interactive SQL terminal. Enter SQL and get results back in real time — suitable for quick queries and data exploration.

→ [Connect with Command-Line Client](connect-with-cli.md)

---

## Client Downloads

For download links for all client drivers and toolkits, see [Downloads](Lakehouse-client-repository.md).

---

## Common Connection Parameters

Regardless of which connection method you use, the following core information is required:

| Parameter | Description | How to Obtain |
|------|------|---------|
| **Service Endpoint** | Service endpoint address | See [Cloud Region Endpoints](connect-with-cz-cli.md#cloud-region-endpoints) |
| **Instance ID** | Instance identifier | Upper-left corner of the Studio homepage |
| **Workspace** | Workspace name | Top dropdown in Studio |
| **Schema** | Default Schema | Run `SHOW SCHEMAS` after connecting |
| **VCluster** | Virtual Cluster name | Run `SHOW VCLUSTERS` after connecting |
| **Username / Password** | Authentication credentials | Platform registered account |
