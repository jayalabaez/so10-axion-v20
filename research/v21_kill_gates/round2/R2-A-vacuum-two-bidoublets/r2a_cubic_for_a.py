"""R2-A: cubic/quartic rows along the EW direction u = q_vev(a*) of a given EW-target npz (key 'a'), for the light-cubic
constraints and the exact tree lambda_eff (as r2_cubic_rows.py, but with the target a* taken verbatim so that the
EW eigen-equation of r2_lp6 --ew_target and the cubic rows refer to the SAME direction).
V is quartic: rows at q0 +- eta u give dH_i, d2H_i exactly: b_i = dH_i u, V4_i = u.d2H_i.u.
usage: python -B r2a_cubic_for_a.py <tag> <ew npz>   -> cubic_<ew npz stem>.npz (keys b_up, V4_up, u_up, a, ids)"""
import sys, time, numpy as np
import k3_common as K
import r2_compose as RC
tag, ewf = sys.argv[1], sys.argv[2]
ze = np.load(K.SCRATCH / ewf); a = np.asarray(ze["a"], complex); a = a / np.linalg.norm(a)
nt = RC.Neutral(tag); u = nt.q_of_a(a); cm = nt.comp_of_a(a)
Z = np.load(K.SCRATCH / f"{tag}_rows.npz"); q0 = Z["q"]; ids = [str(x) for x in Z["ids"]]; H0 = Z["hess"]
eta = 0.1; t0 = time.time()
rp = K.parameter_rows(K.chart.unpack(q0 + eta * u)); rm = K.parameter_rows(K.chart.unpack(q0 - eta * u))
Hp = np.array([np.asarray(rp[i].hessian, float) for i in ids]); Hm = np.array([np.asarray(rm[i].hessian, float) for i in ids])
Hp = 0.5 * (Hp + np.transpose(Hp, (0, 2, 1))); Hm = 0.5 * (Hm + np.transpose(Hm, (0, 2, 1)))
dH = (Hp - Hm) / (2 * eta); d2H = (Hp + Hm - 2 * H0) / eta ** 2
b = np.einsum("pij,j->pi", dH, u); V4 = np.einsum("i,pij,j->p", u, d2H, u)
outn = "cubic_" + ewf.replace(".npz", "") + ".npz"
np.savez_compressed(K.SCRATCH / outn, ids=np.array(ids), eta=eta, b_up=b, V4_up=V4, u_up=u, a=a, r=abs(cm["r"]), s=np.array([cm["s"].real, cm["s"].imag]))
print(f"saved {outn} in {time.time()-t0:.0f}s; |r| {abs(cm['r']):.5g} s {cm['s']:.5g}; max|b| {np.max(np.abs(b)):.3e}; V4 range [{V4.min():.3f}, {V4.max():.3f}]")
