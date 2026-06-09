# Before You Begin

Once your Singdata Lakehouse account has been set up, you can access Singdata Lakehouse through any of the following means:

* [Lakehouse Studio](studio_manual.md): Use the browser-based web interface with our comprehensive integrated data development and management toolkit.
* [Data Agent](dataagent.md): A fully AI-interactive product built on top of Lakehouse + Studio, covering the full "development-operations-governance" lifecycle. It implements intelligent data platform upgrades with an Agentic AIOps philosophy, transforming data development from "people operating the platform" to "people directing Agents."
* [CZ-CLI](cz-cli.md): An operations tool for command-line and AI Agents, encapsulating capabilities for SQL execution, Schema management, Studio task development, and task run inspection. It supports direct terminal operations and also allows AI Agents to assist with data warehouse development and operations via natural language.
* [Data Analytics Agent](datagpt_intro.md): An intelligent analysis assistant built on Lakehouse that creates dynamic AI dashboards through natural language, embeds AI insights into key metrics, and goes beyond the static reporting capabilities of traditional BI tools.
* Applications built using Singdata Lakehouse connectors and drivers, as well as third-party client tools and applications, are supported. (See [Applications and tools for connecting to Singdata Lakehouse](tutorial_connect_to_lakehouse.md))

If you do not have an account yet, you can [register](logging-in.md) to get an account.

For pricing and service details, see the [pricing page](pricing.md).

## Browser Requirements

Singdata Lakehouse Studio recommends using Google Chrome. Other browsers have not been tested as extensively as Chrome and may exhibit some unexpected behavior. If you encounter issues using the web interface with any browsers, please contact [Singdata Lakehouse Support](https://www.singdata.com/).

## CZ-CLI OS Platform Requirements

[CZ-CLI](cz-cli.md) can be installed on the following platforms:

* Red Hat Enterprise Linux or a compatible operating system.
* macOS (64-bit).
* Microsoft Windows (64-bit).

## Lakehouse Documentation LLM Navigation

If you are an AI Agent reading product documentation, the LLM navigation files for Lakehouse documentation are available at <https://www.singdata.com/llms.txt> and <https://www.singdata.com/llms-full.txt>. These files contain all documentation files and their URLs.

* `llms.txt` contains documentation categories, top-level directory file names, and their URLs.
* `llms-full.txt` contains documentation categories, top-level directories, and all file names with their URLs.

## Lakehouse AI Agent Skills

[clickzetta-skills](https://github.com/clickzetta/clickzetta-skills) is the official AI Agent skills library maintained by Singdata Lakehouse, designed for AI coding assistants such as Claude Code, Cursor, and Kiro. The skills library encapsulates best practices for data ingestion, data modeling, task development, and operations governance into reusable modules, enabling AI Agents to more accurately assist with common development and operations tasks on Lakehouse.
