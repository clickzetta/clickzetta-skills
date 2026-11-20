#!/usr/bin/env python3
"""SingSight command line for agents: Open API (evaluation / dataset) + cz-cli SQL.

Covers the SingSight tools of the ClickZetta MCP server without needing that server. Uses
only the Python standard library (3.11+ for tomllib).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import stat
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    tomllib = None

DEFAULT_CONFIG_PATH = Path.home() / ".clickzetta" / "singsight.toml"
CACHE_DIR = Path(os.environ.get("SINGSIGHT_CACHE_DIR", Path.home() / ".cache" / "singsight"))
TOKEN_REFRESH_MARGIN_SECONDS = 300
CONTEXT_CACHE_SECONDS = 24 * 60 * 60
HTTP_TIMEOUT_SECONDS = 30

DEFAULT_MAX_BYTES = 48 * 1024
MAX_RESPONSE_ITEMS = 100
MAX_STRING_LENGTH = 4_000
MAX_EVALUATOR_STEPS = 20
MAX_EVALUATOR_STEP_NAME_LENGTH = 100
MAX_EVALUATOR_PROMPT_LENGTH = 20_000
MAX_EVALUATOR_NAME_LENGTH = 100
MAX_EVALUATOR_GROUP_LENGTH = 50
MAX_EVALUATOR_DESCRIPTION_LENGTH = 500
MAX_DATASET_NAME_LENGTH = 128
MAX_DATASET_DESCRIPTION_LENGTH = 1024
MAX_EXPLICIT_TRACE_IDS = 100
CUSTOM_EVALUATOR_FIELDS = {
    "name", "evaluator_group", "description", "evaluator_config",
    "reasoning_prompt", "score_prompt", "score_type", "score_min", "score_max",
}
FILTER_FIELDS = {
    "time_start", "time_end", "date_range_days", "has_error", "min_duration_ms",
    "event_type", "service_name", "agent_name", "model_name", "model_provider",
    "platform", "tool_name", "span_name", "span_kind", "ai_span_kind", "user_id",
    "session_id", "trace_id", "agent_source", "operation_name", "status_code",
    "error_type", "raw_span_attributes", "tool_call_args",
}
DYNAMIC_FILTER_FIELDS = FILTER_FIELDS - {
    "time_start", "time_end", "date_range_days", "has_error", "min_duration_ms",
    "raw_span_attributes", "tool_call_args",
}
DATASET_TAG_PATTERN = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
TRACE_ID_PATTERN = re.compile(r"^[0-9a-fA-F]{16,64}$")
EVAL_TERMINAL_STATUSES = {"COMPLETE", "ERROR", "STOPPED"}
IMPORT_TERMINAL_STATUSES = {"SUCCEEDED", "FAILED"}


class SingSightError(RuntimeError):
    """A user-facing error; printed as JSON on stderr."""

    def __init__(self, message: str, code: str = "SINGSIGHT_ERROR", retryable: bool = False,
                 next_action: str | None = None, exit_code: int = 1):
        super().__init__(message)
        self.code = code
        self.retryable = retryable
        self.next_action = next_action
        self.exit_code = exit_code


def _invalid(message: str) -> SingSightError:
    return SingSightError(message, code="INVALID_ARGUMENT", exit_code=2)


# ---------------------------------------------------------------- config

def load_project(config_path: str | None, project: str | None) -> dict:
    path = Path(config_path or os.environ.get("SINGSIGHT_CONFIG") or DEFAULT_CONFIG_PATH).expanduser()
    if tomllib is None:
        raise SingSightError("Python 3.11+ is required (tomllib).", code="UNSUPPORTED_PYTHON")
    if not path.is_file():
        raise SingSightError(
            f"SingSight config not found: {path}",
            code="SINGSIGHT_NOT_CONFIGURED",
            next_action="Create it from references/config.example.toml in the singsight-operate skill.",
        )
    with path.open("rb") as fh:
        try:
            config = tomllib.load(fh)
        except tomllib.TOMLDecodeError as exc:
            raise SingSightError(f"Invalid TOML in {path}: {exc}", code="INVALID_CONFIGURATION") from exc
    projects = config.get("projects") or {}
    name = project or os.environ.get("SINGSIGHT_PROJECT") or config.get("default_project")
    if not name and len(projects) == 1:
        name = next(iter(projects))
    if not name or name not in projects:
        raise SingSightError(
            f"SingSight project not found in {path}: {name or '(none)'}; available: {', '.join(projects) or '(none)'}",
            code="SINGSIGHT_NOT_CONFIGURED",
            next_action="Pass --project NAME or set default_project.",
        )
    settings = dict(projects[name])
    settings["name"] = name
    settings["config_path"] = str(path)
    if settings.get("api_key_env"):
        settings["api_key"] = os.environ.get(settings["api_key_env"], "").strip()
    elif settings.get("api_key"):
        mode = path.stat().st_mode
        if mode & (stat.S_IRGRP | stat.S_IROTH):
            print(f"warning: {path} holds an api_key and is readable by other users; run chmod 600 {path}",
                  file=sys.stderr)
    settings["base_url"] = str(settings.get("base_url") or "").rstrip("/")
    if not settings["base_url"] or not settings.get("api_key"):
        raise SingSightError(
            f"Project {name} needs base_url and api_key (or api_key_env).",
            code="SINGSIGHT_NOT_CONFIGURED",
        )
    if not settings["base_url"].startswith(("https://", "http://")):
        raise SingSightError("base_url must be an http(s) URL.", code="INVALID_CONFIGURATION")
    return settings


# ---------------------------------------------------------------- Open API client

def _cache_file(prefix: str, settings: dict) -> Path:
    digest = hashlib.sha256(f"{settings['base_url']}|{settings['api_key']}".encode("utf-8")).hexdigest()[:32]
    return CACHE_DIR / f"{prefix}-{digest}.json"


def _read_cache(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _write_private(path: Path, text: str) -> None:
    """Write a file only the current user can read; tokens and trace content live here."""
    path.parent.mkdir(parents=True, exist_ok=True)
    for directory in {CACHE_DIR, path.parent}:
        os.chmod(directory, 0o700)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(text)


def _write_cache(path: Path, value: dict) -> None:
    _write_private(path, json.dumps(value))


def _parse_expiry(value: Any) -> float:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value) / 1000 if value > 10_000_000_000 else float(value)
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
        except ValueError:
            pass
    return time.time() + 23 * 60 * 60


class SingSightClient:
    def __init__(self, settings: dict):
        self.settings = settings
        self.base_url = settings["base_url"]
        self.api_key = settings["api_key"]
        self.token_cache = _cache_file("token", settings)

    def _http(self, method: str, url: str, headers: dict, body: bytes | None) -> tuple[int, Any]:
        request = urllib.request.Request(url, data=body, method=method, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
                status, raw = response.status, response.read()
        except urllib.error.HTTPError as exc:
            with exc:
                status, raw = exc.code, exc.read()
        except TimeoutError as exc:
            raise SingSightError("SingSight request timed out.", code="UPSTREAM_TIMEOUT", retryable=True,
                                 next_action="Retry with a narrower time range or filter.") from exc
        except urllib.error.URLError as exc:
            raise SingSightError(f"SingSight service is unavailable: {exc.reason}", code="UPSTREAM_UNAVAILABLE",
                                 retryable=True,
                                 next_action="Retry after checking network connectivity and service health.") from exc
        try:
            return status, json.loads(raw.decode("utf-8")) if raw else None
        except ValueError as exc:
            raise SingSightError(f"SingSight returned invalid JSON (HTTP {status}).",
                                 code="UPSTREAM_INVALID_RESPONSE", retryable=status >= 500) from exc

    @staticmethod
    def _decode(status: int, payload: Any) -> Any:
        if status >= 400:
            message = payload.get("message") if isinstance(payload, dict) else None
            code = (payload.get("code") or payload.get("errorCode")) if isinstance(payload, dict) else None
            raise SingSightError(
                message or f"SingSight request failed (HTTP {status}).",
                code=str(code or f"HTTP_{status}"),
                retryable=status >= 500 or status == 429,
                next_action="Retry after the upstream service recovers." if status >= 500 else None,
            )
        if isinstance(payload, dict) and payload.get("success") is False:
            raise SingSightError(
                payload.get("message") or "SingSight request failed.",
                code=str(payload.get("code") or payload.get("errorCode") or "SINGSIGHT_ERROR"),
                retryable=bool(payload.get("retryable", False)),
                next_action=payload.get("next_action") or payload.get("nextAction"),
            )
        return payload.get("data") if isinstance(payload, dict) and "data" in payload else payload

    def _token(self, force_refresh: bool = False) -> str:
        cached = None if force_refresh else _read_cache(self.token_cache)
        if cached and cached.get("expires_at", 0) - TOKEN_REFRESH_MARGIN_SECONDS > time.time():
            return cached["token"]
        query = urllib.parse.urlencode({"appSecretKey": self.api_key})
        status, payload = self._http("GET", f"{self.base_url}/open/api/v1/appSecretKey/generateAuthToken?{query}",
                                     {"Accept": "application/json"}, None)
        data = self._decode(status, payload)
        token = data.get("token") if isinstance(data, dict) else None
        if not token:
            raise SingSightError("SingSight token exchange returned no token.", code="UPSTREAM_AUTH_ERROR",
                                 retryable=True,
                                 next_action="Retry; if it persists, verify the key is an Access (not Ingest) key.")
        _write_cache(self.token_cache, {"token": token, "expires_at": _parse_expiry(data.get("expiresAt"))})
        return token

    def request(self, method: str, path: str, params: dict | None = None, body: Any = None) -> Any:
        url = f"{self.base_url}{path}"
        if params:
            query = {k: v for k, v in params.items() if v is not None}
            if query:
                url = f"{url}?{urllib.parse.urlencode(query)}"
        data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
        headers = {"Accept": "application/json"}
        if data is not None:
            headers["Content-Type"] = "application/json"
        headers["Authorization"] = f"Bearer {self._token()}"
        status, payload = self._http(method, url, headers, data)
        if status == 401:
            headers["Authorization"] = f"Bearer {self._token(force_refresh=True)}"
            status, payload = self._http(method, url, headers, data)
        return self._decode(status, payload)

    def schema_context(self, use_cache: bool = True) -> Any:
        cache = _cache_file("context", self.settings)
        cached = _read_cache(cache) if use_cache else None
        if cached and cached.get("fetched_at", 0) + CONTEXT_CACHE_SECONDS > time.time():
            return cached["data"]
        data = self.request("GET", "/open/api/v1/mcp/schema-context")
        _write_cache(cache, {"fetched_at": time.time(), "data": data})
        return data


# ---------------------------------------------------------------- validation (same rules as the MCP tools)

def _parse_utc(value: Any, field: str) -> datetime:
    if not isinstance(value, str):
        raise _invalid(f"{field} must be a UTC ISO 8601 string.")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise _invalid(f"{field} must be a UTC ISO 8601 string.") from exc
    if parsed.tzinfo is None:
        raise _invalid(f"{field} must include a timezone.")
    return parsed


def validate_filter(filter_value: Any, require_time: bool = False) -> dict:
    if not isinstance(filter_value, dict):
        raise _invalid("filter must be a JSON object.")
    unknown = sorted(set(filter_value) - FILTER_FIELDS)
    if unknown:
        raise _invalid(f"filter contains unsupported fields: {', '.join(unknown)}")
    if require_time and (not filter_value.get("time_start") or not filter_value.get("time_end")):
        raise _invalid("filter.time_start and filter.time_end are required.")
    parsed = {f: _parse_utc(filter_value[f], f) for f in ("time_start", "time_end") if filter_value.get(f) is not None}
    if len(parsed) == 2 and parsed["time_start"] >= parsed["time_end"]:
        raise _invalid("time_start must be earlier than time_end.")
    days = filter_value.get("date_range_days")
    if "date_range_days" in filter_value and (not isinstance(days, int) or isinstance(days, bool) or days < 0):
        raise _invalid("date_range_days must be a non-negative integer.")
    if "has_error" in filter_value and not isinstance(filter_value["has_error"], bool):
        raise _invalid("has_error must be a boolean.")
    duration = filter_value.get("min_duration_ms")
    if "min_duration_ms" in filter_value and (
            not isinstance(duration, (int, float)) or isinstance(duration, bool) or duration < 0):
        raise _invalid("min_duration_ms must be a non-negative number.")
    for field in DYNAMIC_FILTER_FIELDS & set(filter_value):
        value = filter_value[field]
        if not isinstance(value, list) and not (
                isinstance(value, dict) and set(value) == {"none_of"} and isinstance(value["none_of"], list)):
            raise _invalid(f"filter.{field} must be a list or {{\"none_of\": [...]}}.")
        values = value if isinstance(value, list) else value["none_of"]
        if not values or len(values) > MAX_RESPONSE_ITEMS or any(
                not isinstance(item, (str, int, float, bool)) for item in values):
            raise _invalid(f"filter.{field} must contain 1-{MAX_RESPONSE_ITEMS} scalar values.")
        if any(isinstance(item, str) and len(item) > MAX_STRING_LENGTH for item in values):
            raise _invalid(f"filter.{field} string values must be at most {MAX_STRING_LENGTH} characters.")
    for field in ("raw_span_attributes", "tool_call_args"):
        if field not in filter_value:
            continue
        value = filter_value[field]
        if not isinstance(value, dict) or len(value) > MAX_RESPONSE_ITEMS:
            raise _invalid(f"filter.{field} must be an object with at most {MAX_RESPONSE_ITEMS} entries.")
        for key, item in value.items():
            if not key or len(key) > MAX_STRING_LENGTH:
                raise _invalid(f"filter.{field} keys must be non-empty strings of at most {MAX_STRING_LENGTH} characters.")
            if not isinstance(item, (str, int, float, bool)):
                raise _invalid(f"filter.{field} values must be scalar values.")
            if isinstance(item, str) and len(item) > MAX_STRING_LENGTH:
                raise _invalid(f"filter.{field} values must be at most {MAX_STRING_LENGTH} characters.")
    return filter_value


def _eval_source(filter_value: Any, dataset_id: int | None) -> dict:
    """Exactly one evaluation source: a live-trace filter or a dataset snapshot."""
    if (filter_value is None) == (dataset_id is None):
        raise _invalid("Provide exactly one of --filter (live traces) or --dataset-id (dataset snapshot).")
    if dataset_id is not None:
        return {"datasetId": dataset_id}
    return {"filter": validate_filter(filter_value, require_time=True)}


def validate_custom_evaluator(spec: Any) -> dict:
    """Validate the snake_case evaluator spec and translate it to Open API JSON."""
    if not isinstance(spec, dict):
        raise _invalid("evaluator spec must be a JSON object.")
    unknown = sorted(set(spec) - CUSTOM_EVALUATOR_FIELDS)
    if unknown:
        raise _invalid(f"unsupported fields: {', '.join(unknown)}")
    name = spec.get("name")
    if not isinstance(name, str) or not name.strip():
        raise _invalid("name is required and must be a non-empty string.")
    name = name.strip()
    if len(name) > MAX_EVALUATOR_NAME_LENGTH:
        raise _invalid(f"name must be at most {MAX_EVALUATOR_NAME_LENGTH} characters.")
    config = spec.get("evaluator_config")
    if not isinstance(config, dict):
        raise _invalid("evaluator_config is required and must be an object.")
    unknown = sorted(set(config) - {"step_prompts"})
    if unknown:
        raise _invalid(f"evaluator_config contains unsupported fields: {', '.join(unknown)}")
    steps = config.get("step_prompts")
    if not isinstance(steps, list) or not 1 <= len(steps) <= MAX_EVALUATOR_STEPS:
        raise _invalid(f"evaluator_config.step_prompts must contain 1-{MAX_EVALUATOR_STEPS} steps.")
    normalized_steps, seen = [], set()
    for index, item in enumerate(steps, start=1):
        if not isinstance(item, dict) or set(item) != {"step", "prompt"}:
            raise _invalid(f"step_prompts[{index}] must contain only step and prompt.")
        step, prompt = item["step"], item["prompt"]
        if not isinstance(step, str) or not step.strip():
            raise _invalid(f"step_prompts[{index}].step must be a non-empty string.")
        step = step.strip()
        if len(step) > MAX_EVALUATOR_STEP_NAME_LENGTH:
            raise _invalid(f"step_prompts[{index}].step must be at most {MAX_EVALUATOR_STEP_NAME_LENGTH} characters.")
        if step in seen:
            raise _invalid(f"step_prompts contains duplicate step: {step}")
        if not isinstance(prompt, str) or not prompt.strip():
            raise _invalid(f"step_prompts[{index}].prompt must be a non-empty string.")
        if len(prompt) > MAX_EVALUATOR_PROMPT_LENGTH:
            raise _invalid(f"step_prompts[{index}].prompt must be at most {MAX_EVALUATOR_PROMPT_LENGTH} characters.")
        seen.add(step)
        normalized_steps.append({"step": step, "prompt": prompt})
    score_type = spec.get("score_type", "NUMERIC")
    if score_type not in {"NUMERIC", "BOOLEAN", "INTEGER"}:
        raise _invalid("score_type must be NUMERIC, BOOLEAN or INTEGER.")
    score_min, score_max = spec.get("score_min", 0.0), spec.get("score_max", 1.0)
    for field, value in (("score_min", score_min), ("score_max", score_max)):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise _invalid(f"{field} must be a finite number.")
    if score_min >= score_max:
        raise _invalid("score_min must be less than score_max.")
    payload = {
        "name": name,
        "evaluatorConfig": {"stepPrompts": normalized_steps},
        "scoreType": score_type,
        "scoreMin": score_min,
        "scoreMax": score_max,
    }
    group = spec.get("evaluator_group")
    if group is not None:
        if not isinstance(group, str) or not group.strip():
            raise _invalid("evaluator_group must be a non-empty string when provided.")
        if len(group.strip()) > MAX_EVALUATOR_GROUP_LENGTH:
            raise _invalid(f"evaluator_group must be at most {MAX_EVALUATOR_GROUP_LENGTH} characters.")
        payload["evaluatorGroup"] = group.strip()
    description = spec.get("description")
    if description is not None:
        if not isinstance(description, str) or len(description) > MAX_EVALUATOR_DESCRIPTION_LENGTH:
            raise _invalid(f"description must be a string of at most {MAX_EVALUATOR_DESCRIPTION_LENGTH} characters.")
        payload["description"] = description
    for source, target in (("reasoning_prompt", "reasoningPrompt"), ("score_prompt", "scorePrompt")):
        value = spec.get(source)
        if value is not None:
            if not isinstance(value, str) or len(value) > MAX_EVALUATOR_PROMPT_LENGTH:
                raise _invalid(f"{source} must be a string of at most {MAX_EVALUATOR_PROMPT_LENGTH} characters.")
            payload[target] = value
    return payload


def validate_dataset(name: str, tag: str | None, description: str | None) -> dict:
    if not name or not name.strip():
        raise _invalid("--name must be a non-empty string.")
    if len(name.strip()) > MAX_DATASET_NAME_LENGTH:
        raise _invalid(f"--name must be at most {MAX_DATASET_NAME_LENGTH} characters.")
    payload = {"name": name.strip()}
    if tag is not None:
        if not DATASET_TAG_PATTERN.match(tag):
            raise _invalid("--tag must start with a lowercase letter and contain only lowercase letters, "
                           "digits and underscores (max 64).")
        payload["datasetTag"] = tag
    if description is not None:
        if len(description) > MAX_DATASET_DESCRIPTION_LENGTH:
            raise _invalid(f"--description must be at most {MAX_DATASET_DESCRIPTION_LENGTH} characters.")
        payload["description"] = description
    return payload


def validate_add_traces(args: argparse.Namespace) -> dict:
    """Build the Open API ImportRequest; exactly one source."""
    has_job, has_ids = args.eval_job_id is not None, args.trace_ids is not None
    if has_job == has_ids:
        raise _invalid("Provide exactly one of --eval-job-id (preferred) or --trace-ids.")
    if has_job:
        if args.time_start or args.time_end:
            raise _invalid("--time-start/--time-end only apply to --trace-ids.")
        scope = args.job_scope or "RESULTS"
        payload: dict[str, Any] = {"evalJobId": args.eval_job_id, "jobScope": scope}
        if (args.min_score is not None or args.max_score is not None) and scope != "RESULTS":
            raise _invalid("--min-score/--max-score require --job-scope RESULTS.")
        for value, field in ((args.min_score, "min_score"), (args.max_score, "max_score")):
            if value is not None and not math.isfinite(value):
                raise _invalid(f"{field} must be a finite number.")
        if args.min_score is not None and args.max_score is not None and args.min_score > args.max_score:
            raise _invalid("--min-score must not exceed --max-score.")
        if args.min_score is not None:
            payload["minScore"] = args.min_score
        if args.max_score is not None:
            payload["maxScore"] = args.max_score
        return payload
    if args.job_scope or args.min_score is not None or args.max_score is not None:
        raise _invalid("--job-scope/--min-score/--max-score only apply to --eval-job-id.")
    ids = []
    for value in args.trace_ids:
        value = value.strip()
        if not TRACE_ID_PATTERN.match(value):
            raise _invalid(f"invalid trace id {value!r}: must be 16-64 hexadecimal characters.")
        if value not in ids:
            ids.append(value)
    if not 1 <= len(ids) <= MAX_EXPLICIT_TRACE_IDS:
        raise _invalid(f"--trace-ids must contain 1-{MAX_EXPLICIT_TRACE_IDS} ids; for larger sets use --eval-job-id.")
    payload = {"traceIds": ids}
    parsed = {}
    for value, field, target in ((args.time_start, "time_start", "timeStart"), (args.time_end, "time_end", "timeEnd")):
        if value:
            parsed[field] = _parse_utc(value, field)
            payload[target] = value
    if len(parsed) == 2 and parsed["time_start"] >= parsed["time_end"]:
        raise _invalid("--time-start must be earlier than --time-end.")
    return payload


# ---------------------------------------------------------------- output

def _bound(value: Any) -> tuple[Any, bool]:
    """Cap list/dict sizes and string lengths so results fit an agent context."""
    if isinstance(value, str):
        if len(value) <= MAX_STRING_LENGTH:
            return value, False
        return value[:MAX_STRING_LENGTH] + "… [truncated]", True
    if isinstance(value, (list, dict)):
        items = list(value.items()) if isinstance(value, dict) else list(enumerate(value))
        truncated = len(items) > MAX_RESPONSE_ITEMS
        bounded = {} if isinstance(value, dict) else []
        for key, item in items[:MAX_RESPONSE_ITEMS]:
            item_value, item_truncated = _bound(item)
            truncated = truncated or item_truncated
            if isinstance(bounded, dict):
                bounded[key] = item_value
            else:
                bounded.append(item_value)
        return bounded, truncated
    return value, False


def _dump(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, default=str)


def emit(data: Any, command: str, max_bytes: int, full: bool) -> None:
    bounded, truncated = (data, False) if full else _bound(data)
    payload: dict[str, Any] = {"success": True, "data": bounded}
    if truncated:
        payload["truncated"] = True
        payload["next_action"] = "Narrow the filter/page, or rerun with --full to write everything to a file."
    text = _dump(payload)
    if full or len(text.encode("utf-8")) > max_bytes:
        out_file = CACHE_DIR / "out" / f"{command}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}.json"
        _write_private(out_file, json.dumps(data, ensure_ascii=False, indent=2, default=str))
        text = _dump({
            "success": True,
            "output_file": str(out_file),
            "bytes": out_file.stat().st_size,
            "next_action": "Inspect the file with jq/grep instead of printing it whole.",
        })
    print(text)


def emit_dry_run(method: str, path: str, body: Any, target: Any = None) -> None:
    payload: dict[str, Any] = {"success": True, "dry_run": True,
                               "request": {"method": method, "path": path, "body": body}}
    if target is not None:
        payload["target"] = target
        payload["irreversible"] = True
    payload["next_action"] = "Show this request to the user; after they confirm, rerun the same command with --yes."
    print(_dump(payload))


# ---------------------------------------------------------------- argument helpers

def json_arg(value: str) -> Any:
    """Parse inline JSON, @path (file) or - (stdin)."""
    try:
        if value == "-":
            return json.load(sys.stdin)
        if value.startswith("@"):
            return json.loads(Path(value[1:]).expanduser().read_text(encoding="utf-8"))
        return json.loads(value)
    except OSError as exc:
        raise argparse.ArgumentTypeError(f"cannot read {value}: {exc}") from exc
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid JSON: {exc}") from exc


def trace_ids_arg(value: str) -> list[str]:
    """Comma/whitespace separated ids, or @path holding a JSON array or one id per line."""
    text = value
    if value.startswith("@"):
        try:
            text = Path(value[1:]).expanduser().read_text(encoding="utf-8")
        except OSError as exc:
            raise argparse.ArgumentTypeError(f"cannot read {value}: {exc}") from exc
        if text.lstrip().startswith("["):
            try:
                return [str(item) for item in json.loads(text)]
            except ValueError as exc:
                raise argparse.ArgumentTypeError(f"invalid JSON array: {exc}") from exc
    return [item for item in re.split(r"[\s,]+", text) if item]


def positive_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a positive integer") from exc
    if number <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def sampling_rate(value: str) -> float:
    try:
        rate = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a number between 0 and 1") from exc
    if not 0 <= rate <= 1:
        raise argparse.ArgumentTypeError("must be a number between 0 and 1")
    return rate


def page_size(value: str) -> int:
    size = positive_int(value)
    if size > 100:
        raise argparse.ArgumentTypeError("must be between 1 and 100")
    return size


# ---------------------------------------------------------------- commands

def _poll(client: SingSightClient, path: str, terminal: set[str], wait_seconds: int, interval: int) -> Any:
    deadline = time.monotonic() + wait_seconds
    while True:
        data = client.request("GET", path)
        status = data.get("status") if isinstance(data, dict) else None
        if wait_seconds <= 0 or status in terminal or time.monotonic() >= deadline:
            if wait_seconds > 0 and status not in terminal and isinstance(data, dict):
                data = {**data, "wait_timed_out": True}
            return data
        time.sleep(min(interval, max(1, deadline - time.monotonic())))


def _jobs_referencing(client: SingSightClient, field: str, value: int) -> list[int]:
    jobs = client.request("GET", "/open/api/v1/eval/jobs") or []
    return [job["id"] for job in jobs if job.get(field) == value]


def _in_use(kind: str, target_id: int, job_ids: list[int]) -> SingSightError:
    return SingSightError(
        f"{kind} {target_id} is still referenced by eval jobs {job_ids}.",
        code="TARGET_IN_USE",
        next_action="Delete those eval jobs first (delete-eval-job), then retry.",
    )


def delete_target(client: SingSightClient, kind: str, target_id: int) -> tuple[str, dict]:
    """Look up a delete target and refuse deletes that would break other objects."""
    if kind == "eval-job":
        job = client.request("GET", f"/open/api/v1/eval/jobs/{target_id}")
        if job.get("status") not in EVAL_TERMINAL_STATUSES:
            raise SingSightError(
                f"eval job {target_id} is {job.get('status')}; only finished jobs can be deleted.",
                code="TARGET_BUSY", next_action="Wait for the job to finish (eval-status --wait), then retry.")
        summary = {k: job.get(k) for k in ("id", "name", "status", "evaluatorId", "datasetId", "createdAt")}
        return f"/open/api/v1/eval/jobs/{target_id}", summary
    if kind == "dataset":
        dataset = client.request("GET", f"/open/api/v1/eval/datasets/{target_id}")
        job_ids = _jobs_referencing(client, "datasetId", target_id)
        if job_ids:
            raise _in_use("dataset", target_id, job_ids)
        if dataset.get("activeImports"):
            raise SingSightError(f"dataset {target_id} has imports in progress.", code="TARGET_BUSY",
                                 next_action="Wait for the imports to finish (import-status --wait), then retry.")
        summary = {k: dataset.get(k) for k in ("id", "name", "datasetTag", "traceCount", "spanCount", "createdAt")}
        return f"/open/api/v1/eval/datasets/{target_id}", summary
    evaluators = client.request("GET", "/open/api/v1/evaluator") or []
    evaluator = next((item for item in evaluators if item.get("id") == target_id), None)
    if evaluator is None:
        raise SingSightError(f"evaluator {target_id} not found in this project.", code="NOT_FOUND")
    if evaluator.get("builtIn"):
        raise SingSightError(f"evaluator {target_id} ({evaluator.get('name')}) is built in and cannot be deleted.",
                             code="BUILT_IN_EVALUATOR")
    job_ids = _jobs_referencing(client, "evaluatorId", target_id)
    if job_ids:
        raise _in_use("evaluator", target_id, job_ids)
    summary = {k: evaluator.get(k) for k in ("id", "name", "evaluatorGroup", "scoreType", "createdAt")}
    return f"/open/api/v1/evaluator/{target_id}", summary


def resolve_schema(client: SingSightClient, settings: dict) -> str:
    if settings.get("schema"):
        return settings["schema"]
    context = client.schema_context()
    schema = context.get("schema") if isinstance(context, dict) else None
    if not schema:
        raise SingSightError("schema-context returned no schema; set schema in the project config.",
                             code="INVALID_CONFIGURATION")
    return schema


def run_sql(client: SingSightClient, settings: dict, args: argparse.Namespace) -> int:
    for key in ("cz_profile", "workspace"):
        if not settings.get(key):
            raise SingSightError(
                f"Project {settings['name']} needs {key} to run SQL; it pins cz-cli to the project's Lakehouse workspace.",
                code="SINGSIGHT_NOT_CONFIGURED")
    if (args.statement is None) == (args.file is None):
        raise _invalid("Provide exactly one of a SQL statement or --file.")
    command = [settings.get("cz_cli") or "cz-cli", "sql",
               "-p", settings["cz_profile"],
               "--workspace", settings["workspace"],
               "-s", resolve_schema(client, settings),
               "--format", args.format]
    if settings.get("vcluster"):
        command += ["--vcluster", settings["vcluster"]]
    if args.no_truncate:
        command.append("--no-truncate")
    command += ["-f", args.file] if args.file else ["-e", args.statement]
    try:
        return subprocess.run(command, check=False).returncode
    except FileNotFoundError as exc:
        raise SingSightError(f"cz-cli not found: {command[0]}", code="CZ_CLI_NOT_FOUND",
                             next_action="Install cz-cli or set cz_cli in the project config.") from exc


def dispatch(args: argparse.Namespace) -> int:
    settings = load_project(args.config, args.project)
    client = SingSightClient(settings)
    cmd = args.command

    def out(data: Any) -> int:
        emit(data, cmd, args.max_bytes, args.full)
        return 0

    def write(method: str, path: str, body: Any) -> int:
        if not args.yes:
            emit_dry_run(method, path, body)
            return 0
        return out(client.request(method, path, body=body))

    if cmd == "config":
        return out({key: settings.get(key) for key in (
            "name", "config_path", "base_url", "cz_profile", "workspace", "schema", "vcluster", "cz_cli")
            if settings.get(key)} | {"api_key": "(set)"})
    if cmd == "sql":
        return run_sql(client, settings, args)
    if cmd == "schema-context":
        return out(client.schema_context(use_cache=not args.refresh))
    if cmd == "filter-options":
        params = None
        if args.filter is not None:
            params = {"filter": json.dumps(validate_filter(args.filter), ensure_ascii=False, separators=(",", ":"))}
        return out(client.request("GET", "/open/api/v1/eval/jobs/filter-options", params=params))
    if cmd == "preview":
        body = {"granularity": args.granularity, "samplingRate": args.sampling_rate,
                **_eval_source(args.filter, args.dataset_id)}
        return out(client.request("POST", "/open/api/v1/eval/jobs/preview", body=body))
    if cmd == "evaluators":
        return out(client.request("GET", "/open/api/v1/evaluator/page",
                                  params={"page": args.page, "pageSize": args.page_size}))
    if cmd == "create-evaluator":
        return write("POST", "/open/api/v1/evaluator", validate_custom_evaluator(args.spec))
    if cmd == "trigger-eval":
        if not args.name.strip():
            raise _invalid("--name must be a non-empty string.")
        body = {"name": args.name.strip(), "evaluatorId": args.evaluator_id,
                "granularity": args.granularity, "samplingRate": args.sampling_rate,
                **_eval_source(args.filter, args.dataset_id)}
        if args.description is not None:
            body["description"] = args.description
        if args.evaluator_params is not None:
            if not isinstance(args.evaluator_params, dict) or len(args.evaluator_params) > 50:
                raise _invalid("--evaluator-params must be a JSON object with at most 50 keys.")
            body["evaluatorParams"] = args.evaluator_params
        return write("POST", "/open/api/v1/eval/jobs", body)
    if cmd == "eval-status":
        return out(_poll(client, f"/open/api/v1/eval/jobs/{args.job_id}", EVAL_TERMINAL_STATUSES,
                         args.wait, args.interval))
    if cmd == "eval-jobs":
        return out(client.request("GET", "/open/api/v1/eval/jobs/page",
                                  params={"page": args.page, "pageSize": args.page_size}))
    if cmd == "eval-results":
        if args.min_score is not None and args.max_score is not None and args.min_score > args.max_score:
            raise _invalid("--min-score must not exceed --max-score.")
        return out(client.request("GET", f"/open/api/v1/eval/jobs/{args.job_id}/results", params={
            "page": args.page, "pageSize": args.page_size, "minScore": args.min_score,
            "maxScore": args.max_score, "serviceName": args.service_name}))
    if cmd == "datasets":
        return out(client.request("GET", "/open/api/v1/eval/datasets"))
    if cmd == "create-dataset":
        return write("POST", "/open/api/v1/eval/datasets", validate_dataset(args.name, args.tag, args.description))
    if cmd == "add-traces":
        return write("POST", f"/open/api/v1/eval/datasets/{args.dataset_id}/traces", validate_add_traces(args))
    if cmd in {"delete-eval-job", "delete-dataset", "delete-evaluator"}:
        path, target = delete_target(client, cmd.removeprefix("delete-"), args.target_id)
        if not args.yes:
            emit_dry_run("DELETE", path, None, target)
            return 0
        client.request("DELETE", path)
        return out({"deleted": target})
    if cmd == "import-status":
        return out(_poll(client, f"/open/api/v1/eval/datasets/imports/{args.import_id}", IMPORT_TERMINAL_STATUSES,
                         args.wait, args.interval))
    raise _invalid(f"unknown command: {cmd}")


def build_parser() -> argparse.ArgumentParser:
    def common_options(suppress: bool) -> argparse.ArgumentParser:
        # Subcommands repeat the global options with SUPPRESS defaults so that a value given
        # before the subcommand is not overwritten by the subparser's default.
        def default(value: Any) -> Any:
            return argparse.SUPPRESS if suppress else value

        options = argparse.ArgumentParser(add_help=False)
        options.add_argument("--project", default=default(None),
                             help="project name in the config (default: default_project)")
        options.add_argument("--config", default=default(None),
                             help=f"config path (default: $SINGSIGHT_CONFIG or {DEFAULT_CONFIG_PATH})")
        options.add_argument("--max-bytes", type=positive_int, default=default(DEFAULT_MAX_BYTES),
                             help="print budget; larger results go to a file under the cache dir")
        options.add_argument("--full", action="store_true", default=default(False),
                             help="no truncation; write the full result to a file")
        return options

    common = common_options(suppress=True)
    parser = argparse.ArgumentParser(prog="singsight.py", description=__doc__.splitlines()[0],
                                     parents=[common_options(suppress=False)])
    sub = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")

    def add(name: str, help_text: str) -> argparse.ArgumentParser:
        return sub.add_parser(name, help=help_text, description=help_text, parents=[common])

    def source_args(p: argparse.ArgumentParser) -> None:
        p.add_argument("--filter", type=json_arg, help="live-trace filter JSON, @file or - (needs time_start/time_end)")
        p.add_argument("--dataset-id", type=positive_int, help="evaluate a dataset snapshot instead of a filter")
        p.add_argument("--granularity", choices=["TRACE", "SPAN", "SESSION"], default="TRACE")
        p.add_argument("--sampling-rate", type=sampling_rate, default=1.0)

    def paging(p: argparse.ArgumentParser, default_size: int) -> None:
        p.add_argument("--page", type=positive_int, default=1)
        p.add_argument("--page-size", type=page_size, default=default_size)

    def confirm(p: argparse.ArgumentParser) -> None:
        p.add_argument("--yes", action="store_true", help="actually send; without it only prints the request")

    def waiting(p: argparse.ArgumentParser) -> None:
        p.add_argument("--wait", type=int, default=0, metavar="SECONDS", help="poll until a terminal status")
        p.add_argument("--interval", type=positive_int, default=5, metavar="SECONDS")

    add("config", "show the resolved project binding (secrets hidden)")
    p = add("schema-context", "Lakehouse schema, tables, columns and query rules of the project")
    p.add_argument("--refresh", action="store_true", help="bypass the 24h cache")
    p = add("sql", "run read-only SQL through cz-cli, pinned to the project's profile/workspace/schema")
    p.add_argument("statement", nargs="?")
    p.add_argument("-f", "--file", help="read SQL from a file")
    p.add_argument("--format", default="json", choices=["json", "pretty", "table", "csv", "text", "jsonl", "toon"])
    p.add_argument("--no-truncate", action="store_true", help="do not truncate long field values")
    p = add("filter-options", "candidate values per filter dimension (max 100 each)")
    p.add_argument("--filter", type=json_arg, help="optional narrowing filter JSON, @file or -")
    source_args(add("preview", "preview the evaluation scope with the exact evaluation semantics"))
    paging(add("evaluators", "list evaluators usable by trigger-eval"), 50)
    p = add("create-evaluator", "create a project custom multi-step evaluator (write)")
    p.add_argument("--spec", type=json_arg, required=True, help="evaluator spec JSON, @file or -")
    confirm(p)
    p = add("trigger-eval", "create and start an evaluation job; consumes evaluation quota (write)")
    p.add_argument("--name", required=True)
    p.add_argument("--evaluator-id", type=positive_int, required=True)
    p.add_argument("--description")
    p.add_argument("--evaluator-params", type=json_arg, help="JSON object, @file or -")
    source_args(p)
    confirm(p)
    p = add("eval-status", "status, current step and error of an evaluation job")
    p.add_argument("job_id", type=positive_int)
    waiting(p)
    paging(add("eval-jobs", "list evaluation jobs"), 50)
    p = add("eval-results", "per-trace/span/session results of an evaluation job")
    p.add_argument("job_id", type=positive_int)
    paging(p, 20)
    p.add_argument("--min-score", type=float)
    p.add_argument("--max-score", type=float)
    p.add_argument("--service-name")
    add("datasets", "list evaluation datasets (trace snapshots)")
    p = add("create-dataset", "create an empty evaluation dataset (write)")
    p.add_argument("--name", required=True)
    p.add_argument("--tag", help="Lakehouse partition tag; immutable, auto-generated when omitted")
    p.add_argument("--description")
    confirm(p)
    p = add("add-traces", "asynchronously import traces into a dataset (write, idempotent)")
    p.add_argument("dataset_id", type=positive_int)
    p.add_argument("--eval-job-id", type=positive_int, help="preferred: source live-trace evaluation job")
    p.add_argument("--job-scope", choices=["RESULTS", "FILTER"], help="RESULTS (default) or FILTER")
    p.add_argument("--min-score", type=float)
    p.add_argument("--max-score", type=float)
    p.add_argument("--trace-ids", type=trace_ids_arg, help=f"comma list or @file, max {MAX_EXPLICIT_TRACE_IDS}")
    p.add_argument("--time-start", help="trace-ids only: UTC ISO 8601 lower bound")
    p.add_argument("--time-end", help="trace-ids only: UTC ISO 8601 upper bound")
    confirm(p)
    p = add("import-status", "status of a dataset import job")
    p.add_argument("import_id", type=positive_int)
    waiting(p)
    for name, help_text in (
            ("delete-eval-job", "delete a finished evaluation job (write, irreversible)"),
            ("delete-dataset", "delete a dataset and its trace snapshot; no job may reference it (write, irreversible)"),
            ("delete-evaluator", "delete a custom evaluator; no job may reference it (write, irreversible)")):
        p = add(name, help_text)
        p.add_argument("target_id", type=positive_int)
        confirm(p)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return dispatch(args)
    except SingSightError as exc:
        error = {"success": False, "code": exc.code, "message": str(exc), "retryable": exc.retryable}
        if exc.next_action:
            error["next_action"] = exc.next_action
        print(_dump(error), file=sys.stderr)
        return exc.exit_code


if __name__ == "__main__":
    sys.exit(main())
