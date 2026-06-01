# DBT + Singdata Lakehouse Quickstart

This guide uses the [jaffle-shop-clickzetta](https://github.com/clickzetta/jaffle-shop-clickzetta) sample project to walk you through the complete workflow for connecting dbt to Singdata Lakehouse: installing dependencies, configuring the connection, loading data, building models, and running tests.

jaffle-shop is the standard sample project maintained by dbt, simulating a coffee shop's order data. It includes 6 raw data tables, 6 staging views, 7 mart tables, and 27 data quality tests.

## Prerequisites

- Python 3.10 or higher (3.12 recommended)
- A working Singdata Lakehouse instance (requires a workspace, vcluster, username, and password)

## Step 1: Clone the Project

```bash
git clone https://github.com/clickzetta/jaffle-shop-clickzetta.git
cd jaffle-shop-clickzetta
```

## Step 2: Install dbt-clickzetta

Create a virtual environment and install the adapter:

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install "dbt-clickzetta>=1.7.8"
```

Verify the installation:

```bash
dbt --version
```

Example output:

```Plain
Core:
  - installed: 1.10.x

Plugins:
  - clickzetta: 1.6.5 - Up to date!
```

## Step 3: Configure the Connection

Copy the connection template and fill in your instance information:

```bash
cp profiles.yml.example profiles.yml
```

Edit `profiles.yml` and replace the placeholders in angle brackets:

```yaml
jaffle_shop:
  target: dev
  outputs:
    dev:
      type: clickzetta
      service: <your-service-endpoint>   # e.g. cn-shanghai-alicloud.api.clickzetta.com, without https://
      instance: <your-instance-id>
      workspace: <your-workspace>
      username: <your-username>
      password: <your-password>
      schema: dbt_jaffle
      vcluster: default
```

> ⚠️ **Note**: `profiles.yml` is already in `.gitignore` and will not be committed to Git, preventing password leaks.

Verify the connection:

```bash
dbt debug --profiles-dir .
```

All checks showing `OK` means the connection is successful.

> 💡 **Tip**: `dbt debug` does not verify whether the `vcluster` exists. If it is entered incorrectly, the error will only appear at the `dbt seed` stage. The `vcluster` name can be confirmed on the compute cluster page in Singdata Lakehouse Studio.

## Step 4: Install Dependency Packages

```bash
dbt deps --profiles-dir .
```

This project depends on `dbt_utils` (1.3.3) and `dbt_date` (0.17.1). After installation:

```Plain
Installing dbt-labs/dbt_utils
Installed from version 1.3.3

Installing godatadriven/dbt_date
Installed from version 0.17.1
```

## Step 5: Load Raw Data

```bash
dbt seed --profiles-dir .
```

Loads the 6 CSV files under `seeds/jaffle-data/` into the `dbt_jaffle.raw` schema, approximately 150,000 rows total. This normally completes in about 1 minute:

```Plain
1 of 6 OK loaded seed file raw.raw_customers ......... INSERT 935
2 of 6 OK loaded seed file raw.raw_items ............. INSERT 90900
3 of 6 OK loaded seed file raw.raw_orders ............ INSERT 61948
4 of 6 OK loaded seed file raw.raw_products .......... INSERT 10
5 of 6 OK loaded seed file raw.raw_stores ............ INSERT 6
6 of 6 OK loaded seed file raw.raw_supplies .......... INSERT 65

Done. PASS=6 WARN=0 ERROR=0 SKIP=0 TOTAL=6
```

> 💡 **Tip**: If it fails or is interrupted midway, add `--full-refresh` when rerunning to clear already-written data and start over:
>
> ```bash
> dbt seed --profiles-dir . --full-refresh
> ```

## Step 6: Build Models

```bash
dbt run --profiles-dir .
```

Builds 13 models in dependency order (6 staging views + 7 mart tables):

```Plain
1 of 13 OK created sql table model dbt_jaffle.metricflow_time_spine
2 of 13 OK created sql view model dbt_jaffle.stg_customers
3 of 13 OK created sql view model dbt_jaffle.stg_locations
4 of 13 OK created sql view model dbt_jaffle.stg_order_items
5 of 13 OK created sql view model dbt_jaffle.stg_orders
6 of 13 OK created sql view model dbt_jaffle.stg_products
7 of 13 OK created sql view model dbt_jaffle.stg_supplies
8 of 13 OK created sql table model dbt_jaffle.locations
9 of 13 OK created sql table model dbt_jaffle.products
10 of 13 OK created sql table model dbt_jaffle.order_items
11 of 13 OK created sql table model dbt_jaffle.supplies
12 of 13 OK created sql table model dbt_jaffle.orders
13 of 13 OK created sql table model dbt_jaffle.customers

Done. PASS=13 WARN=0 ERROR=0 SKIP=0 TOTAL=13
```

After the build completes, the following objects will appear in the `dbt_jaffle` schema of Singdata Lakehouse:

| Object | Type | Description |
|--------|------|-------------|
| `stg_customers` | View | Cleaned customer data |
| `stg_locations` | View | Cleaned store data |
| `stg_order_items` | View | Cleaned order line item data |
| `stg_orders` | View | Cleaned order data |
| `stg_products` | View | Cleaned product data |
| `stg_supplies` | View | Cleaned supply data |
| `customers` | Table | Customer wide table (with spending summary) |
| `orders` | Table | Order wide table (with product and amount details) |
| `order_items` | Table | Order line item wide table |
| `locations` | Table | Store dimension table |
| `products` | Table | Product dimension table |
| `supplies` | Table | Supply dimension table |
| `metricflow_time_spine` | Table | MetricFlow time axis helper table |

## Step 7: Run Data Quality Tests

```bash
dbt test --profiles-dir .
```

Runs 27 data quality tests covering uniqueness, non-null, referential integrity, and business logic validation:

```Plain
Done. PASS=27 WARN=0 ERROR=0 SKIP=0 TOTAL=27
```

## Step 8: View Project Documentation (Optional)

```bash
dbt docs generate --profiles-dir .
dbt docs serve
```

Open `http://localhost:8080` in your browser to view the complete data lineage graph and field descriptions.

## Project Structure

```Plain
jaffle-shop-clickzetta/
├── models/
│   ├── staging/
│   └── marts/
├── seeds/
│   └── jaffle-data/
├── macros/
│   └── clickzetta_seed_batch_size.sql
├── profiles.yml.example
└── dbt_project.yml
```

- `models/staging/`: Raw data cleaning layer, materialized as views
- `models/marts/`: Business wide table layer, materialized as tables
- `seeds/jaffle-data/`: 6 CSV raw data files
- `macros/clickzetta_seed_batch_size.sql`: Singdata Lakehouse adaptation macro, controls batch write size
- `profiles.yml.example`: Connection configuration template

## Frequently Asked Questions

**Q: What should I do if `dbt debug` reports a connection failure?**

Check that `service`, `instance`, and `workspace` in `profiles.yml` are filled in correctly. `service` is the API endpoint domain name, not an HTTP URL — do not add the `https://` prefix.

**Q: Why are unit tests disabled?**

The original jaffle-shop project includes 3 dbt unit tests. The SQL they generate uses `cast(null as string not null)` syntax, which Singdata Lakehouse does not currently support in `cast` expressions with `not null` constraints. Therefore, unit tests are uniformly disabled in `dbt_project.yml`. All 27 data tests run normally.

## Command Reference

| Command | Purpose |
|---------|---------|
| `dbt deps` | Install dependency packages declared in packages.yml |
| `dbt seed` | Load CSV files as database tables |
| `dbt run` | Compile and execute all models |
| `dbt test` | Run data quality tests |
| `dbt docs generate` | Generate project documentation |
| `dbt docs serve` | View documentation in a local browser |

## Related Documentation

- [dbt ClickZetta Adapter Usage Guide](dbt.md)
- [jaffle-shop-clickzetta GitHub Repository](https://github.com/clickzetta/jaffle-shop-clickzetta)
