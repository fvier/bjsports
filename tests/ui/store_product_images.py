"""Inspect the four refreshed catalog images without sending messages."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
base=os.environ.get('STORE_BASE_URL','http://127.0.0.1:37995')
out=Path(os.environ.get('STORE_EVIDENCE_DIR','/tmp/bj-apparel-20260914/ui'));out.mkdir(parents=True,exist_ok=True)
products={'BJJ-004':'rashguard_eagle_studio_v1.png','BJJ-005':'fight_shorts_grappling_studio_v1.png','BJJ-006':'fight_shorts_brasil_studio_v1.png','BJJ-007':'rashguard_camuflada_studio_v1.png'}
results=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
 for width in (360,390,1440):
  context=browser.new_context(viewport={'width':width,'height':1000},is_mobile=width<600,has_touch=width<600)
  context.add_init_script("window.shared=[]; Object.defineProperty(navigator,'share',{value:async data=>window.shared.push(data)});")
  page=context.new_page();errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
  assert page.goto(base+'/loja.html',wait_until='networkidle').status==200
  for pid,filename in products.items():
   card=page.locator(f'.store-product-card[data-id="{pid}"]')
   card.evaluate("el=>el.scrollIntoView({block:'center'})")
   img=card.locator('.card-img-element')
   expect(img).to_have_attribute('src','/static/img/store/'+filename)
   page.wait_for_function('(selector)=>{const img=document.querySelector(selector);return img.complete&&img.naturalWidth>1000}',arg=f'.store-product-card[data-id="{pid}"] img.card-img-element')
   rect=img.bounding_box();media=card.locator('.store-product-media').bounding_box()
   assert abs(media['width']-media['height'])<2
   assert rect['height']<=media['height']+1 and rect['width']<=media['width']+1
   card.screenshot(path=str(out/f'{pid}-{width}.png'))
   card.locator('[data-share-product]').click()
   link=page.evaluate('window.shared.at(-1).url');assert 'produto='+pid in link
   card.locator('.store-quickview-btn').click()
   expect(page.locator('#modalMainImg')).to_have_attribute('src','/static/img/store/'+filename)
   expect(page.locator('#modalPrice')).to_have_text(card.locator('.card-price').inner_text())
   page.keyboard.press('Escape')
   results.append({'width':width,'product':pid,'image_loaded':True,'whole_image':True,'details':True,'share_link':link})
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  assert not errors,errors
  page.goto(base+'/loja.html?produto=BJJ-007',wait_until='networkidle')
  expect(page.locator('#storeProductModal')).to_be_visible()
  expect(page.locator('#modalMainImg')).to_have_attribute('src','/static/img/store/rashguard_camuflada_studio_v1.png')
  page.locator('#storeProductModal').screenshot(path=str(out/f'camo-details-{width}.png'))
  context.close()
 browser.close()
(out/'results.json').write_text(json.dumps({'base_url':base,'products':results,'sharing':'mocked; no messages sent'},indent=2))
print(json.dumps({'checks':len(results),'viewports':[360,390,1440],'status':'passed'}))
