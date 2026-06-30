# Test Plan

1. Unit tests: cookie masking and text parser.
2. CLI import test: `python -m cli_anything.facebook_automato --help`.
3. Install test: `pip install -e .` then `fbcli tabs --json`.
4. Live CDP read-only tests: `fbcli cookies --json`, `fbcli whoami --json`.
