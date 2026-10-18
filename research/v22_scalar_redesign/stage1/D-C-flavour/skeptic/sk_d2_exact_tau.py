"""SKEPTIC D2 re-test with the EXACT O5 Clebsch at the design orientation (Am45, omega = 0).

o5_clebsch.py (own SO(10) code, designer's stated convention: unit-norm (isometric) CG projection of Delta x Phi):
  k'_R = +0.05176, k'_u = k'_d = +0.08165  =>  tau = 2 sqrt6 (k'_R - k'_d) = -(sqrt3 - 1)/5 = -0.14641 (EXACT),
  vs the designer's settings |tau| = 3 ('typical'), 5 (top-down), 9.8 ('optimistic').
This driver imports the DESIGNER's flavour model read-only (lib_flav, d2_targets, d2_eft_fit, d2_decoupled, d2_joint)
and re-runs, for the realisable chain b (eps = 0.024):
  (1) the decoupled required-coefficient ratio Q = required max|S_ij| at TAU = 0.14641 (sigma = 0);
  (2) the joint 18-observable forward fit (d2_joint.fit_full) with |tau| <= 0.14641, |sigma| <= 1.5 (generous) and caps
      |S_ij| <= 1 (designer's realisability condition |K_ij| <= eps), 2, 4 and 4 pi (NDA ceiling).
Output: sk_d2_exact_tau.json (this folder only).
"""
from __future__ import annotations
import json, math, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
DES = HERE.parent
sys.path.insert(0, str(DES))
import d2_targets as TG  # noqa: E402
import d2_decoupled as Dc  # noqa: E402
import d2_eft_fit as E  # noqa: E402
import d2_joint as J  # noqa: E402

TAU_EXACT = (math.sqrt(3) - 1) / 5
EPS = 0.024
tg = TG.gut_targets("b", floor=0.01)
sols = json.load(open(DES / "fits" / "d2_chainb.json", encoding="utf-8"))
out = {"TAU_exact": TAU_EXACT, "eps": EPS, "chain": "b", "decoupled": {}, "joint": []}
t0 = time.time()
OUT = HERE / "sk_d2_exact_tau.json"
for key, row in sols.items():
    x1 = np.array(row["x"]); m = Dc.charged_mats(x1, tg)
    for vR in (1e16, 3e16, 6e16):
        q = Dc.minimise_Q(m, tg, vR, tg["data"], TAU_EXACT, EPS, seed=2, nstart=15)
        out["decoupled"][f"{key}|vR={vR:.0e}"] = {"chi2_13": row["chi2_13"], "required_max|S|": q["Q"], "chi2_nu": q["chi2_nu"],
                                                   "c_d126": q["c_d126"], "M_R_GeV": q["M_R_GeV"]}
        print(f"[decoupled] rho_max {key} (chi2_13 {row['chi2_13']:.2f}) vR={vR:.0e}: required max|S| = {q['Q']:.2f}  (t={time.time()-t0:.0f}s)", flush=True)
        json.dump(out, open(OUT, "w"), indent=1)

E.TAU, E.SIG = TAU_EXACT, 1.5
for vR in (1e16, 3e16):
    for cap in (1.0, 2.0, 4.0, 4 * math.pi):
        eps_eff = cap * EPS
        best = (1e18, None)
        for key, row in sols.items():
            x1 = np.array(row["x"]); m = Dc.charged_mats(x1, tg)
            nu = Dc.minimise_Q(m, tg, vR, tg["data"], TAU_EXACT, eps_eff, seed=1, nstart=12)
            for ph in (0.0, math.pi):
                x0 = J.seed_full(x1, tg, vR, eps_eff, nu, ph)
                x, c = J.fit_full(x0, tg, vR, eps_eff)
                if c < best[0]:
                    best = (c, x, key)
        c, x, key = best
        summ = E.summarize(x, tg, vR, "o5", eps_eff)
        rec = {"vR": vR, "cap": cap, "chi2": c, "seed": key, "max|S|": summ["max|K|/eps"] * cap,
               "n_pull_gt3": summ.get("n_pull_gt3"), "M_R_GeV": summ.get("M_R_GeV"),
               "tau": summ.get("tau"), "sigma": summ.get("sigma")}
        out["joint"].append(rec)
        print(f"[joint] vR={vR:.0e} cap={cap:.2f}: chi2 = {c:10.3f}  max|S| = {rec['max|S|']:.3f}  n>3 = {rec['n_pull_gt3']}  M_R = {np.array(rec['M_R_GeV'])}  (t={time.time()-t0:.0f}s)", flush=True)
        json.dump(out, open(OUT, "w"), indent=1, default=float)
print("done", time.time() - t0)
