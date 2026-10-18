"""SKEPTIC cross-check of o5_clebsch.py by a second, independent construction of the 126bar component of Delta x Phi:
the explicit two-index contraction (Phi.Delta)_{abefg} = Phi_{abcd} Delta_{cdefg} (fully antisymmetrised), restricted to
the -i Hodge eigenspace, normalised by the same isometric-CG condition c^2 sum_A M_A M_A^dag = 1.
Also checks Tr(M M^dag) = 126/210 for a unit Phi, and computes the alternative 'max-eigenvalue = 1' normalisation
(the most generous convention one could adopt), to bound tau under any convention with |k'| <= 1.
"""
from __future__ import annotations
import itertools, math, sys, json
from pathlib import Path
import numpy as np

REPO = r"C:\Users\jayal\Downloads\So10Theory2\So10Theory\_v22research"
sys.path.insert(0, REPO)
import direct_phi_h_sigmabar_tensor_v20 as direct  # noqa: E402 (conventions: p,a,omega forms only)
import g3_sigma_hypercharge_audit_v20 as hyp  # noqa: E402 (SM generator integer bases only)

N = 10
B5 = list(itertools.combinations(range(N), 5)); I5 = {t: i for i, t in enumerate(B5)}
B4 = list(itertools.combinations(range(N), 4))


def sgn(seq):
    s = 1; seq = list(seq)
    for i in range(len(seq)):
        for j in range(i + 1, len(seq)):
            if seq[i] > seq[j]:
                s = -s
    return s


def contraction_matrix(phi):
    """Matrix of Delta -> sum over ordered (c<d) of Phi_{ab cd} Delta_{cd efg}, as a 5-form, basis e_I."""
    M = np.zeros((252, 252))
    for I4, pv in phi.items():
        if abs(pv) < 1e-15:
            continue
        for col, J in enumerate(B5):
            common = set(I4) & set(J)
            if len(common) != 2:
                continue
            c, d = sorted(common)
            a, b = [i for i in I4 if i not in common]
            efg = [j for j in J if j not in common]
            # Phi_{a b c d} with I4 sorted: sign to bring I4 to order (a,b,c,d)
            s1 = sgn([I4.index(t) for t in (a, b, c, d)])
            # Delta_{c d e f g}: sign to bring J to order (c,d,e,f,g)
            s2 = sgn([J.index(t) for t in [c, d] + efg])
            out = [a, b] + efg
            srt = tuple(sorted(out))
            M[I5[srt], col] += np.real(pv) * s1 * s2 * sgn([out.index(t) for t in srt])
    return M


Hs = np.zeros((252, 252))
for col, I in enumerate(B5):
    comp = tuple(sorted(set(range(N)) - set(I)))
    Hs[I5[comp], col] = sgn(I + comp)
w, U = np.linalg.eig(Hs.astype(complex))
Qm, _ = np.linalg.qr(U[:, np.abs(w + 1j) < 1e-9]); P = Qm.conj().T

basis = direct.singlet_basis()
Ma = contraction_matrix(basis["a"])
comm = float(np.max(np.abs(Ma @ Hs - Hs @ Ma)))
Ssum = np.zeros((126, 126), complex)
for I in B4:
    KA = P @ contraction_matrix({I: 1.0}) @ Qm
    Ssum += KA @ KA.conj().T
ev = np.linalg.eigvalsh(0.5 * (Ssum + Ssum.conj().T))
c = 1 / math.sqrt(ev.mean())


def lift(Mv):
    L = np.zeros((252, 252))
    for col, I in enumerate(B5):
        for pos, i in enumerate(I):
            for j in range(N):
                if Mv[j, i] == 0 or (j in I and j != i):
                    continue
                if j == i:
                    L[col, col] += Mv[j, i]; continue
                new = list(I); new[pos] = j
                L[I5[tuple(sorted(new))], col] += Mv[j, i] * sgn(new)
    return L


g = lambda v: lift(hyp._matrix(v).astype(float))
su3 = [g(v) for v in hyp.su3_colour_integer_basis()]; su2L = [g(v) for v in hyp.SU2L_INTEGER]
Y = -1j * (P @ (g(hyp.Y_STANDARD_INTEGER) / 6) @ Qm)
C3 = -sum(P @ x @ x @ Qm for x in su3); C2 = -sum(P @ (0.5 * x) @ (0.5 * x) @ Qm for x in su2L)


def sub(conds):
    Mt = sum((o - v * np.eye(126)).conj().T @ (o - v * np.eye(126)) for o, v in conds)
    w, V = np.linalg.eigh(0.5 * (Mt + Mt.conj().T)); return V[:, w < 1e-9]


S0 = sub([(C3, 0), (C2, 0), (Y, 0)]); Du = sub([(C3, 0), (C2, .75), (Y, .5)]); Dd = sub([(C3, 0), (C2, .75), (Y, -.5)])
res = {"hodge_commutator": comm, "casimir_spread": float(ev.max() - ev.min()), "c": c}
for name, (p, a, om) in {"Am45": (1, -1, 0), "Ap45": (1, 1, 0), "P": (1, 0, 0), "A": (0, 1, 0), "W": (0, 0, 1)}.items():
    f = direct.add_forms(direct.scale_form(basis["p"], p), direct.scale_form(basis["a"], a), direct.scale_form(basis["omega"], om))
    n = math.sqrt(sum(abs(v) ** 2 for v in f.values())); f = {k: v / n for k, v in f.items()}
    M = c * (P @ contraction_matrix(f) @ Qm)
    kR = float(np.real(S0[:, 0].conj() @ M @ S0[:, 0]))
    ku = float(np.real(np.trace(Du.conj().T @ M @ Du)) / Du.shape[1]); kd = float(np.real(np.trace(Dd.conj().T @ M @ Dd)) / Dd.shape[1])
    spec = np.linalg.eigvalsh(0.5 * (M + M.conj().T))
    lam_max = float(np.max(np.abs(spec)))
    res[name] = {"kR": kR, "ku": ku, "kd": kd, "tau=2sqrt6(kR-kd)": 2 * math.sqrt(6) * (kR - kd),
                 "TrMMdag": float(np.real(np.trace(M @ M.conj().T))), "max|eig|": lam_max,
                 "tau_if_max|eig|_rescaled_to_1": 2 * math.sqrt(6) * (kR - kd) / lam_max}
json.dump(res, open(Path(__file__).with_name("o5_clebsch_check.json"), "w"), indent=1)
print(json.dumps(res, indent=1))
