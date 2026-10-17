"""K4 toolkit: exact/fast algebra of the real SO(10) 210 = Lambda^4(R^10).

Self-contained (no repo imports).  Conventions:
  * basis index I <-> sorted 4-tuple (i<j<k<l); Phi is a length-210 vector.
  * A(Phi): symmetric 45x45 matrix on 2-forms, A_[ab],[cd] = Phi_abcd (with sign).
  * M(Phi) = Hodge-star(Phi ^ Phi): a 2-form (45 components).
  * S(Phi)_ij = sum_{a<b<c} Phi_iabc Phi_jabc: symmetric 10x10.
  * invariants: I2 = Phi.Phi, I3 = tr A^3, Ja = I2^2, Jb = tr A^4, Jc = |M|^2, Jd = tr S^2.
Everything is built from integer sparse tensors, so exact (Fraction/object) evaluation is
possible by passing object arrays; float evaluation is fast.
"""
from __future__ import annotations

import itertools
from fractions import Fraction

import numpy as np
from scipy import sparse

N = 10
FOUR = tuple(itertools.combinations(range(N), 4))
FOUR_INDEX = {t: i for i, t in enumerate(FOUR)}
TWO = tuple(itertools.combinations(range(N), 2))
TWO_INDEX = {t: i for i, t in enumerate(TWO)}
THREE = tuple(itertools.combinations(range(N), 3))
THREE_INDEX = {t: i for i, t in enumerate(THREE)}
DIM = len(FOUR)  # 210


def perm_sign(seq) -> int:
    s = 1
    seq = list(seq)
    for i in range(len(seq)):
        for j in range(i + 1, len(seq)):
            if seq[i] > seq[j]:
                s = -s
    return s


def sorted_with_sign(seq):
    """Return (sorted tuple, sign) or (None, 0) if repeated indices."""
    if len(set(seq)) != len(seq):
        return None, 0
    return tuple(sorted(seq)), perm_sign(seq)


# ----------------------------------------------------------------------------
# Generators L_ab = e_a ^ i_b - e_b ^ i_a   (integer 210x210 matrices)
# ----------------------------------------------------------------------------
def _interior_terms(indices, b):
    """i_b e_{indices}: returns (reduced tuple, sign) or None."""
    if b not in indices:
        return None
    pos = indices.index(b)
    reduced = indices[:pos] + indices[pos + 1:]
    return reduced, (-1) ** pos


def generator(a: int, b: int) -> sparse.csr_matrix:
    rows, cols, vals = [], [], []
    for col, t in enumerate(FOUR):
        # e_a ^ i_b t
        r = _interior_terms(t, b)
        if r is not None:
            red, sg = r
            st, s2 = sorted_with_sign((a,) + red)
            if st is not None:
                rows.append(FOUR_INDEX[st]); cols.append(col); vals.append(sg * s2)
        r = _interior_terms(t, a)
        if r is not None:
            red, sg = r
            st, s2 = sorted_with_sign((b,) + red)
            if st is not None:
                rows.append(FOUR_INDEX[st]); cols.append(col); vals.append(-sg * s2)
    return sparse.csr_matrix((vals, (rows, cols)), shape=(DIM, DIM), dtype=np.int64)


_GENS = None


def generators():
    global _GENS
    if _GENS is None:
        _GENS = tuple(generator(a, b) for a, b in TWO)
    return _GENS


# ----------------------------------------------------------------------------
# Linear map Phi -> A (45x45 symmetric), as sparse 2025x210 integer matrix
# ----------------------------------------------------------------------------
def _build_LA():
    rows, cols, vals = [], [], []
    for r, (a, b) in enumerate(TWO):
        for c, (cc, d) in enumerate(TWO):
            st, sg = sorted_with_sign((a, b, cc, d))
            if st is None:
                continue
            rows.append(r * 45 + c); cols.append(FOUR_INDEX[st]); vals.append(sg)
    return sparse.csr_matrix((vals, (rows, cols)), shape=(45 * 45, DIM), dtype=np.int64)


LA = _build_LA()
LA_T = LA.T.tocsr()


def A_matrix(phi):
    """45x45 symmetric matrix; works for float and object arrays."""
    if phi.dtype == object:
        out = np.zeros((45, 45), dtype=object)
        out[:] = Fraction(0)
        coo = LA.tocoo()
        for r, c, v in zip(coo.row, coo.col, coo.data):
            out[r // 45, r % 45] += int(v) * phi[c]
        return out
    return (LA @ phi).reshape(45, 45)


def A_to_phi_dual(mat):
    """LA^T vec(mat): the 210-vector of d<mat, A(Phi)>/dPhi  (mat 45x45)."""
    if mat.dtype == object:
        out = np.zeros(DIM, dtype=object)
        out[:] = Fraction(0)
        coo = LA.tocoo()
        for r, c, v in zip(coo.row, coo.col, coo.data):
            out[c] += int(v) * mat[r // 45, r % 45]
        return out
    return LA_T @ mat.reshape(-1)


# ----------------------------------------------------------------------------
# Quadratic covariants: M_[ij] = Phi^T B_[ij] Phi ; S_(ij) = Phi^T C_(ij) Phi
# ----------------------------------------------------------------------------
def _build_B():
    """Hodge star of Phi^Phi.  (Phi^Phi)_{K L} with K,L 4-subsets; star gives 2-form."""
    out = []
    full = set(range(N))
    for (i, j) in TWO:
        comp = tuple(sorted(full - {i, j}))  # 8 indices
        rows, cols, vals = [], [], []
        seen = set()
        for K in itertools.combinations(comp, 4):
            L = tuple(sorted(set(comp) - set(K)))
            key = (K, L) if K < L else (L, K)
            if key in seen:
                continue
            seen.add(key)
            # Phi^Phi component on the 8-form e_{K+L}: sign(K+L -> sorted comp) ; two orderings (K,L),(L,K) equal
            # (4-forms commute), so the coefficient of e_comp in Phi^Phi is 2*sign*Phi_K Phi_L (K != L always).
            sg8 = perm_sign(K + L)
            # Hodge: *(e_comp) = sign(comp + (i,j)) e_{ij}
            sgh = perm_sign(comp + (i, j))
            v = 2 * sg8 * sgh
            rows.append(FOUR_INDEX[K]); cols.append(FOUR_INDEX[L]); vals.append(v)
            rows.append(FOUR_INDEX[L]); cols.append(FOUR_INDEX[K]); vals.append(v)
        out.append(sparse.csr_matrix((vals, (rows, cols)), shape=(DIM, DIM), dtype=np.int64) * 0.5)
    # each B symmetric with B[K,L] = B[L,K] = v/2 so that Phi^T B Phi = sum_{K!=L unordered} v Phi_K Phi_L
    return tuple(b.tocsr() for b in out)


def _build_C():
    out = {}
    for i in range(N):
        for j in range(i, N):
            rows, cols, vals = [], [], []
            for abc in THREE:
                if i in abc or j in abc:
                    continue
                si, sgi = sorted_with_sign((i,) + abc)
                sj, sgj = sorted_with_sign((j,) + abc)
                v = sgi * sgj
                if i == j:
                    rows.append(FOUR_INDEX[si]); cols.append(FOUR_INDEX[sj]); vals.append(v)
                else:
                    rows.append(FOUR_INDEX[si]); cols.append(FOUR_INDEX[sj]); vals.append(v)
                    rows.append(FOUR_INDEX[sj]); cols.append(FOUR_INDEX[si]); vals.append(v)
            m = sparse.csr_matrix((vals, (rows, cols)), shape=(DIM, DIM), dtype=float)
            if i != j:
                m = m * 0.5
            out[(i, j)] = m.tocsr()
    return out


B_LIST = _build_B()          # 45 symmetric sparse matrices (float, half-integers)
C_DICT = _build_C()          # 55 symmetric sparse matrices
C_LIST = tuple(C_DICT[(i, j)] for i in range(N) for j in range(i, N))
C_PAIRS = tuple((i, j) for i in range(N) for j in range(i, N))


def quad_form(Bm, phi):
    if phi.dtype == object:
        coo = Bm.tocoo()
        tot = Fraction(0)
        for r, c, v in zip(coo.row, coo.col, coo.data):
            tot += Fraction(v).limit_denominator(4) * phi[r] * phi[c]
        return tot
    return float(phi @ (Bm @ phi))


def M_vector(phi):
    if phi.dtype == object:
        out = np.array([quad_form(b, phi) for b in B_LIST], dtype=object)
        return out
    return np.array([phi @ (b @ phi) for b in B_LIST])


def S_matrix(phi):
    if phi.dtype == object:
        S = np.zeros((N, N), dtype=object); S[:] = Fraction(0)
        for (i, j), c in C_DICT.items():
            v = quad_form(c, phi)
            S[i, j] = v; S[j, i] = v
        return S
    S = np.zeros((N, N))
    for (i, j), c in C_DICT.items():
        v = float(phi @ (c @ phi))
        S[i, j] = v; S[j, i] = v
    return S


# ----------------------------------------------------------------------------
# Gauge-mass quadratic covariant G_AB = <T_A Phi, T_B Phi>  (Sym^2(45) = 1+54+210+770)
# and the quartic Je = sum_AB G_AB^2  (= repo pair-Casimir moment M2)
# ----------------------------------------------------------------------------
_TT = None


def tt_pairs():
    """Symmetrised products  T_A^T T_B + T_B^T T_A  for A<=B (sparse int64)."""
    global _TT
    if _TT is None:
        gens = generators()
        out = {}
        for i in range(45):
            for j in range(i, 45):
                m = gens[i].T @ gens[j] + gens[j].T @ gens[i]
                out[(i, j)] = m.tocsr()
        _TT = out
    return _TT


def gram_tangents(phi):
    gens = generators()
    if phi.dtype == object:
        tans = exact_tangent_matrix(phi)
        G = np.zeros((45, 45), dtype=object)
        for i in range(45):
            for j in range(i, 45):
                v = sum(x * y for x, y in zip(tans[i], tans[j]))
                G[i, j] = v; G[j, i] = v
        return G
    T = np.column_stack([g @ phi for g in gens])
    return T.T @ T


def Je_value(phi):
    G = gram_tangents(phi)
    if phi.dtype == object:
        return sum(G[i, j] * G[i, j] for i in range(45) for j in range(45))
    return float(np.sum(G * G))


def Je_grad(phi):
    G = gram_tangents(phi)
    g = np.zeros(DIM)
    for (i, j), m in tt_pairs().items():
        w = G[i, j] * (1.0 if i == j else 2.0)
        if w != 0.0:
            g += (2.0 * w) * (m @ phi)
    return g


def Je_hessian(phi):
    G = gram_tangents(phi)
    H = np.zeros((DIM, DIM))
    for (i, j), m in tt_pairs().items():
        w = 1.0 if i == j else 2.0
        mp = m @ phi
        H += w * 2.0 * np.outer(mp, mp)
        if G[i, j] != 0.0:
            H += w * 2.0 * G[i, j] * m.toarray()
    return H


# ----------------------------------------------------------------------------
# Invariants, gradients, Hessians
# ----------------------------------------------------------------------------
def invariants(phi):
    """dict with I2, I3, Ja, Jb, Jc, Jd (exact if phi is an object array of Fractions/ints)."""
    A = A_matrix(phi)
    if phi.dtype == object:
        I2 = sum(x * x for x in phi)
        A2 = A.dot(A); A3 = A2.dot(A)
        I3 = sum(A3[i, i] for i in range(45))
        Jb = sum((A2.dot(A2))[i, i] for i in range(45))
        M = M_vector(phi)
        Jc = sum(m * m for m in M)
        S = S_matrix(phi)
        Jd = sum(S[i, j] * S[i, j] for i in range(N) for j in range(N))
        return {"I2": I2, "I3": I3, "Ja": I2 * I2, "Jb": Jb, "Jc": Jc, "Jd": Jd, "Je": Je_value(phi)}
    I2 = float(phi @ phi)
    A2 = A @ A
    I3 = float(np.trace(A2 @ A))
    Jb = float(np.sum(A2 * A2))
    M = M_vector(phi)
    Jc = float(M @ M)
    S = S_matrix(phi)
    Jd = float(np.sum(S * S))
    return {"I2": I2, "I3": I3, "Ja": I2 * I2, "Jb": Jb, "Jc": Jc, "Jd": Jd, "Je": Je_value(phi)}


NAMES = ("I2", "I3", "Ja", "Jb", "Jc", "Jd", "Je")
BASIS = ("I2", "I3", "Ja", "Jb", "Jc", "Je")   # independent set used for potentials


def value_grad(phi, coeff):
    """V = c_I2*I2 + c_I3*I3 + c_Ja*Ja + ... ; returns (V, grad) in float."""
    phi = np.asarray(phi, dtype=float)
    A = A_matrix(phi)
    A2 = A @ A
    A3 = A2 @ A
    I2 = float(phi @ phi)
    I3 = float(np.trace(A3))
    Jb = float(np.sum(A2 * A2))
    M = M_vector(phi)
    Jc = float(M @ M)
    S = S_matrix(phi)
    Jd = float(np.sum(S * S))
    cJd = coeff.get("Jd", 0.0)
    cJe = coeff.get("Je", 0.0)
    Je = Je_value(phi) if cJe != 0.0 else 0.0
    V = coeff["I2"] * I2 + coeff["I3"] * I3 + coeff["Ja"] * I2 ** 2 + coeff["Jb"] * Jb + coeff["Jc"] * Jc + cJd * Jd + cJe * Je
    g = 2.0 * coeff["I2"] * phi
    g = g + coeff["I3"] * 3.0 * (LA_T @ A2.reshape(-1))
    g = g + coeff["Ja"] * 4.0 * I2 * phi
    g = g + coeff["Jb"] * 4.0 * (LA_T @ A3.reshape(-1))
    if coeff["Jc"] != 0.0:
        gm = np.zeros(DIM)
        for mk, b in zip(M, B_LIST):
            if mk != 0.0:
                gm += (4.0 * mk) * (b @ phi)
        g = g + coeff["Jc"] * gm
    if cJe != 0.0:
        g = g + cJe * Je_grad(phi)
    if cJd != 0.0:
        gs = np.zeros(DIM)
        for (i, j), c in zip(C_PAIRS, C_LIST):
            sij = S[i, j]
            if sij != 0.0:
                mult = 1.0 if i == j else 2.0
                gs += (4.0 * mult * sij) * (c @ phi)
        g = g + cJd * gs
    return V, g


def hessian(phi, coeff):
    """Exact-structure Hessian (float).  210x210."""
    phi = np.asarray(phi, dtype=float)
    A = A_matrix(phi)
    A2 = A @ A
    I2 = float(phi @ phi)
    H = 2.0 * coeff["I2"] * np.eye(DIM)
    H += coeff["Ja"] * (8.0 * np.outer(phi, phi) + 4.0 * I2 * np.eye(DIM))
    # basis matrices E_I = LA e_I  (as dense 45x45) -- build once
    E = LA.toarray().reshape(45, 45, DIM).transpose(2, 0, 1).astype(float)  # (210,45,45)
    if coeff["I3"] != 0.0 or coeff["Jb"] != 0.0:
        # d/dPhi_J of 3 tr(E_I A^2) = 3 tr(E_I E_J A + E_I A E_J)
        # d/dPhi_J of 4 tr(E_I A^3) = 4 tr(E_I (E_J A^2 + A E_J A + A^2 E_J))
        EA = np.einsum("iab,bc->iac", E, A)       # E_I A
        AE = np.einsum("ab,ibc->iac", A, E)       # A E_I
        EA2 = np.einsum("iab,bc->iac", E, A2)
        if coeff["I3"] != 0.0:
            t1 = np.einsum("iab,jba->ij", EA, E)  # tr(E_I A E_J)
            t2 = np.einsum("iab,jba->ij", E, AE)  # tr(E_I E_J A) = tr(E_I (A E_J)^T?) careful
            # tr(E_I E_J A) = sum_{ab,bc,ca} E_I[a,b] E_J[b,c] A[c,a] = einsum('iab,jbc,ca')
            t2 = np.einsum("iab,jbc,ca->ij", E, E, A, optimize=True)
            H += coeff["I3"] * 3.0 * (t1 + t2)
        if coeff["Jb"] != 0.0:
            u1 = np.einsum("iab,jbc,ca->ij", E, E, A2, optimize=True)   # tr(E_I E_J A^2)
            u2 = np.einsum("iab,jbc,ca->ij", EA, E, A, optimize=True)   # tr(E_I A E_J A)
            u3 = np.einsum("iab,jba->ij", EA2, E)                        # tr(E_I A^2 E_J)
            H += coeff["Jb"] * 4.0 * (u1 + u2 + u3)
    if coeff["Jc"] != 0.0:
        M = M_vector(phi)
        Hc = np.zeros((DIM, DIM))
        for mk, b in zip(M, B_LIST):
            bp = b @ phi
            Hc += 8.0 * np.outer(bp, bp)
            if mk != 0.0:
                Hc += 4.0 * mk * b.toarray()
        H += coeff["Jc"] * Hc
    if coeff.get("Je", 0.0) != 0.0:
        H += coeff["Je"] * Je_hessian(phi)
    if coeff.get("Jd", 0.0) != 0.0:
        S = S_matrix(phi)
        Hd = np.zeros((DIM, DIM))
        for (i, j), c in zip(C_PAIRS, C_LIST):
            mult = 1.0 if i == j else 2.0
            cp = c @ phi
            Hd += mult * 8.0 * np.outer(cp, cp)
            if S[i, j] != 0.0:
                Hd += mult * 4.0 * S[i, j] * c.toarray()
        H += coeff["Jd"] * Hd
    return 0.5 * (H + H.T)


# ----------------------------------------------------------------------------
# (p, a, omega) singlet forms (integer components, unnormalised)
# ----------------------------------------------------------------------------
def form_vector(terms, dtype=float):
    """terms: dict {4-tuple(any order): coeff}"""
    v = np.zeros(DIM, dtype=dtype)
    if dtype == object:
        v[:] = Fraction(0)
    for t, c in terms.items():
        st, sg = sorted_with_sign(t)
        v[FOUR_INDEX[st]] += sg * c
    return v


P_TERMS = {(6, 7, 8, 9): 1}
A_TERMS = {(0, 1, 2, 3): 1, (0, 1, 4, 5): 1, (2, 3, 4, 5): 1}         # *_6 J, J = e01+e23+e45
W_TERMS = {(0, 1, 6, 7): 1, (0, 1, 8, 9): 1, (2, 3, 6, 7): 1, (2, 3, 8, 9): 1, (4, 5, 6, 7): 1, (4, 5, 8, 9): 1}  # J ^ (e67+e89)


def pao_vector(p, a, w, dtype=float):
    v = form_vector(P_TERMS, dtype) * p + form_vector(A_TERMS, dtype) * a + form_vector(W_TERMS, dtype) * w
    return v


def stabilizer(phi, tol=1e-12):
    """Return (list of unbroken generator labels, tangent matrix 210 x n_broken)."""
    unb, tangents = [], []
    for (a, b), g in zip(TWO, generators()):
        t = g @ phi
        if np.linalg.norm(t) < tol:
            unb.append((a, b))
        else:
            tangents.append(t)
    return unb, np.column_stack(tangents) if tangents else np.zeros((DIM, 0))


def exact_tangent_matrix(phi_obj):
    """Exact (object) tangent vectors g.phi for all 45 generators -> list."""
    out = []
    for g in generators():
        coo = g.tocoo()
        t = np.zeros(DIM, dtype=object); t[:] = Fraction(0)
        for r, c, v in zip(coo.row, coo.col, coo.data):
            t[r] += int(v) * phi_obj[c]
        out.append(t)
    return out
