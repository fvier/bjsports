"""Validação da gestão unificada; execute apenas em banco/servidor descartáveis.
Requer Playwright e BJ_UI_BASE_URL, BJ_UI_TEST_USERNAME, BJ_UI_TEST_PASSWORD.
Cria e exclui planos técnicos; não deve apontar para produção.
"""
import json
import os
import time
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, expect

base = os.environ['BJ_UI_BASE_URL'].rstrip('/')
assert urlparse(base).hostname in {'127.0.0.1', 'localhost'}, 'Use servidor local descartável.'
output = Path(os.environ.get('BJ_UI_OUTPUT', '/tmp/bj-management-ui'))
output.mkdir(parents=True, exist_ok=True)
results = []

def check_layout(page, width, label):
    size = page.evaluate('({viewport: innerWidth, content: document.documentElement.scrollWidth})')
    assert size['content'] <= size['viewport'], (label, size)
    results.append({'page': label, 'width': width, **size})

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(executable_path=os.environ.get('BJ_UI_CHROME', '/usr/bin/google-chrome'), headless=True, args=['--no-sandbox'])
    for width in (360, 390, 768, 1440):
        context = browser.new_context(viewport={'width': width, 'height': 900})
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(base + '/login')
        page.locator('#portalCpf').fill(os.environ['BJ_UI_TEST_USERNAME'])
        page.locator('#portalPassword').fill(os.environ['BJ_UI_TEST_PASSWORD'])
        page.locator('#btnLoginSubmit').click()
        page.wait_for_url('**/dashboard')
        for theme in ('dark', 'light'):
            page.evaluate('(theme) => localStorage.setItem("bjSportsTheme", theme)', theme)
            page.goto(base + '/gestao_turmas.html', wait_until='networkidle')
            expect(page.locator('h1')).to_have_text('Turmas e planos')
            expect(page.locator('.management-tabs [aria-current]')).to_have_text('Turmas')
            assert page.locator('.erp-sidebar a[href*="planos_admin"]').count() == 0
            check_layout(page, width, 'turmas-' + theme)
            page.locator('.management-tabs a').filter(has_text='Planos').click()
            page.wait_for_url('**/gestao_turmas.html?tab=plans')
            expect(page.locator('.management-tabs [aria-current]')).to_have_text('Planos')
            assert page.locator('[data-class-modal]').count() == 0
            expect(page.locator('[data-plan-panel="modalities"]')).to_be_visible()
            check_layout(page, width, 'individuais-' + theme)
            page.screenshot(path=str(output / f'plans-{width}-{theme}.png'))
            page.locator('[data-plan-tab="plans"]').focus()
            page.keyboard.press('Enter')
            expect(page.locator('[data-plan-tab="plans"]')).to_have_attribute('aria-pressed', 'true')
            expect(page.locator('[data-plan-panel="modalities"]')).to_be_hidden()
            page.reload(wait_until='networkidle')
            expect(page.locator('[data-plan-panel="plans"]')).to_be_visible()
            check_layout(page, width, 'combos-' + theme)
            page.screenshot(path=str(output / f'combos-{width}-{theme}.png'))
        if width in (390, 1440):
            page.goto(base + '/planos_admin.html?tab=plans')
            expect(page.locator('[data-plan-panel="plans"]')).to_be_visible()
            assert '/gestao_turmas.html?' in page.url
            page.locator('[data-plan-tab="modalities"]').click()
            page.locator('.plan-catalog-heading [data-plan-create-toggle]').click()
            form = page.locator('.plan-catalog-form')
            name = f'Plano navegador {width} {time.time_ns()}'
            expect(form.locator('[name="name"]')).to_be_focused()
            form.locator('[name="name"]').fill(name)
            form.locator('[name="price_ter_qui"]').fill('valor inválido')
            form.locator('[name="price_seg_qua_sex"]').fill('R$ 100,00/mês')
            form.locator('[name="price_all_days"]').fill('R$ 120,00/mês')
            form.locator('label:has(input[name="modalities"][value="Boxe"])').click()
            form.locator('[name="features"]').fill('Benefício preservado')
            with page.expect_response(lambda response: response.request.method == 'POST' and '/gestao_turmas' in response.url) as submitted:
                form.locator('button[type="submit"]').click()
            assert submitted.value.status == 400
            expect(page.locator('#planFormErrors')).to_be_focused()
            expect(form).to_be_visible()
            expect(form.locator('[name="name"]')).to_have_value(name)
            expect(form.locator('[name="features"]')).to_have_value('Benefício preservado')
            expect(form.locator('input[name="modalities"][value="Boxe"]')).to_be_checked()
            check_layout(page, width, 'erro-criacao')
            form.locator('[name="price_ter_qui"]').fill('R$ 90,00/mês')
            with page.expect_navigation():
                form.locator('button[type="submit"]').click()
            row = page.locator('[data-plan-panel="modalities"] tr').filter(has_text=name).first
            expect(row).to_be_visible()
            row.locator('[name="price_ter_qui"]').fill('R$ 95,00/mês')
            with page.expect_navigation():
                row.locator('button[title="Salvar alterações"]').click()
            row = page.locator('[data-plan-panel="modalities"] tr').filter(has_text=name).first
            expect(row.locator('[name="price_ter_qui"]')).to_have_value('R$ 95,00/mês')
            row.scroll_into_view_if_needed()
            page.screenshot(path=str(output / f'edit-{width}.png'))
            row.locator('button[title="Excluir"]').click()
            with page.expect_navigation():
                page.get_by_role('button', name='Sim, Excluir', exact=True).click()
            assert page.locator('[data-plan-panel="modalities"] tr').filter(has_text=name).count() == 0
            results.append({'width': width, 'create_error_restored': True, 'create_edit_delete': True, 'legacy_redirect': True})
        assert not errors, errors
        context.close()
    browser.close()
(output / 'results.json').write_text(json.dumps(results, ensure_ascii=False, indent=2))
print(json.dumps({'checks': len(results), 'results': results}, ensure_ascii=False))
