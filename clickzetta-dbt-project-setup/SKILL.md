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
See [references/elt-standards.md](references/elt-standards.md) for the **complete end-to-end pipeline architecture** (ingestion → dbt modeling → Studio publishing), layering patterns, and naming conventions.

---

## Goal

Help users establish a dbt-clickzetta project that runs immediately, with correct connection configuration and layering standards.
Users don't need to understand dbt internals — they only need to answer a few business questions.

## Workflow

This skill runs as a series of conversation turns. Each turn ends with a question to the user — nothing is executed until the user responds to that turn's question.

---

### Turn 0 — Check installation, then ask setup questions

Run `pip show dbt-clickzetta` and `cz-cli schema list` in parallel. Report results immediately:
- Installation status ("dbt-clickzetta 1.7.x installed ✓" or "not installed — will install")
- Lakehouse state (greenfield or existing schemas found)

Then ask the user four things at once (present as choices, not blank fields):

1. **Connection config**: do you have an existing profiles.yml or cz-cli config file? If yes, paste or upload it. If no, I'll ask for each parameter next.
2. **Project directory**: current directory, or specify a path.
3. **Layering mode**: choose the pattern that fits your team —
   - **dbt standard** (staging → marts): recommended for most projects; add `intermediate/` when marts need complex multi-table JOINs
   - **Medallion** (bronze → silver → gold): popular in data lakehouse contexts; bronze = raw, silver = cleaned/conformed, gold = business-ready
   - **Traditional DW** (ODS → DWD → DWS → ADS): familiar to data warehouse teams; four-layer with aggregation layer
   - **Custom**: specify your own layer names
4. **Naming prefix**: business domain (e.g. retail, finance), company/team name, or custom.

**Stop here. Do not run `dbt init` or create any files yet.**

---

### Turn 1 — Collect connection parameters (if no config file provided)

If the user provided a config file in Turn 0: extract all parameters from it, skip to Turn 2.

If not, ask for each connection parameter (see [references/dbt-clickzetta-adapter.md](references/dbt-clickzetta-adapter.md)):
- `service`: API endpoint (e.g. `cn-shanghai-alicloud.api.clickzetta.com`)
- `instance`: instance ID
- `workspace`: workspace name (= dbt database)
- `schema`: **where dbt writes model outputs** — NOT the source data schema. Do not infer from the current session. Typical: `{project}_dw` or a name the user specifies.
- `vcluster`: compute cluster name (use `default` if unsure)
- `username` / `password`

**Stop here. Do not create any files yet.**

---

### Turn 2 — Confirm plan, then scaffold

Show a one-line summary of what will be created:
> "Creating `retail_dw` in current directory — staging → marts (dbt standard), prefix `retail`, writing to schema `retail_dw`."

(Adjust the summary to match the user's chosen layering mode.)

Ask: "Confirm?" Wait for the user's go-ahead.

Only after confirmation:
```bash
pip install dbt-clickzetta   # if not installed
dbt init {project_name}
rm -rf models/example        # remove example files — they pollute dbt run
```

Generate `dbt_project.yml`, `profiles.yml`, `.gitignore`. **Do NOT create any `.sql` model files** — model files are created by `clickzetta-dbt-modeling` after data exploration.

`dbt_project.yml` sets `dynamic_table` as the default materialization. Do not add `refresh_interval` here — each model sets its own value in `{{ config() }}`.

Generate the `+schema` blocks to match the user's chosen layering mode. Examples:

```yaml
# dbt standard (staging → marts)
models:
  {project_name}:
    +persist_docs:
      relation: true
      columns: true
    staging:
      +materialized: dynamic_table
      +schema: staging
    marts:
      +materialized: dynamic_table
      +schema: marts

# Medallion (bronze → silver → gold)
models:
  {project_name}:
    +persist_docs:
      relation: true
      columns: true
    bronze:
      +materialized: table
      +schema: bronze
    silver:
      +materialized: dynamic_table
      +schema: silver
    gold:
      +materialized: dynamic_table
      +schema: gold

# Traditional DW (ODS → DWD → DWS → ADS)
models:
  {project_name}:
    +persist_docs:
      relation: true
      columns: true
    ods:
      +materialized: table
      +schema: ods
    dwd:
      +materialized: dynamic_table
      +schema: dwd
    dws:
      +materialized: dynamic_table
      +schema: dws
    ads:
      +materialized: dynamic_table
      +schema: ads
```

For custom layering, generate the blocks based on the layer names the user specified.

---

### Turn 3 — Verify and hand off

Run `dbt debug --profiles-dir .` and report the result. If all checks pass, tell the user:
> "Project is ready. Next: load `clickzetta-dbt-modeling` to explore your Lakehouse data and build models."

If debug fails, diagnose and fix before handing off.

## Key Constraints

- **workspace = database**: ClickZetta workspace maps to dbt database; `{{ this }}` renders as `workspace.schema.table` — understanding this mapping is essential for correctly configuring profiles.yml and sources.yml
- **profiles.yml must not be committed to git**: the file contains plaintext passwords; committing to a public repo causes credential leakage — must be added to .gitignore
- **Clean up example files after dbt init**: `rm -rf models/example` — example models execute during `dbt run`, creating meaningless tables in Lakehouse and polluting the schema

## Routing

| Scenario | Route to |
|---|---|
| Already have a dbt project, want to model | `clickzetta-dbt-modeling` |
| Already have a dbt project, want to publish and schedule | `clickzetta-dbt-studio-pipeline` |
| Want SQL modeling without dbt (Dynamic Table / raw SQL) | `clickzetta-dw-modeling` |
| Need to sync data from MySQL/PostgreSQL in real-time | `clickzetta-cdc-sync-pipeline` |
| Need to sync data from any DB in batch | `clickzetta-batch-sync-pipeline` |
| Need to ingest files from OSS/S3/COS continuously | `clickzetta-oss-ingest-pipeline` |
| Need to ingest from Kafka | `clickzetta-kafka-ingest-pipeline` |
| Not sure which ingestion method to use | `clickzetta-data-ingest-pipeline` |
| Don't want dbt, use Dynamic Table directly | `clickzetta-sql-pipeline-manager` |

## Completion Criteria

- `dbt debug --profiles-dir .` outputs `All checks passed!`
- dbt_project.yml generated with layer schemas configured
- Next step: `clickzetta-dbt-modeling`
