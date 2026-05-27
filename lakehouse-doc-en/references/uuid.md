## Function

The `uuid()` function is used to generate a globally unique identifier (UUID), which is a 36-character long string that conforms to common standards. UUID is a widely used identification method in distributed systems, ensuring that UUID values generated at different times and in different systems are unique.

## Syntax
```
uuid()
```
## Return Value

This function returns a UUID of string type, formatted as `8-4-4-4-12`, for example: `123e4567-e89b-12d3-a456-426614174000`.

## Usage Example

Here are some examples of using the `uuid()` function:

1. Generate a UUID and use it as the ID for a new record:
   ```SQL
   INSERT INTO users (id, username, email) VALUES (uuid(), 'john_doe', 'john@example.com');
   ```
```markdown
2. Use UUID as a unique identifier in queries:
```
   ```SQL
   SELECT * FROM products WHERE id = 'a1b2c3d4-5678-90ab-cdef-1234567890ab';
   ```
3. Generate a unique tracking code for each order:
   ```SQL
   UPDATE orders SET tracking_number = uuid() WHERE status = 'pending';
   ```
4. When creating a new log entry, use UUID as the unique identifier for the log:
   ```SQL
   INSERT INTO logs (log_id, user_id, action, timestamp) VALUES (uuid(), 123, 'login', NOW());
   ```
## Notes

- The generation of UUID values depends on specific algorithms, so different database systems may generate UUIDs in different formats.
- When using UUID as the primary key for database tables, be aware of its performance impact, as the generation of UUIDs is usually random and may lead to uneven data distribution.
- Although UUIDs have extremely high uniqueness, they may not be suitable in certain scenarios, such as business logic that requires ordered processing.