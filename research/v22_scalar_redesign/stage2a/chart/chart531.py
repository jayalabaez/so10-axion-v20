#!/usr/bin/env python3
"""chart531 - the 531-real scalar chart of v22-L2 (repo 486-real chart + one real 45_H), self-contained.

Coordinates (identity kinetic metric, K = 1/2 q.q):
    q[  0:210]  Phi210       independent components P_abcd, a<b<c<d          (repo chart, verbatim)
    q[210:230]  H10          H_a = (x_a + i y_a)/sqrt2, interleaved          (repo chart, verbatim)
    q[230:482]  Sigma126bar  126 -i Hodge basis coefficients, interleaved    (repo chart, verbatim)
    q[482:484]  S            (x + i y)/sqrt2                                  (repo chart, verbatim)
    q[484:486]  Phi17        (x + i y)/sqrt2                                  (repo chart, verbatim)
    q[486:531]  A45          A_ab, a<b, itertools.combinations(range(10),2) order (= generator order of the repo);
                             kinetic (1/4) dA_ab dA_ab = (1/2) sum_{a<b} dA_ab^2, K45 = (1/2) A_ab A_ab.
The first 486 coordinates ARE the repository chart (live_g2_canonical_486_field_chart_v20); nothing is re-derived there.

Potential rows (V = sum_k c_k I_k, 85 real parameters = 51 + 34):
  * 51 v20 rows: the repository's exact-X compiler (g3_candidate_physical_target_audit_v20.parameter_rows, read-only
    import) evaluated at the 486 sub-state and embedded with zero A-blocks (they do not depend on A).
  * 34 new rows: the 30 A45 invariants of stage2a/model/invariants.json (A01..A30).  Each is compiled HERE into an
    exact sparse polynomial in the complex chart variables w (w = q on Phi/A; z = (x+iy)/sqrt2 and zbar on the complex
    blocks) with Gaussian-integer numerators and an integer denominator: the only irrational number anywhere is the
    chart's 1/sqrt2.  Row conventions follow the repo (live_g2_exact_quadratic_family_derivatives_v20):
        hermitian invariant I (real coupling)    -> 'lambda::<name>'  = I
        complex coupling (V contains c I + c.c.) -> 're::<name>' = 2 Re I,  'im::<name>' = -2 Im I
    Values, gradients (531) and Hessians (531x531) are exact polynomial derivatives (no finite differences).
Symmetry: the 45 so(10) generators on the 531 chart (repo 486 blocks + the adjoint action delta A = [L_ab, A] with
L_ab e_b = e_a), the U(1)_X and PQ phase generators (A carries X = PQ = 0), Goldstone tangents.
Labels: SU(3)_c and SU(2)_L Casimirs, T3R, B-L, T3L, Y on the 531 chart (same constructions as the repo's
g3_sm_pati_salam_candidate_v20.sm_label_operators, extended); complex isotypic decomposition into G3211
(SU3 x SU2L x U1R x U1BL) or SM irreps, highest-weight slices, Hessian decomposition, A-block projectors.
Vacuum parametrisation: g3211_point(p, a, omega, omega_R, omega_BL, sigma, s, x).

Convention for charges: the Hermitian charge of a U(1) generator G (real antisymmetric chart matrix) is Q = -i G on
the complexified chart (repo convention T3R = (1/2)(-i) T3R_INTEGER, B-L = -(2/3)(-i) BL_INTEGER,
Y = (1/6)(-i) Y_STANDARD_INTEGER); a field component z with delta z = i q z carries charge q.  "3" is the colour
triplet with 3(B-L) = 1 mod 3 (quark-like; triality is fixed by B-L, resp. by 6Y, in every SO(10) representation).

Normalisation (see REPORT.txt sec. 2c): the rows implement the DECLARED machine_spec formulas of invariants.json;
its reference values differ by 1152 (A04, A06), 192 (A07, A12) and -1 (A13, A17) - the model evaluator's
sorted-block eps sums and multigraph index re-ordering.  OPTIONAL fast v20 rows: parameter_rows(q,
v20_backend="poly") uses v20poly.py (graph-polynomial identities validated against the repo; default "repo").

Repo caveat (inherited, NOT changed): potential.FieldState.validated() drops Phi210 and Sigma126bar components with
|value| <= 1e-14 (chart units) and chart.unpack/sigma_from_coordinates use direct.add_forms (threshold 1e-13), so the
51 v20 rows cannot see Sigma components below ~1e-13.  The new A rows use q directly (no threshold).
Nothing in the repository is modified; all repo modules are imported read-only.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import os
import sys
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
from scipy import sparse

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
MODEL_DIR = HERE.parent / "model"
INVARIANTS_JSON = MODEL_DIR / "invariants.json"
BIG = Path(os.environ.get(
    "V22_CHART531_BIG",
    r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory"
    r"\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\v22_stage2a_big\chart"))
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import direct_phi_h_sigmabar_tensor_v20 as direct  # noqa: E402
import live_g2_canonical_486_field_chart_v20 as chart  # noqa: E402
import live_g2_arbitrary_component_potential_values_v20 as potential  # noqa: E402
import gauged_u1x_g2_derivative_audit_v20 as g2_audit  # noqa: E402
import g3_sigma_hypercharge_audit_v20 as hypercharge  # noqa: E402
import exact_gauged_u1x_physical_quotient_v20 as quotient  # noqa: E402

CODE_VERSION = "chart531-v1"

# =====================================================================================================================
# 1. chart
# =====================================================================================================================
DIM486 = chart.TOTAL_DIM
A_DIM = 45
TOTAL_DIM = DIM486 + A_DIM
PHI_SLICE = chart.PHI_SLICE
H_SLICE = chart.H_SLICE
SIGMA_SLICE = chart.SIGMA_SLICE
S_SLICE = chart.S_SLICE
X_SLICE = chart.X_SLICE
A_SLICE = slice(DIM486, TOTAL_DIM)
BLOCKS = OrderedDict((("Phi210", PHI_SLICE), ("H10", H_SLICE), ("Sigma126bar", SIGMA_SLICE), ("S", S_SLICE),
                      ("Phi17", X_SLICE), ("A45", A_SLICE)))
PAIRS = tuple(itertools.combinations(range(10), 2))
assert PAIRS == tuple(hypercharge.GENERATORS)
PAIR_INDEX = {p: k for k, p in enumerate(PAIRS)}
_IU = (np.array([p[0] for p in PAIRS]), np.array([p[1] for p in PAIRS]))
SQRT2 = math.sqrt(2.0)
U1X_CHARGES = dict(g2_audit.U1X_CHARGES, A45=0)
PQ_CHARGES = dict(quotient.PQ_CHARGES, Phi210=0, A45=0)
assert TOTAL_DIM == 531


def a_matrix(qa: np.ndarray) -> np.ndarray:
    """10x10 real antisymmetric A from its 45 chart coordinates A_ab (a<b)."""
    qa = np.asarray(qa, dtype=float).reshape(A_DIM)
    m = np.zeros((10, 10))
    m[_IU] = qa
    return m - m.T


def a_coordinates(m: np.ndarray) -> np.ndarray:
    m = np.asarray(m, dtype=float)
    if np.max(np.abs(m + m.T)) > 1e-12 * max(1.0, np.max(np.abs(m))):
        raise ValueError("A45 must be antisymmetric")
    return m[_IU].copy()


def split(q: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    q = np.asarray(q, dtype=float).reshape(TOTAL_DIM)
    return q[:DIM486].copy(), q[A_SLICE].copy()


def join(q486: np.ndarray, qa: np.ndarray | None = None) -> np.ndarray:
    out = np.zeros(TOTAL_DIM)
    out[:DIM486] = np.asarray(q486, dtype=float).reshape(DIM486)
    if qa is not None:
        out[A_SLICE] = np.asarray(qa, dtype=float).reshape(A_DIM)
    return out


def pack(state: potential.FieldState, A: np.ndarray | None = None) -> np.ndarray:
    """(repo FieldState, A as 10x10 antisymmetric matrix or 45-vector) -> 531-real q."""
    qa = None
    if A is not None:
        A = np.asarray(A, dtype=float)
        qa = a_coordinates(A) if A.shape == (10, 10) else A.reshape(A_DIM)
    return join(chart.pack(state), qa)


def unpack(q: np.ndarray) -> tuple[potential.FieldState, np.ndarray]:
    q486, qa = split(q)
    return chart.unpack(q486), a_matrix(qa)


def coordinate_names() -> tuple[str, ...]:
    return tuple(chart.coordinate_names()) + tuple(f"A[{a},{b}]" for a, b in PAIRS)


# =====================================================================================================================
# 2. complex chart variables w = M q  (real coordinates unchanged; complex pairs -> z, zbar)
# =====================================================================================================================
_Z = np.arange(H_SLICE.start, X_SLICE.stop, 2)          # x positions of every complex pair (H, Sigma, S, Phi17)
_ZB = _Z + 1                                            # y positions
_REAL = np.r_[np.arange(PHI_SLICE.start, PHI_SLICE.stop), np.arange(A_SLICE.start, A_SLICE.stop)]
CONJVAR = np.arange(TOTAL_DIM)
CONJVAR[_Z] = _ZB
CONJVAR[_ZB] = _Z
# variable index of the slots of an invariant
VAR_P0, VAR_A0 = PHI_SLICE.start, A_SLICE.start
VAR_H0, VAR_D0 = H_SLICE.start, SIGMA_SLICE.start
VAR_S, VAR_SB, VAR_T, VAR_TB = S_SLICE.start, S_SLICE.start + 1, X_SLICE.start, X_SLICE.start + 1


def w_of_q(q: np.ndarray) -> np.ndarray:
    q = np.asarray(q, dtype=float)
    w = q.astype(complex)
    z = (q[..., _Z] + 1j * q[..., _ZB]) / SQRT2
    w[..., _Z] = z
    w[..., _ZB] = np.conj(z)
    return w


def _grad_to_q(gw: np.ndarray) -> np.ndarray:
    """g_q = M^T g_w."""
    out = gw.copy()
    a, b = gw[..., _Z], gw[..., _ZB]
    out[..., _Z] = (a + b) / SQRT2
    out[..., _ZB] = 1j * (a - b) / SQRT2
    return out


def _hess_to_q(hw: np.ndarray) -> np.ndarray:
    """H_q = M^T H_w M (both axes)."""
    h = hw.copy()
    a, b = h[_Z, :].copy(), h[_ZB, :].copy()
    h[_Z, :] = (a + b) / SQRT2
    h[_ZB, :] = 1j * (a - b) / SQRT2
    a, b = h[:, _Z].copy(), h[:, _ZB].copy()
    h[:, _Z] = (a + b) / SQRT2
    h[:, _ZB] = 1j * (a - b) / SQRT2
    return h


# =====================================================================================================================
# 3. exact sparse polynomials (Gaussian-integer numerators / integer denominator) in the w variables
# =====================================================================================================================
@dataclass
class Poly:
    """sum_t (num_re[t] + i num_im[t]) / den * prod_k w[idx[t, k]]; idx rows sorted ascending."""
    idx: np.ndarray       # (T, d) int16
    num_re: np.ndarray    # (T,) int64
    num_im: np.ndarray    # (T,) int64
    den: int

    @property
    def degree(self) -> int:
        return int(self.idx.shape[1])

    @property
    def n_terms(self) -> int:
        return int(self.idx.shape[0])

    def coef(self) -> np.ndarray:
        return (self.num_re.astype(float) + 1j * self.num_im.astype(float)) / float(self.den)


_BASE = 1024


def _keys(idx: np.ndarray) -> np.ndarray:
    k = np.zeros(idx.shape[0], dtype=np.int64)
    for j in range(idx.shape[1]):
        k = k * _BASE + idx[:, j].astype(np.int64)
    return k


def _unkeys(keys: np.ndarray, d: int) -> np.ndarray:
    out = np.zeros((keys.size, d), dtype=np.int16)
    k = keys.copy()
    for j in range(d - 1, -1, -1):
        out[:, j] = (k % _BASE).astype(np.int16)
        k //= _BASE
    return out


def _aggregate(idx: np.ndarray, re: np.ndarray, im: np.ndarray, den: int) -> Poly:
    """sum equal monomials exactly (integer-valued floats or ints), drop zeros."""
    idx = np.sort(np.asarray(idx), axis=1).astype(np.int16)
    keys = _keys(idx)
    uk, inv = np.unique(keys, return_inverse=True)
    sr = np.bincount(inv, weights=np.asarray(re, dtype=float), minlength=uk.size)
    si = np.bincount(inv, weights=np.asarray(im, dtype=float), minlength=uk.size)
    rr, ri = np.rint(sr), np.rint(si)
    if np.max(np.abs(sr - rr), initial=0.0) > 0 or np.max(np.abs(si - ri), initial=0.0) > 0:
        raise ArithmeticError("non-integer aggregated numerator")
    if np.max(np.abs(rr), initial=0.0) > 2.0 ** 52 or np.max(np.abs(ri), initial=0.0) > 2.0 ** 52:
        raise ArithmeticError("numerator overflow risk")
    keep = (rr != 0) | (ri != 0)
    return Poly(_unkeys(uk[keep], idx.shape[1]), rr[keep].astype(np.int64), ri[keep].astype(np.int64), int(den))


def poly_conj(p: Poly) -> Poly:
    return _aggregate(CONJVAR[p.idx.astype(np.int64)], p.num_re, -p.num_im, p.den)


def poly_lincomb(terms: Sequence[tuple[complex, Poly]], den: int) -> Poly:
    """sum_k u_k P_k with u_k in {+-1, +-i}*integer and all P_k sharing degree; result over common denominator den."""
    idx, re, im = [], [], []
    for u, p in terms:
        scale = Fraction(den, p.den)
        if scale.denominator != 1:
            raise ArithmeticError("denominator must be a common multiple")
        s = int(scale)
        ur, ui = int(round(u.real)), int(round(u.imag))
        if complex(ur, ui) != complex(u):
            raise ArithmeticError("lincomb weights must be Gaussian integers")
        idx.append(p.idx)
        re.append(s * (ur * p.num_re - ui * p.num_im))
        im.append(s * (ur * p.num_im + ui * p.num_re))
    return _aggregate(np.vstack(idx), np.concatenate(re), np.concatenate(im), den)


def poly_div(p: Poly, k: int) -> Poly:
    """p / k (exact: the denominator is multiplied by k)."""
    return Poly(p.idx, p.num_re, p.num_im, p.den * int(k))


def poly_equal(p: Poly, q: Poly) -> bool:
    if p.idx.shape != q.idx.shape:
        return False
    d = poly_lincomb([(1, p), (-1, q)], math.lcm(p.den, q.den))
    return d.n_terms == 0


# ---------------------------------------------------------------------------------------------------------------------
# lookup tables: sorted index tuples -> chart coordinates
# ---------------------------------------------------------------------------------------------------------------------
@lru_cache(maxsize=1)
def _tables() -> dict[str, np.ndarray]:
    bm4 = np.full(1024, -1, dtype=np.int64)
    for k, t in enumerate(chart.phi_indices()):
        bm4[sum(1 << i for i in t)] = k
    bm2 = np.full(1024, -1, dtype=np.int64)
    for k, t in enumerate(PAIRS):
        bm2[sum(1 << i for i in t)] = k
    dstate = np.full(1024, -1, dtype=np.int64)
    dcoef = np.zeros(1024, dtype=complex)
    for i, st in enumerate(chart.sigma_basis()):
        for t, c in st.items():
            bm = sum(1 << j for j in t)
            if dstate[bm] != -1:
                raise AssertionError("sorted 5-tuple in two basis states")
            dstate[bm] = i
            c = complex(c)
            if c not in (1, 1j, -1j):
                raise AssertionError("unexpected Sigma basis component")
            dcoef[bm] = c
    if np.sum(dstate >= 0) != 252:
        raise AssertionError("Sigma basis does not cover the 252 sorted 5-tuples exactly once")
    return {"bm4": bm4, "bm2": bm2, "dstate": dstate, "dcoef": dcoef}


def _sort_sign(vals: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """rows of distinct ints -> (sorted rows, permutation sign, bitmask)."""
    r = vals.shape[1]
    inv = np.zeros(vals.shape[0], dtype=np.int64)
    for i in range(r):
        for j in range(i + 1, r):
            inv += (vals[:, i] > vals[:, j])
    sign = 1 - 2 * (inv % 2)
    bm = np.zeros(vals.shape[0], dtype=np.int64)
    for i in range(r):
        bm |= (np.int64(1) << vals[:, i].astype(np.int64))
    return np.sort(vals, axis=1), sign, bm


TYPE = {"A45": "A", "Phi210": "P", "H10": "H", "H10^dag": "Hb", "Delta126bar": "D", "Delta126bar^dag": "Db"}
RANK = {"A": 2, "P": 4, "H": 1, "Hb": 1, "D": 5, "Db": 5}
SINGLET_VAR = {"S": VAR_S, "Sb": VAR_SB, "T": VAR_T, "Tb": VAR_TB}
FIELD_OF_VAR_TYPE = {"A": "A45", "P": "Phi210", "H": "H10", "Hb": "H10", "D": "Sigma126bar", "Db": "Sigma126bar",
                     "S": "S", "Sb": "S", "T": "Phi17", "Tb": "Phi17"}
HOLOMORPHIC_SIGN = {"H": 1, "Hb": -1, "D": 1, "Db": -1, "S": 1, "Sb": -1, "T": 1, "Tb": -1, "A": 0, "P": 0}


def _enumerate(types: list[str], idxs: list[str]) -> tuple[np.ndarray, list[str], int, bool]:
    """All index assignments of a contraction, letters grouped by signature (sorted subsets x k! factor)."""
    occ: dict[str, list[tuple[int, int]]] = {}
    order: list[str] = []
    for t, s in enumerate(idxs):
        if len(s) != RANK[types[t]]:
            raise ValueError(f"index string {s} does not match rank of {types[t]}")
        for pos, ch in enumerate(s):
            if ch not in occ:
                order.append(ch)
            occ.setdefault(ch, []).append((t, pos))
    groups: dict[tuple, list[str]] = {}
    has_eps = False
    for ch in order:
        o = occ[ch]
        if ch.isupper():
            if len(o) != 1:
                raise ValueError(f"eps letter {ch} must appear once")
            key = ("E", o[0][0])
            has_eps = True
        else:
            if len(o) != 2 or o[0][0] == o[1][0]:
                raise ValueError(f"letter {ch} must join two different tensors")
            key = ("L", o[0][0], o[1][0])
        groups.setdefault(key, []).append(ch)
    glist = sorted(groups.items(), key=lambda kv: (kv[0][0] != "E", -len(kv[1])))
    n_slots = len(types)
    assign = np.zeros((1, 0), dtype=np.int8)
    masks = np.zeros((1, n_slots), dtype=np.int64)
    emask = np.zeros(1, dtype=np.int64)
    cols: list[str] = []
    factor = 1
    for key, chs in glist:
        k = len(chs)
        factor *= math.factorial(k)
        C = np.array(list(itertools.combinations(range(10), k)), dtype=np.int8).reshape(-1, k)
        mc = np.zeros(C.shape[0], dtype=np.int64)
        for j in range(k):
            mc |= (np.int64(1) << C[:, j].astype(np.int64))
        tslots = [key[1]] if key[0] == "E" else [key[1], key[2]]
        n, nc = assign.shape[0], C.shape[0]
        I = np.repeat(np.arange(n), nc)
        J = np.tile(np.arange(nc), n)
        ok = np.ones(I.size, dtype=bool)
        for t in tslots:
            if RANK[types[t]] > 1:
                ok &= (masks[I, t] & mc[J]) == 0
        if key[0] == "E":
            ok &= (emask[I] & mc[J]) == 0
        I, J = I[ok], J[ok]
        assign = np.hstack([assign[I], C[J]])
        masks = masks[I].copy()
        for t in tslots:
            masks[:, t] |= mc[J]
        emask = emask[I] | mc[J] if key[0] == "E" else emask[I]
        cols.extend(chs)
    if has_eps and not np.all(emask == 1023):
        raise AssertionError("eps letters do not exhaust 0..9")
    return assign, cols, factor, has_eps


def build_contraction(spec: Mapping[str, Any]) -> Poly:
    """Exact polynomial of  prefactor * contraction (* singlet factors), BEFORE taking any Re/Im part."""
    types = [TYPE[t] for t in spec["tensors"]]
    idxs = list(spec["indices"])
    assign, cols, factor, has_eps = _enumerate(types, idxs)
    col = {ch: j for j, ch in enumerate(cols)}
    T = _tables()
    n = assign.shape[0]
    coef = np.full(n, float(factor), dtype=complex)
    variables = []
    for t, s in enumerate(idxs):
        vals = np.stack([assign[:, col[ch]] for ch in s], axis=1).astype(np.int64)
        ty = types[t]
        if ty in ("H", "Hb"):
            variables.append(VAR_H0 + 2 * vals[:, 0] + (1 if ty == "Hb" else 0))
            continue
        srt, sign, bm = _sort_sign(vals)
        coef *= sign
        if ty == "P":
            k = T["bm4"][bm]
            variables.append(VAR_P0 + k)
        elif ty == "A":
            k = T["bm2"][bm]
            variables.append(VAR_A0 + k)
        else:
            i = T["dstate"][bm]
            c = T["dcoef"][bm]
            if ty == "D":
                coef *= c
                variables.append(VAR_D0 + 2 * i)
            else:
                coef *= np.conj(c)
                variables.append(VAR_D0 + 2 * i + 1)
        if np.any(variables[-1] < 0):
            raise AssertionError("index tuple outside the chart")
    if has_eps:
        caps = [ch for s in idxs for ch in s if ch.isupper()]
        seq = np.stack([assign[:, col[ch]] for ch in caps], axis=1).astype(np.int64)
        _, esign, _ = _sort_sign(seq)
        coef *= esign
    for sname in spec.get("singlet_factors", []) or []:
        variables.append(np.full(n, SINGLET_VAR[sname], dtype=np.int64))
    pref = spec["prefactor"]
    den = 1
    if pref == "1/2":
        den = 2
    elif pref == "i":
        coef *= 1j
    elif pref != "1":
        raise ValueError(f"unknown prefactor {pref}")
    idx = np.stack(variables, axis=1)
    return _aggregate(idx, coef.real, coef.imag, den)


# ---------------------------------------------------------------------------------------------------------------------
# rows from invariants.json
# ---------------------------------------------------------------------------------------------------------------------
@dataclass
class RowDef:
    parameter_id: str
    invariant: str
    coupling: str
    component: str          # real | re | im
    family: str
    field_content: dict
    poly: Poly
    contraction: str
    holomorphic_charges: dict = field(default_factory=dict)   # n(field) - n(field^dag) of the underlying invariant


def _load_invariants() -> dict:
    return json.loads(INVARIANTS_JSON.read_text(encoding="utf-8"))


def _spec_hash() -> str:
    d = _load_invariants()
    blob = json.dumps([(e["name"], e["machine_spec"], e["coupling_type"]) for e in d["A45_invariants"]],
                      sort_keys=True).encode()
    return hashlib.sha256(blob + CODE_VERSION.encode()).hexdigest()[:16]


def _holo_charges(entry: Mapping[str, Any]) -> dict[str, int]:
    ms = entry["machine_spec"]
    out = {"H10": 0, "Sigma126bar": 0, "S": 0, "Phi17": 0}
    for t in ms["tensors"]:
        ty = TYPE[t]
        f = FIELD_OF_VAR_TYPE[ty]
        if f in out:
            out[f] += HOLOMORPHIC_SIGN[ty]
    for s in ms.get("singlet_factors", []) or []:
        out[FIELD_OF_VAR_TYPE[s]] += HOLOMORPHIC_SIGN[s]
    return out


def _build_rowdefs() -> list[RowDef]:
    d = _load_invariants()
    rows: list[RowDef] = []
    for e in d["A45_invariants"]:
        ms = e["machine_spec"]
        p0 = build_contraction(ms)
        cplx = e["real_parameters"] == 2
        hc = _holo_charges(e)
        common = dict(invariant=e["name"], coupling=e["coupling"], family=e["family"],
                      field_content=e["field_content"], contraction=e["contraction"], holomorphic_charges=hc)
        pc = poly_conj(p0)
        if cplx:
            if ms["part"] != "full":
                raise ValueError("complex coupling with a Re/Im part")
            # 2 Re I = I + conj(I);  -2 Im I = i (I - conj(I))
            rows.append(RowDef(f"re::{e['name']}", component="re", poly=poly_lincomb([(1, p0), (1, pc)], p0.den), **common))
            rows.append(RowDef(f"im::{e['name']}", component="im", poly=poly_lincomb([(1j, p0), (-1j, pc)], p0.den), **common))
        else:
            if ms["part"] == "full":
                if not poly_equal(p0, pc):
                    raise ArithmeticError(f"{e['name']}: declared hermitian invariant is not self-conjugate (EXACT check)")
                poly = p0
            elif ms["part"] == "Re":      # Re I = (I + conj I)/2
                poly = poly_div(poly_lincomb([(1, p0), (1, pc)], p0.den), 2)
            elif ms["part"] == "Im":      # Im I = -i (I - conj I)/2
                poly = poly_div(poly_lincomb([(-1j, p0), (1j, pc)], p0.den), 2)
            else:
                raise ValueError(ms["part"])
            rows.append(RowDef(f"lambda::{e['name']}", component="real", poly=poly, **common))
    for r in rows:   # every row is an exactly self-conjugate (real-valued) polynomial
        if not poly_equal(r.poly, poly_conj(r.poly)):
            raise ArithmeticError(f"{r.parameter_id}: row polynomial not self-conjugate")
    return rows


def _cache_path() -> Path:
    return BIG / f"poly_cache_{CODE_VERSION}_{_spec_hash()}.npz"


_ROWDEFS: list[RowDef] | None = None
_RAW_CONTRACTIONS: dict[str, Poly] = {}


def rowdefs(rebuild: bool = False) -> list[RowDef]:
    """The 34 new exact rows (cached polynomial data under BIG)."""
    global _ROWDEFS
    if _ROWDEFS is not None and not rebuild:
        return _ROWDEFS
    path = _cache_path()
    d = _load_invariants()
    meta_by_name = {e["name"]: e for e in d["A45_invariants"]}
    if path.exists() and not rebuild:
        z = np.load(path, allow_pickle=False)
        meta = json.loads(str(z["meta"]))
        rows = []
        for k, m in enumerate(meta):
            e = meta_by_name[m["invariant"]]
            rows.append(RowDef(m["parameter_id"], m["invariant"], e["coupling"], m["component"], e["family"],
                               e["field_content"], Poly(z[f"idx{k}"], z[f"re{k}"], z[f"im{k}"], int(m["den"])),
                               e["contraction"], _holo_charges(e)))
        _ROWDEFS = rows
        return rows
    rows = _build_rowdefs()
    BIG.mkdir(parents=True, exist_ok=True)
    arrays = {}
    meta = []
    for k, r in enumerate(rows):
        arrays[f"idx{k}"] = r.poly.idx
        arrays[f"re{k}"] = r.poly.num_re
        arrays[f"im{k}"] = r.poly.num_im
        meta.append({"parameter_id": r.parameter_id, "invariant": r.invariant, "component": r.component,
                     "den": r.poly.den})
    np.savez_compressed(path, meta=json.dumps(meta), **arrays)
    _ROWDEFS = rows
    return rows


def raw_contraction(name: str) -> Poly:
    """prefactor * contraction of invariant `name` before any Re/Im (for X-charge and cross-checks)."""
    if name not in _RAW_CONTRACTIONS:
        e = next(e for e in _load_invariants()["A45_invariants"] if e["name"] == name)
        _RAW_CONTRACTIONS[name] = build_contraction(e["machine_spec"])
    return _RAW_CONTRACTIONS[name]


def new_parameter_ids() -> tuple[str, ...]:
    return tuple(r.parameter_id for r in rowdefs())


# ---------------------------------------------------------------------------------------------------------------------
# polynomial evaluation
# ---------------------------------------------------------------------------------------------------------------------
def poly_value(p: Poly, w: np.ndarray) -> complex | np.ndarray:
    """w: (531,) or (n, 531) complex -> value(s)."""
    c = p.coef()
    if w.ndim == 1:
        prod = np.prod(w[p.idx.astype(np.int64)], axis=1)
        return complex(prod @ c)
    out = np.zeros(w.shape[0], dtype=complex)
    chunk = max(1, int(2e7 // max(1, p.n_terms * p.degree)))
    ix = p.idx.astype(np.int64)
    for s in range(0, w.shape[0], chunk):
        out[s:s + chunk] = np.prod(w[s:s + chunk][:, ix], axis=2) @ c
    return out


def _bincount_c(index: np.ndarray, weights: np.ndarray, n: int) -> np.ndarray:
    return np.bincount(index, weights=weights.real, minlength=n) + 1j * np.bincount(index, weights=weights.imag, minlength=n)


def poly_derivatives(p: Poly, w: np.ndarray, *, hessian: bool = True) -> tuple[complex, np.ndarray, np.ndarray | None]:
    """value, gradient (w.r.t. w), Hessian (w.r.t. w) of a polynomial at one point."""
    N = TOTAL_DIM
    ix = p.idx.astype(np.int64)
    W = w[ix]                     # (T, d)
    c = p.coef()
    d = p.degree
    val = complex(np.prod(W, axis=1) @ c)
    g = np.zeros(N, dtype=complex)
    for a in range(d):
        rest = c * np.prod(np.delete(W, a, axis=1), axis=1) if d > 1 else c.copy()
        g += _bincount_c(ix[:, a], rest, N)
    H = None
    if hessian:
        U = np.zeros(N * N, dtype=complex)
        for a in range(d):
            for b in range(a + 1, d):
                if d > 2:
                    rest = c * np.prod(np.delete(W, [a, b], axis=1), axis=1)
                else:
                    rest = c
                U += _bincount_c(ix[:, a] * N + ix[:, b], rest, N * N)
        U = U.reshape(N, N)
        H = U + U.T
    return val, g, H


@dataclass
class Row:
    parameter_id: str
    value: float
    gradient: np.ndarray
    hessian: np.ndarray | None


def new_rows(q: np.ndarray, *, hessian: bool = True, check_real: bool = True) -> dict[str, Row]:
    """The 34 new exact-X rows at q (531): value, gradient (531), Hessian (531x531)."""
    q = np.asarray(q, dtype=float).reshape(TOTAL_DIM)
    w = w_of_q(q)
    out: dict[str, Row] = {}
    for r in rowdefs():
        v, gw, hw = poly_derivatives(r.poly, w, hessian=hessian)
        gq = _grad_to_q(gw)
        hq = _hess_to_q(hw) if hessian else None
        if check_real:
            scale = max(1.0, abs(v), float(np.max(np.abs(gq))))
            if abs(v.imag) > 1e-9 * scale or np.max(np.abs(gq.imag)) > 1e-9 * scale:
                raise ArithmeticError(f"{r.parameter_id}: imaginary part in a real row")
        out[r.parameter_id] = Row(r.parameter_id, float(v.real), gq.real.copy(),
                                  None if hq is None else np.ascontiguousarray(hq.real))
    return out


def new_row_values(qs: np.ndarray) -> np.ndarray:
    """values of the 34 new rows at many points: (n, 531) -> (n, 34)."""
    qs = np.atleast_2d(np.asarray(qs, dtype=float))
    w = w_of_q(qs)
    return np.stack([poly_value(r.poly, w).real for r in rowdefs()], axis=1)


# =====================================================================================================================
# 4. v20 rows (repo compiler, read-only) embedded in 531
# =====================================================================================================================
_V20_CACHE: OrderedDict[bytes, dict] = OrderedDict()


def v20_parameter_ids() -> tuple[str, ...]:
    return tuple(g2_audit.contract_selection()["parameter_ids"])


def v20_rows(q: np.ndarray, *, embed: bool = True) -> dict[str, Row]:
    """The 51 repo rows at the 486 sub-state of q (A-independent); cached on q[:486]."""
    import g3_candidate_physical_target_audit_v20 as target
    q486, _ = split(q) if np.asarray(q).size == TOTAL_DIM else (np.asarray(q, dtype=float), None)
    key = q486.tobytes()
    if key in _V20_CACHE:
        rows486 = _V20_CACHE[key]
        _V20_CACHE.move_to_end(key)
    else:
        rows486 = target.parameter_rows(chart.unpack(q486))
        _V20_CACHE[key] = rows486
        while len(_V20_CACHE) > 3:
            _V20_CACHE.popitem(last=False)
    out: dict[str, Row] = {}
    for pid, r in rows486.items():
        g = np.asarray(r.gradient, dtype=float)
        h = np.asarray(r.hessian, dtype=float)
        if embed:
            g2 = np.zeros(TOTAL_DIM)
            g2[:DIM486] = g
            h2 = np.zeros((TOTAL_DIM, TOTAL_DIM))
            h2[:DIM486, :DIM486] = h
            g, h = g2, h2
        out[pid] = Row(pid, float(r.value), g, h)
    return out


def v20_row_values(q: np.ndarray) -> dict[str, float]:
    """Values only (repo evaluate_directions, ~1.6 s), same parameter conventions as parameter_rows."""
    q486 = split(q)[0] if np.asarray(q).size == TOTAL_DIM else np.asarray(q, dtype=float)
    live = set(g2_audit.contract_selection()["direction_ids"])
    out = {}
    for d in potential.evaluate_directions(chart.unpack(q486)):
        if d.direction_id not in live:
            continue
        if d.self_conjugate:
            out[f"lambda::{d.direction_id}"] = float(d.value.real)
        else:
            out[f"re::{d.direction_id}"] = float(2.0 * d.value.real)
            out[f"im::{d.direction_id}"] = float(-2.0 * d.value.imag)
    return out


def parameter_rows(q: np.ndarray, *, include_v20: bool = True, hessian: bool = True,
                   v20_backend: str = "repo") -> dict[str, Row]:
    """All 85 rows (51 v20 + 34 new) at q, in the 531 chart.

    v20_backend = "repo" (default; the repository compiler, authoritative) or "poly" (OPTIONAL fast backend of
    v20poly.py: graph-polynomial identities fitted to and validated against the repo; see v20poly_validation.json)."""
    rows: dict[str, Row] = {}
    if include_v20:
        if v20_backend == "repo":
            rows.update(v20_rows(q))
        elif v20_backend == "poly":
            if str(HERE) not in sys.path:
                sys.path.insert(0, str(HERE))
            import v20poly
            rows.update(v20poly.v20_rows_poly(q, hessian=hessian))
        else:
            raise ValueError(v20_backend)
    rows.update(new_rows(q, hessian=hessian))
    return rows


def assemble(rows: Mapping[str, Row], coefficients: Mapping[str, float]) -> tuple[float, np.ndarray, np.ndarray]:
    missing = sorted(set(coefficients).difference(rows))
    if missing:
        raise KeyError(f"coefficients without rows: {missing}")
    V = 0.0
    g = np.zeros(TOTAL_DIM)
    H = np.zeros((TOTAL_DIM, TOTAL_DIM))
    for pid, c in coefficients.items():
        if c == 0:
            continue
        r = rows[pid]
        V += c * r.value
        g += c * r.gradient
        if r.hessian is not None:
            H += c * r.hessian
    return V, g, 0.5 * (H + H.T)


def full_hessian(q: np.ndarray, coefficients: Mapping[str, float], *,
                 v20_backend: str = "repo") -> tuple[float, np.ndarray, np.ndarray]:
    """(V, gradient, 531x531 Hessian) of V = sum c_k I_k; v20 rows are computed only if a v20 coefficient is used."""
    new_ids = set(new_parameter_ids())
    need_v20 = any(k not in new_ids and c != 0 for k, c in coefficients.items())
    rows = parameter_rows(q, include_v20=need_v20, v20_backend=v20_backend)
    return assemble(rows, coefficients)


def save_rows_npz(path: Path, q: np.ndarray, rows: Mapping[str, Row], **extra) -> None:
    ids = sorted(rows)
    np.savez_compressed(path, q=q, ids=np.array(ids), values=np.array([rows[i].value for i in ids]),
                        grads=np.array([rows[i].gradient for i in ids]),
                        hess=np.array([rows[i].hessian for i in ids]), **extra)


# =====================================================================================================================
# 5. symmetry: so(10) generators, U(1)_X, PQ, Goldstone tangents
# =====================================================================================================================
def _elementary(a: int, b: int) -> np.ndarray:
    m = np.zeros((10, 10))
    m[a, b] = 1.0
    m[b, a] = -1.0
    return m


@lru_cache(maxsize=1)
def adjoint_generators_45() -> tuple[np.ndarray, ...]:
    """45x45 integer matrices of delta A = [L_k, A] on the A coordinates."""
    out = []
    basis = [_elementary(c, d) for c, d in PAIRS]
    for a, b in PAIRS:
        L = _elementary(a, b)
        M = np.zeros((A_DIM, A_DIM))
        for col, E in enumerate(basis):
            M[:, col] = (L @ E - E @ L)[_IU]
        out.append(M)
    return tuple(out)


@lru_cache(maxsize=1)
def so10_generators() -> tuple[sparse.csr_matrix, ...]:
    """45 real 531x531 generators: repo 486 blocks (g2_audit) + adjoint block on A."""
    g486 = g2_audit._so10_generator_matrices_cached()
    ad = adjoint_generators_45()
    out = []
    for k in range(45):
        G = sparse.lil_matrix((TOTAL_DIM, TOTAL_DIM))
        g = sparse.csr_matrix(g486[k])
        G[:DIM486, :DIM486] = g
        G[A_SLICE, A_SLICE] = ad[k]
        out.append(sparse.csr_matrix(G))
    return tuple(out)


def generator(vector: Sequence[float]) -> sparse.csr_matrix:
    """sum_k v_k G_k (v in the repo's 45-generator order, e.g. hypercharge.T3R_INTEGER)."""
    gens = so10_generators()
    out = sparse.csr_matrix((TOTAL_DIM, TOTAL_DIM))
    for v, G in zip(vector, gens, strict=True):
        if v:
            out = out + float(v) * G
    return out


def phase_generator(charges: Mapping[str, int]) -> sparse.csr_matrix:
    G = sparse.lil_matrix((TOTAL_DIM, TOTAL_DIM))
    for name, sl in (("H10", H_SLICE), ("Sigma126bar", SIGMA_SLICE), ("S", S_SLICE), ("Phi17", X_SLICE)):
        Q = float(charges.get(name, 0))
        for x in range(sl.start, sl.stop, 2):
            G[x, x + 1] = -Q
            G[x + 1, x] = Q
    return sparse.csr_matrix(G)


@lru_cache(maxsize=1)
def u1x_generator() -> sparse.csr_matrix:
    return phase_generator(U1X_CHARGES)


@lru_cache(maxsize=1)
def pq_generator() -> sparse.csr_matrix:
    return phase_generator(PQ_CHARGES)


def gauge_tangents(q: np.ndarray) -> np.ndarray:
    q = np.asarray(q, dtype=float).reshape(TOTAL_DIM)
    return np.column_stack([G @ q for G in so10_generators()])


def _rank(m: np.ndarray, rel: float = 1e-9) -> int:
    if m.size == 0:
        return 0
    s = np.linalg.svd(m, compute_uv=False)
    return int(np.sum(s > rel * s[0])) if s[0] > 0 else 0


def symmetry_matrix(q: np.ndarray) -> tuple[np.ndarray, dict[str, int]]:
    """531 x 47 tangents (45 so(10), U(1)_X, PQ) and their ranks."""
    q = np.asarray(q, dtype=float).reshape(TOTAL_DIM)
    orbit = gauge_tangents(q)
    ux = u1x_generator() @ q
    pq = pq_generator() @ q
    full = np.column_stack((orbit, ux, pq))
    return full, {"so10_orbit_rank": _rank(orbit), "so10_plus_u1x_rank": _rank(np.column_stack((orbit, ux))),
                  "so10_plus_u1x_plus_pq_rank": _rank(full), "so10_stabilizer_dimension": 45 - _rank(orbit)}


@lru_cache(maxsize=None)
def generator_w(k: int) -> sparse.csr_matrix:
    """so(10) generator k acting on the complex variables w (delta w = G_w w), exact Gaussian integers.

    Real blocks (Phi, A): G_w = G_q.  Complex blocks: the real chart form [[Re K, -Im K], [Im K, Re K]] of a
    complex-linear map K gives delta z = K z, delta zbar = conj(K) zbar."""
    Gq = so10_generators()[k].toarray()
    if np.max(np.abs(Gq[np.ix_(_REAL, _Z)])) or np.max(np.abs(Gq[np.ix_(_REAL, _ZB)])) or \
            np.max(np.abs(Gq[np.ix_(_Z, _REAL)])) or np.max(np.abs(Gq[np.ix_(_ZB, _REAL)])):
        raise AssertionError("generator mixes real and complex blocks")
    K = Gq[np.ix_(_Z, _Z)] + 1j * Gq[np.ix_(_ZB, _Z)]
    if np.max(np.abs(Gq[np.ix_(_Z, _ZB)] + K.imag)) > 1e-13 or np.max(np.abs(Gq[np.ix_(_ZB, _ZB)] - K.real)) > 1e-13:
        raise AssertionError("complex block is not complex-linear")
    Gw = np.zeros((TOTAL_DIM, TOTAL_DIM), dtype=complex)
    Gw[np.ix_(_REAL, _REAL)] = Gq[np.ix_(_REAL, _REAL)]
    Gw[np.ix_(_Z, _Z)] = K
    Gw[np.ix_(_ZB, _ZB)] = np.conj(K)
    R = np.round(Gw.real) + 1j * np.round(Gw.imag)
    if np.max(np.abs(Gw - R)) > 1e-12:
        raise ArithmeticError("generator on w is not a Gaussian-integer matrix")
    return sparse.csr_matrix(R)


def phase_generator_w(charges: Mapping[str, int]) -> sparse.csr_matrix:
    """delta z = i Q z, delta zbar = -i Q zbar (exact)."""
    d = np.zeros(TOTAL_DIM, dtype=complex)
    for name, sl in (("H10", H_SLICE), ("Sigma126bar", SIGMA_SLICE), ("S", S_SLICE), ("Phi17", X_SLICE)):
        Q = int(charges.get(name, 0))
        d[sl.start:sl.stop:2] = 1j * Q
        d[sl.start + 1:sl.stop:2] = -1j * Q
    return sparse.csr_matrix(sparse.diags(d))


def poly_derivation(p: Poly, Gw: sparse.csr_matrix) -> Poly:
    """The polynomial  sum_v (dP/dw_v) (G_w w)_v  computed exactly (integer arithmetic in float64, |.| < 2^52)."""
    G = sparse.csr_matrix(Gw)
    idx = p.idx.astype(np.int64)
    T, d = idx.shape
    out_idx, out_re, out_im = [], [], []
    for pos in range(d):
        v = idx[:, pos]
        cnt = G.indptr[v + 1] - G.indptr[v]
        tot = int(cnt.sum())
        if tot == 0:
            continue
        rep = np.repeat(np.arange(T), cnt)
        e = np.repeat(G.indptr[v], cnt) + (np.arange(tot) - np.repeat(np.cumsum(cnt) - cnt, cnt))
        new = idx[rep].copy()
        new[:, pos] = G.indices[e]
        coef = (p.num_re[rep].astype(float) + 1j * p.num_im[rep].astype(float)) * G.data[e]
        out_idx.append(new)
        out_re.append(coef.real)
        out_im.append(coef.imag)
    if not out_idx:
        return Poly(np.zeros((0, d), dtype=np.int16), np.zeros(0, dtype=np.int64), np.zeros(0, dtype=np.int64), p.den)
    return _aggregate(np.vstack(out_idx), np.concatenate(out_re), np.concatenate(out_im), p.den)


VAR_FIELD = np.array([""] * TOTAL_DIM, dtype=object)
VAR_FIELD[PHI_SLICE] = "Phi210"
VAR_FIELD[A_SLICE] = "A45"
VAR_FIELD[H_SLICE] = "H10"
VAR_FIELD[SIGMA_SLICE] = "Sigma126bar"
VAR_FIELD[S_SLICE] = "S"
VAR_FIELD[X_SLICE] = "Phi17"
VAR_HOLO = np.zeros(TOTAL_DIM, dtype=np.int64)     # +1 for z, -1 for zbar, 0 for real coordinates
VAR_HOLO[_Z] = 1
VAR_HOLO[_ZB] = -1


def monomial_charges(p: Poly, charges: Mapping[str, int]) -> np.ndarray:
    """Exact integer charge of every monomial (sum over variables of Q_field * (+1 z / -1 zbar))."""
    qv = np.array([int(charges.get(f, 0)) for f in VAR_FIELD], dtype=np.int64) * VAR_HOLO
    return qv[p.idx.astype(np.int64)].sum(axis=1)


EXPECTED_GOLDSTONES = {
    "G3211 stage (sigma = 0, H = 0, <S> != 0, <Phi17> != 0)": {
        "breaking": "SO(10) x U(1)_X -> G3211 x Z17  (G3211 = SU(3)c x SU(2)L x U(1)R x U(1)B-L, dim 13)",
        "so10_orbit_rank": 32, "so10_plus_u1x_rank": 33, "so10_plus_u1x_plus_pq_rank": 34,
        "statement": "45 - 13 = 32 broken so(10) generators + 1 (U(1)_X -> Z17 by <Phi17>) = 33 gauge Goldstones; "
                     "+1 global (accidental U(1)_PQ broken by <S>: the axion direction) = 34 symmetry zero modes."},
    "SM stage (sigma != 0, H = 0)": {
        "breaking": "SO(10) x U(1)_X -> SU(3)c x SU(2)L x U(1)Y x Z17",
        "so10_orbit_rank": 33, "so10_plus_u1x_rank": 34, "so10_plus_u1x_plus_pq_rank": 35,
        "statement": "45 - 12 = 33 + 1 (X) = 34 gauge Goldstones, + 1 PQ = 35 symmetry zero modes (as the v20 "
                     "SM candidate: 35)."},
}


# =====================================================================================================================
# 6. labels: Casimirs, charges, isotypic decomposition, projectors, Hessian decomposition
# =====================================================================================================================
@lru_cache(maxsize=1)
def label_operators() -> dict[str, np.ndarray]:
    """Dense 531x531 real operators.  C3, C2L, Y2 built exactly as the repo's sm_label_operators (extended);
    charge generators T3R_op, BL_op, Y_op, T3L_op (real antisymmetric; Hermitian charge = -i * op) and the
    su(3) Cartan pair H1 = J01 - J23, H2 = J23 - J45 used for highest-weight slices."""
    import sympy
    su3 = hypercharge.su3_colour_integer_basis()
    mats = [hypercharge._matrix(v) for v in su3]
    gram = sympy.Matrix(8, 8, lambda i, j: -int(np.trace(mats[i] @ mats[j])))
    lower = gram.inv().cholesky(hermitian=False)
    combos = np.asarray(lower.evalf(30).tolist(), dtype=float)
    su3_g = [generator(v).toarray() for v in su3]
    C3 = np.zeros((TOTAL_DIM, TOTAL_DIM))
    for k in range(8):
        X = sum(combos[a, k] * su3_g[a] for a in range(8))
        C3 -= X @ X
    C2L = np.zeros((TOTAL_DIM, TOTAL_DIM))
    for v in hypercharge.SU2L_INTEGER:
        X = 0.5 * generator(v).toarray()
        C2L -= X @ X
    Y = generator(hypercharge.Y_STANDARD_INTEGER).toarray() / 6.0
    T3R = 0.5 * generator(hypercharge.T3R_INTEGER).toarray()
    BL = -(2.0 / 3.0) * generator(hypercharge.BL_INTEGER).toarray()
    T3L = 0.5 * generator(hypercharge.T3L_INTEGER).toarray()
    H1 = generator(hypercharge._generator_vector({(0, 1): 1, (2, 3): -1})).toarray()
    H2 = generator(hypercharge._generator_vector({(2, 3): 1, (4, 5): -1})).toarray()
    return {"C3": C3, "C2L": C2L, "Y2": -(Y @ Y), "Y_op": Y, "T3R_op": T3R, "BL_op": BL, "T3L_op": T3L,
            "H1": H1, "H2": H2}


_COLOUR = {Fraction(0): ("1", 1), Fraction(4, 3): ("3", 3), Fraction(3): ("8", 8), Fraction(10, 3): ("6", 6),
           Fraction(6): ("10", 10), Fraction(16, 3): ("15", 15)}
_WEAK = {Fraction(0): ("1", 1), Fraction(3, 4): ("2", 2), Fraction(2): ("3", 3), Fraction(15, 4): ("4", 4)}


def _near(value: float, table: Mapping[Fraction, tuple[str, int]]) -> tuple[Fraction, tuple[str, int]]:
    key = min(table, key=lambda f: abs(float(f) - value))
    if abs(float(key) - value) > 1e-6:
        raise ValueError(f"Casimir value {value} not in table")
    return key, table[key]


def _frac(x: float, den: int = 12) -> Fraction:
    f = Fraction(x).limit_denominator(den)
    if abs(float(f) - x) > 1e-6:
        raise ValueError(f"charge {x} is not a small rational")
    return f


@dataclass
class Component:
    kind: str
    label: str
    colour: str
    weak: str
    charges: dict
    irrep_dim: int
    m: int                  # complex multiplicity (copies of the complex irrep)
    self_conjugate: bool
    canonical: bool
    basis: np.ndarray       # 531 x (irrep_dim*m) complex orthonormal (complex isotypic component)
    hw: np.ndarray          # 531 x m complex: highest-weight slice
    conjugate_label: str = ""


def _refine(blocks: list, op: np.ndarray, tol: float) -> list:
    out = []
    for B, lab in blocks:
        Hr = B.conj().T @ op @ B
        Hr = 0.5 * (Hr + Hr.conj().T)
        w, V = np.linalg.eigh(Hr)
        s = 0
        while s < len(w):
            e = s + 1
            while e < len(w) and abs(w[e] - w[s]) <= tol:
                e += 1
            out.append((B @ V[:, s:e], lab + (float(np.mean(w[s:e])),)))
            s = e
    return out


def _fmt(f: Fraction) -> str:
    return ("+" if f > 0 else "") + str(f)


@lru_cache(maxsize=4)
def isotypic_components(kind: str = "G3211", subspace: str = "full") -> tuple[Component, ...]:
    """Complex isotypic decomposition of the (complexified) 531 chart under G3211 or SM.

    subspace: 'full' or a block name (e.g. 'A45') - restricts to that field block (block-diagonal action).
    Labels: G3211 '(c,w)_{T3R=..,B-L=..}', SM '(c,w)_{Y=..}'; conjugate pairs are both returned, `canonical`
    marks the representative (G3211: first nonzero of (T3R, B-L) positive; SM: Y > 0; self-conjugate: itself)."""
    ops = label_operators()
    if subspace == "full":
        B0 = np.eye(TOTAL_DIM, dtype=complex)
    else:
        sl = BLOCKS[subspace]
        B0 = np.zeros((TOTAL_DIM, sl.stop - sl.start), dtype=complex)
        B0[sl, :] = np.eye(sl.stop - sl.start)
    blocks = [(B0, ())]
    tol = 1e-7
    blocks = _refine(blocks, ops["C3"].astype(complex), tol)
    blocks = _refine(blocks, ops["C2L"].astype(complex), tol)
    if kind == "G3211":
        blocks = _refine(blocks, -1j * ops["T3R_op"], tol)
        blocks = _refine(blocks, -1j * ops["BL_op"], tol)
    elif kind == "SM":
        blocks = _refine(blocks, -1j * ops["Y_op"], tol)
    else:
        raise ValueError(kind)
    hgen = -1j * (math.pi * ops["H1"] + math.e * ops["H2"] + math.sqrt(2.0) * 1.37 * ops["T3L_op"])
    comps = []
    for B, lab in blocks:
        _, (cname, cdim) = _near(lab[0], _COLOUR)
        _, (wname, wdim) = _near(lab[1], _WEAK)
        if kind == "G3211":
            t3r, bl = _frac(lab[2]), _frac(lab[3])
            charges = {"T3R": t3r, "B-L": bl, "Y": t3r + bl / 2}
            tri = int(round(3 * float(bl))) % 3
            qtuple = (t3r, bl)
        else:
            y = _frac(lab[2])
            charges = {"Y": y}
            tri = int(round(6 * float(y))) % 3
            qtuple = (y,)
        if cname in ("3", "6"):
            if tri == 0:
                raise AssertionError("colour triplet/sextet with zero triality")
            cname = {("3", 1): "3", ("3", 2): "3bar", ("6", 2): "6", ("6", 1): "6bar"}[(cname, tri)]
        elif tri != 0 and cname in ("1", "8"):
            raise AssertionError("triality inconsistent with colour")
        D = B.shape[1]
        idim = cdim * wdim
        if D % idim:
            raise AssertionError(f"component dimension {D} not a multiple of irrep dimension {idim}")
        m = D // idim
        Hh = B.conj().T @ hgen @ B
        Hh = 0.5 * (Hh + Hh.conj().T)
        w, V = np.linalg.eigh(Hh)
        sel = w > w[-1] - 1e-7
        if int(np.sum(sel)) != m:
            raise AssertionError(f"highest-weight slice of dimension {int(np.sum(sel))} != multiplicity {m}")
        hw = B @ V[:, sel]
        if kind == "G3211":
            lbl = f"({cname},{wname})_{{T3R={_fmt(charges['T3R']) if charges['T3R'] else '0'},B-L={_fmt(charges['B-L']) if charges['B-L'] else '0'}}}"
        else:
            lbl = f"({cname},{wname})_{{Y={_fmt(charges['Y']) if charges['Y'] else '0'}}}"
        selfc = all(x == 0 for x in qtuple) and cname in ("1", "8")
        first = next((x for x in qtuple if x != 0), Fraction(0))
        canonical = selfc or first > 0
        comps.append(Component(kind, lbl, cname, wname, charges, idim, m, selfc, canonical, B, hw))
    # conjugate labels
    by_q = {}
    for c in comps:
        key = (c.colour, c.weak, tuple(c.charges[k] for k in (("T3R", "B-L") if kind == "G3211" else ("Y",))))
        by_q[key] = c
    conjc = {"1": "1", "8": "8", "3": "3bar", "3bar": "3", "6": "6bar", "6bar": "6", "10": "10bar", "15": "15"}
    for c in comps:
        qk = tuple(-c.charges[k] for k in (("T3R", "B-L") if kind == "G3211" else ("Y",)))
        partner = by_q.get((conjc.get(c.colour, c.colour), c.weak, qk))
        if partner is None:
            raise AssertionError(f"conjugate of {c.label} missing")
        c.conjugate_label = partner.label
        if partner.basis.shape != c.basis.shape:
            raise AssertionError("conjugate components of different size")
    return tuple(comps)


def real_basis(c: Component) -> np.ndarray:
    """Orthonormal real basis of the real component spanned by c and its conjugate."""
    M = np.hstack([c.basis.real, c.basis.imag])
    u, s, _ = np.linalg.svd(M, full_matrices=False)
    r = c.basis.shape[1] * (1 if c.self_conjugate else 2)
    if s[r - 1] < 1e-8 or (r < len(s) and s[r] > 1e-8):
        raise AssertionError(f"real span of {c.label} has unexpected rank")
    return u[:, :r]


def real_components(kind: str = "G3211", subspace: str = "full") -> list[dict]:
    """Canonical real components: label, conjugate label, real dimension, real basis (projector = W W^T)."""
    out = []
    for c in isotypic_components(kind, subspace):
        if not c.canonical:
            continue
        W = real_basis(c)
        out.append({"label": c.label, "conjugate": c.conjugate_label, "self_conjugate": c.self_conjugate,
                    "irrep_dim": c.irrep_dim, "complex_multiplicity": c.m, "real_dim": W.shape[1], "W": W,
                    "component": c})
    return out


def a_block_projectors(kind: str = "G3211") -> list[dict]:
    """G3211 / SM components of the 45_H block (real projectors P = W W^T, W 531 x d supported on A45)."""
    return real_components(kind, "A45")


def singlet_basis(kind: str = "G3211") -> np.ndarray:
    """Real orthonormal basis of the G3211- or SM-singlet subspace of the 531 chart."""
    for rc in real_components(kind):
        c = rc["component"]
        if c.colour == "1" and c.weak == "1" and all(v == 0 for v in c.charges.values()):
            return rc["W"]
    return np.zeros((TOTAL_DIM, 0))


def label_vectors(V: np.ndarray) -> list[str]:
    """SM label of each (real) column vector (assumed inside one SM isotypic component)."""
    ops = label_operators()
    out = []
    for v in V.T:
        n = float(v @ v)
        c3 = float(v @ ops["C3"] @ v) / n
        c2 = float(v @ ops["C2L"] @ v) / n
        y2 = float(v @ ops["Y2"] @ v) / n
        try:
            cn = _near(c3, _COLOUR)[1][0]
            wn = _near(c2, _WEAK)[1][0]
            ya = math.sqrt(max(y2, 0.0))
            out.append(f"({cn},{wn})_|Y|={_frac(ya)}")
        except ValueError:
            out.append(f"(C3={c3:.4g},C2L={c2:.4g})_Y2={y2:.4g}")
    return out


def _group(values: np.ndarray, mult: int, rel: float = 1e-7, absol: float = 1e-12) -> list[dict]:
    out = []
    for v in np.sort(values):
        if out and abs(v - out[-1]["mass_squared"]) <= absol + rel * max(1.0, abs(out[-1]["mass_squared"])):
            out[-1]["real_multiplicity"] += mult
        else:
            out.append({"mass_squared": float(v), "real_multiplicity": mult})
    return out


def decompose_hessian(H: np.ndarray, kind: str = "G3211", *, tangents: np.ndarray | None = None) -> dict:
    """Decompose a 531x531 Hessian into G3211 or SM multiplets.

    Per canonical real component: real dimension, the reduced m x m Hermitian matrix on the highest-weight slice
    and its eigenvalues (each with real multiplicity irrep_dim x (1 if self-conjugate else 2)), the eigenvalues of
    the full real block, the Goldstone count (rank of the symmetry tangents projected on the component) and the
    leakage ||H W - W (W^T H W)|| (zero iff H commutes with the group on this component, i.e. at symmetric points)."""
    H = 0.5 * (np.asarray(H, dtype=float) + np.asarray(H, dtype=float).T)
    Tn = None
    if tangents is not None:
        u, s, _ = np.linalg.svd(tangents, full_matrices=False)
        r = int(np.sum(s > 1e-9 * s[0])) if s.size and s[0] > 0 else 0
        Tn = u[:, :r]
    comps = real_components(kind)
    out = []
    total = 0
    max_leak = 0.0
    hscale = max(1.0, float(np.max(np.abs(H))))
    for rc in comps:
        c = rc["component"]
        W = rc["W"]
        Hb = W.T @ H @ W
        leak = float(np.linalg.norm(H @ W - W @ Hb)) / hscale
        max_leak = max(max_leak, leak)
        red = c.hw.conj().T @ H @ c.hw
        red = 0.5 * (red + red.conj().T)
        mult = c.irrep_dim * (1 if c.self_conjugate else 2)
        ev_red = np.linalg.eigvalsh(red)
        ng = None
        if Tn is not None:   # singular values of W^T Tn are cosines (both orthonormal): absolute threshold
            ng = int(np.sum(np.linalg.svd(W.T @ Tn, compute_uv=False) > 1e-6)) if Tn.shape[1] else 0
        out.append({"label": c.label, "conjugate": c.conjugate_label, "real_dim": W.shape[1], "m": c.m,
                    "irrep_dim": c.irrep_dim, "self_conjugate": c.self_conjugate,
                    "reduced_eigenvalues": [float(x) for x in ev_red],
                    "spectrum": _group(ev_red, mult), "block_eigenvalues": np.linalg.eigvalsh(Hb).tolist(),
                    "goldstone_real_dim": ng, "leakage": leak, "reduced_matrix": red})
        total += W.shape[1]
    if total != TOTAL_DIM:
        raise AssertionError(f"components cover {total} != 531 real dimensions")
    return {"kind": kind, "components": out, "max_leakage": max_leak, "real_dimension_total": total}


def reduce_rows(rows: Mapping[str, Row], kind: str = "G3211") -> dict:
    """Per canonical component, the reduced (highest-weight) Hessian of every row: {label: (ids, n_par x m x m)}."""
    ids = sorted(rows)
    out = {}
    for rc in real_components(kind):
        hw = rc["component"].hw
        A = np.array([hw.conj().T @ rows[i].hessian @ hw for i in ids])
        out[rc["label"]] = (ids, 0.5 * (A + np.transpose(A.conj(), (0, 2, 1))))
    return out


# =====================================================================================================================
# 7. G3211 vacuum parametrisation
# =====================================================================================================================
T3R_UNIT = np.asarray(hypercharge.T3R_INTEGER, dtype=float) / math.sqrt(2.0)   # A_67 = A_89 = 1/sqrt2
TBL_UNIT = np.asarray(hypercharge.BL_INTEGER, dtype=float) / math.sqrt(3.0)    # A_01 = A_23 = A_45 = 1/sqrt3


@lru_cache(maxsize=1)
def sigma_std_unit_coordinates() -> np.ndarray:
    """Y = 0 SM singlet z1^z2^z3^z4^z5 of the 126bar (T3R = +1, B-L = -2), unit kinetic norm (repo definition)."""
    import g3_sm_pati_salam_candidate_v20 as candidate
    return np.asarray(candidate.sigma_std_unit_coordinates(), dtype=complex)


def g3211_point(p: float, a: float, omega: float, omega_R: float, omega_BL: float, sigma: complex = 0.0,
                s: complex = 0.0, x: complex = 0.0, h: np.ndarray | None = None,
                sigma_extra: np.ndarray | None = None) -> np.ndarray:
    """q531 of (Phi, H, Sigma, S, Phi17, A) = (p P + a A + omega W, h, sigma sigma_std (+extra), s, x,
    omega_R T3R + omega_BL T_BL), all kinetic-normalised (|q_block| = |coefficient| for unit directions):
      P, A, W: direct.singlet_basis() p, a, omega four-forms (unit chart norm);
      T3R: A_67 = A_89 = 1/sqrt2;  T_BL: A_01 = A_23 = A_45 = 1/sqrt3  (unit chart norm, repo generator vectors);
      sigma_std: Y = 0 singlet z1^..^z5 (T3R = +1, B-L = -2).
    Complex arguments are kinetic-normalised complex field values (z = (x+iy)/sqrt2 convention of the chart)."""
    basis = direct.singlet_basis()
    q = np.zeros(TOTAL_DIM)
    for coef, name in ((p, "p"), (a, "a"), (omega, "omega")):
        for k, t in enumerate(chart.phi_indices()):
            v = basis[name].get(t)
            if v is not None:
                q[PHI_SLICE.start + k] += float(coef) * float(np.real(v))
    if h is not None:
        hv = np.asarray(h, dtype=complex).reshape(10)
        q[H_SLICE.start:H_SLICE.stop:2] = SQRT2 * hv.real
        q[H_SLICE.start + 1:H_SLICE.stop:2] = SQRT2 * hv.imag
    zs = complex(sigma) * sigma_std_unit_coordinates()
    if sigma_extra is not None:
        zs = zs + np.asarray(sigma_extra, dtype=complex).reshape(126)
    q[SIGMA_SLICE.start:SIGMA_SLICE.stop:2] = SQRT2 * zs.real
    q[SIGMA_SLICE.start + 1:SIGMA_SLICE.stop:2] = SQRT2 * zs.imag
    for sl, val in ((S_SLICE, complex(s)), (X_SLICE, complex(x))):
        q[sl.start] = SQRT2 * val.real
        q[sl.start + 1] = SQRT2 * val.imag
    q[A_SLICE] = float(omega_R) * T3R_UNIT + float(omega_BL) * TBL_UNIT
    return q


def g3211_coordinates(q: np.ndarray) -> dict[str, Any]:
    """Project q onto the vacuum parametrisation (p, a, omega, omega_R, omega_BL, sigma, s, x) + residual norm."""
    basis = direct.singlet_basis()
    q = np.asarray(q, dtype=float)
    out = {}
    rec = np.zeros(TOTAL_DIM)
    for name, key in (("p", "p"), ("a", "a"), ("omega", "omega")):
        v = np.zeros(TOTAL_DIM)
        for k, t in enumerate(chart.phi_indices()):
            if t in basis[key]:
                v[k] = float(np.real(basis[key][t]))
        out[name] = float(v @ q)
        rec += out[name] * v
    for name, u in (("omega_R", T3R_UNIT), ("omega_BL", TBL_UNIT)):
        out[name] = float(u @ q[A_SLICE])
        rec[A_SLICE] += out[name] * u
    zs = (q[SIGMA_SLICE.start:SIGMA_SLICE.stop:2] + 1j * q[SIGMA_SLICE.start + 1:SIGMA_SLICE.stop:2]) / SQRT2
    ss = sigma_std_unit_coordinates()
    out["sigma"] = complex(np.vdot(ss, zs))
    out["s"] = complex(q[S_SLICE.start] + 1j * q[S_SLICE.start + 1]) / SQRT2
    out["x"] = complex(q[X_SLICE.start] + 1j * q[X_SLICE.start + 1]) / SQRT2
    rec2 = g3211_point(out["p"], out["a"], out["omega"], out["omega_R"], out["omega_BL"], out["sigma"], out["s"], out["x"])
    out["residual_norm"] = float(np.linalg.norm(q - rec2))
    return out


def hessian_and_decomposition(q: np.ndarray, coefficients: Mapping[str, float],
                              kinds: Sequence[str] = ("G3211", "SM"), *, v20_backend: str = "repo") -> dict:
    """Full 531x531 Hessian of V = sum c_k I_k at q, its spectrum, and its G3211 / SM decompositions."""
    V, g, H = full_hessian(q, coefficients, v20_backend=v20_backend)
    T, ranks = symmetry_matrix(q)
    ev = np.linalg.eigvalsh(H)
    return {"V": V, "gradient": g, "hessian": H, "eigenvalues": ev, "symmetry_ranks": ranks,
            "decompositions": {k: decompose_hessian(H, k, tangents=T) for k in kinds}}


if __name__ == "__main__":
    t0 = time.time()
    rows = rowdefs()
    print(f"{len(rows)} new rows built/loaded in {time.time() - t0:.1f}s from {_cache_path()}")
    for r in rows:
        print(f"  {r.parameter_id:28s} degree {r.poly.degree} terms {r.poly.n_terms:8d} den {r.poly.den}")
