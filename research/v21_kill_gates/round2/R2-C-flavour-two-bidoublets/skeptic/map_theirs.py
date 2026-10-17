"""Map the researcher's best points (z vectors) into GUT-scale (H, F, r, s, c_d126) using THEIR proxy layout
(needs their targets tg.sd0/se0), and save them as my parameter vectors P (skchain.pack).  Their code is imported
read-only from the copied folder skeptic/theirs (never edited)."""
import sys, os, json, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "theirs"))
os.chdir(os.path.join(HERE, "theirs"))
import lib_r2c as L, model_r2c as M
sys.path.insert(0, HERE)
import skchain as S

pts = []
V = json.load(open("vscan_fine.json"))
for e in V:
    pts.append(("vscan_fine", e["vR"], e["content"], e["MU"], e["report"]["z"], e["report"]["chi2"], e["report"]["pulls"]))
# main runs (best exact result of each)
import glob
for f in ["main_2e+10_C2_I.json", "main_1e+11_R813_I.json", "main_1e+12_R813_I.json", "main_2e+12_R813_I.json",
          "main_3e+12_R622_I.json", "main_1e+13_R622_I.json", "main_3e+13_R622_I.json", "main_1e+14_R622_I.json"]:
    J = json.load(open(f))
    r = J["exact_results"][0]
    pts.append(("main:" + f, J["vR"], J["content"], J["MU"], r["z"], r["chi2"], None))
d = L.data_set("nufit60_sk", 0.01)
out = []
cache = {}
for tag, vR, c, MU, z, chi2, pulls in pts:
    key = (vR, c, MU)
    if key not in cache:
        cache[key] = M.make_setup(vR, d, content=c, MU=MU)
    setup = cache[key]; tg = setup["targets"]
    lay = M.Layout(typeII=False, free=True)
    z = np.array(z, float)
    G = M.gut_matrices(z[None, :-1], lay, tg.sd0, tg.se0)
    H, Fm, r, s = G["H"], G["F"], G["r"], G["s"]
    cd = np.array([10.0**z[-1]])
    Hd, Fd = S.to_Hdiag(H, Fm)
    P = S.pack(Hd, Fd, r, s, cd)[0]
    out.append({"tag": tag, "vR": vR, "content": c, "MU": MU, "chi2_theirs": chi2, "pulls_theirs": pulls,
                "P": P.tolist(), "z": z.tolist(),
                "env_theirs": {"g_MU": setup["env"]["g_MU"], "g_vR": setup["env"]["g_vR"], "g_sm_vR": setup["env"]["g_sm_vR"],
                               "lam_vR": setup["env"]["lam_vR"], "alpha_inv_vR": setup["env"]["alpha_inv_vR"]}})
    print(tag, f"{vR:.1e}", c, f"chi2_theirs={chi2:.2f}", flush=True)
json.dump(out, open(os.path.join(HERE, "their_points.json"), "w"), indent=1)
