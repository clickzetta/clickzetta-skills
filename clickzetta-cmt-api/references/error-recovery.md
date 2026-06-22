# Error Recovery

## Status Handling

- `accepted`: the run exists but has not progressed yet; wait rather than branching to legacy state.
- `preparing`: the start path is still translating intent into runnable work; wait unless the user asked to interrupt.
- `ready`: tasks are prepared; if the user asked for status, report it as runnable state, not as success.
- `running`: keep waiting and summarize progress from structured events.
- `succeeded`: verify targets and checks before claiming success. If all run children are `skipped`, report that no execution task was generated rather than implying data moved.
- `failed`: inspect run events or logs before proposing cleanup or retry.
- `attention`: do not guess. Read `next_action.recommended_action` and surface it.

## Error Categories

- `environment_unspecified`: the user did not say whether to use local CMT or an online CMT service. Ask which environment to use before touching `/doc` or `/api/v2`.
- `service_url_missing`: the user chose an online CMT service but did not provide its base URL. Ask for the URL before proceeding.
- `service_unavailable_local`: `localhost:6060` is not listening yet. Start `MMAv3.jar` with the documented `nohup` command, record the PID, and surface the local links after the port is ready.
- `validation`: fix request shape or missing identifiers before retrying.
- `conflict`: inspect existing targets or conflicting runs, then clean up only with explicit user intent.
- `upstream_timeout`: prefer the retry path suggested by the response or `next_action`.
- `transient`: safe to retry when the response marks it retryable.
- `dangerous_operation_requires_confirmation`: stop and get explicit user intent.

## Decision Rules

- If the environment is unspecified, clarify local vs online before assuming `localhost:6060`.
- If the user wants an online CMT service, require and restate the base URL before calling `/doc`, `/llms.txt`, or `/api/v2/*`.
- If the response already carries a next step, follow that instead of inventing one.
- If the run is failed but the target identity is still needed, read verification before discussing cleanup.
- If the user asks “what should I do now”, answer from `recommended_action`, conflict context, or verification state.
- If there is no v2 signal for the recovery path, say that explicitly instead of silently dropping to legacy routes.
- If the user asks why a succeeded run has no execution tasks, answer from `children.status=skipped` and `children.reason_*` before falling back to legacy inference.
- If `/doc` is unreachable because the local service is down, start it first, record the PID file path, and return `http://localhost:6060/doc` as the next link to open.

## Cleanup and Retry

- Retry only after identifying why the previous run stopped.
- Cleanup is an admin mutation and must be user-authorized.
- Do not fall back to legacy mutation endpoints on your own.

## Current Surface Limits

- The current v2 verification surface is still derived from existing run/task state and is not yet a full independent target probe.
- The current `/doc` surface still exposes many legacy endpoints; treat that as documentation noise, not as permission to use them by default.
- A succeeded run with skipped-only children is not evidence that data was copied; explain the outcome from `children.reason_code` / `children.reason_summary`.
