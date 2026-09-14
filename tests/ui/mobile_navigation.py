"""Smoke test de layout/teclado em um servidor local já preparado.
Requer Playwright e Chrome. BJ_UI_BASE_URL, BJ_UI_TEST_USERNAME e
BJ_UI_TEST_PASSWORD devem apontar para contas de um banco descartável.
"""
import json
import os
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, expect

base = os.environ['BJ_UI_BASE_URL'].rstrip('/')
assert urlparse(base).hostname in {'127.0.0.1', 'localhost'}, 'Use um servidor local de testes.'
output = Path(os.environ.get('BJ_UI_OUTPUT', '/tmp/bj-mobile-ui-results'))
output.mkdir(parents=True, exist_ok=True)
results = []
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(executable_path=os.environ.get('BJ_UI_CHROME', '/usr/bin/google-chrome'), headless=True, args=['--no-sandbox'])
    for width in (320, 390, 768):
        context = browser.new_context(viewport={'width': width, 'height': 844}, has_touch=True, is_mobile=width < 768)
        page = context.new_page()
        for kind in ('public', 'portal'):
            if kind == 'public':
                page.goto(base + '/')
                toggle, panel, close, backdrop = '#mobileNavToggle', '#mobileNavDrawer', '#mobileDrawerClose', '#mobileNavOverlay'
            else:
                page.goto(base + '/login')
                page.locator('#portalCpf').fill(os.environ['BJ_UI_TEST_USERNAME'])
                page.locator('#portalPassword').fill(os.environ['BJ_UI_TEST_PASSWORD'])
                page.locator('#btnLoginSubmit').click()
                page.wait_for_url('**/dashboard')
                toggle, panel, close, backdrop = '#erpHambergerBtn', '#erpSidebar', '#erpSidebarClose', '#erpSidebarBackdrop'
            assert page.evaluate('document.documentElement.scrollWidth') <= width
            assert page.locator(panel).evaluate('(e)=>e.inert')
            page.locator(toggle).click()
            expect(page.locator(close)).to_be_focused()
            expect(page.locator(panel)).to_have_attribute('aria-modal', 'true')
            page.keyboard.press('Shift+Tab')
            assert page.locator(panel).evaluate('(e)=>e.contains(document.activeElement)')
            page.keyboard.press('Tab')
            expect(page.locator(close)).to_be_focused()
            page.screenshot(path=str(output / f'menu-{kind}-{width}.png'))
            page.keyboard.press('Escape')
            expect(page.locator(toggle)).to_be_focused()
            page.locator(toggle).click()
            page.locator(backdrop).click(position={'x': 5 if kind == 'public' else width - 5, 'y': 400})
            expect(page.locator(toggle)).to_have_attribute('aria-expanded', 'false')
            page.locator(toggle).click()
            page.set_viewport_size({'width': 1440, 'height': 900})
            page.wait_for_function('!document.body.classList.contains("navigation-drawer-open")')
            if kind == 'portal':
                assert not page.locator(panel).evaluate('(e)=>e.inert')
                page.locator(toggle).click()
                expect(page.locator(toggle)).to_have_attribute('aria-expanded', 'false')
                page.locator(toggle).click()
                expect(page.locator(toggle)).to_have_attribute('aria-expanded', 'true')
            page.set_viewport_size({'width': width, 'height': 844})
            page.wait_for_function('(selector)=>document.querySelector(selector).inert', arg=panel)
            results.append({'width': width, 'menu': kind, 'keyboard_backdrop_resize': True})
        context.close()
    browser.close()
(output / 'navigation-results.json').write_text(json.dumps(results, indent=2))
print(json.dumps(results))
