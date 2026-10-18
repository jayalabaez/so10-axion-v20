"""Common helpers for the chart531 build skeptic (independent code; imports repo modules and chart531 read-only).

Independent constructions here:
  * the 45 so(10) generators on the A block are DERIVED from the repo's H10 block action (delta H = L H  =>
    delta A = [L, A] for A ~ H H'^T - H' H^T), not copied from chart531;
  * my own tensor maps chart -> (P_abcd, H_a, D_abcde, A_ab) through the repo's chart.unpack (not chart531's tables).
"""
from __future__ import annotations

import itertools
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CHART_DIR = HERE.parent
REPO = HERE.parents[4]
BIG = Path(r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory"
           r"\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\v22_stage2a_big\chart_skeptic")
BIG.mkdir(parents=True, exist_ok=True)
for p in (str(REPO), str(CHART_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

import gauged_u1x_g2_derivative_audit_v20 as g2_audit  # noqa: E402
import live_g2_canonical_486_field_chart_v20 as rchart  # noqa: E402

PAIRS = list(itertools.combinations(range(10), 2))
PIDX = {p: k for k, p in enumerate(PAIRS)}
N486 = rchart.TOTAL_DIM
NTOT = N486 + 45
SL = {
    "P": rchart.PHI_SLICE, "H": rchart.H_SLICE, "D": rchart.SIGMA_SLICE, "S": rchart.S_SLICE,
    "T": rchart.X_SLICE, "A": slice(N486, NTOT),
}
XCH = {"P": 0, "A": 0, "H": -2, "D": -2, "S": 4, "T": 17}


def log(msg: str, fh=None) -> None:
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    if fh is not None:
        fh.write(line + "\n")
        fh.flush()


_G486 = None


def repo_generators486():
    global _G486
    if _G486 is None:
        _G486 = g2_audit._so10_generator_matrices_cached()
    return _G486


def h_block_vector_matrices() -> list[np.ndarray]:
    """L_k (10x10) read off the repo's H10 block: complex-linear map K with delta z = K z."""
    G = repo_generators486()
    hs = SL["H"]
    out = []
    for k in range(45):
        g = np.asarray(G[k])[hs, hs]
        gxx, gyx, gxy, gyy = g[0::2, 0::2], g[1::2, 0::2], g[0::2, 1::2], g[1::2, 1::2]
        K = gxx + 1j * gyx
        assert np.max(np.abs(gxy + K.imag)) < 1e-14 and np.max(np.abs(gyy - K.real)) < 1e-14, "H block not C-linear"
        assert np.max(np.abs(K.imag)) < 1e-14, "H block generator not real (10 should be real)"
        out.append(K.real.copy())
    return out


def my_adjoint_block() -> list[np.ndarray]:
    """45x45 matrices of delta A = [L_k, A] in coordinates A_ab (a<b), L_k from the repo H block."""
    Ls = h_block_vector_matrices()
    basis = []
    for c, d in PAIRS:
        E = np.zeros((10, 10))
        E[c, d], E[d, c] = 1.0, -1.0
        basis.append(E)
    iu = (np.array([p[0] for p in PAIRS]), np.array([p[1] for p in PAIRS]))
    out = []
    for L in Ls:
        M = np.zeros((45, 45))
        for col, E in enumerate(basis):
            M[:, col] = (L @ E - E @ L)[iu]
        out.append(M)
    return out


def my_generators531() -> list[np.ndarray]:
    G = repo_generators486()
    ad = my_adjoint_block()
    out = []
    for k in range(45):
        M = np.zeros((NTOT, NTOT))
        M[:N486, :N486] = np.asarray(G[k])
        M[N486:, N486:] = ad[k]
        out.append(M)
    return out


def phase_rotation(theta_by_field: dict, n: int = NTOT) -> np.ndarray:
    """Real rotation z -> exp(i theta_F) z on each complex block (x, y interleaved)."""
    R = np.eye(n)
    for f in ("H", "D", "S", "T"):
        th = theta_by_field.get(f, 0.0)
        if th == 0.0:
            continue
        s = SL[f]
        c, si = math.cos(th), math.sin(th)
        for x in range(s.start, s.stop, 2):
            R[x, x], R[x, x + 1], R[x + 1, x], R[x + 1, x + 1] = c, -si, si, c
    return R


def a_matrix(qa: np.ndarray) -> np.ndarray:
    m = np.zeros((10, 10))
    for k, (a, b) in enumerate(PAIRS):
        m[a, b] = qa[k]
        m[b, a] = -qa[k]
    return m


def perm_sign_array(arr: np.ndarray) -> np.ndarray:
    r = arr.shape[1]
    inv = np.zeros(arr.shape[0], dtype=np.int64)
    for i in range(r):
        for j in range(i + 1, r):
            inv += (arr[:, i] > arr[:, j])
    return 1 - 2 * (inv % 2)


def full_antisym(form: dict, rank: int, dtype=complex) -> np.ndarray:
    """dense fully antisymmetric tensor from a dict {sorted tuple: value}."""
    T = np.zeros((10,) * rank, dtype=dtype)
    for t, v in form.items():
        for perm in itertools.permutations(range(rank)):
            idx = tuple(t[p] for p in perm)
            # sign of perm
            s = 1
            pl = list(perm)
            for i in range(rank):
                for j in range(i + 1, rank):
                    if pl[i] > pl[j]:
                        s = -s
            T[idx] = s * v
    return T


def tensors_from_q(q: np.ndarray) -> dict:
    """my own map: repo chart.unpack on q[:486] (+ A block) -> dense tensors."""
    st = rchart.unpack(np.asarray(q[:N486], dtype=float))
    P = full_antisym({t: complex(v).real for t, v in st.phi.items()}, 4, dtype=float)
    D = full_antisym({t: complex(v) for t, v in st.sigma.items()}, 5, dtype=complex)
    return {"P": P, "H": np.asarray(st.h, dtype=complex), "D": D, "A": a_matrix(q[N486:]),
            "S": complex(st.s), "T": complex(st.x)}


def json_dump(obj, path: Path) -> None:
    def conv(o):
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, complex):
            return [o.real, o.imag]
        raise TypeError(type(o))
    path.write_text(json.dumps(obj, indent=1, default=conv), encoding="utf-8")
