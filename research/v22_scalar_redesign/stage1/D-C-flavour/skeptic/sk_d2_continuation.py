"""SKEPTIC D2: chi2 versus the O5 coefficient cap at the EXACT Clebsch |tau| = (sqrt3-1)/5, chain b, v_R = 1e16,
by continuation DOWNWARD from the cap = 4 pi solution (each step seeded by the previous optimum with K clipped to the
new cap), so that the trade-off path is followed instead of restarting from the decoupled seed.
Designer's model imported read-only (d2_eft_fit, d2_joint, d2_decoupled, d2_targets).  Output: sk_d2_continuation.json
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
vR = float(sys.argv[1]) if len(sys.argv) > 1 else 1e16
tg = TG.gut_targets("b", floor=0.01)
sols = json.load(open(DES / "fits" / "d2_chainb.json", encoding="utf-8"))
E.TAU, E.SIG = TAU_EXACT, 1.5
sig = lambda u: 1 / (1 + math.exp(-u))
t0 = time.time()
cap0 = 4 * math.pi
best = (1e18, None)
for key, row in sols.items():
    x1 = np.array(row["x"]); m = Dc.charged_mats(x1, tg)
    nu = Dc.minimise_Q(m, tg, vR, tg["data"], TAU_EXACT, cap0 * EPS, seed=1, nstart=12)
    for ph in (0.0, math.pi):
        x0 = J.seed_full(x1, tg, vR, cap0 * EPS, nu, ph)
        x, c = J.fit_full(x0, tg, vR, cap0 * EPS)
        if c < best[0]:
            best = (c, x)
c, x = best
res = {"vR": vR, "TAU": TAU_EXACT, "path": []}
cap_prev = cap0
for cap in [cap0, 11.0, 10.0, 9.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0]:
    if cap != cap_prev:
        xs = x.copy()
        for n in range(len(E.SYM)):
            k = cap_prev * EPS * sig(xs[16 + 2 * n])
            xs[16 + 2 * n] = J.logit(min(k / (cap * EPS), 0.999))
        x, c = J.fit_full(xs, tg, vR, cap * EPS, nfev=8000)
    summ = E.summarize(x, tg, vR, "o5", cap * EPS)
    rec = {"cap": cap, "chi2": c, "max|S|": summ["max|K|/eps"] * cap, "n_pull_gt3": summ.get("n_pull_gt3"), "M_R_GeV": summ.get("M_R_GeV")}
    res["path"].append(rec)
    print(f"cap {cap:6.2f}: chi2 = {c:10.3f}  max|S| = {rec['max|S|']:.3f}  n>3 = {rec['n_pull_gt3']}  (t={time.time()-t0:.0f}s)", flush=True)
    json.dump(res, open(HERE / f"sk_d2_continuation_{vR:.0e}.json", "w"), indent=1, default=float)
    cap_prev = cap
print("done")
