"""t7: Hessian-level necessary condition for a degree-3 SOS certificate built from the explicit (small-irrep)
vanishing families at Phi0:   h(Phi0) Hess V(Phi0) = 2 sum_tau sum_ab Q^tau_ab J_a^T W_tau J_b ,  Q^tau >= 0,
with J_a the exact polarisation matrices (target_dim x 210) and W_tau the invariant inner-product weights.
Both sides annihilate the 30 tangents; the equation is imposed on the 180-dim normal space.
A nonzero minimum residual (NUM, solver) shows that no SOS certificate using only these squares can match the
true Hessian at the vacuum, independently of any point sampling.  Also reports the unconstrained (indefinite)
least-squares residual to separate "span" from "PSD" failure."""
import json, os, sys, time
from fractions import Fraction
import numpy as np
import cvxpy as cp
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import k4lib as K
import k4fast as F
import k4cov as C
import k4van as VN

t0 = time.time()
P0, A0 = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (3, 2)
lab = f"p{P0}_a{A0}"
proto = json.load(open(os.path.join(HERE, f"t1d_exact_prototype_{lab}.json")))
NAMES = ("I2", "I3", "Ja", "Jb", "Jc", "Je")
cf = tuple(float(Fraction(proto["couplings"][n])) for n in NAMES)
phi0 = K.pao_vector(P0, A0, 0)
phi0_int = phi0.astype(np.int64)
VN.FAMILIES = {
    "F4": {n: v for n, v in C.F4_COVARIANTS.items() if n not in ("eps3x3x3", "eps4x3x2")},
    "F2": {n: v for n, v in C.F2_COVARIANTS.items() if n != "chain"},
    "S2": dict(C.S2_COVARIANTS), "SC": dict(C.SC_COVARIANTS)}
H = K.hessian(phi0, F.coeff_dict(cf))
unb, tan = K.stabilizer(phi0)
U, s, Vt = np.linalg.svd(tan, full_matrices=True)
Nb = U[:, 30:]
HN = Nb.T @ H @ Nb                                   # 180 x 180
I2_0 = float(phi0 @ phi0)
# polarisation matrices
blocks = {}
for target in ("SC", "F2", "S2", "F4"):
    names, degs, alphas = VN.vanishing_combinations(target, phi0_int)
    w = VN.inner_weights(target)
    Js = []
    for alpha in alphas:
        J = VN.polarisation_matrix(target, names, degs, alpha, phi0_int).astype(float)   # dim x 210
        Js.append((np.sqrt(w)[:, None] * J) @ Nb)                                       # weighted, on N
    blocks[target] = Js
    print(target, "n", len(Js), f"[{time.time() - t0:.0f}s]", flush=True)
# unknowns: upper-triangular Gram entries per block + h1.  Residual matrix R = (1 + h1 I2_0) HN - 2 sum Q_ab sym(J_a^T J_b)
cols = []; keys = []
for t, Js in blocks.items():
    n = len(Js)
    for a in range(n):
        for b in range(a, n):
            M = Js[a].T @ Js[b]; M = (M + M.T) * (1.0 if a == b else 1.0)   # 2*sym for a<b counted once via Q_ab + Q_ba
            cols.append(M.ravel()); keys.append((t, a, b))
A = np.column_stack(cols)                     # 32400 x n_q
bvec = HN.ravel()
hcol = -(I2_0 * HN).ravel()
scale = float(np.linalg.norm(HN))
# unconstrained (indefinite Q) least squares
x, res, rk, sv = np.linalg.lstsq(np.column_stack([A, hcol]), bvec, rcond=None)
lin_res = float(np.linalg.norm(np.column_stack([A, hcol]) @ x - bvec) / scale)
print("unconstrained (indefinite) Hessian match: relative residual", lin_res, "rank", rk, "/", A.shape[1] + 1, flush=True)
Qlin = {}
for t, Js in blocks.items():
    n = len(Js); M = np.zeros((n, n))
    for j, (tt, a, b) in enumerate(keys):
        if tt == t:
            M[a, b] = x[j]; M[b, a] = x[j]
    Qlin[t] = np.linalg.eigvalsh(M).tolist() if n else []
print("indefinite solution block eigenvalues:", {t: [round(e, 4) for e in v] for t, v in Qlin.items()}, flush=True)
# PSD-constrained: variables Q blocks, h1 >= 0 ; minimise ||A q + hcol h1 - b||
Qs = {t: cp.Variable((len(Js), len(Js)), PSD=True) for t, Js in blocks.items() if Js}
h1 = cp.Variable(nonneg=True)
qvec = cp.hstack([Qs[t][a, b] for (t, a, b) in keys])
expr = A @ qvec + hcol * h1 - bvec
prob = cp.Problem(cp.Minimize(cp.norm(expr, 2) / scale))
psd_res = None
for solver in (cp.CLARABEL, cp.SCS):
    try:
        prob.solve(solver=solver, **({} if solver == cp.CLARABEL else {"max_iters": 50000, "eps": 1e-9}))
        psd_res = float(prob.value); break
    except Exception as e:
        print("solver", solver, "failed:", e, flush=True)
print("PSD-constrained Hessian match: relative residual", psd_res, "status", prob.status, "h1", None if h1.value is None else float(h1.value), flush=True)
out = {"point": [P0, A0], "psd_relative_residual": psd_res, "psd_status": prob.status, "h1": float(h1.value) if h1.value is not None else None,
       "indefinite_relative_residual": lin_res, "indefinite_rank": int(rk), "n_unknowns": A.shape[1] + 1,
       "indefinite_solution_block_eigs": Qlin, "elapsed_s": time.time() - t0}
print(json.dumps(out, indent=1), flush=True)
json.dump(out, open(os.path.join(HERE, f"t7_hessian_lmi_{lab}.json"), "w"), indent=1)
