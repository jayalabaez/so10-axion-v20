"""v2 setup test: environments per v_R (content, M_U from R2-B), proxy chi2 at the first-attempt best points,
batched exact chain timing and perturbativity penalty."""
import json, math, time, os, sys
import numpy as np
import lib_r2c as L, model_r2c as M, bexact as B

L.USE_RK4 = True
ASSIGN = {2e10: "C2", 1e11: "R813", 1e12: "R813", 3e12: "R622", 1e13: "R622", 3e13: "R622", 1e14: "R622"}
d = L.data_set("nufit60_sk", 0.01)
old = os.path.join("..", "src", "campaign_main_3e+13_I.json")
J = json.load(open(old))
x0 = np.array(J["distinct_minima"][0]["x"])
for vR, c in ASSIGN.items():
    MU = L.R2B_NOMINAL[c][1]
    st = M.make_setup(vR, d, content=c, MU=MU)
    env = st["env"]; tg = st["targets"]
    lay = M.Layout()
    R, chi2 = M.proxy_eval(x0[None], lay, tg)
    print(f"vR={vR:.0e} {c:5s} MU={MU:.2e} gBL:{env['gBL_status']:8s} a^-1(vR)={np.round(env['alpha_inv_vR'],2).tolist()} "
          f"a^-1(MU)={np.round(env['alpha_inv_MU'],2).tolist()} eta={ {k: round(v,4) for k,v in tg.info['eta'].items()} } "
          f"mb/mtau(MU)={tg.T[5]/tg.T[8]:.4f} proxy chi2(old 3e13 best)={chi2[0]:.1f}", flush=True)
# exact timing at 1e13
vR = 1e13; c = "R622"
st = M.make_setup(vR, d, content=c, MU=L.R2B_NOMINAL[c][1]); tg = st["targets"]
Ex = B.Exact(st, tg, False, d)
z = np.concatenate([x0, np.zeros(6), [-1.5]])
Z = np.tile(z, (200, 1)); Z[:, -1] = np.linspace(-4.5, -1.0, 200)
t0 = time.time(); R = Ex.resid(Z); t1 = time.time()
c2 = np.sum(R**2, 1)
i = int(np.argmin(c2))
print(f"exact N=200: {t1-t0:.2f}s; best lc={Z[i,-1]:.3f} chi2={c2[i]:.1f}; ymax at best {Ex.last_ymax[i]}; pert-res {R[i,18:]}")
print("ymax range over lc:", Ex.last_ymax[[0, 50, 100, 150, 199]].round(4).tolist())
