# cli-anything-facebook-automato

Install:

```bash
cd /root/.openclaw/workspace/facebook-automato-humanmode/agent-harness
pip install -e .
```

Commands:

```bash
fbcli tabs --json
fbcli cookies --json
fbcli extract-cookies --json
fbcli whoami --json
fbcli page-posts 'https://www.facebook.com/somepage' --limit 20 --json
fbcli comments 'https://www.facebook.com/...' --limit 50 --json
```

Safety: V0 is read-only except `extract-cookies`, which writes cookie files locally and never prints cookie values.
