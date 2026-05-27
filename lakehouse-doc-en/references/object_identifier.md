# Lakehouse Object Naming Rules

In Lakehouse, to ensure consistency and readability of metadata (such as databases, tables, views, users, etc.) and to avoid potential issues, we have established a set of naming rules. This document will detail these rules to help you better understand and use Lakehouse.

## Identifier Types

Lakehouse supports the following types of identifier naming:

* **Regular Identifiers**: Do not require quotes but must follow specific naming rules.
* **Double-quoted Identifiers**: Need to be enclosed in double quotes (") and can translate keywords.
* **Backtick Identifiers**: Need to be enclosed in backticks (\`), can contain any character but cannot contain backticks themselves. The default is backticks, but it can be switched to double quotes by setting (set `cz.sql.double.quoted.identifiers=true`).

## Naming Rules

### Naming Conventions for Regular Identifiers

1. **Starting Character**: Identifiers must start with a letter (including uppercase A-Z, lowercase a-z) or an underscore ("_"). They cannot start with a number or other special characters.
2. **Character Composition**: Identifiers can only contain letters, underscores, and decimal digits (0-9). Other special characters and keywords, such as hyphens (-), spaces, or other non-alphanumeric characters, are not allowed.
3. **Case Sensitivity**: Although case can be specified when creating, metadata will be parsed as lowercase characters when stored. In Lakehouse, all object names are case-insensitive. This means "MyTable" and "mytable" will be considered the same identifier.
4. **Language Restrictions**: Chinese characters are not supported.
5. **Length Restrictions**: Length is 1 to 255 characters, WORKSPACE NAME length is limited to 3 to 28 characters.

Below are some examples of valid identifiers:
```SQL
my_table
table1
table_2
```
### Backtick Identifiers

If backticks are added when naming objects, the following rules apply:

* Users are allowed to use keywords.
* Column names can include special characters such as Chinese.
For identifier names that need to use keywords, you can surround them with double quotes or backticks, for example:
```SQL
-- Allow numbers
create schema `123`
-- Use keywords as object names
create schema `select`

```
Please note that backticks can be used to enclose identifiers, but their behavior may differ in certain situations. Generally, it is recommended to use backticks only when necessary.

### Double-Quoted Identifiers

In the ANSI/ISO standard for SQL, identifiers within double quotes (delimited identifiers) allow users to use keywords. Lakehouse is also compatible with this behavior. When enabled, double quotes act as delimiters for identifiers by setting `cz.sql.double.quoted.identifiers=true`, currently only supported at the session level. It is important to note that if double quotes are enabled as delimiters for identifiers, Lakehouse will no longer consider data enclosed in double quotes as a string type.
```SQL
"[ ... ]"
```
**Precautions**

* If an object is created using double-quote identifiers, when referencing the object in queries or any other SQL statements, if it is a keyword, the identifier must be exactly as specified during creation, including the double quotes. Omitting the double quotes may result in errors.
```SQL
--Need to use keywords as object names
create schema "select"
```
# Naming Conventions for Various Objects
## Instance INSTANCE NAME

|     | Constraint       | Constraint Conditions                                                  |
| ---- | -------- | ----------------------------------------------------- |
| Name Rule | Naming Rule     | System-generated. Starts with a letter (A-Z, a-z) or underscore ("_"). Uppercase letters are converted to lowercase. |
|      | Length Limit     | Length of 3\~28 characters                                           |
|      | Special Characters Support | Contains only letters, underscores, and decimal digits (0-9), no spaces allowed                         |
|      | Chinese Support   | Not supported                                                   |
|      | Reserved Words   | No reserved words                                                  |
|      | Repetition Allowance   | Unique identifier for user lakehouse                                      |

## WORKSPACE
|         | Constraint       | Constraint Conditions                              |
| ------- | -------- | --------------------------------- |
| Name Rule    | Naming Rule     | Starts with a letter (A-Z, a-z) or underscore ("_"). Uppercase letters are converted to lowercase. |
|         | Length Limit     | Length of 3\~28 characters                       |
|         | Special Characters Support | Contains only letters, underscores, and decimal digits (0-9), no spaces allowed     |
|         | Chinese Support   | Not supported                               |
|         | Reserved Words   | Reserved word: sys                            |
|         | Repetition Allowance   | Not allowed to repeat within the current instance                       |
| COMMENT | Naming Rule     | Starts with a letter or Chinese character                          |
|         | Length Limit     | Length cannot exceed 1024 characters,                    |
|         | Special Characters Support | Contains only letters, underscores, and decimal digits (0-9), spaces allowed in between    |
|         | Chinese Support   | Yes                                 |
|         | Case Sensitivity  | Distinguished                                |

## SCHEMA
|         | Constraint       | Constraint Conditions                              |
| ------- | -------- | --------------------------------- |
| Name Rule    | Naming Rule     | Starts with a letter (A-Z, a-z) or underscore ("_"). Uppercase letters are converted to lowercase. |
|         | Length Limit     | Maximum length of 1-256 characters                     |
|         | Special Characters Support | Contains only letters, underscores, and decimal digits (0-9), no spaces allowed     |
|         | Chinese Support   | Not supported                               |
|         | Reserved Words   | Reserved words: information_schema, public   |
|         | Repetition Allowance   | Not allowed to repeat within the current WORKSPACE and with volume   |
| COMMENT | Naming Rule     | Starts with a letter or Chinese character                          |
|         | Length Limit     | 1024 characters                            |
|         | Special Characters Support | Contains letters, Chinese characters, underscores, and decimal digits (0-9)            |
|         | Chinese Support   | Yes                                 |
|         | Case Sensitivity  | Distinguished                                |

## TABLE
|         | Constraint       | Constraint Conditions                              |
| ------- | -------- | --------------------------------- |
| Name Rule    | Naming Rule     | Starts with a letter (A-Z, a-z) or underscore ("_"). Uppercase letters are converted to lowercase. |
|         | Length Limit     | Maximum length of 1-256 characters                     |
|         | Special Characters Support | Contains only letters, underscores, and decimal digits (0-9), no spaces allowed     |
|         | Chinese Support   | Not supported                               |
|         | Repetition Allowance   | Not allowed to repeat within the current schema                   |
| COMMENT | Naming Rule     | Starts with a letter or Chinese character                          |
|         | Length Limit     | 1024 characters                            |
|         | Special Characters Support | Contains letters, Chinese characters, underscores, and decimal digits (0-9), spaces allowed    |
|         | Chinese Support   | Yes                                 |
|         | Case Sensitivity  | Distinguished                                |

## VIEW
|         | Constraint       | Constraint Conditions                              |
| ------- | -------- | --------------------------------- |
| Name Rule    | Naming Rule     | Starts with a letter (A-Z, a-z) or underscore ("_"). Uppercase letters are converted to lowercase. |
|         | Length Limit     | Maximum length of 1-256 characters                     |
|         | Special Characters Support | Contains only letters, underscores, and decimal digits (0-9), no spaces allowed     |
|         | Chinese Support   | Not supported                               |
|         | Repetition Allowance   | Not allowed to repeat within the current schema                   |
| COMMENT | Naming Rule     | Starts with a letter or Chinese character                          |
|         | Length Limit     | 1024 characters                            |
|         | Special Characters Support | Contains letters, Chinese characters, underscores, and decimal digits (0-9), spaces allowed    |
|         | Chinese Support   | Yes                                 |
|         | Case Sensitivity  | Distinguished                                |

## VIRTUAL CLUSTER

|         | Constraint       | Constraint Conditions                              |
| ------- | -------- | --------------------------------- |
| Name Rule    | Naming Rule     | Starts with a letter (A-Z, a-z) or underscore ("_"). Uppercase letters are converted to lowercase. |
|         | Length Limit     | Maximum length of 1-256 characters                     |
|         | Special Characters Support | Contains only letters, underscores, and decimal digits (0-9), no spaces allowed     |
|         | Chinese Support   | Not supported                               |
|         | Repetition Allowance   | Not repeated within the current workspace                   |
| COMMENT | Naming Rule     | Starts with a letter or Chinese character                          |
|         | Length Limit     | 1024 characters                            |
|         | Special Characters Support | Contains letters, Chinese characters, underscores, and decimal digits (0-9), spaces allowed    |
|         | Chinese Support   | Yes                                 |
|         | Case Sensitivity  | Distinguished                                |

## COLUMN

|         | Constraint       | Constraint Conditions                              |
| ------- | -------- | --------------------------------- |
| Name Rule    | Naming Rule     | Starts with a letter (A-Z, a-z) or underscore ("_"). Uppercase letters are converted to lowercase. |
|         | Length Limit     | Maximum length of 1-256 characters                     |
|         | Special Characters Support | Contains only letters, underscores, and decimal digits (0-9), no spaces allowed     |
|         | Chinese Support   | Supported                               |
|         | Reserved Words   | Has reserved words                              |
|         | Repetition Allowance   | Not allowed to repeat within the current table                        |
| COMMENT | Naming Rule     | Starts with a letter or Chinese character                          |
|         | Length Limit     | 1024 characters                            |
|         | Special Characters Support | Contains letters, Chinese characters, underscores, and decimal digits (0-9), spaces allowed    |
|         | Chinese Support   | Yes                                 |
|         | Case Sensitivity  | Distinguished                                |

## VOLUME
|         | Constraint       | Constraint Conditions                              |
| ------- | -------- | --------------------------------- |
| Name Rule    | Naming Rule     | Starts with a letter (A-Z, a-z) or underscore ("_"). Uppercase letters are converted to lowercase. |
|         | Length Limit     | Maximum length of 1-256 characters                     |
|         | Special Characters Support | Contains only letters, underscores, and decimal digits (0-9), no spaces allowed     |
|         | Chinese Support   | Not supported                               |
|         | Reserved Words   | Has reserved words                              |
|         | Repetition Allowance   | Not repeated within the current workspace, and not allowed to repeat with schema      |
| COMMENT | Naming Rule     | Starts with a letter or Chinese character                          |
|         | Length Limit     | 1024 characters                            |
|         | Special Characters Support | Contains letters, Chinese characters, underscores, and decimal digits (0-9), spaces allowed    |
|         | Chinese Support   | Yes                                 |
|         | Case Sensitivity  | Distinguished                                |

## FUNCTION

|         | Constraint       | Constraint Conditions                                        |
| ------- | -------- | ------------------------------------------- |
| Name Rule    | Naming Rule     | Starts with a letter (A-Z, a-z) or underscore ("_"). Uppercase letters are converted to lowercase, avoid duplication with built-in functions. |
|         | Length Limit     | Maximum length of 1-256 characters                               |
|         | Special Characters Support | Contains only letters, underscores, and decimal digits (0-9), no spaces allowed               |
|         | Chinese Support   | Not supported                                         |
|         | Reserved Words   | Has reserved words                                        |
|         | Repetition Allowance   | Allowed, distinguished by input parameters                              |
| COMMENT | Naming Rule     | Starts with a letter or Chinese character                                    |
|         | Length Limit     | 1024 characters                                      |
|         | Special Characters Support | Contains letters, Chinese characters, underscores, and decimal digits (0-9), spaces allowed               |
|         | Chinese Support   | Yes                                           |
|         | Case Sensitivity  | Distinguished                                          |

## ROLE
|             | Constraint       | Constraint Conditions                              |
| ----------- | -------- | --------------------------------- |
| Name Rule        | Naming Rule     | Starts with a letter (A-Z, a-z) or underscore ("_"). Uppercase letters are converted to lowercase. |
|             | Length Limit     | Maximum length of 1-256 characters                     |
|             | Special Characters Support | Contains only letters, underscores, and decimal digits (0-9), no spaces allowed     |
|             | Chinese Support   | Not supported                               |
|             | Reserved Words   | Has reserved roles                             |
|             | Repetition Allowance   | Allowed                              |
| COMMENT     | Naming Rule     | Starts with a letter or Chinese character                          |
|             | Length Limit     | 1024 characters                            |
|             | Special Characters Support | Contains letters, Chinese characters, underscores, and decimal digits (0-9), spaces allowed    |
|             | Chinese Support   | Yes                                 |
|             | Case Sensitivity  | Distinguished                                |
| ROLE\_ALIAS | Naming Rule     | Starts with a letter or Chinese character                          |
|             | Length Limit     | 1024 characters                            |
|             | Special Characters Support | Contains letters, Chinese characters, underscores, and decimal digits (0-9), spaces allowed    |
|             | Chinese Support   | Yes                                 |
|             | Case Sensitivity  | Not distinguished                               |

## USER
|         | Constraint       | Constraint Conditions                              |
| ------- | -------- | --------------------------------- |
| Name Rule    | Naming Rule     | Starts with a letter (A-Z, a-z) or underscore ("_"). Uppercase letters are converted to lowercase. |
|         | Length Limit     | Maximum length of 1-256 characters                     |
|         | Special Characters Support | Contains only letters, underscores, and decimal digits (0-9), no spaces allowed     |
|         | Chinese Support   | Not supported                               |
|         | Reserved Words   |                                   |
|         | Repetition Allowance   | Not allowed to repeat within the current Account                    |
| COMMENT | Naming Rule     | Starts with a letter or Chinese character                          |
|         | Length Limit     | 1024 characters                            |
|         | Special Characters Support | Contains letters, Chinese characters, underscores, and decimal digits (0-9), spaces allowed    |
|         | Chinese Support   | Yes                                 |
|         | Case Sensitivity  | Distinguished                                |

## INDEX
|         | Constraint       | Constraint Conditions                              |
| ------- | -------- | --------------------------------- |
| Name Rule    | Naming Rule     | Starts with a letter (A-Z, a-z) or underscore ("_"). Uppercase letters are converted to lowercase. |
|         | Length Limit     | Maximum length of 1-256 characters                     |
|         | Special Characters Support | Contains only letters, underscores, and decimal digits (0-9), no spaces allowed     |
|         | Chinese Support   | Not supported                               |
|         | Reserved Words   |                                   |
|         | Repetition Allowance   | Not allowed to repeat within the current schema                     |
| COMMENT | Naming Rule     | Starts with a letter or Chinese character                          |
|         | Length Limit     | 1024 characters                            |
|         | Special Characters Support | Contains letters, Chinese characters, underscores, and decimal digits (0-9), spaces allowed    |
|         | Chinese Support   | Yes                                 |
|         | Case Sensitivity  | Distinguished                                |