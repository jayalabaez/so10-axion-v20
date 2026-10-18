"""Feedback round (R2-A protocol): lowest point of each fresh descent bank (w.r.t. the coupling vector of the LP point
that launched it) + the 52 R2-A endpoints -> deep_endpoints_fb1.npz.  usage: python -B build_feedback_bank.py <sol> <bank>..."""
import sys, os
import numpy as np
import k3_common as K
solf = sys.argv[1]
c = np.load(K.SCRATCH / solf)["c"]
old = np.load(K.SCRATCH / "deep_endpoints.npz")
Qs, Js, names = list(old["Q"]), list(old["J"]), [str(x) for x in old["names"]]
for bf in sys.argv[2:]:
    B = np.load(K.SCRATCH / bf); J = B["J"]; Q = B["Q"]
    for k in np.argsort(J @ c)[:2]:
        Qs.append(Q[k]); Js.append(J[k]); names.append(f"fb1:{bf}:{k}")
np.savez_compressed(K.SCRATCH / "deep_endpoints_fb1.npz", Q=np.array(Qs), J=np.array(Js), ids=old["ids"], names=np.array(names))
print(len(names), "points in deep_endpoints_fb1.npz")
