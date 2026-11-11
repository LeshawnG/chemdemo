"""SVG figures for the CHEM 1170 Lab 4 Wednesday companion."""
import math

INK = "#1b2330"
MUTED = "#5b6472"
RULE = "#c9ced6"
POS = "#2f67d8"      # + phase
POS_L = "#dbe6fb"
NEG = "#e0782f"      # - phase
NEG_L = "#fbe6d6"
HCOL = "#9aa3ae"
NCOL = "#3a4a8c"
GREEN = "#13795b"
ATOM = "#8796ad"


def sub(t):
    """'_x' or '_{xy}' -> subscript, '^x' or '^{xy}' -> superscript."""
    out = ""
    i = 0
    while i < len(t):
        c = t[i]
        if c in "_^" and i + 1 < len(t):
            if t[i + 1] == "{":
                j = t.index("}", i + 2)
                tok = t[i + 2:j]
                i = j + 1
            else:
                tok = t[i + 1]
                i += 2
            if c == "_":
                out += f'<tspan baseline-shift="sub" font-size="72%">{tok}</tspan>'
            else:
                out += f'<tspan baseline-shift="super" font-size="70%">{tok}</tspan>'
        else:
            out += {"&": "&amp;", "<": "&lt;", ">": "&gt;"}.get(c, c)
            i += 1
    return out


HALO = [False]


def text(x, y, s, size=11, anchor="middle", weight=400, fill=INK, italic=False, extra=""):
    st = ' font-style="italic"' if italic else ""
    if HALO[0]:
        st += ' stroke="#ffffff" stroke-width="3.2" stroke-linejoin="round" paint-order="stroke"'
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" '
            f'font-weight="{weight}" fill="{fill}"{st} {extra}>{sub(s)}</text>')


def lobe_circle(x, y, r, sign, label=True):
    fill = POS if sign > 0 else NEG
    s = f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}" fill-opacity="0.82" stroke="{INK}" stroke-width="0.9"/>'
    if label and r >= 9:
        s += text(x, y + 4.2, "+" if sign > 0 else "−", size=12, weight=700, fill="#fff")
    return s


def p_lobe(cx, cy, ang_deg, length, width, sign):
    """A teardrop p lobe from (cx,cy) pointing at angle (deg, SVG coords, 0 = right, 90 = down)."""
    a = math.radians(ang_deg)
    ux, uy = math.cos(a), math.sin(a)
    vx, vy = -uy, ux
    tipx, tipy = cx + ux * length, cy + uy * length
    c1 = (cx + vx * width * 0.9 + ux * length * 0.15, cy + vy * width * 0.9 + uy * length * 0.15)
    c2 = (tipx + vx * width * 1.05, tipy + vy * width * 1.05)
    c3 = (tipx - vx * width * 1.05, tipy - vy * width * 1.05)
    c4 = (cx - vx * width * 0.9 + ux * length * 0.15, cy - vy * width * 0.9 + uy * length * 0.15)
    fill = POS if sign > 0 else NEG
    d = (f"M{cx:.1f},{cy:.1f} C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {tipx:.1f},{tipy:.1f} "
         f"C{c3[0]:.1f},{c3[1]:.1f} {c4[0]:.1f},{c4[1]:.1f} {cx:.1f},{cy:.1f} Z")
    s = f'<path d="{d}" fill="{fill}" fill-opacity="0.82" stroke="{INK}" stroke-width="0.9"/>'
    lx, ly = cx + ux * length * 0.62, cy + uy * length * 0.62
    s += text(lx, ly + 4.2, "+" if sign > 0 else "−", size=12, weight=700, fill="#fff")
    return s


def atom_dot(x, y, label, col=INK, r=3.2, dx=0, dy=-8, size=10):
    s = f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{col}"/>'
    if label:
        s += text(x + dx, y + dy, label, size=size, weight=600, fill=col)
    return s


def svg(w, h, body, cls="fig"):
    return (f'<svg class="{cls}" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'xmlns="http://www.w3.org/2000/svg" font-family="IBM Plex Sans, sans-serif">{body}</svg>')


# ---------------------------------------------------------------------------
# Geometry of NH3 (top view: looking down the C3 axis from above N)
# H1 on +x (right), H2 at 120 deg, H3 at 240 deg; SVG y is down so y -> -y
def hpos(cx, cy, R):
    pts = []
    for k, deg in enumerate([0, 120, 240]):
        a = math.radians(deg)
        pts.append((cx + R * math.cos(a), cy - R * math.sin(a)))
    return pts


# ---------------------------------------------------------------------------
def fig_nh3_structure():
    """Side view (perspective-ish) and top view with C3 axis and one sigma_v."""
    W, H = 430, 215
    b = ""
    # side view, 3D projected
    dNH, ang = 1.012, math.radians(106.7)
    hh = 2 * dNH * math.sin(ang / 2)
    Rc = hh / math.sqrt(3)
    hN = math.sqrt(dNH ** 2 - Rc ** 2)
    tilt = math.radians(24)
    S = 62
    ox, oy = 110, 118

    def proj(x, y, z):
        # rotate about x axis by tilt so we look slightly from above
        y2 = y * math.cos(tilt) - z * math.sin(tilt)
        z2 = y * math.sin(tilt) + z * math.cos(tilt)
        return ox + S * x, oy - S * z2, y2

    N = proj(0, 0, hN)
    Hs = []
    for deg in [0, 120, 240]:
        a = math.radians(deg - 90)
        Hs.append(proj(Rc * math.cos(a), Rc * math.sin(a), 0))
    # C3 axis
    top = proj(0, 0, hN + 0.85)
    bot = proj(0, 0, -0.75)
    b += f'<line x1="{bot[0]:.1f}" y1="{bot[1]:.1f}" x2="{top[0]:.1f}" y2="{top[1]:.1f}" stroke="{GREEN}" stroke-width="1.6" stroke-dasharray="5 3"/>'
    b += text(top[0] + 4, top[1] + 4, "C_3", size=11, anchor="start", weight=600, fill=GREEN)
    # bonds and atoms, back to front
    order = sorted(range(3), key=lambda i: Hs[i][2], reverse=True)
    for i in order:
        hx, hy, _ = Hs[i]
        b += f'<line x1="{N[0]:.1f}" y1="{N[1]:.1f}" x2="{hx:.1f}" y2="{hy:.1f}" stroke="#6b7480" stroke-width="5" stroke-linecap="round"/>'
    for i in order:
        hx, hy, _ = Hs[i]
        b += f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="10" fill="url(#gH)" stroke="#5d6672" stroke-width="0.8"/>'
    b += f'<circle cx="{N[0]:.1f}" cy="{N[1]:.1f}" r="15" fill="url(#gN)" stroke="#27306a" stroke-width="0.8"/>'
    b += text(N[0], N[1] + 4.5, "N", size=12, weight=700, fill="#fff")
    # lone pair hint
    lp = proj(0, 0, hN + 0.42)
    b += f'<ellipse cx="{lp[0]:.1f}" cy="{lp[1]:.1f}" rx="9" ry="13" fill="{POS}" fill-opacity="0.18" stroke="{POS}" stroke-width="0.8" stroke-dasharray="2 2"/>'
    b += text(lp[0] - 16, lp[1] + 2, "lone pair", size=9, anchor="end", fill=MUTED)
    b += text(ox, 192, "Side view: trigonal pyramid", size=9.5, fill=MUTED)
    b += text(ox, 205, "H–N–H 107°, N above the H_3 plane", size=9.5, fill=MUTED)

    # top view
    cx, cy, R = 320, 100, 50
    hp = hpos(cx, cy, R)
    # sigma_v planes as lines through centre and each H
    for k, (x, y) in enumerate(hp):
        ex, ey = cx - (x - cx) * 0.75, cy - (y - cy) * 0.75
        fx, fy = cx + (x - cx) * 1.45, cy + (y - cy) * 1.45
        b += f'<line x1="{ex:.1f}" y1="{ey:.1f}" x2="{fx:.1f}" y2="{fy:.1f}" stroke="#7c4dbd" stroke-width="1.1" stroke-dasharray="4 3"/>'
    b += text(cx + R * 1.45 + 3, cy + 4, "σ_v", size=11, anchor="start", weight=600, fill="#7c4dbd")
    for k, (x, y) in enumerate(hp):
        b += f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#6b7480" stroke-width="4" stroke-linecap="round"/>'
    for k, (x, y) in enumerate(hp):
        b += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="10" fill="url(#gH)" stroke="#5d6672" stroke-width="0.8"/>'
        b += text(x, y + 4, str(k + 1), size=10, weight=700, fill=INK)
    b += f'<circle cx="{cx}" cy="{cy}" r="13" fill="url(#gN)" stroke="#27306a" stroke-width="0.8"/>'
    b += f'<circle cx="{cx}" cy="{cy}" r="3" fill="{GREEN}"/>'
    b += text(cx, 192, "Top view down C_3 (N on top)", size=9.5, fill=MUTED)
    b += text(cx, 205, "three σ_v planes, one through each N–H", size=9.5, fill=MUTED)
    defs = ('<defs><radialGradient id="gN" cx="35%" cy="30%" r="70%"><stop offset="0" stop-color="#7d8fe0"/>'
            '<stop offset="1" stop-color="#2e3c8a"/></radialGradient>'
            '<radialGradient id="gH" cx="35%" cy="30%" r="70%"><stop offset="0" stop-color="#ffffff"/>'
            '<stop offset="1" stop-color="#b9c0c9"/></radialGradient></defs>')
    return svg(W, H, defs + b)


# ---------------------------------------------------------------------------
def salc_panel(cx, cy, R, coeffs, title, formula, node=None, scale=34, minr=0):
    b = ""
    hp = hpos(cx, cy, R)
    # faint triangle
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in hp)
    b += f'<polygon points="{pts}" fill="none" stroke="{RULE}" stroke-width="1"/>'
    if node == "x":   # nodal plane perpendicular to x, through centre
        b += f'<line x1="{cx}" y1="{cy - R - 22}" x2="{cx}" y2="{cy + R + 18}" stroke="{INK}" stroke-width="1" stroke-dasharray="4 3"/>'
    if node == "y":   # nodal plane along x through centre and H1
        b += f'<line x1="{cx - R - 18}" y1="{cy}" x2="{cx + R + 22}" y2="{cy}" stroke="{INK}" stroke-width="1" stroke-dasharray="4 3"/>'
    for k, ((x, y), c) in enumerate(zip(hp, coeffs)):
        if abs(c) < 1e-6:
            b += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="13" fill="none" stroke="{MUTED}" stroke-width="1" stroke-dasharray="2 2"/>'
            b += text(x, y + 4, "0", size=10, fill=MUTED)
        else:
            b += lobe_circle(x, y, max(minr, scale * abs(c)), 1 if c > 0 else -1)
    b += f'<circle cx="{cx}" cy="{cy}" r="2.6" fill="{INK}"/>'
    # H numbers outside
    for k, (x, y) in enumerate(hp):
        dx, dy = (x - cx) / R, (y - cy) / R
        b += text(x + dx * 33, y + dy * 33 + 4, f"H{k+1}", size=9, fill=MUTED)
    b += text(cx, cy + R + 48, title, size=13, weight=700)
    b += text(cx, cy + R + 65, formula, size=10.5, fill=INK)
    return b


def fig_salcs():
    W, H = 640, 240
    R = 52
    b = ""
    b += salc_panel(110, 88, R, [1 / math.sqrt(3)] * 3, "a_1", "φ_1 + φ_2 + φ_3", scale=30)
    b += salc_panel(320, 88, R, [2 / math.sqrt(6), -1 / math.sqrt(6), -1 / math.sqrt(6)], "e (x)",
                    "2φ_1 − φ_2 − φ_3", node="x", scale=30)
    b += salc_panel(530, 88, R, [0, 1 / math.sqrt(2), -1 / math.sqrt(2)], "e (y)", "φ_2 − φ_3",
                    node="y", scale=30)
    b += text(110, 232, "no node · lowest energy", size=9.5, fill=MUTED)
    b += text(425, 232, "one nodal plane each (dashed) · same energy: a degenerate pair", size=9.5, fill=MUTED)
    b += f'<line x1="232" y1="10" x2="232" y2="220" stroke="{RULE}" stroke-width="1"/>'
    return svg(W, H, b)


def mini_salc(cx, cy, kind, R=11, s=9):
    if kind == "a1":
        co = [1, 1, 1]
    elif kind == "ex":
        co = [1.35, -0.7, -0.7]
    else:
        co = [0, 1, -1]
    b = ""
    for (x, y), c in zip(hpos(cx, cy, R), co):
        if c == 0:
            continue
        b += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{s * abs(c) * 0.62:.1f}" fill="{POS if c > 0 else NEG}" fill-opacity="0.85" stroke="{INK}" stroke-width="0.5"/>'
    return b


def elec(x, y, n, gap=7):
    """n = 0,1,2 electrons drawn as arrows on a level at (x,y)."""
    b = ""
    if n >= 1:
        b += f'<path d="M{x - (gap/2 if n == 2 else 0):.1f},{y + 7} L{x - (gap/2 if n == 2 else 0):.1f},{y - 8}" stroke="{INK}" stroke-width="1.3" marker-end="url(#ah)"/>'
    if n == 2:
        b += f'<path d="M{x + gap/2:.1f},{y - 7} L{x + gap/2:.1f},{y + 8}" stroke="{INK}" stroke-width="1.3" marker-end="url(#ah)"/>'
    return b


ARROW_DEFS = ('<defs><marker id="ah" viewBox="0 0 6 6" refX="3" refY="3" markerWidth="4.2" markerHeight="4.2" orient="auto">'
              f'<path d="M0,0 L6,3 L0,6 Z" fill="{INK}"/></marker>'
              '<marker id="ax" viewBox="0 0 8 8" refX="4" refY="4" markerWidth="7" markerHeight="7" orient="auto">'
              f'<path d="M0,0 L8,4 L0,8 Z" fill="{MUTED}"/></marker></defs>')


def level(x, y, w, col=INK, sw=2):
    return f'<line x1="{x - w/2:.1f}" y1="{y:.1f}" x2="{x + w/2:.1f}" y2="{y:.1f}" stroke="{col}" stroke-width="{sw}" stroke-linecap="round"/>'


def dash(x1, y1, x2, y2, op=1.0):
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{MUTED}" stroke-width="0.9" stroke-dasharray="3 3" opacity="{op}"/>'


def fig_h3_diagram():
    W, H = 330, 230
    b = ARROW_DEFS
    # axis
    b += f'<line x1="26" y1="205" x2="26" y2="18" stroke="{MUTED}" stroke-width="1.2" marker-end="url(#ax)"/>'
    b += text(18, 22, "E", size=11, weight=600, fill=MUTED, anchor="end")
    yH, ya1, ye = 112, 160, 88
    # H 1s x3
    for i, x in enumerate([70, 98, 126]):
        b += level(x, yH, 22)
        b += elec(x, yH, 1)
    b += text(98, yH + 22, "3 × H 1s", size=10.5)
    b += text(98, yH + 36, "−13.6 eV", size=9.5, fill=MUTED)
    # fragment MOs
    xm = 238
    b += level(xm, ya1, 46)
    b += elec(xm, ya1, 2)
    b += level(xm - 26, ye, 40) + level(xm + 26, ye, 40)
    b += elec(xm - 26, ye, 1)
    for x in [70, 98, 126]:
        pass
    b += dash(137, yH, xm - 23, ya1) + dash(137, yH, xm - 46, ye)
    b += text(xm + 34, ya1 + 4, "a_1", size=12, weight=700, anchor="start")
    b += text(xm + 52, ye + 4, "e", size=12, weight=700, anchor="start")
    # mini SALC icons
    b += mini_salc(xm, ya1 + 26, "a1")
    b += mini_salc(xm - 26, ye - 24, "ex")
    b += mini_salc(xm + 26, ye - 24, "ey")
    # splitting brackets
    b += text(310, 130, "", size=9)
    b += f'<line x1="158" y1="{yH}" x2="300" y2="{yH}" stroke="{RULE}" stroke-width="0.8" stroke-dasharray="1 3"/>'
    b += text(300, yH - 4, "H 1s level", size=8.5, anchor="end", fill=MUTED)
    b += text(xm, 218, "H_3 fragment (NH_3 geometry)", size=10, fill=MUTED)
    return svg(W, H, b)


# ---------------------------------------------------------------------------
def overlap_panel_top(cx, cy, porb, coeffs, title, sub1, R=50):
    """Top-view panel: N p (x or y) or s orbital at centre, H SALC around."""
    b = ""
    hp = hpos(cx, cy, R)
    if porb == "s":
        b += lobe_circle(cx, cy, 17, 1)
    elif porb == "px":
        b += p_lobe(cx, cy, 0, 40, 15, 1) + p_lobe(cx, cy, 180, 40, 15, -1)
    elif porb == "py":
        b += p_lobe(cx, cy, -90, 40, 15, 1) + p_lobe(cx, cy, 90, 40, 15, -1)
    elif porb == "px_bad":
        b += p_lobe(cx, cy, 0, 40, 15, 1) + p_lobe(cx, cy, 180, 40, 15, -1)
    for (x, y), c in zip(hp, coeffs):
        if abs(c) < 1e-6:
            b += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="11" fill="none" stroke="{MUTED}" stroke-width="1" stroke-dasharray="2 2"/>'
        else:
            b += lobe_circle(x, y, 22 * abs(c) + 4, 1 if c > 0 else -1)
    if porb != "s":
        b += f'<circle cx="{cx}" cy="{cy}" r="2.6" fill="{INK}"/>'
    b += text(cx, cy + R + 28, title, size=11.5, weight=700)
    b += text(cx, cy + R + 42, sub1, size=9.5, fill=MUTED)
    return b


def fig_overlaps():
    W, H = 650, 345
    b = ""
    a1 = [1 / math.sqrt(3)] * 3
    ex = [2 / math.sqrt(6), -1 / math.sqrt(6), -1 / math.sqrt(6)]
    ey = [0, 1 / math.sqrt(2), -1 / math.sqrt(2)]
    # row 1
    b += overlap_panel_top(100, 72, "s", a1, "N 2s + a_1", "a_1 with a_1: overlap · top view")
    # side view panel for pz
    cx, cy = 325, 56
    b += p_lobe(cx, cy, -90, 38, 14, -1) + p_lobe(cx, cy, 90, 38, 14, 1)
    yplane = cy + 58
    b += f'<line x1="{cx - 80}" y1="{yplane}" x2="{cx + 80}" y2="{yplane}" stroke="{RULE}" stroke-width="1" stroke-dasharray="4 3"/>'
    for x, op in [(cx - 30, 0.55), (cx - 22, 1.0), (cx + 52, 1.0)]:
        b += f'<g opacity="{op}">' + lobe_circle(x, yplane, 18, 1) + '</g>'
    b += f'<circle cx="{cx}" cy="{cy}" r="2.6" fill="{INK}"/>'
    b += text(cx + 86, yplane + 4, "H_3 plane", size=9, anchor="start", fill=MUTED)
    b += text(cx, 150, "N 2p_z + a_1", size=11.5, weight=700)
    b += text(cx, 164, "a_1 with a_1: overlap · side view", size=9.5, fill=MUTED)
    # mismatch panel
    b += overlap_panel_top(545, 72, "px_bad", a1, "N 2p_x + a_1  ✗", "+ and − overlaps cancel: zero net")
    b += f'<rect x="458" y="4" width="176" height="168" rx="8" fill="none" stroke="#e4b343" stroke-width="1.2" stroke-dasharray="5 3"/>'
    # row 2
    b += overlap_panel_top(210, 245, "px", ex, "N 2p_x + e(x)", "e with e: overlap · top view")
    b += overlap_panel_top(440, 245, "py", ey, "N 2p_y + e(y)", "e with e: H1 sits on the node")
    b += f'<line x1="20" y1="180" x2="630" y2="180" stroke="{RULE}" stroke-width="1"/>'
    return svg(W, H, b)


# ---------------------------------------------------------------------------
def fig_mo_diagram():
    HALO[0] = True
    W, H = 660, 470
    b = ARROW_DEFS
    top, bottom = 22, 380
    Emax, Emin = 2.0, -29.0

    def Y(E):
        return top + (Emax - E) / (Emax - Emin) * (bottom - top)

    xN, xM, xH = 165, 352, 550
    # energy axis
    b += f'<line x1="52" y1="{bottom + 6}" x2="52" y2="{top - 4}" stroke="{MUTED}" stroke-width="1.2" marker-end="url(#ax)"/>'
    b += text(48, top - 8, "E / eV", size=10, anchor="start", weight=600, fill=MUTED)
    for E in [0, -5, -10, -15, -20, -25]:
        y = Y(E)
        b += f'<line x1="48" y1="{y:.1f}" x2="56" y2="{y:.1f}" stroke="{MUTED}" stroke-width="1"/>'
        b += text(44, y + 3.5, str(E).replace("-", "−"), size=8.5, anchor="end", fill=MUTED)
    # axis break and core
    yb = bottom + 18
    b += f'<path d="M46,{yb - 4} l12,-5 M46,{yb + 3} l12,-5" stroke="{MUTED}" stroke-width="1.1"/>'
    yc = H - 30
    b += f'<line x1="52" y1="{yb + 6}" x2="52" y2="{yc + 8}" stroke="{MUTED}" stroke-width="1.2"/>'
    b += text(44, yc + 3.5, "≈ −400", size=8.5, anchor="end", fill=MUTED)

    # AO and fragment levels (valence-orbital ionisation energies)
    EN2s, EN2p = -25.6, -13.2
    Ea1, Ee = -14.8, -13.0
    # MOs (qualitative, ordered as in PES)
    E2a1, E1e, E3a1, E4a1, E2e = -27.0, -16.2, -11.6, -1.2, -4.5

    # N column
    b += level(xN, Y(EN2s), 40) + elec(xN, Y(EN2s), 2)
    for dx in [-36, 0, 36]:
        b += level(xN + dx, Y(EN2p), 28) + elec(xN + dx, Y(EN2p), 1)
    b += text(xN - 64, Y(EN2p) + 4, "2p", size=11, weight=700, anchor="end")
    b += text(xN - 64, Y(EN2s) + 4, "2s", size=11, weight=700, anchor="end")
    b += text(xN, Y(EN2p) + 22, "a_1 + e", size=8.5, fill=MUTED)
    b += text(xN, Y(EN2s) + 22, "a_1", size=8.5, fill=MUTED)
    b += level(xN, yc, 40) + elec(xN, yc, 2)
    b += text(xN - 64, yc + 4, "1s", size=11, weight=700, anchor="end")
    b += text(xN, 14, "N", size=12, weight=700)

    # H3 column
    b += level(xH, Y(Ea1), 40) + elec(xH, Y(Ea1), 2)
    b += level(xH - 22, Y(Ee), 34) + level(xH + 22, Y(Ee), 34) + elec(xH - 22, Y(Ee), 1)
    b += text(xH + 46, Y(Ea1) + 4, "a_1", size=11, weight=700, anchor="start")
    b += text(xH + 46, Y(Ee) + 4, "e", size=11, weight=700, anchor="start")
    b += mini_salc(xH + 82, Y(Ea1) + 1, "a1", R=9, s=8)
    b += mini_salc(xH + 72, Y(Ee) - 1, "ex", R=9, s=8)
    b += mini_salc(xH + 98, Y(Ee) - 1, "ey", R=9, s=8)
    b += text(xH, 14, "H_3 fragment", size=12, weight=700)

    # MO column
    b += text(xM, 14, "NH_3 (C_{3v})", size=12, weight=700)
    mo = [(E2a1, 1, 2, "2a_1", "bonding"), (E1e, 2, 2, "1e", "bonding"),
          (E3a1, 1, 2, "3a_1", "HOMO · lone pair"), (E4a1, 1, 0, "4a_1*", "antibonding"),
          (E2e, 2, 0, "2e*", "antibonding")]
    for E, deg, ne, lab, note in mo:
        y = Y(E)
        if deg == 1:
            b += level(xM, y, 44) + elec(xM, y, ne)
        else:
            b += level(xM - 25, y, 40) + level(xM + 25, y, 40)
            b += elec(xM - 25, y, ne) + elec(xM + 25, y, ne)
        b += text(xM + 54, y + 4, lab, size=11, weight=700, anchor="start")
        b += text(xM + 54, y + 16, note, size=8.5, anchor="start", fill=MUTED)
    b += level(xM, yc, 44) + elec(xM, yc, 2)
    b += text(xM + 54, yc + 4, "1a_1", size=11, weight=700, anchor="start")
    b += text(xM + 54, yc + 16, "N 1s core · nonbonding", size=8.5, anchor="start", fill=MUTED)

    # correlation lines: N side (right ends of N levels -> left ends of MO levels)
    nR2s, nR2p = xN + 22, xN + 52
    mL1, mL2 = xM - 24, xM - 47
    lines_N = [(nR2s, EN2s, mL1, E2a1, 1), (nR2s, EN2s, mL1, E4a1, 0.45),
               (nR2p, EN2p, mL1, E3a1, 1), (nR2p, EN2p, mL2, E1e, 1),
               (nR2p, EN2p, mL2, E2e, 1), (nR2p, EN2p, mL1, E4a1, 0.45)]
    for x1, E1, x2, E2, op in lines_N:
        b += dash(x1, Y(E1), x2, Y(E2), op)
    hL1, hL2 = xH - 22, xH - 41
    mR1, mR2 = xM + 24, xM + 47
    lines_H = [(hL1, Ea1, mR1, E2a1, 1), (hL1, Ea1, mR1, E3a1, 0.45), (hL1, Ea1, mR1, E4a1, 1),
               (hL2, Ee, mR2, E1e, 1), (hL2, Ee, mR2, E2e, 1)]
    for x1, E1, x2, E2, op in lines_H:
        b += dash(x1, Y(E1), x2, Y(E2), op)
    b += dash(xN + 22, yc, xM - 24, yc, 1)
    HALO[0] = False
    return svg(W, H, b)


# ---------------------------------------------------------------------------
def sphere(x, y, r, gid="gA"):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="url(#{gid})" stroke="#4e5a6c" stroke-width="0.7"/>'


def fig_cells():
    W, H = 650, 262
    defs = ('<defs><radialGradient id="gA" cx="35%" cy="30%" r="70%"><stop offset="0" stop-color="#f1c9a5"/>'
            '<stop offset="1" stop-color="#b8693a"/></radialGradient>'
            '<radialGradient id="gB" cx="35%" cy="30%" r="70%"><stop offset="0" stop-color="#c9d6f3"/>'
            '<stop offset="1" stop-color="#4865b0"/></radialGradient>'
            '<clipPath id="cpB"><rect x="0" y="0" width="1" height="1"/></clipPath></defs>')
    b = defs + ARROW_DEFS
    s, dx, dy = 108, 46, -34

    def cube(ox, oy, kind):
        out = ""
        P = {}
        for i in (0, 1):
            for j in (0, 1):
                for k in (0, 1):
                    P[(i, j, k)] = (ox + i * s + k * dx, oy - j * s + k * dy)
        edges = []
        for a in P:
            for d in range(3):
                if a[d] == 0:
                    bb = list(a)
                    bb[d] = 1
                    edges.append((a, tuple(bb)))
        hidden = (0, 0, 1)
        for a, c in edges:
            dashp = ' stroke-dasharray="4 3"' if hidden in (a, c) else ""
            out += f'<line x1="{P[a][0]:.1f}" y1="{P[a][1]:.1f}" x2="{P[c][0]:.1f}" y2="{P[c][1]:.1f}" stroke="#6b7480" stroke-width="1.1"{dashp}/>'

        def at(i, j, k):
            return (ox + i * s + k * dx, oy - j * s + k * dy)
        atoms = [((i, j, k), "gA") for i in (0, 1) for j in (0, 1) for k in (0, 1)]
        if kind == "bcc":
            atoms.append(((0.5, 0.5, 0.5), "gB"))
            d0, d1 = at(0, 0, 1), at(1, 1, 0)
            d0, d1 = at(0, 0, 0), at(1, 1, 1)
        else:
            for f in [(0.5, 0.5, 0), (0.5, 0.5, 1), (0, 0.5, 0.5), (1, 0.5, 0.5), (0.5, 0, 0.5), (0.5, 1, 0.5)]:
                atoms.append((f, "gB"))
            d0, d1 = at(0, 0, 0), at(1, 1, 0)
        # diagonal
        out += f'<line x1="{d0[0]:.1f}" y1="{d0[1]:.1f}" x2="{d1[0]:.1f}" y2="{d1[1]:.1f}" stroke="{GREEN}" stroke-width="2.2"/>'
        atoms.sort(key=lambda t: -t[0][2])
        for (i, j, k), g in atoms:
            x, y = at(i, j, k)
            out += sphere(x, y, 9 if g == "gA" else 10, g)
        # edge label a along bottom front edge
        p0, p1 = at(0, 0, 0), at(1, 0, 0)
        out += f'<line x1="{p0[0]:.1f}" y1="{p0[1] + 18:.1f}" x2="{p1[0]:.1f}" y2="{p1[1] + 18:.1f}" stroke="{INK}" stroke-width="0.9" marker-end="url(#ah)" marker-start="url(#ah)"/>'
        out += text((p0[0] + p1[0]) / 2, p0[1] + 32, "a", size=12, weight=700, italic=True)
        return out, d0, d1

    c1, d0, d1 = cube(60, 178, "bcc")
    b += c1
    b += text(118, 232, "BCC: atoms touch along the body diagonal", size=10, fill=MUTED)
    b += text(118, 236, "", size=10)
    b += text(d1[0] + 14, d1[1] + 4, "body diagonal √3 a = 4r", size=10.5, weight=700, fill=GREEN, anchor="start")
    c2, e0, e1 = cube(400, 178, "fcc")
    b += c2
    b += text(458, 232, "FCC: atoms touch along a face diagonal", size=10, fill=MUTED)
    b += text(566, 104, "face diagonal", size=10.5, weight=700, fill=GREEN, anchor="start")
    b += text(566, 118, "√2 a = 4r", size=10.5, weight=700, fill=GREEN, anchor="start")
    b += text(118, 252, "corners 8 × ⅛ + centre 1 = 2 atoms", size=10, weight=600)
    b += text(458, 252, "corners 8 × ⅛ + faces 6 × ½ = 4 atoms", size=10, weight=600)
    # orange = corner, blue = centre/face key
    b += sphere(262, 190, 6, "gA") + text(272, 194, "corner", size=9, anchor="start", fill=MUTED)
    b += sphere(262, 208, 6, "gB") + text(272, 212, "body or face centre", size=9, anchor="start", fill=MUTED)
    return svg(W, H, b)


def fig_sections():
    """Hard-sphere cross-sections that carry the 4r argument."""
    W, H = 650, 150
    r = 32
    b = ('<defs><radialGradient id="gA2" cx="35%" cy="30%" r="70%"><stop offset="0" stop-color="#f1c9a5"/>'
         '<stop offset="1" stop-color="#b8693a"/></radialGradient>'
         '<radialGradient id="gB2" cx="35%" cy="30%" r="70%"><stop offset="0" stop-color="#c9d6f3"/>'
         '<stop offset="1" stop-color="#4865b0"/></radialGradient>')
    # BCC diagonal plane: width a*sqrt2, height a
    a_b = 4 * r / math.sqrt(3)
    wB, hB = a_b * math.sqrt(2), a_b
    x0, y0 = 70, 22
    b += f'<clipPath id="clipB"><rect x="{x0}" y="{y0}" width="{wB:.1f}" height="{hB:.1f}"/></clipPath>'
    a_f = 2 * math.sqrt(2) * r
    x1, y1 = 420, 14
    b += f'<clipPath id="clipF"><rect x="{x1}" y="{y1}" width="{a_f:.1f}" height="{a_f:.1f}"/></clipPath></defs>'
    g = f'<g clip-path="url(#clipB)">'
    for (cx, cy) in [(x0, y0), (x0 + wB, y0), (x0, y0 + hB), (x0 + wB, y0 + hB)]:
        g += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="url(#gA2)" stroke="#4e5a6c" stroke-width="0.8"/>'
    g += f'<circle cx="{x0 + wB/2:.1f}" cy="{y0 + hB/2:.1f}" r="{r}" fill="url(#gB2)" stroke="#4e5a6c" stroke-width="0.8"/>'
    g += '</g>'
    b += g
    b += f'<rect x="{x0}" y="{y0}" width="{wB:.1f}" height="{hB:.1f}" fill="none" stroke="{INK}" stroke-width="1.2"/>'
    b += f'<line x1="{x0}" y1="{y0 + hB:.1f}" x2="{x0 + wB:.1f}" y2="{y0:.1f}" stroke="{GREEN}" stroke-width="2"/>'
    # ticks for r 2r r along diagonal
    L = math.hypot(wB, hB)
    ux, uy = wB / L, -hB / L
    for t in [r, 3 * r]:
        px, py = x0 + ux * t, y0 + hB + uy * t
        b += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="2.4" fill="{GREEN}"/>'
    b += text(x0 + wB / 2, y0 + hB + 18, "a√2 (face diagonal)", size=10, fill=INK)
    b += text(x0 - 8, y0 + hB / 2 + 4, "a", size=12, italic=True, weight=700, anchor="end")
    b += text(x0 + wB + 12, y0 + hB / 2 - 2, "body diagonal", size=10, anchor="start", fill=GREEN, weight=600)
    b += text(x0 + wB + 12, y0 + hB / 2 + 12, "= r + 2r + r = 4r", size=10, anchor="start", fill=GREEN, weight=600)
    b += text(x0 + wB + 12, y0 + hB / 2 + 26, "(√3 a)² = a² + (a√2)²", size=9.5, anchor="start", fill=MUTED)
    b += text(x0 + wB / 2 + 50, 144, "BCC: slice through two opposite edges", size=10, fill=MUTED)
    # FCC face
    g = f'<g clip-path="url(#clipF)">'
    for (cx, cy) in [(x1, y1), (x1 + a_f, y1), (x1, y1 + a_f), (x1 + a_f, y1 + a_f)]:
        g += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="url(#gA2)" stroke="#4e5a6c" stroke-width="0.8"/>'
    g += f'<circle cx="{x1 + a_f/2:.1f}" cy="{y1 + a_f/2:.1f}" r="{r}" fill="url(#gB2)" stroke="#4e5a6c" stroke-width="0.8"/>'
    g += '</g>'
    b += g
    b += f'<rect x="{x1}" y="{y1}" width="{a_f:.1f}" height="{a_f:.1f}" fill="none" stroke="{INK}" stroke-width="1.2"/>'
    b += f'<line x1="{x1}" y1="{y1 + a_f:.1f}" x2="{x1 + a_f:.1f}" y2="{y1:.1f}" stroke="{GREEN}" stroke-width="2"/>'
    L = math.hypot(a_f, a_f)
    for t in [r, 3 * r]:
        px, py = x1 + t / math.sqrt(2), y1 + a_f - t / math.sqrt(2)
        b += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="2.4" fill="{GREEN}"/>'
    b += text(x1 + a_f / 2, y1 + a_f + 18, "a", size=12, italic=True, weight=700)
    b += text(x1 - 8, y1 + a_f / 2 + 4, "a", size=12, italic=True, weight=700, anchor="end")
    b += text(x1 + a_f + 12, y1 + a_f / 2 - 2, "face diagonal", size=10, anchor="start", fill=GREEN, weight=600)
    b += text(x1 + a_f + 12, y1 + a_f / 2 + 12, "= 4r", size=10, anchor="start", fill=GREEN, weight=600)
    b += text(x1 + a_f + 12, y1 + a_f / 2 + 26, "(√2 a)² = a² + a²", size=9.5, anchor="start", fill=MUTED)
    b += text(x1 + a_f / 2 + 40, 144, "FCC: one face of the cube", size=10, fill=MUTED)
    return svg(W, H, b)


# ---------------------------------------------------------------------------
def fig_plots():
    HALO[0] = True
    W, H = 650, 270

    def panel(ox, title, pts, lit=None, trend=None, extrap=None):
        pw, ph = 250, 175
        x0, y0 = ox + 46, 28
        xmin, xmax, ymin, ymax = 0, 140, 100, 400

        def X(v):
            return x0 + (v - xmin) / (xmax - xmin) * pw

        def Yv(v):
            return y0 + ph - (v - ymin) / (ymax - ymin) * ph
        out = ""
        for gy in range(100, 401, 50):
            out += f'<line x1="{x0}" y1="{Yv(gy):.1f}" x2="{x0 + pw}" y2="{Yv(gy):.1f}" stroke="#e7eaee" stroke-width="1"/>'
            out += text(x0 - 6, Yv(gy) + 3.5, str(gy), size=8.5, anchor="end", fill=MUTED)
        for gx in range(0, 141, 20):
            out += f'<line x1="{X(gx):.1f}" y1="{y0 + ph}" x2="{X(gx):.1f}" y2="{y0 + ph + 4}" stroke="{MUTED}" stroke-width="1"/>'
            out += text(X(gx), y0 + ph + 15, str(gx), size=8.5, fill=MUTED)
        out += f'<rect x="{x0}" y="{y0}" width="{pw}" height="{ph}" fill="none" stroke="{MUTED}" stroke-width="1"/>'
        out += text(x0 + pw / 2, y0 + ph + 30, "Relative molecular mass", size=9.5, fill=INK)
        out += text(x0 - 34, y0 + ph / 2, "Boiling point / K", size=9.5, fill=INK,
                    extra=f'transform="rotate(-90 {x0 - 34} {y0 + ph / 2})"')
        out += text(x0 + pw / 2, 16, title, size=11, weight=700)
        if extrap:
            (xa, ya), (xb, yb) = extrap
            out += f'<line x1="{X(xa):.1f}" y1="{Yv(ya):.1f}" x2="{X(xb):.1f}" y2="{Yv(yb):.1f}" stroke="{GREEN}" stroke-width="1.3" stroke-dasharray="5 3"/>'
        if trend:
            d = " ".join(f"{'M' if i == 0 else 'L'}{X(a):.1f},{Yv(c):.1f}" for i, (a, c) in enumerate(trend))
            out += f'<path d="{d}" fill="none" stroke="{GREEN}" stroke-width="1.3" stroke-dasharray="5 3"/>'
        d = " ".join(f"{'M' if i == 0 else 'L'}{X(a):.1f},{Yv(c):.1f}" for i, (a, c, _, _) in enumerate(pts))
        out += f'<path d="{d}" fill="none" stroke="{POS}" stroke-width="1.6"/>'
        for a, c, lab, pos in pts:
            out += f'<circle cx="{X(a):.1f}" cy="{Yv(c):.1f}" r="4" fill="{POS}" stroke="#fff" stroke-width="1"/>'
            dx, dy, anc = {"r": (7, 4, "start"), "l": (-7, 4, "end"), "a": (0, -9, "middle"), "b": (0, 15, "middle")}[pos]
            out += text(X(a) + dx, Yv(c) + dy, lab, size=9.5, anchor=anc, weight=600)
        if lit:
            a, c, lab = lit
            out += f'<circle cx="{X(a):.1f}" cy="{Yv(c):.1f}" r="4" fill="#fff" stroke="{GREEN}" stroke-width="1.6"/>'
            out += text(X(a) + 8, Yv(c) + 12, lab, size=8.5, anchor="start", fill=GREEN)
        return out

    g14 = [(16.04, 109.15, "CH_4", "r"), (32.12, 161.15, "SiH_4", "a"), (76.66, 264.15, "GeH_4", "a"), (122.74, 221.15, "SnH_4", "a")]
    g16 = [(18.02, 373.15, "H_2O", "r"), (34.08, 213.15, "H_2S", "b"), (80.99, 232.15, "H_2Se", "b"), (129.62, 271.15, "H_2Te", "a")]
    b = ""
    b += panel(0, "Group 14 hydrides (sheet values)", g14, lit=(76.66, 184.65, "GeH_4 literature, 185 K"),
               trend=[(16.04, 109.15), (32.12, 161.15), (76.66, 184.65), (122.74, 221.15)])
    m, c0 = 0.6082660792345946, 189.2044576906956
    b += panel(330, "Group 16 hydrides (sheet values)", g16, extrap=((18.02, m * 18.02 + c0), (129.62, m * 129.62 + c0)))
    b += text(384, 182, "H_2S–H_2Te trend line", size=8.5, anchor="start", fill=GREEN)
    b += text(384, 194, "reaches ≈ 200 K at M = 18", size=8.5, anchor="start", fill=GREEN)
    # legend
    b += f'<circle cx="60" cy="262" r="4" fill="{POS}"/>' + text(68, 265, "sheet value, joined", size=9, anchor="start", fill=MUTED)
    b += f'<line x1="200" y1="262" x2="222" y2="262" stroke="{GREEN}" stroke-width="1.3" stroke-dasharray="5 3"/>' + text(228, 265, "trend without the anomaly", size=9, anchor="start", fill=MUTED)
    HALO[0] = False
    return svg(W, H, b)


FIGS = {
    "FIG_NH3": fig_nh3_structure,
    "FIG_SALC": fig_salcs,
    "FIG_H3": fig_h3_diagram,
    "FIG_OVERLAP": fig_overlaps,
    "FIG_MO": fig_mo_diagram,
    "FIG_CELLS": fig_cells,
    "FIG_SECTIONS": fig_sections,
    "FIG_PLOTS": fig_plots,
}

if __name__ == "__main__":
    import sys, os
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for k, f in FIGS.items():
        with open(os.path.join(out, k + ".svg"), "w") as fh:
            fh.write(f())
    print("ok")
