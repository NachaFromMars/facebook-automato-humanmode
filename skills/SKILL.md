---
name: facebook-automato-humanmode
description: Use when hydrating Facebook cookies from a trusted PC Chrome/CDP session into OpenClaw Facebook HumanMode.
---

# Facebook Automato HumanMode

Use this skill when Facebook login should be handled via a trusted PC browser, then cookies installed into OpenClaw HumanMode.

Procedure:

1. Connect to trusted Chrome CDP endpoint over Tailscale.
2. Confirm Facebook tab is logged in.
3. Extract cookies without printing values.
4. Install to HumanMode cookie paths.
5. Verify `c_user` and `xs` exist.

Never commit cookies or print cookie values.
