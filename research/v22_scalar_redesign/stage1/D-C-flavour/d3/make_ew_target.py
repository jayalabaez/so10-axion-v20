"""Build the EW-target doublet vector a (slice coordinates of the (1,2)_|Y|=1/2 block) realising the flavour-fit
composition: |r| = v_u/v_d = 65.3, s = (w_u/w_d)/(v_u/v_d) = rho/r = 0.459 (rho = 30), with the up-type 126bar fraction
|c_u126|^2 = F_U (default 0.9, the fit's c_d126 = 0.98 c_max; 0.5 variant) and no phi admixture.
Uses r2_compose.Neutral (R2-A, exact map) on the X-diagonal basis of the H10 and Sigma pairs.
usage: python -B make_ew_target.py <tag> <F_U> <out.npz>"""
import sys, json, math
import numpy as np
from scipy.optimize import least_squares
import k3_common as K
import r2_compose as RC

tag, FU, outn = sys.argv[1], float(sys.argv[2]), sys.argv[3]
R_T, S_T = 65.3, 0.459
B = np.load(K.SCRATCH / f"{tag}_blocks.npz"); labels = [str(x) for x in B["labels"]]
kd = labels.index("(1,2)_|Y|=1/2"); W = B[f"W{kd}"]
meta = json.load(open(K.SCRATCH / f"{tag}_blocks.json", encoding="utf-8"))["blocks"][kd]["meta"]
Xop = np.zeros((K.TOTAL, K.TOTAL))
for name, sl in K.BLOCKS.items():
    ch = {"Phi210": 0, "H10": -2, "Sigma126bar": -2, "S": 4, "Phi17": 17}[name]
    if ch == 0: continue
    idx = np.arange(sl.start, sl.stop)
    for i in range(0, len(idx), 2):
        Xop[idx[i], idx[i + 1]] = -ch; Xop[idx[i + 1], idx[i]] = ch
m = W.shape[1]; Rm = np.eye(m, dtype=complex); lab = {}
for blk, (ln, lp) in (("H10", ("Hu", "Hd*")), ("Sigma126bar", ("Du", "Dd*"))):
    js = [j for j, c in enumerate(meta) if c["block"] == blk]
    Xs = W[:, js].conj().T @ (1j * Xop) @ W[:, js]; Xs = 0.5 * (Xs + Xs.conj().T)
    w, v = np.linalg.eigh(Xs); Rm[np.ix_(js, js)] = v; lab[ln] = js[0]; lab[lp] = js[1]
lab["phi"] = [j for j, c in enumerate(meta) if c["block"] == "Phi210"][0]
nt = RC.Neutral(tag)
cu10 = math.sqrt(max(1 - FU - 1e-6, 1e-6))

def a_of(z):
    aX = np.zeros(m, complex)
    aX[lab["Hu"]] = cu10; aX[lab["Du"]] = math.sqrt(FU)
    aX[lab["Hd*"]] = z[0] * np.exp(1j * z[1]); aX[lab["Dd*"]] = z[2] * np.exp(1j * z[3])
    a = Rm @ aX
    return a / np.linalg.norm(a)

def res(z):
    c = nt.comp_of_a(a_of(z)); r, s = c["r"], c["s"]
    return [math.log(abs(r) / R_T), (s.real - S_T), s.imag]

best = None
for z0 in ([0.005, 0.0, 0.03, 0.0], [0.005, 3.14, 0.03, 0.0], [0.005, 0.0, 0.03, 3.14], [0.005, 1.5, 0.03, -1.5]):
    sol = least_squares(res, z0, xtol=1e-14, ftol=1e-14)
    if best is None or np.sum(np.square(sol.fun)) < np.sum(np.square(best.fun)): best = sol
a = a_of(best.x); c = nt.comp_of_a(a)
np.savez(K.SCRATCH / outn, a=a)
print(f"{outn}: |r| = {abs(c['r']):.4f}, s = {c['s']:.5f}, frac = { {k: round(v, 5) for k, v in c['frac'].items() if v > 1e-9} }, "
      f"slice |a|^2 = {np.round(np.abs(a) ** 2, 5)}, residual {np.sum(np.square(best.fun)):.2e}")
