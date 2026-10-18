"""SKEPTIC (D-C-flavour): exact O5 Clebsch at the intended Am45 orientation.

O5 = S_ij (F_i F_j)_126 (Delta Phi210)_126bar / M_Pl,red.  The 126bar component of Delta x Phi is the unique
SO(10)-equivariant map M_Phi : 126bar -> 126bar, linear in Phi (multiplicity of 210 in 126 x 126bar is 1).
Own construction (no repo tensor code): K_Phi = sum_{a<b<c<d} Phi_abcd (L_ab L_cd - L_ac L_bd + L_ad L_bc),
L_ab = derivation lift of the so(10) generator E_ab to Lambda^5 R^10, restricted to the -i Hodge eigenspace.
Unit-norm CG convention: c^2 sum_A K_A K_A^dag = 1 on 126bar (A over an orthonormal basis of Lambda^4), so every
eigenvalue k' of M = c K_Phihat satisfies |k'| <= 1 (the designer's |tau| <= 9.8 bound = 2 C_R).
The repo is used ONLY for the conventions: the (p, a, omega) unit forms (direct.singlet_basis) and the integer
SM generator bases (g3_sigma_hypercharge_audit_v20), both read-only.
Outputs: k'_R (SM singlet Delta_R), k'_u, k'_d (the two SM doublets of 126bar), tau = 2 sqrt6 (k'_R - k'_d)
as functions of (p, a, omega), at Am45 (p,a,omega) = (1,-1,0)/sqrt2 and the mirror (1,1,0)/sqrt2.
"""
from __future__ import annotations
import itertools, json, math, sys
from pathlib import Path
import numpy as np

REPO = r"C:\Users\jayal\Downloads\So10Theory2\So10Theory\_v22research"
sys.path.insert(0, REPO)
import direct_phi_h_sigmabar_tensor_v20 as direct  # noqa: E402  (conventions only)
import g3_sigma_hypercharge_audit_v20 as hyp  # noqa: E402  (conventions only)

N = 10
B5 = list(itertools.combinations(range(N), 5)); I5 = {t: i for i, t in enumerate(B5)}
B4 = list(itertools.combinations(range(N), 4))


def perm_sign(seq):
    s = 1
    seq = list(seq)
    for i in range(len(seq)):
        for j in range(i + 1, len(seq)):
            if seq[i] > seq[j]:
                s = -s
    return s


def lift(M):
    """Derivation lift of a 10x10 matrix to Lambda^5 (basis e_I, I sorted)."""
    L = np.zeros((len(B5), len(B5)))
    for col, I in enumerate(B5):
        for pos, i in enumerate(I):
            for j in range(N):
                if M[j, i] == 0:
                    continue
                if j in I and j != i:
                    continue
                newI = list(I); newI[pos] = j
                if j == i:
                    L[col, col] += M[j, i]
                    continue
                srt = tuple(sorted(newI))
                L[I5[srt], col] += M[j, i] * perm_sign(newI)
    return L


def E(a, b):
    m = np.zeros((N, N)); m[a, b] = -1.0; m[b, a] = 1.0   # rotation a -> b
    return m


Lab = {(a, b): lift(E(a, b)) for a, b in itertools.combinations(range(N), 2)}

# Hodge star on 5-forms
Hs = np.zeros((len(B5), len(B5)))
for col, I in enumerate(B5):
    comp = tuple(sorted(set(range(N)) - set(I)))
    Hs[I5[comp], col] = perm_sign(I + comp)
w, U = np.linalg.eig(Hs.astype(complex))
minus_i = U[:, np.abs(w + 1j) < 1e-9]
# orthonormal basis of the -i eigenspace
Qm, _ = np.linalg.qr(minus_i)
assert Qm.shape[1] == 126, Qm.shape


def K_of(phi_form):
    K = np.zeros((len(B5), len(B5)))
    for I, val in phi_form.items():
        if abs(val) < 1e-15:
            continue
        a, b, c, d = I
        K += np.real(val) * (Lab[(a, b)] @ Lab[(c, d)] - Lab[(a, c)] @ Lab[(b, d)] + Lab[(a, d)] @ Lab[(b, c)])
    return K


# checks: K commutes with Hodge
basis = direct.singlet_basis()
Ktest = K_of(basis["a"])
assert np.max(np.abs(Ktest @ Hs - Hs @ Ktest)) < 1e-9

# unit-norm CG normalisation: sum_A K_A^2 on 126bar
Ssum = np.zeros((126, 126), complex)
for I in B4:
    KA = Qm.conj().T @ K_of({I: 1.0}) @ Qm
    Ssum += KA @ KA.conj().T
ev = np.linalg.eigvalsh(0.5 * (Ssum + Ssum.conj().T))
assert ev.max() - ev.min() < 1e-8 * ev.max(), (ev.min(), ev.max())
cnorm = 1.0 / math.sqrt(ev.mean())

# SM generators (repo integer conventions) lifted
def gen_matrix(vec):
    return hyp._matrix(vec).astype(float)

su3 = [lift(gen_matrix(v)) for v in hyp.su3_colour_integer_basis()]
su2L = [lift(gen_matrix(v)) for v in hyp.SU2L_INTEGER]
Yg = lift(gen_matrix(hyp.Y_STANDARD_INTEGER)) / 6.0          # Y = (1/6)(-i) Y_STANDARD
T3R = lift(gen_matrix(hyp.T3R_INTEGER)) / 2.0
BL = lift(gen_matrix(hyp.BL_INTEGER)) * (-2.0 / 3.0)
P = Qm.conj().T
C3 = -sum(P @ g @ g @ Qm for g in su3)  # unnormalised colour Casimir (zero <=> singlet)
C2L = -sum(P @ (0.5 * g) @ (0.5 * g) @ Qm for g in su2L)
Yop = -1j * (P @ Yg @ Qm)                                        # Hermitian hypercharge on 126bar
T3Rop = -1j * (P @ T3R @ Qm); BLop = -1j * (P @ BL @ Qm)


def subspace(cond_ops_vals):
    """common eigenspace of commuting Hermitian ops with given values."""
    Mtot = sum((op - val * np.eye(126)).conj().T @ (op - val * np.eye(126)) for op, val in cond_ops_vals)
    w, V = np.linalg.eigh(0.5 * (Mtot + Mtot.conj().T))
    return V[:, w < 1e-9]


sing = subspace([(C3, 0.0), (C2L, 0.0), (Yop, 0.0)])
dup = subspace([(C3, 0.0), (C2L, 0.75), (Yop, 0.5)])
ddn = subspace([(C3, 0.0), (C2L, 0.75), (Yop, -0.5)])
out = {"dims": {"SM singlet": sing.shape[1], "doublet Y=+1/2 (complex dim)": dup.shape[1], "doublet Y=-1/2": ddn.shape[1]},
       "cnorm": cnorm}
# B-L, T3R of the singlet
out["singlet_BL_T3R"] = [float(np.real(sing[:, 0].conj() @ BLop @ sing[:, 0])), float(np.real(sing[:, 0].conj() @ T3Rop @ sing[:, 0]))]


def kprime(p, a, om):
    form = direct.add_forms(direct.scale_form(basis["p"], p), direct.scale_form(basis["a"], a), direct.scale_form(basis["omega"], om))
    nrm = math.sqrt(sum(abs(v) ** 2 for v in form.values()))
    form = {k: v / nrm for k, v in form.items()}
    M = cnorm * (P @ K_of(form) @ Qm)
    res = {}
    for name, sub in (("R", sing), ("u(Y=+1/2)", dup), ("d(Y=-1/2)", ddn)):
        blk = sub.conj().T @ M @ sub
        e = np.linalg.eigvalsh(0.5 * (blk + blk.conj().T))
        # M must act as a scalar on each SM irrep sub-block
        res[name] = {"eig": [round(float(x), 12) for x in e], "spread": float(e.max() - e.min())}
        # leakage out of the block (equivariance check)
        leak = np.linalg.norm(M @ sub - sub @ blk)
        res[name]["leak"] = float(leak)
    kR = res["R"]["eig"][0]; ku = float(np.mean(res["u(Y=+1/2)"]["eig"])); kd = float(np.mean(res["d(Y=-1/2)"]["eig"]))
    CR = 2 * math.sqrt(6)
    res["tau_vs_u"] = CR * (kR - ku); res["tau_vs_d"] = CR * (kR - kd)
    full = np.linalg.eigvalsh(0.5 * (M + M.conj().T))
    res["M_spectrum_minmax"] = [float(full.min()), float(full.max())]
    return res


points = {"P (1,0,0)": (1, 0, 0), "A (0,1,0)": (0, 1, 0), "W (0,0,1)": (0, 0, 1),
          "Am45 (1,-1,0)/sqrt2 [design]": (1, -1, 0), "Ap45 (1,1,0)/sqrt2 [mirror]": (1, 1, 0),
          "SMa (0.5,-0.5,0.707)": (0.5, -0.5, 0.70710678), "SMe (0.693,-0.693,0.2)": (0.693, -0.693, 0.2)}
out["points"] = {k: kprime(*v) for k, v in points.items()}
# tau along the (p, a) circle at omega = 0
scan = []
for th in np.linspace(0, 2 * math.pi, 73):
    r = kprime(math.cos(th), math.sin(th), 0.0)
    scan.append([round(math.degrees(th), 1), r["tau_vs_d"]])
out["tau_circle_omega0"] = scan
json.dump(out, open(Path(__file__).with_name("o5_clebsch.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "tau_circle_omega0"}, indent=1))
print("tau(theta) omega=0:", scan[::6])
