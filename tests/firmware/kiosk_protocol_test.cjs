const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync('templates/catraca_app.html', 'utf8');
for (const match of html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)) new vm.Script(match[1]);
const start = html.indexOf('    let unlockInFlight');
const end = html.indexOf('    let currentCpf', start);
const protocol = html.slice(start, end);
function context(responses, settings = {}) {
  const calls = [];
  const values = {bj_esp32_ip: 'http://192.168.1.2', bj_esp32_key: 'a'.repeat(48), ...settings};
  const ctx = vm.createContext({
    localStorage: {getItem: key => values[key]}, AbortController,
    crypto: {randomUUID: () => '28e46453-49ad-4cae-a519-ad8932983013'},
    fetch: async (url, options) => {calls.push({url, options}); const item = responses.shift(); if (item instanceof Error) throw item; return item;},
    setTimeout: () => 1, clearTimeout: () => {}, resetTimer: null,
    feedbackDesc: {}, feedbackTitle: {}, container: {},
    resetToStandby: () => {}, playBeep: () => {}, TypeError, Error,
  });
  vm.runInContext(protocol, ctx);
  return {ctx, calls, run: () => vm.runInContext('triggerTurnstileUnlock()', ctx)};
}
const response = (body, ok = true) => ({ok, json: async () => body});
const status = () => response({ready:true, pulso_ativo:false, boot_id:'boot', uptime_ms:100});
(async () => {
  let t = context([status(), response({success:true, state:'command_accepted', command_id:'28e46453-49ad-4cae-a519-ad8932983013'})]);
  assert.equal(await t.run(), true);
  assert.equal(t.calls.length, 2);
  assert.equal(t.calls[1].options.mode, 'cors');
  assert.equal(t.calls[1].options.headers['X-Expires-Ms'], '5100');
  assert.match(t.ctx.feedbackDesc.textContent, /Pulso confirmado/);
  t = context([response({}, false)]); assert.equal(await t.run(), false); assert.equal(t.calls.length, 1);
  t = context([status(), response({}, false)]); assert.equal(await t.run(), false); assert.equal(t.calls.length, 2);
  t = context([status(), response({success:true, state:'command_accepted', command_id:'other'})]); assert.equal(await t.run(), false);
  t = context([status(), new TypeError('network')]); assert.equal(await t.run(), false); assert.equal(t.calls.length, 2);
  t = context([], {bj_esp32_key:''}); assert.equal(await t.run(), false); assert.equal(t.calls.length, 0);
  t = context([response({ready:true,pulso_ativo:true,boot_id:'boot',uptime_ms:100})]); assert.equal(await t.run(), false); assert.equal(t.calls.length, 1);
  console.log('Kiosk: syntax and 7 protocol scenarios passed');
})().catch(error => {console.error(error); process.exitCode=1;});
