"""SKEPTIC: re-evaluate a skeptic descent endpoint with the J_at path + gauge-tangent check."""
import sys, json, numpy as np
from pathlib import Path
HERE = Path(__file__).resolve().parent; PARENT = HERE.parent; sys.path.insert(0, str(PARENT))
import k3_common as K
solf, tag, dnpz = sys.argv[1:4]
sol = np.load(HERE / solf); c = sol["c"]; ids = [str(x) for x in sol["ids"]]
def J_at(q):
    jac = K.potential.coefficient_jacobian(K.potential.evaluate_directions(K.chart.unpack(np.asarray(q, float)).validated())); return np.array([float(np.real(jac[p])) for p in ids])
q0 = np.load(PARENT / f"{tag}_rows.npz")["q"]; qm = np.load(HERE / dnpz)["qmin"]
Vs = float(c @ J_at(q0)); Vm = float(c @ J_at(qm))
T, _ = K.symmetry_tangents(K.chart.unpack(qm).validated()); T = np.asarray(T, float); h = 1e-4; inv = []
for a in range(T.shape[1]):
    v = T[:, a]; n = np.linalg.norm(v)
    if n < 1e-12: continue
    v /= n; inv.append(abs(float(c @ J_at(qm + h * v)) - float(c @ J_at(qm - h * v))) / (2 * h))
# Higgs-doublet content of the endpoint: H10 and Sigma doublet (1,2)_{1/2} lift norms
B = np.load(PARENT / f"{tag}_blocks.npz"); labels = [str(x) for x in B["labels"]]
proj = {}
for k, lab in enumerate(labels):
    W = B[f"W{k}"]; M = np.column_stack([W.real, W.imag]); u, s, _ = np.linalg.svd(M, full_matrices=False); u = u[:, s > 1e-9]
    proj[lab] = float(np.linalg.norm(u.T @ (qm - q0)))
res = {"V*": Vs, "Vmin-V*": Vm - Vs, "max_tangent_dV": max(inv), "n_tangents": len(inv),
       "displacement_by_SM_block_top6": sorted(proj.items(), key=lambda kv: -kv[1])[:6]}
print(json.dumps(res, default=float)); json.dump(res, open(HERE / f"check_{Path(dnpz).stem}.json", "w"), indent=1, default=float)
