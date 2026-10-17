"""R2-A: compositions of the light (1,2)_{1/2} doublets of a coupling point and the realisable (|r|, s) range.

usage: python -B r2_light_comp.py <tag> <solution npz (c)> [n_light] [--target_r 66 --target_s 0.43,0.0]
For the light subspace L (lowest n_light eigenvectors of the (1,2)_{1/2} block of the Hessian at c) it reports each
eigenvector's composition, samples h in L (EW vev direction, chosen by the EW-scale tuning inside L) and maps the
realisable (|r|, s); with a target it minimises | log|r|/|r*| |^2 + |s - s*|^2 over h in L.
"""
from __future__ import annotations
import sys, json, math, argparse
import numpy as np
from scipy.optimize import minimize
import k3_common as K
import r2_compose as RC

ap = argparse.ArgumentParser(); ap.add_argument("tag"); ap.add_argument("sol"); ap.add_argument("nl", type=int, nargs="?", default=None)
ap.add_argument("--target_r", type=float, default=66.0); ap.add_argument("--target_s", default="0.43,0.0")
ap.add_argument("--out", default=None); ap.add_argument("--nsample", type=int, default=4000)
args = ap.parse_args()
B = np.load(K.SCRATCH / f"{args.tag}_blocks.npz"); labels = [str(x) for x in B["labels"]]
kd = labels.index("(1,2)_|Y|=1/2"); A = B[f"A{kd}"]
sol = np.load(K.SCRATCH / args.sol); c = sol["c"]
Ac = np.einsum("p,pij->ij", c, A); Ac = 0.5 * (Ac + Ac.conj().T)
w, V = np.linalg.eigh(Ac)
nl = args.nl if args.nl is not None else int(np.sum(w < 1e-4))
nt = RC.Neutral(args.tag)
rep = {"tag": args.tag, "sol": args.sol, "eigenvalues": w.tolist(), "n_light": nl, "eigvecs": []}
print(f"(1,2)_1/2 block eigenvalues: {np.array2string(w, precision=4)}; light = {nl}")
for j in range(5):
    cmp_ = nt.comp_of_a(V[:, j])
    e = {"j": j, "eig": float(w[j]), "frac": cmp_["frac"], "|vu|": abs(cmp_["vu"]), "|vd|": abs(cmp_["vd"]), "|wu|": abs(cmp_["wu"]), "|wd|": abs(cmp_["wd"]),
         "|r|": float(abs(cmp_["r"])) if np.isfinite(abs(cmp_["r"])) else None, "s": [float(np.real(cmp_["s"])), float(np.imag(cmp_["s"]))] if np.isfinite(cmp_["s"]) else None}
    rep["eigvecs"].append(e)
    print(f"  ev{j} m2={w[j]:.4g} frac H10 {cmp_['frac']['H10']:.3f} Sig {cmp_['frac']['Sigma126bar']:.3f} Phi {cmp_['frac']['Phi210']:.3f} |r|={e['|r|']} s={e['s']}")
L = V[:, :nl]
rng = np.random.default_rng(5)
samples = []
for _ in range(args.nsample):
    x = rng.normal(size=nl) + 1j * rng.normal(size=nl); a = L @ x
    cm = nt.comp_of_a(a); r, s = cm["r"], cm["s"]
    if np.isfinite(abs(r)) and np.isfinite(s): samples.append((abs(r), s, cm["frac"]["Sigma126bar"]))
if samples:
    ar = np.array([x[0] for x in samples]); ss = np.array([x[1] for x in samples]); fs = np.array([x[2] for x in samples])
    d1s = np.abs(1 - ss)
    rep["sample"] = {"n": len(samples), "|1-s| quantiles (0,5,50,95,100%)": np.quantile(d1s, [0, .05, .5, .95, 1]).tolist(),
                     "|r| quantiles": np.quantile(ar, [0, .05, .5, .95, 1]).tolist(), "Sigma fraction quantiles": np.quantile(fs, [0, .05, .5, .95, 1]).tolist()}
    print("  sampled |1-s| quantiles", np.round(rep["sample"]["|1-s| quantiles (0,5,50,95,100%)"], 6).tolist(), " |r| quantiles", np.round(rep["sample"]["|r| quantiles"], 3).tolist())
ts = complex(*[float(x) for x in args.target_s.split(",")]); tr = args.target_r


def loss(x):
    a = L @ (x[:nl] + 1j * x[nl:]); cm = nt.comp_of_a(a); r, s = cm["r"], cm["s"]
    if not (np.isfinite(abs(r)) and np.isfinite(s)): return 1e6
    return (math.log(abs(r) / tr)) ** 2 + abs(s - ts) ** 2


best = None
for k in range(60):
    x0 = rng.normal(size=2 * nl)
    res = minimize(loss, x0, method="Nelder-Mead", options={"maxiter": 4000, "xatol": 1e-10, "fatol": 1e-14})
    if best is None or res.fun < best.fun: best = res
a = L @ (best.x[:nl] + 1j * best.x[nl:]); cm = nt.comp_of_a(a)
rep["target"] = {"r*": tr, "s*": [ts.real, ts.imag], "loss": float(best.fun), "|r|": float(abs(cm["r"])), "s": [float(np.real(cm["s"])), float(np.imag(cm["s"]))],
                 "frac": cm["frac"], "a": [[float(np.real(z)), float(np.imag(z))] for z in a / np.linalg.norm(a)],
                 "|vu|,|vd|,|wu|,|wd|": [abs(cm["vu"]), abs(cm["vd"]), abs(cm["wu"]), abs(cm["wd"])]}
print(f"  target |r|={tr}, s={ts}: best loss {best.fun:.3e} -> |r| = {abs(cm['r']):.4g}, s = {cm['s']:.4g}, fractions {{H10: {cm['frac']['H10']:.3f}, Sigma: {cm['frac']['Sigma126bar']:.3f}, Phi: {cm['frac']['Phi210']:.4f}}}")
out = args.out or (args.sol.replace(".npz", "") + "_comp.json")
json.dump(rep, open(K.SCRATCH / out, "w"), indent=1, default=float)
print("saved", out)
