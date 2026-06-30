# OpenClaw HumanMode Usage

Use when Facebook cookies are already hydrated locally.

Expected cookie paths:

```text
skills/facebook-humanmode/data/cookies.json
skills/facebook-humanmode/data/cookies/session.json
facebook-data/cookies.json
```

Rules:

- Use cookies first; avoid repeated login attempts.
- Max 3 login attempts, then stop.
- For browsing/posting/commenting/messaging, use HumanMode pacing.
- Do not automate Facebook aggressively from VPS.
- Do not expose cookies/tokens/passwords in logs or chat.
