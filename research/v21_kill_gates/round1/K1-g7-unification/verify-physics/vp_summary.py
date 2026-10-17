#!/usr/bin/env python3
"""Collect the verifier's decisive numbers and compare them with the researcher's claims -> vp_verdict.json."""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name):
    p = os.path.join(HERE, name)
    return json.load(open(p)) if os.path.exists(p) else None


coeffs = load("vp_coeffs.json")
nominal = load("vp_chain_nominal.json")
scan = load("vp_scan2.json")
mc = load("vp_mc.json")
alpha = load("vp_alpha_space.json")
planck = load("vp_planck.json")
out = {}

out["coefficients"] = {
    "qcd_general_casimir_b3_eq_minus_beta2_all": coeffs["qcd"]["all_equal_minus_beta2"],
    "sm_mss_pure_3loop_match": coeffs["sm_mss"]["matches_MSS"],
    "so10_pins_match": coeffs["so10_pins_ok"],
    "v21_below_Mphi": coeffs["v21_below_Mphi"]["b123"],
    "v21_above_Mphi": coeffs["v21_above_Mphi"]["b123"],
    "comparison_with_researcher_tables": coeffs["comparison_with_researcher"],
}
out["planck_clebsch_agree"] = planck["agrees_with_researcher"] if planck else None

# nominal
nom = {}
for k in ("T2_2L_Ms1e+13_yuk1_Mphi1e+17", "T3_2L_Ms1e+13_yuk1_Mphi1e+17", "T2_1L_Ms1e+13_yuk1_Mphi1e+17",
          "T3_1L_Ms1e+13_yuk1_Mphi1e+17", "T2_2L_Ms5e+12_yuk0_Mphi1e+10", "T3_2L_Ms5e+12_yuk0_Mphi1e+10"):
    r = nominal[k]
    nom[k] = {kk: r[kk] for kk in ("v_R", "M_U", "alpha_U_inv", "L2_ratio", "L3_ratio", "tau_p")}
out["nominal"] = nom
researcher = {"T2": {"v_R": 2.496e13, "M_U": 2.045e16, "alpha_U_inv": 27.102, "L2": 2.417, "L3": 1.051, "tau_p": 8.64e36},
              "T3": {"v_R": 2.958e13, "M_U": 2.914e16, "alpha_U_inv": 26.129, "L2": 2.346, "L3": 1.049, "tau_p": 3.31e37}}
dev = {}
for c in ("T2", "T3"):
    r = nominal[f"{c}_2L_Ms1e+13_yuk1_Mphi1e+17"]
    dev[c] = {"v_R": r["v_R"] / researcher[c]["v_R"] - 1, "M_U": r["M_U"] / researcher[c]["M_U"] - 1,
              "alpha_U_inv": r["alpha_U_inv"] - researcher[c]["alpha_U_inv"], "L2": r["L2_ratio"] / researcher[c]["L2"] - 1,
              "L3": r["L3_ratio"] / researcher[c]["L3"] - 1, "tau_p": r["tau_p"] / researcher[c]["tau_p"] - 1}
out["nominal_relative_deviation_from_researcher"] = dev

if scan:
    out["Ms_crossing"] = {k: v for k, v in scan.items() if k.startswith("Ms_crossing")}
    out["Ms_scan"] = [{k: r[k] for k in ("content", "M_s", "M_phi", "L2_ratio", "L3_ratio", "v_R", "M_U", "alpha_U_inv")}
                      for r in scan["Ms_scan"]]
    for c in ("T2", "T3"):
        s = scan.get(f"syst_{c}")
        if s:
            out[f"syst_{c}"] = {k: (v if not isinstance(v, dict) else {kk: v[kk] for kk in ("L2_ratio", "L3_ratio", "v_R", "M_U", "alpha_U_inv") if kk in v})
                                for k, v in s.items()}
    if "planck" in scan:
        pl = {}
        for r in scan["planck"]:
            key = f"{r['content']}_s{r['s']:+d}_th{r['theta']}"
            pl.setdefault(key, {})[f"c={r['c']:+.2f}"] = {"ok": r["ok"], "L3": r.get("L3_ratio"), "L2": r.get("L2_ratio"),
                                                         "v_R": r["v_R"], "M_U": r["M_U"], "aU": r["alpha_U_inv"],
                                                         "eps_per_c": r["eps_per_c"]}
        out["planck"] = pl
        # three-loop pass summary per c over the scanned orientations
        cs = sorted({r["c"] for r in scan["planck"]})
        summ = {}
        for c_ in ("T2", "T3"):
            summ[c_] = {}
            for cc in cs:
                rows = [r for r in scan["planck"] if r["content"] == c_ and r["c"] == cc]
                okrows = [r for r in rows if r["ok"]]
                summ[c_][f"c={cc:+.2f}"] = {"n": len(rows), "n_ok": len(okrows),
                                            "n_pass3": sum(1 for r in okrows if r.get("L3_ratio", 0) > 1),
                                            "L3_min": min((r["L3_ratio"] for r in okrows), default=None),
                                            "L3_max": max((r["L3_ratio"] for r in okrows), default=None),
                                            "L2_min": min((r["L2_ratio"] for r in okrows), default=None)}
        out["planck_pass_summary"] = summ
if mc:
    out["mc"] = mc
if alpha:
    out["alpha_space"] = alpha
json.dump(out, open(os.path.join(HERE, "vp_verdict.json"), "w"), indent=1, default=float)
print(json.dumps({k: v for k, v in out.items() if k not in ("Ms_scan", "planck", "mc")}, indent=1, default=float))
if mc:
    for k, v in mc.items():
        print(k, {kk: v[kk] for kk in ("n_ok", "pass3", "pass2", "L3_min_p05_med_p95_max", "L2_min_med_max", "frac_tau_below_2.4e34")})
