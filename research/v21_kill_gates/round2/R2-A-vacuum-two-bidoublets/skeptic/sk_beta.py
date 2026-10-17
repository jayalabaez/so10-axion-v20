"""SKEPTIC (R2-A): EW targets WITH a Phi210-doublet admixture (beta).

The gate's EW targets a* (r2a_ew_targets.py) set the Phi210 slot of the (1,2)_{1/2} block to ZERO.  The 210 has no Yukawa
coupling to 16 x 16, so a Phi210 (1,2,2)_{B-L=+-2} admixture in the SM Higgs does NOT change the flavour composition
(r, s are ratios of the H10 / 126bar neutral components); it only rescales the overall Yukawa normalisation by
1/sqrt(1-|beta|^2).  So beta is a physically free parameter that the gate fixed to 0 (2 real conditions).
Here: at a feasible two-light-bidoublet point WITHOUT an EW target that survives all round-1..3 cuts
(G15_Am45_C2noew_R123, t = 0.0119), build a = (beta, gamma x) with x = the gate's target H/Sigma part (same r, s, f_Sigma)
and beta chosen so that a is orthogonal to the heavy doublet eigenvector (a lies exactly in the light doublet space).
Writes ew_beta_<tag>_<label>.npz (key 'a') and U files (U0, U7 projected) for sk_phase1.py.
"""
import sys, json
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; PARENT = HERE.parent
sys.path.insert(0, str(PARENT))
import k3_common as K  # noqa: E402
import r2_compose as RC  # noqa: E402  (read-only import: composition map)

sol_name = sys.argv[1] if len(sys.argv) > 1 else "G15_Am45_C2noew_R123.npz"
tag = sys.argv[2] if len(sys.argv) > 2 else "Am45"
labels_t = sys.argv[3].split(",") if len(sys.argv) > 3 else ["K2", "K2f09", "K2f01", "one", "s2"]
sol = np.load(PARENT / sol_name); c = sol["c"]
B = np.load(PARENT / f"{tag}_blocks.npz"); labels = [str(x) for x in B["labels"]]; kd = labels.index("(1,2)_|Y|=1/2")
A = np.einsum("p,pij->ij", c, B[f"A{kd}"]); A = 0.5 * (A + A.conj().T)
w, V = np.linalg.eigh(A); vh = V[:, -1]
nt = RC.Neutral(tag)
out = {"solution": sol_name, "tag": tag, "doublet_eigs": w.tolist(), "heavy_eigvec_abs2": (np.abs(vh) ** 2).tolist(), "targets": {}}
print("doublet eigenvalues", w, "heavy |v|^2", np.round(np.abs(vh) ** 2, 6))
for lab in labels_t:
    x = np.asarray(np.load(PARENT / f"ew_{tag}_{lab}.npz")["a"], complex); x = x / np.linalg.norm(x)
    assert abs(x[0]) < 1e-12
    beta = -(vh[1:].conj() @ x[1:]) / vh[0].conj()
    a = np.concatenate([[beta], x[1:]]); a /= np.linalg.norm(a)
    cm0 = nt.comp_of_a(x); cm = nt.comp_of_a(a)
    ray = float(np.real(a.conj() @ A @ a)); ray0 = float(np.real(x.conj() @ A @ x))
    rec = {"beta_abs2": float(abs(a[0]) ** 2), "overlap_heavy_target_x": float(abs(vh.conj() @ x)), "Rayleigh_a": ray, "Rayleigh_x(beta=0)": ray0,
           "r_target": float(abs(cm0["r"])), "s_target": [float(cm0["s"].real), float(cm0["s"].imag)],
           "r_beta": float(abs(cm["r"])), "s_beta": [float(cm["s"].real), float(cm["s"].imag)], "frac_beta": cm["frac"]}
    out["targets"][lab] = rec
    np.savez(HERE / f"ew_beta_{tag}_{lab}.npz", a=a)
    print(lab, json.dumps(rec, default=float))
# U files: singlet U0 from the solution; doublet U7 (4 light) projected onto the complement of a* is done in sk_phase1
json.dump(out, open(HERE / f"sk_beta_{tag}.json", "w"), indent=1, default=float)
