"""Build and verify Lab 3 Part 1 molecules (Cr(CO)6, naphthalene) for Symmetry Bench 3D.
Every class member is checked to be a true symmetry operation; every 'fake' is checked to fail;
the group is closed from the class operations and its order compared with the expected value."""
import json, math, itertools
import numpy as np

TOL = 1e-6

def unit(v):
    v = np.array(v, float); return v / np.linalg.norm(v)

def rot(v, a):
    x, y, z = unit(v); c, s, t = math.cos(a), math.sin(a), 1 - math.cos(a)
    return np.array([[t*x*x+c, t*x*y-s*z, t*x*z+s*y], [t*x*y+s*z, t*y*y+c, t*y*z-s*x], [t*x*z-s*y, t*y*z+s*x, t*z*z+c]])

def ref(v):
    n = unit(v); return np.eye(3) - 2*np.outer(n, n)

def op(kind, n, v):
    if kind == 'C': return rot(v, 2*math.pi/n)
    if kind == 's': return ref(v)
    if kind == 'i': return -np.eye(3)
    return ref(v) @ rot(v, 2*math.pi/n)

def perm(M, atoms):
    X = np.array([a['x'] for a in atoms]); Y = X @ M.T; p = []
    for k, y in enumerate(Y):
        hit = [j for j, a in enumerate(atoms) if a['s'] == atoms[k]['s'] and np.linalg.norm(X[j]-y) < 1e-4]
        if not hit: return None
        p.append(hit[0])
    return p

def cycles(p):
    seen, out = set(), []
    for i in range(len(p)):
        if i in seen or p[i] == i: continue
        c, j = [], i
        while j not in seen: seen.add(j); c.append(j); j = p[j]
        out.append(c)
    return out

def key(M): return tuple(np.round(M, 6).flatten() + 0.0)

def close(gens):
    G = {key(np.eye(3)): np.eye(3)}
    frontier = [np.eye(3)]
    while frontier:
        nxt = []
        for A in frontier:
            for g in gens:
                B = g @ A; k = key(B)
                if k not in G: G[k] = B; nxt.append(B)
        frontier = nxt
    return G

def describe(p, atoms, lab, follow=None, unit_word='atom'):
    """Cycle text. follow: set of indices whose motion is implied (e.g. H with its C, O with its C)."""
    cs = [c for c in cycles(p) if not (follow and c[0] in follow)]
    parts = []
    for c in cs:
        names = [lab(atoms[i]) for i in c]
        parts.append('↔'.join(names) if len(c) == 2 else '→'.join(names))
    fixed = [lab(atoms[i]) for i in range(len(p)) if p[i] == i and not (follow and i in follow)]
    txt = '; '.join(parts) + '.' if parts else 'Nothing moves.'
    txt += (' ' + ', '.join(fixed) + (' stays put.' if len(fixed) == 1 else ' stay put.')) if fixed else f' No {unit_word} stays put.'
    return txt

def check_entry(e, expect_order, follow=None, lab=None):
    atoms = e['atoms']; gens = []; report = []
    for c in e['classes']:
        c['moves'] = []
        for v in c['members']:
            M = op(c['kind'], c['n'], v); p = perm(M, atoms)
            if c.get('fake'):
                assert p is None, f"fake {c['label']} is actually a symmetry op!"
                c['moves'].append('')
            else:
                assert p is not None, f"{c['label']} {v} is NOT a symmetry op"
                gens.append(M); c['moves'].append(describe(p, atoms, lab, follow))
    G = close(gens)
    assert len(G) == expect_order, (e['key'], len(G))
    # every op in G must be a symmetry op
    for M in G.values(): assert perm(M, atoms) is not None
    return len(G)

# ----------------------------------------------------------------- Cr(CO)6
rCrC, rCO = 1.91, 1.14
dirs = {1: (0, 0, 1), 2: (1, 0, 0), 3: (0, 1, 0), 4: (-1, 0, 0), 5: (0, -1, 0), 6: (0, 0, -1)}
cr_atoms = [{"s": "Cr", "label": "Cr", "x": [0.0, 0.0, 0.0], "r": 0.46, "c": "#94a3b8"}]
for k in range(1, 7):
    d = np.array(dirs[k], float)
    cr_atoms.append({"s": "C", "label": "", "x": list(d*rCrC), "r": 0.30, "c": "#475569", "lig": k})
for k in range(1, 7):
    d = np.array(dirs[k], float)
    cr_atoms.append({"s": "O", "label": f"CO<sub>{k}</sub>", "x": list(d*(rCrC+rCO)), "r": 0.31, "c": "#f87171", "lig": k})

s3 = 1/math.sqrt(3); s2 = 1/math.sqrt(2)
C3ax = [[s3, s3, s3], [s3, -s3, s3], [s3, -s3, -s3], [s3, s3, -s3]]
C2pax = [[s2, 0, s2], [0, s2, s2], [s2, 0, -s2], [0, s2, -s2], [s2, s2, 0], [s2, -s2, 0]]
cr = {
    "key": "crco6", "title": "[Cr(CO)<sub>6</sub>]", "part": "Lab 3 · Part 1", "pg": "O<sub>h</sub>", "order": 48,
    "sheetLabel": "Elements to list (point group not required)",
    "sheet": "E, 3C<sub>4</sub> (each also C<sub>2</sub> = C<sub>4</sub><sup>2</sup>), 4C<sub>3</sub>, 6C<sub>2</sub>′, <i>i</i>, 3S<sub>4</sub>, 4S<sub>6</sub>, 3σ<sub>h</sub>, 6σ<sub>d</sub>",
    "note": "48 operations. Same symmetry as the paper octahedron from Lab 2: each Cr–C≡O unit is straight, so the ligands behave like octahedron vertices. Labels sit on the O atoms; the C moves with its O.",
    "poly": False, "atoms": cr_atoms,
    "bonds": [[0, k, 1] for k in range(1, 7)] + [[k, k+6, 3] for k in range(1, 7)],
    "classes": [
        {"kind": "C", "n": 4, "label": "C<sub>4</sub>", "color": "#1d4ed8", "members": [[0, 0, 1], [0, 1, 0], [1, 0, 0]], "what": "Turn 90° about the line"},
        {"kind": "C", "n": 3, "label": "C<sub>3</sub>", "color": "#0f766e", "members": C3ax, "what": "Turn 120° about the line"},
        {"kind": "C", "n": 2, "label": "C<sub>2</sub>′", "color": "#7e22ce", "members": C2pax, "what": "Turn 180° about the line"},
        {"kind": "i", "n": 1, "label": "<i>i</i>", "color": "#be123c", "members": [[0, 0, 0]], "what": "Send each atom through Cr to the other side"},
        {"kind": "S", "n": 4, "label": "S<sub>4</sub>", "color": "#db2777", "members": [[0, 0, 1], [0, 1, 0], [1, 0, 0]], "what": "Turn 90°, then reflect through the plane ⟂ to the line"},
        {"kind": "S", "n": 6, "label": "S<sub>6</sub>", "color": "#9f1239", "members": C3ax, "what": "Turn 60°, then reflect through the plane ⟂ to the line"},
        {"kind": "s", "n": 1, "label": "σ<sub>h</sub>", "color": "#6d28d9", "members": [[0, 0, 1], [0, 1, 0], [1, 0, 0]], "what": "Reflect through the plane"},
        {"kind": "s", "n": 1, "label": "σ<sub>d</sub>", "color": "#c2410c", "members": C2pax, "what": "Reflect through the plane"},
        {"kind": "C", "n": 6, "fake": True, "label": "Try C<sub>6</sub> on a C<sub>3</sub> line", "color": "#64748b", "members": [[s3, s3, s3]],
         "what": "Turn 60° about a C<sub>3</sub> line",
         "msg": "Looking down this line you see six ligands in a zig-zag, three up and three down. A plain 60° turn puts an up-ligand where a down-ligand was: <b>not</b> a symmetry operation. Add a reflection and it works: that is the S<sub>6</sub>."},
        {"kind": "C", "n": 8, "fake": True, "label": "Try C<sub>8</sub> (45°)", "color": "#64748b", "members": [[0, 0, 1]],
         "what": "Turn 45° about a C<sub>4</sub> line",
         "msg": "The four equatorial ligands land between their old positions: <b>not</b> a symmetry operation. The smallest turn that works about this line is 90°."},
    ],
    "principal": [0, 0, 1],
    "view": [[0.9396926207859084, -0.3420201433256687, 0.0], [0.11697777844051097, 0.3213938048432697, 0.9396926207859084], [-0.3213938048432697, -0.8830222215594891, 0.3420201433256687]],
    "check": 48,
    "walk": [
        {"q": "Two or more C<sub>3</sub> (or higher) axes?", "a": "Yes", "show": [0, 1], "detail": "Several high-order axes: a T<sub>d</sub>, O<sub>h</sub> or I<sub>h</sub> shape."},
        {"q": "Two or more C<sub>5</sub> axes?", "a": "No", "show": [], "detail": ""},
        {"q": "Two or more C<sub>4</sub> axes?", "a": "Yes", "show": [0], "detail": "3 C<sub>4</sub> axes."},
        {"q": "Inversion centre?", "a": "Yes", "show": [3], "detail": "At Cr."},
        {"q": "Result", "a": "O<sub>h</sub>", "show": [0, 1, 2, 3, 4, 5, 6, 7], "detail": "Order 48. Students are not asked for this label.", "end": True},
    ],
}

def cr_lab(a):
    if a['s'] == 'Cr': return 'Cr'
    return f"CO<sub>{a['lig']}</sub>"

follow_cr = set(range(1, 7))  # C atoms follow their O
n_cr = check_entry(cr, 48, follow_cr, cr_lab)
for c in cr['classes']:
    c['moves'] = [m.replace(' stay put.', ' stay put.').replace('No atom stays put.', 'No ligand stays put.') for m in c['moves']]
for a in cr_atoms: a.pop('lig', None)

# ----------------------------------------------------------------- naphthalene (xy plane, long axis x)
cc, ch = 1.40, 1.08
h = cc*math.sqrt(3)/2
cpos = {
    'C8a': (0.0, cc/2), 'C1': (h, cc), 'C2': (2*h, cc/2), 'C3': (2*h, -cc/2), 'C4': (h, -cc), 'C4a': (0.0, -cc/2),
    'C5': (-h, -cc), 'C6': (-2*h, -cc/2), 'C7': (-2*h, cc/2), 'C8': (-h, cc),
}
order_c = ['C1', 'C2', 'C3', 'C4', 'C4a', 'C5', 'C6', 'C7', 'C8', 'C8a']
def sub(n): return n[0] + '<sub>' + n[1:] + '</sub>'
na_atoms = []
for n in order_c:
    x, y = cpos[n]; na_atoms.append({"s": "C", "label": sub(n), "x": [x, y, 0.0], "r": 0.30, "c": "#475569", "nm": n})
for k in range(1, 9):
    n = f'C{k}'; x, y = cpos[n]; cx = h if x > 0 else -h
    d = unit([x-cx, y, 0]); p = np.array([x, y, 0]) + d*ch
    na_atoms.append({"s": "H", "label": f"H<sub>{k}</sub>", "x": list(p), "r": 0.22, "c": "#ffffff", "nm": f'H{k}', "on": order_c.index(n)})
idx = {a['nm']: i for i, a in enumerate(na_atoms)}
kek_double = {('C1', 'C2'), ('C3', 'C4'), ('C4a', 'C8a'), ('C5', 'C6'), ('C7', 'C8')}
ring_bonds = [('C1', 'C2'), ('C2', 'C3'), ('C3', 'C4'), ('C4', 'C4a'), ('C4a', 'C8a'), ('C8a', 'C1'),
              ('C4a', 'C5'), ('C5', 'C6'), ('C6', 'C7'), ('C7', 'C8'), ('C8', 'C8a')]
na_bonds = [[idx[a], idx[b], 1] for a, b in ring_bonds] + [[idx[f'C{k}'], idx[f'H{k}'], 1] for k in range(1, 9)]

dg = unit([cpos['C1'][0], cpos['C1'][1], 0])  # line through C1 and C5 (passes through centre)
na = {
    "key": "naph", "title": "Naphthalene C<sub>10</sub>H<sub>8</sub>", "part": "Lab 3 · Part 1", "pg": "D<sub>2h</sub>", "order": 8,
    "sheetLabel": "Elements to list (point group not required)",
    "sheet": "E, C<sub>2</sub>(z), C<sub>2</sub>(y), C<sub>2</sub>(x), <i>i</i>, σ(xy), σ(xz), σ(yz)",
    "note": "8 operations. Same point group as B<sub>2</sub>H<sub>6</sub> in Lab 2. x = long axis, y = short axis through C<sub>4a</sub> and C<sub>8a</sub>, z = ⟂ to the ring plane. Each H moves with its C.",
    "poly": False, "atoms": na_atoms, "bonds": na_bonds,
    "classes": [
        {"kind": "C", "n": 2, "label": "C<sub>2</sub>(z)", "color": "#1d4ed8", "members": [[0, 0, 1]], "what": "Turn 180° about the line ⟂ to the ring plane"},
        {"kind": "C", "n": 2, "label": "C<sub>2</sub>(y)", "color": "#7e22ce", "members": [[0, 1, 0]], "what": "Turn 180° about the short axis (through C<sub>4a</sub>, C<sub>8a</sub>)"},
        {"kind": "C", "n": 2, "label": "C<sub>2</sub>(x)", "color": "#0f766e", "members": [[1, 0, 0]], "what": "Turn 180° about the long axis (no atoms on it)"},
        {"kind": "i", "n": 1, "label": "<i>i</i>", "color": "#be123c", "members": [[0, 0, 0]], "what": "Send each atom through the centre of the C<sub>4a</sub>–C<sub>8a</sub> bond"},
        {"kind": "s", "n": 1, "label": "σ(xy)", "color": "#d97706", "members": [[0, 0, 1]], "what": "Reflect through the ring plane"},
        {"kind": "s", "n": 1, "label": "σ(xz)", "color": "#c2410c", "members": [[0, 1, 0]], "what": "Reflect through the plane ⟂ to the ring, along the long axis"},
        {"kind": "s", "n": 1, "label": "σ(yz)", "color": "#a16207", "members": [[1, 0, 0]], "what": "Reflect through the plane ⟂ to the ring, through C<sub>4a</sub> and C<sub>8a</sub>"},
        {"kind": "C", "n": 6, "fake": True, "label": "Try C<sub>6</sub> (benzene thinking)", "color": "#64748b", "members": [[0, 0, 1]],
         "what": "Turn 60° about the line ⟂ to the plane",
         "msg": "Each ring alone looks like benzene, but the molecule is two rings side by side. A 60° turn swings the long axis out of line: <b>not</b> a symmetry operation. Only the 180° turn about this line works."},
        {"kind": "C", "n": 2, "fake": True, "label": "Try C<sub>2</sub> through C<sub>1</sub> and C<sub>5</sub>", "color": "#64748b", "members": [list(dg)],
         "what": "Turn 180° about the diagonal line through C<sub>1</sub> and C<sub>5</sub>",
         "msg": "C<sub>1</sub> and C<sub>5</sub> stay, but the rest of the molecule swings out of place: <b>not</b> a symmetry operation. The in-plane C<sub>2</sub> axes run along the long and short directions only."},
    ],
    "principal": [0, 0, 1],
    "check": 8,
    "walk": [
        {"q": "Two or more C<sub>3</sub> (or higher) axes?", "a": "No", "show": [], "detail": "None."},
        {"q": "Any rotation axis C<sub>n</sub>?", "a": "Yes: C<sub>2</sub>(z)", "show": [0], "detail": "Three C<sub>2</sub> axes tie; take the one ⟂ to the plane as main. Hold it vertical."},
        {"q": "2 C<sub>2</sub> axes ⟂ to it?", "a": "Yes: 2", "show": [1, 2], "detail": "D family."},
        {"q": "σ<sub>h</sub>?", "a": "Yes", "show": [4], "detail": "The ring plane."},
        {"q": "Result", "a": "D<sub>2h</sub>", "show": [0, 1, 2, 3, 4, 5, 6], "detail": "Order 8. Students are not asked for this label.", "end": True},
    ],
}
def na_lab(a): return a['label']
follow_na = {i for i, a in enumerate(na_atoms) if a['s'] == 'H'}
n_na = check_entry(na, 8, follow_na, na_lab)
for c in na['classes']:
    c['moves'] = [m + (' Each H moves with its C.' if m and 'Nothing moves' not in m else '') for m in c['moves']]
    c['moves'] = [m.replace('Nothing moves. ', 'Every atom stays put: the plane contains the whole molecule. It still counts as an operation; it swaps the top and bottom faces of the ring. ').replace(' Each H moves with its C.', '') if m.startswith('Nothing moves') else m for m in c['moves']]

# Kekulé check: does the drawn (manual) structure keep D2h when single/double bonds are distinguished?
def bond_set_ok(M):
    p = perm(M, na_atoms)
    if p is None: return False
    names = [a['nm'] for a in na_atoms]
    D = {frozenset(b) for b in kek_double}
    return all(frozenset((names[p[idx[a]]], names[p[idx[b]]])) in D for a, b in kek_double)
kek_all = all(bond_set_ok(op(c['kind'], c['n'], v)) for c in na['classes'] if not c.get('fake') for v in c['members'])

for a in na_atoms: a.pop('nm', None); a.pop('on', None)

# view: tilt the plane like the manual's picture
def Rx(t): c, s = math.cos(t), math.sin(t); return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
def Rz(t): c, s = math.cos(t), math.sin(t); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
na['view'] = (Rx(math.radians(-58)) @ Rz(math.radians(-8))).tolist()

# ----------------------------------------------------------------- per-class operation counts for the PDF
def class_ops(e):
    out = []
    for c in e['classes']:
        if c.get('fake'): continue
        out.append((c['label'], len(c['members'])))
    return out

json.dump([cr, na], open('lab3_mols.json', 'w'))
print('Cr(CO)6 order', n_cr, '| naphthalene order', n_na, '| manual Kekule structure keeps D2h:', kek_all)
for e in (cr, na):
    for c in e['classes']:
        print(e['key'], c['label'], len(c['members']), 'FAKE' if c.get('fake') else '', c['moves'][0][:110])
