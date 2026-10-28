"""Tiny SVG 3D renderer for the Lab 3 companion: balls, sticks, translucent planes, axes, labels.
All figures are drawn from the same verified coordinates as the app."""
import math, json
import numpy as np

INK = '#1f2937'; MUTED = '#64748b'

def rot(v, a):
    x, y, z = np.array(v, float) / np.linalg.norm(v); c, s, t = math.cos(a), math.sin(a), 1 - math.cos(a)
    return np.array([[t*x*x+c, t*x*y-s*z, t*x*z+s*y], [t*x*y+s*z, t*y*y+c, t*y*z-s*x], [t*x*z-s*y, t*y*z+s*x, t*z*z+c]])
def ref(v): n = np.array(v, float) / np.linalg.norm(v); return np.eye(3) - 2*np.outer(n, n)
def op(kind, n, v):
    if kind == 'C': return rot(v, 2*math.pi/n)
    if kind == 's': return ref(v)
    if kind == 'i': return -np.eye(3)
    return ref(v) @ rot(v, 2*math.pi/n)
def Rx(t): c, s = math.cos(t), math.sin(t); return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
def Ry(t): c, s = math.cos(t), math.sin(t); return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
def Rz(t): c, s = math.cos(t), math.sin(t); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])

def shade(hexc, f):
    hexc = hexc.lstrip('#'); r, g, b = (int(hexc[i:i+2], 16) for i in (0, 2, 4))
    if f > 0: r, g, b = (int(x + (255 - x) * f) for x in (r, g, b))
    else: r, g, b = (int(x * (1 + f)) for x in (r, g, b))
    return f'#{r:02x}{g:02x}{b:02x}'

class Scene:
    """World: z up. View V maps world → (x right, y up, z toward viewer)."""
    def __init__(self, V, w, h, scale, cx=None, cy=None):
        self.V, self.w, self.h, self.s = V, w, h, scale
        self.cx, self.cy = (w/2 if cx is None else cx), (h/2 if cy is None else cy)
        self.items = []; self.defs = set(); self.top = []
    def P(self, p):
        q = self.V @ np.array(p, float); return (self.cx + q[0]*self.s, self.cy - q[1]*self.s, q[2])
    def ball(self, p, r, color, label=None, lab_color=INK, lab_size=11, dim=False, stroke=None, dash=False, flat=False):
        x, y, z = self.P(p); gid = 'g' + color.lstrip('#') + ('d' if dim else '')
        if not flat: self.defs.add((gid, color, dim))
        op = ' opacity="0.22"' if dim else ''
        st = f' stroke="{stroke}" stroke-width="1.6"' if stroke else f' stroke="{shade(color, -0.45)}" stroke-width="0.7"'
        if dash: st += ' stroke-dasharray="3 2"'
        fill = color if flat else f'url(#{gid})'
        svg = f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r*self.s:.1f}" fill="{fill}"{st}{op}/>'
        if label is not None:
            svg += f'<text x="{x:.1f}" y="{y + lab_size*0.36:.1f}" text-anchor="middle" font-size="{lab_size}" font-weight="700" fill="{lab_color}">{label}</text>'
        self.items.append((z, svg))
    def stick(self, p, q, w, color='#8b93a5', dim=False, dash=None):
        x1, y1, z1 = self.P(p); x2, y2, z2 = self.P(q)
        op = ' opacity="0.25"' if dim else ''
        da = f' stroke-dasharray="{dash}"' if dash else ''
        self.items.append(((z1 + z2) / 2 - 0.001, f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{w:.1f}" stroke-linecap="round"{op}{da}/>'))
    def poly(self, pts, fill, op=0.18, stroke=None, z=None, sw=1.2, dash=None):
        P = [self.P(p) for p in pts]; zz = np.mean([t[2] for t in P]) if z is None else z
        d = ' '.join(f'{x:.1f},{y:.1f}' for x, y, _ in P)
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ''
        if dash: st += f' stroke-dasharray="{dash}"'
        self.items.append((zz, f'<polygon points="{d}" fill="{fill}" fill-opacity="{op}"{st} stroke-linejoin="round"/>'))
    def line(self, p, q, color, w=2.2, z=None, dash=None, top=False):
        x1, y1, z1 = self.P(p); x2, y2, z2 = self.P(q)
        da = f' stroke-dasharray="{dash}"' if dash else ''
        svg = f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{w}" stroke-linecap="round"{da}/>'
        if top: self.top.append(svg)
        else: self.items.append(((z1 + z2) / 2 if z is None else z, svg))
    def text(self, p, t, color=INK, size=11, weight=700, anchor='middle', dx=0, dy=0, halo=True):
        x, y, _ = self.P(p)
        h = f' stroke="#ffffff" stroke-width="3" paint-order="stroke"' if halo else ''
        self.top.append(f'<text x="{x+dx:.1f}" y="{y+dy:.1f}" text-anchor="{anchor}" font-size="{size}" font-weight="{weight}" fill="{color}"{h}>{t}</text>')
    def axis(self, v, L, color, label=None, w=2.6, dashed=False):
        """Axis drawn as two half-segments so depth sorting puts the far half behind, near half in front."""
        v = np.array(v, float) / np.linalg.norm(v)
        for sgn in (1, -1):
            self.line([0, 0, 0], v * L * sgn, color, w, dash='5 4' if dashed else None)
        if label: self.text(v * (L + 0.35), label, color=color, size=12)
    def plane(self, n, R, color, op=0.16):
        n = np.array(n, float) / np.linalg.norm(n)
        u = np.cross(n, [0, 0, 1]); u = u if np.linalg.norm(u) > 1e-6 else np.cross(n, [1, 0, 0]); u /= np.linalg.norm(u); w = np.cross(n, u)
        pts = [R * (a*u + b*w) for a, b in ((1, 1), (-1, 1), (-1, -1), (1, -1))]
        # split into 4 quadrants for better depth ordering against atoms
        for (a0, a1), (b0, b1) in (((0, 1), (0, 1)), ((-1, 0), (0, 1)), ((-1, 0), (-1, 0)), ((0, 1), (-1, 0))):
            q = [R*(a0*u + b0*w), R*(a1*u + b0*w), R*(a1*u + b1*w), R*(a0*u + b1*w)]
            self.poly(q, color, op)
        P = [self.P(p) for p in pts]
        d = ' '.join(f'{x:.1f},{y:.1f}' for x, y, _ in P)
        self.top.append(f'<polygon points="{d}" fill="none" stroke="{color}" stroke-width="1.2" stroke-opacity="0.8"/>')
    def rect_plane(self, u, w, ru, rw, color, op=0.16):
        u, w = np.array(u, float), np.array(w, float)
        for (a0, a1), (b0, b1) in (((0, 1), (0, 1)), ((-1, 0), (0, 1)), ((-1, 0), (-1, 0)), ((0, 1), (-1, 0))):
            self.poly([a0*ru*u + b0*rw*w, a1*ru*u + b0*rw*w, a1*ru*u + b1*rw*w, a0*ru*u + b1*rw*w], color, op)
        P = [self.P(a*ru*u + b*rw*w) for a, b in ((1, 1), (-1, 1), (-1, -1), (1, -1))]
        d = ' '.join(f'{x:.1f},{y:.1f}' for x, y, _ in P)
        self.top.append(f'<polygon points="{d}" fill="none" stroke="{color}" stroke-width="1.2" stroke-opacity="0.8"/>')
    def svg(self, extra=''):
        defs = ''.join(
            f'<radialGradient id="{gid}" cx="35%" cy="32%" r="70%"><stop offset="0" stop-color="{shade(c, 0.55)}"/><stop offset="0.55" stop-color="{c}"/><stop offset="1" stop-color="{shade(c, -0.35)}"/></radialGradient>'
            for gid, c, dim in sorted(self.defs))
        body = ''.join(s for _, s in sorted(self.items, key=lambda t: t[0]))
        return (f'<svg viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" xmlns="http://www.w3.org/2000/svg" font-family="IBM Plex Sans, sans-serif">'
                f'<defs>{defs}</defs>{body}{"".join(self.top)}{extra}</svg>')

# ---------------------------------------------------------------- molecules (same data as the app)
MOLS = {m['key']: m for m in json.load(open(__file__.rsplit('/', 1)[0] + '/lab3_mols.json'))}

def perm(M, atoms):
    X = np.array([a['x'] for a in atoms]); Y = X @ M.T; p = []
    for k, y in enumerate(Y):
        hit = [j for j, a in enumerate(atoms) if a['s'] == atoms[k]['s'] and np.linalg.norm(X[j] - y) < 1e-4]
        p.append(hit[0] if hit else None)
    return p
