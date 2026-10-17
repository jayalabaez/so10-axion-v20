import sys, time, os
sys.path.insert(0, r"C:\Users\jayal\Downloads\So10Theory2\So10Theory\_g6_nogo")
os.chdir(r"C:\Users\jayal\Downloads\So10Theory2\So10Theory\_g6_nogo")
t0=time.time()
import numpy as np
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_arbitrary_component_potential_values_v20 as potential
import g3_candidate_physical_target_audit_v20 as target
import gauged_u1x_scalar_contract_v20 as contract
print("imports", time.time()-t0)
st = potential.deterministic_state()
t0=time.time()
dirs = potential.evaluate_directions(st)
print("evaluate_directions", time.time()-t0, len(dirs))
for d in dirs:
    print(d.direction_id, d.degree, d.self_conjugate, d.counts, d.base_key, d.basis_label)
