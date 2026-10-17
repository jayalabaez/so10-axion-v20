"""Step-size / timing check of the verifier chain at the nominal three-loop point (T2, M_s=1e13, Phi at 1e17)."""
import sys, os, time, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import vp_chain as vc
import numpy as np
for h_chain, h_lan in ((0.004, 0.002), (0.02, 0.01), (0.05, 0.02)):
    t0 = time.time()
    # monkeypatch default step
    orig = vc.rk4
    def rk4h(seg, a0, t0_, t1, h=h_chain, stop_at_alpha_inv=None, _o=orig):
        return _o(seg, a0, t0_, t1, h=h, stop_at_alpha_inv=stop_at_alpha_inv)
    vc.rk4 = rk4h
    m = vc.Model(content="T2", loops=3, M_s=1e13, y_s=1e13/2.9e13, M_phi=1e17)
    s = m.solve()
    l2 = m.landau(s["M_U"], s["alpha_U_inv"], loops=2, h=h_lan)
    l3 = m.landau(s["M_U"], s["alpha_U_inv"], loops=3, h=h_lan)
    vc.rk4 = orig
    print(f"h_chain={h_chain} h_lan={h_lan}: v_R={s['v_R']:.6e} M_U={s['M_U']:.6e} aU={s['alpha_U_inv']:.6f} "
          f"L2={l2['ratio']:.6f} L3={l3['ratio']:.6f} ainv_MPl_3L={l3['a_inv_MPl']:.5f} time={time.time()-t0:.1f}s", flush=True)
