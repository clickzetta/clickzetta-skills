# Data Lake Permission Management

Data Lake Permission Management is an important part of ensuring data security and compliance. Through proper permission management, you can ensure that users can only access and operate the data and resources they need. Permission management in a data lake mainly involves two aspects: data access permissions and function call permissions. Specifically, it includes the following aspects:

1. Permission points and permission management of Volume objects
2. Permission points and permission management of Remote Function objects

## Volume Object Permissions

For Volume objects, you can set the following permissions:

* Permissions of the Schema to which the object belongs: CREATE / DROP
* Permissions of the object itself: READ / WRITE / ALTER

### Example 1: Granting a New User Access to a Volume

Suppose you have a new user named `datalake_user`, and you want to grant them access to the workspace. First, grant the user the workspace\_user role (read-only permission):

```
GRANT ROLE workspace_user TO USER datalake_user;
```

Next, if you want to allow the `datalake_user` to read, upload data, and synchronize file metadata to the Lakehouse metadata service for Volume objects, you need to grant the following permissions:

1. Authorize the use of computing resources Virtual Cluster
2. Grant `datalake_user` READ/WRITE/ALTER permissions on the Volume

The specific steps are as follows:

```SQL
GRANT USE VCLUSTER ON VCLUSTER DEFAULT TO USER datalake_user;
```

```SQL
GRANT READ ON volume xxx TO USER datalake_user;
GRANT WRITE ON volume xxx TO USER datalake_user;
GRANT ALTER ON volume xxx TO USER datalake_user;
```

## Remote Function Object Permissions

For Remote Function objects, you can set the following permissions:

* Permissions of the Schema to which the object belongs: CREATE / DROP
* Permissions of the object itself: USE

### Example 2: Granting a User Permission to Use a Remote Function

Suppose you want to grant the user `datalake_user` permission to use a Remote Function named fc\_image\_2\_text, you can execute the following command:

```SQL
GRANT USE ON FUNCTION fc_image_2_text TO USER datalake_user;
```

^
