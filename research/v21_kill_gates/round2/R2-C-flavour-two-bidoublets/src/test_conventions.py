"""Convention / machinery tests for R2-C (run once, log kept)."""
import math, json, time, sys
import numpy as np
import lib_r2c as L
import model_r2c as M

np.set_printoptions(precision=5, suppress=False, linewidth=160)
d = L.data_set("nufit60_sk", floor=0.01)
out = {}
# (a) round trip at M_Z
Yu, Yd, Ye, kap = M.data_matrices(d)
o = L.observables(Yu, Yd, Ye, kap * L.VEV**2)
err = {k: (o[k] - d[k][0]) for k in ["s12", "s23", "s13", "delta", "sin2_th12", "sin2_th23", "sin2_th13", "dm21", "dm31"]}
print("(a) round trip residuals:", {k: f"{v:.2e}" for k, v in err.items()}, " delta_pmns(deg)=", math.degrees(o["delta_pmns"]) % 360)
out["roundtrip_max_abs"] = max(abs(v) for v in err.values())
out["roundtrip_delta_pmns_deg"] = math.degrees(o["delta_pmns"]) % 360
assert out["roundtrip_max_abs"] < 1e-9
assert abs(o["delta"] - d["delta"][0]) < 1e-9, "CKM delta sign convention"

# (b) SM CKM running test (no B63 shift): s23(2e16)/s23(MZ)
gz = L.gauge_mz()
st = L.SMState(gz, 0.26, Yu, Yd, Ye, kap)
t0 = time.time()
st2 = L.run_sm(st, L.MZ, 2e16)
o2 = L.observables(st2.Yu, st2.Yd, st2.Ye, st2.kappa * L.VEV**2)
print("(b) SM to 2e16: s23 ratio", o2["s23"] / o["s23"], " s13 ratio", o2["s13"] / o["s13"], " s12 ratio", o2["s12"] / o["s12"],
      " m_t(2e16)", o2["m_t"], " m_b", o2["m_b"], " m_tau", o2["m_tau"], " a^-1", [4 * math.pi / g**2 for g in st2.g], f" t={time.time()-t0:.2f}s")
out["sm_2e16"] = {"s23_ratio": o2["s23"] / o["s23"], "s13_ratio": o2["s13"] / o["s13"], "m_t": o2["m_t"], "m_b": o2["m_b"], "m_tau": o2["m_tau"],
                  "alpha_inv": [4 * math.pi / g**2 for g in st2.g], "dm31_ratio": o2["dm31"] / o["dm31"]}
# (c) b coefficients
for c in ["C2", "C2m", "T3"]:
    print("(c) b_G3221", c, "with S-sector:", [str(x) for x in L.b_g3221(c, True)], " without:", [str(x) for x in L.b_g3221(c, False)])
out["b"] = {c: {"with_S": [str(x) for x in L.b_g3221(c, True)], "without_S": [str(x) for x in L.b_g3221(c, False)]} for c in ["C2", "C2m", "T3"]}
# K5 cross-check: T2 content = bid + 822 + 831 + 131 + DR, GUT-normalised b_BL = 3/2 b_q
T2 = L.addv(L.GAUGE, *([L.ONE16] * 11), *([L.ONE10] * 2), L.SCAL["bid"], L.SCAL["822"], L.SCAL["831"], L.SCAL["131"], L.SCAL["DR"])
print("(c) T2 check vs K5 (47/6, 12, 29/3, 89/6 GUT-norm):", [str(x) for x in T2[:3]], str(T2[3] * L.Fr(3, 2)))
out["T2_check"] = [str(x) for x in T2[:3]] + [str(T2[3] * L.Fr(3, 2))]
# (d) setups and environment for all v_R
envs = {}
for vR in [1e11, 1e12, 3e12, 1e13, 3e13, 1e14]:
    t0 = time.time()
    S = M.make_setup(vR, d)
    e = S["env"]
    tg = S["targets"]
    print(f"(d) vR={vR:.0e}: MU={e['MU']:.3e} ({e['MU_status']}; {e['gBL_status']}) a^-1(vR)={np.round(e['alpha_inv_vR'],2)} "
          f"a^-1(MU)={np.round(e['alpha_inv_MU'],2)} eta={tg.info['eta']}  t={time.time()-t0:.1f}s")
    print("     targets: mt %.3f mb %.4f mtau %.4f mb/mtau %.4f s23 %.5f s13 %.6f" % (tg.T[2], tg.T[5], tg.T[8], tg.T[5] / tg.T[8], tg.T[10], tg.T[11]))
    envs[f"{vR:.0e}"] = {"env": e, "T": tg.T.tolist(), "S": tg.S.tolist()}
out["envs"] = envs
json.dump(out, open("test_conventions.json", "w"), indent=1, default=str)
