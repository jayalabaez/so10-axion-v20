"""Explicit SO(10)-covariants of the 210 of degree <= 3 (exact integer arithmetic on dense tensors).

A 4-form Phi is stored dense as an antisymmetric int64 array T[a,b,c,d] (10^4 entries).
Covariants return dense tensors in the target irrep's natural index space:
  * 'F4' : 4-form valued (210)        -> antisymmetric rank-4 tensor
  * 'F2' : 2-form valued (45)         -> antisymmetric 10x10
  * 'S2' : symmetric 10x10 (54 + 1)   -> symmetric 10x10 (trace part belongs to the trivial channel)
  * 'SC' : scalar (1)
Epsilon-type covariants are built with exterior-algebra dictionaries (sparse forms) and the Hodge star.
"""
from __future__ import annotations
import itertools
from collections import defaultdict
import numpy as np
import k4lib as K

N = 10
EPS = None


def dense(phi):
    """length-210 vector -> antisymmetric 10^4 tensor (int64, or object for Fraction input)."""
    obj = isinstance(phi, np.ndarray) and phi.dtype == object
    T = np.zeros((N, N, N, N), dtype=object if obj else np.int64)
    if obj:
        T[:] = 0
    for I, t in enumerate(K.FOUR):
        v = phi[I] if obj else int(phi[I])
        if v == 0:
            continue
        for perm in itertools.permutations(range(4)):
            idx = tuple(t[p] for p in perm)
            T[idx] = K.perm_sign(perm) * v
    return T


def from_dense(T):
    return np.array([T[t] for t in K.FOUR], dtype=object)


def _div(X, k):
    """exact division by integer k for int64 (must be exact) or object arrays."""
    if isinstance(X, np.ndarray) and X.dtype == object:
        return X / k
    if isinstance(X, np.ndarray):
        if np.issubdtype(X.dtype, np.integer):
            assert np.all(X % k == 0)
            return X // k
        return X / k
    return X / k if not isinstance(X, (int, np.integer)) else X // k


def _scalar(x):
    return x if not isinstance(x, np.ndarray) else x.item()


def antisym4(X):
    """total antisymmetrisation of a rank-4 tensor (times 24, to stay integral)."""
    out = np.zeros_like(X)
    for perm in itertools.permutations(range(4)):
        out += K.perm_sign(perm) * np.transpose(X, perm)
    return out


def antisym2(X):
    return X - X.T


def sym2(X):
    return X + X.T


# ---- quadratic covariants
def cov_M(T):
    """2-form *(Phi^Phi): M_ij = (1/(4!4!)) eps_{ij abcd efgh} T_abcd T_efgh  -- computed via sparse forms."""
    return hodge_wedge_2form(T)


def cov_S(T):
    """S_ij = T_iabc T_jabc / 6 (symmetric 10x10, integral)."""
    S = np.einsum("iabc,jabc->ij", T, T)
    return _div(S, 6)


def cov_A2_F4(T):
    """210-channel of Phi x Phi:  antisym_{abcd}( T_abef T_efcd )  (this is grad I3 up to factor)."""
    X = np.einsum("abef,efcd->abcd", T, T)
    return antisym4(X)


# ---- cubic covariants into 4-forms (non-epsilon patterns)
def c3_I2Phi(T):
    I2 = _div(_scalar(np.einsum("abcd,abcd->", T, T)), 24)
    return I2 * T


def c4_A3(T):
    X = np.einsum("abef,efgh,ghcd->abcd", T, T, T)
    return antisym4(X)


def c6_SPhi(T):
    S = cov_S(T)
    X = np.einsum("ae,ebcd->abcd", S, T)
    return antisym4(X)


def c7_cross(T):
    X = np.einsum("abef,cegh,dfgh->abcd", T, T, T, optimize=True)
    return antisym4(X)


def c5_MPhi(T):
    """so(10) action of the 2-form M on Phi: (M.Phi)_abcd = M_ae T_ebcd + ... (antisymmetrised)."""
    M = cov_M(T)
    X = np.einsum("ae,ebcd->abcd", M, T)
    return antisym4(X)


# ---- cubic covariants into 2-forms
def d1_PhiM(T):
    M = cov_M(T)
    return np.einsum("abcd,cd->ab", T, M)


def d2_SM(T):
    S = cov_S(T); M = cov_M(T)
    return S @ M - M @ S


def d5_chain(T):
    X = np.einsum("aegh,ghij,beij->ab", T, T, T, optimize=True)
    return antisym2(X)


def d6_eps(T):
    """d6_ab = *(Phi ^ i_a Phi ^ i_b Phi)  (scalar for each ab, antisymmetric)."""
    return eps_three(T)


# ---- cubic covariants into symmetric 10x10 (54 + 1)
def s2_chain(T):
    X = np.einsum("aegh,ghij,beij->ab", T, T, T, optimize=True)
    return sym2(X)


def s3_cross(T):
    X = np.einsum("aefg,behk,fghk->ab", T, T, T, optimize=True)
    return sym2(X)


def s4_SM_anti(T):
    S = cov_S(T); M = cov_M(T)
    return S @ M + M @ S          # symmetric? (SM+MS)^T = M^T S + S M^T = -MS - SM -> antisymmetric! keep for completeness


def s5_SS(T):
    """S acting on Phi then contracted back: (S.Phi)_iabc T_jabc  symmetric part."""
    X = np.einsum("ae,ebcd,fbcd->af", cov_S(T), T, T, optimize=True)
    return sym2(X)


# ---- exterior algebra on sparse forms (for epsilon patterns)
def sparse_form(T):
    f = {}
    for I, t in enumerate(K.FOUR):
        v = T[t]
        if v != 0:
            f[t] = v
    return f


def interior(f, b):
    out = defaultdict(int)
    for idx, c in f.items():
        if b in idx:
            pos = idx.index(b)
            out[idx[:pos] + idx[pos + 1:]] += ((-1) ** pos) * c
    return {k: v for k, v in out.items() if v}


def wedge(f, g):
    out = defaultdict(int)
    for i1, c1 in f.items():
        for i2, c2 in g.items():
            if set(i1) & set(i2):
                continue
            seq = i1 + i2
            st, sg = K.sorted_with_sign(seq)
            out[st] += sg * c1 * c2
    return {k: v for k, v in out.items() if v}


def hodge(f):
    out = defaultdict(int)
    full = set(range(N))
    for idx, c in f.items():
        comp = tuple(sorted(full - set(idx)))
        out[comp] += c * K.perm_sign(idx + comp)
    return {k: v for k, v in out.items() if v}


def hodge_wedge_2form(T):
    f = sparse_form(T)
    w = wedge(f, f)                     # 8-form
    h = hodge(w)                        # 2-form
    M = np.zeros((N, N), dtype=T.dtype)
    if T.dtype == object:
        M[:] = 0
    for (i, j), c in h.items():
        M[i, j] = c; M[j, i] = -c
    return M


def eps_three(T):
    """E_ab = *(Phi ^ i_a Phi ^ i_b Phi): antisymmetric 10x10."""
    f = sparse_form(T)
    ia = [interior(f, a) for a in range(N)]
    E = np.zeros((N, N), dtype=T.dtype)
    if T.dtype == object:
        E[:] = 0
    for a in range(N):
        for b in range(a + 1, N):
            w = wedge(wedge(f, ia[a]), ia[b])    # 4+3+3 = 10-form
            h = hodge(w)
            v = h.get((), 0)
            E[a, b] = v; E[b, a] = -v
    return E


def c11_eps(T):
    """4-form valued: C_abcd = antisym *(i_b Phi ^ i_c Phi ^ i_d Phi)_a  (9-form -> 1-form)."""
    f = sparse_form(T)
    ia = [interior(f, a) for a in range(N)]
    X = np.zeros((N, N, N, N), dtype=T.dtype)
    if T.dtype == object:
        X[:] = 0
    for b in range(N):
        for c in range(b + 1, N):
            wbc = wedge(ia[b], ia[c])
            for d in range(c + 1, N):
                h = hodge(wedge(wbc, ia[d]))      # 1-form
                for (a,), v in h.items():
                    X[a, b, c, d] = v
    return antisym4(X)


def c12_eps(T):
    """4-form valued: C_abcd = antisym *(Phi ^ i_b Phi ^ i_c i_d Phi)_a   (4+3+2 = 9-form -> 1-form)."""
    f = sparse_form(T)
    ia = [interior(f, a) for a in range(N)]
    iab = {}
    for c in range(N):
        for d in range(N):
            if c != d:
                iab[(c, d)] = interior(ia[c], d)
    X = np.zeros((N, N, N, N), dtype=T.dtype)
    if T.dtype == object:
        X[:] = 0
    for b in range(N):
        fb = wedge(f, ia[b])
        for c in range(N):
            for d in range(c + 1, N):
                h = hodge(wedge(fb, iab[(c, d)]))
                for (a,), v in h.items():
                    X[a, b, c, d] = v
    return antisym4(X)


def c18_eps(T):
    """4-form valued: *(i_e i_f Phi ^ i_e i_g Phi ^ i_f i_g Phi)... simpler variant:
       C = *( (i_e Phi) ^ (i_e Phi) ^ Phi ) summed over e  (3+3+4 = 10 -> scalar) is an invariant; instead use
       D_abcd = antisym *( (i_e i_a Phi) ^ (i_e Phi) ^ Phi )_{bcd}?  (2+3+4 = 9 -> 1-form) -> gives 'a' and a 1-form index.
    """
    f = sparse_form(T)
    ia = [interior(f, a) for a in range(N)]
    X = np.zeros((N, N, N, N), dtype=np.int64)
    for a in range(N):
        for e in range(N):
            if e == a:
                continue
            iea = interior(ia[a], e)     # 2-form
            w = wedge(wedge(iea, ia[e]), f)   # 2+3+4 = 9
            h = hodge(w)                 # 1-form index b
            for (b,), v in h.items():
                X[a, b, 0, 0] += 0  # placeholder (pattern gives a 2-index object, not a 4-form)
    return None


def f2_eps_vector(T):
    """2-form valued epsilon pattern:  E2_ab = antisym *( i_a Phi ^ Phi ^ (i_e i_b Phi) ^ ... )  -- omitted."""
    return None


F4_COVARIANTS = {
    # name: (function, degree)
    "I2Phi": (c3_I2Phi, 3), "A3": (c4_A3, 3), "SPhi": (c6_SPhi, 3), "cross": (c7_cross, 3), "MPhi": (c5_MPhi, 3),
    "eps3x3x3": (c11_eps, 3), "eps4x3x2": (c12_eps, 3),
    "gradI3": (cov_A2_F4, 2), "Phi": (lambda T: T, 1),
}
F2_COVARIANTS = {
    "PhiM": (d1_PhiM, 3), "chain": (d5_chain, 3), "eps": (d6_eps, 3), "M": (cov_M, 2),   # SM = S.M is degree 4 (excluded)
}
S2_COVARIANTS = {
    "chain": (s2_chain, 3), "cross": (s3_cross, 3), "S": (cov_S, 2),   # SS = (S.Phi).Phi is degree 4 (excluded)
    "I2delta": (lambda T: _div(_scalar(np.einsum("abcd,abcd->", T, T)), 24) * np.eye(N, dtype=np.int64), 2),
    "delta": (lambda T: np.eye(N, dtype=np.int64), 0),
}
SC_COVARIANTS = {
    "I3": (lambda T: _scalar(np.einsum("abef,efgh,ghab->", T, T, T)), 3),
    "I2": (lambda T: _div(_scalar(np.einsum("abcd,abcd->", T, T)), 24), 2),
    "one": (lambda T: 1, 0),
}
