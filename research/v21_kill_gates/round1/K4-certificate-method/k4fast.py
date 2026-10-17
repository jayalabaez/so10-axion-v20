"""Fast float evaluator for V = c2 I2 + c3 I3 + la Ja + lb Jb + lc Jc + le Je on the 210."""
from __future__ import annotations
import numpy as np
from scipy import sparse
import k4lib as K

TSTACK = sparse.vstack(K.generators()).tocsr().astype(float)   # 9450 x 210
TSTACK_T = TSTACK.T.tocsr()
BSTACK = sparse.vstack(K.B_LIST).tocsr().astype(float)         # 9450 x 210
BSTACK_T = BSTACK.T.tocsr()
LA = K.LA.astype(float).tocsr()
LA_T = LA.T.tocsr()


def value_grad(phi, c):
    """c = (c2, c3, la, lb, lc, le)."""
    c2, c3, la, lb, lc, le = c
    phi = np.asarray(phi, dtype=float)
    I2 = float(phi @ phi)
    A = (LA @ phi).reshape(45, 45)
    A2 = A @ A
    A3 = A2 @ A
    I3 = float(np.trace(A3))
    Jb = float(np.sum(A2 * A2))
    Bp = (BSTACK @ phi).reshape(45, 210)          # rows B_k phi
    M = Bp @ phi                                   # M_k
    Jc = float(M @ M)
    Tp = (TSTACK @ phi).reshape(45, 210)           # rows T_A phi
    G = Tp @ Tp.T
    Je = float(np.sum(G * G))
    V = c2 * I2 + c3 * I3 + la * I2 * I2 + lb * Jb + lc * Jc + le * Je
    g = (2.0 * c2 + 4.0 * la * I2) * phi
    g += 3.0 * c3 * (LA_T @ A2.reshape(-1)) + 4.0 * lb * (LA_T @ A3.reshape(-1))
    g += 4.0 * lc * (Bp.T @ M)
    # Je grad = 4 sum_A T_A^T (sum_B G_AB T_B phi) = 4 TSTACK^T vec(G @ Tp)
    g += 4.0 * le * (TSTACK_T @ (G @ Tp).reshape(-1))
    return V, g


def invariants(phi):
    phi = np.asarray(phi, dtype=float)
    I2 = float(phi @ phi)
    A = (LA @ phi).reshape(45, 45)
    A2 = A @ A
    I3 = float(np.trace(A2 @ A))
    Jb = float(np.sum(A2 * A2))
    Bp = (BSTACK @ phi).reshape(45, 210)
    M = Bp @ phi
    Tp = (TSTACK @ phi).reshape(45, 210)
    G = Tp @ Tp.T
    return np.array([I2, I3, I2 * I2, Jb, float(M @ M), float(np.sum(G * G))])


def coeff_dict(c):
    c2, c3, la, lb, lc, le = c
    return {"I2": c2, "I3": c3, "Ja": la, "Jb": lb, "Jc": lc, "Je": le}
