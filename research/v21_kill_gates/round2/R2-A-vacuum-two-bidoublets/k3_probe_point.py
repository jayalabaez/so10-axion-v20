"""Exact probe of a subspace point z (p,a,om,r1,r2,s,x) for a coupling vector c: V along the straight segment from q*,
gradient norm and lowest Hessian eigenvalues at z (one rows call), gauge-invariant data (|Phi|, |Sigma|, Sigma.Sigma-type
SU(2)_R invariant |Delta.Delta| via the chart), and the stabiliser dimension (rank of the symmetry tangents).
usage: python -B k3_probe_point.py <solution npz> <z: 7 comma-separated> <tag>
"""
from __future__ import annotations
import sys, json, time, numpy as np
import k3_common as K
import k3_verify as VF

sol = np.load(K.SCRATCH / sys.argv[1]); c = sol["c"]; ids = [str(x) for x in sol["ids"]]; assert ids == VF.ids
z = np.array([float(v) for v in sys.argv[2].split(",")]); tag = sys.argv[3]
chart = K.chart; qstar = VF.q0; Vstar = float(VF.VAL0 @ c)
st = VF.state_of_z(z); qz = chart.pack(st)


def value_at(q):
    dirs = K.potential.evaluate_directions(chart.unpack(q)); jac = K.potential.coefficient_jacobian(dirs)
    return float(sum(c[i] * jac[pid] for i, pid in enumerate(ids)))


t0 = time.time()
seg = []
for lam in np.linspace(0, 1, 11):
    q = (1 - lam) * qstar + lam * qz; seg.append((float(lam), value_at(q) - Vstar))
print("V(segment) - V*:", [(round(l, 2), f"{v:.3e}") for l, v in seg])
rows = K.parameter_rows(st)
g = sum(c[i] * np.asarray(rows[pid].gradient, float) for i, pid in enumerate(ids))
H = sum(c[i] * np.asarray(rows[pid].hessian, float) for i, pid in enumerate(ids)); H = 0.5 * (H + H.T)
w = np.linalg.eigvalsh(H)
full, ranks = K.candidate.symmetry_matrix(st)
Vz = float(sum(c[i] * rows[pid].value for i, pid in enumerate(ids)))
out = {"z": z.tolist(), "V_z_minus_Vstar": Vz - Vstar, "grad_norm": float(np.linalg.norm(g)), "n_zero": int(np.sum(np.abs(w) < 1e-9)), "n_neg": int(np.sum(w < -1e-9)),
       "lowest_eigs": w[:8].tolist(), "ranks": ranks, "block_norms": {n: float(np.linalg.norm(qz[s])) for n, s in K.BLOCKS.items()}, "segment": seg,
       "ranks_at_vacuum": K.candidate.symmetry_matrix(chart.unpack(qstar))[1], "seconds": time.time() - t0}
print(json.dumps({k: v for k, v in out.items() if k != "segment"}, default=float))
json.dump(out, open(K.SCRATCH / f"probe_{tag}.json", "w"), indent=1, default=float)
