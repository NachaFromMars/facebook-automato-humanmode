#!/usr/bin/env python3
"""Extract Facebook cookies from a trusted Chrome DevTools endpoint.

Usage:
  python3 scripts/extract-facebook-cookies.py --base http://100.86.14.12:9223 --out ./cookies.json

This script intentionally does not print cookie values.
"""
import argparse, json, urllib.request, itertools, os, sys, time
import websocket


def cdp_call(ws, ids, method, params=None):
    i = next(ids)
    ws.send(json.dumps({'id': i, 'method': method, 'params': params or {}}))
    while True:
        msg = json.loads(ws.recv())
        if msg.get('id') == i:
            return msg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', required=True, help='Chrome DevTools base URL, e.g. http://100.86.14.12:9223')
    ap.add_argument('--out', required=True, help='Output cookies JSON path')
    args = ap.parse_args()

    tabs = json.load(urllib.request.urlopen(args.base.rstrip('/') + '/json/list', timeout=10))
    pages = [t for t in tabs if t.get('type') == 'page' and 'facebook.com' in t.get('url', '')]
    if not pages:
        print('NO_FACEBOOK_TAB', file=sys.stderr)
        return 2

    page = pages[0]
    ws = websocket.create_connection(page['webSocketDebuggerUrl'], timeout=10)
    ids = itertools.count(1)
    cdp_call(ws, ids, 'Network.enable')
    cookies = cdp_call(ws, ids, 'Network.getAllCookies').get('result', {}).get('cookies', [])
    fb = [c for c in cookies if 'facebook.com' in c.get('domain', '') or c.get('domain', '').endswith('.fb.com')]
    names = {c.get('name') for c in fb}

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(fb, f, ensure_ascii=False, indent=2)
    os.chmod(args.out, 0o600)

    print(json.dumps({
        'status': 'ok',
        'cookie_count': len(fb),
        'has_c_user': 'c_user' in names,
        'has_xs': 'xs' in names,
        'out': args.out,
    }, ensure_ascii=False))
    return 0 if ('c_user' in names and 'xs' in names) else 3


if __name__ == '__main__':
    raise SystemExit(main())
