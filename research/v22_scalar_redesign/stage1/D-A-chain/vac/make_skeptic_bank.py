"""Bank (Q, J, ids) of the 8 R2-A-skeptic descent endpoints (qmin only in the skeptic npz) for lp_sm --extra_comp."""
import numpy as np
import k3_common as K

files = ["DPB_a_1", "DPB_a_2", "DPB_a_3", "DPB_b_1", "DPB_b_2", "DPB_b_3", "DPD_a_1", "DPD_b_1"]
Z = np.load(K.SCRATCH / "S1_rows.npz"); ids = [str(x) for x in Z["ids"]]
Q, J = [], []
for f in files:
    q = np.load(K.BANKDIR / "skeptic" / f"{f}.npz")["qmin"]
    st = K.chart.unpack(q)
    dirs = K.potential.evaluate_directions(st); jac = K.potential.coefficient_jacobian(dirs)
    Q.append(q); J.append(np.array([jac[pid] for pid in ids], float))
    print(f, "|q| =", float(np.linalg.norm(q)))
np.savez_compressed(K.SCRATCH / "skeptic_endpoints_bank.npz", Q=np.array(Q), J=np.array(J), ids=np.array(ids))
print("saved skeptic_endpoints_bank.npz", np.array(J).shape)
