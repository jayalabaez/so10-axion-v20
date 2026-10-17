"""R2-A (2): EW (SM-Higgs) direction targets a* in the (1,2)_{1/2} slice for prescribed 10+126bar fit parameters.

Exact map (r2_compose.py, SO(4) covariance; Clebsches of the 10 and of the 126bar colour-singlet (15,2,2) doublets are
u/d symmetric, the SU(4) factor 1 (quarks) / -3 (leptons) is common to u and d):
   M_d = H + F,  M_u = r (H + s F),  M_e = H - 3F,  M_nuD = r (H - 3 s F),
   r = v_u/v_d,  s = (w_u/w_d)/(v_u/v_d),  H = Y10 v_d,  F = Y126 w_d  (v: 10, w: 126bar (15,2,2) neutral components
   of the light SM Higgs).  Under a -> e^{i phi} a:  r -> e^{-2 i phi} r (unphysical), s invariant.
   The free complex ratio zeta = w_d/v_d is absorbed into F (it only sets |Y126|/|Y10|); it is fixed here through the
   126bar fraction f_Sigma of the light doublet (chart norm).
The map a (slots 1..4 = H10, H10, Sigma, Sigma; slot 0 = Phi210 (1,2,2)_-2 set to 0) -> (v_u, v_d, w_u, w_d) is real-linear;
it is inverted exactly (8x8 real system).
usage: python -B r2a_ew_targets.py <tag>  -> ew_<tag>_<label>.npz (key 'a') for the target list below + ew_targets_<tag>.json
"""
import sys, json, math, numpy as np
from scipy.optimize import brentq
import k3_common as K
import r2_compose as RC

tag = sys.argv[1]; nt = RC.Neutral(tag)
slots = [1, 2, 3, 4]


def comp_lin(x):
    a = np.zeros(5, complex); a[slots] = x[:4] + 1j * x[4:]
    c = RC.components(np.real(nt.WN @ a)); return np.array([c["vu"], c["vd"], c["wu"], c["wd"]]), c["frac"]


L = np.zeros((8, 8))
for j in range(8):
    e = np.zeros(8); e[j] = 1.0; v, _ = comp_lin(e); L[:, j] = np.concatenate([v.real, v.imag])
print("rank of the real map a -> (vu, vd, wu, wd):", np.linalg.matrix_rank(L), " cond", np.linalg.cond(L))


def a_for(r, s, zeta):
    tgt = np.array([r, 1.0, s * r * zeta, zeta], complex); x = np.linalg.solve(L, np.concatenate([tgt.real, tgt.imag]))
    a = np.zeros(5, complex); a[slots] = x[:4] + 1j * x[4:]; return a / np.linalg.norm(a)


def frac_sigma(r, s, zabs):
    a = a_for(r, s, zabs); return nt.comp_of_a(a)["frac"]["Sigma126bar"]


TARGETS = [("K2", 66.0, 0.43, 0.5), ("K2f01", 66.0, 0.43, 0.1), ("K2f09", 66.0, 0.43, 0.9), ("K2cs", 66.0, 0.43 + 0.3j, 0.5),
           ("r10", 10.0, 0.43, 0.5), ("r300", 300.0, 0.43, 0.5), ("s2", 66.0, 2.0, 0.5), ("sm1", 66.0, -1.0, 0.5), ("s01", 66.0, 0.1, 0.5),
           ("one", 1.0, 1.0, 0.5)]
out = {}
for lab, r, s, fs in TARGETS:
    g = lambda z: frac_sigma(r, s, z) - fs
    zs = np.logspace(-4, 4, 161); vals = [g(z) for z in zs]
    z0 = None
    for i in range(len(zs) - 1):
        if vals[i] * vals[i + 1] < 0: z0 = brentq(g, zs[i], zs[i + 1], xtol=1e-14); break
    if z0 is None: print(lab, "no zeta for f_Sigma", fs); continue
    a = a_for(r, s, z0); cm = nt.comp_of_a(a)
    np.savez(K.SCRATCH / f"ew_{tag}_{lab}.npz", a=a, r=abs(cm["r"]), s=np.array([cm["s"].real, cm["s"].imag]), zeta=z0)
    out[lab] = {"target": {"|r|": r, "s": [complex(s).real, complex(s).imag], "f_Sigma": fs}, "zeta=wd/vd": z0,
                "achieved": {"|r|": float(abs(cm["r"])), "s": [float(cm["s"].real), float(cm["s"].imag)], "frac": cm["frac"]}}
    print(f"{lab:6s} |r| {abs(cm['r']):.6g}  s {cm['s']:.6g}  f_Sigma {cm['frac']['Sigma126bar']:.4f}  zeta {z0:.5g}")
json.dump(out, open(K.SCRATCH / f"ew_targets_{tag}.json", "w"), indent=1)
