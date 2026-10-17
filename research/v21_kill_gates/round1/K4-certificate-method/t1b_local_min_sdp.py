"""t1b: for rational (p,a) G3221 points, decide by SDP whether some 210-only couplings make Phi0 a strict
local minimum (normal Hessian PD) with stationarity imposed; then round to rationals and verify exactly.
H(c) = sum_k c_k H_k  (H_k = Hessian of invariant k at Phi0);  c2, c3 affine in (la, lb, lc, le) by stationarity.
maximize t  s.t.  N^T H(c) N - t I >= 0,  trace(N^T H N) = normal_dim,  |lambda| <= 50.
"""
import json, os, sys, time
from fractions import Fraction
import numpy as np
import cvxpy as cp
import sympy as sp
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import k4lib as K
import k4fast as F

t0 = time.time()
RATIOS = [(1, 1), (2, 1), (1, 2), (3, 1), (1, 3), (3, 2), (2, 3), (4, 1), (1, 4), (5, 2), (2, 5), (5, 1), (1, 5), (7, 2), (1, 7), (1, 0), (0, 1)]
if len(sys.argv) > 1:
    RATIOS = [tuple(int(x) for x in s.split(",")) for s in sys.argv[1:]]


def restricted_grad_rows(p, a):
    I2 = p * p + 3 * a * a
    return [[2 * p, 0, 4 * I2 * p, 24 * p ** 3, 24 * p * a * a, 96 * p ** 3 + 192 * p * a * a],
            [6 * a, 18 * a * a, 12 * I2 * a, 120 * a ** 3, 24 * p * p * a, 192 * p * p * a + 768 * a ** 3]]


results = {}
for (p, a) in RATIOS:
    lab = f"p{p}_a{a}"
    phi0 = K.pao_vector(p, a, 0)
    unb, tan = K.stabilizer(phi0)
    od = int(np.linalg.matrix_rank(tan))
    U, s, Vt = np.linalg.svd(tan, full_matrices=True)
    Nb = U[:, od:]                                     # orthonormal normal basis 210 x (210-od)
    nd = 210 - od
    # Hessians of the six invariants at phi0
    names = ("I2", "I3", "Ja", "Jb", "Jc", "Je")
    Hk = []
    for n in names:
        cdict = {m: (1.0 if m == n else 0.0) for m in names}
        Hk.append(Nb.T @ K.hessian(phi0, cdict) @ Nb)
    rows = restricted_grad_rows(p, a)
    # stationarity: rows . c = 0 (2 equations)  -> solve for c2, c3 if the 2x2 block is invertible
    Ms = sp.Matrix([[rows[0][0], rows[0][1]], [rows[1][0], rows[1][1]]])
    singular = Ms.det() == 0
    lam = cp.Variable(4)
    t = cp.Variable()
    if not singular:
        Minv = np.array(Ms.inv().tolist(), dtype=float)
        R = np.array([[float(rows[0][k]) for k in range(2, 6)], [float(rows[1][k]) for k in range(2, 6)]])
        c23 = -Minv @ (R @ lam)                        # affine in lam
        c_all = cp.hstack([c23[0], c23[1], lam[0], lam[1], lam[2], lam[3]])
    else:
        # p=0 or a=0: stationarity rows may be degenerate; treat c2,c3 as free with the linear constraints
        cfree = cp.Variable(2)
        c_all = cp.hstack([cfree[0], cfree[1], lam[0], lam[1], lam[2], lam[3]])
    H = sum(c_all[k] * Hk[k] for k in range(6))
    cons = [H - t * np.eye(nd) >> 0, cp.trace(H) == nd, cp.abs(c_all) <= 1e3]
    if singular:
        cons += [sum(float(rows[0][k]) * c_all[k] for k in range(6)) == 0, sum(float(rows[1][k]) * c_all[k] for k in range(6)) == 0]
    prob = cp.Problem(cp.Maximize(t), cons)
    try:
        prob.solve(solver=cp.CLARABEL)
    except Exception as e:
        try:
            prob.solve(solver=cp.SCS, max_iters=20000, eps=1e-8)
        except Exception as e2:
            results[lab] = {"error": str(e2)}; print(lab, "solver error", e2, flush=True); continue
    tval = float(t.value) if t.value is not None else None
    rec = {"orbit_dim": od, "normal_dim": nd, "status": prob.status, "t_max_over_trace_normalised": tval}
    if tval is not None and tval > 1e-6:
        cvals = np.array([float(v) for v in c_all.value])
        rec["couplings_float"] = dict(zip(names, cvals.tolist()))
        # exact rounding: round lambdas to rationals, recompute c2,c3 exactly, verify PD exactly-ish (float eig of exact H)
        lam_r = [Fraction(float(v)).limit_denominator(64) for v in cvals[2:]]
        if not singular:
            rhs = -sp.Matrix([sum(rows[0][k + 2] * sp.Rational(lam_r[k].numerator, lam_r[k].denominator) for k in range(4)),
                              sum(rows[1][k + 2] * sp.Rational(lam_r[k].numerator, lam_r[k].denominator) for k in range(4))])
            sol = Ms.solve(rhs)
            c_r = [Fraction(str(sol[0])), Fraction(str(sol[1]))] + lam_r
        else:
            c_r = [Fraction(float(cvals[0])).limit_denominator(64), Fraction(float(cvals[1])).limit_denominator(64)] + lam_r
        cf = tuple(float(x) for x in c_r)
        Hr = Nb.T @ K.hessian(phi0, F.coeff_dict(cf)) @ Nb
        ev = np.linalg.eigvalsh(Hr)
        V0, g0 = F.value_grad(phi0, cf)
        rec["rounded_couplings"] = dict(zip(names, [str(x) for x in c_r]))
        rec["rounded_grad_norm"] = float(np.linalg.norm(g0))
        rec["rounded_normal_eig_min"] = float(ev[0]); rec["rounded_normal_eig_max"] = float(ev[-1])
        rec["rounded_V0"] = V0
    results[lab] = rec
    print(lab, json.dumps(rec), f"[{time.time() - t0:.0f}s]", flush=True)
json.dump(results, open(os.path.join(HERE, "t1b_local_min_sdp.json"), "w"), indent=1)
print("done", time.time() - t0)
