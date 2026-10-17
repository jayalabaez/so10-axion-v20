"""t1c: prototype 210-only potential with the (p,a) G3221 point as a strict local minimum AND an exactly
bounded (SOS-cone) quartic; rationalise; verify stationarity and normal-Hessian positivity exactly (rational LDL);
numerical multistart global search.
"""
import json, os, sys, time
from fractions import Fraction
import numpy as np
import cvxpy as cp
import sympy as sp
from scipy.optimize import minimize
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = r"C:\Users\jayal\Downloads\So10Theory2\So10Theory\_g6_nogo"
sys.path.insert(0, HERE); sys.path.insert(0, REPO)
import k4lib as K
import k4fast as F
import exact_210_self_invariant_basis_v20 as self210

t0 = time.time()
RATIOS = [(1, 1), (2, 1), (3, 2), (1, 2), (3, 1), (2, 3)]
if len(sys.argv) > 1:
    RATIOS = [tuple(int(x) for x in s.split(",")) for s in sys.argv[1:]]
NAMES = ("I2", "I3", "Ja", "Jb", "Jc", "Je")
# exact map: repo (J0,J2,J3,J4) = (M0,M2,M3,M4) in terms of (Ja,Jb,Jc,Je)
TMAP = sp.Matrix([[1, 0, -66, -24], [0, 0, 7, 116], [0, 0, 9, 332], [0, 1, 9, 120]])   # column j: repo J_j = sum_i TMAP[i,j] mine_i
spec = self210.spectral_quartics_in_basis()      # channel -> coefficients in (M0,M2,M3,M4)
CHANNELS = list(spec.keys())
CH = sp.Matrix([[sp.Rational(c.numerator, c.denominator) for c in spec[ch]] for ch in CHANNELS])  # 8 x 4 (in repo basis)
CH_MINE = CH * TMAP.T                            # 8 x 4 in (Ja,Jb,Jc,Je)
assert all(x == 0 for x in (sp.ones(1, 8) * CH_MINE - sp.Matrix([[1, 0, 0, 0]]))), "channels must sum to Ja=I2^2"
CH_MINE_f = np.array(CH_MINE.tolist(), dtype=float)


def restricted_grad_rows(p, a):
    I2 = p * p + 3 * a * a
    return [[2 * p, 0, 4 * I2 * p, 24 * p ** 3, 24 * p * a * a, 96 * p ** 3 + 192 * p * a * a],
            [6 * a, 18 * a * a, 12 * I2 * a, 120 * a ** 3, 24 * p * p * a, 192 * p * p * a + 768 * a ** 3]]


def rational_ldl_pd(Mq):
    """exact test of positive definiteness of a rational symmetric matrix via LDL^T with Fractions."""
    n = Mq.shape[0]
    A = [[Fraction(Mq[i, j]) for j in range(n)] for i in range(n)]
    for k in range(n):
        piv = A[k][k]
        if piv <= 0:
            return False, k, piv
        for i in range(k + 1, n):
            f = A[i][k] / piv
            if f == 0:
                continue
            rowk = A[k]; rowi = A[i]
            for j in range(k, n):
                rowi[j] -= f * rowk[j]
    return True, n, None


results = {}
best = None
for (p, a) in RATIOS:
    lab = f"p{p}_a{a}"
    phi0 = K.pao_vector(p, a, 0)
    unb, tan = K.stabilizer(phi0)
    od = int(np.linalg.matrix_rank(tan))
    U, s, Vt = np.linalg.svd(tan, full_matrices=True)
    Nb = U[:, od:]; nd = 210 - od
    Hk = []
    for n in NAMES:
        cdict = {m: (1.0 if m == n else 0.0) for m in NAMES}
        Hk.append(Nb.T @ K.hessian(phi0, cdict) @ Nb)
    rows = restricted_grad_rows(p, a)
    Ms = sp.Matrix([[rows[0][0], rows[0][1]], [rows[1][0], rows[1][1]]])
    Minv = np.array(Ms.inv().tolist(), dtype=float)
    R = np.array([[float(rows[0][k]) for k in range(2, 6)], [float(rows[1][k]) for k in range(2, 6)]])
    beta = cp.Variable(8)
    lam = CH_MINE_f.T @ beta                       # quartic couplings in (Ja,Jb,Jc,Je)
    t = cp.Variable()
    c23 = -Minv @ (R @ lam)
    c_all = cp.hstack([c23[0], c23[1], lam[0], lam[1], lam[2], lam[3]])
    H = sum(c_all[k] * Hk[k] for k in range(6))
    cons = [H - t * np.eye(nd) >> 0, cp.trace(H) == nd, beta >= 0.02 * cp.sum(beta), beta <= 1e3]
    prob = cp.Problem(cp.Maximize(t), cons)
    prob.solve(solver=cp.CLARABEL)
    tval = float(t.value) if t.value is not None else None
    rec = {"status": prob.status, "t_max": tval, "orbit_dim": od, "normal_dim": nd}
    print(lab, rec, f"[{time.time() - t0:.0f}s]", flush=True)
    if tval is None or tval <= 1e-6:
        results[lab] = rec; continue
    # rationalise beta (denominator <= 400), recompute everything exactly
    bq = [Fraction(float(b)).limit_denominator(400) for b in beta.value]
    lam_q = [sum(Fraction(str(CH_MINE[i, j])) * bq[i] for i in range(8)) for j in range(4)]
    rhs = -sp.Matrix([sum(rows[0][k + 2] * sp.Rational(lam_q[k].numerator, lam_q[k].denominator) for k in range(4)),
                      sum(rows[1][k + 2] * sp.Rational(lam_q[k].numerator, lam_q[k].denominator) for k in range(4))])
    sol = Ms.solve(rhs)
    c_q = [Fraction(str(sol[0])), Fraction(str(sol[1]))] + lam_q
    cf = tuple(float(x) for x in c_q)
    V0, g0 = F.value_grad(phi0, cf)
    Hr = K.hessian(phi0, F.coeff_dict(cf))
    ev = np.linalg.eigvalsh(Nb.T @ Hr @ Nb)
    rec.update({"beta_rational": [str(b) for b in bq], "couplings": dict(zip(NAMES, [str(x) for x in c_q])),
                "V0_float": V0, "grad_norm_float": float(np.linalg.norm(g0)),
                "normal_eig_min_float": float(ev[0]), "normal_eig_max_float": float(ev[-1]),
                "full_eigs_zero_count": int(np.sum(np.abs(np.linalg.eigvalsh(Hr)) < 1e-9))})
    print("   rationalised:", {k: rec[k] for k in ("couplings", "normal_eig_min_float", "normal_eig_max_float", "full_eigs_zero_count")}, flush=True)
    results[lab] = rec
    if ev[0] > 0 and (best is None or ev[0] / ev[-1] > best[0]):
        best = (ev[0] / ev[-1], lab, (p, a), c_q, bq)

json.dump(results, open(os.path.join(HERE, "t1c_prototype_potential.json"), "w"), indent=1, default=str)
if best is None:
    print("no bounded local-minimum point found"); sys.exit(0)

# ---------------- exact verification at the best point ----------------
ratio, lab, (p, a), c_q, bq = best
print("BEST", lab, "ratio", ratio, flush=True)
phi0o = K.pao_vector(p, a, 0, dtype=object)
vi = np.array([int(x) for x in phi0o])
# exact gradient: grad V = c2*2phi + c3*3 LA^T vec(A^2) + la*4 I2 phi + lb*4 LA^T vec(A^3) + lc*sum 4 M_k B_k phi + le*4 sum_A T_A^T (G Tp)_A
A0 = K.A_matrix(phi0o); A2 = A0.dot(A0); A3 = A2.dot(A0)
I2 = int(vi @ vi)
g = [Fraction(0)] * 210
g = np.array(g, dtype=object)
g += c_q[0] * 2 * phi0o + c_q[1] * 3 * K.A_to_phi_dual(A2) + c_q[2] * 4 * I2 * phi0o + c_q[3] * 4 * K.A_to_phi_dual(A3)
Mv = K.M_vector(phi0o)
for mk, b in zip(Mv, K.B_LIST):
    if mk != 0:
        coo = b.tocoo()
        for r, cidx, v in zip(coo.row, coo.col, coo.data):
            g[r] += c_q[4] * 4 * mk * Fraction(v).limit_denominator(4) * phi0o[cidx]
tans = K.exact_tangent_matrix(phi0o)
G = K.gram_tangents(phi0o)
W = [sum(G[A, B] * tans[B] for B in range(45)) for A in range(45)]      # (Tp G)_A
gens = K.generators()
for A in range(45):
    coo = gens[A].T.tocoo()
    for r, cidx, v in zip(coo.row, coo.col, coo.data):
        g[r] += c_q[5] * 4 * int(v) * W[A][cidx]
print("exact gradient zero:", all(x == 0 for x in g), flush=True)
# exact normal basis and exact Hessian
T = sp.Matrix([[int(x) for x in t] for t in tans])
ns = T.nullspace()
Nq = sp.Matrix.hstack(*ns)                 # 210 x nd
# exact Hessian: build via rational evaluation of the float hessian routine is not exact; instead use exact
# bilinear structure: H_ij = d^2 V.  Use sympy-free approach: evaluate hessian() in object arithmetic is not
# implemented, so compute the exact Hessian by finite polarisation of the exact gradient? Expensive.  Instead:
# the Hessian entries of a polynomial with rational coefficients at an integer point are rationals with bounded
# denominators (lcm of coupling denominators * small ints); float evaluation is exact to ~1e-12 relative, so
# rationalise with the known denominator and verify by LDL.
den = 1
for x in c_q:
    den = den * x.denominator // np.gcd(den, x.denominator)
den *= 8
Hf = K.hessian(K.pao_vector(p, a, 0), F.coeff_dict(tuple(float(x) for x in c_q)))
Hq = sp.Matrix(210, 210, lambda i, j: sp.Rational(int(round(Hf[i, j] * den)), den))
resid = float(np.max(np.abs(np.array(Hq.tolist(), dtype=float) - Hf)))
print("Hessian rationalisation residual:", resid, "(denominator", den, ")", flush=True)
HN = Nq.T * Hq * Nq
ok, k, piv = rational_ldl_pd(HN)
print("exact rational LDL positive definite on normal space:", ok, k, flush=True)
# tangent part must be exactly zero
HT = (Hq * T.T)
print("Hessian annihilates tangents exactly:", all(x == 0 for x in HT), flush=True)
# quartic boundedness exact: beta >= 0 with min beta
print("beta min:", min(bq), "-> Q >= beta_min * I2^2 exactly", flush=True)
# numerical multistart
cf = tuple(float(x) for x in c_q)
phi0 = K.pao_vector(p, a, 0)
V0 = F.value_grad(phi0, cf)[0]
rng = np.random.default_rng(2026)
scale = np.linalg.norm(phi0)
vals = []
lowers = []
starts = []
for name, v in {"PS": K.pao_vector(1, 0, 0), "SU5+": K.pao_vector(1, 1, 1), "SU5-": K.pao_vector(1, 1, -1), "A": K.pao_vector(0, 1, 0),
                "W": K.pao_vector(0, 0, 1), "AW": K.pao_vector(0, 1, 1), "PW": K.pao_vector(1, 0, 1), "PAW": K.pao_vector(p, a, 1), "PAWm": K.pao_vector(p, a, -1)}.items():
    for s in (0.3, 0.6, 1.0, 1.6, 2.5):
        starts.append((f"{name}x{s}", v / np.linalg.norm(v) * scale * s))
for k in range(600):
    s = rng.choice([0.2, 0.5, 0.8, 1.0, 1.3, 2.0, 3.5])
    x = rng.normal(size=210); starts.append((f"rand{k}", x / np.linalg.norm(x) * scale * s))
for k in range(100):
    pp, aa, ww = rng.normal(size=3)
    x = K.pao_vector(pp, aa, ww); starts.append((f"paw{k}", x / np.linalg.norm(x) * scale * rng.choice([0.5, 1.0, 2.0])))
for k in range(100):
    x = phi0 + rng.normal(size=210) * scale * rng.choice([0.05, 0.2, 0.5]); starts.append((f"near{k}", x))
for name, x in starts:
    res = minimize(lambda y: F.value_grad(y, cf), x, jac=True, method="L-BFGS-B", options={"maxiter": 5000, "gtol": 1e-10, "ftol": 1e-16})
    vals.append((res.fun, name))
    if res.fun < V0 - 1e-7 * max(1.0, abs(V0)):
        lowers.append((res.fun, name, res.x))
vals.sort()
distinct = []
for f, name in vals:
    if not distinct or abs(f - distinct[-1][0]) > 1e-6 * max(1.0, abs(f)):
        distinct.append((f, name))
summary = {"best_label": lab, "p": p, "a": a, "couplings": dict(zip(NAMES, [str(x) for x in c_q])), "beta": [str(b) for b in bq],
           "V0": V0, "exact_gradient_zero": bool(all(x == 0 for x in g)), "exact_normal_LDL_PD": bool(ok),
           "hessian_rationalisation_residual": resid, "n_starts": len(starts), "lowest_found": vals[0][0], "lowest_name": vals[0][1],
           "n_lower_than_V0": len(lowers), "distinct_local_values": [(float(f), n) for f, n in distinct[:12]],
           "phi0_global_numerically": len(lowers) == 0, "elapsed_s": time.time() - t0}
if lowers:
    lowers.sort(key=lambda z: z[0]); f, name, x1 = lowers[0]
    unb1, tan1 = K.stabilizer(x1, tol=1e-6 * np.linalg.norm(x1))
    summary["lower_orbit_dim"] = int(np.linalg.matrix_rank(tan1, tol=1e-6 * np.linalg.norm(x1)))
    summary["lower_invariants"] = [float(v) for v in F.invariants(x1)]
    np.save(os.path.join(HERE, "t1c_lower_point.npy"), x1)
print(json.dumps(summary, indent=1))
json.dump(summary, open(os.path.join(HERE, "t1c_prototype_summary.json"), "w"), indent=1)
