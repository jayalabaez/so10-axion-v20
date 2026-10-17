"""t1: find 210-only potentials with the (p,a) G3221 point as a positive-Hessian stationary point,
and test global minimality numerically (multistart L-BFGS + structured starts).

V = c2 I2 + c3 I3 + la Ja + lb Jb + lc Jc + le Je, restricted to (p,a,w):
  I2 = p^2+3a^2+6w^2 ; I3 = 6a^3+36aw^2+18pw^2 ;
  Ja = I2^2 ; Jb = 6p^4+30a^4+96w^4+24p^2w^2+96a^2w^2+48paw^2 ;
  Jc = 12p^2a^2+72a^2w^2+48paw^2+48w^4 ; Je = 24p^4+96p^2a^2+192a^4+240p^2w^2+384paw^2+1056a^2w^2+888w^4.
"""
import json, os, sys, time
from fractions import Fraction
import numpy as np
from scipy.optimize import minimize
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import k4lib as K
import k4fast as F

SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 1
P0, A0 = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (2, 1)
N_COUPLINGS = int(sys.argv[4]) if len(sys.argv) > 4 else 40
TAG = f"s{SEED}_p{P0}_a{A0}"
log = open(os.path.join(HERE, f"t1_{TAG}.log"), "w")


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True); log.write(s + "\n"); log.flush()


def restricted_grad_rows(p, a):
    """rows of d/dp and d/da of (I2, I3, Ja, Jb, Jc, Je) at (p,a,0) as Fractions."""
    I2 = p * p + 3 * a * a
    dI2 = (2 * p, 6 * a)
    dI3 = (0, 18 * a * a)
    dJa = (2 * I2 * 2 * p, 2 * I2 * 6 * a)
    dJb = (24 * p ** 3, 120 * a ** 3)
    dJc = (24 * p * a * a, 24 * p * p * a)
    dJe = (96 * p ** 3 + 192 * p * a * a, 192 * p * p * a + 768 * a ** 3)
    rows = [[dI2[0], dI3[0], dJa[0], dJb[0], dJc[0], dJe[0]], [dI2[1], dI3[1], dJa[1], dJb[1], dJc[1], dJe[1]]]
    return rows


phi0 = K.pao_vector(P0, A0, 0)
unb, tan = K.stabilizer(phi0)
orbit_dim = int(np.linalg.matrix_rank(tan))
Q, _ = np.linalg.qr(tan)                       # orthonormal tangent basis (210 x 30)
Nbasis = np.linalg.svd(np.eye(210) - Q @ Q.T)[0][:, :210 - orbit_dim]   # normal basis
say("phi0 (p,a)=", (P0, A0), "orbit_dim", orbit_dim, "normal dim", 210 - orbit_dim)
rows = restricted_grad_rows(P0, A0)
rng = np.random.default_rng(SEED)

# structured starting points
PS = K.pao_vector(1, 0, 0)
SU5 = K.pao_vector(1, np.sqrt(3) / np.sqrt(3), 0)  # placeholder, replaced below
# SU(5)xU(1) point in normalised coords (1, sqrt3, +-sqrt6)/sqrt10 -> unnormalised (p, a/sqrt3, w/sqrt6)
SU5p = K.pao_vector(1.0, 1.0, 1.0)
SU5m = K.pao_vector(1.0, 1.0, -1.0)
structured = {"PS": PS, "SU5+": SU5p, "SU5-": SU5m, "A_only": K.pao_vector(0, 1, 0), "W_only": K.pao_vector(0, 0, 1),
              "AW": K.pao_vector(0, 1, 1), "PW": K.pao_vector(1, 0, 1)}


def local_min(c, x0, maxiter=3000):
    res = minimize(lambda x: F.value_grad(x, c), x0, jac=True, method="L-BFGS-B", options={"maxiter": maxiter, "gtol": 1e-9, "ftol": 1e-15})
    return res.fun, res.x


def quartic_sphere_min(c, n=60):
    """min of the quartic part on the unit sphere (numerical), to test boundedness."""
    cq = (0.0, 0.0, c[2], c[3], c[4], c[5])
    best = np.inf
    for k in range(n):
        x = rng.normal(size=210); x /= np.linalg.norm(x)
        f = lambda y: (lambda v, g: (v / (y @ y) ** 2, (g * (y @ y) - 4.0 * v * y) / (y @ y) ** 3))(*F.value_grad(y, cq))
        res = minimize(f, x, jac=True, method="L-BFGS-B", options={"maxiter": 2000})
        best = min(best, res.fun)
    return best


results = []
found = 0
t0 = time.time()
for trial in range(N_COUPLINGS):
    # random rational quartics; positive-ish mixture to encourage boundedness
    la, lb, lc, le = [Fraction(int(x), 8) for x in rng.integers(-16, 33, size=4)]
    # solve c2, c3 from stationarity (2x2)
    A = np.array([[float(rows[0][0]), float(rows[0][1])], [float(rows[1][0]), float(rows[1][1])]])
    rhs = -np.array([float(rows[0][2]) * float(la) + float(rows[0][3]) * float(lb) + float(rows[0][4]) * float(lc) + float(rows[0][5]) * float(le),
                     float(rows[1][2]) * float(la) + float(rows[1][3]) * float(lb) + float(rows[1][4]) * float(lc) + float(rows[1][5]) * float(le)])
    try:
        c2f, c3f = np.linalg.solve(A, rhs)
    except np.linalg.LinAlgError:
        continue
    # exact rational version
    import sympy as sp
    Ms = sp.Matrix([[rows[0][0], rows[0][1]], [rows[1][0], rows[1][1]]])
    bs = -sp.Matrix([rows[0][2] * sp.Rational(la) + rows[0][3] * sp.Rational(lb) + rows[0][4] * sp.Rational(lc) + rows[0][5] * sp.Rational(le),
                     rows[1][2] * sp.Rational(la) + rows[1][3] * sp.Rational(lb) + rows[1][4] * sp.Rational(lc) + rows[1][5] * sp.Rational(le)])
    sol = Ms.solve(bs)
    c2, c3 = Fraction(str(sol[0])), Fraction(str(sol[1]))
    c = (float(c2), float(c3), float(la), float(lb), float(lc), float(le))
    V0, g0 = F.value_grad(phi0, c)
    gnorm = float(np.linalg.norm(g0))
    H = K.hessian(phi0, F.coeff_dict(c))
    HN = Nbasis.T @ H @ Nbasis
    ev = np.linalg.eigvalsh(HN)
    evT = np.linalg.eigvalsh(Q.T @ H @ Q)
    if ev[0] <= 1e-9 * max(1.0, abs(ev[-1])):
        continue
    qmin = quartic_sphere_min(c, n=30)
    if qmin <= 0:
        say(f"trial {trial}: PD normal Hessian but quartic sphere min {qmin:.4g} <= 0 (unbounded) -> skip")
        continue
    found += 1
    say(f"trial {trial}: couplings c2={c2} c3={c3} la={la} lb={lb} lc={lc} le={le}; V0={V0:.6f} |grad|={gnorm:.2e} "
        f"normal eig range [{ev[0]:.4g},{ev[-1]:.4g}] tangent max|eig| {np.max(np.abs(evT)):.2e} qsphere_min {qmin:.4g}")
    # global search
    best = (V0, "phi0")
    lowers = []
    scale = np.linalg.norm(phi0)
    starts = []
    for name, v in structured.items():
        for s in (0.5, 1.0, 2.0):
            starts.append((f"{name}x{s}", v / np.linalg.norm(v) * scale * s))
    for k in range(60):
        s = rng.choice([0.3, 0.7, 1.0, 1.5, 3.0])
        x = rng.normal(size=210); x = x / np.linalg.norm(x) * scale * s
        starts.append((f"rand{k}", x))
    for k in range(20):
        p, a, w = rng.normal(size=3)
        x = K.pao_vector(p, a, w); x = x / np.linalg.norm(x) * scale * rng.choice([0.5, 1.0, 2.0])
        starts.append((f"paw{k}", x))
    minima = []
    for name, x in starts:
        f, x1 = local_min(c, x)
        minima.append((f, name))
        if f < V0 - 1e-7 * max(1.0, abs(V0)):
            lowers.append((f, name, x1))
    minima.sort()
    distinct = []
    for f, name in minima:
        if not distinct or abs(f - distinct[-1][0]) > 1e-6 * max(1.0, abs(f)):
            distinct.append((f, name))
    say(f"   lowest found {minima[0][0]:.8f} ({minima[0][1]}) vs V0 {V0:.8f}; distinct local values: {[round(d[0], 6) for d in distinct[:8]]}")
    rec = {"trial": trial, "couplings": {"c2": str(c2), "c3": str(c3), "la": str(la), "lb": str(lb), "lc": str(lc), "le": str(le)},
           "V0": V0, "grad_norm": gnorm, "normal_eig_min": float(ev[0]), "normal_eig_max": float(ev[-1]),
           "quartic_sphere_min": float(qmin), "lowest_found": float(minima[0][0]), "lowest_name": minima[0][1],
           "n_lower": len(lowers), "distinct_values": [float(d[0]) for d in distinct[:10]],
           "phi0_is_global_numerically": len(lowers) == 0}
    if lowers:
        lowers.sort(key=lambda z: z[0])
        f, name, x1 = lowers[0]
        unb1, tan1 = K.stabilizer(x1, tol=1e-6 * np.linalg.norm(x1))
        rec["lower_point_orbit_dim"] = int(np.linalg.matrix_rank(tan1, tol=1e-6 * np.linalg.norm(x1)))
        rec["lower_point_invariants"] = [float(v) for v in F.invariants(x1)]
        say(f"   LOWER orbit found: V={f:.8f} orbit_dim={rec['lower_point_orbit_dim']} invariants={rec['lower_point_invariants']}")
    results.append(rec)
    json.dump({"p": P0, "a": A0, "seed": SEED, "results": results, "elapsed_s": time.time() - t0},
              open(os.path.join(HERE, f"t1_{TAG}.json"), "w"), indent=1)
say("done; found", found, "PD+bounded candidates; elapsed", time.time() - t0)
