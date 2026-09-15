"""Public catalog browser checks. Uses mocked share/clipboard; sends no messages.
Run with a disposable browser profile against local or published STORE_BASE_URL.
"""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

base = os.environ.get('STORE_BASE_URL', 'http://127.0.0.1:37994')
out = Path(os.environ.get('STORE_EVIDENCE_DIR', '/tmp/bj-store-20260914/ui'))
out.mkdir(parents=True, exist_ok=True)
results = []
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox'])
    for width in (360, 390, 1440):
        context = browser.new_context(viewport={'width': width, 'height': 900}, is_mobile=width < 600, has_touch=width < 600)
        context.add_init_script("""
          window.shareCalls = []; window.copiedLinks = []; window.shareMode = 'success';
          Object.defineProperty(navigator, 'share', {configurable: true, value: async data => {
            window.shareCalls.push(data);
            if (window.shareMode === 'cancel') throw new DOMException('Cancelled', 'AbortError');
            if (window.shareMode === 'denied') throw new DOMException('Denied', 'NotAllowedError');
          }});
          Object.defineProperty(navigator, 'clipboard', {configurable: true, value: {writeText: async text => {
            if (window.clipboardDenied) throw new DOMException('Denied', 'NotAllowedError');
            window.copiedLinks.push(text);
          }}});
          localStorage.setItem('bj-sports-store-interest', 'corrupt-json');
        """)
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        response = page.goto(base + '/loja.html', wait_until='networkidle')
        assert response.status == 200
        card = page.locator('.store-product-card[data-id="BJJ-001"]')
        expect(card.locator('.card-price')).to_have_text('R$ 459,90')
        expect(card.locator('[data-color-id="preto"]')).to_have_attribute('aria-pressed', 'true')
        for color, label, price in [('branco', 'Branco', '439,90'), ('azul', 'Azul Royal', '449,90'), ('preto', 'Preto', '459,90')]:
            card.locator(f'[data-color-id="{color}"]').click()
            expect(card.locator('.card-price')).to_have_text('R$ ' + price)
            expect(card.locator('.card-img-element')).to_have_attribute('src', f'/static/img/store/kimono_{color}_frente_costas_v1.png')
            card.locator('[data-share-product]').click()
            payload = page.evaluate('window.shareCalls.at(-1)')
            assert payload['url'] == base + f'/loja.html?produto=BJJ-001&cor={color}'
            assert label in payload['text']
            expect(page.locator('#storeProductModal')).to_be_hidden()
            card.locator('.store-quickview-btn').click()
            expect(page.locator('#modalSelectedColorText')).to_have_text(label)
            expect(page.locator('#modalPrice')).to_have_text('R$ ' + price)
            page.locator('#modalSizePills button', has_text='A3').click()
            page.locator('#modalColorPills button').last.click()
            expect(page.locator('#modalSizePills button.active')).to_have_text('A3')
            page.locator('#modalShareBtn').click()
            assert page.evaluate('window.shareCalls.at(-1).url').endswith('cor=azul')
            page.locator('#closeProductModal').focus()
            page.keyboard.press('Shift+Tab')
            expect(page.locator('#modalShareBtn')).to_be_focused()
            page.keyboard.press('Tab')
            expect(page.locator('#closeProductModal')).to_be_focused()
            page.keyboard.press('Escape')
            expect(card.locator('.store-quickview-btn')).to_be_focused()
        card.locator('[data-color-id="branco"]').click()
        card.evaluate("el => el.scrollIntoView({block: 'center'})")
        card.screenshot(path=str(out / f'card-{width}.png'))
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Page overflows horizontally'
        media = card.locator('.store-product-media').bounding_box()
        img = card.locator('.card-img-element').bounding_box()
        assert img['height'] <= media['height'] + 1 and img['width'] <= media['width'] + 1
        page.evaluate("window.shareMode = 'cancel'; window.copiedLinks = []")
        card.locator('[data-share-product]').click()
        assert page.evaluate('window.copiedLinks.length') == 0
        expect(card.locator('.store-share-status')).to_be_empty()
        page.evaluate("window.shareMode = 'denied'")
        card.locator('[data-share-product]').click()
        expect(card.locator('.store-share-status')).to_contain_text('Link copiado')
        assert page.evaluate('window.copiedLinks.at(-1)').endswith('cor=branco')
        page.evaluate("Object.defineProperty(navigator, 'share', {value: undefined}); window.clipboardDenied = true")
        card.locator('[data-share-product]').click()
        expect(card.locator('.store-share-copy input')).to_be_visible()
        expect(card.locator('.store-share-copy input')).to_have_value(base + '/loja.html?produto=BJJ-001&cor=branco')
        card.locator('.store-quickview-btn').click()
        page.locator('#modalInterestBtn').click()
        expect(page.locator('#interestCount')).to_have_text('1')
        page.locator('#modalInterestBtn').click()
        expect(page.locator('#interestCount')).to_have_text('0')
        page.goto(base + '/loja.html?produto=BJJ-001&cor=azul&ignored=discard', wait_until='networkidle')
        expect(page.locator('#storeProductModal')).to_be_visible()
        expect(page.locator('#modalSelectedColorText')).to_have_text('Azul Royal')
        expect(page.locator('#modalMainImg')).to_have_attribute('src', '/static/img/store/kimono_azul_frente_costas_v1.png')
        page.locator('#storeProductModal').screenshot(path=str(out / f'modal-{width}.png'))
        assert page.locator('#modalMainImg').evaluate('(img) => img.complete && img.naturalWidth > 1000')
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
        page.goto(base + '/loja.html?produto=BJJ-001&cor=invalid', wait_until='networkidle')
        expect(page.locator('#modalSelectedColorText')).to_have_text('Preto')
        page.goto(base + '/loja.html?produto=invalid&cor=azul', wait_until='networkidle')
        expect(page.locator('#storeProductModal')).to_be_hidden()
        assert not errors, errors
        results.append({'width': width, 'status': 'passed', 'javascript_errors': errors, 'native_share': 'mocked', 'clipboard': 'mocked'})
        context.close()
    browser.close()
(out / 'results.json').write_text(json.dumps({'base_url': base, 'checks': results}, indent=2))
print(json.dumps(results))
