"""R2-V: rep-level SO(10) singlet table for fermion bilinears x scalar (own counter), sym/antisym split for identical
reps, the Spin(10)-centre lemma X = z + G2 (mod 4) on every scalar, and the g_X bound check."""
from __future__ import annotations

import json
import math
from pathlib import Path

import so10_chars as so
from b63_verify import sym_antisym_singlets

HERE = Path(__file__).resolve().parent
PAIRS = [(16, 16), (16, -16), (-16, -16), (10, 10), (16, 10), (-16, 10), (1, 1), (1, 10), (1, 16), (1, -16)]
SCAL = {"none": None, "1": 1, "10": 10, "120": 120, "126": 126, "126bar": -126, "210": 210, "45": 45, "54": 54}


def main():
    tab = {}
    for a, b in PAIRS:
        row = {}
        for sn, sr in SCAL.items():
            reps = [a, b] + ([sr] if sr is not None else [])
            n = so.singlets_of(reps)
            entry = {"singlets": n}
            if a == b and a != 1:
                s2, a2 = sym_antisym_singlets(a, sr if sr is not None else 1)
                entry.update({"sym": s2, "antisym": a2})
            row[sn] = entry
        tab["%s x %s" % (a, b)] = row
    zc = {"Phi210": (0, 0, 0), "Delta": (-2, 2, 0), "H10": (-2, 2, 0), "S": (4, 0, 0), "Phi17": (17, 0, 1)}
    lemma = {k: ((x - z - g) % 4 == 0) for k, (x, z, g) in zc.items()}
    ax_inv_MU = 1 + 101203 / (2 * math.pi) * math.log(2.435e18 / 2.13e16)
    out = {"bilinear_x_scalar_singlets": tab, "centre_lemma_X=z+G2_mod4": lemma,
           "alpha_X^-1(M_U) for alpha_X(MPl)=1, b_X=101203": ax_inv_MU, "g_X(M_U) max": math.sqrt(4 * math.pi / ax_inv_MU)}
    (HERE / "rep_table.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    for k, row in tab.items():
        print(k, {s: (e["singlets"] if "sym" not in e else "%d (S%d/A%d)" % (e["singlets"], e["sym"], e["antisym"])) for s, e in row.items()})
    print("centre lemma:", lemma, " g_X(M_U)max = %.4f" % out["g_X(M_U) max"])


if __name__ == "__main__":
    main()
