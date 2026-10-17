"""Robustness re-fits from my best K2 points.
usage: refit.py TAG vR1,vR2 OPTS   with OPTS a comma list of key=value:
   floor=0.03  nuis=3 nsig=0.01  th23s=10  ffac=2  K=2  loop=1  hops=6  src=polish_K2.json"""
import sys, os, json, math, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import skchain as S, skopt as O

tag = sys.argv[1]; vRs = [float(v) for v in sys.argv[2].split(",")]
opt = dict(kv.split("=") for kv in sys.argv[3].split(",")) if len(sys.argv) > 3 and sys.argv[3] else {}
floor = float(opt.get("floor", 0.01)); nuis = int(opt.get("nuis", 0)); nsig = float(opt.get("nsig", 0.01))
th23s = float(opt["th23s"]) if "th23s" in opt else None; ffac = float(opt.get("ffac", 1.0))
S.KAPPA_LAM = float(opt.get("K", 2.0)); S.EXTRA_T10 = float(opt.get("xT", 0.0)); two_loop = opt.get("loop", "2") == "2"; hops = int(opt.get("hops", 6))
srcs = opt.get("src", "polish_K2.json").split("+")
starts_all = []
for sf in srcs:
    for e in json.load(open(os.path.join(HERE, sf))):
        x = e.get("x")
        if x is not None:
            starts_all.append((e["vR"], np.array(x[:19]), sf))
d = S.dataset(floor, th23_sigma=th23s)
if opt.get("lit") or opt.get("nu"):
    ex = json.load(open(os.path.join(HERE, "their_extra.json")))
    lit = ex[0]["data"]                     # researcher's 'literature-era' data dict (2018 errors, NuFIT 3.2)
    if opt.get("lit") == "1":               # literature-era quark/lepton/CKM errors (central values unchanged)
        for k in S.MASS_KEYS + ["s12", "s23", "s13", "delta"]:
            d[k] = (d[k][0], lit[k][1] / lit[k][0] * d[k][0])
    if opt.get("nu") == "nufit32":
        for k in ["sin2_th12", "sin2_th23", "sin2_th13", "dm21", "dm31"]:
            d[k] = tuple(lit[k])
if opt.get("xfl"):                          # extra relative floor on selected masses, e.g. xfl=m_d:0.10;m_s:0.10
    for item in opt["xfl"].split(";"):
        k, v = item.split(":"); v = float(v)
        c0, s0 = d[k]
        d[k] = (c0, c0 * ((s0 / c0)**2 + v**2)**0.5)
print("data used:", {k: (round(v[0], 6), round(v[1] / v[0], 4)) for k, v in d.items()}, flush=True)
out = []
outf = os.path.join(HERE, f"refit_{tag}.json")
rng = np.random.default_rng(99)
for vR in vRs:
    c = "C2" if vR < 5e10 else ("R813" if vR <= 2e12 else "R622"); MU = S.MU_NOMINAL[c]
    env = S.Env(vR, c, MU, d)
    m = S.Model(env, d, fbound=ffac * math.sqrt(4 * math.pi), h_g=0.5, h_hi=0.1, h_lo=0.5, two_loop=two_loop)
    fit = O.Fit(m, "W"); fit.nuis = nuis; fit.nuis_sigma = nsig
    t0 = time.time()
    # starts: the best points of the sources at the two nearest v_R
    st = sorted(starts_all, key=lambda t: abs(math.log(t[0] / vR)))[:int(opt.get("nst", 3))]
    res = []
    for vs, x0, sf in st:
        x0 = np.concatenate([x0, np.zeros(nuis)])
        Z = np.tile(x0, (41, 1)); Z[:, 18] = x0[18] + np.linspace(-0.6, 0.6, 41)
        cs = fit.chi2(Z); j = int(np.argmin(cs))
        x, cx = fit.polish(Z[j], nfev=200)
        res.append((cx, x, f"{sf}@{vs:.0e}"))
        print(f"  vR={vR:.1e} start {sf}@{vs:.0e}: {cs[j]:.2f} -> {cx:.2f} ({time.time()-t0:.0f}s)", flush=True)
    res.sort(key=lambda t: t[0])
    cur = res[0]
    n = 19 + nuis
    steps = np.full(n, 0.12); steps[9:15] = 0.025; steps[15] = 0.025; steps[16] = 0.04; steps[17] = 0.12; steps[18] = 0.08
    if nuis:
        steps[19:] = nsig
    for k in range(hops):
        xk, ck = fit.polish(cur[1] + rng.normal(0, 1, n) * steps, 120)
        print(f"    hop {k}: {ck:.2f} (cur {cur[0]:.2f})", flush=True)
        if ck < cur[0]:
            cur = (ck, xk, cur[2] + "+hop")
    R = fit.resid(cur[1][None])[0]
    o = fit.last[0][0]
    pulls = {k: float(R[i]) for i, k in enumerate(S.KEYS)}
    rec = dict(vR=vR, content=c, opts=opt, chi2_total=cur[0], chi2_obs=float(np.sum(R[:18]**2)),
               chi2_nuis=float(np.sum(R[21:]**2)) if nuis else 0.0, pen=float(np.sum(R[18:21]**2)), pulls=pulls,
               obs={k: float(o[i]) for i, k in enumerate(S.KEYS)}, x=cur[1].tolist(), t=time.time() - t0)
    out.append(rec)
    print(f"vR={vR:.1e} {c} BEST total={cur[0]:.2f} obs={rec['chi2_obs']:.2f} nuis={rec['chi2_nuis']:.2f} pen={rec['pen']:.2g} "
          f"th23={o[14]:.4f}" + (f" eps={np.round(cur[1][19:], 4).tolist()}" if nuis else ""), flush=True)
    print("    pulls:", " ".join(f"{k}={pulls[k]:+.2f}" for k in S.KEYS), flush=True)
    json.dump(out, open(outf, "w"), indent=1)
