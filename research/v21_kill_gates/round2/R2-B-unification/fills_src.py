#!/usr/bin/env python3
"""Write fills.json (placeholder texts) for assemble_report.py from the rescue MC logs."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def scen(fn, cont):
    out = {}
    for line in open(os.path.join(HERE, fn), encoding="utf-8"):
        if not line.startswith(cont + " ") or "coherent" in line or "{" not in line:
            continue
        name, js = line.split(" {", 1)
        try:
            d = json.loads("{" + js)
        except Exception:
            continue
        out[name.split(" ", 1)[1]] = d
    return out


def coh(fn, cont):
    import ast
    rows = []
    for line in open(os.path.join(HERE, fn), encoding="utf-8"):
        if line.startswith(cont + " coherent"):
            rows.append(ast.literal_eval("{" + line.split(" {", 1)[1]))
    return rows


def fmt(cont, fn):
    s = scen(fn, cont)
    lines = []
    for k in ("light", "gut", "both", "both_Ms3e12", "gut_half"):
        if k not in s:
            continue
        d = s[k]
        t = d["tau_p_min_p05_med_p95_max"]
        v = d["v_R_min_p05_med_p95_max"]
        l2 = d["L2_min_p05_med_p95_max"]
        l3 = d["L3_min_p05_med_p95_max"]
        lines.append(f"    {cont:7s} {k:12s} n={d['n']:3d} tau min {t[0]:.2g} (dir {t[0]/4.53:.2g}), median {t[2]:.2g}; "
                     f"L2 min {l2[0]:.2f}; L3 min {l3[0]:.2f}, f(L3>1) = {d['frac_L3_gt_1']:.2f}; v_R {v[0]:.2g}-{v[4]:.2g}, "
                     f"f(v_R in window) = {d['frac_vR_1e11_1e14']:.2f}; f(tau>SK & L2>1) = {d['frac_pass2L(tau>SK & L2>1)']:.2f}")
    c = coh(fn, cont)
    if c:
        taus = [float(r["tau_p"]) for r in c]
        l3s = [float(r["L3"]) for r in c if r.get("L3")]
        vrs = [float(r["v_R"]) for r in c]
        lines.append(f"    {cont:7s} coherent extremes: tau {min(taus):.2g}-{max(taus):.2g}, L3 {min(l3s):.2f}-{max(l3s):.2f}, "
                     f"v_R {min(vrs):.2g}-{max(vrs):.2g}")
    return "\n".join(lines)


t813 = fmt("C1+813", "mc_rescue_C1+813.out")
t622 = fmt("C1+622", "mc_rescue622.out")
table = ("(r2b_scan.py mc, logs mc_rescue_C1+813.out / mc_rescue622.out; same scenarios as section 5;\n"
         "M_s = 1e13 unless stated):\n" + t813 + "\n" + t622 + "\n")
summary = ("Under the declared threshold scan C1 + (8,1,3)_0 is two-loop robust (tau >= 7.8e34 in every sample, direct\n"
           "  normalisation >= 1.7e34 at the extreme corner; Lambda_2L >= 2.1 M_Pl at M_s = 1e13) with v_R in the seesaw window in\n"
           "  85-100% of samples, but three loops fail at M_s = 3e12 (9% pass) and for a coherent GUT x1/2 spectrum (0.80-0.83);\n"
           "  C1 + (6,2,2)_{2/3} is two-loop robust at M_s = 1e13 (tau >= 1.3e35, Lambda_2L >= 1.39) but fails the two-loop\n"
           "  Landau test in 12% of the M_s = 3e12 samples, and its three-loop scale is below M_Pl,red in 35% (M_s = 1e13) to\n"
           "  100% (M_s = 3e12, or GUT x1/2..x1) of the samples (section 12).  With the P831-type spectrum C1 + (6,2,2) loses the two-loop Landau test (0.95) and\n"
           "  C1 + (8,1,3) the three-loop one (0.52) while tau still passes (section 6).  Neither was tested for realisability\n"
           "  by K3 (that is R2-A's question).")
json.dump({"[[MCRESCUE_TABLE]]": table, "[[MCRESCUE]]": summary}, open(os.path.join(HERE, "fills.json"), "w"), indent=1)
print(table)
print(summary)
