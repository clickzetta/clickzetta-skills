# Installation and Usage Guide for N8N Integration with Unified AI Workflows

[N8N](https://n8n.io/) is a workflow automation platform that provides technical teams with code-like flexibility and no-code speed. With 400+ integrations, native AI capabilities, and a fair-code license, N8N enables you to build powerful automation flows while maintaining full control over your data and deployment.

Singdata Lakehouse integrates with N8N. This document is a complete installation, deployment, and daily usage guide to help you quickly get started with the Singdata Lakehouse and N8N integration!

In addition to serving as a standard N8N node, the Singdata Lakehouse extension also provides data comparison features, including:

* **Multi-database support**: In addition to supporting Singdata Lakehouse, this extension also supports Alibaba Cloud MaxCompute, HUAWEI CLOUD DLI, PostgreSQL, ClickZetta, MySQL, SQLite, Oracle, Microsoft SQL Server, and more.
* **Data comparison**: Table data comparison, schema comparison, real-time difference detection.
* **Workflow automation**: Visual workflow based on N8N.
* **Automatic parameter filling**: Intelligently fetches connection information and table lists from upstream nodes.
* **Expression references**: Supports N8N expression syntax for referencing upstream data.

:-: ![](.topwrite/assets/image_1756880876090.png =747)

^

Below are descriptions of the extension nodes:

* N8N nodes supporting Singdata Lakehouse:

:-: ![](.topwrite/assets/image_1756881498726.png =339)

^

* N8N nodes supporting more database types:

:-: ![](.topwrite/assets/image_1756881587120.png =285)

^

* Data comparison node (async execution):

:-: ![](.topwrite/assets/image_1756881686613.png =301)

^

* Get data comparison results node:

:-: ![](.topwrite/assets/image_1756881921377.png =333)

## Prerequisites

* Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) or Docker Engine

* At least 8GB of memory

* Available ports:

  * 80 (Nginx unified entry)
  * 5678 (N8N, modifiable via .env)
  * 8000 (API, modifiable via .env)
  * 3000 (Grafana, modifiable via .env)
  * 9090 (Prometheus, modifiable via .env)
  * 5432 (PostgreSQL, modifiable via .env)

## Installation and Deployment

### 1️⃣ Download the Deployment Package

Download `data-diff-n8n-deploy-latest.zip` and extract it to any directory:

Download using curl (recommended):

```bash
curl -L -O https://github.com/yunqiqiliang/clickzetta_quickstart/raw/main/datadiff_n8n_clickzetta/data-diff-n8n-deploy-latest.zip

```

Or download using wget (overwrite existing files):

```bash
wget -O data-diff-n8n-deploy-latest.zip https://github.com/yunqiqiliang/clickzetta_quickstart/raw/main/datadiff_n8n_clickzetta/data-diff-n8n-deploy-latest.zip

```

Extract deployment package (overwrite mode):

```bash
unzip -o data-diff-n8n-deploy-latest.zip
cd data-diff-n8n/

```

If you need interactive confirmation for each file overwrite:

unzip data-diff-n8n-deploy-latest.zip:

### 2️⃣ Check Ports (Recommended)

Check if the required ports are available before deployment:

**Windows**:
```cmd
check-ports.bat
```

**macOS/Linux**:
```bash
./check-ports.sh
```

The check script automatically detects whether all required ports are available. If port conflicts are found, you can:

1. Stop the service occupying the port
2. Or edit the `.env` file to modify the corresponding port after running `./deploy.sh setup`

### 3️⃣ Initialize Configuration

**Windows**:
```cmd
deploy.bat setup
```

**macOS/Linux**:
```bash
./deploy.sh setup
```

This command will:

* Create the `.env` configuration file
* Automatically generate secure passwords
* Prepare the deployment environment

⚠️ **Important Reminder**:

*   After initialization, **please immediately view and save** the passwords in the `.undefined` **file**.

*   Automatically generated passwords include:

  *   PostgreSQL database password (POSTGRES_PASSWORD)
  *   N8N basic authentication password (N8N_BASIC_AUTH_PASSWORD, default username is admin)
  *   Grafana admin password (GRAFANA_PASSWORD, default username is admin)

* Please keep these passwords safe. They cannot be recovered if lost.

### 4️⃣ Start Services

#### First Deployment

**Windows**:
```cmd
deploy.bat init
```

**macOS/Linux**:
```bash
./deploy.sh init
```

Startup time depends on whether images need to be downloaded:

* **First startup**: 10-20 minutes (all Docker images need to be downloaded, approximately 2GB)
* **Subsequent startups**: 2-3 minutes (images are already local)

During startup, the system will:

1. Automatically pull all required Docker images (6 services)
2. Create and initialize the PostgreSQL database
3. Configure Grafana dashboards
4. Start all services and perform health checks

#### Daily Usage

**Windows**:
```cmd
deploy.bat start
```

**macOS/Linux**:
```bash
./deploy.sh start
```

The `start` command directly starts all services, suitable for daily use.

💡 Tip:

* Use `deploy.sh status` to check startup progress
* Use `deploy.sh logs` to view service logs

## Access Services

After deployment is complete, you can access the services as follows:

| Service            | Access URL                                  | Description                 |
| --------------- | ----------------------------------------- | -------------------- |
| 🏠 Home         | [http://localhost](http://localhost/)               | System overview and quick navigation     |
| 🔄 N8N Workflow    | <http://localhost/n8n/>            | Create and manage data comparison workflows |
| 📊 API Docs     | <http://localhost/api/docs>            | RESTful API interface documentation |
| 📖 API Reference     | <http://localhost/api/redoc>           | API reference manual (ReDoc style) |
| 📈 Grafana Monitoring | <http://localhost/grafana/>            | Data quality and system monitoring dashboards |
| 🔍 Prometheus   | <http://localhost/prometheus/>           | Metrics query and alert management      |

:-: ![](.topwrite/assets/image_1756882465416.png =821)

For login credentials, check the passwords in the `.env` file.

💡 **Tips**:

* All services are accessed through **port 80** (Nginx reverse proxy is automatically configured).
* Due to sub-path configuration, **direct access through service ports is not supported** (e.g., N8N's port 5678).
* **Remote access**: When deployed on a server, replace `localhost` with the server IP address (e.g., `http://172.17.1.220`).
* **Modify port**: To modify port 80, edit `HTTP_PORT` in the `.env` file and restart the services.

## Daily Operations

### Check Service Status

Windows:

```bash
deploy.bat status

```

macOS/Linux:

```bash
./deploy.sh status
```

### View Logs

View all service logs:

```bash
deploy.bat logs

```

View specific service logs:

```bash
deploy.bat logs n8n
```

### Stop Services

**Windows**:
```cmd
deploy.bat stop
```

**macOS/Linux**:
```bash
./deploy.sh stop
```

### Restart Services

**Windows**:
```cmd
deploy.bat restart
```

**macOS/Linux**:
```bash
./deploy.sh restart
```

### Other Commands

**Full stop (remove containers)**:

```bash
./deploy.sh stop-all
```

**Full restart (including initialization check)**:

```bash
./deploy.sh restart-full
```

💡 Tips:

* For daily operations, use `start`, `stop`, `restart`.
* `stop` only stops containers; `stop-all` removes them.
* `init` and `restart-full` include full initialization checks, suitable for troubleshooting.

## Configuration Guide

Edit the `.env` file to modify:

* **Port configuration**: Unified access through port 80 by default
* **Password settings**: Modify access passwords for each service
* **Resource limits**: Adjust the number of API worker processes, etc.
* **Public URL**: Configure N8N's external access address

Example:

Modify the unified entry port (default 80):

```env
HTTP_PORT=8080

```

Configure N8N public URL (for generating invitation links, etc.):

```env
N8N_PUBLIC_URL=http://172.17.1.220/n8n

```

Modify the number of API worker processes (default 4):

```env
API_WORKERS=8

```

Modify the database port (if external access is needed):

```env
POSTGRES_PORT=5433
```

## Diagnostic Tools

### check-env-vars.sh Usage Guide

Use this tool for diagnostics when encountering database connection or authentication issues:

```bash
./check-env-vars.sh
```

**Applicable scenarios**:

* N8N or API service reports "password authentication failed"
* Need to verify whether environment variables are correctly passed to containers
* Check the actual configuration values used inside containers

**Feature description**:

1. Display configuration in the `.env` file
2. Show environment variables after Docker Compose parsing
3. Check actual environment variables of running containers
4. Test whether the database connection is working

**Example output**:

```bash
=== Environment Variable Check Tool ===

1. Check .env file content:
POSTGRES_PASSWORD setting: VUEk30jlqj6rd48U

2. Environment variables after Docker Compose parsing:
[Display environment variable configuration for each service]

3. Actual environment variables of running containers:
[Display actual environment variables inside containers]

4. Test database connection:
✓ Can connect using .env password
```

If password mismatch is found, a cleanup and redeployment is usually needed:

```bash
./deploy.sh clean
./deploy.sh setup
./deploy.sh init
```

## Update Deployment

When a new version is released, follow these steps to update:

### Update with Configuration Preservation

1. Backup current configuration (recommended):

```bash
cp .env .env.backup

```

2. Download the latest version (overwrite old files):

```bash
curl -L -O https://github.com/yunqiqiliang/clickzetta_quickstart/raw/main/datadiff_n8n_clickzetta/data-diff-n8n-deploy-latest.zip

```

3. Extract and overwrite (excluding .env file):

```bash
unzip -o data-diff-n8n-deploy-latest.zip -x "data-diff-n8n/.env"

```

4. Restart services:

```bash
./deploy.sh restart
```

### Full Overwrite Update

Warning: This will overwrite all files, including configurations:

```bash
unzip -o data-diff-n8n-deploy-latest.zip
```

💡 **Tips**:

* The `-o` option means automatically overwrite all files without prompting.
* The `-x` option can exclude specific files from being overwritten.
* It is recommended to always backup the `.env` file first, as it contains your password configuration.

## Troubleshooting

### Port Occupied

Port 80 is used as the unified entry by default. If port 80 is occupied:

1. Edit the `.env` file and modify `HTTP_PORT`:

   ```env
   HTTP_PORT=8080  # or another available port
   ```

2. Restart services:

   ```bash
   ./deploy.sh restart
   ```

3. Access via new port:

   ```bash
   http://localhost:8080
   ```

### Docker Not Running

Make sure Docker Desktop is started and running.

### Service Inaccessible

1. Use `deploy.bat status` to check service status
2. Use `deploy.bat logs` to view error logs
3. Ensure the firewall allows access to the corresponding ports

### Database Initialization Error

If you see the following errors:

* `Database initialization failed: datadiff database does not exist`
* `Database tables were not created correctly`
* `password authentication failed for user "postgres"`
* `relation "data_diff_results.comparison_summary" does not exist`

**Cause**:

1.  The PostgreSQL data volume retains old configuration or passwords.
2.  The database initialization script failed to execute (PostgreSQL only executes scripts in `/docker-entrypoint-initdb.d/` when the data volume is first created).

**Solution**:

Full cleanup and redeployment: ./deploy.sh clean ./deploy.sh setup ./deploy.sh init:

**Notes**:

* PostgreSQL uses Docker volumes to store data. `init-databases.sql` is executed upon first startup.
* If the data volume already exists, the SQL file will not be re-executed even if updated.
* The `clean` command removes the data volume to ensure re-initialization on the next startup.

**Important**: The `clean` command will delete all data. Please ensure important data is backed up.

## Advanced Usage

### Create Your First Comparison Workflow

1. Access N8N (<http://localhost/n8n/>)

2. Log in using the credentials in `.env`

   * Username: admin (or check N8N\_BASIC\_AUTH\_USER)
   * Password: Check N8N\_BASIC\_AUTH\_PASSWORD in `.env`

3. Create a new workflow

4. Add a "Data Comparison Dual Input" node

5. Configure source and target database connections

6. Run the workflow and view the results

### View Monitoring Dashboards

1. Access Grafana (<http://localhost/grafana/>)

2. Log in using admin and the password in `.env`

3. Open the pre-configured dashboards:

   * **Business Metrics**: View data quality and comparison results
   * **System Monitoring**: View performance and resource usage

### Using API Endpoints

1. Access API documentation (<http://localhost/api/docs>)

2. Supported main endpoints:

   * `/api/v1/compare/tables` - Compare data between two tables
   * `/api/v1/compare/schemas/nested` - Compare database schema structures
   * `/api/v1/connections/test` - Test database connection
   * `/api/v1/tables/list` - Get database table list
   * `/api/v1/query/execute` - Execute SQL queries
   * `/api/v1/maintenance/db-maintenance` - Database maintenance operations
   * `/api/v1/metrics` - Get system metrics in Prometheus format

3. You can test API calls directly on the documentation page.

## Need Help?

* View project documentation
* Report issues
* Contact technical support

## Security Tips

* Please be sure to modify the default passwords in the `.env` file
* Regularly backup database data
* Restrict the network access scope of the services

## Reference

This project is open source: <https://github.com/yunqiqiliang/data-diff-n8n>
