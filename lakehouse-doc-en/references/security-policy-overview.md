# Security Policies

Singdata Lakehouse provides multi-layered data security policies to protect data access and transmission security.

| Policy Type | Description | Reference |
|---------|------|---------|
| Network Policy | IP allowlist to restrict access sources | [Network Policy](network_policy.md) |
| Dynamic Masking | Mask sensitive columns (phone numbers, ID numbers, etc.) based on roles | [Dynamic Masking](dynamic-mask.md) |
| Row-Level Permissions | Different users can only see rows within their permission scope | [Row-Level Permissions](row_level_permission.md) |
| User Management | Create and manage user accounts | [User Management](authority-management.md) |
| Role Management | RBAC role system | [Roles](roles.md) |
