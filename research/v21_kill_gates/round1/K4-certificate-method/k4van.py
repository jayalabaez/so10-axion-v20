"""Vanishing covariant combinations at a symmetric point Phi0 and their exact evaluation.

For a target space (F4 / F2 / S2 / SC) with covariants C_i of degree d_i <= 3, a combination
s_alpha(Phi) = sum_i alpha_i C_i(Phi) vanishes on the orbit SO(10).Phi0 iff sum_i alpha_i C_i(Phi0) = 0.
This module computes the integer null vectors alpha (one per vanishing polynomial family), evaluates
s_alpha at arbitrary points (exact for integer input), and computes the polarisation ds_alpha(Phi0)[xi].
"""
from __future__ import annotations
import numpy as np
import sympy as sp
import k4lib as K
import k4cov as C

FAMILIES = {"F4": C.F4_COVARIANTS, "F2": C.F2_COVARIANTS, "S2": C.S2_COVARIANTS, "SC": C.SC_COVARIANTS}
TARGET_DIM = {"F4": 210, "F2": 45, "S2": 55, "SC": 1}


def flat(target, X):
    """flatten a covariant value to a vector of independent components (object/int)."""
    if target == "F4":
        return np.array([X[t] for t in K.FOUR], dtype=object)
    if target == "F2":
        return np.array([X[i, j] for (i, j) in K.TWO], dtype=object)
    if target == "S2":
        return np.array([X[i, j] for i in range(10) for j in range(i, 10)], dtype=object)
    return np.array([X], dtype=object)


def inner_weights(target):
    """weights w such that <X,Y> = sum_k w_k x_k y_k is the SO(10)-invariant inner product on the flattened vector."""
    if target == "F4":
        return np.ones(210)
    if target == "F2":
        return np.ones(45) * 2.0          # sum_{i<j} 2 X_ij Y_ij = sum_{ij} X_ij Y_ij
    if target == "S2":
        return np.array([1.0 if i == j else 2.0 for i in range(10) for j in range(i, 10)])
    return np.ones(1)


def covariant_values(target, phi_int):
    """list of (name, degree, flattened value) at an integer vector phi_int (exact)."""
    T = C.dense(np.asarray(phi_int, dtype=np.int64))
    out = []
    for name, (f, d) in FAMILIES[target].items():
        out.append((name, d, flat(target, f(T))))
    return out


def vanishing_combinations(target, phi0_int):
    """integer null vectors alpha with sum alpha_i C_i(Phi0) = 0.  Returns (names, degrees, [alpha ...])."""
    vals = covariant_values(target, phi0_int)
    names = [v[0] for v in vals]; degs = [v[1] for v in vals]
    V = sp.Matrix(np.column_stack([v[2] for v in vals]).tolist())
    ns = V.nullspace()
    alphas = []
    for vec in ns:
        den = sp.ilcm(*[sp.fraction(x)[1] for x in vec])
        a = [int(x * den) for x in vec]
        g = 0
        for x in a:
            g = sp.igcd(g, x)
        if g > 1:
            a = [x // g for x in a]
        alphas.append(a)
    return names, degs, alphas


def evaluate_combination(target, names, alpha, phi):
    """s_alpha(phi) flattened (exact for int input; float otherwise)."""
    phi = np.asarray(phi)
    T = C.dense(phi.astype(np.int64)) if np.issubdtype(phi.dtype, np.integer) else dense_float(phi)
    tot = None
    for n, a in zip(names, alpha):
        if a == 0:
            continue
        v = flat(target, FAMILIES[target][n][0](T))
        tot = a * v if tot is None else tot + a * v
    return tot


def dense_float(phi):
    import itertools
    T = np.zeros((10, 10, 10, 10))
    for I, t in enumerate(K.FOUR):
        v = float(phi[I])
        if v == 0.0:
            continue
        for perm in itertools.permutations(range(4)):
            T[tuple(t[p] for p in perm)] = K.perm_sign(perm) * v
    return T


def polarisation_matrix(target, names, degs, alpha, phi0_int):
    """exact matrix J (target_dim x 210): column j = d s_alpha (Phi0)[e_j]."""
    T0 = C.dense(np.asarray(phi0_int, dtype=np.int64))
    cols = []
    eye = np.eye(210, dtype=np.int64)
    for j in range(210):
        Tx = C.dense(eye[j])
        tot = None
        for n, d, a in zip(names, degs, alpha):
            if a == 0 or d == 0:
                continue
            f = FAMILIES[target][n][0]
            if d == 3:
                pol = (f(T0 + Tx) - f(T0 - Tx)) // 2 - f(Tx)
            elif d == 2:
                pol = (f(T0 + Tx) - f(T0 - Tx)) // 2
            else:
                pol = f(Tx)
            v = a * flat(target, pol)
            tot = v if tot is None else tot + v
        cols.append(tot)
    return np.column_stack(cols)
