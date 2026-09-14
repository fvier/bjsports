"""Ensaio do editor de idades em servidor local com dados técnicos apenas."""
import json
import os
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, expect

base = os.environ['BJ_UI_BASE_URL'].rstrip('/')
assert urlparse(base).hostname in {'127.0.0.1', 'localhost'}, 'Use banco e servidor descartáveis.'
group_id = int(os.environ['BJ_UI_CLASS_ID'])
output = Path(os.environ.get('BJ_UI_OUTPUT', '/tmp/bj-class-age-ui'))
output.mkdir(parents=True, exist_ok=True)
results = []
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox'])
    for width in (390, 1440):
        context = browser.new_context(viewport={'width': width, 'height': 900})
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(base + '/login')
        page.locator('#portalCpf').fill(os.environ['BJ_UI_TEST_USERNAME'])
        page.locator('#portalPassword').fill(os.environ['BJ_UI_TEST_PASSWORD'])
        page.locator('#btnLoginSubmit').click()
        page.wait_for_url('**/dashboard')
        page.goto(base + '/gestao_turmas.html')
        button = page.locator(f'.class-management-edit[data-class-id="{group_id}"]')
        button.click()
        form = page.locator('.class-editor-form')
        minimum = form.locator('[name="class_min_age"]')
        maximum = form.locator('[name="class_max_age"]')
        minimum.fill('14')
        maximum.fill('7')
        with page.expect_navigation():
            form.locator('button[type="submit"]').click()
        expect(form).to_be_visible()
        expect(minimum).to_have_value('14')
        expect(maximum).to_have_value('7')
        expect(page.get_by_text('A idade máxima deve ser igual ou maior que a idade mínima.', exact=True).first).to_be_visible()
        minimum.fill('7')
        maximum.fill('12')
        with page.expect_navigation():
            form.locator('button[type="submit"]').click()
        expect(button).to_have_attribute('data-class-min-age', '7')
        expect(button).to_have_attribute('data-class-max-age', '12')
        for theme in ('light', 'dark'):
            page.evaluate('(theme) => localStorage.setItem("bjSportsTheme", theme)', theme)
            page.reload(wait_until='networkidle')
            button.click()
            expect(minimum).to_have_value('7')
            expect(maximum).to_have_value('12')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            minimum.scroll_into_view_if_needed()
            page.screenshot(path=str(output / f'age-editor-{width}-{theme}.png'))
            results.append({'width': width, 'theme': theme, 'limits_reloaded': True, 'overflow': False})
            form.locator('[data-class-modal-close]').click()
        button.click()
        minimum.fill('')
        maximum.fill('')
        with page.expect_navigation():
            form.locator('button[type="submit"]').click()
        expect(button).to_have_attribute('data-class-min-age', '')
        expect(button).to_have_attribute('data-class-max-age', '')
        results.append({'width': width, 'invalid_range_preserved': True, 'save_reload_clear': True})
        assert not errors, errors
        context.close()
    browser.close()
(output / 'results.json').write_text(json.dumps(results, ensure_ascii=False, indent=2))
print(json.dumps({'checks': len(results), 'javascript_errors': 0}))
