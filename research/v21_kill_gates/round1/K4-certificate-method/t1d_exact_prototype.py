"""t1d: EXACT verification of the prototype 210-only potential at Phi0 = (p,a) G3221 point.
  * integer Hessians of the six invariants at the integer point (int64, exact; magnitudes are small)
  * couplings: beta (SOS-cone weights) rounded to small denominators, c2,c3 solved exactly from stationarity
  * exact gradient = 0, exact H . tangents = 0, exact rational LDL^T positivity on the normal space
  * numerical multistart global search (NUM) with the final couplings
"""
import json, os, sys, time
from fractions import Fraction
import numpy as np
import sympy as sp
from scipy import sparse
from scipy.optimize import minimize
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = r"C:\Users\jayal\Downloads\So10Theory2\So10Theory\_g6_nogo"
sys.path.insert(0, HERE); sys.path.insert(0, REPO)
import k4lib as K
import k4fast as F
import exact_210_self_invariant_basis_v20 as self210

t0 = time.time()
P0, A0 = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (3, 2)
DEN = int(sys.argv[3]) if len(sys.argv) > 3 else 24
lab = f"p{P0}_a{A0}"
NAMES = ("I2", "I3", "Ja", "Jb", "Jc", "Je")
TMAP = sp.Matrix([[1, 0, -66, -24], [0, 0, 7, 116], [0, 0, 9, 332], [0, 1, 9, 120]])
spec = self210.spectral_quartics_in_basis()
CHANNELS = list(spec.keys())
CH = sp.Matrix([[sp.Rational(c.numerator, c.denominator) for c in spec[ch]] for ch in CHANNELS])
CH_MINE = CH * TMAP.T

phi_int = np.array([int(x) for x in K.pao_vector(P0, A0, 0, dtype=object)], dtype=np.int64)
phi_f = phi_int.astype(float)
gens = K.generators()
Tp = np.column_stack([g @ phi_int for g in gens]).astype(np.int64)        # 210 x 45 tangents (int)
LA = K.LA                                                                # int64 sparse 2025 x 210
A = (LA @ phi_int).reshape(45, 45)
A2 = A @ A; A3 = A2 @ A
I2 = int(phi_int @ phi_int)
E = LA.toarray().reshape(45, 45, 210).transpose(2, 0, 1)                # (210,45,45) int64


def hess_exact():
    H = {}
    H["I2"] = 2 * np.eye(210, dtype=np.int64)
    H["Ja"] = 8 * np.outer(phi_int, phi_int) + 4 * I2 * np.eye(210, dtype=np.int64)
    EA = np.einsum("iab,bc->iac", E, A); EA2 = np.einsum("iab,bc->iac", E, A2)
    t1 = np.einsum("iab,jba->ij", EA, E); t2 = np.einsum("iab,jbc,ca->ij", E, E, A, optimize=True)
    H["I3"] = 3 * (t1 + t2)
    u1 = np.einsum("iab,jbc,ca->ij", E, E, A2, optimize=True); u2 = np.einsum("iab,jbc,ca->ij", EA, E, A, optimize=True)
    u3 = np.einsum("iab,jba->ij", EA2, E)
    H["Jb"] = 4 * (u1 + u2 + u3)
    # Jc: B_k have half-integer entries: use 2*B_k (integer) -> M_k = phi^T B phi = (phi^T (2B) phi)/2
    Hc = np.zeros((210, 210), dtype=np.int64)
    for b in K.B_LIST:
        B2 = (b * 2).astype(np.int64)                      # integer matrix 2B
        bp2 = B2 @ phi_int                                 # = 2 B phi
        Mk2 = int(phi_int @ bp2)                           # = 2 M_k
        Hc += 2 * np.outer(bp2, bp2) + Mk2 * B2.toarray()   # 8 (Bphi)(Bphi)^T + 4 M_k B_k
    H["Jc"] = Hc
    G = Tp.T @ Tp                                           # 45x45 int
    # Je hessian = sum_AB [2 u_AB u_AB^T + 2 G_AB (T_A^T T_B + T_B^T T_A)], u_AB = T_A^T t_B + T_B^T t_A
    U = np.zeros((210, 45 * 45), dtype=np.int64)
    TA_T = [g.T.tocsr() for g in gens]
    for a in range(45):
        for b in range(45):
            U[:, a * 45 + b] = TA_T[a] @ Tp[:, b] + TA_T[b] @ Tp[:, a]
    He = 2 * (U @ U.T)
    # second term: 2 sum_AB G_AB (T_A^T T_B + T_B^T T_A) = 4 sum_AB G_AB T_A^T T_B
    Tst = sparse.vstack(gens).tocsr()                       # 9450 x 210
    GT = sparse.kron(sparse.csr_matrix(G), sparse.identity(210, dtype=np.int64, format="csr")).tocsr()
    He += 4 * (Tst.T @ (GT @ Tst)).toarray().astype(np.int64)
    H["Je"] = He
    return H


Hex = hess_exact()
# cross-check against float routines
for n in NAMES:
    cd = {m: (1.0 if m == n else 0.0) for m in NAMES}
    Hf = K.hessian(phi_f, cd)
    err = float(np.max(np.abs(Hf - Hex[n].astype(float))))
    print(n, "exact-vs-float Hessian max err", err, flush=True)
    assert err < 1e-6
# tangents must be annihilated by each invariant's Hessian? No: only by the full V Hessian at a stationary point.

# stationarity rows (exact) and couplings
p, a = P0, A0
I2r = p * p + 3 * a * a
rows = [[2 * p, 0, 4 * I2r * p, 24 * p ** 3, 24 * p * a * a, 96 * p ** 3 + 192 * p * a * a],
        [6 * a, 18 * a * a, 12 * I2r * a, 120 * a ** 3, 24 * p * p * a, 192 * p * p * a + 768 * a ** 3]]
Ms = sp.Matrix([[rows[0][0], rows[0][1]], [rows[1][0], rows[1][1]]])
# load beta from t1c json (float) and round
prev = json.load(open(os.path.join(HERE, "t1c_prototype_potential.json")))
beta_prev = [Fraction(b) for b in prev[lab]["beta_rational"]]
bq = [Fraction(float(b)).limit_denominator(DEN) for b in beta_prev]
lam_q = [sum(Fraction(str(CH_MINE[i, j])) * bq[i] for i in range(8)) for j in range(4)]
rhs = -sp.Matrix([sum(rows[0][k + 2] * sp.Rational(lam_q[k].numerator, lam_q[k].denominator) for k in range(4)),
                  sum(rows[1][k + 2] * sp.Rational(lam_q[k].numerator, lam_q[k].denominator) for k in range(4))])
sol = Ms.solve(rhs)
c_q = [Fraction(str(sol[0])), Fraction(str(sol[1]))] + lam_q
print("couplings:", dict(zip(NAMES, [str(x) for x in c_q])), flush=True)
cf = tuple(float(x) for x in c_q)
# exact gradient (object arithmetic)
phi_o = np.array([int(x) for x in phi_int], dtype=object)
A_o = K.A_matrix(phi_o); A2_o = A_o.dot(A_o); A3_o = A2_o.dot(A_o)
g = c_q[0] * 2 * phi_o + c_q[1] * 3 * K.A_to_phi_dual(A2_o) + c_q[2] * 4 * I2 * phi_o + c_q[3] * 4 * K.A_to_phi_dual(A3_o)
gc = np.zeros(210, dtype=object); gc[:] = 0
for b in K.B_LIST:
    B2 = (b * 2).astype(np.int64); bp2 = B2 @ phi_int; Mk2 = int(phi_int @ bp2)
    gc += Mk2 * bp2            # 4 M_k B_k phi = (2M_k)(2B_k phi)
g = g + c_q[4] * gc
G = Tp.T @ Tp
W = Tp @ G                     # 210 x 45 : column A = sum_B G_AB t_B
ge = np.zeros(210, dtype=np.int64)
for a_ in range(45):
    ge += gens[a_].T @ W[:, a_]
g = g + c_q[5] * 4 * ge.astype(object)
grad_zero = all(x == 0 for x in g)
print("exact gradient zero:", grad_zero, flush=True)
# exact Hessian (rational) and tangent annihilation
den = 1
for x in c_q:
    den = sp.ilcm(den, x.denominator)
den = int(den)
Hnum = sum(int(c_q[k] * den) * Hex[n].astype(object) for k, n in enumerate(NAMES))   # integer matrix = den * H
HT = Hnum.dot(Tp.astype(object))
tan_ok = all(int(x) == 0 for x in HT.ravel())
print("H . tangents == 0 exactly:", tan_ok, flush=True)
# exact normal basis (integer nullspace of tangents^T) and LDL
Tm = sp.Matrix(Tp.T.tolist())           # 45 x 210
ns = Tm.nullspace()
Nq = sp.Matrix.hstack(*ns)              # 210 x 180 rational
Hq = sp.Matrix(Hnum.tolist())
HN = Nq.T * Hq * Nq
print("normal block built", HN.shape, f"[{time.time() - t0:.0f}s]", flush=True)
n = HN.shape[0]
Af = [[Fraction(int(HN[i, j].p), int(HN[i, j].q)) for j in range(n)] for i in range(n)]
pd = True; kfail = None
for k in range(n):
    piv = Af[k][k]
    if piv <= 0:
        pd = False; kfail = (k, float(piv)); break
    for i in range(k + 1, n):
        f = Af[i][k] / piv
        if f == 0:
            continue
        rk = Af[k]; ri = Af[i]
        for j in range(k, n):
            ri[j] -= f * rk[j]
print("exact LDL positive definite on normal space:", pd, kfail, f"[{time.time() - t0:.0f}s]", flush=True)
ev = np.linalg.eigvalsh(np.array(Nq.tolist(), dtype=float).T @ (Hnum.astype(float) / den) @ np.array(Nq.tolist(), dtype=float))
# float eigen summary of normal Hessian in an orthonormal basis
U_, s_, Vt_ = np.linalg.svd(Tp.astype(float), full_matrices=True)
Nb = U_[:, 30:]
evN = np.linalg.eigvalsh(Nb.T @ (Hnum.astype(float) / den) @ Nb)
# numerical multistart
phi0 = phi_f
V0 = F.value_grad(phi0, cf)[0]
rng = np.random.default_rng(77)
scale = np.linalg.norm(phi0)
starts = []
for name, v in {"PS": K.pao_vector(1, 0, 0), "SU5+": K.pao_vector(1, 1, 1), "SU5-": K.pao_vector(1, 1, -1), "A": K.pao_vector(0, 1, 0),
                "W": K.pao_vector(0, 0, 1), "AW": K.pao_vector(0, 1, 1), "PW": K.pao_vector(1, 0, 1), "PAW": K.pao_vector(p, a, 1)}.items():
    for s in (0.3, 0.6, 1.0, 1.6, 2.5):
        starts.append((f"{name}x{s}", v / np.linalg.norm(v) * scale * s))
for k in range(1500):
    s = rng.choice([0.2, 0.5, 0.8, 1.0, 1.3, 2.0, 3.5])
    x = rng.normal(size=210); starts.append((f"rand{k}", x / np.linalg.norm(x) * scale * s))
for k in range(200):
    pp, aa, ww = rng.normal(size=3)
    x = K.pao_vector(pp, aa, ww); starts.append((f"paw{k}", x / np.linalg.norm(x) * scale * rng.choice([0.5, 1.0, 2.0])))
vals = []; lowers = []
for name, x in starts:
    res = minimize(lambda y: F.value_grad(y, cf), x, jac=True, method="L-BFGS-B", options={"maxiter": 5000, "gtol": 1e-10, "ftol": 1e-16})
    vals.append((float(res.fun), name))
    if res.fun < V0 - 1e-7 * max(1.0, abs(V0)):
        lowers.append((float(res.fun), name, res.x))
vals.sort()
distinct = []
for f_, name in vals:
    if not distinct or abs(f_ - distinct[-1][0]) > 1e-6 * max(1.0, abs(f_)):
        distinct.append((f_, name))
# classify the distinct local minima by orbit dimension (stabiliser)
classes = []
for f_, name in distinct[:10]:
    x = dict((nm, xx) for nm, xx in starts)[name]
    res = minimize(lambda y: F.value_grad(y, cf), x, jac=True, method="L-BFGS-B", options={"maxiter": 5000, "gtol": 1e-10, "ftol": 1e-16})
    unb, tan = K.stabilizer(res.x, tol=1e-6 * np.linalg.norm(res.x))
    classes.append({"V": f_, "orbit_dim": int(np.linalg.matrix_rank(tan, tol=1e-6 * np.linalg.norm(res.x))), "I2": float(res.x @ res.x),
                    "invariants": [float(v) for v in F.invariants(res.x)]})
summary = {"point": [P0, A0], "beta": [str(b) for b in bq], "couplings": dict(zip(NAMES, [str(x) for x in c_q])),
           "coupling_denominator_lcm": den, "exact_gradient_zero": bool(grad_zero), "exact_H_annihilates_tangents": bool(tan_ok),
           "exact_normal_LDL_PD": bool(pd), "normal_eig_min_float": float(evN[0]), "normal_eig_max_float": float(evN[-1]),
           "beta_min": str(min(bq)), "V0": V0, "n_starts": len(starts), "lowest_found": vals[0][0], "n_lower_than_V0": len(lowers),
           "distinct_local_minima": classes, "phi0_global_numerically": len(lowers) == 0, "elapsed_s": time.time() - t0}
print(json.dumps(summary, indent=1))
json.dump(summary, open(os.path.join(HERE, f"t1d_exact_prototype_{lab}.json"), "w"), indent=1)
