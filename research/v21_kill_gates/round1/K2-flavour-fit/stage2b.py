"""Full top-down RG refinement of proxy solutions (one JSON result per input file).
usage: stage2b.py out.json [kappa_scale ymax vR_override] -- file1.json file2.json ...
"""
import json, sys, time, math, numpy as np, fit
args = sys.argv[1:]
out = args[0]
sep = args.index("--")
opts = args[1:sep]; files = args[sep + 1:]
kappa_scale = float(opts[0]) if len(opts) > 0 else 1.0
ymax = float(opts[1]) if len(opts) > 1 else 1.5
vR_override = float(opts[2]) if len(opts) > 2 and opts[2] != "-" else None
fit.KAPPA_R *= kappa_scale; fit.YMAX = ymax
inp = json.load(open("inputs_mz.json"))
res = []
t0 = time.time()
for f in files:
    w = json.load(open(f))
    content = w.get("content", "T2"); scheme = w.get("scheme", "floor1"); type2 = bool(w.get("type2", "II" in f))
    vR = vR_override or w.get("vR", 2.6e13 if content == "T2" else 3.08e13); MU = w.get("MU", 2.13e16 if content == "T2" else 3.05e16)
    R = fit.Runner(inp, vR, MU, content)
    T = fit.build_targets(inp, 0.01) if scheme == "floor1" else fit.build_targets(inp, 0.0, lepton_floor=0.001)
    P = fit.Proxy2(R, T, type2=type2)
    p0 = np.array(w["x"])
    r_before = P.residuals(p0, full=True, log_masses=False)
    chi2_before = float(np.sum(r_before[0][:18]**2))
    try:
        r = fit.fit_proxy(P, p0, full=True, max_nfev=3000, method="lm")
    except Exception as e:
        print("refine failed", f, repr(e), flush=True); continue
    # composition record
    Yu, Yd, Ye, Yn, MR, ML, Hm, F, rr, ss, cd126 = P.matrices(np.array(r["x"]))
    cd10, Y10, Y126 = P.composition(Hm, F, rr, ss, cd126)
    cu10 = rr * cd10; cu126 = rr * ss * cd126
    sv10 = np.linalg.svd(Y10 * fit.N10_ACT)[1]; sv126 = np.linalg.svd(Y126 * fit.N126_ACT)[1]
    MRe = np.linalg.svd(MR)[1]
    r.update({"file": f, "content": content, "scheme": scheme, "type2": type2, "vR": vR, "MU": MU, "kappa_scale": kappa_scale, "ymax": ymax,
              "chi2_full_before_refit": chi2_before, "stage1_chi2": w["chi2"],
              "composition": {"c_u10": [abs(cu10), float(np.angle(cu10))], "c_u126": [abs(cu126), float(np.angle(cu126))],
                              "c_d10": [cd10, 0.0], "c_d126": [cd126, 0.0], "sum_abs2": float(abs(cu10)**2 + abs(cu126)**2 + cd10**2 + cd126**2),
                              "tan_beta_like_|c_u|/|c_d|": float(math.sqrt(abs(cu10)**2 + abs(cu126)**2) / math.sqrt(cd10**2 + cd126**2)),
                              "r": [abs(rr), float(np.angle(rr))], "s": [abs(ss), float(np.angle(ss))]},
              "Y10_act_singular_values": sv10.tolist(), "Y126_act_singular_values": sv126.tolist(),
              "M_R_GeV": MRe.tolist(), "Y10_act_maxabs": float(np.abs(Y10 * fit.N10_ACT).max()), "Y126_act_maxabs": float(np.abs(Y126 * fit.N126_ACT).max()),
              "F_def": [[float(z.real), float(z.imag)] for z in F.ravel()], "Y10_def_diag_basis_note": "up-diagonal basis; Y10_def = (D_u/r - sF)/cd10"})
    if ML is not None:
        r["M_L_eV"] = (np.linalg.svd(ML)[1] * 1e9).tolist()
    res.append(r)
    print(f"{f}: stage1 chi2={w['chi2']:.2f} -> full(before refit)={chi2_before:.2f} -> refit chi2={r['chi2']:.3f} pen={r['penalty']:.2g} y10max={r['Y10_act_maxabs']:.3f} y126max={r['Y126_act_maxabs']:.3f} MR={np.array2string(MRe, precision=2)} t={time.time()-t0:.0f}s", flush=True)
    print("   pulls:", {k: round(v, 2) for k, v in r["pulls"].items()}, flush=True)
res.sort(key=lambda x: x["chi2"] + x["penalty"])
json.dump({"kappa_scale": kappa_scale, "ymax": ymax, "vR_override": vR_override, "results": res}, open(out, "w"), indent=1)
print("done; best", res[0]["chi2"] if res else None)
