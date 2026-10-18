"""SKEPTIC: quartic coefficient along my two runaway directions (H05, CONT endpoints; full and Phi+H+Sigma+S parts) for
EVERY designer LP solution in vac/ (operator rows are c-independent, so a4(c) = c . J4)."""
import json, glob
import numpy as np
import sk_loader as LD
ids = [str(x) for x in np.load(LD.VAC / "L6_S2_U8362e_R.npz")["ids"]]
dirs = {}
for tag in ("H05", "CONT"):
    q = np.load(LD.HERE / f"sk_descend_{tag}.npz")["qbest"]
    dirs[tag + "_full"] = q / np.linalg.norm(q)
    qq = q.copy(); qq[LD.BLOCKS["Phi17"]] = 0; dirs[tag + "_noPhi17"] = qq / np.linalg.norm(qq)
J4 = {}
for k, d in dirs.items():
    lams = np.arange(5.0); Js = np.array([LD.J_at(l * d, ids) for l in lams])
    J4[k] = np.linalg.solve(np.vander(lams, 5, increasing=True), Js)[4]
out = {}
for f in sorted(glob.glob(str(LD.VAC / "L*_S*.npz"))):
    if f.endswith("_iter.npz"): continue
    s = np.load(f)
    if "c" not in s.files: continue
    if [str(x) for x in s["ids"]] != ids: continue
    c = np.asarray(s["c"], float); name = f.split("\\")[-1]
    out[name] = {k: float(c @ v) for k, v in J4.items()}
    print("%-26s " % name + "  ".join("%s %+.5f" % (k, v) for k, v in out[name].items()), flush=True)
json.dump(out, open(LD.HERE / "sk_bfb_all.json", "w"), indent=1)
