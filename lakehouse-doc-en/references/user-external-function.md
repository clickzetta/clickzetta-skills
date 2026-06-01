# User-Defined Functions

User-defined functions extend the SQL computation capabilities of Lakehouse. Two types are supported: SQL Function (executed within the engine) and External Function (calls an external service).

For a detailed introduction, see [Function Object Model](function-overview.md).

---

## In This Chapter

### SQL Function

| Page | Description |
|------|-------------|
| [CREATE SQL FUNCTION](create-sql-function.md) | Create a SQL scalar function or table function |
| [DROP FUNCTION](drop-function.md) | Drop a function |
| [DESC FUNCTION](desc-function.md) | View detailed information about a function |
| [SHOW FUNCTIONS](show-functions.md) | List all functions (including built-in functions) |

### External Function

| Page | Description |
|------|-------------|
| [CREATE EXTERNAL FUNCTION](create_external_function.md) | Create a function that calls an external service (Python/Java) |
| [DROP FUNCTION](drop-function.md) | Drop an external function |
| [SHOW EXTERNAL FUNCTIONS](show-external-functions.md) | List all external functions |

---

## Common Operations

```SQL
-- Create a SQL scalar function
CREATE FUNCTION public.area(x DOUBLE, y DOUBLE)
RETURNS DOUBLE
RETURN x * y;

-- Use the function
SELECT public.area(3, 4);  -- Output: 12.0

-- List all functions
SHOW FUNCTIONS;

-- Drop a function
DROP FUNCTION public.area;
```

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [Function Object Model](function-overview.md) | Function type comparison, permission notes, complete examples |
| [External Function Workflow](remotefunction-best-practice.md) | Complete process from development to deployment |
| [SQL Function Reference](functions.md) | Complete list of built-in functions |
