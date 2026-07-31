# Knowledge Base Management

## Space Lifecycle

### Create

```bash
cz-cli analytics-agent knowledge space create \
  --profile <profile> \
  --name "零售行业知识库" \
  --description "零售行业数据说明、指标口径、分析场景"
# Returns: space id (e.g., 5094)
```

### List

```bash
cz-cli analytics-agent knowledge space list --profile <profile> --format json
```

Response fields: `id`, `name`, `description`, `fileCount`, `domainIds[]`.

### Detail

```bash
cz-cli analytics-agent knowledge folder list <space-id> --profile <profile>
```

## File Upload

The single-step upload command handles file upload, folder creation, and domain binding:

```bash
cz-cli analytics-agent knowledge file upload <space-id> <local-file-path> \
  --profile <profile> \
  --domain-id <domain-id> \
  --target-path "docs/" \
  --name "数据说明文档.md"
```

Options:
- `--target-path`: Remote folder path; intermediate folders auto-created
- `--name`: Remote file name override (defaults to local filename)
- `--domain-id`: Bind to this domain at upload (repeatable)

**Note**: If the space already exists (name collision), `space create` returns an error. Use `knowledge space list` to find existing spaces and reuse them.

### File Operations

```bash
# List files in a space
cz-cli analytics-agent knowledge file list <space-id> --profile <profile>

# Read a file
cz-cli analytics-agent knowledge file get <space-id> <node-id> --profile <profile>

# Delete a file
cz-cli analytics-agent knowledge file delete <space-id> <node-id> --profile <profile>

# Search files by name
cz-cli analytics-agent knowledge file search <space-id> --profile <profile>

# Rename
cz-cli analytics-agent knowledge file rename <space-id> <node-id> --name "新名称.md" --profile <profile>
```

## Domain Binding

Files uploaded with `--domain-id` are automatically bound. To manually bind/unbind:

```bash
# Bind
cz-cli analytics-agent knowledge node bind-domain <space-id> <node-id> \
  --profile <profile> --domain-id <domain-id>

# Unbind
cz-cli analytics-agent knowledge node unbind-domain <space-id> <node-id> \
  --profile <profile> --domain-id <domain-id>
```

## KB Content Guidelines

For an effective knowledge base:

1. **Describe the data scope**: date range, row counts, table purposes
2. **Explain field values**: enumerate status codes, category values, severity levels
3. **Define metric formulas**: show the exact SQL aggregation
4. **List common analysis scenarios**: with example questions
5. **Document business rules**: conversion rates, calculation exceptions

Example KB structure:
```markdown
# 行业分析域 - 数据说明
## 域概述
## 维度表（含关键字段取值）
## 事实表（含行数和说明）
## 关键指标口径
## 常用分析场景
## 注意事项
```
