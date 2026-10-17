#!/usr/bin/env python3
"""Exact coefficient tables for R2-B and cross-checks against the repository (read-only imports):
  * two-loop MV b, b_ij of every G3221 / SM segment vs _g6_nogo/two_loop_thresholds_v20.mv_gauge_coefficients
    (real scalars entered as complex x 1/2, the repository's own convention in g7 mv_single_group);
  * SO(10) b1, b2, b3 of the B63 SO(10)-phase content vs _record/g7_decoupled_singlet_benchmark_evidence_v20
    (so10_rep_data, content_invariants, pgj_b, mv_single_group) and its v20 pins;
  * PGJ three-loop vs QCD (n_f = 5, 6: -9769/54, 65/2) and Mihaila-Salomon-Steinhauser SM pure 3L
    (-388613/24000, 324953/1728, 65/2) through this gate's per-factor routine;
  * the G3221 three-loop per-factor (pure) coefficients used in the '3L|sm3L' runs (EST: cross terms omitted);
  * S_V, U(1)_X coefficients, the Am45 vector-mass ratio and Planck Clebsches.
"""
import importlib.util
import json
import os
import subprocess
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r2b_model as M
from r2b_lib import SO10, C_G_SO10, mv_coefficients, pgj_b, pgj_invariants

REPO_G6 = r"C:\Users\jayal\Downloads\So10Theory2\So10Theory\_g6_nogo"
REPO_REC = r"C:\Users\jayal\Downloads\So10Theory2\So10Theory\_record"


def git_status(path):
    return subprocess.run(["git", "-C", path, "status", "--short"], capture_output=True, text=True).stdout


st_before = {p: git_status(p) for p in (REPO_G6, REPO_REC)}


def load(name, path, extra_path=None):
    if extra_path:
        sys.path.insert(0, extra_path)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if extra_path:
        sys.path.remove(extra_path)
    return mod


two_loop = load("two_loop_thresholds_v20_g6", os.path.join(REPO_G6, "two_loop_thresholds_v20.py"))
sys.modules["two_loop_thresholds_v20"] = load("two_loop_thresholds_v20", os.path.join(REPO_REC, "two_loop_thresholds_v20.py"))
g7 = load("g7_rec", os.path.join(REPO_REC, "g7_decoupled_singlet_benchmark_evidence_v20.py"))

out = {"repo_commits": {}, "checks": {}}
for pth in (REPO_G6, REPO_REC):
    out["repo_commits"][pth] = subprocess.run(["git", "-C", pth, "log", "--oneline", "-1"], capture_output=True,
                                              text=True).stdout.strip()


def to_repo_fields(fields):
    res = []
    for name, kind, reps, mult in fields:
        if kind == "real":
            res.append((name, "cplx", reps, F(mult) / 2))
        else:
            res.append((name, kind, reps, F(mult)))
    return tuple(res)


def s(x):
    return [str(v) for v in x]


tables = {}
allok = True
for cont in ("C0", "C1", "C2", "C1p", "T2", "T3"):
    for withS in (True, False):
        f = M.g3221_fields(M.CONTENTS[cont], withS)
        b, bij = mv_coefficients(M.G3221_C2, f)
        rb, rbij = two_loop.mv_gauge_coefficients(M.G3221_C2, to_repo_fields(f))
        eq = (list(b) == list(rb)) and all(list(r1) == list(r2) for r1, r2 in zip(bij, rbij))
        allok &= eq
        key = f"G3221_{cont}_{'withS' if withS else 'noS'}"
        tables[key] = {"b": s(b), "bij": [s(r) for r in bij], "equals_repo_mv": eq}
        if withS:
            b3 = M._single_group_b3_per_factor(M.G3221_C2, f)
            tables[key]["b3_pure_per_factor_EST"] = s(b3)
for withS in (True, False):
    f = M.sm_fields(withS)
    b, bij = mv_coefficients(M.SM_C2, f)
    rb, rbij = two_loop.mv_gauge_coefficients(M.SM_C2, to_repo_fields(f))
    eq = (list(b) == list(rb)) and all(list(r1) == list(r2) for r1, r2 in zip(bij, rbij))
    allok &= eq
    tables[f"SM_{'withS' if withS else 'noS'}"] = {"b": s(b), "bij": [s(r) for r in bij], "equals_repo_mv": eq,
                                                   "b3_pure_per_factor": s(M._single_group_b3_per_factor(M.SM_C2, f))}
# SM literature (no S): b = (41/10, -19/6, -7), MSS b3 = (-388613/24000, 324953/1728, 65/2)
smt = tables["SM_noS"]
out["checks"]["SM_b_literature"] = smt["b"] == ["41/10", "-19/6", "-7"]
out["checks"]["SM_bij_literature"] = smt["bij"] == [["199/50", "27/10", "44/5"], ["9/10", "35/6", "12"],
                                                     ["11/10", "9/2", "-26"]]
out["checks"]["SM_b3_MSS"] = smt["b3_pure_per_factor"] == ["-388613/24000", "324953/1728", "65/2"]
out["checks"]["all_G3221_SM_equal_repo_MV"] = allok

# QCD n_f Dirac flavours through the per-factor PGJ routine: SU(3) with 2 n_f Weyl triplets
for nf, exp in ((5, "-9769/54"), (6, "65/2")):
    inv = pgj_invariants([("3", "weyl", 2 * nf)], {"3": (3, F(1, 2), F(4, 3))}, F(3))
    out["checks"][f"QCD_b3_nf{nf}"] = str(pgj_b(inv)[2]) == exp

# SO(10) phase of B63 (identical to K1's v21 content multiplet by multiplet)
reps = g7.so10_rep_data()
name_map = {"16": "16", "16b": "16bar", "10": "10", "210": "210", "126b": "126bar"}
so = {}
for label, content in (("below_MPhi", M.SO10_BASE), ("above_MPhi", M.SO10_BASE + M.SO10_PHI_PAIR)):
    mine = M.so10_coeffs(content)
    rc = [(name_map[r], k, m) for r, k, m in content]
    repo = g7.pgj_b(g7.content_invariants(rc, reps))
    mvb1, mvb2 = g7.mv_single_group(rc, reps)
    so[label] = {"mine": s(mine), "repo_pgj": s(repo), "repo_mv": [str(mvb1), str(mvb2)],
                 "equal": s(mine) == s(repo) and [str(mvb1), str(mvb2)] == s(mine)[:2]}
# v20 pins via repo
for k, content in (("no_PQR", g7.SO10_BASE_CONTENT), ("with_PQR", tuple(g7.SO10_BASE_CONTENT) + tuple(g7.SO10_PQR_CONTENT))):
    so["repo_pin_" + k] = {"computed": s(g7.pgj_b(g7.content_invariants(content, reps))),
                           "expected": list(g7.EXPECTED_SO10_B[k])}
    so["repo_pin_" + k]["equal"] = so["repo_pin_" + k]["computed"] == so["repo_pin_" + k]["expected"]
mine_v20 = M.so10_coeffs([("16", "weyl", 3), ("16", "weyl", 5), ("16b", "weyl", 5), ("210", "real", 1),
                          ("126b", "cplx", 1), ("10", "cplx", 1)])
so["mine_reproduces_v20_pin_no_PQR"] = s(mine_v20) == list(g7.EXPECTED_SO10_B["no_PQR"])
out["SO10"] = so
out["checks"]["SO10_B63_equal_repo"] = so["below_MPhi"]["equal"] and so["above_MPhi"]["equal"]
out["checks"]["SO10_repo_pins"] = so["repo_pin_no_PQR"]["equal"] and so["repo_pin_with_PQR"]["equal"] and so["mine_reproduces_v20_pin_no_PQR"]
# the repo's own QCD/MSS checks of the PGJ table
try:
    out["repo_qcd_check"] = {k: str(v) for k, v in g7._qcd_check(g7.PGJ_COEFFICIENTS).items()} if hasattr(g7, "_qcd_check") else None
except Exception as e:  # noqa
    out["repo_qcd_check"] = f"error {e}"
out["checks"]["PGJ_table_identical_to_repo"] = {k: str(v) for k, v in g7.PGJ_COEFFICIENTS.items()} == \
    {k: str(v) for k, v in __import__("r2b_lib").PGJ.items()}

out["tables"] = tables
out["U1X_B63"] = {"below_MPhi": {k: str(v) for k, v in M.u1x_coeffs(False).items()},
                  "above_MPhi": {k: str(v) for k, v in M.u1x_coeffs(True).items()}}
out["S_V"] = {"M_U (SU3,SU2L,SU2R,BL)": M.SV_MU_STR, "U1_Y at v_R (W_R)": M.SV_Y_STR,
              "shift units S_V/(12 pi)": [float(x) / (12 * 3.141592653589793) for x in M.SV_MU]}
out["Am45"] = {"p": M.P_AM45, "a_K1norm": M.A_AM45, "M322_over_gPhi": M.MX_OVER_G_PHI,
               "M311_over_gPhi": M.M311_OVER_G_PHI, "R311": M.R311_AM45,
               "K_over_Phi (SU3,SU2L,SU2R,BL), s=+1": [-2 * M.A_AM45, 2 * M.P_AM45, -2 * M.P_AM45, 4 * M.A_AM45]}
# one-loop light-threshold content per contents
out["light_thresholds"] = {c: [(n, k, m) for n, k, _r, m in M.light_thresholds_at_vR(M.CONTENTS[c])]
                           for c in ("C0", "C1", "C2", "C1p")}
# completeness: heavy + light + 30 Goldstones = full 210 + 126bar + 10 in every factor (b = 64/3 x ... check)
for c in ("C0", "C1", "C2", "C1p"):
    tot = [F(0)] * 4
    for _n, kind, reps_, mult in M.heavy_scalars_at_MU(M.CONTENTS[c]) + [M.g3221_entry(n) for n in M.CONTENTS[c]]:
        for i in range(4):
            tot[i] += M.threshold_b(kind, reps_, i, mult)
    # Goldstones (3,2,2)_-2/3 and (3,1,1)_4/3 complex
    for reps_ in (M.g3221("3", "2", "2", F(-2, 3)), M.g3221("3", "1", "1", F(4, 3))):
        for i in range(4):
            tot[i] += M.threshold_b("cplx", reps_, i, 1)
    so10_scalar_b = F(1, 6) * 56 + F(1, 3) * 35 + F(1, 3) * 1
    out["checks"][f"scalar_completeness_{c}"] = all(x == so10_scalar_b for x in tot)
st_after = {p: git_status(p) for p in (REPO_G6, REPO_REC)}
out["git_status_unchanged"] = st_before == st_after
out["git_status_lines"] = {p: len(st_after[p].splitlines()) for p in st_after}
with open(os.path.join(HERE, "r2b_coeffs.json"), "w") as fh:
    json.dump(out, fh, indent=1, default=str)
print(json.dumps(out["checks"], indent=1))
print("SO10", json.dumps(out["SO10"]["below_MPhi"]), json.dumps(out["SO10"]["above_MPhi"]))
for c in ("C0", "C1", "C2", "C1p"):
    print(c, tables[f"G3221_{c}_withS"]["b"], tables[f"G3221_{c}_noS"]["b"], tables[f"G3221_{c}_withS"]["b3_pure_per_factor_EST"])
print("git unchanged", out["git_status_unchanged"], out["git_status_lines"])
