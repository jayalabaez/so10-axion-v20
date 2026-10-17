import sys, json, numpy as np
from scipy.optimize import linprog
import k3_common as K
tag = sys.argv[1]
S = json.load(open(K.SCRATCH / f"{tag}_sumrules_phi.json"))
# rebuild the mass forms by re-running the extraction quickly
exec(open("k3_sumrules.py", encoding="utf-8").read().split("rank = np.linalg.matrix_rank")[0].replace("tag = sys.argv[1]; sector = sys.argv[2] if len(sys.argv) > 2 else \"phi\"", f"tag = '{tag}'; sector = 'phi'"))
targets = ["(8,3)_|Y|=0", "(1,3)_|Y|=0"]
others = [n for n in names if n not in targets]
# both targets light: maximise min(others) s.t. targets in [0, 1e-3]... homogeneous: fix targets <= 1, maximise t with others >= t
nf = N.shape[1]
obj = np.zeros(nf + 1); obj[-1] = -1
Aub, bub = [], []
for n in others:
    row = np.zeros(nf + 1); row[:nf] = -rows[n]; row[-1] = 1; Aub.append(row); bub.append(0.0)
for tname in targets:
    row = np.zeros(nf + 1); row[:nf] = rows[tname]; Aub.append(row); bub.append(1.0)   # m2(target) <= 1
    row = np.zeros(nf + 1); row[:nf] = -rows[tname]; Aub.append(row); bub.append(0.0)  # m2(target) >= 0
res = linprog(obj, A_ub=np.array(Aub), b_ub=np.array(bub), bounds=[(-1e4, 1e4)] * nf + [(None, None)], method="highs")
print(tag, "both (8,3,1)_0 and (1,3,1)_0 in [0,1]: max of min(others) =", -res.fun if res.status == 0 else res.message)
for tname in targets:
    Aub2, bub2 = [], []
    for n in others:
        row = np.zeros(nf + 1); row[:nf] = -rows[n]; row[-1] = 1; Aub2.append(row); bub2.append(0.0)
    row = np.zeros(nf + 1); row[:nf] = rows[tname]; Aub2.append(row); bub2.append(1.0)
    row = np.zeros(nf + 1); row[:nf] = -rows[tname]; Aub2.append(row); bub2.append(0.0)
    res = linprog(obj, A_ub=np.array(Aub2), b_ub=np.array(bub2), bounds=[(-1e4, 1e4)] * nf + [(None, None)], method="highs")
    print(tag, f"only {tname} in [0,1]: max of min(others) =", -res.fun if res.status == 0 else res.message)
