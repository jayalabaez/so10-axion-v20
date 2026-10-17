"""Profile the per-direction exact derivative cost (value, gradient, Hessian) and the value-only evaluator."""
import time, collections
import numpy as np
import k3_common as K

Z = np.load(K.SCRATCH / "Am45_rows.npz"); q0 = Z["q"]
rng = np.random.default_rng(1); q = q0 + 0.3 * rng.normal(size=q0.size)
state = K.chart.unpack(q).validated(); q = K.chart.pack(state)
t0 = time.time(); dirs = K.potential.evaluate_directions(state); tv = time.time() - t0
print(f"value-only evaluate_directions: {tv:.2f}s, {len(dirs)} directions")
sel = K.g2_audit.contract_selection(); live = set(sel["direction_ids"])
owners = K.g2_audit._adapter_modules_by_family()
cost = collections.defaultdict(float); count = collections.Counter()
for d in dirs:
    if d.direction_id not in live: continue
    t1 = time.time(); owners[d.base_family].direction_derivative(q, d); dt = time.time() - t1
    cost[(d.base_family, owners[d.base_family].__name__)] += dt; count[d.base_family] += 1
for k, v in sorted(cost.items(), key=lambda kv: -kv[1]):
    print(f"{v:8.2f}s  n={count[k[0]]:3d}  {k[0]}  [{k[1]}]")
print("total", sum(cost.values()))
