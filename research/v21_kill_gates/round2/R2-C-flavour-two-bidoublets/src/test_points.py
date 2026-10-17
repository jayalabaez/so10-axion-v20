"""Cross-check: skeptic's round-1 DE point in my proxy and in my exact top-down chain; timing."""
import math, json, time
import numpy as np
import lib_r2c as L
import model_r2c as M

x = np.array([0.21126189059702702, 0.04492979609245994, 0.21505289827528878, -1.8941290577944008, 2.4508827684029044,
              4.919484930834645, -3.72881195473036, -0.5424234932660449, 3.227473439168341, 1.804335277990945,
              -0.32307051465360614, 0.019723473049130604])
d = L.data_set("nufit60_sk", floor=0.01)
for vR, MU in [(3.08e13, 3.05e16), (3.08e13, None)]:
    S = M.make_setup(vR, d, MU=MU)
    tg = S["targets"]
    lay = M.Layout()
    R, c2, aux = M.proxy_eval(x[None], lay, tg, want_obs=True)
    print(f"vR={vR:.2e} MU={S['env']['MU']:.2e}: proxy chi2 = {c2[0]:.2f}")
    print("  proxy pulls:", {k: round(float(R[0, i]), 2) for i, k in enumerate(L.ALL_KEYS)})
    # top-down at the skeptic's composition c_d126 = 0.0294, then scan lc for the best Delta m^2 scale
    best = None
    t0 = time.time()
    for lc in np.linspace(math.log10(0.005), math.log10(0.03), 11):
        o = M.top_down(x, lay, S, tg, lc)
        if o is None:
            continue
        r, pl = M.td_residuals(o, d)
        c = float(np.sum(r**2))
        if best is None or c < best[0]:
            best = (c, lc, pl, o)
    dt = (time.time() - t0) / 11
    print(f"  top-down best over lc: chi2 = {best[0]:.2f} at c_d126 = {10**best[1]:.4f}   ({dt:.3f} s/eval)")
    print("  td pulls:", {k: round(v, 2) for k, v in best[2].items()})
    o, ex = M.top_down(x, lay, S, tg, best[1], want=True)
    print("  extra:", {k: v for k, v in ex.items() if k in ("comp", "Y10_act_max", "Y126_act_max", "M_R_GeV")})
