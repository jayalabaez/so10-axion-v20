"""Monte-Carlo basin hopping with LM polish on the 12-parameter pinned proxy (T3 targets), seeded from json records and,
optionally, from the researcher's best point translated into the d-diagonal W-parametrisation.
usage: hop.py content seed nhops maxminutes in1.json [in2.json ...] [--researcher]
"""
import sys, os, json, math, time
import numpy as np
import k2v

args = [a for a in sys.argv[1:] if not a.startswith("--")]
use_res = "--researcher" in sys.argv
content, seed, nhops, maxmin = args[0], int(args[1]), int(args[2]), float(args[3]); files = args[4:]
vR, MU = (2.6e13, 2.13e16) if content == "T2" else (3.08e13, 3.05e16)
T, info, _ = k2v.build_targets(vR, MU, content)
M = k2v.Model(T, info["rnu"])
rng = np.random.default_rng(seed)
HERE = os.path.dirname(os.path.abspath(__file__))

def takagi(S):
    U, s, Vh = np.linalg.svd(S)
    D = U.conj().T @ S @ U.conj()
    ph = np.exp(1j * np.angle(np.diag(D)) / 2)
    U2 = U @ np.diag(ph)
    s2 = np.abs(np.diag(U2.conj().T @ S @ U2.conj()))
    order = np.argsort(s2)
    return U2[:, order], s2[order]

def params_from_W(W, r, s):
    """invert unitary(p): W = diag(e^{ia1}, e^{ia2}, 1) V(th12, th13, th23, d) diag(e^{ib})"""
    # strip right phases so that row 3 of V is in standard form: V = diag(e^{-ia}) W diag(e^{-ib}); fit by least squares
    from scipy.optimize import least_squares
    def res(p):
        Wp = k2v.unitary(p)
        return np.concatenate([(Wp - W).real.ravel(), (Wp - W).imag.ravel()])
    best = None
    for k in range(40):
        p0 = np.concatenate([np.arcsin(np.sqrt(rng.uniform(0, 1, 3))), rng.uniform(-math.pi, math.pi, 6)])
        try:
            rr = least_squares(res, p0, method="lm", xtol=1e-14, ftol=1e-14, gtol=1e-14)
        except Exception:
            continue
        if best is None or rr.cost < best.cost:
            best = rr
        if best.cost < 1e-20:
            break
    p = np.zeros(12); p[0:9] = best.x; p[9] = math.log10(r); p[10] = math.log10(abs(s)); p[11] = np.angle(s)
    return p, float(best.cost)

seeds = []
for f in files:
    w = json.load(open(f))
    for rec in w.get("records", [w])[:5]:
        x = np.array(rec["x"])[:12]
        seeds.append((x, M.chi2(x), os.path.basename(f) + ":" + rec.get("label", "")))
if use_res:
    sys.path.insert(0, os.path.join(HERE, "res"))
    import fit as rfit
    inp = json.load(open(os.path.join(HERE, "res", "inputs_mz.json")))
    R = rfit.Runner(inp, 2.6e13, 2.13e16, "T2"); TT = rfit.build_targets(inp, 0.01)
    P = rfit.Proxy2(R, TT, type2=False)
    w = json.load(open(os.path.join(HERE, "res", "de_I_0.json"))); x = np.array(w["x"])
    Yu, Yd, Ye, Yn, MR, ML, Hm, F, r, s, cd126 = P.matrices(x)
    Ud, dd = takagi(Yd)                      # Yd = Ud diag Ud^T  ->  basis change 16 -> Ud^* 16: Yd' = Ud^dag Yd Ud^* = D_d
    Yep = Ud.conj().T @ Ye @ Ud.conj()
    W, ee = takagi(Yep)
    # r phase is redundant (absorbed in F); use |r| and s as they are (same definitions H, F, Yu = r(H+sF))
    p, cost = params_from_W(W, abs(r), s)
    print("researcher point translated: W-fit cost", cost, "chi2 in my proxy =", M.chi2(p), flush=True)
    seeds.append((p, M.chi2(p), "researcher"))
seeds.sort(key=lambda z: z[1])
print("seeds:", [(lab, round(c, 1)) for _, c, lab in seeds], flush=True)

t0 = time.time()
gbest = None; recs = []
cur_x, cur_c = seeds[0][0].copy(), seeds[0][1]
Tmc = 3.0
steps = [0.02, 0.05, 0.15, 0.4]
for h in range(nhops):
    if (time.time() - t0) / 60 > maxmin:
        break
    if h % 60 == 59 and len(seeds) > 1:     # restart from another seed occasionally
        k = rng.integers(len(seeds)); cur_x, cur_c = seeds[k][0].copy(), seeds[k][1]
    st = steps[rng.integers(len(steps))]
    mask = rng.uniform(size=12) < rng.uniform(0.2, 1.0)
    p = cur_x + st * rng.normal(size=12) * mask
    try:
        x, c2, nf = k2v.lm_fit(M, p, max_nfev=1500)
    except Exception:
        continue
    if c2 < cur_c or rng.uniform() < math.exp(-(c2 - cur_c) / Tmc):
        cur_x, cur_c = x, c2
    if gbest is None or c2 < gbest[1]:
        gbest = (x, c2)
        print(f"hop {h}: new best chi2={c2:.3f} (step {st}) t={time.time()-t0:.0f}s", flush=True)
        if c2 < 100:
            recs.append(k2v.result_record(M, x, vR, f"hop{h}"))
recs.sort(key=lambda r: r["chi2_18"])
out = os.path.join(HERE, f"hop_{content}_{seed}.json")
json.dump({"content": content, "vR": vR, "MU": MU, "seed": seed, "best_chi2": gbest[1] if gbest else None, "records": recs[:10], "info": info},
          open(out, "w"), indent=1)
if gbest:
    rec = k2v.result_record(M, gbest[0], vR, "best")
    print("BEST chi2_18 =", round(rec["chi2_18"], 4), "max|pull| =", round(rec["max_abs_pull"], 3))
    print("pulls:", {k: round(v, 2) for k, v in rec["pulls"].items()})
    print("comp:", {k: (round(v, 5) if isinstance(v, float) else v) for k, v in rec["comp"].items()})
