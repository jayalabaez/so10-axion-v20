"""SKEPTIC (variant V2 only): Clebsch of the X-allowed analogue (FF)_126 (Delta H45)_126bar for a 45_H vev along the SM-singlet
directions T3R (1,1,3) and B-L (15,1,1).  The 126bar component of Delta x 45 is the generator action (unique, 45 appears once
in 126 x 126bar); unit-norm CG: c^2 sum_A M_A M_A^dag = 1 over an orthonormal basis of the 45.  Own code."""
import itertools, math, json, sys
from pathlib import Path
import numpy as np
REPO = r"C:\Users\jayal\Downloads\So10Theory2\So10Theory\_v22research"
sys.path.insert(0, REPO)
import g3_sigma_hypercharge_audit_v20 as hyp  # conventions only
N = 10
B5 = list(itertools.combinations(range(N), 5)); I5 = {t: i for i, t in enumerate(B5)}
def sgn(s):
    s = list(s); v = 1
    for i in range(len(s)):
        for j in range(i + 1, len(s)):
            if s[i] > s[j]: v = -v
    return v
def lift(M):
    L = np.zeros((252, 252))
    for col, I in enumerate(B5):
        for pos, i in enumerate(I):
            for j in range(N):
                if M[j, i] == 0 or (j in I and j != i): continue
                if j == i: L[col, col] += M[j, i]; continue
                new = list(I); new[pos] = j
                L[I5[tuple(sorted(new))], col] += M[j, i] * sgn(new)
    return L
Hs = np.zeros((252, 252))
for col, I in enumerate(B5):
    comp = tuple(sorted(set(range(N)) - set(I))); Hs[I5[comp], col] = sgn(I + comp)
w, U = np.linalg.eig(Hs.astype(complex)); Q, _ = np.linalg.qr(U[:, np.abs(w + 1j) < 1e-9]); P = Q.conj().T
def E(a, b):
    m = np.zeros((N, N)); m[a, b] = -1; m[b, a] = 1; return m / math.sqrt(2)   # unit Frobenius/2-form norm
gens = [P @ lift(E(a, b)) @ Q for a, b in itertools.combinations(range(N), 2)]
Ssum = sum(1j * g @ (1j * g).conj().T for g in gens)
ev = np.linalg.eigvalsh(0.5 * (Ssum + Ssum.conj().T)); c = 1 / math.sqrt(ev.mean())
g = lambda v: P @ lift(hyp._matrix(v).astype(float)) @ Q
su3 = [g(v) for v in hyp.su3_colour_integer_basis()]; su2 = [g(v) for v in hyp.SU2L_INTEGER]
Y = -1j * g(hyp.Y_STANDARD_INTEGER) / 6
C3 = -sum(x @ x for x in su3); C2 = -sum((0.5 * x) @ (0.5 * x) for x in su2)
def sub(conds):
    Mt = sum((o - v * np.eye(126)).conj().T @ (o - v * np.eye(126)) for o, v in conds)
    w, V = np.linalg.eigh(0.5 * (Mt + Mt.conj().T)); return V[:, w < 1e-9]
S0 = sub([(C3, 0), (C2, 0), (Y, 0)]); Dd = sub([(C3, 0), (C2, .75), (Y, -.5)]); Du = sub([(C3, 0), (C2, .75), (Y, .5)])
res = {"casimir_spread": float(ev.max() - ev.min())}
for name, vec in (("T3R", hyp.T3R_INTEGER), ("B-L", hyp.BL_INTEGER)):
    Mm = hyp._matrix(vec).astype(float); Mm /= math.sqrt(0.5 * np.sum(Mm ** 2))   # unit 2-form norm
    M = c * 1j * (P @ lift(Mm) @ Q)
    kR = float(np.real(S0[:, 0].conj() @ M @ S0[:, 0]))
    kd = float(np.real(np.trace(Dd.conj().T @ M @ Dd)) / 2); ku = float(np.real(np.trace(Du.conj().T @ M @ Du)) / 2)
    res[name] = {"kR": kR, "ku": ku, "kd": kd, "tau": 2 * math.sqrt(6) * (kR - kd)}
print(json.dumps(res, indent=1)); json.dump(res, open(Path(__file__).with_name("o5_45_clebsch.json"), "w"), indent=1)
