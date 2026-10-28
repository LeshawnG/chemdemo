"""Part 2 drop-in: tile-sheet photos → (1) sheets.json for Lab 3 Bench, (2) Lab3_Part2_Addon.pdf.
usage: python3 part2_addon.py sheets_input.json
sheets_input.json: [{ "photo": "path.jpg", "name": "Sheet A", "a": [x,y], "b": [x,y], "o": [x,y] (optional lattice point, px),
                      "type": "Hexagonal", "per": "1 tile", "note": "...", "conv": [[x,y],[x,y]] (optional), "wrong": {"a":[..],"b":[..],"why":"..."} (optional) }]
Vectors are in the ORIGINAL photo's pixels (findlattice.py prints them)."""
import sys, json, base64, io, math, pathlib
import numpy as np
from PIL import Image, ImageOps
B = pathlib.Path(__file__).parent
spec = json.load(open(sys.argv[1]))
MAXD = 1400
sheets, figs = [], []
for k, s in enumerate(spec):
    im = ImageOps.exif_transpose(Image.open(s['photo'])).convert('RGB')
    f = min(1.0, MAXD / max(im.size)); im2 = im.resize((round(im.width * f), round(im.height * f)), Image.LANCZOS) if f < 1 else im
    buf = io.BytesIO(); im2.save(buf, 'JPEG', quality=80); uri = 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()
    sc = lambda v: [round(v[0] * f, 2), round(v[1] * f, 2)]
    a, b = sc(s['a']), sc(s['b']); o = sc(s.get('o', [im.width / 2, im.height / 2]))
    # move the origin to the lattice point nearest the photo centre, so drawn cells sit mid-photo
    Dt = a[0] * b[1] - a[1] * b[0]; c = [im2.width / 2 - o[0], im2.height / 2 - o[1]]
    ci, cj = round((c[0] * b[1] - c[1] * b[0]) / Dt), round((a[0] * c[1] - a[1] * c[0]) / Dt)
    o = [round(o[0] + ci * a[0] + cj * b[0], 2), round(o[1] + ci * a[1] + cj * b[1], 2)]
    ans = [{'a': a, 'b': b, 'kind': 'prim', 'note': s.get('note', 'Primitive cell: holds 1 lattice point.')}]
    if s.get('conv'): ans.append({'a': sc(s['conv'][0]), 'b': sc(s['conv'][1]), 'kind': 'conv', 'note': s.get('conv_note', 'Also valid, but holds more than 1 lattice point.')})
    entry = {'key': f'sheet{k+1}', 'name': s['name'], 'src': uri, 'a': a, 'b': b, 'o': o, 'type': s.get('type', ''), 'per': s.get('per', '1 repeat'), 'answers': ans}
    if s.get('wrong'): entry['wrong'] = {'a': sc(s['wrong']['a']), 'b': sc(s['wrong']['b']), 'why': s['wrong']['why']}
    sheets.append(entry)
    # figure: photo with lattice points, primitive cell (green), conventional (amber dashed), wrong (red dashed)
    W, H = im2.size; disp = 315; z = disp / W; hh = H * z
    def poly(O, u, v, col, dash='', fill='none', sw=3):
        P = [O, (O[0] + u[0], O[1] + u[1]), (O[0] + u[0] + v[0], O[1] + u[1] + v[1]), (O[0] + v[0], O[1] + v[1])]
        return f'<polygon points="{" ".join(f"{x*z:.1f},{y*z:.1f}" for x, y in P)}" fill="{fill}" stroke="{col}" stroke-width="{sw}" {dash} stroke-linejoin="round"/>'
    D = a[0] * b[1] - a[1] * b[0]; dots = ''
    for i in range(-40, 41):
        for j in range(-40, 41):
            x, y = o[0] + i * a[0] + j * b[0], o[1] + i * a[1] + j * b[1]
            if -5 <= x <= W + 5 and -5 <= y <= H + 5: dots += f'<circle cx="{x*z:.1f}" cy="{y*z:.1f}" r="2.6" fill="#1d4ed8" fill-opacity=".85"/>'
    cells = ''
    if s.get('wrong'): cells += poly(o, entry['wrong']['a'], entry['wrong']['b'], '#b42318', 'stroke-dasharray="5 4"', sw=2.2)
    if s.get('conv'): cells += poly(o, ans[1]['a'], ans[1]['b'], '#b45309', 'stroke-dasharray="7 5"', sw=2.4)
    cells += poly(o, a, b, '#15803d', '', 'rgba(21,128,61,.18)', 3.2)
    svg = (f'<svg viewBox="0 0 {disp} {hh:.0f}" width="{disp}" height="{hh:.0f}" xmlns="http://www.w3.org/2000/svg"><image href="{uri}" width="{disp}" height="{hh:.0f}"/>{dots}{cells}'
           f'<rect width="{disp}" height="{hh:.0f}" fill="none" stroke="#d9dfe8"/></svg>')
    la, lb = math.hypot(*s['a']), math.hypot(*s['b']); ang = math.degrees(math.acos(max(-1, min(1, (s['a'][0]*s['b'][0] + s['a'][1]*s['b'][1]) / la / lb))))
    figs.append(f'<figure class="pat">{svg}<figcaption><b>{s["name"]}</b> · {s.get("type", "")}<br>{s.get("note", "")}'
                f'<br><span class="small">|a| = {la:.0f} px, |b| = {lb:.0f} px, angle {ang:.0f}° (in the photo). Holds {s.get("per", "1 repeat")}.</span>'
                + (f'<br><span style="color:#b42318">✗ {s["wrong"]["why"]}</span>' if s.get('wrong') else '') + '</figcaption></figure>')
json.dump(sheets, open(B / 'sheets.json', 'w'))
# PDF: reuse the companion's look
sys.argv = [sys.argv[0]]
import importlib.util
spec_b = importlib.util.spec_from_file_location('pb', B / 'pdf_build.py'); pb = importlib.util.module_from_spec(spec_b)
src = (B / 'pdf_build.py').read_text()
css = src[src.index("CSS = fontfaces() + '''") + len("CSS = fontfaces() + '''"): src.index("'''\nhtml = f'<!doctype html>")]
pb.__dict__['__file__'] = str(B / 'pdf_build.py')
exec(src[:src.index('# ================================================================ COVER')], pb.__dict__)
pb.pages.clear()
per_page = 4
for p in range(0, len(figs), per_page):
    body = (f'<p class="intro"><span class="sw g"></span> primitive cell · <span class="sw o"></span> another valid cell · <span class="sw r"></span> the common mistake · blue dots: lattice points. '
            f'Cells were found by autocorrelation of each photo and checked by eye. A student\'s cell is right if its edges join two blue dots each and it is a parallelogram.</p>'
            f'<div class="grid2">{"".join(figs[p:p+per_page])}</div>')
    pb.page(f'addon{p}', 'p2', 'Part 2 · the lab\'s tile sheets', body, 'Add-on · your photos')
html = f'<!doctype html><html><head><meta charset="utf-8"><title>Lab 3 Part 2 Add-on</title><style>{pb.fontfaces() + css}</style></head><body>{"".join(pb.pages)}<script>document.querySelectorAll(".pn").forEach((e,i)=>e.textContent="Add-on "+(i+1))</script></body></html>'
(B / 'out' / 'addon.html').write_text(html)
print('sheets:', len(sheets), '→ sheets.json; addon.html written')
