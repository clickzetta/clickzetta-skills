# Data Local Import and Export Function

The system provides data import and export functions to facilitate the transfer of data between local files and the database. The current version supports uploading and downloading data from local paths, but does not support using the COPY command directly in Studio. To execute the COPY command, you can use the [sqlline](connect-with-cli.md) tool or [database management tools](eco_integration/dbeaver-lakehouse.md). The local COPY command is different from the server-side COPY command. The current syntax is only applicable for local imports. For server-side imports to storage, please refer to the server-side COPY command.

# Notes
This command has been deprecated since jdbc2.0.0.
- To upload data, please first download the SQL LINE command line. Then use the [PUT command](<PUT.md>) to upload the file to the internal volume and then use the copy command to import it into the table. For specific practice commands, refer to [Import Local Data into Lakehouse](<load-data-local.md>).
- To download data, first download the SQL LINE command line. Then export the data to the internal volume and then use the [GET command](<GET.md>) to download it. For specific practice commands, refer to [Export Lakehouse Data to Local](<unload-data-local.md>).

## Upload Data

### Supported Parameter Settings

Before uploading data, you can set the following parameters to adjust the import process according to your needs. These parameters are only effective in the current session.

| Parameter                        | Default | Values       | Meaning                                   |
| -------------------------------- | ------- | ------------ | ----------------------------------------- |
| set copy.csv.skip.header=false   | false   | false\|TRUE  | Whether to skip the header, if the data contains a header, whether to skip it |
| set copy.csv.with.header=false   | false   | false\|true  | Whether the CSV contains a header, if it does, use the CSV header to match the table fields for insertion |
| set copy.csv.delimiter=','       | ','     | Single character delimiter supported | CSV delimiter                              |
| set copy.csv.escape='\\'         | '\\'    | Single character supported | CSV escape character                       |
| set copy.csv.null.string='\N'    | '\N'    | Single character supported | Empty string representing null in CSV      |

### Syntax

To upload data, use the following syntax:
```SQL
COPY table_name 
FROM file_location;
```
**Parameter Description**
**1. table_name**
Specify the name of the table to import data into.
**2. file_location**
Specify the local file path, enclosed in quotes.

### Example

On Linux and macOS systems:
```SQL
COPY demo_table FROM "/data/data.csv";
```
On Windows system:
```SQL
COPY demo_table FROM "c:\data\data.csv";
```
## Download Data

### Syntax

To download data, please use the following syntax:
```SQL
COPY select_statement|tablename
TO file_location;
```
**Parameter Description**
**1. table_name**
Specify the name of the table to export data from.
**2. select_statement**
Supports SELECT query statements.
**3. file_location**
Specify the local file path.

**Note**
When downloading data, the file format cannot be specified. The downloaded file is comma-separated by default. If the data volume is large, multiple files may be generated.

## Example

Download data:
```SQL
COPY demo_table TO "c:\data\output.csv";
```

^
