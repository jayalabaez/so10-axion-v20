#!/usr/bin/env python3
"""v22-L2 stage-2a VACUUM TESTER - common helpers (531-real chart of stage2a/chart, imported read-only).

* IDS: the 85 parameter ids (51 v20 + 34 new A45 rows), fixed sorted order; DEG: polynomial degree of each row.
* all row polynomials: v20 rows from the optional exact backend v20poly (graph identities validated against the repo;
  final points are confirmed with the repo compiler), new rows from chart531 (exact).
* FastV(c): V_c = sum_k c_k I_k as ONE combined polynomial in the complex chart variables w, stored in a
  "pair" representation (degree 4: y^T M4 y with y = w_i w_j over the used pairs; degree 3: w^T M3 y; degree 2: w^T M2 w)
  -> value + gradient ~0.05-0.2 s, exact Hessian-vector products, exact Hessian (bincount).
* RowBank: the 85 per-row values J(q) at many points (batched pair representation).
* BOX normalisation: v20 rows (mass 40, cubic 2, quartic 1: R2-A/K3 convention); new rows the same per degree, divided
  by the eps-row normalisation factor of the chart report F1 (A04, A06: 1152; A07, A12: 192) so that |c| <= box means
  the same "natural" size as the invariants.json reference normalisation.
Labels: everything here is exact polynomial algebra evaluated in float64 (NUM, residuals reported by the callers).
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np
from scipy import sparse

HERE = Path(__file__).resolve().parent
CHART_DIR = HERE.parent / "chart"
BIG = Path(os.environ.get(
    "V22_VACUUM_BIG",
    r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory"
    r"\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\v22_stage2a_big\vacuum"))
BIG.mkdir(parents=True, exist_ok=True)
if str(CHART_DIR) not in sys.path:
    sys.path.insert(0, str(CHART_DIR))

import chart531 as C  # noqa: E402
import v20poly as VP  # noqa: E402

N = C.TOTAL_DIM
BLOCKS = C.BLOCKS
EPS_FACTOR = {"lambda::A04_PPA_eps": 1152.0, "lambda::A06_PPPA_eps1": 1152.0,
              "lambda::A07_PPPA_eps2": 192.0, "lambda::A12_PAAA_eps": 192.0}
BASE_BOX = {2: 40.0, 3: 2.0, 4: 1.0}


def _all_polys():
    out = dict(VP.rowpolys())
    for r in C.rowdefs():
        out[r.parameter_id] = r.poly
    return out


POLYS = _all_polys()
IDS = tuple(sorted(POLYS))
NPAR = len(IDS)
assert NPAR == 85
DEG = np.array([POLYS[p].degree for p in IDS])
IDX = {p: i for i, p in enumerate(IDS)}
NEW_IDS = set(C.new_parameter_ids())
IS_NEW = np.array([p in NEW_IDS for p in IDS])


def boxes(scale: float = 1.0, override: dict | None = None) -> np.ndarray:
    b = np.array([BASE_BOX[int(d)] / EPS_FACTOR.get(p, 1.0) for p, d in zip(IDS, DEG)]) * scale
    for k, v in (override or {}).items():
        for i, p in enumerate(IDS):
            if k in p:
                b[i] = v
    return b


def cvec(c) -> np.ndarray:
    if isinstance(c, dict):
        v = np.zeros(NPAR)
        for k, val in c.items():
            v[IDX[k]] = val
        return v
    v = np.asarray(c, dtype=float)
    assert v.shape == (NPAR,)
    return v


def cdict(c: np.ndarray) -> dict:
    return {p: float(x) for p, x in zip(IDS, c)}


def coef_of(p) -> np.ndarray:
    return p.coef()


# ------------------------------------------------------------------------------------------------------------------
# combined polynomial in pair representation
# ------------------------------------------------------------------------------------------------------------------
def _aggregate_float(idx: np.ndarray, coef: np.ndarray):
    idx = np.sort(np.asarray(idx, dtype=np.int64), axis=1)
    keys = np.zeros(idx.shape[0], dtype=np.int64)
    for j in range(idx.shape[1]):
        keys = keys * 1024 + idx[:, j]
    uk, inv = np.unique(keys, return_inverse=True)
    cr = np.bincount(inv, weights=coef.real, minlength=uk.size)
    ci = np.bincount(inv, weights=coef.imag, minlength=uk.size)
    out_idx = np.zeros((uk.size, idx.shape[1]), dtype=np.int64)
    k = uk.copy()
    for j in range(idx.shape[1] - 1, -1, -1):
        out_idx[:, j] = k % 1024
        k //= 1024
    c = cr + 1j * ci
    keep = c != 0
    return out_idx[keep], c[keep]


class PairStruct:
    """Pair list shared by several polynomials: y_p = w[P0[p]] * w[P1[p]]."""

    def __init__(self, pairs_keys: np.ndarray):
        self.keys = np.unique(pairs_keys)
        self.P0 = (self.keys // N).astype(np.int64)
        self.P1 = (self.keys % N).astype(np.int64)
        self.n = self.keys.size

    def index(self, i: np.ndarray, j: np.ndarray) -> np.ndarray:
        return np.searchsorted(self.keys, i * N + j)


def _pairs_needed(idx_by_deg: dict) -> np.ndarray:
    ks = []
    if 4 in idx_by_deg:
        ix = idx_by_deg[4]
        ks += [ix[:, 0] * N + ix[:, 1], ix[:, 2] * N + ix[:, 3]]
    if 3 in idx_by_deg:
        ix = idx_by_deg[3]
        ks += [ix[:, 1] * N + ix[:, 2]]
    return np.concatenate(ks) if ks else np.zeros(0, dtype=np.int64)


class FastV:
    """V_c(q) for a fixed coupling vector c (85) - value, gradient, Hessian-vector product, Hessian."""

    def __init__(self, c, polys: dict | None = None):
        c = cvec(c)
        polys = POLYS if polys is None else polys
        self.c = c
        by_deg = {}
        for k, pid in enumerate(IDS):
            if c[k] == 0:
                continue
            p = polys[pid]
            by_deg.setdefault(p.degree, []).append((p.idx.astype(np.int64), c[k] * coef_of(p)))
        self.idx = {}
        self.coef = {}
        for d, lst in by_deg.items():
            ix = np.vstack([a for a, _ in lst])
            cf = np.concatenate([b for _, b in lst])
            self.idx[d], self.coef[d] = _aggregate_float(ix, cf)
        self.ps = PairStruct(_pairs_needed(self.idx))
        ps = self.ps
        self.M2 = np.zeros((N, N), dtype=complex)
        if 2 in self.idx:
            ix = self.idx[2]
            np.add.at(self.M2, (ix[:, 0], ix[:, 1]), self.coef[2])
        self.M2s = self.M2 + self.M2.T
        self.M3 = None
        if 3 in self.idx:
            ix = self.idx[3]
            self.M3 = sparse.csr_matrix((self.coef[3], (ix[:, 0], ps.index(ix[:, 1], ix[:, 2]))), shape=(N, ps.n))
            self.M3T = self.M3.T.tocsr()
        self.M4 = None
        if 4 in self.idx:
            ix = self.idx[4]
            M = sparse.csr_matrix((self.coef[4], (ps.index(ix[:, 0], ix[:, 1]), ps.index(ix[:, 2], ix[:, 3]))),
                                  shape=(ps.n, ps.n))
            self.M4s = (M + M.T).tocsr()
            self.M4 = M
        self.n_terms = {d: int(v.shape[0]) for d, v in self.idx.items()}

    # w-space ---------------------------------------------------------------------------------------------------
    def _vg_w(self, w):
        ps = self.ps
        y = w[ps.P0] * w[ps.P1]
        V = complex(w @ self.M2 @ w)
        g = self.M2s @ w
        u = np.zeros(ps.n, dtype=complex)
        if self.M3 is not None:
            m3y = self.M3 @ y
            V += complex(w @ m3y)
            g = g + m3y
            u += self.M3T @ w
        if self.M4 is not None:
            m4y = self.M4s @ y
            V += 0.5 * complex(y @ m4y)
            u += m4y
        if self.M3 is not None or self.M4 is not None:
            # d y_p / d w_m contributions
            g = g + np.bincount(ps.P0, weights=(u * w[ps.P1]).real, minlength=N) \
                + 1j * np.bincount(ps.P0, weights=(u * w[ps.P1]).imag, minlength=N) \
                + np.bincount(ps.P1, weights=(u * w[ps.P0]).real, minlength=N) \
                + 1j * np.bincount(ps.P1, weights=(u * w[ps.P0]).imag, minlength=N)
        return V, g, y, u

    def value(self, q):
        w = C.w_of_q(np.asarray(q, float))
        ps = self.ps
        y = w[ps.P0] * w[ps.P1]
        V = complex(w @ self.M2 @ w)
        if self.M3 is not None:
            V += complex(w @ (self.M3 @ y))
        if self.M4 is not None:
            V += complex(y @ (self.M4 @ y))
        return float(V.real)

    def value_grad(self, q):
        w = C.w_of_q(np.asarray(q, float))
        V, gw, _, _ = self._vg_w(w)
        return float(V.real), np.real(C._grad_to_q(gw))

    def hvp(self, q, v):
        """exact Hessian-vector product H_q v."""
        w = C.w_of_q(np.asarray(q, float))
        vw = C.w_of_q(np.asarray(v, float))     # the chart map is linear
        ps = self.ps
        y = w[ps.P0] * w[ps.P1]
        dy = w[ps.P0] * vw[ps.P1] + vw[ps.P0] * w[ps.P1]
        hv = self.M2s @ vw
        u = np.zeros(ps.n, dtype=complex)
        du = np.zeros(ps.n, dtype=complex)
        if self.M3 is not None:
            hv = hv + self.M3 @ dy
            u += self.M3T @ w
            du += self.M3T @ vw
        if self.M4 is not None:
            u += self.M4s @ y
            du += self.M4s @ dy
        if self.M3 is not None or self.M4 is not None:
            for a, b in ((ps.P0, ps.P1), (ps.P1, ps.P0)):
                t1 = u * vw[b] + du * w[b]
                hv = hv + np.bincount(a, weights=t1.real, minlength=N) + 1j * np.bincount(a, weights=t1.imag, minlength=N)
        return np.real(C._grad_to_q(hv))

    def hessian(self, q):
        """exact Hessian by the chart531 bincount engine on the combined polynomial (2-6 s)."""
        w = C.w_of_q(np.asarray(q, float))
        H = np.zeros((N, N), dtype=complex)
        for d in self.idx:
            p = VP.FPoly(self.idx[d].astype(np.int16), self.coef[d])
            _, _, hw = C.poly_derivatives(p, w, hessian=True)
            H += hw
        Hq = np.real(C._hess_to_q(H))
        return 0.5 * (Hq + Hq.T)

    def degree4_value(self, q):
        if self.M4 is None:
            return 0.0
        w = C.w_of_q(np.asarray(q, float))
        y = w[self.ps.P0] * w[self.ps.P1]
        return float((y @ (self.M4 @ y)).real)


# ------------------------------------------------------------------------------------------------------------------
# per-row values at many points
# ------------------------------------------------------------------------------------------------------------------
class RowBank:
    """J(q) = values of the 85 rows (IDS order) at many points, via a stacked pair representation."""

    def __init__(self, polys: dict | None = None):
        polys = POLYS if polys is None else polys
        idx_by_deg = {}
        for pid in IDS:
            p = polys[pid]
            idx_by_deg.setdefault(p.degree, []).append(p.idx.astype(np.int64))
        allix = {d: np.vstack(v) for d, v in idx_by_deg.items()}
        self.ps = PairStruct(_pairs_needed(allix))
        ps = self.ps
        self.rows = []
        for k, pid in enumerate(IDS):
            p = polys[pid]
            ix = p.idx.astype(np.int64)
            cf = coef_of(p)
            if p.degree == 2:
                self.rows.append((2, ix[:, 0], ix[:, 1], cf))
            elif p.degree == 3:
                self.rows.append((3, ix[:, 0], ps.index(ix[:, 1], ix[:, 2]), cf))
            else:
                self.rows.append((4, ps.index(ix[:, 0], ix[:, 1]), ps.index(ix[:, 2], ix[:, 3]), cf))
        # stacked sparse matrices for degree 3 and 4 rows
        r4 = [(k, r) for k, r in enumerate(self.rows) if r[0] == 4]
        self.k4 = np.array([k for k, _ in r4])
        rows_ = np.concatenate([np.full(r[1].size, j, dtype=np.int64) * ps.n + r[1] for j, (_, r) in enumerate(r4)])
        cols_ = np.concatenate([r[2] for _, r in r4])
        data_ = np.concatenate([r[3] for _, r in r4])
        self.S4 = sparse.csr_matrix((data_, (rows_, cols_)), shape=(len(r4) * ps.n, ps.n))
        r3 = [(k, r) for k, r in enumerate(self.rows) if r[0] == 3]
        self.k3 = np.array([k for k, _ in r3])
        rows_ = np.concatenate([np.full(r[1].size, j, dtype=np.int64) * N + r[1] for j, (_, r) in enumerate(r3)])
        cols_ = np.concatenate([r[2] for _, r in r3])
        data_ = np.concatenate([r[3] for _, r in r3])
        self.S3 = sparse.csr_matrix((data_, (rows_, cols_)), shape=(len(r3) * N, ps.n))
        self.r2 = [(k, r) for k, r in enumerate(self.rows) if r[0] == 2]

    def values(self, Q: np.ndarray, chunk: int = 3) -> np.ndarray:   # chunk 3: peak ~0.45 GB (8.6e6 x 3 complex)
        Q = np.atleast_2d(np.asarray(Q, float))
        out = np.zeros((Q.shape[0], NPAR))
        ps = self.ps
        n4 = len(self.k4)
        n3 = len(self.k3)
        for s in range(0, Q.shape[0], chunk):
            W = C.w_of_q(Q[s:s + chunk])                 # (b, N)
            Y = (W[:, ps.P0] * W[:, ps.P1]).T             # (n_p, b)
            Z = self.S4 @ Y                               # (n4*n_p, b)
            b = W.shape[0]
            Z = Z.reshape(n4, ps.n, b)
            out[s:s + b, self.k4] = np.real(np.einsum("pb,kpb->bk", Y, Z))
            Z3 = (self.S3 @ Y).reshape(n3, N, b)
            out[s:s + b, self.k3] = np.real(np.einsum("bn,knb->bk", W, Z3))
            for k, r in self.r2:
                out[s:s + b, k] = np.real(np.sum(W[:, r[1]] * W[:, r[2]] * r[3][None, :], axis=1))
        return out


_ROWBANK = None


def rowbank() -> RowBank:
    global _ROWBANK
    if _ROWBANK is None:
        _ROWBANK = RowBank()
    return _ROWBANK


def J_values(Q: np.ndarray) -> np.ndarray:
    return rowbank().values(Q)


def rows_at(q, hessian=True, backend="poly"):
    """85 rows (value, gradient, Hessian) at q in IDS order: (values (85), grads (85,531), hess (85,531,531) or None)."""
    rows = C.parameter_rows(np.asarray(q, float), v20_backend=backend, hessian=hessian)
    vals = np.array([rows[p].value for p in IDS])
    grads = np.array([rows[p].gradient for p in IDS])
    hess = np.array([rows[p].hessian for p in IDS]) if hessian else None
    return vals, grads, hess


# ------------------------------------------------------------------------------------------------------------------
# misc
# ------------------------------------------------------------------------------------------------------------------
def block_norms(q) -> dict:
    q = np.asarray(q, float)
    return {k: float(np.linalg.norm(q[sl])) for k, sl in BLOCKS.items()}


def jsonable(v):
    if isinstance(v, dict):
        return {str(k): jsonable(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [jsonable(x) for x in v]
    if isinstance(v, np.ndarray):
        return jsonable(v.tolist())
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.bool_,)):
        return bool(v)
    if isinstance(v, complex):
        return {"re": v.real, "im": v.imag}
    return v


class Logger:
    def __init__(self, path: Path):
        self.f = open(path, "a", encoding="utf-8")

    def __call__(self, msg: str):
        line = f"[{time.strftime('%H:%M:%S')}] {msg}"
        print(line, flush=True)
        self.f.write(line + "\n")
        self.f.flush()
