"""Find the 2D lattice of a tile-pattern photo by autocorrelation.
usage: python3 findlattice.py photo.jpg [out_overlay.png]
Prints the reduced primitive basis (px, in the photo's own pixels), angle, a lattice-type guess, and writes an overlay PNG."""
import sys, math, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

def load(path, maxdim=900):
    im = Image.open(path).convert('L'); s = min(1.0, maxdim / max(im.size))
    small = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS) if s < 1 else im
    return im, np.asarray(small, float), s

def autocorr(g):
    g = g - g.mean(); h, w = g.shape
    win = np.outer(np.hanning(h), np.hanning(w)); g = g * win
    F = np.fft.fft2(g, s=(2 * h, 2 * w)); A = np.fft.ifft2(F * np.conj(F)).real
    A = np.fft.fftshift(A); return A / A.max()

def peaks(A, rmin=6, thr=0.12, k=60):
    H, W = A.shape; cy, cx = H // 2, W // 2
    from scipy.ndimage import maximum_filter
    M = (A == maximum_filter(A, size=9)) & (A > thr)
    ys, xs = np.nonzero(M); out = []
    for y, x in zip(ys, xs):
        v = np.array([x - cx, y - cy], float)
        if np.hypot(*v) < rmin: continue
        # sub-pixel refine (parabolic)
        if 0 < y < H - 1 and 0 < x < W - 1:
            dx = 0.5 * (A[y, x - 1] - A[y, x + 1]) / (A[y, x - 1] - 2 * A[y, x] + A[y, x + 1] + 1e-12)
            dy = 0.5 * (A[y - 1, x] - A[y + 1, x]) / (A[y - 1, x] - 2 * A[y, x] + A[y + 1, x] + 1e-12)
            v += [dx, dy]
        out.append((A[y, x], v))
    out.sort(key=lambda t: -t[0]); return out[:k]

def reduce_basis(a, b):
    a, b = np.array(a, float), np.array(b, float)
    for _ in range(50):
        if np.dot(b, b) < np.dot(a, a): a, b = b, a
        m = round(np.dot(a, b) / np.dot(a, a))
        if m == 0: break
        b = b - m * a
    if np.dot(a, b) > 0 and np.hypot(*(b - a)) < np.hypot(*b): b = b - a  # prefer obtuse-or-right convention
    return a, b

def find(path):
    full, g, s = load(path); A = autocorr(g); P = peaks(A)
    if len(P) < 2: raise SystemExit('No repeat found: is the photo sharp and flat-on?')
    strong = [v for h, v in P if h > 0.35 * P[0][0]] or [v for h, v in P]
    strong.sort(key=lambda v: np.hypot(*v))
    a = strong[0]
    b = next((v for v in strong[1:] if abs(a[0] * v[1] - a[1] * v[0]) > 0.25 * np.hypot(*a) * np.hypot(*v)), None)
    if b is None: raise SystemExit('Only one repeat direction found.')
    a, b = reduce_basis(a, b)
    if a[0] < 0 or (abs(a[0]) < 1e-9 and a[1] < 0): a = -a
    if a[0] * b[1] - a[1] * b[0] < 0: b = -b  # right-handed on screen (y down)
    a, b = a / s, b / s
    la, lb = np.hypot(*a), np.hypot(*b); ang = math.degrees(math.acos(np.clip(np.dot(a, b) / la / lb, -1, 1)))
    eq = abs(la - lb) / max(la, lb) < 0.04
    if eq and abs(ang - 90) < 3: t = 'square'
    elif eq and (abs(ang - 60) < 3 or abs(ang - 120) < 3): t = 'hexagonal'
    elif abs(ang - 90) < 3: t = 'rectangular'
    elif eq: t = 'centred rectangular (rhombic primitive cell)'
    elif abs(lb * math.cos(math.radians(ang)) - la / 2) / la < 0.04 or abs(la * math.cos(math.radians(ang)) - lb / 2) / lb < 0.04: t = 'centred rectangular'
    else: t = 'oblique'
    return full, a, b, la, lb, ang, t

def overlay(full, a, b, out, o=None):
    im = full.convert('RGB'); d = ImageDraw.Draw(im, 'RGBA'); W, H = im.size
    o = np.array(o if o is not None else [W / 2, H / 2])
    for i in range(-30, 31):
        for j in range(-30, 31):
            p = o + i * a + j * b
            if -50 < p[0] < W + 50 and -50 < p[1] < H + 50: d.ellipse([p[0] - 4, p[1] - 4, p[0] + 4, p[1] + 4], fill=(29, 78, 216, 230))
    P = [o, o + a, o + a + b, o + b]
    d.polygon([tuple(q) for q in P], fill=(21, 128, 61, 60), outline=(21, 128, 61, 255), width=max(3, W // 300))
    im.save(out)

if __name__ == '__main__':
    path = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else path.rsplit('.', 1)[0] + '_cell.png'
    full, a, b, la, lb, ang, t = find(path); overlay(full, a, b, out)
    print(json.dumps({'a': [round(x, 1) for x in a], 'b': [round(x, 1) for x in b], '|a|': round(la, 1), '|b|': round(lb, 1), 'angle': round(ang, 1), 'type_guess': t, 'overlay': out}))
