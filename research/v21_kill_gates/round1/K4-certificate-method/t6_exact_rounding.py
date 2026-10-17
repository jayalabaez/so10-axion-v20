"""t6: exact rounding of a restricted degree-3 SOS certificate (if the t5 ansatz is feasible).

  h(Phi)(V(Phi)-V0) = sum_tau <s^tau(Phi), Q^tau s^tau(Phi)>,  h = 1 + h1 I2.
1. exact integer products P^tau_ab(Phi_k) at K random integer points, exact rhs.
2. interior SDP: maximise t s.t. Q^tau >= t I, identity at all points (equalities).
3. exact projection of the rounded (Q, h1) onto the affine identity subspace (rational linear algebra);
   exact PSD check by rational LDL (PD required).
4. identity verification beyond the fitting points: (a) 20 fresh random points with entries in [-1000,1000]
   (Schwartz-Zippel: a wrong identity survives each with prob <= 6/2001); (b) deterministic: rank of a candidate
   basis of the 30-dim invariant space on the point set (rank 30 -> the identity is an exact polynomial identity).
"""
import json, os, sys, time
from fractions import Fraction
import numpy as np
import sympy as sp
import cvxpy as cp
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import k4lib as K
import k4cov as C
import k4van as VN

t0 = time.time()
P0, A0 = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (3, 2)
KPTS = int(sys.argv[3]) if len(sys.argv) > 3 else 60
lab = f"p{P0}_a{A0}"
proto = json.load(open(os.path.join(HERE, f"t1d_exact_prototype_{lab}.json")))
NAMES = ("I2", "I3", "Ja", "Jb", "Jc", "Je")
c_q = [Fraction(proto["couplings"][n]) for n in NAMES]
phi0_int = np.array([int(x) for x in K.pao_vector(P0, A0, 0, dtype=object)], dtype=np.int64)
VN.FAMILIES = {
    "F4": {n: v for n, v in C.F4_COVARIANTS.items() if n not in ("eps3x3x3", "eps4x3x2")},
    "F2": {n: v for n, v in C.F2_COVARIANTS.items() if n != "chain"},
    "S2": dict(C.S2_COVARIANTS), "SC": dict(C.SC_COVARIANTS)}


def V_exact(phi_int):
    vo = np.array([int(x) for x in phi_int], dtype=object)
    inv = K.invariants(vo)
    return sum(c * Fraction(inv[n]) for c, n in zip(c_q, NAMES)), inv


V0, _ = V_exact(phi0_int)
combos = {t: VN.vanishing_combinations(t, phi0_int) for t in ("SC", "F2", "S2", "F4")}
TARGETS = [t for t in combos if combos[t][2]]
nvar = {t: len(combos[t][2]) for t in TARGETS}


def eval_points(pts):
    """exact products P[t][k] (n x n Fractions/ints), rhs r_k = V - V0, I2_k, and invariant family values."""
    P = {t: [] for t in TARGETS}; r = []; I2s = []; fam = []
    for p in pts:
        T = C.dense(p)
        covs = {t: {n: VN.flat(t, VN.FAMILIES[t][n][0](T)) for n in combos[t][0]} for t in TARGETS}
        for t in TARGETS:
            names, degs, alphas = combos[t]; w = VN.inner_weights(t)
            svals = []
            for alpha in alphas:
                tot = None
                for n, a in zip(names, alpha):
                    if a:
                        tot = a * covs[t][n] if tot is None else tot + a * covs[t][n]
                svals.append(tot)
            n = len(alphas); M = [[0] * n for _ in range(n)]
            for a in range(n):
                for b in range(a, n):
                    val = sum(int(w[i]) * int(svals[a][i]) * int(svals[b][i]) for i in range(len(w)))
                    M[a][b] = val; M[b][a] = val
            P[t].append(M)
        Vp, inv = V_exact(p)
        r.append(Vp - V0); I2s.append(int(p @ p))
        # candidate invariant family: products of generators + covariant pairings (deg <= 6)
        I2, I3, Ja, Jb, Jc, Je = (Fraction(inv[n]) for n in NAMES)
        row = [1, I2, I3, Ja, Jb, Jc, Je, I2 * I3, I2 * Ja, I2 * Jb, I2 * Jc, I2 * Je, I3 * I3]
        for t in TARGETS:
            names = combos[t][0]; w = VN.inner_weights(t)
            cl = [n for n in names]
            for i in range(len(cl)):
                for j in range(i, len(cl)):
                    row.append(sum(int(w[k]) * int(covs[t][cl[i]][k]) * int(covs[t][cl[j]][k]) for k in range(len(w))))
        fam.append(row)
    return P, r, I2s, fam


rng = np.random.default_rng(777)
pts = []
while len(pts) < KPTS:
    v = rng.integers(-3, 4, size=210) * (rng.random(210) < 0.35)
    if np.count_nonzero(v) >= 8:
        pts.append(v.astype(np.int64))
P, r, I2s, fam = eval_points(pts)
print("evaluated", KPTS, "points", f"[{time.time() - t0:.0f}s]", flush=True)
famM = sp.Matrix([[sp.Rational(x.numerator, x.denominator) if isinstance(x, Fraction) else sp.Integer(int(x)) for x in row] for row in fam])
fam_rank = famM.rank()
print("candidate invariant family: size", famM.shape[1], "rank on points", fam_rank, "(dim Inv_<=6 = 30)", flush=True)

# ---- interior SDP
scale = max(1.0, max(abs(float(x)) for x in r))
Qs = {t: cp.Variable((nvar[t], nvar[t]), symmetric=True) for t in TARGETS}
h1 = cp.Variable(); tt = cp.Variable()
cons = [h1 >= 0]
for t in TARGETS:
    cons.append(Qs[t] - tt * np.eye(nvar[t]) >> 0)
    cons.append(cp.trace(Qs[t]) <= 1e4)
for k in range(KPTS):
    lhs = (1.0 + h1 * I2s[k]) * float(r[k]) / scale
    rhs = sum(cp.sum(cp.multiply(Qs[t], np.array(P[t][k], dtype=float) / scale)) for t in TARGETS)
    cons.append(lhs == rhs)
prob = cp.Problem(cp.Maximize(tt), cons)
prob.solve(solver=cp.CLARABEL)
print("interior SDP status", prob.status, "t_max", tt.value, "h1", h1.value, f"[{time.time() - t0:.0f}s]", flush=True)
out = {"point": [P0, A0], "K": KPTS, "nvar": nvar, "sdp_status": prob.status, "t_max": float(tt.value) if tt.value is not None else None,
       "h1": float(h1.value) if h1.value is not None else None, "invariant_family_rank": int(fam_rank)}
if tt.value is None or tt.value <= 1e-7:
    print("no interior restricted certificate; stop", flush=True)
    json.dump(out, open(os.path.join(HERE, f"t6_exact_rounding_{lab}.json"), "w"), indent=1)
    sys.exit(0)

# ---- exact projection onto the identity subspace
# unknown vector x: for each target, upper-triangular entries (a<=b) of Q; then h1.  Identity at point k:
#   sum_t sum_{a<=b} m_ab Q_ab P_ab(k) - h1 * I2_k r_k = r_k    with m_ab = 1 (a=b) or 2 (a<b)
cols = []
for t in TARGETS:
    for a in range(nvar[t]):
        for b in range(a, nvar[t]):
            cols.append((t, a, b))
A = sp.zeros(KPTS, len(cols) + 1); bvec = sp.zeros(KPTS, 1)
for k in range(KPTS):
    for j, (t, a, b) in enumerate(cols):
        A[k, j] = (1 if a == b else 2) * int(P[t][k][a][b])
    A[k, len(cols)] = -sp.Rational(r[k].numerator, r[k].denominator) * I2s[k]
    bvec[k, 0] = sp.Rational(r[k].numerator, r[k].denominator)
x_num = []
for (t, a, b) in cols:
    x_num.append(float(Qs[t].value[a, b]))
x_num.append(float(h1.value))
x_r = sp.Matrix([sp.Rational(Fraction(v).limit_denominator(10 ** 6)) for v in x_num])
rankA = A.rank(); rankAb = A.row_join(bvec).rank()
print("identity system: rank A", rankA, "rank [A|b]", rankAb, "unknowns", A.shape[1], flush=True)
out["identity_rank_A"] = int(rankA); out["identity_rank_Ab"] = int(rankAb)
if rankAb > rankA:
    print("EXACT: the identity system is inconsistent over Q (no exact certificate in this ansatz at these points)", flush=True)
    out["exact_consistent"] = False
    json.dump(out, open(os.path.join(HERE, f"t6_exact_rounding_{lab}.json"), "w"), indent=1)
    sys.exit(0)
out["exact_consistent"] = True
# least-norm exact correction: x = x_r - A^T (A A^T)^+ (A x_r - b)  (use independent rows)
_, piv = A.T.rref()
rows = list(piv)
Ar = A.extract(rows, list(range(A.shape[1]))); br = bvec.extract(rows, [0])
resid = Ar * x_r - br
corr = Ar.T * (Ar * Ar.T).inv() * resid
x_ex = x_r - corr
assert (A * x_ex - bvec) == sp.zeros(KPTS, 1)
print("exact projection done; max correction", max(abs(float(v)) for v in corr), f"[{time.time() - t0:.0f}s]", flush=True)
# exact PSD check per block
Qex = {}
for t in TARGETS:
    n = nvar[t]; M = sp.zeros(n, n)
    for j, (tt_, a, b) in enumerate(cols):
        if tt_ == t:
            M[a, b] = x_ex[j]; M[b, a] = x_ex[j]
    Qex[t] = M
h1_ex = x_ex[len(cols)]
pd_all = True
for t, M in Qex.items():
    Mf = [[Fraction(int(M[i, j].p), int(M[i, j].q)) for j in range(M.shape[0])] for i in range(M.shape[0])]
    n = len(Mf); ok = True
    for k in range(n):
        piv_ = Mf[k][k]
        if piv_ <= 0:
            ok = False; break
        for i in range(k + 1, n):
            f = Mf[i][k] / piv_
            for j in range(k, n):
                Mf[i][j] -= f * Mf[k][j]
    print(t, "exact Q block PD:", ok, "float eigs", np.linalg.eigvalsh(np.array(M.tolist(), dtype=float)).round(6).tolist(), flush=True)
    pd_all &= ok
out["h1_exact"] = str(h1_ex); out["Q_exact"] = {t: [[str(M[i, j]) for j in range(M.shape[0])] for i in range(M.shape[0])] for t, M in Qex.items()}
out["all_blocks_exact_PD"] = bool(pd_all) and h1_ex >= 0
# ---- verification beyond fitting points
pts2 = []
rng2 = np.random.default_rng(99)
while len(pts2) < 20:
    v = rng2.integers(-1000, 1001, size=210) * (rng2.random(210) < 0.35)
    if np.count_nonzero(v) >= 8:
        pts2.append(v.astype(np.int64))
P2, r2, I22, fam2 = eval_points(pts2)
ok_all = True
for k in range(len(pts2)):
    lhs = (1 + h1_ex * I22[k]) * sp.Rational(r2[k].numerator, r2[k].denominator)
    rhs = 0
    for t in TARGETS:
        for a in range(nvar[t]):
            for b in range(nvar[t]):
                rhs += Qex[t][a, b] * int(P2[t][k][a][b])
    ok_all &= (lhs - rhs == 0)
print("identity holds exactly at 20 fresh large-box points:", ok_all, flush=True)
out["identity_exact_at_fresh_points"] = bool(ok_all)
famM2 = sp.Matrix([[sp.Rational(x.numerator, x.denominator) if isinstance(x, Fraction) else sp.Integer(int(x)) for x in row] for row in fam + fam2])
out["invariant_family_rank_all_points"] = int(famM2.rank())
out["deterministic_identity_proof"] = bool(famM2.rank() == 30 and ok_all)
out["elapsed_s"] = time.time() - t0
print(json.dumps({k: v for k, v in out.items() if k != "Q_exact"}, indent=1), flush=True)
json.dump(out, open(os.path.join(HERE, f"t6_exact_rounding_{lab}.json"), "w"), indent=1)
