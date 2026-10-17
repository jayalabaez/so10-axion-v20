import time, json, math, numpy as np
import lib_r2c as L, model_r2c as M, bexact as B, mapping
L.USE_RK4 = True; L.RK4_H = 0.5
d = L.data_set("nufit60_sk", 0.01)
setup = M.make_setup(3e13, d); tg = setup["targets"]
J = json.load(open("campaign_main_3e+13_I.json"))
lay = M.Layout(free=True)
Ex = B.Exact(setup, tg)
rng = np.random.default_rng(0)
Zs = []
for m in J["distinct_minima"][:4]:
    mp = mapping.proxy_to_exact(setup, tg, np.array(m["x"]), iters=12)
    z = np.concatenate([mp["x"], [mp["lc"]]])
    Zs.append(z)
    for k in range(2):
        Zs.append(z + rng.normal(0, 0.003, len(z)))
Zs = np.array(Zs)
t0 = time.time(); R = Ex.resid(Zs); tb = time.time() - t0
cb = np.sum(R**2, 1)
for i, z in enumerate(Zs):
    o = M.top_down(z[:-1], lay, setup, tg, z[-1])
    r, _ = M.td_residuals(o, d)
    if o["dm31"] <= 0: r = r + 1e3
    cs = float(np.sum(r**2))
    print(f"pt {i}: scalar chi2 {cs:.4f}  batched {cb[i]:.4f}  max|dR| {np.max(np.abs(r - R[i])):.2e}")
print(f"batched time for N={len(Zs)}: {tb:.2f}s")
for N in (20, 100, 300):
    Z = np.repeat(Zs[:1], N, 0) + rng.normal(0, 0.002, (N, Zs.shape[1]))
    t0 = time.time(); Ex.chi2(Z); dt = time.time() - t0
    print(f"N={N}: {dt:.2f}s  ({dt/N*1e3:.2f} ms/pt)")
# step-size check
Ex2 = B.Exact(setup, tg, h_g=0.25, h_sm=0.5)
R2 = Ex2.resid(Zs[:4])
print("h halving: max |dR| =", np.max(np.abs(R2 - R[:4])))
