from cli_anything.facebook_automato.utils.cdp import sanitize_cookie_summary, parse_posts_from_text


def test_cookie_summary_masks_values():
    s = sanitize_cookie_summary([{'name':'c_user','value':'615123456'}, {'name':'xs','value':'secret'}])
    assert s['has_c_user'] is True
    assert s['has_xs'] is True
    assert s['user_id_masked'] == '615***'
    assert 'secret' not in str(s)


def test_parse_posts_snapshot():
    posts = parse_posts_from_text('Alice\nHello world\nLike\nComment\nShare', 5)
    assert posts


def test_humanmode_post_command_registered():
    from click.testing import CliRunner
    from cli_anything.facebook_automato.facebook_automato_cli import cli
    result = CliRunner().invoke(cli, ['humanmode-post', '--help'])
    assert result.exit_code == 0
    assert 'Post via the Facebook HumanMode skill' in result.output
