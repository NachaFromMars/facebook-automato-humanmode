# Chrome CDP over Tailscale for Facebook

Use a trusted Windows PC Chrome profile instead of logging into Facebook from a VPS.

## 1. Start Chrome debug profile on Windows

PowerShell:

```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-address=0.0.0.0 --remote-debugging-port=9222 --remote-allow-origins=* --user-data-dir="C:\facebook-chrome"
```

Chrome may still bind only `127.0.0.1:9222`. If so, bridge it to the Tailscale IP:

```powershell
netsh interface portproxy add v4tov4 listenaddress=<TAILSCALE_PC_IP> listenport=9223 connectaddress=127.0.0.1 connectport=9222
New-NetFirewallRule -DisplayName "Chrome Remote Debug 9223" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 9223
```

Verify:

```powershell
netstat -ano | findstr :9223
```

## 2. Login Facebook on PC

Open `https://www.facebook.com/` in that Chrome window and login manually.

## 3. Extract cookies from VPS

```bash
python3 scripts/extract-facebook-cookies.py --base http://<TAILSCALE_PC_IP>:9223 --out /root/.openclaw/workspace/secrets/facebook/cookies.json
./scripts/install-cookies.sh /root/.openclaw/workspace/secrets/facebook/cookies.json
```

Do not print or commit cookie contents.
