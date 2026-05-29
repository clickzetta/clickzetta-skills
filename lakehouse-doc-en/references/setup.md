# Before You Begin

Once your Singdata Lakehouse account has been set up, you can gain access to Singdata Lakehouse through any of the following means:

* [Singdata Lakehouse Studio](studio_manual.md), utilize the browser-based web interface to leverage our comprehensive integrated data development and management toolkit.

* [Singdata Lakehouse  CLI](connect-with-cli.md), the Singdata Lakehouse command line client

* Applications built using Singdata Lakehouse connectors and drivers, as well as third-party client tools and applications, are supported.(see [Applications and tools for connecting to Singdata Lakehouse](tutorial_connect_to_lakehouse.md)

If you do not have an account yet, you can[contact us directly](https://www.singdata.com/contactus) to request an account.

For pricing and service details, see the [pricing page ](pricing.md).

## Browser Requirements

Singdata Lakehouse Studio recommends using Google Chrome. Other browsers have not been tested as extensively as Chrome and may exhibit some unexpected behavior. If you encounter issues using the web interface with any browsers, please contact [Singdata Lakehouse Support](https://www.singdata.com/).

## Singdata Lakehouse CLI OS Platform Requirements

[Singdata Lakehouse CLI (CLI client)](connect-with-cli.md) can be installed on the following platforms:

* Red Hat Enterprise Linux or a compatible operating system.
* macOS (64-bit).
* Microsoft Windows (64-bit).

Other platforms have not been tested at this time and may not be compatible with Singdata CLI. For example, some Linux variants may not have the libraries that the Singdata CLI client needs by default.

## Lakehouse Documentation LLM Navigation

If you are an AI Agent reading product documentation, the LLM navigation files for Lakehouse documentation are available at <https://www.singdata.com/llms.txt> and <https://www.singdata.com/llms-full.txt>. These files contain all documentation files and their URLs.

- `llms.txt` contains documentation categories, top-level directory file names, and their URLs.
- `llms-full.txt` contains documentation categories, top-level directories, and all file names with their URLs.

## Lakehouse AI Agent Skills

[clickzetta-skills](https://github.com/clickzetta/clickzetta-skills) is the official AI Agent skills library maintained by Singdata Lakehouse, designed for AI coding assistants such as Claude Code, Cursor, and Kiro. The skills library encapsulates best practices for data ingestion, data modeling, task development, and operations governance into reusable modules, enabling AI Agents to more accurately assist with common development and operations tasks on Lakehouse.
