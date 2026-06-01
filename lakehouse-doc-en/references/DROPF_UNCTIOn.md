# DROP FUNCTION

Delete the external function in the current or specified schema.

Related functions: [CREATE CONNECTION](createconnection.md), [CREATE EXTERNAL FUNCTION](create_external_function.md), [SHOW EXTERNAL FUNCTION](showfunctions.md)

### Syntax

```
DROP FUNCTION <function_name>;
```

### Parameter Description

\<function\_name> ：The specified external function name

^

### Usage Notes:

* The deleted function cannot be recovered, it can only be recreated.
* Deleting a function will not clean up the function code & executable files stored in object storage.

### Example:

Delete the external function ext\_to\_upper

```
drop function ext_to_upper;
```

^
