"""D1 (y_s window) re-derived in the ONE-STEP gauge environments of the D-C-flavour designs (ys_core.py = verbatim copy
of R2-V ys_rg.py; only its gauge environment is replaced): SM + light colour states (one loop) + B63 exotics above M_s,
no G3221 segment (v_R = M_U), SO(10) above M_U with alpha_U^-1 of the two-loop unification solution (unif1s.py).
Lower edge of the window: y_s >= M_s / <S>_max = 1e13 / 3.285e13 = 0.304 (quality certificate K_min = 17, unchanged).
Upper edge: y_s cap from y <= sqrt(4 pi) up to M_Pl,red (R2-V definition)."""
import json, math
import numpy as np
from scipy.integrate import solve_ivp
import ys_core as Y

CHAINS = {"a": {"MU": 1.017e16, "aU": 27.53, "light": {(0.0, 0.0, 0.5): 1.0e4, (0.0, 8 / 3, 1.5): 2.248e9}},
          "b": {"MU": 2.16e16, "aU": 25.71, "light": {(1 / 15, 1.0, 5 / 3): 1.0e9, (0.0, 8 / 3, 1.5): 2.95e11}}}
out = {}
for ch, C in CHAINS.items():
    Y.MU = C["MU"]; Y.VR = C["MU"]; Y.AINV_U = C["aU"]
    Y._SO10 = solve_ivp(lambda t, y: [-float(Y.B1_10) / (2 * Y.PI) - float(Y.B2_10) / (8 * Y.PI ** 2) / y[0]],
                        [math.log(Y.MU), math.log(Y.MPL) + 0.05], [Y.AINV_U], rtol=1e-10, atol=1e-12, dense_output=True)
    light = C["light"]

    def g2_env(mu, gx_on, light=light):
        if mu < Y.VR * (1 + 1e-7):
            a = Y.AINV_MZ - Y.B_SM / (2 * Y.PI) * math.log(mu / Y.MZ) - (Y.DB_EXOTIC / (2 * Y.PI) * math.log(mu / Y.MS) if mu > Y.MS else 0.0)
            for db, m in light.items():
                if mu > m:
                    a = a - np.array(db) / (2 * Y.PI) * math.log(mu / m)
            return "SM", (4 * Y.PI / a)[::-1]
        a10 = float(Y._SO10.sol(math.log(mu))[0])
        gx2 = 0.0
        if gx_on and mu > Y.VPHI:
            gx2 = 4 * Y.PI / (1.0 + Y.BX / (2 * Y.PI) * math.log(Y.MPL / mu))
        return "SO10", np.array([4 * Y.PI / a10, gx2])
    Y.g2_env = g2_env
    # segments: SM up to M_U, then SO(10) (the G3221 segment of ys_core has zero length when VR = MU)
    res = {}
    for k, kw in {"gauge, g_X off, rms": dict(gauge=True, gx_on=False, match="rms"),
                  "gauge, g_X off, max": dict(gauge=True, gx_on=False, match="max"),
                  "gauge + U(1)_X alpha_X(MPl)=1, rms": dict(gauge=True, gx_on=True, match="rms")}.items():
        c, who = Y.cap(**kw)
        res[k] = {"y_s_cap": c, "binding": who}
        print(ch, k, round(c, 4), who, flush=True)
    out[ch] = {"MU": C["MU"], "aU": C["aU"], "caps": res, "window": [0.304, min(v["y_s_cap"] for v in res.values())]}
json.dump(out, open("ys_window_1s.json", "w", encoding="utf-8"), indent=1)
print(json.dumps({k: v["window"] for k, v in out.items()}))
