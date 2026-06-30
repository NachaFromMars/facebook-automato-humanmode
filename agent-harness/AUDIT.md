# Audit Notes

V1 guardrails:
- All FB commands use existing CDP/cookie session; no password login.
- Cookie output is summarized/masked only.
- Write actions are routed to `skills/facebook-humanmode` and must use HumanMode primitives.
- No post/comment write command is added to generic scraper without explicit command.
- Live post command stores screenshot/log in `skills/facebook-humanmode/data/logs/`.

Verification gates:
- `pytest -q`
- `fbcli tabs --json`
- `fbcli cookies --json`
- TypeScript check for HumanMode post script.
