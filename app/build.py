"""Assemble Lab 4 Bench: artifact version (three.js from cdnjs) and GitHub Pages version (three.js inlined, PWA files)."""
import json, pathlib
B = pathlib.Path(__file__).parent
head = (B / "head.html").read_text(); body = (B / "body.html").read_text()
mo = json.loads((B / "mo.json").read_text())
p1 = (B / "p1.js").read_text(); p2 = (B / "p2.js").read_text(); shell = (B / "shell.js").read_text()
app = "<script>\nwindow.LAB4_MO = " + json.dumps(mo) + ";\n" + p1 + "\n" + p2 + "\n" + shell + "\n</script>\n"
THREE_CDN = '<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>\n'
out = B / "out"; out.mkdir(exist_ok=True)
(out / "lab4-bench.html").write_text(head + body + THREE_CDN + app)

three = (B / "npmtmp/node_modules/three/build/three.min.js").read_text()
gh = out / "github/lab4"; gh.mkdir(parents=True, exist_ok=True)
skel_head = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Lab 4 Bench">
<meta name="theme-color" content="#f3f5f8">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icon-180.png">
<link rel="icon" href="icon-192.png">
<style>:root{color-scheme:light;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;padding:0;font:14px -apple-system,BlinkMacSystemFont,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>
'''
sw_reg = '''<script>if ("serviceWorker" in navigator) { window.addEventListener("load", () => navigator.serviceWorker.register("sw.js").catch(() => {})); }</script>\n'''
(gh / "index.html").write_text(skel_head + head + "</head>\n<body>\n" + body + "<script>\n" + three + "\n</script>\n" + app + sw_reg + "</body>\n</html>\n")
(gh / "manifest.webmanifest").write_text(json.dumps({
    "name": "Lab 4 Bench", "short_name": "Lab 4 Bench", "start_url": "./", "scope": "./", "display": "standalone",
    "orientation": "any", "background_color": "#f3f5f8", "theme_color": "#f3f5f8",
    "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
              {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}, indent=2))
(gh / "sw.js").write_text('''// Network first, so updates show up; falls back to the saved copy when the lab Wi-Fi is down.
const CACHE = "lab4-bench-v1";
const FILES = ["./", "./index.html", "./manifest.webmanifest", "./icon-180.png", "./icon-192.png", "./icon-512.png"];
self.addEventListener("install", (e) => { e.waitUntil(caches.open(CACHE).then((c) => c.addAll(FILES)).then(() => self.skipWaiting())); });
self.addEventListener("activate", (e) => { e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  e.respondWith(fetch(e.request).then((r) => { const copy = r.clone(); caches.open(CACHE).then((c) => c.put(e.request, copy)); return r; })
    .catch(() => caches.match(e.request, { ignoreSearch: true }).then((m) => m || caches.match("./index.html"))));
});
''')
(B / "icon.svg").write_text('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
<rect width="512" height="512" fill="#1d4ed8"/>
<path d="M256 236 C 300 200 318 120 256 84 C 194 120 212 200 256 236 Z" fill="#ff9a52" stroke="#fff" stroke-width="10"/>
<path d="M256 236 C 292 262 300 318 256 340 C 212 318 220 262 256 236 Z" fill="#ffffff" stroke="#fff" stroke-width="10"/>
<g stroke="#ffffff" stroke-width="14" stroke-linecap="round"><line x1="256" y1="236" x2="400" y2="368"/><line x1="256" y1="236" x2="112" y2="368"/><line x1="256" y1="236" x2="256" y2="428"/></g>
<circle cx="400" cy="368" r="34" fill="#9ec0ff" stroke="#fff" stroke-width="10"/><circle cx="112" cy="368" r="34" fill="#9ec0ff" stroke="#fff" stroke-width="10"/><circle cx="256" cy="428" r="34" fill="#9ec0ff" stroke="#fff" stroke-width="10"/>
<circle cx="256" cy="236" r="26" fill="#1d4ed8" stroke="#fff" stroke-width="10"/>
</svg>''')
print("artifact", (out / "lab4-bench.html").stat().st_size, "github", (gh / "index.html").stat().st_size)
