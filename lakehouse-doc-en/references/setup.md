# Before You Begin

After your Singdata Lakehouse account is set up, you can access Lakehouse in any of the following ways:

* [Lakehouse Studio](studio_manual.md): Use the browser-based web interface for data development, management, scheduling, and operations.
* [Data Engineering Agent](dataagent.md): Use the AI agent built on Lakehouse and Studio to assist with data development, operations monitoring, and governance tasks through natural language.
* [CZ-CLI](cz-cli.md): Use the command-line operations tool for SQL execution, Schema management, Studio task development, and task run inspection. CZ-CLI supports direct terminal operations and can also be invoked by AI agents.
* [Data Analytics Agent](datagpt_introduction.md): Use the analytics assistant built on Lakehouse to create AI dashboards, query data in natural language, and add AI-generated insights to key metrics.
* Applications: Use applications built with Singdata Lakehouse connectors and drivers, as well as third-party client tools and applications. See [Applications and tools for connecting to Singdata Lakehouse](tutorial_connect_to_lakehouse.md).

If you do not have an account yet, [register](logging-in.md) to create one.

For pricing and service details, see the [pricing page](pricing.md).

## Browser Requirements

We recommend using Google Chrome for Singdata Lakehouse Studio. Other browsers have not been tested as extensively as Chrome and may behave differently. If you encounter issues with the web interface in any browser, contact [Singdata Lakehouse Support](https://www.singdata.com/).

## CZ-CLI OS Platform Requirements

[CZ-CLI](cz-cli.md) can be installed on the following platforms:

* Red Hat Enterprise Linux or a compatible operating system.
* macOS (64-bit).
* Microsoft Windows (64-bit).

## Lakehouse Documentation LLM Navigation

For AI agents reading the product documentation, Lakehouse provides LLM navigation files at <https://www.singdata.com/llms.txt> and <https://www.singdata.com/llms-full.txt>. These files list the documentation files and their URLs.

* `llms.txt` contains documentation categories, top-level file names, and their URLs.
* `llms-full.txt` contains documentation categories, top-level directories, and all file names with their URLs.

## Lakehouse AI Agent Skills

[clickzetta-skills](https://github.com/clickzetta/clickzetta-skills) is the official AI agent skills library maintained by Singdata Lakehouse for AI coding assistants such as Claude Code, Cursor, and Kiro. The library packages best practices for data ingestion, data modeling, task development, and operations governance into reusable modules, helping AI agents assist with common Lakehouse development and operations tasks.
