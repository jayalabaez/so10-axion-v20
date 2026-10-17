import time, numpy as np, k3_common as K
Z = np.load(K.SCRATCH / "Am45_rows.npz"); q = Z["q"].copy()
rng = np.random.default_rng(0); q2 = q + 0.3 * rng.normal(size=q.size)
st = K.chart.unpack(q2).validated()
t0 = time.time(); dirs = K.potential.evaluate_directions(st); jac = K.potential.coefficient_jacobian(dirs); t1 = time.time()
print("evaluate_directions + jacobian:", round(t1 - t0, 3), "s; n =", len(jac))
