"""t0b: Je independence, change of basis to the repo (J0,J2,J3,J4), derivative checks, generic stabilizer."""
import json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = r"C:\Users\jayal\Downloads\So10Theory2\So10Theory\_g6_nogo"
sys.path.insert(0, HERE); sys.path.insert(0, REPO)
import k4lib as K
import exact_210_self_invariant_basis_v20 as self210
import sympy as sp
t0 = time.time(); out = {}
rng = np.random.default_rng(11)
rows_mine, rows_repo = [], []
for k in range(6):
    v = rng.integers(-2, 3, size=210)
    vo = np.array([int(x) for x in v], dtype=object)
    inv = K.invariants(vo)
    mom = self210.integer_pair_moments(v.astype(np.int64))
    rows_mine.append([inv["Ja"], inv["Jb"], inv["Jc"], inv["Je"]])
    rows_repo.append([mom[0], mom[2], mom[3], mom[4]])
    out.setdefault("Je_vs_M2", []).append([str(inv["Je"]), str(mom[2])])
Mm = sp.Matrix(rows_mine); Mr = sp.Matrix(rows_repo)
out["rank_mine"] = int(Mm.rank()); out["rank_repo"] = int(Mr.rank())
_, piv = Mm.T.rref(); piv = list(piv)[:4]
Msub = Mm.extract(piv, [0, 1, 2, 3]); Rsub = Mr.extract(piv, [0, 1, 2, 3])
T = Msub.inv() * Rsub           # repo = mine * T
out["repo_J0J2J3J4_in_terms_of_mine_JaJbJcJe_columns"] = [[str(T[i, j]) for j in range(4)] for i in range(4)]
out["residual_zero"] = all(x == 0 for x in (Mm * T - Mr))
Tinv = T.inv()
out["mine_in_terms_of_repo_columns"] = [[str(Tinv[i, j]) for j in range(4)] for i in range(4)]
coeff = {"I2": 0.0, "I3": 0.0, "Ja": 0.0, "Jb": 0.0, "Jc": 0.0, "Je": 1.0}
phi = rng.normal(size=210)
V, g = K.value_grad(phi, coeff)
eps = 1e-6; gfd = np.zeros(210)
for i in range(210):
    e = np.zeros(210); e[i] = eps
    gfd[i] = (K.value_grad(phi + e, coeff)[0] - K.value_grad(phi - e, coeff)[0]) / (2 * eps)
out["Je_grad_fd_err"] = float(np.max(np.abs(gfd - g)))
out["Je_value_check"] = abs(V - K.Je_value(phi))
H = K.hessian(phi, coeff)
idx = rng.choice(210, 12, replace=False); err = 0.0
for i in idx:
    e = np.zeros(210); e[i] = eps
    col = (K.value_grad(phi + e, coeff)[1] - K.value_grad(phi - e, coeff)[1]) / (2 * eps)
    err = max(err, float(np.max(np.abs(col - H[:, i]))))
out["Je_hess_fd_err_sampled"] = err; out["Je_hess_scale"] = float(np.max(np.abs(H)))
v = rng.normal(size=210)
unb, tan = K.stabilizer(v)
out["generic_orbit_dim"] = int(np.linalg.matrix_rank(tan))
out["orbit_space_dim"] = 210 - out["generic_orbit_dim"]
mons = [(i, j, k) for i in range(5) for j in range(5) for k in range(5) if i + j + k == 4]
pts = [(p, a, w) for p in range(-1, 3) for a in range(-1, 3) for w in range(-1, 3)]
rows, rhs = [], []
for (p, a, w) in pts:
    vo = K.pao_vector(p, a, w, dtype=object)
    rows.append([p ** i * a ** j * w ** k for (i, j, k) in mons]); rhs.append(K.Je_value(vo))
AQ = sp.Matrix(rows); bq = sp.Matrix(rhs)
sol = AQ.solve_least_squares(bq); assert (AQ * sol - bq).norm() == 0
out["Je_on_paw"] = {f"p^{i} a^{j} w^{k}": str(sol[m]) for m, (i, j, k) in enumerate(mons) if sol[m] != 0}
out["elapsed_s"] = time.time() - t0
print(json.dumps(out, indent=1))
json.dump(out, open(os.path.join(HERE, "t0b_validate_je.json"), "w"), indent=1)
