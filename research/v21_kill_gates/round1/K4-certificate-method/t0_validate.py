"""t0: validate k4lib against the repo (read-only imports) and check derivatives."""
import json
import os
import sys
import time
from fractions import Fraction

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = r"C:\Users\jayal\Downloads\So10Theory2\So10Theory\_g6_nogo"
sys.path.insert(0, HERE)
sys.path.insert(0, REPO)
import k4lib as K  # noqa: E402

t0 = time.time()
out = {}

# ---- 1. generators vs repo
import exact_phisigma_casimir_projectors_v20 as proj  # noqa: E402
import exact_210_self_invariant_basis_v20 as self210  # noqa: E402

rg = proj.generator_matrices()
maxdiff = 0.0
for g1, g2 in zip(K.generators(), rg):
    maxdiff = max(maxdiff, abs(g1.astype(float) - g2).max())
out["generator_max_abs_diff_vs_repo"] = float(maxdiff)
# repo basis order FOUR_INDICES equals mine?
out["basis_order_matches_repo"] = tuple(proj.FOUR_INDICES) == K.FOUR

# ---- 2. invariants vs repo pair moments (exact)
rng = np.random.default_rng(7)
rows_mine, rows_repo = [], []
pts = []
for k in range(7):
    v = rng.integers(-2, 3, size=210)
    pts.append(v)
    vo = np.array([Fraction(int(x)) for x in v], dtype=object)
    inv = K.invariants(vo)
    mom = self210.integer_pair_moments(v.astype(np.int64))
    rows_mine.append([inv["Ja"], inv["Jb"], inv["Jc"], inv["Jd"]])
    rows_repo.append([Fraction(mom[0]), Fraction(mom[2]), Fraction(mom[3]), Fraction(mom[4])])
    # I2 check vs mom? mom[0] = (phi.phi)^2
    assert inv["Ja"] == Fraction(mom[0]), "Ja != M0"
    # cubic invariant vs repo (float)
    c_repo = self210.cubic_invariant(self210.vector_to_phi(v.astype(float)))
    assert abs(float(inv["I3"]) - c_repo) < 1e-9 * (1 + abs(c_repo)), (inv["I3"], c_repo)
import sympy as sp  # noqa: E402
Mm = sp.Matrix([[sp.Rational(x.numerator, x.denominator) for x in r] for r in rows_mine])
Mr = sp.Matrix([[sp.Rational(x.numerator, x.denominator) for x in r] for r in rows_repo])
out["rank_mine_quartics"] = int(Mm.rank())
out["rank_repo_quartics"] = int(Mr.rank())
# solve repo = mine * T  (T 4x4) exactly using first 4 independent rows
print("ranks", Mm.rank(), Mr.rank(), flush=True)
_, piv = Mm.T.rref()
piv = list(piv)[:4]
print("pivot rows", piv, flush=True)
if Mm.rank() == 4:
    Msub = Mm.extract(piv, list(range(4)))
    Rsub = Mr.extract(piv, list(range(4)))
    T = Msub.inv() * Rsub
    resid = (Mm * T - Mr)
    out["repo_in_terms_of_mine_T"] = [[str(T[i, j]) for j in range(4)] for i in range(4)]
    out["change_of_basis_residual_zero"] = all(x == 0 for x in resid)
    Tinv = T.inv()
    out["mine_in_terms_of_repo_Tinv"] = [[str(Tinv[i, j]) for j in range(4)] for i in range(4)]
else:
    ns = Mm.nullspace()
    out["mine_quartic_linear_relations"] = [[str(x) for x in v] for v in ns]
    # express each of mine in repo basis
    _, pivr = Mr.T.rref(); pivr = list(pivr)[:4]
    Rsub = Mr.extract(pivr, list(range(4)))
    Msub = Mm.extract(pivr, list(range(4)))
    T2 = Rsub.inv() * Msub
    out["mine_in_terms_of_repo"] = [[str(T2[i, j]) for j in range(4)] for i in range(4)]
    out["mine_in_terms_of_repo_residual_zero"] = all(x == 0 for x in (Mr * T2 - Mm))

# ---- 3. derivative checks (float)
coeff = {"I2": -0.7, "I3": 0.31, "Ja": 0.9, "Jb": 0.4, "Jc": -0.25, "Jd": 0.6}
phi = rng.normal(size=210)
V, g = K.value_grad(phi, coeff)
inv = K.invariants(phi)
V2 = sum(coeff[n] * inv[n] for n in K.NAMES)
out["value_consistency"] = abs(V - V2)
eps = 1e-6
gfd = np.zeros(210)
for i in range(210):
    e = np.zeros(210); e[i] = eps
    gfd[i] = (K.value_grad(phi + e, coeff)[0] - K.value_grad(phi - e, coeff)[0]) / (2 * eps)
out["grad_fd_max_err"] = float(np.max(np.abs(gfd - g)))
H = K.hessian(phi, coeff)
Hfd = np.zeros((210, 210))
for i in range(210):
    e = np.zeros(210); e[i] = eps
    Hfd[:, i] = (K.value_grad(phi + e, coeff)[1] - K.value_grad(phi - e, coeff)[1]) / (2 * eps)
out["hess_fd_max_err"] = float(np.max(np.abs(Hfd - H)))
out["hess_scale"] = float(np.max(np.abs(H)))

# ---- 4. stabilizers
for lab, (p, a, w) in {"P_only": (1, 0, 0), "A_only": (0, 1, 0), "PA": (2, 1, 0), "PAW": (2, 1, 1), "W_only": (0, 0, 1), "AW": (0, 1, 1)}.items():
    v = K.pao_vector(p, a, w)
    unb, tan = K.stabilizer(v)
    rank = int(np.linalg.matrix_rank(tan, tol=1e-9)) if tan.shape[1] else 0
    out[f"stab_{lab}"] = {"unbroken": len(unb), "orbit_dim": rank}

# ---- 5. I3 and quartics on the (p,a,w) subspace: exact polynomial fit
mons = [(i, j, k) for i in range(5) for j in range(5) for k in range(5) if i + j + k == 4]
mons3 = [(i, j, k) for i in range(4) for j in range(4) for k in range(4) if i + j + k == 3]
pts3 = [(p, a, w) for p in range(-2, 3) for a in range(-2, 3) for w in range(-2, 3)]
rowsI3, rhsI3 = [], []
rowsQ, rhsQ = [], {n: [] for n in ("Ja", "Jb", "Jc", "Jd")}
for (p, a, w) in pts3:
    vo = K.pao_vector(p, a, w, dtype=object)
    inv = K.invariants(vo)
    rowsI3.append([Fraction(p ** i * a ** j * w ** k) for (i, j, k) in mons3]); rhsI3.append(inv["I3"])
    rowsQ.append([Fraction(p ** i * a ** j * w ** k) for (i, j, k) in mons])
    for n in rhsQ:
        rhsQ[n].append(inv[n])
A3 = sp.Matrix([[sp.Rational(x.numerator, x.denominator) for x in r] for r in rowsI3])
b3 = sp.Matrix([sp.Rational(x.numerator, x.denominator) for x in rhsI3])
sol3 = A3.solve_least_squares(b3)
out["I3_on_paw"] = {f"p^{i} a^{j} w^{k}": str(sol3[m]) for m, (i, j, k) in enumerate(mons3) if sol3[m] != 0}
AQ = sp.Matrix([[sp.Rational(x.numerator, x.denominator) for x in r] for r in rowsQ])
out["quartics_on_paw"] = {}
for n in rhsQ:
    bq = sp.Matrix([sp.Rational(x.numerator, x.denominator) for x in rhsQ[n]])
    s = AQ.solve_least_squares(bq)
    assert (AQ * s - bq).norm() == 0
    out["quartics_on_paw"][n] = {f"p^{i} a^{j} w^{k}": str(s[m]) for m, (i, j, k) in enumerate(mons) if s[m] != 0}
out["I2_on_paw"] = "p^2 + 3 a^2 + 6 w^2"
out["elapsed_s"] = time.time() - t0
print(json.dumps(out, indent=1))
with open(os.path.join(HERE, "t0_validate.json"), "w") as f:
    json.dump(out, f, indent=1)
