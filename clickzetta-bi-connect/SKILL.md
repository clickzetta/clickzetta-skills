---
name: clickzetta-bi-connect
description: |
  Connect BI tools and database clients to ClickZetta Lakehouse. Covers complete
  connection setup for Apache Superset, Tableau, Metabase, DBeaver, DataGrip,
  FineBI, PowerBI, Navicat, and more — including JDBC, SQLAlchemy URL, and
  MySQL protocol connection methods, plus driver installation and troubleshooting.

  Trigger this skill whenever the user wants to visualize, query, or report on
  ClickZetta data from an external tool — even if they haven't chosen a tool yet.
  Typical scenarios:
  - Explicitly mentions a BI or client tool (Superset, Tableau, Metabase, DBeaver,
    DataGrip, FineBI, PowerBI, Navicat, Grafana, Redash, Looker)
  - Wants to connect any visualization or reporting tool to Lakehouse
  - Asks about JDBC connection strings, SQLAlchemy URLs, or MySQL protocol connections
  - Has dbt models or marts tables ready and wants to start building dashboards
  - Asks "how do I query Lakehouse from Python / pandas / SQLAlchemy"
  - Gets a connection error from a BI tool and needs help troubleshooting
---

# clickzetta-bi-connect

See [references/bi-tools.md](references/bi-tools.md) for complete connection strings, driver download links, and per-tool configuration details.

---

## Goal

Get the user's chosen BI tool or database client connected to ClickZetta Lakehouse and running queries successfully.
Users don't need to know which connection protocol to use — identify the right method based on their tool and guide them through it.

## Workflow

**Identify tool → Select protocol → Provide connection config → Verify → Troubleshoot if needed**

1. **Identify the tool**: Ask which BI tool or client the user wants to connect (if not already stated). Present common options grouped by protocol:
   - **JDBC**: DBeaver, DataGrip, Tableau (via JDBC driver)
   - **SQLAlchemy**: Apache Superset, Python ORM, pandas
   - **MySQL protocol**: PowerBI, Navicat, FineBI, Metabase, most MySQL-compatible clients
   - **Native connector**: Tableau (via clickzetta connector plugin)

2. **Collect connection parameters** — ask the user for:
   - `instance`: instance ID (e.g. `f8866243`)
   - `workspace`: workspace name
   - `schema`: default schema
   - `vcluster`: compute cluster name (default: `default_ap`)
   - `username` / `password`
   - `region`: cloud region code (see Common Region Codes below)

3. **Provide the exact connection config** for their tool — connection string, URL, or step-by-step UI config. Use the templates in references/bi-tools.md.

4. **Verify**: Ask the user to run a test query (`SELECT 1` or `SHOW TABLES`) and confirm it works.

5. **Troubleshoot** if connection fails — see the Troubleshooting section below.

## Connection Method Quick Reference

| Tool | Protocol | Key config |
|---|---|---|
| Apache Superset | SQLAlchemy | `clickzettasql+clickzetta://...` |
| Tableau | JDBC or native connector | Download clickzetta-connector |
| Metabase | MySQL protocol | Host: `{region}.api.clickzetta.com`, Port: `3306` |
| DBeaver | JDBC | Download `clickzetta-jdbc-*.jar` |
| DataGrip | JDBC | Same as DBeaver |
| PowerBI | MySQL protocol | Use MySQL connector |
| Navicat | MySQL protocol | Host: `{region}.api.clickzetta.com`, Port: `3306` |
| FineBI | MySQL protocol | Same as Navicat |

## JDBC Connection String

```
jdbc:clickzetta://{region}.api.clickzetta.com/{workspace}?instance={instance}&virtualCluster={vcluster}&schema={schema}
```

Driver JAR: download from https://github.com/clickzetta/clickzetta-jdbc/releases

## SQLAlchemy URL (Superset / Python ORM)

```
clickzettasql+clickzetta://{username}:{password}@{region}.api.clickzetta.com/{workspace}?instance={instance}&virtualCluster={vcluster}&schema={schema}
```

Install: `pip install clickzetta-sqlalchemy`

## MySQL Protocol (PowerBI / Navicat / FineBI)

| Field | Value |
|---|---|
| Host | `{region}.api.clickzetta.com` |
| Port | `3306` |
| Database | `{workspace}` |
| Username | `{instance}/{username}` |
| Password | user password |

## Common Region Codes

| Region | Code |
|---|---|
| Alibaba Cloud Shanghai | `cn-shanghai-alicloud` |
| Alibaba Cloud Hangzhou | `cn-hangzhou-alicloud` |
| Tencent Cloud Shanghai | `cn-shanghai-tencent` |
| AWS Singapore | `ap-southeast-1-aws` |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Connection timeout | Wrong region code | Check instance region in ClickZetta console |
| Authentication failed | Wrong username format | MySQL protocol requires `{instance}/{username}` format |
| Driver not found | JDBC JAR not loaded | Add JAR path in DBeaver/DataGrip driver settings |
| SSL error | SSL not configured | Add `useSSL=false` to JDBC URL, or enable SSL in console |
| Schema not found | Wrong schema name | Run `SHOW SCHEMAS` to list available schemas |
| DirectQuery slow (PowerBI) | Large table scan | Add partition filter or use Import mode |

For persistent issues, check the ClickZetta console for connection logs, or run the test query directly in `cz-cli sql` to isolate whether the issue is the tool or the Lakehouse.
