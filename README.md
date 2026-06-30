# Facebook Automato HumanMode

Agent-native Facebook session/cookie bridge for OpenClaw HumanMode workflows.

This repo documents and wraps a safe flow for using a trusted desktop Chrome session (via Tailscale + Chrome DevTools Protocol) to hydrate Facebook cookies for local automation tools.

## What it does

- Opens/controls a trusted PC Chrome session through CDP.
- Verifies Facebook login state without re-typing credentials on the VPS.
- Extracts only the needed Facebook cookies locally.
- Installs cookies into expected HumanMode paths.
- Keeps cookies, tokens, passwords, and profiles out of git.

## Why

Facebook/Meta is sensitive to headless/VPS login attempts. The safer path is:

1. Login on a trusted PC/browser.
2. Extract session cookies via CDP over Tailscale.
3. Use cookies with slow, human-like automation.

## Expected local paths

The wrapper can install cookies into:

```text
/root/.openclaw/workspace/secrets/facebook/cookies.json
/root/.openclaw/workspace/skills/facebook-humanmode/data/cookies.json
/root/.openclaw/workspace/skills/facebook-humanmode/data/cookies/session.json
/root/.openclaw/workspace/facebook-data/cookies.json
```

## Safety rules

- Never commit cookies or tokens.
- Never print `c_user`, `xs`, or full cookie values in chat/logs.
- Do not spam login attempts.
- Prefer trusted PC Chrome/CDP over VPS direct login.
- For any posting/commenting/messaging, use HumanMode pacing and explicit user intent.

## Quick verification

A successful cookie extraction should detect:

- `c_user`
- `xs`

## License

MIT for wrapper/docs in this repo. Facebook and upstream OpenClaw/HumanMode code remain under their own terms.
