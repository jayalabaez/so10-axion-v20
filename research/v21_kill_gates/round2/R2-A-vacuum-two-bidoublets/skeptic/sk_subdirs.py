"""SKEPTIC helper: the 7 SM-singlet/Delta_R subspace directions (p, a, omega, sigma_std, delta_R, S, Phi17) in the repo chart."""
import sys, numpy as np
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE.parent))
import k3_common as K
chart = K.chart; basis = K.direct.singlet_basis()
def pk(**kw):
    d = dict(phi={}, h=np.zeros(10, complex), sigma={}, s=0j, x=0j); d.update(kw); return chart.pack(K.potential.FieldState(**d))
sig = K.candidate.sigma_std_unit_coordinates()
drc = chart.sigma_coordinates(K.direct.delta_r()); drc = drc / np.linalg.norm(drc)
D = [pk(phi=basis["p"]), pk(phi=basis["a"]), pk(phi=basis["omega"]), pk(sigma=chart.sigma_from_coordinates(sig)),
     pk(sigma=chart.sigma_from_coordinates(drc)), pk(s=1 + 0j), pk(x=1 + 0j)]
np.savez(HERE / "subdirs.npz", D=np.array(D)); print([float(np.linalg.norm(d)) for d in D])
