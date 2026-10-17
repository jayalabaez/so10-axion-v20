"""Generate the per-v_R table, robustness numbers and composition block for REPORT.txt (prints text blocks to
tables.txt and a machine-readable final_numbers.json)."""
import json, glob, os, math

S = {(r["tag"], r["vR"]): r for r in json.load(open("summary.json"))}
fl0 = {}
for f in glob.glob("*_floor0.json"):
    J = json.load(open(f)); fl0[f.replace("_floor0.json", ".json")] = J
V = json.load(open("vscan_fine.json")) if os.path.exists("vscan_fine.json") else []
out = []


def line(r, f0=None):
    p = r["pulls"]
    return (f"  v_R = {r['vR']:.0e}  {r['content']:4s} M_U = {r['MU']:.2e}: chi2 = {r['exact_min']:.2f} (scalar DOP853 {r['chi2_scalar_DOP853']:.2f}), "
            f"floor0 = {f0 if f0 is None else round(f0, 2)}, max|pull| = {r['max_abs_pull']:.2f}, #(|pull|>3) = {r['n_pulls_gt3']}\n"
            f"     pulls: " + " ".join(f"{k}={v:+.2f}" for k, v in p.items()) + "\n"
            f"     r = {r['r']:.2f}, s = {r['s'][0]:+.4f}{r['s'][1]:+.4f}i, c_d126 = {r['c_d126']:.4g}; |c_u10|, |c_u126|, |c_d10|, |c_d126| = "
            + ", ".join(f"{v:.4g}" for v in r["comp"]["abs"]) + "\n"
            f"     max|Y10_act| = {r['ymax_act_MU_vR'][0]:.3f}, max|Y126_act| = {r['ymax_act_MU_vR'][1]:.3f}, f(v_R) max sv = {max(r['fh_vR_sv']):.3f}; "
            f"M_R = " + ", ".join(f"{v:.3g}" for v in r["M_R_GeV"]) + " GeV\n"
            f"     m_nu = " + ", ".join(f"{v*1e3:.2f}" for v in r["m_nu_eV"]) + f" meV, sum = {r['sum_mnu_eV']*1e3:.1f} meV, m_bb = {r['m_betabeta_eV']*1e3:.2f} meV, "
            f"delta_PMNS = {r['delta_pmns_deg']:.1f} deg, sin^2 th23 = {r['sin2_th23_fit']:.4f}\n")


tab = []
mains = sorted([r for (t, v), r in S.items() if t in ("main", "mainfix") and "pulls" in r], key=lambda r: (r["vR"], r["tag"]))
for r in mains:
    f0 = fl0.get(r["file"], {}).get("best_floor0")
    tab.append(line(r, f0))
tab.append("  Fine exact continuation scan (vscan.py; starts = best points of the main runs; f <= sqrt(4 pi)):\n")
for v in V:
    rp = v["report"]
    tab.append(f"     v_R = {v['vR']:.0e} {v['content']:4s}: chi2 = {v['chi2_min']:.2f}, sin^2 th23 = {rp['obs_MZ']['sin2_th23']:.4f}, max|pull| = {rp['max_abs_pull']:.2f}, "
               f"r = {rp['r']:.1f}, |s| = {rp['s_abs']:.3f}, max|Y126_act(M_U)| = {rp['Y126_act_max']:.3f}, f(v_R) = {max(rp['fh_vR_sv']):.2f}, M_R3 = {max(rp['M_R_GeV']):.3g}\n")
for tag in ("fh7", "fhinf"):
    f = f"vscan_{tag}.json"
    if os.path.exists(f):
        tab.append(f"  f-bound variant {tag} (R2C_FHMAX = {'7.09' if tag == 'fh7' else 'inf'}):\n")
        for v in json.load(open(f)):
            rp = v["report"]
            tab.append(f"     v_R = {v['vR']:.0e}: chi2 = {v['chi2_min']:.2f}, sin^2 th23 = {rp['obs_MZ']['sin2_th23']:.4f}, max|pull| = {rp.get('max_abs_pull', float('nan')):.2f}, "
                       f"max|Y126_act(M_U)| = {rp.get('Y126_act_max', float('nan')):.3f}, f(v_R) = {max(rp.get('fh_vR_sv', [float('nan')])):.2f}\n")
open("tables.txt", "w").write("".join(tab))
diag = {}
for (t, v), r in S.items():
    if t not in ("main", "mainfix"):
        diag[f"{t}_{v:.0e}"] = {k: r.get(k) for k in ("exact_min", "proxy_min", "max_abs_pull", "n_pulls_gt3", "chi2_without_th23",
                                                       "sin2_th23_fit", "r", "s", "c_d126", "pulls", "chi2_floor0_repolished")}
fin = {"mains": [{k: r.get(k) for k in ("tag", "vR", "content", "MU", "proxy_min", "exact_min", "chi2_scalar_DOP853", "max_abs_pull",
                                         "n_pulls_gt3", "chi2_without_th23", "sin2_th23_fit", "r", "s", "c_d126", "comp", "pulls",
                                         "ymax_act_MU_vR", "fh_vR_sv", "M_R_GeV", "m_nu_eV", "m_betabeta_eV", "delta_pmns_deg")}
                  | {"floor0": fl0.get(r["file"], {}).get("best_floor0")} for r in mains],
       "vscan_fine": [{"vR": v["vR"], "content": v["content"], "chi2": v["chi2_min"]} for v in V], "diagnostics": diag}
for tag in ("fh7", "fhinf"):
    f = f"vscan_{tag}.json"
    if os.path.exists(f):
        fin["vscan_" + tag] = [{"vR": v["vR"], "chi2": v["chi2_min"]} for v in json.load(open(f))]
for f in glob.glob("sens_*.json"):
    J = json.load(open(f)); fin.setdefault("sens", []).append({"vR": J["vR"], "content": J["content"], "MU": J["MU"], "chi2": J["bh_best"]})
json.dump(fin, open("final_numbers.json", "w"), indent=1, default=str)
print("".join(tab))
