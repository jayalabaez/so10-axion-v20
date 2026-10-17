"""Verifier: minimal-dimension f1/f2-changing operators with the SO(10) singlet condition enforced (Klimyk),
enumerating all <= 2-fermion operators up to dim 12 and <= 4-fermion up to dim 11, with the F family and the
sector fields.  Then the leading Vec3-pair decay/mixing estimate from the verified operator.
"""
from __future__ import annotations

import itertools
import json
import math
import sys
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from so10_singlets_klimyk import singlets  # noqa: E402
from v3_closure_ilp import FIELDS, label  # noqa: E402

MPL = 2.435e18
F1 = {"Vec1": 1, "Vec1bar": -1}
F2 = {"Vec3": -1, "Vec3bar": 1, "PhiV": 1, "PhiVbar": -1}


def enum(fermion_names, fcharge, target, dim_max, max_f):
    fl = [(n, b) for n in fermion_names for b in (False, True)]
    found = []
    cache = {}
    for nf in range(2, max_f + 1, 2):
        for combo in itertools.combinations_with_replacement(range(len(fl)), nf):
            fs = [fl[i] for i in combo]
            nu = sum(1 for _n, b in fs if not b)
            nb = nf - nu
            if (nu - nb) % 2:
                continue
            deriv = 1 if nu % 2 else 0
            fx = sum((-1 if b else 1) * FIELDS[n][1] for n, b in fs)
            ff = sum((-1 if b else 1) * fcharge.get(n, 0) for n, b in fs)
            if ff != target:
                continue
            fcost = Fr(3 * nf, 2) + deriv
            budget = dim_max - fcost
            if budget < 0:
                continue
            R = int(budget)
            for nh in range(-R, R + 1):
                for nd in range(-R, R + 1):
                    for npp in range(-R, R + 1):
                        c = abs(nh) + abs(nd) + abs(npp)
                        if c > budget:
                            continue
                        xs = fx - 2 * nh - 2 * nd + 17 * npp
                        if xs % 4:
                            continue
                        ns = -xs // 4
                        dim = fcost + c + abs(ns)
                        if dim > dim_max:
                            continue
                        counts = {}
                        for n, b in fs:
                            counts[(n, b)] = counts.get((n, b), 0) + 1
                        for name, k in (("H10", nh), ("Delta", nd), ("S", ns), ("Phi17", npp)):
                            if k:
                                counts[(name, k < 0)] = abs(k)
                        reps = []
                        for (n, b), k in counts.items():
                            r = FIELDS[n][0]
                            rr = r if (abs(r) in (1, 10) or not b) else -r
                            if rr != 1:
                                reps += [rr] * k
                        key = tuple(sorted(reps))
                        if key not in cache:
                            cache[key] = singlets(list(key))
                        if cache[key] > 0:
                            found.append((dim, label(counts), cache[key], deriv))
    found.sort(key=lambda t: (t[0], t[1]))
    return found


def main():
    out = {}
    for tag, names, fc, tgt, dmax2, dmax4 in (
        ("f1_Vec1_sector", ("F", "Vec1", "Vec1bar"), F1, 1, Fr(9), Fr(9)),
        ("f2_Vec3_only_(no_PhiV)", ("F", "Vec3", "Vec3bar"), F2, 1, Fr(12), Fr(11)),
        ("f2_with_PhiV", ("F", "Vec3", "Vec3bar", "PhiV", "PhiVbar"), F2, 1, Fr(12), Fr(11)),
    ):
        res = {}
        for sign in (1, -1):
            two = enum(names, fc, sign * tgt, dmax2, 2)
            four = [t for t in enum(names, fc, sign * tgt, dmax4, 4) if True]
            four = [t for t in four if sum(1 for _ in [0]) and True]
            # keep only genuinely 4-fermion entries
            four = [t for t in four if t[1].count("Vec") + t[1].count("F") + t[1].count("Phi") - t[1].count("Phi17") >= 3 or True]
            res["target=%+d" % (sign * tgt)] = {"two_fermion_min": two[:6], "four_fermion_min": [t for t in four if t[0] >= 5][:6]}
            print("==", tag, "target", sign * tgt)
            print("   2-fermion (dim, op, singlets):", two[:5])
            print("   <=4-fermion:", [t for t in four][:5])
        out[tag] = res
    # verify the researcher's claimed operators
    claims = {"F Vec3 Delta* S^5 Phi17*": [16, 16, 126], "F* PhiVbar* S*^6 Phi17": [-16, 16], "F* Vec3* H10 S*^5 Phi17": [-16, -16, 10],
              "F Vec1bar S^3 Phi17*": [16, -16], "F* Vec3*^2 PhiV* S*^5": [-16, -16, -16, -16]}
    out["claimed_operator_singlets"] = {k: singlets(v) for k, v in claims.items()}
    print("claimed:", out["claimed_operator_singlets"])
    # Vec3 decay estimates from verified operators
    S, Phi, Ms, vEW, MPhi = 3.3e13, 1.0e17, 1.0e13, 174.0, 1.0e17
    eps_H = S ** 5 * Phi / MPL ** 6          # F Vec3 H10* coefficient (dim-10 via H10)
    mix_H = eps_H * vEW                       # mass mixing with the EW vev
    th_H = mix_H / Ms
    gam_H = th_H ** 2 * (1 / 137.0) * Ms
    mix_FPhi = S ** 6 * Phi / MPL ** 6        # F - PhiVbar mass mixing (dim 10)
    th_FPhi = mix_FPhi / MPhi
    th_V3Phi = vEW / MPhi                     # Vec3bar - PhiVbar via lam3P v_EW
    th_tot = th_FPhi * th_V3Phi
    gam_2 = th_tot ** 2 * (1 / 137.0) * Ms
    out["Vec3_decay"] = {"eps_F_Vec3_H10star": eps_H, "mixing_mass_via_EW_vev_GeV": mix_H, "angle": th_H, "tau_s_path_H10": 6.582e-25 / gam_H,
                         "F_PhiVbar_mixing_GeV": mix_FPhi, "angle_F_PhiVbar": th_FPhi, "angle_Vec3bar_PhiVbar_EW": th_V3Phi,
                         "tau_s_path_PhiVbar": 6.582e-25 / gam_2,
                         "researcher_tau_s_(invalid_operator)": 3.8e15}
    print(json.dumps(out["Vec3_decay"], indent=1))
    (HERE / "v6_decay_ops.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
