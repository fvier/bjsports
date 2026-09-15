"""Cadastro real no navegador contra servidor de ensaio, nunca produção."""
import json, os
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, expect

base = os.environ['BJ_UI_BASE_URL'].rstrip('/')
assert urlparse(base).hostname in {'localhost', '127.0.0.1'}
output = Path(os.environ.get('BJ_UI_OUTPUT', '/tmp/bj-registration-choices-ui'))
output.mkdir(parents=True, exist_ok=True)

def cpf(index):
    digits = [int(x) for x in f'913450{index:03d}']
    for size in (10, 11):
        value = sum(digit*(size-i) for i,digit in enumerate(digits)) % 11
        digits.append(0 if value < 2 else 11-value)
    return ''.join(map(str,digits))

results = []
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox'])
    for index, (width, theme) in enumerate(((390,'dark'),(390,'light'),(1440,'dark'),(1440,'light')), 1):
        context = browser.new_context(viewport={'width':width, 'height':900})
        context.add_init_script('localStorage.setItem("bjSportsTheme", '+json.dumps(theme)+')')
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(base+'/login?mode=register')
        username = f'choices_ui_{index}'
        for field, value in {'regUsername':username, 'regName':'Aluno de Ensaio', 'regCpf':cpf(index),
                             'regBirthDate':'1990-01-01', 'regPhoneNumber':'999999999',
                             'regEmail':username+'@example.invalid', 'regPass':'Ensaio12345',
                             'regPassConfirm':'Ensaio12345'}.items():
            page.locator('#'+field).fill(value)
        page.locator('#regDDD').select_option('83')
        page.locator('#regSex').select_option('prefer_not')
        page.locator('#regPlan').select_option(label='Boxe')
        section = page.locator('#registrationClasses')
        expect(section.locator('[data-select-class]')).to_have_count(2)
        first = section.locator('[data-select-class]').first
        first.focus()
        page.keyboard.press('Space')
        expect(first).to_be_checked()
        expect(section.locator('[data-training-summary]')).to_contain_text('Preferência: Boxe manhã')
        section.locator('[data-select-class]').last.check()
        expect(section.locator('[data-select-class]:checked')).to_have_count(2)
        # Créditos permitem preferências inclusive em turma cheia, sem matrícula.
        page.reload()
        expect(section.locator('[data-select-class]:checked')).to_have_count(2)
        for field in ('regPass','regPassConfirm'):
            page.locator('#'+field).fill('Ensaio12345')
        section.scroll_into_view_if_needed()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=str(output/f'cadastro-{width}-{theme}.png'))
        page.locator('#btnRegisterSubmit').click()
        page.wait_for_url('**/dashboard', timeout=15000)
        choices = page.locator('.welcome-training-choices')
        expect(choices.locator('.welcome-training-choice')).to_have_count(2)
        expect(choices).to_contain_text('sem reserva de vaga')
        choices.scroll_into_view_if_needed()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=str(output/f'painel-{width}-{theme}.png'))
        page.goto(base+'/calendario.html')
        expect(page.locator('.calendar-my-choice').first).to_have_text('Seu horário de preferência')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=str(output/f'calendario-{width}-{theme}.png'))
        page.goto(base+'/presencas')
        slot = page.locator('select[name=class_slot]')
        expect(slot).to_be_visible()
        value = slot.locator('option').evaluate_all('(options)=>options.find(o=>o.value)?.value')
        assert value
        slot.select_option(value)
        form = slot.locator('xpath=ancestor::form')
        form.locator('button[type=submit]').click()
        expect(page.get_by_text('Check-in enviado!', exact=False).first).to_be_visible()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=str(output/f'checkin-{width}-{theme}.png'))
        assert not errors, errors
        results.append({'width':width,'theme':theme,'account_created':True,'preferences_persisted':2,
                        'draft_recovered':True,'keyboard_selection':True,'calendar_verified':True,
                        'checkin_sent':True,'overflow':False,'javascript_errors':0})
        context.close()
    browser.close()
(output/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print(json.dumps({'flows':len(results),'production_writes':False}))
