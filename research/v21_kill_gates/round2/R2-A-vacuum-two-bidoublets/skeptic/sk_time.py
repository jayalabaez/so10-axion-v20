import sys, time, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import k3_common as K
Z = np.load(K.SCRATCH / "Am45_rows.npz"); q = Z["q"]; ids=[str(x) for x in Z["ids"]]
t=time.time(); st=K.chart.unpack(q).validated(); d=K.potential.evaluate_directions(st); j=K.potential.coefficient_jacobian(d); print("J_at", time.time()-t)
J=np.array([float(np.real(j[p])) for p in ids]); print("maxdiff vs stored", np.max(np.abs(J-Z["values"])))
