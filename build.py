"""Assemble Lab 3 Bench: artifact version (three.js from cdnjs) and GitHub Pages version (three.js inlined, PWA files)."""
import json, pathlib, re
B = pathlib.Path(__file__).parent
js = (B / 'p1_orig.js').read_text()

def rep(a, b, n=1):
    global js
    assert js.count(a) == n, (a[:70], js.count(a)); js = js.replace(a, b)

rep('''    document.querySelectorAll("#pick button").forEach(b => b.setAttribute("aria-pressed", b.dataset.key === item.key ? "true" : "false"));
    $("shapeSel").value = item.key;''',
'''    document.querySelectorAll("#molSel button").forEach(b => b.setAttribute("aria-pressed", b.dataset.key === item.key ? "true" : "false"));''')
rep('''    document.querySelectorAll("#pick .g").forEach(g => g.hidden = on);\n''', '')
start = js.index('  // ------------------------------------------------------------ shape pickers')
end = js.index('  // ------------------------------------------------------------ view controls')
js = js[:start] + '''  // ------------------------------------------------------------ molecule switch
  const molSel = $("molSel");
  for (const it of DATA) {
    const b = document.createElement("button"); b.type = "button"; b.dataset.key = it.key; b.setAttribute("aria-pressed", "false");
    b.innerHTML = "<span>" + (it.short || it.title) + "</span>"; b.addEventListener("click", () => load(it)); molSel.appendChild(b);
  }

''' + js[end:]
rep('''  $("bStudent").addEventListener("click", () => setStudent(!student));
  $("bPresent").addEventListener("click", () => setPresent(!present));\n''', '')
rep('''    if (e.target.closest && e.target.closest("input, select, textarea")) return;''',
    '''    if (!active) return;
    if (e.target.closest && e.target.closest("input, select, textarea")) return;''')
rep('''    else if (k === "p") setPresent(!present);
    else if (k === "s") setStudent(!student);
    else if (k === "escape") { if (walk) stopWalk(); else if (present) setPresent(false); }''',
    '''    else if (k === "escape") { if (walk) stopWalk(); }''')
rep('''    const w = stage.clientWidth, h = stage.clientHeight; renderer.setSize(w, h, false);''',
    '''    const w = stage.clientWidth, h = stage.clientHeight; if (!w || !h) return; renderer.setSize(w, h, false);''')
rep('''    renderer.render(scene, camera); placeLabels(); requestAnimationFrame(loop);''',
    '''    if (active) { renderer.render(scene, camera); placeLabels(); } requestAnimationFrame(loop);''')
rep('''  resize(); load(DATA[1]); requestAnimationFrame(loop);''',
    '''  resize(); load(DATA[0]); requestAnimationFrame(loop);
  window.P1 = { setActive(v) { active = v; if (v) { applyTheme(); resize(); } }, setStudent };''')
rep('''  let anim = null, slow = false, student = false, present = false;''',
    '''  let anim = null, slow = false, student = false, present = false, active = false;''')
rep('''    h += `<div class="note ans">${it.note}</div>`;''',
    '''    h += `<div class="note ans">${it.note}</div>`;
    if (it.ops) h += `<div class="sheet ans"><div class="k">Operations from each element</div><table class="t"><tbody>` +
      it.ops.map(o => `<tr class="${o[0] === "Total" ? "tot" : ""}"><td>${o[0]}</td><td class="n">${o[1]}</td></tr>`).join("") +
      `</tbody></table>${it.opsNote ? `<div class="note">${it.opsNote}</div>` : ""}</div>`;''')
# the info panel's sheet label line uses .k class markup; keep sheetLabel support
rep('''<div class="k">On the sheet: symmetry elements</div>''', '''<div class="k">${it.sheetLabel || "On the sheet: symmetry elements"}</div>''')

data = json.load(open(B / 'lab3_mols.json'))
cr, na = data
cr['short'] = 'Cr(CO)<sub>6</sub>'; na['short'] = 'Naphthalene'
for e in data: e['part'] = 'Part 1 · Symmetry'
pairs = {'C<sub>2</sub>(z)': 'Same atom swaps as <i>i</i>: on a flat molecule the atoms alone cannot tell them apart. Mark the top face (a dot above C<sub>1</sub>) to see the difference.',
         'C<sub>2</sub>(y)': 'Same atom swaps as σ(yz); only the top and bottom faces tell them apart.',
         'C<sub>2</sub>(x)': 'Same atom swaps as σ(xz); only the top and bottom faces tell them apart.'}
for c in na['classes']:
    if c['label'] in pairs: c['moves'] = [m + ' ' + pairs[c['label']] for m in c['moves']]
cr['ops'] = [["E", "1"], ["C<sub>4</sub>, C<sub>4</sub><sup>3</sup> · 3 axes", "6"], ["C<sub>2</sub> = C<sub>4</sub><sup>2</sup> · same 3 axes", "3"],
             ["C<sub>3</sub>, C<sub>3</sub><sup>2</sup> · 4 axes", "8"], ["C<sub>2</sub>′ · 6 axes", "6"], ["<i>i</i>", "1"],
             ["S<sub>4</sub>, S<sub>4</sub><sup>3</sup> · 3 axes", "6"], ["S<sub>6</sub>, S<sub>6</sub><sup>5</sup> · 4 axes", "8"],
             ["σ<sub>h</sub> · 3 planes", "3"], ["σ<sub>d</sub> · 6 planes", "6"], ["Total", "48"]]
cr['opsNote'] = 'Do not count twice: S<sub>4</sub><sup>2</sup> = C<sub>2</sub>, S<sub>6</sub><sup>2</sup> = C<sub>3</sub>, S<sub>6</sub><sup>3</sup> = <i>i</i>, and any element to the power n is E.'
na['ops'] = [["E", "1"], ["C<sub>2</sub>(z), C<sub>2</sub>(y), C<sub>2</sub>(x)", "3"], ["<i>i</i>", "1"], ["σ(xy), σ(xz), σ(yz)", "3"], ["Total", "8"]]

head = (B / 'bench_head.html').read_text(); body = (B / 'bench_body.html').read_text()
p2 = (B / 'p2.js').read_text(); p3 = (B / 'p3.js').read_text(); shell = (B / 'shell.js').read_text()
sheets_path = B / 'sheets.json'
sheets = json.loads(sheets_path.read_text()) if sheets_path.exists() else []
app = ('<script>\nwindow.LAB3_SHEETS = ' + json.dumps(sheets, ensure_ascii=False) + ';\nconst DATA = ' + json.dumps(data, ensure_ascii=False) + ';\n' + js + '\n' + p2 + '\n' + p3 + '\n' + shell + '\n</script>\n')
THREE_CDN = '<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>\n'
out = B / 'out'; out.mkdir(exist_ok=True)
(out / 'lab3-bench.html').write_text(head + body + THREE_CDN + app)

# ---- GitHub Pages bundle
three = (B / 'npmtmp/node_modules/three/build/three.min.js').read_text()
gh = B / 'out/github/lab3'; gh.mkdir(parents=True, exist_ok=True)
skel_head = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Lab 3 Bench">
<meta name="theme-color" content="#f3f5f8">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icon-180.png">
<link rel="icon" href="icon-192.png">
<style>:root{color-scheme:light;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;padding:0;font:14px -apple-system,BlinkMacSystemFont,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>
'''
sw_reg = '''<script>if ("serviceWorker" in navigator) { window.addEventListener("load", () => navigator.serviceWorker.register("sw.js").catch(() => {})); }</script>\n'''
gh_html = skel_head + head + '</head>\n<body>\n' + body + '<script>\n' + three + '\n</script>\n' + app + sw_reg + '</body>\n</html>\n'
(gh / 'index.html').write_text(gh_html)
(gh / 'manifest.webmanifest').write_text(json.dumps({
    "name": "Lab 3 Bench", "short_name": "Lab 3 Bench", "start_url": "./", "scope": "./", "display": "standalone",
    "orientation": "any", "background_color": "#f3f5f8", "theme_color": "#f3f5f8",
    "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
              {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}, indent=2))
(gh / 'sw.js').write_text('''// Network first, so updates show up; falls back to the saved copy when the lab Wi-Fi is down.
const CACHE = "lab3-bench-v1";
const FILES = ["./", "./index.html", "./manifest.webmanifest", "./icon-180.png", "./icon-192.png", "./icon-512.png"];
self.addEventListener("install", (e) => { e.waitUntil(caches.open(CACHE).then((c) => c.addAll(FILES)).then(() => self.skipWaiting())); });
self.addEventListener("activate", (e) => { e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  e.respondWith(fetch(e.request).then((r) => { const copy = r.clone(); caches.open(CACHE).then((c) => c.put(e.request, copy)); return r; })
    .catch(() => caches.match(e.request, { ignoreSearch: true }).then((m) => m || caches.match("./index.html"))));
});
''')
print('artifact', (out / 'lab3-bench.html').stat().st_size, 'github', (gh / 'index.html').stat().st_size)
