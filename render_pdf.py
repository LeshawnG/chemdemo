import sys, pathlib
from playwright.sync_api import sync_playwright
src = pathlib.Path(sys.argv[1]).resolve(); out = sys.argv[2]
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 720, 'height': 1024})
    pg.goto('file://' + str(src)); pg.wait_for_timeout(800)
    over = pg.evaluate("""() => [...document.querySelectorAll('.page')].map((s, i) => {
        const body = s.querySelector('.body') || s; const r = body.getBoundingClientRect();
        let maxB = 0; body.querySelectorAll('*').forEach(e => { const q = e.getBoundingClientRect(); if (q.height) maxB = Math.max(maxB, q.bottom); });
        const wide = [...s.querySelectorAll('svg, table, figure')].filter(e => e.getBoundingClientRect().right > s.getBoundingClientRect().right - 29).length;
        return [i + 1, s.id, Math.round(maxB - r.bottom), wide]; })""")
    for i, pid, ov, wide in over: print(f'page {i:2d} {pid:12s} overflow {ov:5d}px  wide {wide}')
    pg.pdf(path=out, width='7.5in', height='10.667in', print_background=True, prefer_css_page_size=True)
    b.close()
