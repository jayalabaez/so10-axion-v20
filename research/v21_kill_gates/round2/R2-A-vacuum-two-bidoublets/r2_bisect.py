"""Bisection along the segment c(tau) = (1-tau) c_lo + tau c_hi between two feasible solutions with the same light
subspaces (the feasible set is convex for fixed U; verified a posteriori) to hit lambda_eff = target.
usage: python -B k3_bisect.py <c_lo npz> <c_hi npz> <target> <out tag> [which: all|heavy]
"""
from __future__ import annotations
import sys, json, numpy as np
import k3_common as K
import r2_verify as VF

lo = np.load(K.SCRATCH / sys.argv[1]); hi = np.load(K.SCRATCH / sys.argv[2]); target = float(sys.argv[3]); tag = sys.argv[4]
which = sys.argv[5] if len(sys.argv) > 5 else "all"
c_lo, c_hi = lo["c"], hi["c"]
key = "lambda_eff_all" if which == "all" else "lambda_eff_heavy"
def lam(tau): return VF.lambda_eff_exact((1 - tau) * c_lo + tau * c_hi)[key]
f_lo, f_hi = lam(0.0), lam(1.0)
print(f"lambda_eff({key}) at tau=0: {f_lo:.6g}, tau=1: {f_hi:.6g}; target {target}")
# coarse scan to find the first bracket (lambda_eff need not be monotone: it is concave in tau)
taus = np.linspace(0, 1, 41); vals = [lam(t) for t in taus]
print("scan:", " ".join(f"{t:.3f}:{v:.4g}" for t, v in zip(taus, vals)))
bracket = None
for i in range(len(taus) - 1):
    if (vals[i] - target) * (vals[i + 1] - target) <= 0: bracket = (taus[i], taus[i + 1]); break
if bracket is None: raise SystemExit("no bracket: target outside the range on the segment")
a, b = bracket; fa = lam(a) - target
for _ in range(60):
    m = 0.5 * (a + b); fm = lam(m) - target
    if fa * fm <= 0: b = m
    else: a, fa = m, fm
    if abs(b - a) < 1e-12: break
tau = 0.5 * (a + b); c = (1 - tau) * c_lo + tau * c_hi
rep = VF.verify(c, screen=True); rep["tau"] = tau; rep["target"] = target; rep["which"] = key
ids = [str(x) for x in lo["ids"]]
np.savez(K.SCRATCH / f"{tag}.npz", c=c, ids=np.array(ids), tau=tau, **{k: lo[k] for k in lo.files if k.startswith("U")})
json.dump({"c": {ids[i]: float(c[i]) for i in range(len(ids))}, **rep}, open(K.SCRATCH / f"{tag}.json", "w"), indent=1, default=float)
print(json.dumps({k: v for k, v in rep.items() if k not in ("subspace_screen",)}, default=float, indent=None)[:3000])
for s in rep["subspace_screen"]:
    print(f"screen {s['mode']}: V* = {s['V_star']:.9g}, V_min_all = {s['V_min_all']:.9g}, n_lower_non_orbit = {s['n_lower_non_orbit']}, runaway = {s['runaway']}, lowest_non_orbit V = {s['lowest_non_orbit'][0][0] if s['lowest_non_orbit'] else None}")
print("saved", tag)
