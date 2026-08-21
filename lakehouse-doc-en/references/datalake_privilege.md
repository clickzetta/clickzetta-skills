# Data Lake Permission Management

Volumes and Remote Functions are both objects under a schema. Grant object-creation privileges on the parent schema, and grant privileges for reading, using, altering, or dropping an existing object on that specific object. This separation avoids granting broad schema privileges when a user only needs access to one object.

This page covers permissions for:

1. Volume objects
2. Remote Function objects

## Volume Object Permissions

| Level | Privilege | Purpose |
|---|---|---|
| Schema | `CREATE VOLUME` | Create a Named Volume or External Volume in the schema |
| Volume | `READ METADATA` | View Volume object metadata |
| Volume | `READ VOLUME` | List, query, and download files in the Volume |
| Volume | `WRITE VOLUME` | Upload or remove files in the Volume |
| Volume | `ALTER VOLUME` | Alter the Volume or refresh file metadata for an External Volume |
| Volume | `DROP VOLUME` | Drop the specified Volume |
| Volume | `ALL PRIVILEGES` | Grant all privileges on the Volume |

Grant `CREATE VOLUME` only on the parent schema and `DROP VOLUME` only on a specific Volume. For example:

```sql
GRANT CREATE VOLUME ON SCHEMA public TO ROLE volume_admin;
GRANT DROP VOLUME ON VOLUME public.shared_files TO ROLE volume_admin;
```

The `VOLUME` suffix in a privilege name is optional. For example, `GRANT READ ON VOLUME ...` is accepted, but the full privilege name is recommended. `SHOW GRANTS` displays the normalized names `READ VOLUME`, `WRITE VOLUME`, `ALTER VOLUME`, and `DROP VOLUME`.

### Grant a New User Access to a Volume

The following example creates a read-only role and allows a user to read `public.shared_files`:

```sql
CREATE ROLE volume_reader;
GRANT READ VOLUME ON VOLUME public.shared_files TO ROLE volume_reader;
GRANT ROLE volume_reader TO USER datalake_user;
```

The user also needs access to a compute cluster to run queries or file operations. To allow the user to upload files and refresh file metadata for an External Volume, grant these additional privileges:

```sql
GRANT USE VCLUSTER ON VCLUSTER DEFAULT TO USER datalake_user;
GRANT WRITE VOLUME ON VOLUME public.shared_files TO USER datalake_user;
GRANT ALTER VOLUME ON VOLUME public.shared_files TO USER datalake_user;
```

When a Volume object privilege is granted, the system also grants `READ METADATA` on the parent schema so the grantee can discover and reference the Volume. Use `SHOW GRANTS TO USER datalake_user` or `SHOW GRANTS TO ROLE volume_reader` to inspect the resulting privileges.

## Remote Function Object Permissions

| Level | Privilege | Purpose |
|---|---|---|
| Schema | `CREATE FUNCTION` | Create a Function in the schema |
| Function | `READ METADATA` | View Function object metadata |
| Function | `USE FUNCTION` | Invoke the specified Function |
| Function | `ALTER FUNCTION` | Alter the specified Function |
| Function | `DROP FUNCTION` | Drop the specified Function |
| Function | `ALL PRIVILEGES` | Grant all privileges on the Function |

Grant `CREATE FUNCTION` only on the parent schema and `DROP FUNCTION` only on a specific Function. The `FUNCTION` suffix in a Function privilege name is optional, but the full privilege name is recommended in documentation and operational scripts.

### Grant Permission to Use a Remote Function

The following command allows user `datalake_user` to invoke `public.fc_image_2_text`:

```sql
GRANT USE FUNCTION ON FUNCTION public.fc_image_2_text TO USER datalake_user;
```

This privilege only allows the user to invoke an existing Function. To create Functions, the user also needs `CREATE FUNCTION` on the parent schema:

```sql
GRANT CREATE FUNCTION ON SCHEMA public TO USER datalake_user;
```
