#!/usr/bin/env bash
# Serialise the live suites.
#
# All three live suites create objects in a schema and then drop it. Running two at once against
# the same profile does not corrupt anything - they contend for the same vcluster instead, and both
# start failing with JOB_TIMEOUT after a few minutes, which looks like a product problem and is not.
# This lock turns that into an immediate, clear refusal.
#
# Usage, right after the profile is known:
#
#     . "$HERE/lib/lock.sh"          # or ../lib/lock.sh from a subdirectory
#     acquire_lock "$PROFILE" || exit 3
#
# and call `release_lock` from the script's own EXIT cleanup.

LOCK_ROOT="${LOCK_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/.locks}"

acquire_lock() {  # acquire_lock <profile>
    local profile="$1"
    mkdir -p "$LOCK_ROOT"
    LOCK_DIR="$LOCK_ROOT/${profile//\//_}.lock"
    if ! mkdir "$LOCK_DIR" 2>/dev/null; then          # mkdir is atomic, so this is the whole lock
        echo "ABORT: another live suite is already running against profile '$profile'."
        echo "       Two at once contend for the same vcluster and both start failing with"
        echo "       JOB_TIMEOUT, which looks like a product problem and is not. Wait for it,"
        echo "       or remove the stale lock if that run died: $LOCK_DIR"
        [ -f "$LOCK_DIR/owner" ] && echo "       lock held by: $(cat "$LOCK_DIR/owner")"
        LOCK_DIR=""
        return 1
    fi
    printf 'pid %s on %s\n' "$$" "$(hostname)" > "$LOCK_DIR/owner"
    echo "lock: $LOCK_DIR" >&2
    return 0
}

release_lock() {
    [ -n "${LOCK_DIR:-}" ] || return 0
    rm -rf "$LOCK_DIR"
    LOCK_DIR=""
}
