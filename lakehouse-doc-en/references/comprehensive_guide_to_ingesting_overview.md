# A Comprehensive Guide to Importing Data into Singdata Lakehouse

## Overview

There are many ways to import data into Singdata Lakehouse. Different scenarios, requirements, team skills, and technology stack choices may lead to different data ingestion decisions. This quick start guide will walk you through examples of loading the same data using different methods:

### Data Warehousing

* Load local files through Singdata Lakehouse Studio
* Batch load through Singdata Lakehouse Studio (public network connection)
* Batch load through Singdata Lakehouse Studio (private network connection)
* Real-time multi-table load through Singdata Lakehouse Studio (CDC)
* Import data using Zettapark SQL
* Import data from Dataframe using Zettapark
* From Kafka – using Zettapipe
* From Kafka – external table method
* From Data Lake (object storage) - SQL Volume method
* From Data Lake (object storage) - SQL Copy Into method
* From External Catalog (Hive) - SQL method
* From Java SDK - using Singdata real-time write service

### Data Lake

* Using database client DBV/SQLWorkbench to PUT files
* Using ZettaPark to PUT files

By the end of this guide, you should be familiar with various methods of loading data and be able to choose the right approach based on your goals and requirements. After completing the initial project setup, each extraction method can be performed independently and does not depend on the others.

### Prerequisites

* Singdata Lakehouse account with the ability to create users, roles, workspaces, schemas, dynamic tables, virtual compute clusters, data synchronization, and scheduling tasks
* Familiarity with Python, Kafka, and/or Java
* Basic knowledge of Docker
* Ability to run Docker locally or access an environment to run Kafka and Kafka Connectors

### What You Will Learn

* How and when to use Singdata Lakehouse Studio for offline data synchronization
* How and when to use Singdata Lakehouse Studio for real-time multi-table data synchronization
* How to import data from a data lake
* How and when to import data from files
* How to load data from Kafka
* How to load data from streams

### What You Need

* [Singdata Lakehouse](https://www.yunqi.tech/) account
* [Github repository](https://github.com/yunqiqiliang/clickzetta_quickstart/tree/main/a_comprehensive_guide_to_ingesting_data_into_clickzetta) for this guide

### Mac Requirements

* [Docker](https://docs.docker.com/desktop/install/mac-install/) installation
* [Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/macos.html) installation

### Linux Requirements

* [Docker](https://docs.docker.com/engine/install/ubuntu/) installation
* [Conda](https://docs.conda.io/projects/conda/en/stable/user-guide/install/linux.html) installation

### Windows Requirements

* [WSL with Ubuntu](https://learn.microsoft.com/en-us/windows/wsl/install) for Windows
* Install [Docker](https://docs.docker.com/engine/install/ubuntu/) in Ubuntu
* Install [Conda](https://docs.conda.io/projects/conda/en/stable/user-guide/install/linux.html) in Ubuntu

^