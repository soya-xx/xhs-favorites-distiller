#!/usr/bin/env python3
"""Optional Playwright page capture, using a private persistent browser profile."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys


def capture(url, data_dir, *, login=False, headed=False, wait_for=None):
    from playwright.sync_api import sync_playwright

    root = Path(data_dir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    profile = root / 'browser-profile'
    profile.mkdir(exist_ok=True, mode=0o700)
    with sync_playwright() as pw:
        context = pw.chromium.launch_persistent_context(
            str(profile), headless=not (headed or login), viewport={'width': 1280, 'height': 900})
        try:
            page = context.pages[0] if context.pages else context.new_page()
            response = page.goto(url, wait_until='domcontentloaded', timeout=45000)
            if login:
                input('Complete login in the browser, then press Enter here. ')
            if wait_for:
                page.locator(wait_for).first.wait_for(state='visible', timeout=30000)
            # Capturing a page is not proof of login, source success or article completeness.
            body = page.locator('body').inner_text()
            links = page.locator('a[href]').evaluate_all(
                '(els) => els.map(e => ({text:e.innerText, url:e.href}))')
            images = page.locator('img').evaluate_all(
                '(els) => els.map(e => ({alt:e.alt, url:e.currentSrc || e.src}))')
            output = root / 'evidence' / datetime.now(timezone.utc).strftime('browser-%Y%m%dT%H%M%S%fZ')
            output.mkdir(parents=True)
            page.screenshot(path=str(output / 'page.png'), full_page=True)
            result = {'url': page.url, 'title': page.title(), 'http_status': response.status if response else None,
                      'text': body, 'links': links, 'images': images, 'complete': False,
                      'source_status': 'unverified', 'screenshot': str(output / 'page.png')}
            (output / 'page.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
            return output
        finally:
            context.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('url', help='User-provided or observed URL; never guess private note URLs')
    parser.add_argument('--data-dir', type=Path, default=Path(os.environ.get(
        'SAVED_TO_PRACTICE_DATA', str(Path.home()/'.local/share/saved-to-practice'))))
    parser.add_argument('--login', action='store_true', help='Open visible browser and wait for user login')
    parser.add_argument('--headed', action='store_true')
    parser.add_argument('--wait-for', help='Observed CSS selector to wait for on a dynamic page')
    args = parser.parse_args()
    if args.login and not sys.stdin.isatty():
        parser.exit(2, 'Login requires an interactive terminal; run with a PTY.\n')
    try:
        output = capture(args.url, args.data_dir, login=args.login, headed=args.headed, wait_for=args.wait_for)
    except ImportError:
        parser.exit(2, 'Configured Playwright runtime is unavailable.\n')
    except Exception as error:
        # Do not echo exceptions containing signed navigation URLs to shared logs.
        parser.exit(2, f'Browser capture failed ({type(error).__name__}). Check browser installation, login, URL and selector; no inbox progress advanced.\n')
    print(json.dumps({'capture_dir': str(output), 'source_status': 'unverified'}))


if __name__ == '__main__':
    main()
