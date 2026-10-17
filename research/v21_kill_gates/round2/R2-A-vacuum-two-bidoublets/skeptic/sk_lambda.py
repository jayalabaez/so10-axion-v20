"""SKEPTIC (R2-A): exact tree lambda_eff along the EW (SM-Higgs) neutral direction of a coupling point, and the
heavy-relaxed Higgs valley V(q* + h u + h^2/2 phi2) - V*.

u = neutral real chart direction of the EW eigenvector a* (r2_compose.Neutral.q_of_a, read-only import).
V is an exact quartic polynomial in the fields, so along a line every finite-difference formula below is EXACT:
  V4 = d^4V/du^4 from 5 equally spaced values;  b_j = d^2(dV/dq_j)/du^2 = [g(+e) - 2 g(0) + g(-e)]/e^2 (exact gradients).
lambda_eff_heavy = V4/6 - b_h^T M_h^-1 b_h / 2 (heavy = Hessian eigenvalues >= 3e-5),  R_light from light non-doublet modes.
usage: python -B sk_lambda.py <solution npz (skeptic/)> <tag> <ew npz (relative to parent)>
"""
import sys, json
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; PARENT = HERE.parent
sys.path.insert(0, str(PARENT))
import k3_common as K  # noqa: E402
import r2_compose as RC  # noqa: E402

solf, tag, ewf = sys.argv[1:4]
sol = np.load(HERE / solf if (HERE / solf).exists() else PARENT / solf); c = sol["c"]; ids = [str(x) for x in sol["ids"]]
Z = np.load(PARENT / f"{tag}_rows.npz"); q0 = Z["q"]; H = np.einsum("p,pij->ij", c, Z["hess"]); H = 0.5 * (H + H.T)
a = np.asarray(np.load(PARENT / ewf)["a"], complex); a /= np.linalg.norm(a)
nt = RC.Neutral(tag); u = nt.q_of_a(a); u /= np.linalg.norm(u)
chart = K.chart; pot = K.potential


def V(q):
    jac = pot.coefficient_jacobian(pot.evaluate_directions(chart.unpack(q).validated()))
    return float(c @ np.array([float(np.real(jac[p])) for p in ids]))


def grad(q):
    rows = K.parameter_rows(chart.unpack(q))
    return sum(c[i] * np.asarray(rows[p].gradient, float) for i, p in enumerate(ids))


e = 0.1
f = [V(q0 + k * e * u) for k in (-2, -1, 0, 1, 2)]
V4 = (f[4] - 4 * f[3] + 6 * f[2] - 4 * f[1] + f[0]) / e ** 4
gp, g0, gm = grad(q0 + e * u), grad(q0), grad(q0 - e * u)
b = (gp - 2 * g0 + gm) / e ** 2
w, Vec = np.linalg.eigh(H)
heavy = w >= 3e-5; gold = np.abs(w) < 1e-9; light = (~heavy) & (~gold)
# light doublet directions (lifted): exclude modes with large overlap on the doublet block lift
B = np.load(PARENT / f"{tag}_blocks.npz"); labels = [str(x) for x in B["labels"]]; kd = labels.index("(1,2)_|Y|=1/2"); W = B[f"W{kd}"]
Dl = np.linalg.svd(np.column_stack([W.real, W.imag]), full_matrices=False)[0]
Dl = Dl[:, :np.linalg.matrix_rank(np.column_stack([W.real, W.imag]))]
bh = Vec[:, heavy].T @ b; Rh = float(np.sum(bh ** 2 / w[heavy]))
lt = [j for j in np.where(light)[0] if np.linalg.norm(Dl.T @ Vec[:, j]) < 0.5]
bl = Vec[:, lt].T @ b; Rl = float(np.sum(bl ** 2 / w[lt])) if lt else 0.0
lam_h = V4 / 6 - Rh / 2; lam_all = V4 / 6 - (Rh + Rl) / 2
mu2 = float(u @ H @ u)
phi2 = -Vec[:, heavy] @ (bh / w[heavy])
val = []
for h in (0.01, 0.02, 0.05, 0.1):
    dv = V(q0 + h * u + 0.5 * h * h * phi2) - f[2]
    val.append({"h": h, "dV_relaxed": dv, "dV_EFT_pred": 0.5 * mu2 * h * h + lam_h / 4 * h ** 4})
res = {"solution": solf, "tag": tag, "ew": ewf, "u_mass2": mu2, "lambda_direct": V4 / 6, "R_heavy": Rh, "R_light_nondoublet": Rl,
       "lambda_eff_heavy": lam_h, "lambda_eff_all": lam_all, "n_light_nondoublet": len(lt), "valley": val,
       "b_goldstone_max": float(np.max(np.abs(Vec[:, gold].T @ b))) if gold.any() else 0.0}
print(json.dumps(res, default=float, indent=1))
json.dump(res, open(HERE / f"lambda_{Path(solf).stem}.json", "w"), indent=1, default=float)
