"""R2-A (b): GUT-scale thresholds of an EXPLICIT realisable vacuum point (any tag, any coupling vector) through R2-B's
two/three-loop unification code (r2b_model.py / r2b_lib.py copied unchanged from R2-B-unification).

1. Block spectra M_k = sum_i c_i A_k[i] on the Goldstone complement of the tag's SM-isotypic blocks.
2. Heavy eigenvalues (m^2 > 1e-4 |Phi|^2) assigned to G3221 multiplets of 210+126bar+10 by the degeneracy pattern
   across SM blocks (R2-B's r2b_p831.assign, rtol 3e-3); light multiplets (those of the content) are checked to sit in
   the light window (m^2 < 1e-4) in every SM block they populate.
3. Vector masses at THIS orientation from the chart tangents (gauge_ratios.json): M_X = M(3,2,2) = k_X g_U |Phi|,
   M(3,1,1) = v311 M_X; R2-B's MX_OVER_G_PHI and v311_ratio are overridden per tag (R2-B used the Am45 values).
4. Solve at 2L and 3L (g_U iterated to self-consistency), tau_p in the repository and the direct-lattice normalisation.
usage: python -B r2a_thresholds.py <out.json> <tag:sol.npz:content> [<tag:sol.npz:content> ...]
   content in {C1, C2, C1p, C1813, C1622, C0}
"""
import json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import r2b_model as M
from fractions import Fraction as F

CMAP = {"C1": "C1", "C2": "C2", "C1p": "C1p", "C1813": "C1+813", "C1622": "C1+622", "C0": "C0"}
GR = json.load(open(os.path.join(HERE, "gauge_ratios.json")))
EXTRA = json.loads(os.environ.get("R2A_PARAMS", "{}"))  # e.g. {"M_s": 1.21e13, "y_s": 0.368, "M_phi": 1.25e17}


def block_spectrum(Bz, labels, c):
    spec = {}
    for k, lab in enumerate(labels):
        A = Bz[f"A{k}"]; Mk = np.einsum("i,ijk->jk", c, A); Mk = 0.5 * (Mk + Mk.conj().T); G = Bz[f"G{k}"]; m = Mk.shape[0]
        if G.shape[1] > 0:
            uu, ss, _ = np.linalg.svd(G, full_matrices=True); Q = uu[:, G.shape[1]:]
        else:
            Q = np.eye(m)
        spec[lab] = sorted(np.linalg.eigvalsh(Q.conj().T @ Mk @ Q).tolist())
    return spec


def k3_label(su3, su2l, y):
    d3 = {"1": 1, "3": 3, "3b": 3, "6": 6, "6b": 6, "8": 8}[su3]; ya = abs(F(y))
    ys = str(ya.numerator) if ya.denominator == 1 else f"{ya.numerator}/{ya.denominator}"
    return f"({d3},{su2l})_|Y|={ys}"


def pieces_blocks(name):
    kind, c3, l, r, q = M.SCALAR_TABLE[name]; out = []; nr = int(r); seen = set()
    for k in range(nr):
        t3r = F(nr - 1, 2) - k; y = t3r + q / 2; lab = k3_label(c3, l, y)
        if kind == "real":
            key = (lab, abs(y))
            if key in seen: continue
            seen.add(key)
        out.append(lab)
    return out


def assign(spec, light, heavy_floor=1e-4, rtol=3e-3):
    avail = {lab: [v for v in vals if v > heavy_floor] for lab, vals in spec.items()}
    heavy = [n for n in M.SCALAR_TABLE if n not in light]
    order = sorted(heavy, key=lambda n: -len(pieces_blocks(n)))
    res, problems = {}, []
    for n in order:
        pb = pieces_blocks(n); need = {}
        for lab in pb: need[lab] = need.get(lab, 0) + 1
        best = None
        for cand in sorted(set(avail.get(pb[0], []))):
            if all(sum(1 for v in avail.get(lab, []) if abs(v - cand) <= rtol * cand) >= cnt for lab, cnt in need.items()):
                best = cand; break
        if best is None: problems.append(n); continue
        for lab, cnt in need.items():
            for _ in range(cnt):
                j = min(range(len(avail[lab])), key=lambda i: abs(avail[lab][i] - best)); avail[lab].pop(j)
        res[n] = best
    leftover = {lab: v for lab, v in avail.items() if v}
    return res, problems, leftover


def light_check(spec, light, floor=1e-4):
    """number of sub-floor (light, non-Goldstone) eigenvalues per SM block vs the number the content needs"""
    need = {}
    for n in light:
        for lab in pieces_blocks(n): need[lab] = need.get(lab, 0) + 1
    got = {lab: sum(1 for v in vals if 1e-9 < v < floor) for lab, vals in spec.items()}
    return need, {lab: got.get(lab, 0) for lab in set(need) | {l for l, g in got.items() if g}}


def solve(light, m2, kx, v311, loops, sv=+1, scale=1.0):
    aU = 33.0; row = None; gr = {}
    M.MX_OVER_G_PHI = kx
    for _ in range(6):
        g = math.sqrt(4 * math.pi / aU); mx_phi = kx * g
        gr = {n: scale * math.sqrt(v) / mx_phi for n, v in m2.items() if n not in light}
        p = M.Params(light=light, gut_ratios=gr, loops=loops, sv_sign=sv, v311_ratio=v311, **EXTRA)
        row = M.full_point(p, landau_loops=(loops,), x_opts=(None,))
        if not row.get("ok"): break
        if abs(row["alpha_U_inv"] - aU) < 1e-5: break
        aU = row["alpha_U_inv"]
    out = {k: row.get(k) for k in ("ok", "v_R", "M_U", "alpha_U_inv", "tau_p_yr", f"L{loops}")}
    if row.get("ok"):
        out["tau_dir"] = M.proton_lifetime_direct_years(row["M_U"], row["alpha_U_inv"])
        out["pass_SK_repo"] = out["tau_p_yr"] > 2.4e34; out["pass_SK_dir"] = out["tau_dir"] > 2.4e34
        out["vR_in_seesaw_window"] = 1e11 <= row["v_R"] <= 1e14
    if gr:
        out["ratio_min"] = min(gr.values()); out["ratio_max"] = max(gr.values())
        out["lightest_heavy"] = min(gr, key=gr.get)
    return out


def run_one(tag, solp, content):
    Bz = np.load(os.path.join(HERE, f"{tag}_blocks.npz")); labels = [str(x) for x in Bz["labels"]]
    c = np.load(os.path.join(HERE, solp))["c"]
    spec = block_spectrum(Bz, labels, c); light = M.CONTENTS[CMAP[content]]
    m2, problems, leftover = assign(spec, light); need, got = light_check(spec, light)
    kx = GR[tag]["MX_over_gPhi"]; v311 = GR[tag]["v311_ratio"]
    rec = {"tag": tag, "sol": solp, "content": content, "MX_over_gPhi": kx, "v311_ratio": v311,
           "assigned_m2_over_Phi2": m2, "unassigned": problems, "leftover": leftover, "light_needed": need, "light_found": got,
           "solutions": {}}
    if problems or kx is None or v311 is None:
        rec["error"] = "assignment failed or no (3,1,1) vector"; return rec
    for loops in (2, 3):
        for sv in ((+1, -1) if loops == 2 else (+1,)):
            key = f"{loops}L" + ("" if sv == 1 else "|sv-")
            rec["solutions"][key] = solve(light, m2, kx, v311, loops, sv=sv)
    return rec


if __name__ == "__main__":
    outp = sys.argv[1]; res = []
    for spec_ in sys.argv[2:]:
        tag, solp, content = spec_.split(":")
        r = run_one(tag, solp, content); res.append(r)
        s2 = r["solutions"].get("2L", {}); s3 = r["solutions"].get("3L", {})
        fmt = lambda x: "-" if x is None else (f"{x:.3g}" if isinstance(x, float) else str(x))
        print(f"{tag:6s} {content:6s} {solp:28s} unassigned={r['unassigned']} | 2L: v_R={fmt(s2.get('v_R'))} M_U={fmt(s2.get('M_U'))} aU^-1={fmt(s2.get('alpha_U_inv'))} "
              f"tau={fmt(s2.get('tau_p_yr'))} tau_dir={fmt(s2.get('tau_dir'))} L2={fmt(s2.get('L2'))} min_ratio={fmt(s2.get('ratio_min'))} ({s2.get('lightest_heavy')}) | "
              f"3L: tau={fmt(s3.get('tau_p_yr'))} L3={fmt(s3.get('L3'))} | 2L sv-: tau={fmt(r['solutions'].get('2L|sv-', {}).get('tau_p_yr'))}", flush=True)
    json.dump(res, open(os.path.join(HERE, outp), "w"), indent=1, default=str)
