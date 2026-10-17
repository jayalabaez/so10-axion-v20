"""Independent 210-sector machinery for the K3 verification (verifier's own code).

Real 210 = Lambda^4(R^10), basis e_I, I in combinations(range(10),4) (same ordering as the repo chart's PHI block,
which is just the natural lexicographic ordering).  Generators L_ab (a<b) act as derivations with L_ab e_b = e_a,
L_ab e_a = -e_b.  The six renormalisable self-invariants: I2 = |Phi|^2, I3 = Tr(A_Phi^3) (unique cubic), and the four
pair-Casimir moments J_d = <Phi x Phi, K^d Phi x Phi>, d = 0,2,3,4 (K = sum_{a<b} L_ab x L_ab).  Hessians are exact
(analytic), validated by 5-point finite differences in check210.py.
"""
from __future__ import annotations
import itertools
import numpy as np
import scipy.sparse as sp

N = 10
IDX4 = list(itertools.combinations(range(N), 4))
POS4 = {I: i for i, I in enumerate(IDX4)}
IDX2 = list(itertools.combinations(range(N), 2))
POS2 = {I: i for i, I in enumerate(IDX2)}
DIM = len(IDX4)  # 210


def perm_sign(seq):
    seq = list(seq)
    s = 1
    for i in range(len(seq)):
        for j in range(i + 1, len(seq)):
            if seq[i] > seq[j]:
                s = -s
    return s


def gen4(a: int, b: int) -> sp.csr_matrix:
    """210x210 matrix of L_ab on 4-forms (L_ab e_b = e_a, L_ab e_a = -e_b)."""
    rows, cols, vals = [], [], []
    for j, I in enumerate(IDX4):
        for k, c in enumerate(I):
            if c == b:
                new, s = a, +1
            elif c == a:
                new, s = b, -1
            else:
                continue
            if new in I:
                continue
            J = list(I)
            J[k] = new
            sign = perm_sign(J)
            rows.append(POS4[tuple(sorted(J))]); cols.append(j); vals.append(s * sign)
    return sp.csr_matrix((vals, (rows, cols)), shape=(DIM, DIM), dtype=float)


_GENS = None


def generators():
    """Tuple of the 45 sparse generators in the order of IDX2."""
    global _GENS
    if _GENS is None:
        _GENS = tuple(gen4(a, b) for a, b in IDX2)
    return _GENS


_K = None


def pair_casimir() -> sp.csr_matrix:
    global _K
    if _K is None:
        K = sp.csr_matrix((DIM * DIM, DIM * DIM), dtype=float)
        for T in generators():
            K = K + sp.kron(T, T, format="csr")
        _K = K.tocsr()
    return _K


# ---------------------------------------------------------------- forms in the 210 basis
def form_vector(form: dict) -> np.ndarray:
    v = np.zeros(DIM)
    for I, c in form.items():
        v[POS4[tuple(I)]] = float(np.real(c))
    return v


def wedge_basis(indices):
    """unit vector of e_{i1}^...^e_{i4} for a (possibly unsorted) index tuple with sign."""
    v = np.zeros(DIM)
    v[POS4[tuple(sorted(indices))]] = perm_sign(indices)
    return v


def singlet_forms():
    """p = e6789, a = *_6 (e01+e23+e45) = e2345 + e0145 + e0123, omega = (e01+e23+e45)^(e67+e89); unit norm."""
    p = wedge_basis((6, 7, 8, 9))
    a = wedge_basis((2, 3, 4, 5)) + wedge_basis((0, 1, 4, 5)) + wedge_basis((0, 1, 2, 3))
    om = np.zeros(DIM)
    for (i, j) in ((0, 1), (2, 3), (4, 5)):
        for (k, l) in ((6, 7), (8, 9)):
            om += wedge_basis((i, j, k, l))
    return {"p": p / np.linalg.norm(p), "a": a / np.linalg.norm(a), "omega": om / np.linalg.norm(om)}


# ---------------------------------------------------------------- invariants: values, gradients, Hessians
def _apply_Kd(K, X, d):
    for _ in range(d):
        X = K @ X
    return X


def moment_values(phi: np.ndarray, degrees=(0, 2, 3, 4)) -> dict:
    K = pair_casimir()
    pair = np.kron(phi, phi)
    out = {}
    cur = pair
    for d in range(0, max(degrees) + 1):
        if d > 0:
            cur = K @ cur
        if d in degrees:
            out[d] = float(pair @ cur)
    return out


def moment_gradients(phi: np.ndarray, degrees=(0, 2, 3, 4)) -> dict:
    K = pair_casimir()
    pair = np.kron(phi, phi)
    out = {}
    cur = pair
    for d in range(0, max(degrees) + 1):
        if d > 0:
            cur = K @ cur
        if d in degrees:
            out[d] = 4.0 * (cur.reshape(DIM, DIM) @ phi)
    return out


def moment_hessians(phi: np.ndarray, degrees=(0, 2, 3, 4)) -> dict:
    """H_d = 4 A_d + 4 (B_d + B'_d), A_d = mat(K^d phi x phi), B_d = (I x phi)^T K^d (I x phi), B'_d = (phi x I)^T K^d (I x phi)."""
    K = pair_casimir()
    pair = np.kron(phi, phi)
    X = np.kron(np.eye(DIM), phi[:, None])      # (I x phi): column m = e_m x phi
    Xp = np.kron(phi[:, None], np.eye(DIM))     # (phi x I): column m = phi x e_m
    out = {}
    cur_pair, cur_X = pair, X
    for d in range(0, max(degrees) + 1):
        if d > 0:
            cur_pair = K @ cur_pair
            cur_X = K @ cur_X
        if d in degrees:
            A = cur_pair.reshape(DIM, DIM)
            B = X.T @ cur_X
            Bp = Xp.T @ cur_X
            H = 4.0 * A + 4.0 * (B + Bp)
            out[d] = 0.5 * (H + H.T)
    return out


# cubic Tr(A_Phi^3), (A_Phi)_{[ab],[cd]} = Phi_abcd
_E = None


def cubic_E():
    """E_m: 45x45 symmetric matrices with A_Phi = sum_m Phi_m E_m; returned as dense (210,45,45) and flattened sparse."""
    global _E
    if _E is None:
        E = np.zeros((DIM, 45, 45))
        for m, (i, j, k, l) in enumerate(IDX4):
            for (pq, rs, seq) in (((i, j), (k, l), (i, j, k, l)), ((i, k), (j, l), (i, k, j, l)), ((i, l), (j, k), (i, l, j, k))):
                s = perm_sign(seq)
                E[m, POS2[pq], POS2[rs]] = s
                E[m, POS2[rs], POS2[pq]] = s
        _E = E
    return _E


def A_matrix(phi):
    return np.tensordot(phi, cubic_E(), axes=(0, 0))


def cubic_value(phi):
    A = A_matrix(phi)
    return float(np.trace(A @ A @ A))


def cubic_gradient(phi):
    A = A_matrix(phi)
    A2 = A @ A
    E = cubic_E()
    return 3.0 * np.einsum("mxy,yx->m", E, A2)


def cubic_hessian(phi):
    A = A_matrix(phi)
    E = cubic_E()
    EA = np.einsum("mxy,yz->mxz", E, A)             # E_m A
    H = 6.0 * np.einsum("mxz,nzx->mn", EA, E)        # Tr(E_m A E_n)
    return 0.5 * (H + H.T)


def all_hessians(phi):
    """dict name -> Hessian for the six self-couplings: I2, I3, J0, J2, J3, J4."""
    out = {"I2": 2.0 * np.eye(DIM), "I3": cubic_hessian(phi)}
    for d, H in moment_hessians(phi).items():
        out[f"J{d}"] = H
    return out


def all_gradients(phi):
    out = {"I2": 2.0 * phi, "I3": cubic_gradient(phi)}
    for d, g in moment_gradients(phi).items():
        out[f"J{d}"] = g
    return out


def all_values(phi):
    out = {"I2": float(phi @ phi), "I3": cubic_value(phi)}
    for d, v in moment_values(phi).items():
        out[f"J{d}"] = v
    return out


NAMES = ("I2", "I3", "J0", "J2", "J3", "J4")


# ---------------------------------------------------------------- G3221 = SU(3) x SU(2)_L x SU(2)_R x U(1)_{B-L}
def so_matrix(M6: np.ndarray, offset: int = 0) -> sp.csr_matrix:
    """210 rep of the antisymmetric matrix M (acting on indices offset..offset+n-1): sum_{a<b} M_ab L_ab."""
    T = sp.csr_matrix((DIM, DIM), dtype=float)
    n = M6.shape[0]
    G = generators()
    for a in range(n):
        for b in range(a + 1, n):
            if abs(M6[a, b]) > 0:
                T = T + M6[a, b] * G[POS2[(a + offset, b + offset)]]
    return T


def g3221_generators():
    """Return dict with lists of sparse 210 generators: su3 (8), u1 (1, B-L normalised: vector 6 has |B-L| = 2/3),
    su2L (3), su2R (3), normalised so that Casimirs are the standard j(j+1), C_3(3) = 4/3."""
    # complex structure on R^6: J e_{2k} = e_{2k+1}
    J = np.zeros((6, 6))
    for k in range(3):
        J[2 * k + 1, 2 * k] = 1.0
        J[2 * k, 2 * k + 1] = -1.0
    # basis of so(6): antisymmetric E_ab
    basis = []
    for a in range(6):
        for b in range(a + 1, 6):
            M = np.zeros((6, 6)); M[a, b] = 1.0; M[b, a] = -1.0
            basis.append(M)
    # commutant with J
    C = np.array([(M @ J - J @ M).ravel() for M in basis]).T  # 36 x 15
    u, s, vt = np.linalg.svd(C)
    null = vt[np.sum(s > 1e-10):]  # rows: combinations of basis with [M,J] = 0
    u3 = [sum(c * M for c, M in zip(row, basis)) for row in null]
    assert len(u3) == 9, len(u3)
    # B-L generator proportional to J; su(3) = combinations orthogonal to J under the trace form
    Jn = J / np.sqrt(np.sum(J * J))
    su3 = []
    for M in u3:
        M2 = M - np.sum(M * Jn) * Jn
        su3.append(M2)
    # orthonormalise su3 under -Tr(MN)/2
    mats = []
    for M in su3:
        for P in mats:
            M = M - (np.sum(M * P) / np.sum(P * P)) * P
        if np.sqrt(np.sum(M * M)) > 1e-8:
            mats.append(M / np.sqrt(np.sum(M * M)))
    assert len(mats) == 8, len(mats)
    # normalise so that on the vector 6 the su(3) Casimir is 4/3: C = -sum_i (c M_i)^2 restricted to 6 -> fix c
    Cv = -sum(M @ M for M in mats)
    ev = np.linalg.eigvalsh(Cv)
    # all six vector states are in 3 or 3bar: eigenvalues equal; scale
    c3 = np.sqrt((4.0 / 3.0) / ev[0])
    su3_mats = [c3 * M for M in mats]
    # B-L: on the 6, eigenvalue of -(c J)^2 should be (2/3)^2
    evJ = np.linalg.eigvalsh(-J @ J)
    cJ = np.sqrt((2.0 / 3.0) ** 2 / evJ[0])
    bl_mat = cJ * J
    # so(4) on 6..9: self-dual (R) and anti-self-dual (L) combinations
    def E4(a, b):
        M = np.zeros((4, 4)); M[a, b] = 1.0; M[b, a] = -1.0; return M
    sd = [E4(0, 1) + E4(2, 3), E4(0, 2) - E4(1, 3), E4(0, 3) + E4(1, 2)]
    asd = [E4(0, 1) - E4(2, 3), E4(0, 2) + E4(1, 3), E4(0, 3) - E4(1, 2)]
    # normalise: on the 4, Casimir 3/4
    def norm_su2(ms):
        Cv = -sum(M @ M for M in ms)
        ev = np.linalg.eigvalsh(Cv)
        c = np.sqrt(0.75 / ev[0])
        return [c * M for M in ms]
    sd = norm_su2(sd); asd = norm_su2(asd)
    out = {
        "su3": [so_matrix(M, 0) for M in su3_mats],
        "u1": [so_matrix(bl_mat, 0)],
        "su2R": [so_matrix(M, 6) for M in sd],
        "su2L": [so_matrix(M, 6) for M in asd],
    }
    return out


def casimirs(gens=None):
    gens = gens or g3221_generators()
    def cas(ms):
        C = sp.csr_matrix((DIM, DIM), dtype=float)
        for T in ms:
            C = C - T @ T
        return C.toarray()
    return {"C3": cas(gens["su3"]), "CL": cas(gens["su2L"]), "CR": cas(gens["su2R"]), "Q2": cas(gens["u1"])}


def isotypic_blocks(cas=None, seed=0, tol=1e-7):
    """Simultaneous eigenspaces of (C3, CL, CR, Q2) on the real 210: list of (label, orthonormal basis (210,k))."""
    cas = cas or casimirs()
    rng = np.random.default_rng(seed)
    w = rng.normal(size=4)
    Mix = w[0] * cas["C3"] + w[1] * cas["CL"] + w[2] * cas["CR"] + w[3] * cas["Q2"]
    ev, U = np.linalg.eigh(0.5 * (Mix + Mix.T))
    # cluster
    blocks = []
    start = 0
    for i in range(1, DIM + 1):
        if i == DIM or abs(ev[i] - ev[start]) > 1e-6:
            B = U[:, start:i]
            lab = tuple(round(float(np.trace(B.T @ cas[k] @ B) / B.shape[1]), 6) for k in ("C3", "CL", "CR", "Q2"))
            blocks.append((lab, B))
            start = i
    # merge blocks with identical labels (random mix might split by accident: it cannot, but be safe)
    merged = {}
    for lab, B in blocks:
        merged.setdefault(lab, []).append(B)
    out = []
    for lab, Bs in merged.items():
        B = np.hstack(Bs)
        out.append((lab, B))
    return out


def irrep_name(lab):
    C3, CL, CR, Q2 = lab
    col = {0.0: "1", 1.333333: "3", 3.0: "8", 3.333333: "6"}.get(round(C3, 6), f"C3={C3}")
    dl = {0.0: "1", 0.75: "2", 2.0: "3"}.get(round(CL, 6), f"CL={CL}")
    dr = {0.0: "1", 0.75: "2", 2.0: "3"}.get(round(CR, 6), f"CR={CR}")
    q = np.sqrt(max(Q2, 0.0))
    return f"({col},{dl},{dr})_|B-L|={q:.4g}"


def goldstone_matrix(phi):
    return np.column_stack([T @ phi for T in generators()])


def complement_in_block(B, G, tol=1e-9):
    """orthonormal basis of the part of span(B) orthogonal to span(G) (G = Goldstone directions)."""
    if G.shape[1] == 0:
        return B
    # project Goldstones into the block
    P = B.T @ G
    u, s, vt = np.linalg.svd(P, full_matrices=True)
    r = int(np.sum(s > tol))
    return B @ u[:, r:]


def gauge_mass_matrix(phi, g=1.0):
    """M^2_AB = (g^2/2) (L_A phi).(L_B phi): T(10)=1 normalisation (T_A = L_A/sqrt2)."""
    G = goldstone_matrix(phi)
    return 0.5 * g * g * (G.T @ G)
