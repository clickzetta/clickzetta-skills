# AMQP Data Source Configuration Guide

## Overview

The AMQP data source is suited for connecting to AMQP-protocol message systems and is used for message consumption, event collection, and real-time data sync scenarios. After configuration in Lakehouse Studio, you can select this data source directly in supported sync tasks.

## Scope

The AMQP data source can currently be used as a source data source for single-table offline sync tasks. For task support scope, see [Data Source Support Scope](data-sources.md).

## Parameter Configuration

When creating an AMQP data source, the page requires the following information:

* **Data source name**: Used to identify this data source within the Workspace. Use a name that reflects the business source or purpose.
* **Host**: The AMQP service address. Enter the connection address provided by the message service and add the port as required.
* **Authentication method**: Select the authentication method required by your message service. The page shows the corresponding authentication parameters based on your selection.
* **IOT INSTANCE ID**: When the message service being connected requires an instance-level identifier, enter the corresponding instance ID.
* **Data source description (optional)**: Add the purpose, environment, or owning system of the data source for easier future maintenance.
* **Available Workspaces**: Specify which Workspaces this data source is authorized for. You can target specific Workspaces or authorize all Workspaces.

## Configuration Recommendations

* **Include the environment in the name**: Include production, test, or other environment information in the data source name to reduce misuse.
* **Confirm the connection address first**: The connection address, port, and authentication method can vary across AMQP services. Confirm with the message service administrator before configuring.
* **Authorize Workspaces as needed**: If this message data serves only specific projects, authorize only the corresponding Workspaces.

## Testing Connectivity

After filling in the parameters, click **Test Connection** at the bottom of the page to verify the configuration.

If the test fails, check the following in order:

* Whether the Host is correct and whether the port is open
* Whether the authentication method matches the source service configuration
* Whether the IOT INSTANCE ID is set to the correct instance
* Whether network allowlists, firewalls, or dedicated-line network policies allow the current environment to access the message service

## Usage Notes

After saving the data source, you can select this AMQP data source in supported sync tasks. For task support scope and source/target combinations, follow what is available in the specific task page.

## Related Documents

- [Data Source Support Scope](data-sources.md)
- [Data Source Management](config-datasource.md)
- [Data Integration](data-integration.md)
