The COPY command is a local data import and export interface provided by Singdata Lakehouse

## COPY Command

[COPY Command](download-data-with-copy.md)

## Usage Restrictions

* Only supports CSV file export
* Does not support using this command on the studio page, only supports executing with jdbc client, because this path needs to specify a local path. The studio page cannot read it. You can refer to the database management tools or command line tools in the ecosystem extension to connect to Lakehouse

## Application Scenarios

* Download data locally

## Prerequisites

* Install [Command Line Tool](connect-with-cli.md)
* Have SELECT permission on the table

## Execute Command

```
copy select * from my_table where id=1 to "/data/"
```

^
