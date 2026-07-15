// Validate the inline <script> of a Paris-guide page WITHOUT a browser.
// Runs the page's last inline script against stubbed Leaflet/DOM so syntax or
// runtime errors surface here instead of as a blank published page.
//
// Usage:  node tools/validate.js crepes.html
// Prints "OK: …" and exits 0 on success; prints "FAIL: <message>" and exits 1 otherwise.

const fs = require('fs');

const file = process.argv[2];
if (!file) { console.error('usage: node tools/validate.js <page>.html'); process.exit(2); }

const html = fs.readFileSync(file, 'utf8');
// Grab every inline <script> (no src=), validate the LAST one (the page logic).
const scripts = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]);
const code = scripts[scripts.length - 1];
if (!code) { console.error('no inline script found'); process.exit(2); }

// L = a swallow-everything proxy so any Leaflet call/chain/new is harmless.
const L = new Proxy(function () {}, { get: () => L, apply: () => L, construct: () => L });
const el = new Proxy({ style: {} }, {
  get: (t, p) => (p in t ? t[p] : (p === 'appendChild' ? () => {} : (p === 'innerHTML' ? '' : L))),
  set: () => true,
});
const document = {
  getElementById: () => el,
  createElement: () => ({ style: {}, set innerHTML(v) {}, appendChild() {} }),
};
const window = { matchMedia: () => ({ matches: false }) };

try {
  new Function('L', 'document', 'window', 'encodeURIComponent', code)(L, document, window, encodeURIComponent);
  console.log('OK: script parsed and ran without throwing');
} catch (e) {
  console.error('FAIL:', e.message);
  process.exit(1);
}
