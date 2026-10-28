"""Screenshot a local artifact page with CDN scripts served from local copies.
usage: python3 shot.py page.html out.png WxH [js-to-run-before-shot] [dark]"""
import sys, pathlib
from playwright.sync_api import sync_playwright
BASE = pathlib.Path(__file__).parent
LIBS = {'three.min.js': BASE / 'npmtmp/node_modules/three/build/three.min.js'}
page_path, out, size = sys.argv[1], sys.argv[2], sys.argv[3]
js = sys.argv[4] if len(sys.argv) > 4 else ''
dark = len(sys.argv) > 5 and sys.argv[5] == 'dark'
w, h = map(int, size.split('x'))
SKEL = '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"></head><body>'
with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
    ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=float(__import__("os").environ.get("DSF","2")), color_scheme='dark' if dark else 'light')
    pg = ctx.new_page()
    errs = []
    pg.on('console', lambda m: errs.append(m.type + ': ' + m.text) if m.type in ('error', 'warning') else None)
    pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)))
    def route(r):
        url = r.request.url
        for k, v in LIBS.items():
            if url.endswith(k): return r.fulfill(path=str(v), content_type='application/javascript')
        if 'fonts.g' in url: return r.fulfill(body='', content_type='text/css')
        return r.continue_()
    pg.route('**/*', route)
    html = pathlib.Path(page_path).read_text()
    if not html.lstrip().lower().startswith('<!doctype'): html = SKEL + html + '</body></html>'
    pg.set_content(html, wait_until='load')
    pg.wait_for_timeout(800)
    if js:
        for part in js.split(';;'):
            pg.evaluate(part); pg.wait_for_timeout(1700)
    pg.wait_for_timeout(500)
    pg.screenshot(path=out)
    print('\n'.join(errs) or 'no console errors')
    b.close()
