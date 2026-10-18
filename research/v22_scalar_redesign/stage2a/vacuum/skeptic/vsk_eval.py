#!/usr/bin/env python3
"""VACUUM SKEPTIC - my own independent evaluator of V_c(q) on the 531 chart of v22-L2.

Independence (what is NOT used): vc.FastV, v20poly, chart531's compiled polynomials and chart531's tables.
  * 51 v20 rows: the REPOSITORY direction evaluator potential.evaluate_directions (live_g2_arbitrary_component_
    potential_values_v20) at the repo FieldState, with the repo parameter conventions (lambda:: = I, re:: = 2 Re I,
    im:: = -2 Im I) - the authoritative code path, different from both v20poly (used by the descents) and the
    parameter_rows/adapters path.
  * 34 A45 rows: my own tensor code.  Tensors P_abcd, H_a, D_abcde, A_ab are built directly from the chart coordinates
    (repo phi_indices order; the repo's 126 anti-self-dual basis {first: 1, second: i sign} written out by hand here,
    no add_forms thresholds), then each invariants.json machine_spec is evaluated literally:
       - no eps: one numpy einsum of the full index string;
       - eps: lower-case-connected groups are einsum-contracted to block tensors carrying their eps letters, each block
         is antisymmetrised, and the 10!-term eps sum is done EXACTLY as a sum over ordered set partitions of {0..9}
         into the block sizes (3150 terms for 4+4+2, 18900 for 4+2+2+2) times prod n_b! and the sign of the block
         order (a third method: chart531 uses a compiled polynomial, the chart skeptic the literal 10! permutations).
  * gauge transformations: finite SO(10) rotations R = expm(Omega) applied to the TENSORS (P -> R^4 P, D -> R^5 D,
    A -> R A R^T, H -> R H) and re-packed into chart coordinates by my own packer; U(1)_X and PQ phases on the
    complex blocks with the repo charge tables.
Labels: float64 evaluation of exact formulas (NUM).
"""
from __future__ import annotations

import itertools
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
from scipy.linalg import expm

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
MODEL = HERE.parents[1] / "model"
BIGV = Path(r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory"
            r"\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\v22_stage2a_big\vacuum")
BIGS = Path(r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory"
            r"\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\v22_stage2a_big\vacuum_skeptic")
BIGS.mkdir(parents=True, exist_ok=True)
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import live_g2_canonical_486_field_chart_v20 as rchart  # noqa: E402
import live_g2_arbitrary_component_potential_values_v20 as potential  # noqa: E402
import gauged_u1x_g2_derivative_audit_v20 as g2_audit  # noqa: E402
import exact_gauged_u1x_physical_quotient_v20 as quotient  # noqa: E402

N486 = rchart.TOTAL_DIM
NT = N486 + 45
SQ2 = math.sqrt(2.0)
PHS, HS, SGS, SS, XS = rchart.PHI_SLICE, rchart.H_SLICE, rchart.SIGMA_SLICE, rchart.S_SLICE, rchart.X_SLICE
AS = slice(N486, NT)
PAIRS = list(itertools.combinations(range(10), 2))
PHI_IDX = list(rchart.phi_indices())
assert len(PHI_IDX) == 210 and all(tuple(sorted(t)) == tuple(t) for t in PHI_IDX)


def perm_sign(seq) -> int:
    seq = list(seq)
    inv = sum(1 for i in range(len(seq)) for j in range(i + 1, len(seq)) if seq[i] > seq[j])
    return -1 if inv % 2 else 1


# ---------------------------------------------------------------------------------------------------------------------
# chart -> tensors (own construction)
# ---------------------------------------------------------------------------------------------------------------------
def _scatter_tables(sorted_tuples, k):
    """flat indices of every permutation of every sorted k-tuple, the source tuple id and the sign."""
    perms = list(itertools.permutations(range(k)))
    psg = np.array([perm_sign(p) for p in perms], dtype=float)
    flat, src, sg = [], [], []
    for t_id, t in enumerate(sorted_tuples):
        for p, s in zip(perms, psg):
            idx = [t[i] for i in p]
            f = 0
            for i in idx:
                f = f * 10 + i
            flat.append(f)
            src.append(t_id)
            sg.append(s)
    return np.array(flat), np.array(src), np.array(sg)


_PF, _PSRC, _PSG = _scatter_tables(PHI_IDX, 4)
FIVE = list(itertools.combinations(range(10), 5))
FIVE_ID = {t: i for i, t in enumerate(FIVE)}
_DF, _DSRC, _DSG = _scatter_tables(FIVE, 5)
# repo anti-self-dual basis, written out by hand: state_k = {first: 1, second: i*sign(first+second)} in the order of
# direct.anti_self_dual_five_form_basis (checked against the repo basis in selftest())
_BASIS = []
_seen = set()
for _init in itertools.combinations(range(10), 5):
    if _init in _seen:
        continue
    _comp = tuple(sorted(set(range(10)).difference(_init)))
    _seen.add(_init)
    _seen.add(_comp)
    _first, _second = (_init, _comp) if _init < _comp else (_comp, _init)
    _BASIS.append((_first, _second, perm_sign(_first + _second)))
assert len(_BASIS) == 126
_BFIRST = np.array([FIVE_ID[b[0]] for b in _BASIS])
_BSECOND = np.array([FIVE_ID[b[1]] for b in _BASIS])
_BSIGN = np.array([b[2] for b in _BASIS], dtype=float)
_IU = (np.array([p[0] for p in PAIRS]), np.array([p[1] for p in PAIRS]))


def tensors(q):
    q = np.asarray(q, float).reshape(NT)
    P = np.zeros(10 ** 4)
    P[_PF] = _PSG * q[PHS][_PSRC]
    P = P.reshape((10,) * 4)
    h = (q[HS][0::2] + 1j * q[HS][1::2]) / SQ2
    z = (q[SGS][0::2] + 1j * q[SGS][1::2]) / SQ2
    Dsorted = np.zeros(252, dtype=complex)
    Dsorted[_BFIRST] += z
    Dsorted[_BSECOND] += 1j * _BSIGN * z
    D = np.zeros(10 ** 5, dtype=complex)
    D[_DF] = _DSG * Dsorted[_DSRC]
    D = D.reshape((10,) * 5)
    S = complex((q[SS][0] + 1j * q[SS][1]) / SQ2)
    T = complex((q[XS][0] + 1j * q[XS][1]) / SQ2)
    A = np.zeros((10, 10))
    A[_IU] = q[AS]
    A = A - A.T
    return {"P": P, "H": h, "D": D, "S": S, "T": T, "A": A}


def pack(t) -> np.ndarray:
    """tensors -> 531 chart (inverse of tensors(); assumes antisymmetric P, D anti-self-dual)."""
    q = np.zeros(NT)
    P = t["P"].reshape(-1)
    q[PHS] = np.array([P[((a * 10 + b) * 10 + c) * 10 + d].real for a, b, c, d in PHI_IDX])
    h = t["H"]
    q[HS][0::2] = SQ2 * h.real
    q[HS][1::2] = SQ2 * h.imag
    D = t["D"].reshape(-1)
    fl = np.array([sum(i * 10 ** (4 - k) for k, i in enumerate(f)) for f in FIVE])
    Ds = D[fl]
    # z_k = <state_k, D>_kin = (1/2) (conj(1) D[first] + conj(i sign) D[second])
    z = 0.5 * (Ds[_BFIRST] - 1j * _BSIGN * Ds[_BSECOND])
    q[SGS][0::2] = SQ2 * z.real
    q[SGS][1::2] = SQ2 * z.imag
    q[SS] = [SQ2 * t["S"].real, SQ2 * t["S"].imag]
    q[XS] = [SQ2 * t["T"].real, SQ2 * t["T"].imag]
    q[AS] = t["A"][_IU]
    return q


def rotate(t, R):
    out = dict(t)
    P = t["P"]
    for ax in range(4):
        P = np.moveaxis(np.tensordot(R, P, axes=([1], [ax])), 0, ax)
    D = t["D"]
    for ax in range(5):
        D = np.moveaxis(np.tensordot(R, D, axes=([1], [ax])), 0, ax)
    out["P"], out["D"] = P, D
    out["H"] = R @ t["H"]
    out["A"] = R @ t["A"] @ R.T
    return out


XCH = {"H": -2, "D": -2, "S": 4, "T": 17}


def phase(t, charges, theta):
    out = dict(t)
    for k, ch in charges.items():
        out[k] = t[k] * np.exp(1j * ch * theta)
    return out


def pq_charges():
    pq = quotient.PQ_CHARGES
    return {"H": pq["H10"], "D": pq["Sigma126bar"], "S": pq["S"], "T": pq["Phi17"]}


# ---------------------------------------------------------------------------------------------------------------------
# A45 rows (literal machine_spec evaluation; eps sums by ordered set partitions)
# ---------------------------------------------------------------------------------------------------------------------
INV = json.load(open(MODEL / "invariants.json", encoding="utf-8"))
_PARTS = {}


def _partitions(sizes):
    key = tuple(sizes)
    if key in _PARTS:
        return _PARTS[key]
    blocks_idx = [[] for _ in sizes]
    signs = []

    def rec(remaining, b, chosen):
        if b == len(sizes):
            seq = tuple(x for blk in chosen for x in blk)
            signs.append(perm_sign(seq))
            for j, blk in enumerate(chosen):
                f = 0
                for i in blk:
                    f = f * 10 + i
                blocks_idx[j].append(f)
            return
        for comb in itertools.combinations(remaining, sizes[b]):
            rest = tuple(x for x in remaining if x not in comb)
            rec(rest, b + 1, chosen + [comb])

    rec(tuple(range(10)), 0, [])
    out = ([np.array(x) for x in blocks_idx], np.array(signs, dtype=float),
           float(np.prod([math.factorial(s) for s in sizes])))
    _PARTS[key] = out
    return out


def _alt(T):
    k = T.ndim
    if k <= 1:
        return T
    out = np.zeros_like(T)
    for p in itertools.permutations(range(k)):
        out = out + perm_sign(p) * np.transpose(T, p)
    return out / math.factorial(k)


TY = {"A45": "A", "Phi210": "P", "H10": "H", "H10^dag": "Hb", "Delta126bar": "D", "Delta126bar^dag": "Db"}


def _tensor(t, ty):
    return {"A": t["A"], "P": t["P"], "H": t["H"], "Hb": np.conj(t["H"]), "D": t["D"], "Db": np.conj(t["D"])}[ty]


def eval_spec(t, spec) -> complex:
    tens = [_tensor(t, TY[x]) for x in spec["tensors"]]
    idxs = list(spec["indices"])
    upper = [ch for s in idxs for ch in s if ch.isupper()]
    if not upper:
        v = complex(np.einsum(",".join(idxs) + "->", *tens, optimize=True))
    else:
        assert len(upper) == 10 and len(set(upper)) == 10
        pos = {ch: k for k, ch in enumerate(upper)}
        n = len(tens)
        parent = list(range(n))

        def find(x):
            while parent[x] != x:
                x = parent[x]
            return x
        for i in range(n):
            for j in range(i + 1, n):
                if set(c for c in idxs[i] if c.islower()) & set(c for c in idxs[j] if c.islower()):
                    parent[find(i)] = find(j)
        groups = {}
        for i in range(n):
            groups.setdefault(find(i), []).append(i)
        blocks = []
        for members in sorted(groups.values(), key=lambda m: min(m)):
            ups = "".join(ch for i in members for ch in idxs[i] if ch.isupper())
            T = np.einsum(",".join(idxs[i] for i in members) + "->" + ups, *[tens[i] for i in members], optimize=True)
            blocks.append((_alt(np.asarray(T, dtype=complex)), [pos[ch] for ch in ups]))
        rho = [p for _, ps in blocks for p in ps]
        sg_rho = perm_sign(rho)
        sizes = [len(ps) for _, ps in blocks]
        bidx, sgn, fact = _partitions(sizes)
        val = sgn.astype(complex)
        for (T, _), fi in zip(blocks, bidx):
            val = val * T.reshape(-1)[fi]
        v = complex(sg_rho * fact * val.sum())
    for s in spec.get("singlet_factors", []) or []:
        v *= {"S": t["S"], "Sb": np.conj(t["S"]), "T": t["T"], "Tb": np.conj(t["T"])}[s]
    v *= {"1": 1.0, "1/2": 0.5, "i": 1j}[spec["prefactor"]]
    if spec["part"] == "Re":
        v = complex(v.real)
    elif spec["part"] == "Im":
        v = complex(v.imag)
    return v


def a_rows(t) -> dict:
    out = {}
    for e in INV["A45_invariants"]:
        v = eval_spec(t, e["machine_spec"])
        if e["real_parameters"] == 2:
            out[f"re::{e['name']}"] = 2.0 * v.real
            out[f"im::{e['name']}"] = -2.0 * v.imag
        else:
            assert abs(v.imag) <= 1e-9 * max(1.0, abs(v)), (e["name"], v)
            out[f"lambda::{e['name']}"] = v.real
    return out


# ---------------------------------------------------------------------------------------------------------------------
# v20 rows: repo evaluate_directions
# ---------------------------------------------------------------------------------------------------------------------
_LIVE = None


def v20_rows(q) -> dict:
    global _LIVE
    if _LIVE is None:
        _LIVE = set(g2_audit.contract_selection()["direction_ids"])
    st = rchart.unpack(np.asarray(q, float)[:N486])
    out = {}
    for d in potential.evaluate_directions(st):
        if d.direction_id not in _LIVE:
            continue
        if d.self_conjugate:
            out[f"lambda::{d.direction_id}"] = float(d.value.real)
        else:
            out[f"re::{d.direction_id}"] = float(2.0 * d.value.real)
            out[f"im::{d.direction_id}"] = float(-2.0 * d.value.imag)
    return out


def v20_rows_from_tensors(t) -> dict:
    """repo rows at a state built from my tensors (repo FieldState, validated by the repo)."""
    return v20_rows(pack(t))


def all_rows(q) -> dict:
    r = v20_rows(q)
    r.update(a_rows(tensors(q)))
    return r


def V(q, cdict) -> float:
    r = all_rows(q)
    missing = set(cdict) - set(r)
    assert not missing, missing
    return float(sum(c * r[k] for k, c in cdict.items()))


def load_c(sol):
    z = np.load(sol if os.path.isabs(str(sol)) else BIGV / sol)
    ids = [str(x) for x in z["ids"]]
    return dict(zip(ids, map(float, z["c"])))


def random_rotation(rng, scale=1.0):
    Om = rng.normal(size=(10, 10)) * scale
    return expm(Om - Om.T)


def selftest():
    """my basis == repo basis; pack(tensors(q)) == q; repo FieldState from my tensors matches rchart.unpack."""
    import direct_phi_h_sigmabar_tensor_v20 as direct
    rb = rchart.sigma_basis()
    err = 0.0
    for k, st in enumerate(rb):
        f, s, sg = _BASIS[k]
        err = max(err, abs(st.get(f, 0) - 1.0), abs(st.get(s, 0) - 1j * sg), len(st) - 2)
    rng = np.random.default_rng(7)
    q = rng.normal(size=NT)
    t = tensors(q)
    e_pack = float(np.max(np.abs(pack(t) - q)))
    st = rchart.unpack(q[:N486])
    e_phi = max(abs(st.phi.get(tuple(i), 0) - t["P"][tuple(i)]) for i in PHI_IDX)
    e_sig = max(abs(v - t["D"][k]) for k, v in st.sigma.items())
    hod = direct.hodge_star({k: t["D"][k] for k in FIVE})
    e_asd = max(abs(hod.get(k, 0) + 1j * t["D"][k]) for k in FIVE)
    e_h = float(np.max(np.abs(st.h - t["H"])))
    return {"basis_err": float(err), "pack_roundtrip": e_pack, "phi_vs_repo_unpack": float(e_phi),
            "sigma_vs_repo_unpack": float(e_sig), "anti_self_dual": float(e_asd), "H_vs_repo": e_h}


if __name__ == "__main__":
    print(selftest())
