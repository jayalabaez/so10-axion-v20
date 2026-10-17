"""sk2: f1-sector (V1', Vb1) decay channels R2-V's relic enumeration did not consider: two-fermion f1-f2 MIXING
operators (one f1 field, one f2 field V2/Vb2/V3/Vb3, scalars S, Phi17, <= 1 H-type leg, derivative for opposite
chirality), lowest dimension, plus the resulting EST lifetime of the S-scale f1 state through its f2 admixture
(f2 decays promptly via dim 7, R2-V/relics.log).  Also re-derives the lowest direct f1 -> F operator (dim 12).
EST only (O(1) coefficients, Delta M ~ M_s for the mixing denominator)."""
import itertools, json, math
from pathlib import Path
import importlib.util
spec = importlib.util.spec_from_file_location("t", str(Path(__file__).with_name("sk2_tight2.py")))
t = importlib.util.module_from_spec(spec); spec.loader.exec_module(t)
S, P, MPL, MS, HB = 3.0e13, 1.0e17, 2.435e18, 1.0e13, 6.582e-25
items = []
for n, r, x, g in t.FERM:
    items.append(dict(lab=n, rep=r, X=x, z=t.ZC[r], dot=0, sp=n))
    items.append(dict(lab=n + "^", rep=t.CONJ[r], X=-x, z=(-t.ZC[r]) % 4, dot=1, sp=n))
F1, F2 = {"V1", "Vb1", "Pb"}, {"V2", "Vb2", "V3", "Vb3"}
def scan(setA, setB):
    out = []
    for a in items:
        if a["sp"] not in setA: continue
        for b in items:
            if b["sp"] not in setB: continue
            deriv = 1 if a["dot"] != b["dot"] else 0
            for hn, hr, hx in t.HTYPE:
                if (a["z"] + b["z"] + t.ZC[hr]) % 4: continue
                if t.CONJ[hr] not in t.prod(a["rep"], b["rep"]): continue
                for p in range(-8, 9):
                    rest = -(a["X"] + b["X"] + hx + 17 * p)
                    if rest % 4: continue
                    k = rest // 4
                    d = 3 + deriv + (hn != "none") + abs(k) + abs(p)
                    out.append((d, a["lab"], b["lab"], hn, k, p, deriv))
    out.sort()
    return out
mix = scan(F1, F2)[:8]
sm = scan(F1, {"F"})[:6]
res = {"lowest f1-f2 mixing ops (d, a, b, Hleg, k_S, p_Phi17, deriv)": mix, "lowest f1-F ops": sm}
# EST for the best no-H-leg mixing op with both legs physical-mass-type (V1-Vb2 like)
best = [m for m in mix if m[3] == "none"][0]
d, a, b, hn, k, p, dv = best
delta = MPL * (S / MPL) ** abs(k) * (P / MPL) ** abs(p) * (MPL / MPL) ** 0  # mass mixing (GeV) = vevs / MPL^(d-4) ... * MPL^(4-3)
delta = (S ** abs(k)) * (P ** abs(p)) / MPL ** (d - 4)
if dv:
    delta *= MS  # derivative -> momentum ~ M_s
theta = delta / MS
c2 = (S / MPL) ** 2 * (P / MPL)       # f2 -> F H coupling (dim 7 V2 F H10* S^2 Phi17)
G_chain = (theta * c2) ** 2 * MS / (8 * math.pi)
c12 = (S / MPL) ** 8                 # direct dim 12 V1 F H10* S^8
G_dir = c12 ** 2 * MS / (8 * math.pi)
res["best_mixing_op"] = best
res["delta_GeV"] = delta
res["theta(DeltaM~M_s)"] = theta
res["tau_chain_s (EST)"] = HB / G_chain
res["tau_direct_dim12_s (EST)"] = HB / G_dir
res["ratio"] = G_chain / G_dir
print(json.dumps(res, indent=1))
Path(__file__).with_name("sk2_relic.json").write_text(json.dumps(res, indent=1))
