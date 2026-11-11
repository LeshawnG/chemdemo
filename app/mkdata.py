import json, numpy as np, math
d = json.load(open("eht.json"))
E = np.array(d["E"]); C = np.array(d["C"]); S = np.array(d["S"])
def snorm(v): return v / math.sqrt(v @ S @ v)
mos = {}
order = np.argsort(E)
v = [C[k] for k in order]
# indices: 0 2a1, 1-2 1e, 3 3a1, 4-5 2e*, 6 4a1*
def fix(u, comp):
    u = snorm(u); return u if u[comp] > 0 else -u
def split(a, b):
    # x member: py = 0 ; y member: px = 0
    x = b[2] * a - a[2] * b; y = b[1] * a - a[1] * b
    return fix(x, 1), fix(y, 2)
e1x, e1y = split(v[1], v[2]); e2x, e2y = split(v[4], v[5])
a2 = fix(v[0], 0); a3 = fix(v[3], 3); a4 = fix(v[6], 0)
out = {"2a1": a2, "1ex": e1x, "1ey": e1y, "3a1": a3, "2ex": e2x, "2ey": e2y, "4a1": a4}
res = {k: [round(float(x), 3) for x in u] for k, u in out.items()}
res["_E"] = {"2a1": E[order[0]], "1e": E[order[1]], "3a1": E[order[3]], "2e": E[order[4]], "4a1": E[order[6]]}
res["_S"] = {"sH": round(float(S[0, 4]), 3), "pxH1": round(float(S[1, 4]), 3), "pzH": round(float(S[3, 4]), 3), "HH": round(float(S[4, 5]), 3)}
res["_geom"] = d["geom"]
for k, u in res.items(): print(k, u)
json.dump(res, open("mo.json", "w"))
