# Importing Data from Feishu

## How to Import Feishu Spreadsheet Data into Lakehouse

## 1. **Prerequisites**

Feishu app creation: Obtain app credential information

Singdata Lakehouse account information: Log in to the Singdata web console to create script tasks for data import

Target spreadsheet type confirmation: This part is very important! You need to determine the required permissions based on the target spreadsheet type.

## 2. **Feishu App Creation and Configuration**

### Create a Feishu App

#### Step 1: Log in to Feishu Open Platform

Visit: <https://open.feishu.cn/>

Log in with your Feishu account

Click "Enter Developer Console" in the upper right corner

![](.topwrite/assets/702bc8f656/84b36fb92c71d784ac5232a6d14363a3ce7b1ca9.png =200)

#### Step 2: Create an App

Click "Create App"

Select "Enterprise Self-built App"

Fill in app information:

**App Name**: Singdata Data Sync App

**App Description**: Sync Feishu spreadsheet data to Singdata Lakehouse

**App Icon**: Upload an app icon (optional)

#### Step 3: Obtain App Credentials

After creation, on the "Credentials & Basic Info" page in the left menu, record:

**App ID**: cli_xxxxxxxxxx

**App Secret**: xxxxxxxxxxxxxxxx

### Configure App Permissions

Before configuring permissions, first confirm the file type you need to import, and enable the corresponding permissions based on Feishu documentation requirements. This article uses spreadsheets (sheets) as an example. For details, refer to the [Feishu API documentation](https://open.feishu.cn/document/server-docs/docs/docs-overview)

#### Step 1: Request Permission Scope

Enter the "Permission Management" page

Search and add the following permissions:

**Spreadsheet-related permissions**:

sheets:spreadsheet - View, comment, edit, and manage spreadsheets

sheets:spreadsheet:readonly - View spreadsheets

drive:drive - View cloud document folders

**Specific operations**:

> Permission Scope -> Search "sheets" -> Check the following permissions:
>  1. View, comment, edit, and manage spreadsheets
>  2. View and edit spreadsheets
>  3. View cloud document folders

#### Step 2: Request Permission Approval

Click "Create Version"

Fill in the version description: Data sync feature launch

Submit for review (if it is an internal enterprise app, it is usually automatically approved)

#### Step 3: Publish the App

After approval, click "Apply for Online Release"

Select release scope:

**Visible to All**: Recommended

**Specified Departments**: Choose as needed

### Obtain Spreadsheet Access Permission

Note: For enterprise users, in addition to configuring permissions in the app development settings, you also need to grant app access permissions within the document.

1. Open the target Feishu spreadsheet
2. Click the ... in the upper right corner -> Select More -> Add Document App

   ![](.topwrite/assets/702bc8f656/d2431b8bc2172f0528f9b4015bafc0eef754e3ff.png =200)
3. Configure document app permissions
   Search for app name: Singdata Data Sync App
   Set permission: **Editable** (ensures data can be read)

### Record Key Information

**App Credentials**: The identity and security credentials for the Feishu Open Platform app

* **App ID**: cli_xxxxxxxxxx
* **App Secret**: xxxxxxxxxxxxxxxx

**tenant_access_token**: The credential used by self-built apps on the Feishu Open Platform to access tenant resources. Maximum validity period is 2 hours.

**Information required in data resource URLs**: For example, for spreadsheet URLs: <https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/:spreadsheetToken/values/:range>

* spreadsheetToken: The token of the spreadsheet
* Range: Format is <sheetId>!<start_position>:<end_position>.

## 3. **Importing Feishu Data into Singdata Lakehouse**

### Method 1: Import Feishu Data Using a Python Script

#### Step 1: Create a Python Task in Singdata Studio

1. Log in to the Singdata Lakehouse console
2. Go to "Development" -> "Python Tasks"
3. Click "New Task"
4. Configure task info: **Task Name**: Feishu Data Sync, **Task Description**: Import data from Feishu spreadsheet to Lakehouse

#### Step 2: Configure Code Parameters

```py
import requests
from sqlalchemy import text
from clickzetta_dbutils import get_active_lakehouse_engine

def get_feishu_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    data = {"app_id": "your_own_app_id", "app_secret": "xxxxxxxxxxxxx"}
    response = requests.post(url, json=data, timeout=5)
    return response.json()['tenant_access_token']

def get_sheet_data(token):
    url = "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/DuUHsqS6qh97i9tpNkYcoC84nHb/values/2729cf!A1:B2"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers, timeout=5)
    return response.json()['data']['valueRange']['values']

def get_lakehouse_connection():
    """
    Use get_active_lakehouse_engine to connect to Lakehouse. Users do not need to fill in Singdata-related account info in Python.
    Note: The vcluster parameter is required.
    """
    engine = get_active_lakehouse_engine(
        vcluster="DEFAULT",  # Required: virtual cluster name
        workspace="corresponding workspace name",  # Optional: workspace name
        schema="public"  # Optional: schema name, defaults to public
    )
    return engine

def create_table():
    """Create table: Users need to create a standardized table based on the data info in the Feishu spreadsheet"""
    engine = get_lakehouse_connection()

    create_sql = text("""
    CREATE TABLE IF NOT EXISTS feishu_data (
        name VARCHAR(255),
        id BIGINT,
        created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    with engine.connect() as conn:
        conn.execute(create_sql)

    print("Table created successfully")

def insert_data(data):
    """Insert data"""
    engine = get_lakehouse_connection()
    headers = data[0]
    rows = data[1:]

    # Batch generate SQL
    for i, row in enumerate(rows):
        name = str(row[0]).replace("'", "''")  # Escape single quotes
        id_value = int(row[1])

        with engine.connect() as conn:
            insert_sql = f"INSERT INTO feishu_data (name, id) VALUES ('{name}', {id_value})"
            conn.execute(text(insert_sql))
            print(f"Inserted row {i+1}: {name}, {id_value}")

    print(f"Data insertion complete, {len(rows)} records total")

def verify_data():
    """Verify data"""
    engine = get_lakehouse_connection()

    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM feishu_data ORDER BY created_time DESC"))
        rows = result.fetchall()

        print(f"\nVerification result ({len(rows)} records total):")
        for row in rows:
            print(f"  name: {row.name}, ID: {row.id}, Time: {row.created_time}")

if __name__ == "__main__":
    print("Feishu data import to Singdata Lakehouse")
    print("=" * 50)

    # 1. Get Feishu data
    print("\nGetting Feishu data...")
    token = get_feishu_token()
    print(f"Token obtained: {token[:10]}...")

    data = get_sheet_data(token)
    print("Feishu data obtained:")
    for i, row in enumerate(data):
        print(f"  Row {i+1}: {row}")

    # 2. Create table
    print(f"\nCreating Lakehouse table...")
    create_table()

    # 3. Insert data
    print(f"\nInserting data...")
    insert_data(data)

    # 4. Verify data
    print(f"\nVerifying results...")
    verify_data()

    print(f"\nTask complete!")
```

#### Step 3: Configure Schedule for Periodic Execution (Optional)

If you need to periodically pull data from the spreadsheet, you can directly configure the schedule for this Python task.

For example: To pull the latest data at 8:00 AM every day, configure as follows:

1. Schedule cycle: Daily
2. Schedule frequency: Execute once, Start time: 08:00
3. Effective date: 2025-06-11 (the date you want the task to start running)

![](.topwrite/assets/702bc8f656/0aabbf094597aaef2e4fcda3bb5a5f4cda9e35c8.png =300)

### Method 2: Import Feishu Data Using an Offline Sync Task

Currently, the offline task method does not support periodic data extraction; only manual trigger execution is supported.

#### Step 1: Obtain tenant_access_token

You can use a Python script to obtain the **tenant_access_token**.

1. Log in to the Singdata Lakehouse console
2. Go to "Development" -> "Python Tasks"
3. Click "New Task"

Configure task info:

**Task Name**: Get Feishu tenant_access_token

```
import requests  # Add import statement

def get_feishu_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    data = {
        "app_id": "cli_xxxxxxx",
        "app_secret": "xxxxxxxxxxxxxx"
    }
    response = requests.post(url, json=data)

    # Add error handling (important!)
    if response.status_code != 200:
        raise Exception(f"HTTP request failed, status code: {response.status_code}")

    json_data = response.json()

    # Check Feishu API error response
    if json_data.get("code") != 0:
        raise Exception(f"Feishu API error: [{json_data.get('code')}] {json_data.get('msg')}")

    return json_data['tenant_access_token']

# Call the function and print the result
try:
    result = get_feishu_token()
    print(f"Obtained tenant access token: {result}")
except Exception as e:
    print(f"Failed to get token: {str(e)}")
```

^

#### Step 2: Create Feishu Data Source Using RestApi

1. Log in to the Singdata Lakehouse console
2. Go to "Administration - Data Sources"
3. Create a new data source, select RestApi

> * Data Source Name: Feishu Data
> * URL: <https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/>:**spreadsheetToken**/values/:**range**
>   * spreadsheetToken: The token of the spreadsheet
>   * Range: Format is <sheetId>!<start_position>:<end_position>. For parameter details, refer to the [Feishu documentation](https://open.feishu.cn/document/server-docs/docs/sheets-v3/data-operation/reading-a-single-range)
> * Request Method: GET
> * KEY: Content-Type // fixed value
> * VALUE: application/json; charset=utf-8 // fixed value
> * Authentication Method: No verification

![](.topwrite/assets/702bc8f656/d60f2dd672cc92dd8344e17699256b288942d1e1.png =300)

#### Step 3: Create an Offline Sync Task to Sync Data

1. Log in to the Singdata Lakehouse console
2. Go to "Development" -> "Offline Sync"
3. Click "New Task"

> Source and Target Configuration:
>
> * Source Data: Select the data source to sync: Feishu Data. Data source configuration refers to Step 2.
> * Request Parameters: Empty
> * Request Body: Fill in app credentials  { "app_id": "cli_xxxx", "app_secret": "xxxxxxxxxxxxxx" }
> * Request Headers: key : value  Content-Type: application/json; charset=utf-8  Authorization: Bearer **tenant_access_token**
> * Result Data Path: The specific location of the data you want to import. You can leave this empty first, and fill it in after previewing the data to confirm the location.
>   -----------------------------------------------------------------------------------
> * Target Data: The destination address for the imported data. If importing into Singdata Lakehouse, you need to create the corresponding table first. (Quick table creation is not currently supported for this method.)
>   Illustration: The target data object table name is: test02_feishu

![](.topwrite/assets/702bc8f656/0c09f43f3b51860fa007c039db7a532a5a9f7cc5.png =300)

Field Mapping Configuration: Nested array format JSON parsing is not currently supported. Therefore, for data returned by the Feishu API, only value values can be imported into the target table as string type.
| ------------------------------------------------------------------- |

![](.topwrite/assets/702bc8f656/06c63b288c79f24b2781a479041ca4da24faf705.png =300)

#### Step 4: Data Processing - Parse Imported String Fields into Standardized Tables

1. Prerequisite: Users need to define the table structure in advance.
2. Log in to the Singdata Lakehouse console
3. Go to "Development" -> "SQL Tasks"
4. Click "New Task"

```
-- 1. Create target table
CREATE TABLE if not EXISTS test02_feishu_parsed (
    name STRING,
    id BIGINT
);

-- 2. Transform and insert data
INSERT INTO test02_feishu_parsed
WITH parsed AS (
    SELECT from_json(content, 'array<array<string>>') as arr
    FROM test02_feishu
    WHERE content IS NOT NULL
),
flattened AS (
    SELECT explode(slice(arr, 2, size(arr))) as row_data
    FROM parsed
    WHERE size(arr) > 1
)
SELECT
    row_data[0] as name,
    CAST(row_data[1] AS BIGINT) as id
FROM flattened;

-- 3. View results
SELECT * FROM test02_feishu_parsed;
```

## 4. **FAQ**

### Q1: What is the difference between using a Python script and an offline task to import Feishu data?

Python script import: Supports periodic scheduling for data from Feishu spreadsheets, but requires users to be familiar with Python syntax.

Offline task import: Provides a no-code page configuration with a lower barrier to entry. However, periodic scheduling is not currently supported; it will be supported in future versions.

### Q2: I keep getting permission errors during development

Check whether the relevant permissions are configured correctly.

In the Feishu app: Whether the correct permissions have been configured based on the file type. Note that the permissions for sheets and wikis in the URL are different; make sure to select the correct permission points.

Whether it has been published and approved after configuration: After configuring permissions, users also need to click "Publish" and wait for administrator approval before the permission points take effect.

Whether access permissions have been configured for the app within the Feishu document. This step is very important! Enterprise users must complete this configuration to access via the API.
