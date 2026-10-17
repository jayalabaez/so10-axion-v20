"""Skeptic re-derivation (own code) of the EXACT K0b claims for v21-F17-B63.

Independent of R2-V's so10_chars.py and of round-1's k0b_engine: SO(10) tensor products are taken from the
standard Slansky tables (hard-coded), the kernel is computed with sympy, the PQ data with Fractions.
"""
from __future__ import annotations
import itertools, json, math
from fractions import Fraction as Fr
from pathlib import Path
import sympy as sp

HERE = Path(__file__).resolve().parent

# species: name, rep, X, generations   (rep: 16, -16 (=16bar), 10, 1)
FER = [("F", 16, 1, 3), ("V1", 16, -35, 2), ("Vb1", -16, 39, 1), ("V2", 16, -28, 1), ("Vb2", -16, 32, 1),
       ("V3", 16, 34, 1), ("Vb3", -16, -30, 1), ("T", 10, 2, 2), ("Pb", -16, 18, 1), ("N1", 1, -63, 1),
       ("N1b", 1, 59, 1), ("N2", 1, -58, 1), ("N2b", 1, 54, 1), ("N3", 1, -57, 1), ("N3b", 1, 61, 1),
       ("NMm", 1, -2, 2)]
# scalars: name, rep, X, real?
SCA = [("Phi210", 210, 0, True), ("Delta", -126, -2, False), ("H10", 10, -2, False), ("S", 1, 4, False),
       ("Phi17", 1, 17, False)]
DIM = {16: 16, -16: 16, 10: 10, 1: 1, 126: 126, -126: 126, 210: 210}
TIDX = {16: Fr(2), -16: Fr(2), 10: Fr(1), 1: Fr(0)}       # SO(10) Dynkin index, T(10)=1 (= SU(3) index T(3)=1/2)

def conj(r):
    return -r if r in (16, 126) or r in (-16, -126) else r

# Slansky: decomposition of fermion bilinears (sym part, antisym part) for SAME-rep pairs, and full for distinct reps
PROD = {
    (16, 16): {"s": [10, 126], "a": [120]},
    (-16, -16): {"s": [10, -126], "a": [120]},
    (16, -16): {"all": [1, 45, 210]},
    (10, 10): {"s": [1, 54], "a": [45]},
    (16, 10): {"all": [-16, 144]},
    (-16, 10): {"all": [16, -144]},
    (16, 1): {"all": [16]}, (-16, 1): {"all": [-16]}, (10, 1): {"all": [10]}, (1, 1): {"s": [1], "a": []},
}

def prod(r1, r2):
    if (r1, r2) in PROD:
        return PROD[(r1, r2)]
    return PROD[(r2, r1)]

def insertions():
    out = [("mass", 1, 0)]
    for n, r, x, real in SCA:
        out.append((n, r, x))
        if not real:
            out.append(("conj[" + n + "]", conj(r), -x))
    return out

def yukawas():
    res = []
    ins = insertions()
    for i, j in itertools.combinations_with_replacement(range(len(FER)), 2):
        a, b = FER[i], FER[j]
        for nm, r, x in ins:
            if a[2] + b[2] + x != 0:
                continue
            need = conj(r)  # bilinear must contain conj(rep of scalar)
            p = prod(a[1], b[1])
            if i != j:
                if need in p.get("all", p.get("s", []) + p.get("a", [])):
                    res.append((a[0] + "." + b[0], nm, "%dx%d" % (a[3], b[3])))
            else:
                g = a[3]
                if need in p.get("s", []) or need in p.get("all", []):
                    res.append((a[0] + "." + b[0], nm, "%dx%d sym" % (g, g)))
                if need in p.get("a", []) and g >= 2:
                    res.append((a[0] + "." + b[0], nm, "%dx%d antisym" % (g, g)))
    return res

def x_allowed_pairs():
    """all pairs+insertions with X=0 regardless of SO(10) (to show what SO(10) kills)"""
    out = []
    ins = insertions()
    for i, j in itertools.combinations_with_replacement(range(len(FER)), 2):
        a, b = FER[i], FER[j]
        for nm, r, x in ins:
            if a[2] + b[2] + x == 0:
                out.append((a[0] + "." + b[0], nm))
    return out

def anomalies():
    s2x = sum(TIDX[r] * x * g for n, r, x, g in FER)
    grav = sum(DIM[r] * x * g for n, r, x, g in FER)
    x3 = sum(DIM[r] * x ** 3 * g for n, r, x, g in FER)
    bX = Fr(2, 3) * sum(DIM[r] * x * x * g for n, r, x, g in FER) + Fr(1, 3) * sum(
        DIM[r] * x * x for n, r, x, real in SCA if not real)
    net16 = sum(g * (1 if r == 16 else -1 if r == -16 else 0) for n, r, x, g in FER)
    return {"SO10^2X": str(s2x), "grav-X": str(grav), "X^3": str(x3), "b_X": str(bX), "net16": net16}

def kernel(yuk):
    names = [f[0] for f in FER] + ["H10", "Delta", "S", "Phi17"]
    idx = {n: k for k, n in enumerate(names)}
    rows = []
    def addrow(terms):
        v = [0] * len(names)
        for nm, c in terms:
            v[idx[nm]] += c
        rows.append(v)
    for pair, ins, _ in yuk:
        a, b = pair.split(".")
        t = [(a, 1), (b, 1)]
        if ins.startswith("conj["):
            t.append((ins[5:-1], -1))
        elif ins not in ("mass", "Phi210"):
            t.append((ins, 1))
        addrow(t)
    # renormalizable phase-sensitive scalar terms of v20 (Phi210 real -> charge 0)
    addrow([("H10", 2), ("S", 1)])                      # kappaH H10.H10.S
    addrow([("H10", -1), ("Delta", 1)])                 # Phi210.H10*.Delta
    addrow([("H10", -1), ("Delta", -1), ("S", -1)])     # Phi210.H10*.Delta*.S*
    addrow([("Delta", 2), ("H10", -2)])                 # Delta^2 H10*^2
    M = sp.Matrix(rows)
    ns = M.nullspace()
    X = [f[2] for f in FER] + [-2, -2, 4, 17]
    def vec(d):
        v = [0] * len(names)
        for k, c in d.items():
            v[idx[k]] = c
        return v
    basis = {"X": X, "G2": vec({"V1": -1, "Vb1": 1, "Phi17": 1}), "f1": vec({"V1": 1, "Vb1": -1, "Pb": -1}),
             "f2": vec({"V2": 1, "Vb2": -1, "V3": -1, "Vb3": 1}), "f3": vec({"N1": 1, "N1b": -1}),
             "f4": vec({"N2": 1, "N2b": -1}), "f5": vec({"N3": 1, "N3b": -1})}
    inker = {k: all(x == 0 for x in (M * sp.Matrix(v))) for k, v in basis.items()}
    B = sp.Matrix([basis[k] for k in basis])
    return {"rank": M.rank(), "kernel_dim": len(ns), "basis_in_kernel": inker, "basis_rank": B.rank(),
            "spans": B.rank() == len(ns) and all(inker.values()), "names": names}, basis, idx

def pq(basis, idx):
    G2 = basis["G2"]; X = basis["X"]
    PQ = [x - 17 * g for x, g in zip(X, G2)]
    # QCD anomaly N = sum_gen T_SU3(R) * PQ, T_SU3(16)=2, T_SU3(10)=1; E = sum Q^2 PQ, sum Q^2: 16 -> 16/3, 10 -> 8/3
    Q2 = {16: Fr(16, 3), -16: Fr(16, 3), 10: Fr(8, 3), 1: Fr(0)}
    N = sum(TIDX[r] * g * PQ[idx[n]] for n, r, x, g in FER)
    E = sum(Q2[r] * g * PQ[idx[n]] for n, r, x, g in FER)
    def Nof(v):
        return sum(TIDX[r] * g * v[idx[n]] for n, r, x, g in FER)
    return {"N": str(N), "E": str(E), "E/N": str(E / N), "N(X)": str(Nof(X)), "N(G2)": str(Nof(G2)),
            "N(f)": [str(Nof(basis[k])) for k in ("f1", "f2", "f3", "f4", "f5")]}

def ndw():
    """axion circle: (theta_S, theta_Phi, theta_Delta, theta_H) modulo gauge X(alpha) x centre; G2 shifts theta_Phi.
    Find smallest G2 shift beta>0 equal to a gauge transformation leaving S, Delta, H10, Phi210 vevs fixed."""
    # gauge element X(alpha) c^k acts on S: 4 alpha; Phi17: 17 alpha; Delta, H10: -2 alpha + 2*(pi/2)k (centre i^z, z=2)
    sols = []
    for k in range(4):
        for m in range(-40, 41):   # alpha = 2 pi m / 4 ... search alpha in (pi/2) Z (S invariant)
            alpha = Fr(m, 4)       # in units of 2 pi
            s_ok = (4 * alpha).denominator == 1
            dh = (-2 * alpha + Fr(2 * k, 4))      # phase/2pi on Delta, H10
            if s_ok and dh.denominator == 1:
                phi = (17 * alpha) % 1
                sols.append(phi)
    shifts = sorted(set(sols))
    period = min([s for s in shifts if s > 0] + [Fr(1)])
    # G2 by beta (units 2pi) shifts theta_QCD by 2 N(G2) beta = -4 beta (units 2 pi); over the axion period:
    return {"gauge_identified_Phi_shifts(2pi units)": [str(s) for s in shifts], "axion_period_in_theta_Phi": str(period),
            "theta_QCD_winding_over_period": str(abs(-4 * period)), "N_DW": str(abs(-4 * period))}

def closure():
    Xs = {f[0]: f[2] for f in FER}; Xs.update({"S": 4, "Phi17": 17})
    q = {"N1": (0, 0, 0, 1, 0, 0), "N1b": (0, 0, 0, -1, 0, 0), "N2": (0, 0, 0, 0, 1, 0), "N2b": (0, 0, 0, 0, -1, 0),
         "N3": (0, 0, 0, 0, 0, 1), "N3b": (0, 0, 0, 0, 0, -1), "S": (0,) * 6, "Phi17": (1, 0, 0, 0, 0, 0)}
    # (field, power, conj?)  fermions dim 3/2, scalars 1
    ops = [(4, [("N1", 1, 0), ("N2b", 1, 0), ("S", 2, 1), ("Phi17", 1, 0)]),
           (1, [("N1", 2, 1), ("N3b", 2, 1), ("S", 1, 1)]),
           (2, [("N1b", 1, 0), ("N2", 2, 0), ("N3b", 1, 0), ("S", 1, 1)])]
    K = 0; Q = [0] * 6; rows = []
    vevS = 0; vevP = 0
    for mult, op in ops:
        X = sum((-1 if c else 1) * Xs[f] * p for f, p, c in op)
        d = sum((Fr(3, 2) if f[0] == "N" else 1) * p for f, p, c in op)
        und = sum(p for f, p, c in op if f[0] == "N" and not c); dot = sum(p for f, p, c in op if f[0] == "N" and c)
        qq = [sum((-1 if c else 1) * q[f][i] * p for f, p, c in op) for i in range(6)]
        rows.append({"mult": mult, "X": X, "d": str(d), "undotted": und, "dotted": dot, "q": qq,
                     "max_power_per_Weyl_singlet<=2": all(p <= 2 for f, p, c in op if f[0] == "N")})
        K += mult * (d - 4)
        Q = [Q[i] + mult * qq[i] for i in range(6)]
        vevS += mult * sum((-1 if c else 1) * p for f, p, c in op if f == "S")
        vevP += mult * sum((-1 if c else 1) * p for f, p, c in op if f == "Phi17")
    # propagators: N1 4 undotted + 2 dotted fields... mass insertions needed = N1-N1b and N2-N2b flips
    nfields = sum(mult * sum(p for f, p, c in op if f[0] == "N") for mult, op in ops)
    return {"ops": rows, "K": str(K), "sum_q": Q, "explicit_vev_S_power": vevS, "vev_Phi17_power": vevP,
            "X_of_explicit_vevs": 4 * vevS + 17 * vevP, "S*_needed_from_mass_insertions": (4 * vevS + 17 * vevP) // 4,
            "fermion_fields": nfields}

def numbers():
    MPl = 2.435e18; chi = 0.0755 ** 4; Phi = 1e17
    def dth(S, P=Phi, c=2.0):
        return c * P ** 4 * (S / MPl) ** 17 / chi
    Smax = MPl * (1e-10 * chi / (2 * Phi ** 4)) ** (1 / 17)
    ysmin = 1e13 / Smax
    L = math.log(MPl / 1e13)
    cap = (1 / (1 / (4 * math.pi) + 2 * 63 * L / (16 * math.pi ** 2))) ** 0.5
    fa = lambda S: math.sqrt(2) * S / 17
    ma = lambda S: 5.70 * 1e12 / fa(S)
    # tolerance in |g| for the strict floor: need y_s,min(g) <= cap
    gtol_floor = (cap / ysmin) ** 17   # S_max scales g^(-1/17) -> y_min scales g^(1/17)
    gtol_368 = (0.368 / ysmin) ** 17
    gtol_380 = (0.380 / ysmin) ** 17
    Phitol_368 = Phi * (0.368 / ysmin) ** (17 / 4)
    Phitol_floor = Phi * (cap / ysmin) ** (17 / 4)
    return {"dtheta(2.72e13)": dth(2.72e13), "dtheta(3e13)": dth(3e13), "dtheta(3.29e13)": dth(3.29e13),
            "S_max": Smax, "ys_min": ysmin, "cap_no_gauge_analytic": cap,
            "f_a(2.7e13,3.29e13)": [fa(2.7e13), fa(3.29e13)], "m_a_ueV(2.7e13,3.29e13)": [ma(2.7e13), ma(3.29e13)],
            "g_tolerance_floor": gtol_floor, "g_tolerance_cap0.368": gtol_368, "g_tolerance_cap0.380": gtol_380,
            "Phi17_tol_cap0.368": Phitol_368, "Phi17_tol_floor": Phitol_floor,
            "window_width_floor_percent": 100 * (cap - ysmin) / ysmin}

def main():
    out = {}
    out["anomalies"] = anomalies()
    yk = yukawas()
    out["yukawas"] = yk; out["n_yukawas"] = len(yk)
    allowed_x = x_allowed_pairs()
    yset = {(p, i) for p, i, _ in yk}
    out["X_allowed_but_SO10_forbidden"] = [a for a in allowed_x if a not in yset]
    k, basis, idx = kernel(yk)
    out["kernel"] = k
    out["pq"] = pq(basis, idx)
    out["ndw"] = ndw()
    out["closure"] = closure()
    out["numbers"] = numbers()
    (HERE / "sk_exact.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(json.dumps(out, indent=1, default=str))

if __name__ == "__main__":
    main()
