"""Localise the neutrino-observable difference between my chain and the researcher's scalar DOP853 chain."""
import sys, os, json, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "theirs")); os.chdir(os.path.join(HERE, "theirs"))
import lib_r2c as L, model_r2c as M
sys.path.insert(0, HERE)
import skchain as S

pts = json.load(open(os.path.join(HERE, "their_points.json")))
p = [q for q in pts if q["tag"] == "vscan_fine" and abs(q["vR"] - 3e12) < 1][0]
vR, c, MU = p["vR"], p["content"], p["MU"]
d = L.data_set("nufit60_sk", 0.01)
setup = M.make_setup(vR, d, content=c, MU=MU); tg = setup["targets"]
lay = M.Layout(typeII=False, free=True)
z = np.array(p["z"])
o_th = M.top_down(z[:-1], lay, setup, tg, z[-1], rtol=1e-9)
keys = S.KEYS
print("theirs DOP853 :", " ".join(f"{k}={o_th[k]:.6g}" for k in keys[9:]))
dd = S.dataset(0.01)
for lam_coef in (2.0, 1.0):
    for lam0 in (0.27, 0.26):
        S.KAPPA_LAM = lam_coef
        env = S.Env(vR, c, MU, dd, lam0=lam0)
        m = S.Model(env, dd, h_g=0.1, h_hi=0.01, h_lo=0.1)
        R = m.resid(np.array(p["P"])[None])[0]
        o = m.last[0][0]
        print(f"mine KAPPA_LAM={lam_coef} lam0={lam0}:", " ".join(f"{k}={o[i]:.6g}" for i, k in enumerate(keys) if i >= 9),
              f"chi2={np.sum(R[:18]**2):.2f}")
S.KAPPA_LAM = 2.0
# their SM-only run from v_R with seesaw versus mine starting from IDENTICAL v_R inputs (their G3221 output)
G = M.gut_matrices(np.atleast_2d(z[:-1]), lay, tg.sd0, tg.se0)
Hm, F = G["H"][0], G["F"][0]; r = float(G["r"][0]); s = complex(G["s"][0]); cd126 = 10**z[-1]
comp = M.composition(r, s, cd126)
Y10 = Hm / comp["c_d10"]; Y126 = F / cd126
env_t = setup["env"]
g, Yq, Yl, fhR = L.run_g3221(np.array(env_t["g_MU"]), [Y10, Y126], [Y10, -3 * Y126], L.C_R * Y126, env_t["MU"], vR,
                             env_t["b_lo"], env_t["b_hi"], rtol=1e-10)
# mine G3221 from the same GUT inputs
envm = S.Env(vR, c, MU, dd)
st = S.run_g3221([Y10[None], Y126[None], Y10[None], -3 * Y126[None], L.C_R * Y126[None]], envm, h=0.05)
for nm, a, b in [("Yq10", Yq[0], st[0][0]), ("Yq126", Yq[1], st[1][0]), ("Yl10", Yl[0], st[2][0]), ("Yl126", Yl[1], st[3][0]), ("f", fhR, st[4][0])]:
    print(f"G3221 {nm}: max|diff|/max = {np.abs(a - b).max() / np.abs(a).max():.2e}")
print("gauge at MU theirs (g3,gL,gR,gBL):", env_t["g_MU"], " mine:", np.sqrt(4 * math.pi / envm.ainv_MU))
# SM part: same v_R inputs into both SM runners
cu10, cu126, cd10 = comp["c_u10"], comp["c_u126"], comp["c_d10"]
Yu = cu10 * Yq[0] + cu126 * Yq[1]; Yd = cd10 * Yq[0] + cd126 * Yq[1]; Ye = cd10 * Yl[0] + cd126 * Yl[1]; Yn = cu10 * Yl[0] + cu126 * Yl[1]
MR = vR * fhR
stt = L.SMState(env_t["g_sm_vR"], env_t["lam_vR"], Yu, Yd, Ye, np.zeros((3, 3), complex), Yn, MR)
stt = L.run_sm_with_seesaw(stt, vR, L.MZ, db_func=L.db_sm, rtol=1e-10, thresholds_extra=(L.M_S,))
ot = L.observables(stt.Yu, stt.Yd, stt.Ye, stt.kappa * L.VEV**2)
print("their SM part  :", " ".join(f"{k}={ot[k]:.6g}" for k in keys[9:]))
for lam_coef in (2.0, 1.0):
    S.KAPPA_LAM = lam_coef
    st2 = [np.array(env_t["g_sm_vR"])[None], np.array([env_t["lam_vR"]]), Yu.T[None], Yd.T[None], Ye.T[None], np.zeros((1, 3, 3), complex),
           Yn.T[None], MR[None]]
    st2 = S.run_sm_seesaw(st2, vR, h_hi=0.005, h_lo=0.05)
    om, _ = S.observables(np.swapaxes(st2[2], 1, 2), np.swapaxes(st2[3], 1, 2), np.swapaxes(st2[4], 1, 2), st2[5] * S.VEV**2)
    print(f"my SM part K={lam_coef}:", " ".join(f"{k}={om[0, i]:.6g}" for i, k in enumerate(keys) if i >= 9))
S.KAPPA_LAM = 2.0
