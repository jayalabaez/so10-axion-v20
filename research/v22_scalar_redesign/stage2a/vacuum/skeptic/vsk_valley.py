#!/usr/bin/env python3
"""Explicit light-direction valley at a round point: for a light unit direction u (the most negative effective-quartic
direction found by vsk_light.py, or the most cubic one), V_min(phi) = min_y V(q* + phi u + y), y orthogonal to u (all
531 - 1 other directions relaxed, including the gauge/heavy/other light ones), for phi on a grid.  Compared with the
light-EFT prediction (1/2) m_u^2 phi^2 + C(u) phi^3 + lambda(u) phi^4.  Then a free descent from the deepest valley
point.  Lower values (below the round's 'lower' threshold) are re-evaluated with my independent evaluator.
usage: python -B vsk_valley.py <solution npz> [phi list]
"""
from __future__ import annotations

import json
import sys
import time

import numpy as np
from scipy.optimize import minimize

import vsk_eval as E

sys.path.insert(0, str(E.HERE.parent))
import vc  # noqa: E402

sol = sys.argv[1]
phis = [float(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else \
    [1e-3, 2e-3, 4e-3, 7e-3, 0.01, 0.02, 0.04, 0.07, 0.1, 0.15, 0.2, 0.3, 0.45]
P = np.load(E.BIGV / "pt_O11.npz")
qs = P["q"]
c = E.load_c(sol)
cv = np.array([c[p] for p in vc.IDS])
F = vc.FastV(cv)
Vs = F.value(qs)
Z = np.load(E.BIGS / f"light_{sol[:-4]}.npz")
L, xb, TK, Kvals, w = Z["L"], Z["xb"], Z["TK"], Z["Kvals"], Z["w"]
u = L @ xb
u /= np.linalg.norm(u)
m2 = float(u @ F.hvp(qs, u))
eps = 1e-3
Tuu = (F.value_grad(qs + eps * u)[1] + F.value_grad(qs - eps * u)[1] - 2 * F.value_grad(qs)[1]) / eps ** 2
Cu = float(Tuu @ u) / 6.0
F4 = vc.FastV(cv * (vc.DEG == 4))
lam = float(F4.degree4_value(u)) - 0.125 * float(np.sum((np.einsum("i,j,ijm->m", xb, xb, TK)) ** 2 / Kvals))
print(f"[{sol}] V* {Vs:.12g}; m_u^2 {m2:.4e}; C(u) {Cu:.4e}; lambda(u) {lam:.5f}", flush=True)
out = {"sol": sol, "m_u2": m2, "C_u": Cu, "lambda_u": lam, "valley": []}
Pperp = lambda v: v - u * (u @ v)
y = np.zeros(vc.N)
best = (0.0, None, None)
for phi in phis:
    t0 = time.time()
    def fg(yy):
        yy = Pperp(yy)
        V, g = F.value_grad(qs + phi * u + yy)
        return V - Vs, Pperp(g)
    r = minimize(fg, Pperp(y), jac=True, method="L-BFGS-B",
                 options={"maxiter": 4000, "maxcor": 30, "ftol": 1e-16, "gtol": 1e-13})
    y = Pperp(r.x)
    dv = float(r.fun)
    pred = 0.5 * m2 * phi ** 2 + Cu * phi ** 3 + lam * phi ** 4
    rec = {"phi": phi, "dV_valley": dv, "pred_EFT": pred, "|y|": float(np.linalg.norm(y)),
           "block_norms": {k: float(np.linalg.norm((qs + phi * u + y)[s])) for k, s in vc.BLOCKS.items()}}
    out["valley"].append(rec)
    print(f"  phi {phi:.4g}: dV valley {dv:+.6e}  EFT {pred:+.6e}  |y| {rec['|y|']:.3e} ({time.time() - t0:.0f}s)",
          flush=True)
    if dv < best[0]:
        best = (dv, phi, qs + phi * u + y)
if best[2] is not None:
    qv = best[2]
    dv_mine = E.V(qv, c) - E.V(qs, c)
    out["deepest_valley"] = {"phi": best[1], "dV_fast": best[0], "dV_mine": dv_mine}
    print(f"deepest valley point phi {best[1]}: dV fast {best[0]:+.6e} mine {dv_mine:+.6e}", flush=True)
    r = minimize(lambda x: F.value_grad(x), qv, jac=True, method="L-BFGS-B",
                 options={"maxiter": 6000, "maxcor": 30, "ftol": 1e-16, "gtol": 1e-11})
    qe = r.x
    Hq = F.hessian(qe)
    lmin = float(np.linalg.eigvalsh(Hq)[0])
    dvf = F.value(qe) - Vs
    dvm = E.V(qe, c) - E.V(qs, c)
    out["free_descent_from_valley"] = {"dV_fast": dvf, "dV_mine": dvm, "lam_min": lmin,
                                       "dist_to_qstar": float(np.linalg.norm(qe - qs)),
                                       "block_norms": {k: float(np.linalg.norm(qe[s])) for k, s in vc.BLOCKS.items()}}
    print("free descent:", json.dumps(out["free_descent_from_valley"]), flush=True)
    np.savez_compressed(E.BIGS / f"valley_{sol[:-4]}.npz", qv=qv, qe=qe)
json.dump(out, open(E.HERE / f"vsk_valley_{sol[:-4]}.json", "w"), indent=1, default=float)
