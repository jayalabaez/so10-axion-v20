"""Verifier: round-trip test of fit.observables() in the convention the code actually uses (holomorphic Weyl Yukawas:
term f_L^T Y f^c and (1/2) nu^T m nu).  In that convention the left rotation U (f_L = U f^m) satisfies Y = U^* D V^T and the
Majorana matrix is m = W^* D W^dag with nu = W nu^m, so U_PMNS = Ue^dag W.  The code's U = conj(Ue)^dag T with the Takagi
factor T = W^* equals U_PMNS^* : moduli (angles) correct, Dirac phases sign-flipped.  (My first test built the matrices in
the \bar f_L M f_R convention and therefore disagreed; that was my error, not the code's.)"""
import math, numpy as np, fit
rng = np.random.default_rng(11)
v = 174.1
def ru():
    return np.linalg.qr(rng.normal(size=(3, 3)) + 1j * rng.normal(size=(3, 3)))[0]
mu = np.array([1.25e-3, 0.632, 169.5]); md = np.array([2.72e-3, 0.054, 2.866]); me = np.array([4.87e-4, 0.1027, 1.7464])
s12, s23, s13, dl = 0.22501, 0.04182, 0.003731, 1.1472
V = fit.ckm_matrix(s12, s23, s13, dl)
Uu = ru(); Ud = Uu @ V          # V_CKM = Uu^dag Ud
Yu = Uu.conj() @ np.diag(mu) @ ru().T / v
Yd = Ud.conj() @ np.diag(md) @ ru().T / v
Ue = ru()
Ye = Ue.conj() @ np.diag(me) @ ru().T / v
n12, n23, n13, nd = math.sqrt(0.308), math.sqrt(0.470), math.sqrt(0.02215), math.radians(212)
U = fit.pmns_matrix(n12, n23, n13, nd)
W = Ue @ U
mn = np.array([0.0, math.sqrt(7.49e-5), math.sqrt(2.513e-3)]) * 1e-9
mnu = W.conj() @ np.diag(mn) @ W.conj().T
obs = fit.observables(Yu, Yd, Ye, mnu, v)
print("CKM  s12 %.5f s23 %.5f s13 %.6f delta %.4f" % (obs["s12"], obs["s23"], obs["s13"], obs["delta"]), " (in: %.5f %.5f %.6f %.4f)" % (s12, s23, s13, dl))
print("PMNS sin2 th12 %.4f th23 %.4f th13 %.5f delta %.1f deg" % (obs["sin2_th12"], obs["sin2_th23"], obs["sin2_th13"], obs["delta_deg"]), " (in: 0.308 0.470 0.02215 212)")
print("dm21 %.4g dm31 %.4g (in 7.49e-5 2.513e-3)" % (obs["dm21"], obs["dm31"]))
