"""Verifier: synthetic round-trip test of the researcher's observable extraction (CKM, PMNS, seesaw) in fit.py.
Construct Yu, Yd, Ye, m_nu from known angles/masses in the PDG convention and check observables() returns them."""
import json, math, numpy as np, fit
rng = np.random.default_rng(7)
v = 174.1
# charged sector: Yu diagonal, Yd = V diag V^dag-free form: M_d = V_CKM diag(m_d) in the basis where M_u diagonal (left rotation)
mu = np.array([1.25e-3, 0.632, 169.5]); md = np.array([2.72e-3, 0.054, 2.866]); me = np.array([4.87e-4, 0.1027, 1.7464])
s12, s23, s13, dl = 0.22501, 0.04182, 0.003731, 1.1472
V = fit.ckm_matrix(s12, s23, s13, dl)
Wr = np.linalg.qr(rng.normal(size=(3, 3)) + 1j * rng.normal(size=(3, 3)))[0]   # random right-handed rotation (unobservable)
Yu = np.diag(mu) / v
Yd = (V @ np.diag(md) @ Wr) / v
Ue = np.linalg.qr(rng.normal(size=(3, 3)) + 1j * rng.normal(size=(3, 3)))[0]
Ye = (Ue @ np.diag(me) @ Wr.conj().T) / v
# PMNS in the PDG convention: nu_L = U nu_mass, m_nu = U^* D U^dag ; with charged leptons rotated by Ue: m_nu(flavour) = Ue^* ... careful:
# observables() computes U_PMNS = Ue^dag Un with Ye = Ue diag Ue'^dag  (left rotation Ue) and mnu = Un diag Un^T (Takagi).
# For a Majorana mass term (1/2) nu^T m nu, with nu = Un nu_mass, m = Un^* D Un^dag.  Takagi of m gives Un^* -> angles identical, phase sign flips.
n12, n23, n13, nd = math.sqrt(0.308), math.sqrt(0.470), math.sqrt(0.02215), math.radians(212)
U = fit.pmns_matrix(n12, n23, n13, nd)
mn = np.array([0.0, math.sqrt(7.49e-5), math.sqrt(2.513e-3)]) * 1e-9
Un = Ue @ U                      # flavour-basis nu rotation includes the charged-lepton rotation
mnu = Un.conj() @ np.diag(mn) @ Un.conj().T   # PDG: m = U^* D U^dag
obs = fit.observables(Yu, Yd, Ye, mnu, v)
print("CKM  s12 %.5f s23 %.5f s13 %.6f delta %.4f" % (obs["s12"], obs["s23"], obs["s13"], obs["delta"]), " (in: %.5f %.5f %.6f %.4f)" % (s12, s23, s13, dl))
print("PMNS sin2 th12 %.4f th23 %.4f th13 %.5f delta %.1f deg" % (obs["sin2_th12"], obs["sin2_th23"], obs["sin2_th13"], obs["delta_deg"]), " (in: 0.308 0.470 0.02215 212)")
print("dm21 %.4g dm31 %.4g (in 7.49e-5 2.513e-3); masses" % (obs["dm21"], obs["dm31"]), [round(x, 5) for x in obs["m_nu_eV"]])
print("charged masses:", [round(obs[k], 5) for k in ("m_u", "m_c", "m_t", "m_d", "m_s", "m_b", "m_e", "m_mu", "m_tau")])
# seesaw sanity: type I with M_R and Yn: mnu = -v^2 Yn MR^-1 Yn^T ; check against direct inversion for a random case
Yn = rng.normal(size=(3, 3)) * 0.1; Yn = Yn + Yn.T
MR = rng.normal(size=(3, 3)) * 1e12; MR = MR + MR.T
m1 = -(Yn * v) @ np.linalg.solve(MR, (Yn * v).T)
m2 = -(Yn * v) @ np.linalg.inv(MR) @ (Yn * v).T
print("seesaw solve vs inv max rel diff %.2e" % (np.abs(m1 - m2).max() / np.abs(m1).max()))
