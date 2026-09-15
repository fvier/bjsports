"""Combo com matrícula por modalidade em servidor local de ensaio."""
import json,os
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright,expect
base=os.environ['BJ_UI_BASE_URL'].rstrip('/')
assert urlparse(base).hostname in {'127.0.0.1','localhost'}
output=Path(os.environ.get('BJ_UI_OUTPUT','/tmp/bj-fixed-ui'));output.mkdir(parents=True,exist_ok=True)
results=[]
with sync_playwright() as playwright:
 browser=playwright.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
 for width,cpf in ((390,'52998224725'),(1440,'11144477735')):
  context=browser.new_context(viewport={'width':width,'height':900});page=context.new_page();errors=[]
  page.on('pageerror',lambda error:errors.append(str(error)))
  page.goto(base+'/login?mode=register')
  username=f'fixed_ui_{width}'
  for field,value in {'regUsername':username,'regName':'Aluno Fixo de Ensaio','regCpf':cpf,'regBirthDate':'1990-01-01',
                      'regPhoneNumber':'999999999','regEmail':username+'@example.invalid','regPass':'Ensaio12345','regPassConfirm':'Ensaio12345'}.items():page.locator('#'+field).fill(value)
  page.locator('#regDDD').select_option('83');page.locator('#regSex').select_option('prefer_not')
  page.locator('#btnTypeCombos').click();page.locator('#regPlan').select_option(label='Combo de ensaio')
  modalities=page.locator('[data-combo-slot] select:not(:disabled)')
  modalities.nth(0).select_option('Boxe');modalities.nth(1).select_option('Jiu-Jitsu')
  section=page.locator('#registrationClasses')
  expect(section.locator('.registration-class-card')).to_have_count(4)
  for summary in section.locator('.registration-class-list summary').all():summary.click()
  boxe=section.locator('.registration-class-card').filter(has=page.get_by_role('heading',name='Boxe manhã',exact=True))
  full=section.locator('.registration-class-card').filter(has=page.get_by_role('heading',name='Boxe noite',exact=True))
  kids=section.locator('.registration-class-card').filter(has=page.get_by_role('heading',name='Jiu-Jitsu Kids',exact=True))
  adult=section.locator('.registration-class-card').filter(has=page.get_by_role('heading',name='Jiu-Jitsu adulto',exact=True))
  expect(full.locator('input')).to_be_disabled();expect(kids.locator('input')).to_be_disabled()
  boxe.locator('input').check();adult.locator('input').check()
  expect(section.locator('input:checked')).to_have_count(2)
  expect(section.locator('[data-training-summary]')).to_contain_text('Turma para matrícula: Jiu-Jitsu adulto')
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  section.locator('[data-training-summary]').scroll_into_view_if_needed();page.screenshot(path=str(output/f'combo-{width}.png'))
  page.locator('#btnRegisterSubmit').click();page.wait_for_url('**/dashboard')
  expect(page.locator('.welcome-training-choice')).to_have_count(2)
  expect(page.locator('.welcome-training-choices')).to_contain_text('Matrícula na turma')
  page.goto(base+'/calendario.html');expect(page.locator('.calendar-my-choice').first).to_have_text('Matrícula na turma')
  assert not errors,errors
  results.append({'width':width,'combo_registered':True,'enrollments':2,'full_disabled':True,'age_validated':True,'calendar':True,'javascript_errors':0})
  context.close()
 browser.close()
(output/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2));print(json.dumps({'flows':len(results)}))
