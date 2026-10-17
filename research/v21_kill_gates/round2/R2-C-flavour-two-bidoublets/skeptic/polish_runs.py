"""Re-polish the researcher's best points in MY chain (+ basin hops), per v_R.
usage: polish_runs.py TAG KAPPA_LAM vR1,vR2,... NHOPS [floor] [fbound_factor] [th23sigma]"""
import sys, os, json, math, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import skchain as S, skopt as O

tag = sys.argv[1]; S.KAPPA_LAM = float(sys.argv[2]); vRs = [float(v) for v in sys.argv[3].split(",")]
nh = int(sys.argv[4]); floor = float(sys.argv[5]) if len(sys.argv) > 5 else 0.01
ffac = float(sys.argv[6]) if len(sys.argv) > 6 else 1.0
th23s = float(sys.argv[7]) if len(sys.argv) > 7 else None
pts = json.load(open(os.path.join(HERE, "their_points.json")))
d = S.dataset(floor, th23_sigma=th23s)
STEP = dict(h_g=0.5, h_hi=0.1, h_lo=0.5)
FINE = dict(h_g=0.1, h_hi=0.02, h_lo=0.1)
out = []
outf = os.path.join(HERE, f"polish_{tag}.json")
if os.path.exists(outf):
    out = json.load(open(outf))
done = {round(math.log10(e["vR"]), 4) for e in out}


def content_for(vR):
    return "C2" if vR < 5e10 else ("R813" if vR <= 2e12 else "R622")


rng = np.random.default_rng(12345)
for vR in vRs:
    if round(math.log10(vR), 4) in done:
        continue
    c = content_for(vR); MU = S.MU_NOMINAL[c]
    env = S.Env(vR, c, MU, d)
    m = S.Model(env, d, fbound=ffac * math.sqrt(4 * math.pi), **STEP)
    fit = O.Fit(m, "W")
    t0 = time.time()
    # starts: all of their points (any v_R), mapped to W-param; scan lc
    starts = []
    for p in pts:
        H, F, r, s, cd = S.unpack(np.array(p["P"])[None])
        X = O.gut_to_w(H, F, r, s, cd)[0]
        Z = np.tile(X, (41, 1)); Z[:, 18] = np.linspace(-4.0, -1.0, 41)
        cs = fit.chi2(Z)
        j = int(np.argmin(cs))
        starts.append((float(cs[j]), Z[j], p["tag"] + f"@{p['vR']:.0e}"))
    starts.sort(key=lambda t: t[0])
    res = []
    for c0, x0, src in starts[:6]:
        x, cx = fit.polish(x0, nfev=150)
        res.append((cx, x, src))
        print(f"  vR={vR:.1e} start {src}: {c0:.2f} -> {cx:.2f}  ({time.time()-t0:.0f}s)", flush=True)
    res.sort(key=lambda t: t[0])
    best = res[0]
    steps = np.full(19, 0.15); steps[9:15] = 0.03; steps[15] = 0.03; steps[16] = 0.05; steps[17] = 0.15; steps[18] = 0.1
    cur = best
    for k in range(nh):
        xk, ck = fit.polish(cur[1] + rng.normal(0, 1, 19) * steps, 120)
        print(f"    hop {k}: {ck:.2f} (cur {cur[0]:.2f})", flush=True)
        if ck < cur[0]:
            cur = (ck, xk, cur[2] + "+hop")
    best = cur
    # final polish at fine step and report
    mF = S.Model(env, d, fbound=ffac * math.sqrt(4 * math.pi), **FINE)
    fitF = O.Fit(mF, "W")
    xF, cF = fitF.polish(best[1], nfev=60)
    R = fitF.resid(xF[None])[0]
    o, ok, info = fitF.last
    pulls = {k: float(R[i]) for i, k in enumerate(S.KEYS)}
    H, F, r, s, cd = O.w_to_gut(xF[None])
    okc, cd10, cu10, cu126 = S.composition(r, s, cd)
    rec = dict(vR=vR, content=c, MU=MU, KAPPA_LAM=S.KAPPA_LAM, floor=floor, fbound=ffac * math.sqrt(4 * math.pi),
               chi2_std=best[0], chi2_fine=float(np.sum(R[:18]**2)), pen_fine=float(np.sum(R[18:]**2)), pulls=pulls,
               obs={k: float(o[0, i]) for i, k in enumerate(S.KEYS)}, x=xF.tolist(), src=best[2],
               r=float(r[0]), s=[float(s[0].real), float(s[0].imag)], cd126=float(cd[0]),
               comp=[float(cu10[0]), float(abs(cu126[0])), float(cd10[0]), float(cd[0])],
               fmax=float(max(info["fU"][0], info["fR"][0])), y126max=float(max(info["y126U"][0], info["y126R"][0])),
               y10max=float(max(info["y10U"][0], info["y10R"][0])), MR=info["MR"][0].tolist(),
               mnu=info["mn"][0].tolist(), start_chi2s=[t[0] for t in res], t=time.time() - t0)
    out.append(rec)
    print(f"vR={vR:.1e} {c} BEST chi2(std)={best[0]:.2f} fine={rec['chi2_fine']:.2f} pen={rec['pen_fine']:.2g} "
          f"th23={o[0,14]:.4f} fmax={rec['fmax']:.3f} r={rec['r']:.1f} |s|={abs(complex(*rec['s'])):.3f} t={rec['t']:.0f}s", flush=True)
    print("    pulls:", " ".join(f"{k}={pulls[k]:+.2f}" for k in S.KEYS), flush=True)
    json.dump(out, open(outf, "w"), indent=1)
