import json
import os
import subprocess
from pathlib import Path
from typing import List

import click

from .utils.cdp import (
    CdpClient, pick_facebook_tab, sanitize_cookie_summary, extract_text_snapshot,
    navigate, get_location, facebook_cookies, whoami_from_dom, parse_posts_from_text,
)

DEFAULT_BASE = os.environ.get('FB_CDP_BASE', 'http://100.86.14.12:9223')
ROOT = Path(__file__).resolve().parents[4]
BRIDGE = ROOT / 'scripts'
DEFAULT_COOKIE = Path('/root/.openclaw/workspace/secrets/facebook/cookies.json')
CONFIG_PATH = ROOT / 'config.json'
HUMANMODE_DIR = Path('/root/.openclaw/workspace/skills/facebook-humanmode')



def load_config():
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
    return {'defaults': {'posts_per_category': 6, 'comments_per_post': 6}}

def default_limit(key: str, fallback: int = 6) -> int:
    return int(load_config().get('defaults', {}).get(key, fallback))

def emit(data, as_json=False):
    if as_json:
        click.echo(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        if isinstance(data, str):
            click.echo(data)
        else:
            click.echo(json.dumps(data, ensure_ascii=False, indent=2))


def json_option(fn):
    def callback(ctx, param, value):
        if value:
            ctx.ensure_object(dict)
            ctx.obj['json'] = True
        return value
    return click.option('--json-output', '--json', 'cmd_json', is_flag=True, expose_value=False, callback=callback, help='Machine-readable JSON output')(fn)


@click.group(invoke_without_command=True)
@click.option('--base', default=DEFAULT_BASE, show_default=True, help='Chrome DevTools base URL')
@click.option('--json-output', '--json', 'as_json', is_flag=True, help='Machine-readable JSON output')
@click.pass_context
def cli(ctx, base, as_json):
    """Facebook Automato HumanMode CLI. V0 is read-only by default."""
    ctx.ensure_object(dict)
    ctx.obj['base'] = base
    ctx.obj['json'] = as_json
    if ctx.invoked_subcommand is None:
        emit('fbcli ready. Commands: tabs, whoami, cookies, extract-cookies, page-posts, comments, category-batch, humanmode-post', as_json=False)


@cli.command()
@json_option
@click.pass_context
def tabs(ctx):
    c = CdpClient(ctx.obj['base'])
    data = [{'title': t.title, 'url': t.url, 'type': t.type, 'facebook': 'facebook.com' in t.url} for t in c.list_tabs()]
    emit({'tabs': data}, ctx.obj['json'])


@cli.command('cookies')
@json_option
@click.pass_context
def cookies_cmd(ctx):
    c = CdpClient(ctx.obj['base'])
    tab = pick_facebook_tab(c.list_tabs())
    if not tab:
        raise click.ClickException('NO_FACEBOOK_TAB')
    c.connect(tab)
    try:
        emit({'tab': {'title': tab.title, 'url': tab.url}, 'cookies': sanitize_cookie_summary(facebook_cookies(c))}, ctx.obj['json'])
    finally:
        c.close()


@cli.command('extract-cookies')
@json_option
@click.option('--out', default=str(DEFAULT_COOKIE), show_default=True)
@click.option('--install/--no-install', default=True, show_default=True)
@click.pass_context
def extract_cookies(ctx, out, install):
    script = ROOT / 'scripts' / 'extract-facebook-cookies.py'
    install_script = ROOT / 'scripts' / 'install-cookies.sh'
    res = subprocess.run(['python3', str(script), '--base', ctx.obj['base'], '--out', out], text=True, capture_output=True)
    if res.returncode != 0:
        raise click.ClickException((res.stderr or res.stdout).strip())
    data = json.loads(res.stdout)
    if install:
        ins = subprocess.run([str(install_script), out], text=True, capture_output=True)
        if ins.returncode != 0:
            raise click.ClickException((ins.stderr or ins.stdout).strip())
        data['installed'] = True
    emit(data, ctx.obj['json'])


@cli.command()
@json_option
@click.pass_context
def whoami(ctx):
    c = CdpClient(ctx.obj['base'])
    tab = pick_facebook_tab(c.list_tabs())
    if not tab:
        raise click.ClickException('NO_FACEBOOK_TAB')
    c.connect(tab)
    try:
        text = extract_text_snapshot(c)
        data = {'url': get_location(c), 'cookie_login': sanitize_cookie_summary(facebook_cookies(c)), 'dom': whoami_from_dom(text)}
        emit(data, ctx.obj['json'])
    finally:
        c.close()


@cli.command('page-posts')
@json_option
@click.argument('url')
@click.option('--limit', default=None, type=int, help='Defaults to config defaults.posts_per_category (6)')
@click.option('--wait', default=5.0, show_default=True)
@click.pass_context
def page_posts(ctx, url, limit, wait):
    c = CdpClient(ctx.obj['base'])
    tab = pick_facebook_tab(c.list_tabs())
    if not tab:
        raise click.ClickException('NO_FACEBOOK_TAB')
    c.connect(tab)
    try:
        navigate(c, url, wait)
        text = extract_text_snapshot(c)
        limit = limit or default_limit('posts_per_category', 6)
        emit({'url': get_location(c), 'limit': limit, 'posts': parse_posts_from_text(text, limit)}, ctx.obj['json'])
    finally:
        c.close()


@cli.command('comments')
@json_option
@click.argument('post_url')
@click.option('--limit', default=None, type=int, help='Defaults to config defaults.comments_per_post (6)')
@click.option('--wait', default=5.0, show_default=True)
@click.pass_context
def comments(ctx, post_url, limit, wait):
    limit = limit or default_limit('comments_per_post', 6)
    c = CdpClient(ctx.obj['base'])
    tab = pick_facebook_tab(c.list_tabs())
    if not tab:
        raise click.ClickException('NO_FACEBOOK_TAB')
    c.connect(tab)
    try:
        navigate(c, post_url, wait)
        text = extract_text_snapshot(c)
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        comments = []
        for line in lines:
            if 3 <= len(line) <= 600 and not line.lower().startswith(('like', 'comment', 'share')):
                comments.append(line)
            if len(comments) >= limit:
                break
        emit({'url': get_location(c), 'comments_or_snapshot_lines': comments, 'warning': 'V0 heuristic parser'}, ctx.obj['json'])
    finally:
        c.close()



@cli.command('category-batch')
@json_option
@click.argument('urls', nargs=-1, required=True)
@click.option('--limit', default=None, type=int, help='Posts per category URL; defaults to config value 6')
@click.option('--wait', default=5.0, show_default=True)
@click.pass_context
def category_batch(ctx, urls: List[str], limit, wait):
    """Scrape each category/page URL with the configured default of 6 posts each."""
    limit = limit or default_limit('posts_per_category', 6)
    c = CdpClient(ctx.obj['base'])
    tab = pick_facebook_tab(c.list_tabs())
    if not tab:
        raise click.ClickException('NO_FACEBOOK_TAB')
    c.connect(tab)
    out = []
    try:
        for url in urls:
            navigate(c, url, wait)
            text = extract_text_snapshot(c)
            out.append({'category_url': get_location(c), 'limit': limit, 'posts': parse_posts_from_text(text, limit)})
        emit({'posts_per_category': limit, 'categories': out}, ctx.obj['json'])
    finally:
        c.close()

@cli.command('humanmode-post')
@json_option
@click.option('--text', required=True, help='Post text; explicit user intent required')
@click.option('--image', required=True, type=click.Path(exists=True), help='Local image path')
@click.pass_context
def humanmode_post(ctx, text, image):
    """Post via the Facebook HumanMode skill (write action)."""
    cmd = ['npx', 'tsx', 'scripts/post_topic_humanmode.ts', text, image]
    res = subprocess.run(cmd, cwd=str(HUMANMODE_DIR), text=True, capture_output=True, timeout=180)
    data = {'ok': res.returncode == 0, 'stdout': res.stdout[-4000:], 'stderr': res.stderr[-4000:]}
    if res.returncode != 0:
        raise click.ClickException(json.dumps(data, ensure_ascii=False))
    emit(data, ctx.obj['json'])


if __name__ == '__main__':
    cli()
