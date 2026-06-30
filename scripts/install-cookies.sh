#!/usr/bin/env bash
set -euo pipefail

SRC="${1:-}"
if [[ -z "$SRC" || ! -f "$SRC" ]]; then
  echo "Usage: $0 /path/to/cookies.json" >&2
  exit 2
fi

ROOT="${OPENCLAW_WORKSPACE:-/root/.openclaw/workspace}"
mkdir -p \
  "$ROOT/secrets/facebook" \
  "$ROOT/skills/facebook-humanmode/data/cookies" \
  "$ROOT/facebook-data"

install -m 600 "$SRC" "$ROOT/secrets/facebook/cookies.json"
install -m 600 "$SRC" "$ROOT/skills/facebook-humanmode/data/cookies.json"
install -m 600 "$SRC" "$ROOT/skills/facebook-humanmode/data/cookies/session.json"
install -m 600 "$SRC" "$ROOT/facebook-data/cookies.json"

python3 - <<PY
import json
paths = [
 '$ROOT/secrets/facebook/cookies.json',
 '$ROOT/skills/facebook-humanmode/data/cookies.json',
 '$ROOT/skills/facebook-humanmode/data/cookies/session.json',
 '$ROOT/facebook-data/cookies.json',
]
for p in paths:
    data=json.load(open(p)); names={c.get('name') for c in data}
    print(p, len(data), 'c_user=' + str('c_user' in names), 'xs=' + str('xs' in names))
PY
