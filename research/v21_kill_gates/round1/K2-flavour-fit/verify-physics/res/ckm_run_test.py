# Test: does the researcher's SM RGE run the CKM (y_t^2 effect) in its stated (f_L)_i (f^c)_j convention?
import json, math, numpy as np, sys
sys.path.insert(0, '.')
import rge, fit
inp = json.load(open('inputs_mz.json'))
v = inp['VEV']; MZ = inp['MZ']
m = {k: inp['masses_GeV_MZ'][k][0] for k in fit.MASS_KEYS}
s12, s23, s13, dl = [inp['ckm_MZ'][k][0] for k in fit.CKM_KEYS]
V = fit.ckm_matrix(s12, s23, s13, dl)
Yu = np.diag([m['m_u'], m['m_c'], m['m_t']]).astype(complex) / v
Yd = (V @ np.diag([m['m_d'], m['m_s'], m['m_b']])).astype(complex) / v
Ye = np.diag([m['m_e'], m['m_mu'], m['m_tau']]).astype(complex) / v
g = rge.gauge_bottom_up(inp, None, 2.6e13, 2.13e16, 'T2')['g_MZ']
y = rge.pack_sm(g, 0.26, Yu, Yd, Ye)
for mu in [1e6, 1e10, 2.6e13, 2e16]:
    yy = rge.run_sm(y, MZ, mu, False)
    _, _, Yu2, Yd2, Ye2, _ = rge.unpack_sm(yy, False)
    obs = fit.observables(Yu2, Yd2, Ye2, np.eye(3)*1e-12, v)
    print(f"mu={mu:.1e}: s12={obs['s12']:.5f} s23={obs['s23']:.5f} s13={obs['s13']:.6f} delta={obs['delta']:.4f} | yt={obs['m_t']/v:.4f} yb={obs['m_b']/v:.5f} ytau={obs['m_tau']/v:.5f} mb/mtau={obs['m_b']/obs['m_tau']:.4f} ms/mmu={obs['m_s']/obs['m_mu']:.4f} md/me={obs['m_d']/obs['m_e']:.3f}")
# Same with transposed Yukawas (i.e. feeding the RGE the (f^c)_i (f_L)_j convention) to see which convention it implements
y = rge.pack_sm(g, 0.26, Yu.T, Yd.T, Ye.T)
yy = rge.run_sm(y, MZ, 2e16, False)
_, _, Yu2, Yd2, Ye2, _ = rge.unpack_sm(yy, False)
obs = fit.observables(Yu2.T, Yd2.T, Ye2.T, np.eye(3)*1e-12, v)
print(f"TRANSPOSED feed, mu=2e16: s12={obs['s12']:.5f} s23={obs['s23']:.5f} s13={obs['s13']:.6f} | yt={obs['m_t']/v:.4f} yb={obs['m_b']/v:.5f}")
