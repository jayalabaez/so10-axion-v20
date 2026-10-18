"""SKEPTIC: quartic coefficient a4 of V_c(lambda d) (L6 couplings) along sub-directions of my H05 descent endpoint
(exact quartic interpolation, J path).  Locates which field blocks the unbounded direction needs."""
import json, itertools
import numpy as np
import sk_loader as LD
sol = np.load(LD.VAC / "L6_S2_U8362e_R.npz"); c = np.asarray(sol["c"], float); ids = [str(x) for x in sol["ids"]]
q = np.load(LD.HERE / "sk_descend_H05.npz")["qbest"]
def a_of(d):
    lams = np.arange(5.0); Vs = np.array([float(c @ LD.J_at(l * d, ids)) for l in lams])
    return np.linalg.solve(np.vander(lams, 5, increasing=True), Vs)
names = ["Phi210", "H10", "Sigma126bar", "S", "Phi17"]
out = {}
for k in range(1, 6):
    for sub in itertools.combinations(names, k):
        qq = np.zeros_like(q)
        for n in sub: qq[LD.BLOCKS[n]] = q[LD.BLOCKS[n]]
        a = a_of(qq / np.linalg.norm(qq)); out["+".join(sub)] = a.tolist()
        print("%-40s a4 = %+.6f  a3 = %+.5f  a2 = %+.5f" % ("+".join(sub), a[4], a[3], a[2]), flush=True)
json.dump(out, open(LD.HERE / "sk_bfb_sub.json", "w"), indent=1)
