"""Extended Hueckel for NH3 (Hoffmann parameters) to get qualitative MO coefficients for the app."""
import numpy as np, scipy.linalg as la, json, math
A2B = 1/0.529177
d, ang = 1.012, math.radians(106.7)
hh = 2*d*math.sin(ang/2); Rc = hh/math.sqrt(3); hN = math.sqrt(d*d-Rc*Rc)
N = np.array([0, 0, hN])*A2B
Hs = [np.array([Rc*math.cos(t), Rc*math.sin(t), 0])*A2B for t in (0, 2*math.pi/3, 4*math.pi/3)]
zN, zH = 1.950, 1.300
# grid
c = np.array([0, 0, hN/2])*A2B
L, h = 8.0, 0.075
ax = np.arange(-L, L+h/2, h)
X, Y, Z = np.meshgrid(ax+c[0], ax+c[1], ax+c[2], indexing='ij')
dV = h**3
def s1(p, z):
    r = np.sqrt((X-p[0])**2+(Y-p[1])**2+(Z-p[2])**2); return math.sqrt(z**3/math.pi)*np.exp(-z*r)
def n2(p, z, kind):
    dx, dy, dz = X-p[0], Y-p[1], Z-p[2]; r = np.sqrt(dx*dx+dy*dy+dz*dz)
    R = (2*z)**2.5/math.sqrt(24)*r*np.exp(-z*r)
    if kind == 's': return R/math.sqrt(4*math.pi)
    comp = {'x': dx, 'y': dy, 'z': dz}[kind]
    with np.errstate(invalid='ignore', divide='ignore'):
        a = np.where(r > 0, comp/r, 0)
    return R*math.sqrt(3/(4*math.pi))*a
basis = [n2(N, zN, 's'), n2(N, zN, 'x'), n2(N, zN, 'y'), n2(N, zN, 'z')] + [s1(p, zH) for p in Hs]
names = ['N2s', 'N2px', 'N2py', 'N2pz', 'H1', 'H2', 'H3']
n = len(basis)
S = np.zeros((n, n))
for i in range(n):
    for j in range(i, n):
        S[i, j] = S[j, i] = (basis[i]*basis[j]).sum()*dV
print("diag S (should be ~1):", np.round(np.diag(S), 3))
S = S/np.sqrt(np.outer(np.diag(S), np.diag(S)))  # renormalise for grid error
Hii = np.array([-26.0, -13.4, -13.4, -13.4, -13.6, -13.6, -13.6])
K = 1.75
Hm = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        Hm[i, j] = Hii[i] if i == j else K*S[i, j]*(Hii[i]+Hii[j])/2
E, C = la.eigh(Hm, S)
print(np.round(S, 3))
for k in range(n):
    v = C[:, k]
    if v[np.argmax(np.abs(v))] < 0: v = -v
    print(f"{E[k]:8.2f}", " ".join(f"{x:6.2f}" for x in v))
json.dump({"E": E.tolist(), "C": C.T.tolist(), "S": S.tolist(), "names": names,
           "geom": {"Rc": Rc, "hN": hN, "d": d}}, open("eht.json", "w"))
