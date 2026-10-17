"""R2-V item (4), extension: the round-1 oracle allows at most ONE derivative (only for odd/odd fermion parity).
A genuine Planck operator can also be a LOW-dimension monomial M (d(M) <= 4, which the oracle never tests because
it requires 5 <= d) dressed with field strengths and/or extra derivatives to reach d >= 5, e.g. a dipole
psi_a sigma.F psi_b.  Dressings carry no X, centre or accidental charge; a field strength F_{alpha beta} costs 2
and cannot fix single-index Lorentz parity, so it is equivalent to two derivatives for the purpose of the
necessary conditions.  Here an explicit derivative item D (dimension 1, flips both Lorentz parities) is added to
the exact DP, and the final state must have even/even parity: this covers every number of derivatives and field
strengths.  The certificate is re-checked for 5 <= d <= 24.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import dual_dp as dd

HERE = Path(__file__).resolve().parent


def main():
    its = dd.items()
    its.append({"label": "D", "X": 0, "z": 0, "v": 0, "w": 2, "u": 1, "b": 1, "q": (0,) * 6})
    xmax = max(abs(i["X"]) for i in its)
    dmax = 24
    best, par = dd.dp(its, 2 * dmax, xmax)
    rows = []
    worst = None
    for d in range(1, dmax + 1):
        v = int(best[2 * d, xmax, 0, 0, 0])
        if v <= dd.NEG // 2:
            rows.append({"d": d, "max_4mu.q": None})
            continue
        mono = dd.backtrack(best, par, its, 2 * d, xmax, 0, 0)
        exc = v - 4 * (d - 4)
        rows.append({"d": d, "max_4mu.q": v, "excess_x4": exc, "monomial": mono})
        if d >= 5 and (worst is None or exc > worst[0]):
            worst = (exc, d, mono)
    # low-dimension monomials (d <= 4) without dressing: their max 4 mu.q (these must have q = 0 if renormalizable)
    its0 = dd.items()
    best0, par0 = dd.dp(its0, 8, xmax)
    low = {}
    for W in range(0, 9):
        for pr in (0, 1):
            v = int(best0[W, xmax, 0, pr, pr])
            if v > dd.NEG // 2:
                low["W=%d parity=%d (d=%s)" % (W, pr, W / 2)] = {"max_4mu.q": v, "monomial": dd.backtrack(best0, par0, its0, W, xmax, pr, pr)}
    out = {"rows": rows, "max_excess_x4_5<=d<=24": worst[0], "at": worst[1], "monomial": worst[2],
           "certificate_holds_with_any_dressing": worst[0] <= 0, "undressed_low_dim_monomials": low}
    (HERE / "dual_dp_dressed.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    for r in rows:
        print(r)
    print("low-dim:", json.dumps(low))
    print("max excess (x4) with arbitrary derivative/field-strength dressing, 5<=d<=24:", worst)


if __name__ == "__main__":
    main()
