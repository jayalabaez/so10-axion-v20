"""Collect run_vr.py result JSONs into summary.json and a text table (summary.txt)."""
import json, glob, math, sys
import numpy as np

KEYS = ["m_u", "m_c", "m_t", "m_d", "m_s", "m_b", "m_e", "m_mu", "m_tau", "s12", "s23", "s13", "delta",
        "sin2_th12", "sin2_th23", "sin2_th13", "dm21", "dm31"]
rows = []
for f in sorted(glob.glob("*_I.json") + glob.glob("*_II.json")):
    if f.endswith("_proxy.json") or f.startswith("smoke"):
        continue
    J = json.load(open(f))
    rep = next((r for r in J["reports"] if "error" not in r), None)
    row = {"file": f, "tag": J["tag"], "vR": J["vR"], "content": J["content"], "MU": J["MU"], "type": J["type"],
           "nu": J["nu"], "err": J["err"], "th23": J["th23"], "floor": J["floor"],
           "proxy_min": J["proxy"]["min"], "proxy_by_opt": {k: v["min"] for k, v in J["proxy"]["summary"].items()},
           "proxy_lit_seeds": min([s["chi2_free"] for s in J["proxy"]["seed_detail"]] or [None]),
           "exact_min": J["exact_min"], "exact_by_src": J["exact_by_src"],
           "n_exact_within_5": int(sum(1 for r in J["exact_results"] if r["chi2"] < J["exact_min"] + 5)),
           "time_s": J["time_s"]}
    if rep:
        row.update({"chi2_scalar_DOP853": rep["chi2"], "chi2_batched_rk4": rep["chi2_batched_rk4"], "max_abs_pull": rep["max_abs_pull"],
                    "pulls": rep["pulls"], "r": rep["r"], "s": rep["s"], "s_abs": rep["s_abs"], "c_d126": rep["c_d126"],
                    "comp": rep["comp"], "Y10_act_max_MU": rep["Y10_act_max"], "Y126_act_max_MU": rep["Y126_act_max"],
                    "ymax_act_MU_vR": rep["ymax_act_batched"], "M_R_GeV": rep["M_R_GeV"], "fh_vR_sv": rep.get("fh_vR_sv"),
                    "Y10_def_sv": rep.get("Y10_def_sv"), "Y126_def_sv": rep.get("Y126_def_sv"), "m_nu_eV": rep["m_nu_eV"],
                    "m_lightest_eV": rep["m_lightest_eV"], "m_betabeta_eV": rep["m_betabeta_eV"],
                    "sum_mnu_eV": rep["sum_mnu_eV"], "delta_pmns_deg": rep["delta_pmns_deg"],
                    "sin2_th23_fit": rep["obs_MZ"]["sin2_th23"], "src": rep["src"],
                    "chi2_without_th23": rep["chi2"] - rep["pulls"]["sin2_th23"] ** 2,
                    "n_pulls_gt3": int(sum(1 for k in KEYS if abs(rep["pulls"][k]) > 3)), "z": rep["z"]})
        if J["type"] == "II":
            row["log10_t"] = rep.get("log10_t")
    if J.get("floor0"):
        f0 = J["floor0"][0]
        row["chi2_floor0_repolished"] = min(x["chi2_floor0_repolished"] for x in J["floor0"])
        row["chi2_floor0_at_floor1_point"] = f0["chi2_floor0_at_floor1_point"]
        r0 = min(J["floor0"], key=lambda x: x["chi2_floor0_repolished"])["report"]
        if "pulls" in r0:
            row["floor0_pulls"] = r0["pulls"]; row["floor0_chi2_scalar"] = r0["chi2"]
    rows.append(row)
json.dump(rows, open("summary.json", "w"), indent=1)
with open("summary.txt", "w") as fo:
    for r in sorted(rows, key=lambda r: (r["tag"], r["vR"])):
        fo.write(f"{r['tag']:8s} vR={r['vR']:.1e} {r['content']:5s} MU={r['MU']:.2e} {r['type']:2s} nu={r['nu']} err={r['err']} th23={r['th23']}\n")
        fo.write(f"   proxy min {r['proxy_min']:.2f} by opt {json.dumps({k: round(v, 2) for k, v in r['proxy_by_opt'].items()})} lit-seeds {r['proxy_lit_seeds']:.2f}\n")
        fo.write(f"   exact min {r['exact_min']:.2f} by src {json.dumps({k: (round(v, 2) if v else None) for k, v in r['exact_by_src'].items()})} n(within 5)={r['n_exact_within_5']}\n")
        if "pulls" in r:
            fo.write(f"   scalar DOP853 chi2 {r['chi2_scalar_DOP853']:.2f} (batched {r['chi2_batched_rk4']:.2f}); max|pull| {r['max_abs_pull']:.2f}; "
                     f"#pulls>3: {r['n_pulls_gt3']}; chi2 w/o th23 {r['chi2_without_th23']:.2f}; floor0 {r.get('chi2_floor0_repolished', float('nan')):.2f}\n")
            fo.write("   pulls " + " ".join(f"{k}={v:+.2f}" for k, v in r["pulls"].items()) + "\n")
            c = r["comp"]
            fo.write(f"   r={r['r']:.2f} s={r['s'][0]:+.4f}{r['s'][1]:+.4f}i |s|={r['s_abs']:.4f} c_d126={r['c_d126']:.4g} comp |c_u10|,|c_u126|,|c_d10|,|c_d126| = "
                     f"{', '.join(f'{v:.4g}' for v in c['abs'])}; 126-fraction(H) {c['frac_126_in_H']:.3f}\n")
            fo.write(f"   ymax_act (M_U/vR max) Y10 {r['ymax_act_MU_vR'][0]:.3f} Y126 {r['ymax_act_MU_vR'][1]:.3f}; fh(vR) sv max {max(r['fh_vR_sv']):.3f}; M_R = {', '.join(f'{v:.3g}' for v in r['M_R_GeV'])} GeV\n")
            fo.write(f"   m_nu = {', '.join(f'{v*1e3:.3f}' for v in r['m_nu_eV'])} meV; m_bb = {r['m_betabeta_eV']*1e3:.3f} meV; delta_PMNS = {r['delta_pmns_deg']:.1f} deg; "
                     f"sin2th23(fit) = {r['sin2_th23_fit']:.4f}\n")
print(open("summary.txt").read())
