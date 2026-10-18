"""D2 structural check (NUM, exact rows in float64): sparsity pattern of the (1,2)_{1/2} doublet mass matrix over ALL
51 coupling directions at an SM-direct point (restricted to the stationarity null space c = N y).
An entry that vanishes for every coupling is a structural zero of the orientation (a residual-symmetry selection rule).
Prints |A_ij| max over the null-space basis, and the connected components of the doublet mixing graph.
Slice coordinates: [Phi210 doublet, H10 (X<0 / X>0 halves), Sigma126bar (X<0 / X>0 halves)] with T3R labels."""
import sys, json
import numpy as np
import k3_common as K

for tag in sys.argv[1:]:
    B = np.load(K.SCRATCH / f"{tag}_blocks.npz"); labels = [str(x) for x in B["labels"]]
    meta = json.load(open(K.SCRATCH / f"{tag}_blocks.json", encoding="utf-8"))["blocks"]
    kd = labels.index("(1,2)_|Y|=1/2"); A = B[f"A{kd}"]                 # 51 x 5 x 5
    stat = B["stat_rows"]; _, s_, vt = np.linalg.svd(stat, full_matrices=True); N = vt[stat.shape[0]:].T
    Ay = np.einsum("ia,ijk->ajk", N, A)
    M = np.max(np.abs(Ay), axis=0); M = M / M.max()
    cols = [(m["block"], m.get("T3R"), m.get("X")) for m in meta[kd]["meta"]]
    print(f"[{tag}] point {json.load(open(K.SCRATCH / f'{tag}_rows_meta.json'))['point']}")
    print("   cols:", cols)
    print(np.array2string(M, precision=2, suppress_small=False, max_line_width=200))
    # connected components of |M| > 1e-9
    n = M.shape[0]; adj = M > 1e-9; seen = set(); comps = []
    for i in range(n):
        if i in seen: continue
        st = [i]; comp = []
        while st:
            j = st.pop()
            if j in seen: continue
            seen.add(j); comp.append(j); st += [k for k in range(n) if adj[j, k] and k not in seen]
        comps.append(sorted(comp))
    print("   mixing components:", comps)
