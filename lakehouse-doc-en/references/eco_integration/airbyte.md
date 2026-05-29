# Airbyte Clickzetta Destination Plugin User Guide

## Introduction

Airbyte is an open-source data synchronization tool that efficiently connects various data sources with data warehouses. With Airbyte, users can easily perform data extraction, transformation, and loading (ETL) to meet data integration needs.

This document aims to help users understand how to configure and use the Clickzetta Lakehouse destination plugin in Airbyte to achieve efficient data synchronization. Before reading this document, you may need to have a basic understanding of Airbyte. If you are not familiar with Airbyte, it is recommended to refer to its [official documentation](https://docs.airbyte.com/category/getting-started).

## Plugin Features

The Clickzetta Lakehouse destination plugin supports the following synchronization modes:

1. Full Refresh Sync
2. Incremental - Append Sync
3. Incremental - Append + Deduped Sync

## Plugin Installation

Airbyte supports multiple deployment methods, including standalone and Kubernetes (k8s) clusters. After deploying Airbyte, follow these steps:

1. Log in to the Airbyte console.
2. Go to the Settings page and select Destinations.
3. Click the New connector button to enter the new destination connector interface.
4. Fill in the relevant information:
   - Connector display name: Set an easily recognizable name for your connector, such as "Clickzetta Lakehouse".
   - Docker repository name: Enter "clickzetta/clickzetta-airbyte".
   - Docker image tag: Query and enter the latest image version number from [Docker Hub](https://hub.docker.com/r/clickzetta/clickzetta-airbyte/tags).
   - Connector documentation URL: You can fill in the link to this document here for easy reference.
5. Click the Add button, wait a moment, and the plugin will be configured.

## Plugin Configuration

To create Source, Destination, and Connection objects in Airbyte, refer to the [official documentation](https://docs.airbyte.com/quickstart/set-up-a-connection). The following are the configuration instructions for the Clickzetta Lakehouse destination connector:

1. In the Airbyte console, go to the Destination page.
2. Click the New destination button to create a new destination object.
3. Select the Clickzetta Lakehouse connector.
4. Fill in the configuration information:
   - Username: Your Clickzetta Lakehouse username.
   - Password: The corresponding user password.
   - Service: Service address, such as "api.clickzetta.com".
   - Instance: Instance name.
   - Workspace: Workspace name, such as "quickstart_ws".
   - VirtualCluster: Cluster name, such as "default". Airbyte will use the computing resources of this cluster to execute the ELT Transform SQL.
   - Schema (optional): Default is "public", can be modified if needed.
   - Normalization: Select "Normalized tabular data" to restore the data to the schema of the source table.
   - Split size: Set the slice size for Normalization SQL execution. It is recommended to keep the default value to avoid affecting performance.

## Usage Examples

Here are some typical use cases to help you better understand how to use the Clickzetta Lakehouse destination plugin:

### Example 1: Full Data Synchronization

1. Create a Source object to connect to your data source.
2. Create a Destination object and configure the Clickzetta Lakehouse connector.
3. Create a Connection object to associate the Source and Destination.
4. In the Connection configuration, select the Full Refresh Sync synchronization mode.
5. Start the Connection, and Airbyte will fully synchronize the data to Clickzetta Lakehouse.

### Example 2: Incremental Synchronization with Deduplication
1. Follow the steps in Example 1 to configure the Source, Destination, and Connection objects.
2. In the Connection configuration, select the Incremental - Append + Deduped sync mode.
3. Set the Incremental trigger conditions, such as based on timestamps or record IDs.
4. Start the Connection, and Airbyte will incrementally sync the data and automatically deduplicate it.

## Summary

This article provides a detailed introduction on how to configure and use the Clickzetta Lakehouse destination plugin in Airbyte. By following the above steps and examples, you can easily achieve efficient data synchronization.

## References

- [Airbyte Official Documentation](https://docs.airbyte.com/category/getting-started)
- [Airbyte ELT Implementation and Analysis of Various Sync Modes](https://airbyte.com/tutorials/incremental-data-synchronization)