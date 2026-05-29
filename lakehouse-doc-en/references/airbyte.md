# Connecting Airbyte to Singdata Lakehouse

> 💡 **If your goal is to sync data into Singdata Lakehouse**, Singdata provides built-in data ingestion options that require no Airbyte deployment or maintenance. Choose the right option based on your data source:
>
> | Data Source | Recommended Option | Notes |
> |-------------|-------------------|-------|
> | MySQL / PostgreSQL / Oracle / SQL Server and other relational databases | [Studio Real-Time Sync Task](realtime_sync.md) | Visual CDC configuration, supports Insert / Update / Delete, no extra components needed |
> | Full database migration, syncing multiple tables at once | [Multi-Table Real-Time Sync](multitable_realtime_sync.md) | Sync an entire database in one task, auto table creation, supports schema mapping |
> | OSS / S3 / COS files with continuous writes | [Pipe](pipe-introduction.md) | Automatically monitors new files and writes to the target table, no polling scripts needed |
> | Kafka / AutoMQ message streams | [Kafka Pipe](pipe-introduction.md) or [Studio Kafka Sync Task](realtime_sync.md) | Native support, second-level latency, SQL-defined consumption logic |
> | Scheduled batch sync (offline) | [Studio Offline Sync Task](batch_sync.md) | Supports 40+ data sources, wizard-based configuration, supports scheduled execution |
> | Flink job writes | [Flink Connector](flink-write-connector.md) | Supports CDC mode and Append-only mode, suitable for existing Flink pipelines |
> | Custom program writes | [Streaming SDK / JDBC](data-integration.md) | Provides Java / Python SDK and standard JDBC interface |
>
> Not sure which to choose? See [Data Sync Overview](data-integration-intro.md) for a full comparison of all options.

---

## Connecting to Singdata Lakehouse via Airbyte

Airbyte is an open-source data integration platform designed for ELT (Extract, Load, Transform) pipelines from APIs, databases, and files to data warehouses and data lakes. If you are already using Airbyte, you can write data into Lakehouse through the official Singdata connector.

![Airbyte Architecture Diagram](.topwrite/assets/image_1705039346358.png)

## Local Docker Installation

## Airbyte Version

For version v0.50.41, follow the installation steps in this guide, which use the `run-ab-platform` method.

For Airbyte 2.0 and later versions, which use the `abctl` installation method, refer to the [Airbyte installation documentation](https://docs.airbyte.com/platform/using-airbyte/getting-started/oss-quickstart) instead. The installation method provided in this guide does not apply to those versions.

## System Requirements

This guide has been tested on the following operating systems: macOS, Windows 10, and Ubuntu 22.04.

## Installation Steps

1. Ensure that Docker Engine is installed on your computer, along with the Docker Compose plugin. For specific installation methods, please refer to the [official documentation](https://docs.docker.com/engine/install/).
2. After installation, start Airbyte locally with the following command:
```bash
# Clone the Airbyte repository from GitHub
git clone --branch v0.50.41 --single-branch --depth=1 https://github.com/airbytehq/airbyte.git

# Switch to the Airbyte directory
cd airbyte

# Start Airbyte
./run-ab-platform.sh
```
3. Visit [http://localhost:8000](http://localhost:8000/) to open the Airbyte web interface in your browser.
4. The system will prompt you to enter a username and password. By default, the username is `airbyte` and the password is `password`. You can modify these credentials in the `.env` file:
```
# Proxy Configuration
# Set BASIC_AUTH_USERNAME and BASIC_AUTH_PASSWORD to empty values, such as "", to disable basic authentication
BASIC_AUTH_USERNAME=your_new_username_here
BASIC_AUTH_PASSWORD=your_new_password_here
```

## Deploy on Windows

After installing the WSL 2 backend and Docker, you can run containers using Windows PowerShell. Additionally, we recommend building Airbyte from source on Windows to install `docker-compose`. Below is the recommended guide for installing Airbyte on Windows.

## Setup Guide

1. Please review the system requirements in the [Docker documentation](https://docs.docker.com/desktop/windows/install/).
2. Follow the steps for the system requirements and ensure to download and install the Linux kernel update package.
3. Install Docker Desktop on Windows. Download link: [Docker Desktop](https://docs.docker.com/desktop/windows/install/).
4. Make sure to select the following options during installation:
   * Enable Hyper-V Windows feature
   * Install the Windows components necessary for WSL 2 (a computer restart is required after installation)
```bash
git clone --depth=1 https://github.com/airbytehq/airbyte.git
cd airbyte
bash run-ab-platform.sh
```
5. Access [http://localhost:8000](http://localhost:8000/) in your browser.
6. The system will prompt you to enter a username and password. By default, the username is `airbyte` and the password is `password`. Please change these credentials after deploying Airbyte to the server.

## Install Singdata Lakehouse Destination Connector in Airbyte

## Configuration Reference

Connector display name: Clickzetta Lakehouse

Docker repository name: clickzetta/clickzetta-airbyte

Docker image tag: 0.1.0

Connector documentation URL Optional: <https://www.yunqi.tech>

1. Create a new connector in Airbyte, and select "Clickzetta Lakehouse" as the display name.
   ![New Connector](.topwrite/assets/20240112141059_rec_.gif)
2. Configure the connector by filling in the necessary parameters, such as database address, port, username, and password.
3. Create a data sync connection from other data sources to Singdata Lakehouse and start data synchronization.
   ![Create Data Sync Connection](.topwrite/assets/20240112141631_rec_.gif)

## Establish Connection and Sync Data to Singdata Lakehouse

1. Create a new connection and select the "Clickzetta Lakehouse" connector that was just created.
   ![](.topwrite/assets/20240112141631_rec_.gif)
2. Fill in the connection configuration information, such as database address, port, username, and password.
3. Configure the sync task by selecting the source data source and target data table, setting the sync frequency, and filtering conditions.
4. Start the sync task to begin synchronizing data from the source data source to Singdata Lakehouse.

![Data Sync Configuration](.topwrite/assets/image_1705040300515.png)
![Data Sync Configuration2](.topwrite/assets/image_1705040390515.png)
