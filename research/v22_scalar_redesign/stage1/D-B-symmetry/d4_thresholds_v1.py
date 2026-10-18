"""D-B-symmetry D4: GUT thresholds of EXPLICIT coupling points through R2-B's two/three-loop code, with V1's field content.

Uses r2a_thresholds.py (R2-A, copied unedited) as a library: block spectra -> G3221 multiplet assignment -> 2L/3L solve.
V1 modifications (monkey-patched, not edited): SO(10) phase + one complex 10 (H2); light lists
   V1C2    = (10:(1,2,2)_0 [H1], 10:(1,2,2)_0 [H2], Delta_R)
   V1C1622 = V1C2 + (8,3,1)_0 + (6,2,2)_{2/3}
The chart spectrum (486 chart, H2 = 0 slice) supplies every multiplet except H2's own; H2's colour triplets are put at
M_U (no one-loop threshold; EST), the H2 bidoublet is light.  The 126bar bidoublet is heavy and assigned from the chart.
Also re-evaluates R2-A's two-bidoublet realisable spectra 'transplanted' (only the SO(10)-phase change; EST).
tau_LA = direct lattice (W0 = 0.131 GeV^2) with A_R = 3.28.
usage: python -B d4_thresholds_v1.py <out.json> <datadir> <tag:sol.npz:content> ...   (content: V1C2, V1C1622, C2, C1622)
"""
import json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import r2b_model as M
import r2a_thresholds as T

M.SO10_BASE = list(M.SO10_BASE) + [("10", "cplx", 1)]
M.X_CPLX = list(M.X_CPLX) + [("10", -2, 1)]
M.CONTENTS["V1C2"] = ("10:(1,2,2)_0", "10:(1,2,2)_0", M.DR)
M.CONTENTS["V1C1622"] = ("10:(1,2,2)_0", "10:(1,2,2)_0", M.DR, "210:(8,3,1)_0", "210:(6,2,2)_2/3")
T.CMAP.update({"V1C2": "V1C2", "V1C1622": "V1C1622"})


def run_one(datadir, tag, solp, content):
    Bz = np.load(os.path.join(datadir, f"{tag}_blocks.npz")); labels = [str(x) for x in Bz["labels"]]
    c = np.load(os.path.join(datadir, solp))["c"]
    spec = T.block_spectrum(Bz, labels, c); light = M.CONTENTS[T.CMAP[content]]
    m2, problems, leftover = T.assign(spec, light); need, got = T.light_check(spec, light)
    kx = T.GR[tag]["MX_over_gPhi"]; v311 = T.GR[tag]["v311_ratio"]
    rec = {"tag": tag, "sol": solp, "content": content, "assigned_m2_over_Phi2": m2, "unassigned": problems,
           "leftover": leftover, "light_needed(chart+H2)": need, "light_found_in_chart": got, "solutions": {}}
    if problems:
        rec["error"] = "assignment failed"; return rec
    for loops in (2, 3):
        s = T.solve(light, m2, kx, v311, loops, sv=+1)
        if s.get("ok"):
            s["tau_LA"] = M.proton_lifetime_direct_years(s["M_U"], s["alpha_U_inv"], A=3.28)
            s["pass_SK_LA"] = s["tau_LA"] > 2.4e34
        rec["solutions"][f"{loops}L"] = s
    return rec


if __name__ == "__main__":
    outp, datadir = sys.argv[1], sys.argv[2]; res = []
    for spec_ in sys.argv[3:]:
        tag, solp, content = spec_.split(":")
        r = run_one(datadir, tag, solp, content); res.append(r)
        s2 = r["solutions"].get("2L", {}); s3 = r["solutions"].get("3L", {})
        f = lambda x: "-" if x is None else (f"{x:.3g}" if isinstance(x, float) else str(x))
        print(f"{tag} {content} {solp}: unassigned={r['unassigned']} | 2L v_R={f(s2.get('v_R'))} M_U={f(s2.get('M_U'))} "
              f"aU^-1={f(s2.get('alpha_U_inv'))} tau_repo={f(s2.get('tau_p_yr'))} tau_LA={f(s2.get('tau_LA'))} L2={f(s2.get('L2'))} "
              f"min_ratio={f(s2.get('ratio_min'))} ({s2.get('lightest_heavy')}) | 3L L3={f(s3.get('L3'))} tau_LA={f(s3.get('tau_LA'))}", flush=True)
    json.dump(res, open(os.path.join(HERE, outp), "w"), indent=1, default=str)
