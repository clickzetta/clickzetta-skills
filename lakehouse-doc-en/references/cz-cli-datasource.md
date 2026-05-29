# External Data Source Management (datasource)

The `datasource` command browses and tests external data sources configured in Studio (MySQL, PostgreSQL, Kafka, etc.). It is commonly used to validate connections before configuring sync tasks:

```bash
```

List all configured data sources:

```bash
cz-cli -p prod datasource list

```

Test data source connectivity:

```bash
cz-cli -p prod datasource test <datasource_name>

```

Browse databases/schemas in a data source:

```bash
cz-cli -p prod datasource catalogs <datasource_name>

```

Browse tables in a specific database:

```bash
cz-cli -p prod datasource objects <datasource_name> <catalog_name>

```

View metadata for a specific table:

```bash
cz-cli -p prod datasource describe <datasource_name> <catalog_name> <table_name>

```

Preview sample data from a table:

```bash
cz-cli -p prod datasource sample <datasource_name> <catalog_name> <table_name>
```

## Related Documentation

**cz-cli Documentation**

- [Installation and Configuration Guide](setup_cz_cli.md) — Installation, profile configuration, basic usage
- [Studio Task Development and Operations](cz-cli-studio-tasks.md) — Data sync task management

**Lakehouse Documentation**

- [Data Source Management](config-datasource.md) — External data source connection configuration (Web UI)
- [Data Integration Overview](data-integration.md) — Data sync feature overview
- [Real-time Sync Tasks](realtime_sync.md) — CDC real-time sync configuration
- [Batch Sync Tasks](batch_sync.md) — Batch offline sync configuration
