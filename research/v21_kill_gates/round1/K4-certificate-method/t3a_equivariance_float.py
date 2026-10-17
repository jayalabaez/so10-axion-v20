"""t3a (float): equivariance test of every explicit covariant under SO(10) rotations R = R2 R1
(planes (0,1) 3-4-5 and (2,7) 5-12-13) and an odd signed permutation; residuals relative to scale."""
import json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import k4lib as K
import k4cov as C

t0 = time.time(); N = 10


def rot(plane, c, s):
    R = np.eye(N); i, j = plane
    R[i, i] = c; R[j, j] = c; R[i, j] = -s; R[j, i] = s
    return R


R = rot((2, 7), 5 / 13, 12 / 13) @ rot((0, 1), 3 / 5, 4 / 5)
P = np.eye(N); P[0, 0] = 0; P[9, 9] = 0; P[0, 9] = 1; P[9, 0] = 1


def act4(R, T):
    return np.einsum("ia,jb,kc,ld,abcd->ijkl", R, R, R, R, T, optimize=True)


def act2(R, X):
    return np.einsum("ia,jb,ab->ij", R, R, X)


rng = np.random.default_rng(9)
v = rng.integers(-2, 3, size=210)
T = C.dense(v).astype(float)
TR = act4(R, T); TP = act4(P, T)
results = {}
for fam_name, fam, target in (("F4", C.F4_COVARIANTS, "F4"), ("F2", C.F2_COVARIANTS, "F2"), ("S2", C.S2_COVARIANTS, "S2"), ("SC", C.SC_COVARIANTS, "SC")):
    for name, (f, deg) in fam.items():
        cT = np.asarray(f(T), dtype=float); cTR = np.asarray(f(TR), dtype=float); cTP = np.asarray(f(TP), dtype=float)
        if target == "F4":
            lhs = act4(R, cT); lhsP = act4(P, cT)
        elif target in ("F2", "S2"):
            lhs = act2(R, cT); lhsP = act2(P, cT)
        else:
            lhs = cT; lhsP = cT
        sc = max(1e-300, float(np.max(np.abs(cT))))
        r_rot = float(np.max(np.abs(cTR - lhs))) / sc
        r_p = float(np.max(np.abs(cTP - lhsP))) / sc
        r_m = float(np.max(np.abs(cTP + lhsP))) / sc
        parity = "tensor" if r_p < 1e-9 else ("pseudo" if r_m < 1e-9 else "NEITHER")
        results[f"{fam_name}:{name}"] = {"deg": deg, "rot_residual": r_rot, "SO10_equivariant": r_rot < 1e-9, "O10_parity": parity, "scale": sc}
        print(f"{fam_name}:{name:10s} deg {deg}  rot residual {r_rot:.2e}  O(10): {parity}  [{time.time() - t0:.0f}s]", flush=True)
json.dump(results, open(os.path.join(HERE, "t3a_equivariance.json"), "w"), indent=1)
