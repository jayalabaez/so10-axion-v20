"""R2-A: real-bidoublet structure of a light doublet space L (lowest nl eigenvectors of the (1,2)_{1/2} block).

A state inside ONE real G3221 bidoublet has |r| = 1 and s = 1 (neutral components (z1 xi, z1 xibar, z2 xi, z2 xibar)).
For nl = 2 the M_U-level light space should be R(z) + R(z'); we locate the real-bidoublet states in L by minimising
(log|r|)^2 + |s - 1|^2, read off the compositions zeta = z2/z1 (126bar/10 ratio, complex) and report the split
|zeta - zeta'| / |zeta| (0 for an X-symmetric complex bidoublet Phi_L = alpha Phi10 + beta Phi126 -> s = 1 on all of L).
usage: python -B r2_split.py <tag> <solution npz> [nl]
"""
import sys, math, json
import numpy as np
from scipy.optimize import minimize
import k3_common as K
import r2_compose as RC

tag, solp = sys.argv[1], sys.argv[2]; nl = int(sys.argv[3]) if len(sys.argv) > 3 else 2
B = np.load(K.SCRATCH / f"{tag}_blocks.npz"); labels = [str(x) for x in B["labels"]]; kd = labels.index("(1,2)_|Y|=1/2")
c = np.load(K.SCRATCH / solp)["c"]; Ac = np.einsum("p,pij->ij", c, B[f"A{kd}"]); w, V = np.linalg.eigh(0.5 * (Ac + Ac.conj().T))
L = V[:, :nl]; nt = RC.Neutral(tag); rng = np.random.default_rng(2)


def f(x):
    a = L @ (x[:nl] + 1j * x[nl:]); cm = nt.comp_of_a(a)
    if abs(cm["vu"]) < 1e-12 or abs(cm["vd"]) < 1e-12 or abs(cm["wd"]) < 1e-12: return 10.0
    r, s = cm["r"], cm["s"]; return math.log(abs(r)) ** 2 + abs(s - 1) ** 2


sols = []
for k in range(80):
    res = minimize(f, rng.normal(size=2 * nl), method="Nelder-Mead", options={"maxiter": 5000, "xatol": 1e-12, "fatol": 1e-16})
    a = L @ (res.x[:nl] + 1j * res.x[nl:]); a /= np.linalg.norm(a); cm = nt.comp_of_a(a)
    zeta = (cm["wu"] / cm["vu"]) if abs(cm["vu"]) > 1e-12 else np.inf
    sols.append((res.fun, a, zeta, cm))
sols.sort(key=lambda t: t[0])
# distinct minima (by overlap)
picked = []
for fval, a, zeta, cm in sols:
    if all(abs(np.vdot(a, b)) < 0.9 for _, b, _, _ in picked): picked.append((fval, a, zeta, cm))
    if len(picked) >= nl: break
out = {"tag": tag, "sol": solp, "light_eigs": w[:nl].tolist(), "real_bidoublet_states": []}
for fval, a, zeta, cm in picked:
    out["real_bidoublet_states"].append({"residual": float(fval), "zeta=z126/z10": [float(np.real(zeta)), float(np.imag(zeta))], "|zeta|": float(abs(zeta)),
                                         "arg_zeta_deg": float(np.degrees(np.angle(zeta))), "frac": cm["frac"]})
    print(f"real-bidoublet state: residual {fval:.2e}  zeta = {zeta:.5g} (|zeta| {abs(zeta):.4g}, arg {np.degrees(np.angle(zeta)):.2f} deg)  Sigma frac {cm['frac']['Sigma126bar']:.4f}  overlap with others {[round(abs(np.vdot(a, b)), 3) for _, b, _, _ in picked]}")
if len(picked) >= 2:
    z1, z2 = picked[0][2], picked[1][2]; split = abs(z1 - z2) / max(abs(z1), 1e-30)
    out["split"] = float(split); print(f"composition split |zeta - zeta'|/|zeta| = {split:.4g}")
json.dump(out, open(K.SCRATCH / (solp.replace('.npz', '') + "_split.json"), "w"), indent=1, default=float)
