"""Prepare a user-owned Codex relay, then route OTLP after it is healthy."""

import argparse
import fcntl
import getpass
import hashlib
import json
import os
import plistlib
import secrets
import socket
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

import tomlkit

ROOT = Path(__file__).resolve().parent
SETTINGS = ROOT / "relay.json"
SIGNALS = {"exporter": "/v1/logs", "trace_exporter": "/v1/traces"}
LABEL = "com.clickzetta.singsight-codex"


def write_private(path, data):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as tmp:
        tmp.write(data)
    os.replace(tmp.name, path)


@contextmanager
def configuration_lock():
    # Serialize read/change with relay startup, including the bind to its port.
    with (ROOT / "relay.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def credential_id(upstream):
    # This was the queue filename in older installations.
    return hashlib.sha256(json.dumps(upstream, sort_keys=True).encode()).hexdigest()


def load_settings():
    settings = json.loads(SETTINGS.read_text())
    if "project_id" not in settings:
        settings["project_id"] = credential_id(settings["upstream"])
    return settings


def require_stopped(settings):
    with socket.socket() as sock:
        if sock.connect_ex(("127.0.0.1", settings["port"])) == 0:
            raise SystemExit(
                "Stop the running relay before changing its project or credential."
            )


def prepare(endpoint, switch_project=False, rotate_key=False):
    url = urlsplit(endpoint)
    if (
        url.scheme != "https"
        or not url.hostname
        or url.username
        or url.password
        or url.query
        or url.fragment
        or url.path.strip("/")
    ):
        raise SystemExit("Expected the HTTPS collector base URL from Quick Start.")
    supplied_key = os.getenv("SINGSIGHT_INGEST_KEY")
    if supplied_key is not None and not supplied_key.strip():
        raise SystemExit("An Ingest Key is required.")
    new_install = not SETTINGS.exists()
    if new_install:
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        settings = {"port": port}
    else:
        settings = load_settings()
        if (
            rotate_key
            and settings["upstream"]["/v1/traces"]["endpoint"]
            != endpoint.rstrip("/") + "/v1/traces"
        ):
            raise SystemExit(
                "--rotate-key requires the same collector; use --switch-project for a different project."
            )
    if new_install or switch_project or rotate_key:
        key = supplied_key or getpass.getpass("SingSight Ingest Key: ")
        if not key.strip():
            raise SystemExit("An Ingest Key is required.")
    else:
        key = (
            supplied_key
            or settings["upstream"]["/v1/traces"]["headers"]["x-singsight-apikey"]
        )

    upstream = {
        path: {
            "endpoint": endpoint.rstrip("/") + path,
            "headers": {"x-singsight-apikey": key},
        }
        for path in SIGNALS.values()
    }
    if upstream != settings.get("upstream"):
        if not new_install:
            if not (switch_project or rotate_key):
                raise SystemExit(
                    "Collector or Ingest Key differs. Use --switch-project or --rotate-key explicitly."
                )
            require_stopped(settings)
        projects = settings.setdefault("projects", {})
        if not new_install:
            projects[credential_id(settings["upstream"])] = settings["project_id"]
        destination = credential_id(upstream)
        if new_install or switch_project:
            settings["project_id"] = projects.get(destination, secrets.token_hex(16))
            settings["local_token"] = secrets.token_hex(32)
        elif (
            destination in projects and projects[destination] != settings["project_id"]
        ):
            raise SystemExit(
                "That key is registered to another project. Use --switch-project."
            )
        projects[destination] = settings["project_id"]
        settings["upstream"] = upstream
        write_private(SETTINGS, json.dumps(settings).encode())
    if sys.platform == "darwin":
        directory = Path.home() / "Library/LaunchAgents"
        directory.mkdir(parents=True, exist_ok=True)
        write_private(
            directory / (LABEL + ".plist"),
            plistlib.dumps(
                {
                    "Label": LABEL,
                    "ProgramArguments": [sys.executable, str(ROOT / "relay.py")],
                    "RunAtLoad": True,
                    "KeepAlive": True,
                }
            ),
        )
    print("Relay prepared. Start it before activating the Codex configuration.")


def activate(replace):
    settings = json.loads(SETTINGS.read_text())
    base = "http://127.0.0.1:" + str(settings["port"])
    token = settings["local_token"]
    with urlopen(
        Request(base + "/ready", headers={"x-local-token": token}), timeout=3
    ) as response:
        if response.status != 204:
            raise SystemExit("Relay health check failed.")
    directory = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    path = directory / "config.toml"
    original = path.read_bytes() if path.exists() else b""
    doc = tomlkit.parse(original.decode())
    if "otel" not in doc:
        doc["otel"] = tomlkit.table()
    otel = doc["otel"]
    for field, suffix in SIGNALS.items():
        value = {
            "otlp-http": {
                "endpoint": base + suffix,
                "protocol": "binary",
                "headers": {"x-local-token": token},
            }
        }
        if otel.get(field) == value:
            continue
        if field in otel and otel[field] != "none" and not replace:
            raise SystemExit(
                "Existing OTLP exporter. Review destination before using --replace-exporters."
            )
        otel[field] = value
    updated = tomlkit.dumps(doc).encode()
    if original == updated:
        print("Codex is already configured.")
        return
    if path.exists():
        with tempfile.NamedTemporaryFile(
            prefix="config.toml.pre-singsight-", dir=directory, delete=False
        ) as backup:
            backup.write(original)
            print("Backup:", backup.name)
    write_private(path, updated)
    print("Codex configured. Restart Codex and verify a real turn.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("--endpoint", required=True)
    change = prep.add_mutually_exclusive_group()
    change.add_argument("--switch-project", action="store_true")
    change.add_argument("--rotate-key", action="store_true")
    sub.add_parser("activate").add_argument("--replace-exporters", action="store_true")
    args = parser.parse_args()
    if args.action == "prepare":
        with configuration_lock():
            prepare(args.endpoint, args.switch_project, args.rotate_key)
    else:
        activate(args.replace_exporters)
