# Evaluation filter

`ss preview`, `ss trigger-eval`, and `ss filter-options` take the same JSON object in `--filter`. Use a filter to evaluate live traces; use `--dataset-id` instead to evaluate a dataset. Pass exactly one of the two. Preview and trigger-eval apply identical semantics, so preview with the same filter before triggering.

## Fields

| Field | Type | Meaning |
|---|---|---|
| `time_start`, `time_end` | UTC ISO 8601 string with timezone | `event_time` range (inclusive). Required by preview and trigger-eval; `time_start` must be earlier than `time_end` |
| `date_range_days` | non-negative integer | Last N days (`event_date >= CURRENT_DATE - N`) |
| `has_error` | boolean | `true`: contains an error span; `false`: contains no error span |
| `min_duration_ms` | non-negative number | Minimum span duration |
| `service_name`, `agent_name`, `model_name`, `model_provider`, `platform`, `tool_name`, `span_name`, `span_kind`, `ai_span_kind`, `event_type`, `agent_source`, `operation_name`, `status_code`, `error_type`, `user_id`, `session_id`, `trace_id` | array of values, or `{"none_of": [...]}` | Array: value is one of them. `none_of`: value is none of them (nulls included). 1-100 scalar values |
| `raw_span_attributes` | object `{attribute: value}` | `raw_span_attributes[attribute] = value`; several keys are ANDed |
| `tool_call_args` | object `{json_path: value}` | Tool call argument `$.json_path = value`; several keys are ANDed |

Fields not listed are rejected. `operation_name` is often empty; prefer `span_name` to identify a specific operation. Get candidate values with `ss filter-options --filter '{"time_start": ..., "time_end": ...}'`; each dimension returns up to 100 non-empty values.

## Granularity (`--granularity`)

- `TRACE` (default): a span-level condition means "the trace contains a span that matches". `none_of` and `has_error: false` mean "the trace contains no span that matches".
- `SESSION`: the same, grouped by `session_id`.
- `SPAN`: conditions apply to each span directly.

## Examples

Traces with errors in the `support-agent` service over one day:

```json
{
  "time_start": "2026-11-19T00:00:00Z",
  "time_end": "2026-11-20T00:00:00Z",
  "service_name": ["support-agent"],
  "has_error": true
}
```

Traces that called search tools without using `gpt-4o`:

```json
{
  "time_start": "2026-11-13T00:00:00Z",
  "time_end": "2026-11-20T00:00:00Z",
  "tool_name": ["web_search", "kb_search"],
  "model_name": {"none_of": ["gpt-4o"]}
}
```

Write long filters to a file and pass `--filter @filter.json`, reusing the same file for preview and trigger-eval.
