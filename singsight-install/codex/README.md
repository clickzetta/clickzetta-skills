# Install Codex telemetry on macOS

Tested with Codex CLI 0.167.0-alpha.3.2. The desktop app must be fully quit and reopened to pick up changes to the user config. Run the CLI check below first; verify a desktop conversation separately if that is the target client.

## Configure

1. Get the base HTTPS collector URL and Ingest Key from the selected SingSight project. If the prompt says the key will be provided later, wait for it. If this machine already uses a Codex relay, check its destination and run the verification below before installing a second one.
2. From this skill directory (`singsight-install/codex`), install the three bundled files to a stable, private location. If following a raw URL without a checkout, download [configure.py](configure.py), [relay.py](relay.py) and [requirements.txt](requirements.txt) from the **same revision** first. Use Python 3.10+.

   ```bash
   relay_dir="$HOME/.local/share/singsight-codex"
   install -d -m 700 "$relay_dir"
   install -m 600 configure.py relay.py requirements.txt "$relay_dir/"
   python3 -m venv "$relay_dir/venv"
   "$relay_dir/venv/bin/python" -m pip install -r "$relay_dir/requirements.txt"
   "$relay_dir/venv/bin/python" "$relay_dir/configure.py" prepare --endpoint "$ENDPOINT"
   ```

   Preparation prompts privately for the key, or reads `SINGSIGHT_INGEST_KEY` from the installer environment. Do not put the key on the command line. The relay keeps upstream credentials in a mode-0600 file and listens only on loopback. An existing prepared installation retains its key and port. For a key rotation, stop the relay and replace only its upstream key in the private `relay.json` before starting it again.

3. Load the generated LaunchAgent, then activate Codex's HTTP/protobuf log and trace exporters:

   ```bash
   domain="gui/$(id -u)"
   service="com.clickzetta.singsight-codex"
   if launchctl print "$domain/$service" >/dev/null 2>&1; then
     launchctl kickstart -k "$domain/$service"
   else
     launchctl bootstrap "$domain" "$HOME/Library/LaunchAgents/$service.plist"
   fi
   "$relay_dir/venv/bin/python" "$relay_dir/configure.py" activate
   ```

   If the relay is still starting, retry activation. It checks the authenticated local listener before atomically updating `$CODEX_HOME/config.toml` (default `~/.codex/config.toml`). If exporters are already set, confirm the user intends to switch those destinations and then use `activate --replace-exporters`. Existing settings outside those two exporters are preserved. For rollback, restore the prior exporter values from the named private backup (or remove the two entries on a first install), then unload the LaunchAgent with `launchctl bootout "$domain/$service"` and remove its plist.

## What the relay maps

- Forward native logs and traces. Match a valid conversation UUID directly or correlate a usage span by its OTLP trace ID with a Codex log/span carrying that UUID. Numeric runtime thread IDs are not session IDs. Ambiguous or missing context must not create a fabricated session.
- Mark only a native `handle_responses` span carrying `gen_ai.usage.input_tokens` or `gen_ai.usage.output_tokens` as a `chat` operation. Preserve its trace ID, span ID and original usage. Leave streaming fragments, completion logs and turn-level totals out of the LLM count. Cached input and reasoning output are already represented in the totals.
- Put the conversation UUID in `session.id` and `gen_ai.conversation.id`. SingSight counts distinct sessions and sums input plus output for spans classified as `llm_call`. Internal filesystem and authentication spans can be visible while both KPIs are zero.

## Verify one real conversation

1. Record Overview's project, time window, sessions, LLM calls and token total. Start a **new** Codex CLI process in a trusted directory and run one turn without tools:
   ```bash
   codex exec --json 'Reply only OK. Do not use tools.'
   ```
   Record the `thread_id` from `thread.started` and the input/output counts from `turn.completed.usage`. For this single-request check, expected tokens = input + output.
2. Allow the project's trace-detail and daily overview refreshes to finish; these may be successive cycles. In **Session Tracking**, find the exact thread ID. In its trace, confirm one usage-bearing `chat` span with `event_type = llm_call`, matching input/output counts and a single contribution to the session total.
3. Confirm **Overview** shows the new session, LLM call and token consumption. For an otherwise idle project the delta is +1 session, +1 LLM call and exactly the expected tokens. On a busy project, use the session details for exact attribution and confirm the overview includes the activity. Overview can abbreviate totals: e.g. 27,355 input + 5 output = 27,360 in the session, displayed as 27.4K in Overview.
4. If either KPI remains zero, do not mark the installation verified. Trace-only data: check that both native exporters point at the relay and a restarted client is producing usage-bearing spans. Zero sessions: compare the real thread UUID with session metadata. Zero tokens: check the usage span's classification and fields, then the overview refresh. Doubled totals: look for an extra synthetic span, replayed telemetry, or simultaneous integrations for the same request. If a newer Codex version changes the span shape, report it and adapt the mapping before claiming support.
