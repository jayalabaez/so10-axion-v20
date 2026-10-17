"""t3a: exact equivariance test of every explicit covariant under rational SO(10) rotations
(R1: plane (0,1) with cos=3/5, sin=4/5; R2: plane (2,7) with cos=5/13, sin=12/13; R = R2 R1 mixes the
SO(6)xSO(4) blocks) and under an odd signed permutation (det -1: detects pseudo-tensors)."""
import json, os, sys, time
from fractions import Fraction
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import k4lib as K
import k4cov as C

t0 = time.time()
N = 10


def rot(plane, c, s):
    R = np.array([[Fraction(int(i == j)) for j in range(N)] for i in range(N)], dtype=object)
    i, j = plane
    R[i, i] = c; R[j, j] = c; R[i, j] = -s; R[j, i] = s
    return R


R1 = rot((0, 1), Fraction(3, 5), Fraction(4, 5))
R2 = rot((2, 7), Fraction(5, 13), Fraction(12, 13))
R = R2.dot(R1)
# odd signed permutation: swap coordinates 0 and 9 (det -1)
P = np.array([[Fraction(0)] * N for _ in range(N)], dtype=object)
for i in range(N):
    P[i, i] = Fraction(1)
P[0, 0] = 0; P[9, 9] = 0; P[0, 9] = Fraction(1); P[9, 0] = Fraction(1)


def act4(R, T):
    return np.einsum("ia,jb,kc,ld,abcd->ijkl", R, R, R, R, T)


def act2(R, X):
    return np.einsum("ia,jb,ab->ij", R, R, X)


rng = np.random.default_rng(9)
v = rng.integers(-2, 3, size=210)
vo = np.array([Fraction(int(x)) for x in v], dtype=object)
T = C.dense(vo)
TR = act4(R, T)
TP = act4(P, T)
results = {}
for fam_name, fam, target in (("F4", C.F4_COVARIANTS, "F4"), ("F2", C.F2_COVARIANTS, "F2"), ("S2", C.S2_COVARIANTS, "S2"), ("SC", C.SC_COVARIANTS, "SC")):
    for name, (f, deg) in fam.items():
        cT = f(T)
        cTR = f(TR)
        cTP = f(TP)
        if target == "F4":
            lhs = act4(R, cT); lhsP = act4(P, cT)
        elif target in ("F2", "S2"):
            lhs = act2(R, cT); lhsP = act2(P, cT)
        else:
            lhs = cT; lhsP = cT
        d = np.asarray(cTR) - np.asarray(lhs)
        eq = bool(np.all(d == 0))
        dP = np.asarray(cTP) - np.asarray(lhsP)
        dPm = np.asarray(cTP) + np.asarray(lhsP)
        parity = "tensor" if np.all(dP == 0) else ("pseudo" if np.all(dPm == 0) else "NEITHER")
        results[f"{fam_name}:{name}"] = {"deg": deg, "SO10_equivariant": eq, "O10_parity": parity}
        print(f"{fam_name}:{name:10s} deg {deg}  SO(10)-equivariant: {eq}   O(10): {parity}  [{time.time() - t0:.0f}s]", flush=True)
json.dump(results, open(os.path.join(HERE, "t3a_equivariance.json"), "w"), indent=1)
