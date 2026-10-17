"""R2-A: heavy vector masses M/(g|Phi|) at every scanned G3221 tag from the chart tangents (K3 gauge_masses.py
normalisation M^2 = (g^2/2) T^T T, which reproduces K3's Am45 values 0.5774 / 0.6455).  Output gauge_ratios.json:
per tag the 30 SO(10)/G3221 vector masses grouped by degeneracy, M_X = M(3,2,2) (24 real) and M(3,1,1) (6 real)."""
import json, glob, os, numpy as np
D = os.path.dirname(os.path.abspath(__file__))
out = {}
for fn in sorted(glob.glob(os.path.join(D, "*_rows.npz"))):
    tag = os.path.basename(fn)[:-9]
    if tag.startswith("descend"): continue
    Z = np.load(fn)
    if "tangents" not in Z.files: continue
    T = Z["tangents"][:, :45]; M2 = 0.5 * T.T @ T; w = np.sort(np.linalg.eigvalsh(M2))
    nz = w[w > 1e-12]; heavy = nz[nz > 1e-3]; light = nz[nz <= 1e-3]
    # group heavy by degeneracy
    groups = []
    for x in heavy:
        if groups and abs(x - groups[-1][0]) < 1e-4 * max(1e-3, x): groups[-1][1] += 1
        else: groups.append([x, 1])
    g = [(float(np.sqrt(x)), n) for x, n in groups]
    m322 = [m for m, n in g if n == 24]; m311 = [m for m, n in g if n == 6]
    out[tag] = {"point": Z["point"].tolist(), "heavy_groups(M/g|Phi|, n_real)": g, "light_M/g": np.sqrt(light).tolist(),
                "MX_over_gPhi": m322[0] if m322 else None, "M311_over_gPhi": m311[0] if m311 else None,
                "v311_ratio": (m311[0] / m322[0]) if (m322 and m311) else None}
    print(tag, [(round(m, 4), n) for m, n in g], out[tag]["v311_ratio"])
json.dump(out, open(os.path.join(D, "gauge_ratios.json"), "w"), indent=1)
