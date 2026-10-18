"""SKEPTIC extras for the vacuum test:
 E1  sign-definite generator portals in CHART normalisation: ||G_X(A) q_X||^2 (real chart norm, G(A) = sum_ab A_ab G_ab
     from MY generators) fitted on the chart rows of the family, rationalised and re-verified;
 E2  multiplet machinery: at a G3211 point, spectrum of a random new-row Hessian == union of decompose_hessian block
     spectra; Goldstone count with MY tangents; (8,1)_{0,0} and (8,3)_{0,0} multiplicities vs group theory (3 and 1);
 E3  SM point: same with sigma != 0.
"""
from __future__ import annotations

import sys
import time
from fractions import Fraction
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sk_common as C  # noqa: E402
import chart531 as CH  # noqa: E402

LOG = open(C.HERE / "sk_extra.log", "w", encoding="utf-8")
OUT = C.HERE / "sk_extra.json"
rng = np.random.default_rng(4242)


def log(m):
    C.log(m, LOG)


def e1_portals(G):
    ids = list(CH.new_parameter_ids())
    col = {p: k for k, p in enumerate(ids)}
    fam = {"H": ["lambda::A14_AAHH_1", "lambda::A15_AAHH_2"],
           "D": ["lambda::A18_AADD_1", "lambda::A19_AADD_2", "lambda::A20_AADD_3"],
           "P": ["lambda::A08_PPAA_1", "lambda::A09_PPAA_2", "lambda::A10_PPAA_3", "lambda::A11_PPAA_4"]}
    Q = rng.normal(size=(24, C.NTOT))
    V = CH.new_row_values(Q)
    out = {}
    for X, rows in fam.items():
        sl = C.SL[X]
        y = []
        for q in Q:
            GA = sum(q[C.N486 + k] * G[k][sl, sl] for k in range(45))
            v = GA @ q[sl]
            y.append(float(v @ v))
        y = np.array(y)
        M = V[:, [col[r] for r in rows]]
        c, *_ = np.linalg.lstsq(M, y, rcond=None)
        cr = [Fraction(x).limit_denominator(20000) for x in c]
        resid = float(np.max(np.abs(M @ np.array([float(x) for x in cr]) - y)) / np.max(np.abs(y)))
        out[f"||G_{X}(A) q_{X}||^2 (real chart norm)"] = {"rows": rows, "coefficients": [str(x) for x in cr],
                                                         "max_rel_residual": resid, "exact": resid < 1e-12}
    log(f"E1 portals: {out}")
    return out


def e2_decomposition(G, sigma):
    q = CH.g3211_point(0.6, -0.5, 0.4, 0.3, 0.2, sigma=sigma, s=0.01, x=2.0)
    ids = list(CH.new_parameter_ids())
    coeffs = {p: float(rng.normal()) for p in ids}
    V, g, H = CH.full_hessian(q, coeffs)
    T = np.column_stack([Gk @ q for Gk in G] + [C.phase_rotation({}) @ q * 0])
    ux = np.zeros(C.NTOT)
    for f, xq in (("H", -2), ("D", -2), ("S", 4), ("T", 17)):
        s = C.SL[f]
        ux[s.start:s.stop:2] = -xq * q[s.start + 1:s.stop:2]
        ux[s.start + 1:s.stop:2] = xq * q[s.start:s.stop:2]
    pq = np.zeros(C.NTOT)
    for f, xq in (("H", -2), ("D", -2), ("S", 4), ("T", 0)):
        s = C.SL[f]
        pq[s.start:s.stop:2] = -xq * q[s.start + 1:s.stop:2]
        pq[s.start + 1:s.stop:2] = xq * q[s.start:s.stop:2]
    T = np.column_stack([Gk @ q for Gk in G] + [ux, pq])
    kind = "G3211" if sigma == 0 else "SM"
    dec = CH.decompose_hessian(H, kind, tangents=T)
    ev_full = np.sort(np.linalg.eigvalsh(H))
    ev_union = np.sort(np.concatenate([np.asarray(c["block_eigenvalues"]) for c in dec["components"]]))
    # reduced spectra with multiplicities must reproduce the full spectrum too
    red = []
    for c in dec["components"]:
        mult = c["irrep_dim"] * (1 if c["self_conjugate"] else 2)
        for x in c["reduced_eigenvalues"]:
            red.extend([x] * mult)
    red = np.sort(np.array(red))
    scale = max(1.0, float(np.max(np.abs(ev_full))))
    s = np.linalg.svd(T, compute_uv=False)
    rankT = int(np.sum(s > 1e-9 * s[0]))
    octets = {c["label"]: c["m"] for c in dec["components"] if c["label"].startswith("(8,")}
    res = {"kind": kind, "max_leakage": dec["max_leakage"],
           "full_vs_block_union_max_abs_diff_rel": float(np.max(np.abs(ev_full - ev_union)) / scale),
           "full_vs_reduced_with_multiplicity_max_abs_diff_rel": float(np.max(np.abs(ev_full - red)) / scale)
           if red.size == ev_full.size else f"size mismatch {red.size}",
           "goldstone_sum_over_components": int(sum(c["goldstone_real_dim"] or 0 for c in dec["components"])),
           "rank_of_my_symmetry_tangents": rankT, "octet_components_m": octets,
           "n_components": len(dec["components"])}
    log(f"E2 {kind}: {res}")
    return res


def main():
    t0 = time.time()
    G = C.my_generators531()
    out = {"E1_portals": e1_portals(G)}
    out["E2_G3211"] = e2_decomposition(G, 0.0)
    out["E3_SM"] = e2_decomposition(G, 0.05)
    out["time_s"] = time.time() - t0
    C.json_dump(out, OUT)
    log(f"wrote {OUT} ({time.time() - t0:.1f}s)")


if __name__ == "__main__":
    main()
