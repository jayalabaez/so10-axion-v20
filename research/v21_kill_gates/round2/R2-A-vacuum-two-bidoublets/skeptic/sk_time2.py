import sys, time, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import k3_common as K
Z = np.load(K.SCRATCH / "Am45_rows.npz"); q = Z["q"]; ids=[str(x) for x in Z["ids"]]
for k in range(3):
    t=time.time(); st=K.chart.unpack(q+0.01*k).validated(); d=K.potential.evaluate_directions(st); j=K.potential.coefficient_jacobian(d); print("J_at", time.time()-t, flush=True)
t=time.time(); full, ranks = K.symmetry_tangents(K.chart.unpack(q).validated()); print("tangents", time.time()-t, np.asarray(full).shape, ranks)
