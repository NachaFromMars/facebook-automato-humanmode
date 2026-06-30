# V1 HumanMode CLI Update

## What changed

- `fbcli humanmode-post` routes Facebook write actions through OpenClaw `skills/facebook-humanmode`.
- Write actions must verify publish state with screenshot/log evidence before reporting success.
- Default scraping count is now **6 posts per category**.
- Added `fbcli category-batch <url...> --json` for multi-category pulls.

## Commands

```bash
fbcli page-posts '<facebook-url>' --json              # default 6 posts
fbcli comments '<post-url>' --json                    # default 6 comments/lines
fbcli category-batch '<url1>' '<url2>' --json         # 6 posts per URL/category
fbcli humanmode-post --text '...' --image image.jpg --json
```

## Audit requirements

- Do not print cookies/tokens.
- Do not login with password from VPS.
- Posting/commenting/replying must use HumanMode pacing.
- After posting, verify that the final feed/profile contains the published post, not just that the composer accepted a click.
