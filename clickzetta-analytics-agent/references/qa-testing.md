# QA Testing — Sessions & Natural Language Queries

## Session Management

### Create a Named Session

```bash
cz-cli analytics-agent session create \
  --profile <profile> \
  --domain-id <domain-id> \
  --title "车联网QA测试"
# Returns: sessionId (e.g., 6731)
```

Always use `--title` for traceability. Session maintains conversation context — the agent remembers previous questions within the same session.

### Run a Query

```bash
cz-cli analytics-agent session run \
  --profile <profile> \
  --domain-id <domain-id> \
  --session-id <session-id> \
  --msg "总行驶里程是多少？" \
  --model-name "Qwen3.7 Max" \
  --summary \
  --timeout-ms 180000
```

**Both `--domain-id` and `--session-id` are required** for `session run`. Omitting `--domain-id` causes a `USAGE_ERROR`.

### Options

| Option | Description | Recommendation |
|---|---|---|
| `--model-name` | LLM model | `"Qwen3.7 Max"` for Chinese-domain analytical queries |
| `--summary` | Return final answer only | Always use for testing; omit for debugging |
| `--timeout-ms` | Polling timeout (ms) | `180000` (3 min) for complex queries; `120000` for simple |
| `--model-setting` | `KEY=VALUE` pairs | `--model-setting thinkingLevel=off --model-setting language=zh-CN` |

### Session Operations

```bash
# List sessions
cz-cli analytics-agent session list --profile <profile> --domain-id <domain-id>

# Stop a running query
cz-cli analytics-agent session stop <session-id> <question-id> --profile <profile>

# Get result for a specific question
cz-cli analytics-agent session result <question-id> --profile <profile>
```

## QA Testing Strategy

### Must Test (Serial Order)

Run questions **serially** — the next question must wait for the previous to complete. The agent maintains session context and concurrent questions may cause context corruption.

1. **Simple metric query**: `"总行驶里程是多少？"` → validates basic aggregation
2. **AB matching**: `"各车型行驶里程排名"` → validates Answer Builder triggering
3. **Multi-alias**: `"不同品牌跑了多少趟"` → validates Chinese alias matching
4. **Time range**: `"2026年6月行驶了多少公里"` → validates date filtering
5. **Multi-dimension**: `"各品牌行驶次数、总里程、平均速度"` → validates complex analysis
6. **Chart-specific**: `"各月行驶里程趋势"` (line), `"能源类型占比"` (pie)

### Chart Type Coverage

Test queries that produce data suitable for different chart types:

| Chart | Example Query | Expected Data Shape |
|---|---|---|
| 指标卡 | `"6月行驶了多少公里"` | Single value + trend |
| 柱状图 | `"各车型行驶里程排名"` | Category × Value, sorted |
| 折线图 | `"各月行驶里程趋势"` | Time × Value series |
| 饼图 | `"能源类型占比"` | Category × Percentage |
| 堆叠柱状图 | `"各月各驾驶模式里程"` | Time × Stacked categories |
| 散点图 | `"行驶里程和能耗对比"` | X × Y, colored by group |
| 雷达图 | `"各品牌四维度排名"` | Entity × Multi-axis |
| 瀑布图 | `"各月环比增减量"` | Sequential build-up/break-down |
| 桑基图 | `"区域间行驶流动"` | Source → Target flow |
| 气泡图 | `"里程、能耗、次数三维对比"` | X × Y × Size |

### Expected Response Format

Successful QA responses have:
- A summary conclusion header
- Data table with clear headers
- Business insights section
- Optional: warning notes for incomplete data
- Footer: "本次分析未使用外部信息" (no external KB triggered)

### Common QA Failures

| Symptom | Typical Cause |
|---|---|
| `Task execution failed` (~3s) | Query planning error (bad JOIN, unsupported aggregation) |
| Wrong column in SQL (visible in debug mode) | Column name mismatch between agent's knowledge and actual schema |
| Empty query plan | Agent couldn't map the question to available tables/metrics |
| Time-based question fails | Relative time ("上个月") not supported; use explicit dates ("2026年6月") |
| Consecutive failures after working | Session corruption; create new session |

## Testing Checklist

QA-focused checks below. For the full domain delivery checklist see [troubleshooting.md](troubleshooting.md#delivery-checklist); for semantic-quality scoring see [quality-assessment.md](quality-assessment.md).

After building a domain, verify QA quality:

- [ ] Simple metric query returns correct aggregate value
- [ ] AB matching triggers appropriate Answer Builder
- [ ] Chinese aliases are recognized in natural language questions
- [ ] Date-filtered queries return correct date-scoped results
- [ ] Multi-dimension analysis produces meaningful breakdown
- [ ] At least one chart-type query produces properly structured data
- [ ] Domain prompt influences the analysis style and domain knowledge
