#!/usr/bin/env python3
"""Export a coupling point (couplings, vevs, full spectrum by SM multiplet, light content, checks) as JSON for Stage 2b.

usage: python -B vexport.py <pt_tag> <solution npz> <post json (vpost.py)> <global-search summary json(s), comma list>
        <out json path> [--content Lb] [--note text]
Units: chart units with |Phi210*| = 1 (kinetic-normalised real coordinates); masses^2 in the same units.  The physical
scale is fixed by the heavy-vector spectrum: the (3,2)_{-5/6} vector mass M_X = g sqrt(mu_X) Lambda, mu_X from the
exact gauge tangents at q* (reported), so Lambda = M_X / (g sqrt(mu_X)) [EST mapping, g ~ 0.58 at M_U].
"""
from __future__ import annotations

import argparse
import json
import math

import numpy as np

import vc

C = vc.C
ap = argparse.ArgumentParser()
ap.add_argument("tag")
ap.add_argument("sol")
ap.add_argument("post")
ap.add_argument("globals_")
ap.add_argument("out")
ap.add_argument("--content", default="")
ap.add_argument("--note", default="")
args = ap.parse_args()
P = np.load(vc.BIG / f"pt_{args.tag}.npz")
PJ = json.load(open(vc.BIG / f"pt_{args.tag}.json"))
S = np.load(args.sol if (":" in args.sol) else vc.BIG / args.sol)
post = json.load(open(args.post if (":" in args.post) else vc.BIG / args.post))
q0 = P["q"]
c = S["c"]
inv = json.load(open(C.INVARIANTS_JSON))
cmap = {}
for e in inv["A45_invariants"]:
    cmap[e["name"]] = {"coupling": e["coupling"], "contraction": e["contraction"], "normalisation": e.get("normalisation")}
couplings = []
for pid, x in zip(vc.IDS, c):
    name = pid.split("::")[1]
    rec = {"parameter_id": pid, "value": float(x), "degree": int(vc.DEG[vc.IDX[pid]]),
           "box": float(vc.boxes()[vc.IDX[pid]])}
    if name in cmap:
        rec.update(cmap[name])
        if pid in vc.EPS_FACTOR:
            rec["note_F1"] = (f"chart531 implements the DECLARED formula; invariants.json reference value = declared/"
                              f"{vc.EPS_FACTOR[pid]:g}: coupling in the reference normalisation = {x * vc.EPS_FACTOR[pid]:.6g}")
    couplings.append(rec)
# gauge-vector spectrum at q*
T, _ = C.symmetry_matrix(q0)
G = T[:, :45]
M = G.T @ G
wv, Vv = np.linalg.eigh(0.5 * (M + M.T))
vec_masses = sorted(set(np.round(wv[wv > 1e-12], 10).tolist()))
glob = []
for gfile in [x for x in args.globals_.split(",") if x]:
    glob.append(json.load(open(gfile if (":" in gfile) else vc.BIG / gfile)))
out = {
    "candidate": "v22-L2 (v20 scalars + real 45_H, B63 fermions), stage-2a vacuum tester",
    "content": args.content, "note": args.note,
    "conventions": {"chart": "531-real chart of stage2a/chart/chart531.py (486 repo chart + A_ab, a<b)",
                    "potential": "V = sum_k c_k I_k over the 85 parameter ids (repo conventions: lambda:: = I, re:: = 2Re I, "
                                 "im:: = -2Im I); v20 rows = repository compiler rows, A rows = invariants.json declared formulas",
                    "units": "|Phi210*| = 1 (chart units); masses^2 in the same units"},
    "vevs": PJ["point"],
    "vev_meaning": {"p,a,omega": "Phi210 = p P + a A + omega W (direct.singlet_basis, unit chart norm)",
                    "omega_R,omega_BL": "A45 = omega_R T3R + omega_BL T_BL (A_67 = A_89 = 1/sqrt2; A_01 = A_23 = A_45 = 1/sqrt3)",
                    "r": "Sigma126bar = r sigma_std (Y = 0 SM singlet, T3R = +1, B-L = -2)", "s": "S", "x": "Phi17"},
    "q_star": q0.tolist(),
    "couplings": couplings,
    "ew_doublet": {"a_ew_slot_vector": [[float(z.real), float(z.imag)] for z in S["a_ew"]] if S["a_ew"].size else None},
    "post": post,
    "heavy_vector_mass2_over_g2_distinct": vec_masses,
    "global_search": glob,
}
json.dump(vc.jsonable(out), open(args.out, "w"), indent=1)
print("written", args.out)
