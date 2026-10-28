"""Generate every figure for the Lab 3 companion PDF as SVG strings → figs.json"""
import json, math
import numpy as np
from svgfig import Scene, MOLS, op, perm, Rx, Rz, INK, MUTED, shade

V0 = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], float)
def view(phi, tilt): return Rx(math.radians(tilt)) @ V0 @ Rz(math.radians(phi))
F = {}

# ================================================================= Part 1 · Cr(CO)6
cr = MOLS['crco6']; A = cr['atoms']
LIG = {7 + k: k + 1 for k in range(6)}  # O atom index → ligand number
def cr_panel(kind, n, v, after, color, title, w=168, h=170, show_plane=None, show_axis=True, ax_lab=''):
    sc = Scene(view(-24, 14), w, h, 18, cy=h/2 - 4)
    M = op(kind, n, v) if after else np.eye(3)
    X = np.array([a['x'] for a in A]) @ M.T
    R = 3.05
    if show_plane is not None: sc.plane(show_plane, R * 1.12, color, 0.17)
    if kind in ('C', 'S') and show_axis: sc.axis(v, R + 0.75, color, ax_lab)
    for i in range(1, 7): sc.stick(X[0], X[i], 3.2, '#7c8597'); sc.stick(X[i], X[i + 6], 3.6, '#7c8597')
    sc.ball(X[0], 0.62, '#9aa7ba', 'Cr', lab_size=9)
    for i in range(1, 7): sc.ball(X[i], 0.36, '#475569')
    for i in range(7, 13): sc.ball(X[i], 0.5, '#f87171', str(LIG[i]), lab_size=11)
    if kind == 'i': sc.ball([0, 0, 0], 0.16, color); sc.text([0, 0, 0], '', color=color)
    sc.top.append(f'<text x="{w/2}" y="{h-5}" text-anchor="middle" font-size="11" font-weight="700" fill="{MUTED if not after else color}">{title}</text>')
    return sc.svg()

def perm_text_cr(kind, n, v):
    p = perm(op(kind, n, v), A); seen = set(); cyc = []
    for s in range(7, 13):
        if s in seen or p[s] == s: continue
        c, j = [], s
        while j not in seen: seen.add(j); c.append(LIG[j]); j = p[j]
        cyc.append(('↔' if len(c) == 2 else '→').join(map(str, c)))
    fixed = [str(LIG[s]) for s in range(7, 13) if p[s] == s]
    t = '; '.join(cyc)
    t += ('. Stay: Cr, ' + ', '.join(fixed)) if fixed else '. Only Cr stays'
    return t

s3 = 1 / math.sqrt(3); s2 = 1 / math.sqrt(2)
CR_EL = [
    ('C4', 'C', 4, [0, 0, 1], '#1d4ed8', None, 'C<tspan baseline-shift="sub" font-size="8">4</tspan>', 'C₄ · turn 90°'),
    ('C2', 'C', 2, [0, 0, 1], '#2563eb', None, 'C<tspan baseline-shift="sub" font-size="8">2</tspan>', 'C₂ = C₄² · turn 180°'),
    ('C3', 'C', 3, [s3, s3, s3], '#0f766e', None, 'C<tspan baseline-shift="sub" font-size="8">3</tspan>', 'C₃ · turn 120°'),
    ('C2p', 'C', 2, [s2, 0, s2], '#7e22ce', None, "C<tspan baseline-shift=\"sub\" font-size=\"8\">2</tspan>′", "C₂′ · turn 180°"),
    ('i', 'i', 1, [0, 0, 0], '#be123c', None, '', 'i · through Cr'),
    ('S4', 'S', 4, [0, 0, 1], '#db2777', [0, 0, 1], 'S<tspan baseline-shift="sub" font-size="8">4</tspan>', 'S₄ · 90° + reflect'),
    ('S6', 'S', 6, [s3, s3, s3], '#9f1239', [s3, s3, s3], 'S<tspan baseline-shift="sub" font-size="8">6</tspan>', 'S₆ · 60° + reflect'),
    ('sh', 's', 1, [0, 0, 1], '#6d28d9', [0, 0, 1], '', 'σh · reflect'),
    ('sd', 's', 1, [s2, -s2, 0], '#c2410c', [s2, -s2, 0], '', 'σd · reflect'),
]
for key, kind, n, v, col, pl, axl, title in CR_EL:
    F['cr_' + key + '_b'] = cr_panel(kind, n, v, False, col, 'before', show_plane=pl, ax_lab=axl)
    F['cr_' + key + '_a'] = cr_panel(kind, n, v, True, col, 'after', show_plane=pl, ax_lab=axl)
    F['cr_' + key + '_t'] = perm_text_cr(kind, n, v)
# trap: C6 about a C3 line (fails)
F['cr_C6fake'] = cr_panel('C', 6, [s3, s3, s3], True, '#64748b', 'after 60° only: ✗', ax_lab='?')

# ================================================================= Part 1 · naphthalene
na = MOLS['naph']; NA = na['atoms']
NUM = {i: a['label'].replace('<sub>', '').replace('</sub>', '')[1:] for i, a in enumerate(NA) if a['s'] == 'C'}
C1 = np.array(NA[0]['x'])
def na_panel(kind, n, v, after, color, title, w=212, h=168, plane=None, ax=True, ax_lab=''):
    sc = Scene(view(-22, 58), w, h, 22, cy=h/2 - 6)
    M = op(kind, n, v) if after else np.eye(3)
    X = np.array([a['x'] for a in NA]) @ M.T
    mk = M @ (C1 + np.array([0, 0, 0.95]))  # the top-face marker
    if plane is not None:
        n = list(map(abs, plane))
        if n[2] > .5: sc.rect_plane([1, 0, 0], [0, 1, 0], 3.9, 2.85, color, 0.15)
        elif n[1] > .5: sc.rect_plane([1, 0, 0], [0, 0, 1], 3.9, 1.9, color, 0.15)
        else: sc.rect_plane([0, 1, 0], [0, 0, 1], 2.85, 1.9, color, 0.15)
    if kind in ('C', 'S') and ax: sc.axis(v, 3.4 if abs(v[2]) < 0.5 else 2.6, color, ax_lab)
    for b in na['bonds']: sc.stick(X[b[0]], X[b[1]], 3.2, '#6b7280')
    for i, a in enumerate(NA):
        if a['s'] == 'C': sc.ball(X[i], 0.48, '#1f2937', NUM[i], lab_color='#ffffff', lab_size=8 if len(NUM[i]) > 1 else 9.5, flat=True, stroke='#ffffff')
        else: sc.ball(X[i], 0.22, '#f1f5f9')
    below = mk[2] < 0
    p0 = M @ C1
    sc.stick(p0 + (mk - p0) * 0.35, mk, 1.6, '#dc2626', dash='2 2' if below else None)
    sc.ball(mk, 0.17, '#dc2626', dash=below, stroke='#7f1d1d' if not below else '#dc2626')
    if kind == 'i': sc.ball([0, 0, 0], 0.15, color)
    sc.top.append(f'<text x="{w/2}" y="{h-5}" text-anchor="middle" font-size="11" font-weight="700" fill="{MUTED if not after else color}">{title}</text>')
    return sc.svg()
NA_EL = [
    ('C2z', 'C', 2, [0, 0, 1], '#1d4ed8', None, 'C₂(z) · ⟂ to the plane'),
    ('C2y', 'C', 2, [0, 1, 0], '#7e22ce', None, 'C₂(y) · short axis, through C4a, C8a'),
    ('C2x', 'C', 2, [1, 0, 0], '#0f766e', None, 'C₂(x) · long axis, no atoms on it'),
    ('i', 'i', 1, [0, 0, 0], '#be123c', None, 'i · centre of the C4a–C8a bond'),
    ('sxy', 's', 1, [0, 0, 1], '#d97706', [0, 0, 1], 'σ(xy) · the ring plane'),
    ('sxz', 's', 1, [0, 1, 0], '#c2410c', [0, 1, 0], 'σ(xz) · ⟂ plane along the long axis'),
    ('syz', 's', 1, [1, 0, 0], '#a16207', [1, 0, 0], 'σ(yz) · ⟂ plane through C4a, C8a'),
]
def perm_text_na(kind, n, v):
    p = perm(op(kind, n, v), NA); seen = set(); cyc = []
    for s in NUM:
        if s in seen or p[s] == s: continue
        c, j = [], s
        while j not in seen: seen.add(j); c.append(NUM[j]); j = p[j]
        cyc.append('↔'.join(c))
    fixed = [NUM[s] for s in NUM if p[s] == s]
    if not cyc: return 'All atoms stay; only the red marker flips below the plane'
    t = ' '.join(cyc)
    return t + (f'. Stay: {", ".join(fixed)}' if fixed else '')
for key, kind, n, v, col, pl, title in NA_EL:
    lab = {'C2z': 'z', 'C2y': 'y', 'C2x': 'x'}.get(key, '')
    F['na_' + key + '_b'] = na_panel(kind, n, v, False, col, 'before', plane=pl, ax_lab=lab)
    F['na_' + key + '_a'] = na_panel(kind, n, v, True, col, 'after', plane=pl, ax_lab=lab)
    F['na_' + key + '_t'] = perm_text_na(kind, n, v)
# labelled reference drawing (big)
def na_ref(w=320, h=206):
    sc = Scene(view(0, 90), w, h, 31, cy=h/2 + 4)
    X = np.array([a['x'] for a in NA])
    sc.line([-4.3, 0, 0], [4.3, 0, 0], '#0f766e', 1.4, dash='5 4', z=-9); sc.text([4.55, 0, 0], 'x', color='#0f766e', size=12)
    sc.line([0, -2.75, 0], [0, 2.75, 0], '#7e22ce', 1.4, dash='5 4', z=-9); sc.text([0.22, 2.85, 0], 'y', color='#7e22ce', size=12, anchor='start')
    for b in na['bonds']: sc.stick(X[b[0]], X[b[1]], 3.4, '#6b7280')
    for i, a in enumerate(NA):
        if a['s'] == 'C': sc.ball(X[i], 0.42, '#1f2937', NUM[i], lab_color='#fff', lab_size=9 if len(NUM[i]) > 1 else 10, flat=True)
        else: sc.ball(X[i], 0.25, '#f1f5f9', a['label'].replace('<sub>', '').replace('</sub>', ''), lab_size=7)
    sc.top.append(f'<text x="{w-6}" y="{h-8}" text-anchor="end" font-size="10" fill="{MUTED}">z points out of the page</text>')
    return sc.svg()
F['na_ref'] = na_ref()
# Kekulé structures: the drawn one (D2h) and one of the other two (C2v)
def kekule(doubles, w=240, h=140, title=''):
    sc = Scene(view(0, 90), w, h, 27, cy=h/2 + 8)
    X = {NUM[i]: np.array(a['x']) for i, a in enumerate(NA) if a['s'] == 'C'}
    pairs = [('1', '2'), ('2', '3'), ('3', '4'), ('4', '4a'), ('4a', '8a'), ('8a', '1'), ('4a', '5'), ('5', '6'), ('6', '7'), ('7', '8'), ('8', '8a')]
    for a, b in pairs:
        sc.stick(X[a], X[b], 2.4, INK)
        if (a, b) in doubles or (b, a) in doubles:
            m = (X[a] + X[b]) / 2; c = np.array([1.212 if m[0] > 0.01 else (-1.212 if m[0] < -0.01 else 0), 0, 0])
            if abs(m[0]) < 0.01: off = np.array([0.24, 0, 0]); t = X[b] - X[a]; sc.stick(X[a] + off + t * 0.12, X[b] + off - t * 0.12, 2.0, INK)
            else:
                d = (c - m); d /= np.linalg.norm(d); sh = 0.27
                p, q = X[a] + d * sh, X[b] + d * sh; t = q - p
                sc.stick(p + t * 0.15, q - t * 0.15, 2.0, INK)
    sc.top.append(f'<text x="{w/2}" y="12" text-anchor="middle" font-size="11" font-weight="700" fill="{INK}">{title}</text>')
    return sc.svg()
F['kek_d2h'] = kekule({('1', '2'), ('3', '4'), ('4a', '8a'), ('5', '6'), ('7', '8')}, title='Drawn in the manual: keeps D₂h')
F['kek_c2v'] = kekule({('8a', '1'), ('2', '3'), ('4', '4a'), ('5', '6'), ('7', '8')}, title='Another Kekulé form: only C₂v')

# ================================================================= Part 3 · lattices
S = 4.0
CLR = {'nacl': {'an': '#3b82f6', 'cat': '#ef4444'}, 'cscl': {'an': '#22c55e', 'cat': '#d946ef'}}
def sites(key, ext=1):
    out = []
    if key == 'nacl':
        for i in range(2*ext+1):
            for j in range(2*ext+1):
                for k in range(2*ext+1): out.append(((i/2, j/2, k/2), 'an' if (i+j+k) % 2 == 0 else 'cat'))
    else:
        for i in range(ext+1):
            for j in range(ext+1):
                for k in range(ext+1): out.append(((i, j, k), 'an'))
        for i in range(ext):
            for j in range(ext):
                for k in range(ext): out.append(((i+.5, j+.5, k+.5), 'cat'))
    return out
def Wp(f, ext=1): return (np.array(f, float) - ext/2) * S
def site_of(f, ext=1): return sum(1 for x in f if x in (0, ext))
FRAC = {3: '⅛', 2: '¼', 1: '½', 0: '1'}
def cell(key, w=230, h=220, focus=None, labels=None, ext=1, title='', poly=None, tet=False, scale=None, phi=-32, tilt=18, contacts=True):
    sc = Scene(view(phi, tilt), w, h, scale or (24 if ext == 1 else 15), cy=h/2 + (8 if title else 0))
    L = sites(key, ext); col = CLR[key]
    rad = {'nacl': {'an': 0.42, 'cat': 0.32}, 'cscl': {'an': 0.44, 'cat': 0.4}}[key]
    on = None
    if focus in ('corner', 'edge', 'face', 'body'):
        want = {'corner': 3, 'edge': 2, 'face': 1, 'body': 0}[focus]; on = {i for i, (f, t) in enumerate(L) if site_of(f, ext) == want}
    elif focus in ('cat', 'an'):
        c = (.5, .5, .5) if focus == 'cat' else (1, 1, 1); nn = 0.5 if key == 'nacl' else math.sqrt(3)/2
        on = {i for i, (f, t) in enumerate(L) if np.linalg.norm(np.subtract(f, c)) < 1e-6 or abs(np.linalg.norm(np.subtract(f, c)) - nn) < 1e-6}
    elif focus == 'anions': on = {i for i, (f, t) in enumerate(L) if t == 'an'}
    # cell edges
    for a in range(ext+1):
        for b in range(ext+1):
            for p, q in (([0, a, b], [ext, a, b]), ([a, 0, b], [a, ext, b]), ([a, b, 0], [a, b, ext])):
                sc.line(Wp(p, ext), Wp(q, ext), '#94a3b8', 1.0)
    # sticks
    for i, (f, t) in enumerate(L):
        for j, (g, u) in enumerate(L):
            if j <= i: continue
            d = np.linalg.norm(np.subtract(f, g)); dim = on is not None and not (i in on and j in on)
            if key == 'nacl' and abs(d - 0.5) < 1e-6: sc.stick(Wp(f, ext), Wp(g, ext), 2.6, '#9aa3b5', dim=dim)
            if key == 'cscl' and t == 'an' and u == 'an' and abs(d - 1) < 1e-6: sc.stick(Wp(f, ext), Wp(g, ext), 2.6, '#9aa3b5', dim=on is not None)
            if key == 'cscl' and contacts and t != u and abs(d - math.sqrt(3)/2) < 1e-6: sc.stick(Wp(f, ext), Wp(g, ext), 1.4, '#c4c9d4', dim=dim, dash='3 2')
    if poly == 'oct':
        c = Wp((.5, .5, .5) if focus == 'cat' else (1, 1, 1), ext); r = S/2
        V = [c + r*np.array(v) for v in ([1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1])]
        for a, b, cc in ((0, 2, 4), (2, 1, 4), (1, 3, 4), (3, 0, 4), (0, 2, 5), (2, 1, 5), (1, 3, 5), (3, 0, 5)):
            sc.poly([V[a], V[b], V[cc]], col['cat' if focus == 'cat' else 'an'], 0.13, stroke=col['cat' if focus == 'cat' else 'an'], sw=0.9)
    if poly == 'cube':
        c = Wp((.5, .5, .5) if focus == 'cat' else (1, 1, 1), ext); r = S/2
        for ax in range(3):
            for sgn in (-1, 1):
                q = []
                for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                    v = [0, 0, 0]; v[ax] = sgn; v[(ax+1) % 3] = a; v[(ax+2) % 3] = b; q.append(c + r*np.array(v))
                sc.poly(q, col['cat' if focus == 'cat' else 'an'], 0.08, stroke=col['cat' if focus == 'cat' else 'an'], sw=0.9)
    if tet:
        T = [Wp(f) for f in ((0, 0, 0), (.5, .5, 0), (.5, 0, .5), (0, .5, .5))]
        for a, b, c in ((0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)): sc.poly([T[a], T[b], T[c]], '#f59e0b', 0.22, stroke='#b45309', sw=1)
        for f in [(x, y, z) for x in (.25, .75) for y in (.25, .75) for z in (.25, .75)]: sc.ball(Wp(f), 0.13, '#ffffff', stroke='#334155')
    nb = 0
    for i, (f, t) in enumerate(L):
        dim = on is not None and i not in on
        lab = None
        if labels == 'frac' and (on is None or i in on): lab = FRAC[site_of(f, ext)]
        if focus in ('cat', 'an') and i in on:
            c = (.5, .5, .5) if focus == 'cat' else (1, 1, 1)
            if np.linalg.norm(np.subtract(f, c)) > 1e-6: nb += 1; lab = str(nb)
        if labels == 'frac' and lab:
            sc.ball(Wp(f, ext), rad[t], col[t], None, dim=dim); sc.text(Wp(f, ext), lab, color=INK, size=12, dy=-rad[t] * sc.s - 3)
        else: sc.ball(Wp(f, ext), rad[t], col[t], lab, lab_color='#ffffff', lab_size=9, dim=dim)
    if title: sc.top.append(f'<text x="{w/2}" y="13" text-anchor="middle" font-size="11.5" font-weight="700" fill="{INK}">{title}</text>')
    return sc.svg()

F['nacl_full'] = cell('nacl', 236, 220, title='NaCl: Cl⁻ blue, Na⁺ red (manual colours)', scale=22.5)
for k, t in (('corner', 'Corners: 8 × ⅛'), ('face', 'Faces: 6 × ½'), ('edge', 'Edges: 12 × ¼'), ('body', 'Centre: 1 × 1')):
    F['nacl_' + k] = cell('nacl', 172, 176, focus=k, labels='frac', title=t, scale=21)
F['cscl_full'] = cell('cscl', 210, 210, title='CsCl: Cl⁻ green, Cs⁺ magenta', contacts=True)
F['cscl_corner'] = cell('cscl', 172, 176, focus='corner', labels='frac', title='Corners: 8 × ⅛', scale=21, contacts=False)
F['cscl_body'] = cell('cscl', 172, 176, focus='body', labels='frac', title='Centre: 1 × 1', scale=21)
F['nacl_oct_cat'] = cell('nacl', 200, 200, focus='cat', poly='oct', title='Na⁺: 6 Cl⁻ around it', scale=21)
F['nacl_oct_an'] = cell('nacl', 200, 200, focus='an', poly='oct', ext=2, title='Cl⁻: 6 Na⁺ (8 cells)', scale=12.5)
F['nacl_tet'] = cell('nacl', 200, 200, focus='anions', tet=True, title='Tetrahedral holes: empty', scale=21)
F['cscl_cube_cat'] = cell('cscl', 200, 200, focus='cat', poly='cube', title='Cs⁺: 8 Cl⁻ (a cube)', scale=21)
F['cscl_cube_an'] = cell('cscl', 200, 200, focus='an', poly='cube', ext=2, title='Cl⁻: 8 Cs⁺ (8 cells)', scale=13)

# radius ratio: 2D cross-sections
def rr(kind, rho, w=170, h=170, title='', sub=''):
    R = 1.0; sc = 30; cx, cy = w/2, h/2 + 8
    out = [f'<svg viewBox="0 0 {w} {h+18}" width="{w}" height="{h+18}" xmlns="http://www.w3.org/2000/svg" font-family="IBM Plex Sans, sans-serif">']
    if kind == 'oct':
        d = max(R + rho, R*math.sqrt(2)); pts = [(d, 0), (-d, 0), (0, d), (0, -d)]; touch = R + rho >= R*math.sqrt(2) - 1e-9
        guide = f'<polygon points="{" ".join(f"{cx+x*sc:.1f},{cy-y*sc:.1f}" for x, y in pts[:1]+pts[2:3]+pts[1:2]+pts[3:4])}" fill="none" stroke="#94a3b8" stroke-dasharray="3 3"/>'
    else:
        e = max(2*R, 2*(R + rho)/math.sqrt(3)); pts = [(e/math.sqrt(2)*sx, e/2*sy) for sx in (1, -1) for sy in (1, -1)]; touch = R + rho >= R*math.sqrt(3) - 1e-9
        guide = f'<rect x="{cx - e/math.sqrt(2)*sc:.1f}" y="{cy - e/2*sc:.1f}" width="{2*e/math.sqrt(2)*sc:.1f}" height="{e*sc:.1f}" fill="none" stroke="#94a3b8" stroke-dasharray="3 3"/>'
    out.append(guide)
    for x, y in pts: out.append(f'<circle cx="{cx+x*sc:.1f}" cy="{cy-y*sc:.1f}" r="{R*sc:.1f}" fill="#60a5fa" fill-opacity=".8" stroke="#1e3a8a" stroke-opacity=".5"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{rho*sc:.1f}" fill="#f87171" stroke="{"#15803d" if touch else "#b42318"}" stroke-width="2.4"{"" if touch else " stroke-dasharray=\"4 3\""}/>')
    out.append(f'<text x="{w/2}" y="13" text-anchor="middle" font-size="11.5" font-weight="700" fill="{INK}">{title}</text>')
    out.append(f'<text x="{w/2}" y="{h+14}" text-anchor="middle" font-size="11" font-weight="700" fill="{"#15803d" if touch else "#b42318"}">{sub}</text></svg>')
    return ''.join(out)
F['rr_oct_lim'] = rr('oct', math.sqrt(2) - 1, title='Octahedral limit', sub='r₊/r₋ = √2 − 1 = 0.414')
F['rr_cub_lim'] = rr('cub', math.sqrt(3) - 1, title='Cubic limit', sub='r₊/r₋ = √3 − 1 = 0.732')
F['rr_na_cub'] = rr('cub', 0.56, title='Na⁺ in a cubic hole', sub='0.56: rattles ✗')
F['rr_cs_cub'] = rr('cub', 0.96, title='Cs⁺ in a cubic hole', sub='0.96: touches all 8 ✓')
F['rr_na_oct'] = rr('oct', 0.56, title='Na⁺ in an octahedral hole', sub='0.56: touches all 6 ✓')

json.dump(F, open('figs.json', 'w'))
print(len(F), 'figures')
