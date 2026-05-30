---
name: clickzetta-dbt-project-setup
description: |
  dbt-clickzetta project initialization wizard. Helps users build a dbt project from scratch
  connected to ClickZetta Lakehouse, covering installation verification, profiles.yml configuration,
  layering standards, and dbt_project.yml generation.
  Naturally hands off to clickzetta-dbt-modeling for modeling after completion.

  Trigger this skill whenever the user wants to build a data warehouse or start a dbt project
  in this ClickZetta environment — even if they don't mention ClickZetta or "initialization".
  Typical scenarios:
  - Says "I want to build a data warehouse with dbt" or "build a data warehouse"
  - Asks "how do I get started with dbt" or "dbt beginner guide"
  - Has no dbt project yet and wants to do ELT or data modeling
  - Explicitly mentions project setup (dbt project init, dbt from scratch, how to connect dbt to ClickZetta,
    dbt project setup, dbt profiles configuration, how to configure dbt-clickzetta)
  - Has a ClickZetta account and wants to use dbt for ELT
  - Asks "how does dbt connect to ClickZetta" or "how do I write profiles.yml"
---

# clickzetta-dbt-project-setup

See [references/dbt-clickzetta-adapter.md](references/dbt-clickzetta-adapter.md) for adapter capabilities and connection parameters.
See [references/elt-standards.md](references/elt-standards.md) for layering standards and naming conventions.

---

## Goal

Help users establish a dbt-clickzetta project that runs immediately, with correct connection configuration and layering standards.
Users don't need to understand dbt internals — they only need to answer a few business questions.

## Workflow

**Explore first, then recommend — never make users fill in blanks. Interact early — don't silently run commands for a long time.**

0. **Installation check**: Verify dbt-clickzetta is installed; guide installation if not:
   ```bash
   pip show dbt-clickzetta   # check if installed
   pip install dbt-clickzetta  # install if missing; recommend using a venv
   ```
   Tell the user the result immediately ("dbt-clickzetta 1.7.x is installed ✓" or "Not installed — installing now...").

1. **Quick Lakehouse scan** (~2 seconds): Run `cz-cli schema list` to see if there's existing data. Immediately tell the user what was found (greenfield or existing data), then **ask the three setup questions before doing anything else** — do not silently explore further:

   Ask the user to confirm three things (present as choices, not blank fields):
   - **Project directory**: current directory, or a path they specify
   - **Layering mode**: two-layer (staging → marts, recommended for small/medium), two-layer + intermediate (for complex joins), three-layer (ODS → DWD → ADS), or four-layer (ODS → DWD → DWS → ADS)
   - **Naming prefix**: business domain name (e.g. retail, finance), company/team name, or custom

2. After user answers, generate the full scaffold.

   ```bash
   dbt init {project_name}          # generate project skeleton
   rm -rf models/example            # remove example files to avoid polluting dbt run results
   ```

   Generated directory structure:
   ```
   {project_name}/
   ├── dbt_project.yml              # configure layer schemas + global persist_docs
   ├── profiles.yml                 # connection config (not committed to git — contains passwords)
   ├── .gitignore                   # includes profiles.yml and target/
   └── models/
       ├── staging/                 # cleansing layer
       └── marts/                  # business layer (or adjusted per layering choice)
   ```

   Generate `dbt_project.yml` with **`dynamic_table` as the default materialization for all layers** — this is the ClickZetta Lakehouse native approach. The system handles incremental refresh and dependency propagation automatically; no manual merge logic or Studio dependency config needed.

   ```yaml
   models:
     {project_name}:
       +persist_docs:
         relation: true    # table comments
         columns: true     # column comments

       # Two-layer example (staging → marts):
       staging:
         +materialized: dynamic_table
         +dynamic_table:
           refresh_interval: "5 minutes"   # adjust to business SLA; DOWNSTREAM not supported in ClickZetta
           refresh_vc: default
       marts:
         +materialized: dynamic_table
         +dynamic_table:
           refresh_interval: "5 minutes"  # adjust to business SLA
           refresh_vc: default

       # Four-layer example (ODS → DWD → DWS → ADS):
       ods:
         +materialized: dynamic_table
         +dynamic_table:
           refresh_interval: "5 minutes"
           refresh_vc: default
       dwd:
         +materialized: dynamic_table
         +dynamic_table:
           refresh_interval: "5 minutes"
           refresh_vc: default
       dws:
         +materialized: dynamic_table
         +dynamic_table:
           refresh_interval: "5 minutes"
           refresh_vc: default
       ads:
         +materialized: dynamic_table
         +dynamic_table:
           refresh_interval: "5 minutes"
           refresh_vc: default
   ```

   Use the template matching the user's chosen layering mode. Individual models can override `refresh_interval` in their own `{{ config() }}` block — the layer default is just a fallback.

   **Exception**: small static reference tables (e.g. lookup/config tables with no upstream changes) can use `+materialized: table` at the model level — full rebuild is simpler and cheaper for these.

   Connection parameters for profiles.yml — two options (prefer config file if available):
   - **User provides a config file**: ask user to upload or paste an existing profiles.yml / cz-cli config file, extract parameters directly — no need to ask one by one
   - **Ask individually**: if no existing config, ask for each parameter in turn (see references/dbt-clickzetta-adapter.md):
     - `service`: API endpoint (e.g. `cn-shanghai-alicloud.api.clickzetta.com`)
     - `instance`: instance ID
     - `workspace`: workspace name (= dbt database)
     - `schema`: default write schema
     - `vcluster`: compute cluster name
     - `username` / `password`: credentials

Use the interactive question tool for user decision points. If no such tool is available, list options in text. **Do not proceed before receiving the user's answer.**

Ask the user to confirm three things: (1) **Project directory** — current directory, or a path they specify. (2) **Layering mode** — two-layer (staging → marts, recommended for small/medium projects), two-layer + intermediate (for complex multi-table joins), three-layer (ODS → DWD → ADS, for larger projects with multiple business domains), or four-layer (ODS → DWD → DWS → ADS, for large data warehouses with dedicated data teams). (3) **Naming prefix** — business domain name (e.g. retail, finance, marketing), company/team name (e.g. acme, dataeng), or a custom prefix they specify.

## Key Constraints

- **workspace = database**: ClickZetta workspace maps to dbt database; `{{ this }}` renders as `workspace.schema.table` — understanding this mapping is essential for correctly configuring profiles.yml and sources.yml
- **profiles.yml must not be committed to git**: the file contains plaintext passwords; committing to a public repo causes credential leakage — must be added to .gitignore
- **Clean up example files after dbt init**: `rm -rf models/example` — example models execute during `dbt run`, creating meaningless tables in Lakehouse and polluting the schema

## Routing

| Scenario | Route to |
|---|---|
| Already have a dbt project, want to model | `clickzetta-dbt-modeling` |
| Already have a dbt project, want to publish and schedule | `clickzetta-dbt-studio-pipeline` |
| Need to sync data to Lakehouse first | `clickzetta-data-ingest-pipeline` |
| Don't want dbt, use Dynamic Table directly | `clickzetta-dw-modeling` |

## Completion Criteria

- `dbt debug --profiles-dir .` outputs `All checks passed!`
- dbt_project.yml generated with layer schemas configured
- Next step: `clickzetta-dbt-modeling`
