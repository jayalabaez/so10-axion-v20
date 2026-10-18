#!/usr/bin/env python3
"""Stage-2a "model": the sign-definite 45 'generator portals' |T_A X|^2 expressed EXACTLY in the invariants.json basis.

For X in {H10, Delta126bar, Phi210} the generator action of A (so(10) acting on each antisymmetric slot) is
    (A.H)_a = A_ab H_b,   (A.X)_{a1..ak} = sum_{slots s} A_{a_s b} X_{a1..b..ak},
and the portals  |A.H|^2 = sum_a |(A.H)_a|^2,  |A.D|^2 = (1/5!) sum |(A.D)_{a1..a5}|^2,
|A.P|^2 = (1/4!) sum ((A.P)_{abcd})^2  are manifestly >= 0.  Their coefficients in the explicit basis
(A14,A15 | A18..A20 | A08..A11) are fitted on random configurations and then rationalised and re-verified to
machine precision (NUM, exact rational coefficients).  Output: portal_identities_v22.json.
"""
from __future__ import annotations

import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_invariants_v22 as BI  # noqa: E402
import explicit_basis_v22 as EB  # noqa: E402


def act(A, X):
    k = X.ndim
    out = np.zeros_like(X)
    for s in range(k):
        # contract A_{a_s b} X_{..b..}: move slot s to front, apply, move back
        Xs = np.moveaxis(X, s, 0)
        Ys = np.tensordot(A, Xs, axes=([1], [0]))
        out = out + np.moveaxis(Ys, 0, s)
    return out


def portal(name, F):
    A = F["A"]
    if name == "H":
        v = A @ F["H"]; return float(np.vdot(v, v).real)
    if name == "D":
        v = act(A, F["D"]); return float(np.vdot(v, v).real) / 120.0
    if name == "P":
        v = act(A, F["P"]); return float((v * v).sum()) / 24.0
    raise KeyError(name)


def fit(name, basis_names, samples):
    specs = [next(s for s in BI.NEW if s[0] == b) for b in basis_names]
    M = np.array([[BI.value(sp, F).real for sp in specs] for F in samples])
    y = np.array([portal(name, F) for F in samples])
    c, *_ = np.linalg.lstsq(M, y, rcond=None)
    cr = [Fraction(x).limit_denominator(720) for x in c]
    resid = np.max(np.abs(M @ np.array([float(x) for x in cr]) - y)) / np.max(np.abs(y))
    return {"portal": name, "basis": basis_names, "coefficients": [str(x) for x in cr],
            "max_rel_residual_with_rational_coefficients": float(resid), "exact_identity": bool(resid < 1e-12)}


def main():
    rng = np.random.default_rng(777)
    samples = []
    for _ in range(12):
        F = EB.random_fields(rng); F["S"] = 0; F["T"] = 0
        samples.append(F)
    out = {}
    out["|A.H|^2"] = fit("H", ["A14_AAHH_1", "A15_AAHH_2"], samples)
    out["|A.D|^2"] = fit("D", ["A18_AADD_1", "A19_AADD_2", "A20_AADD_3"], samples)
    out["|A.P|^2"] = fit("P", ["A08_PPAA_1", "A09_PPAA_2", "A10_PPAA_3", "A11_PPAA_4"], samples)
    for k, v in out.items():
        print(k, v)
    out["note"] = ("A15 itself equals |A.H|^2 = sum_a |A_ab H_b|^2 >= 0 and A14 = (A.A)(H^dag H) >= 0; "
                   "the D and P portals are the fitted combinations.  A real 45 vev A = w_R T3R + w_BL T_BL gives "
                   "|A.X|^2 = sum over components |(w_R T3R + w_BL (B-L)) charge|^2 |X_comp|^2 (zero exactly on the "
                   "T3R = B-L = 0 components).")
    (HERE / "portal_identities_v22.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
