"""Coherent GUT-scalar threshold x f at M_U (own implementation) on top of v_chain: two- and three-loop Lambda for T2."""
import math, json, sys
from fractions import Fraction as F
import numpy as np
from scipy.optimize import fsolve
import v_chain as V
from v_chain import SU2, SU3, bl, F as FF

PI = math.pi
def g(su3, l, r, q): return (SU3[su3], SU2[l], SU2[r], bl(q))
# heavy scalars at M_U in G3221 language for T2 (210 + 126bar + 10 minus Goldstones minus the T2 light ones)
HEAVY = [("real", g(8,1,1,0)), ("cplx", g(3,3,1,F(4,3))), ("real", g(8,1,3,0)), ("cplx", g(3,1,3,F(4,3))),
         ("real", g(1,1,3,0)), ("cplx", g(6,2,2,F(2,3))), ("cplx", g(3,2,2,F(-2,3))), ("cplx", g(1,2,2,F(-2))),
         ("cplx", g(3,1,1,F(-2,3))), ("cplx", g(3,1,1,F(2,3))), ("cplx", g(6,3,1,F(2,3))), ("cplx", g(3,3,1,F(-2,3))),
         ("cplx", g(1,3,1,F(-2))), ("cplx", g(6,1,3,F(-2,3))), ("cplx", g(3,1,3,F(2,3))), ("cplx", g(3,2,2,F(4,3))),
         ("cplx", g(3,2,2,F(-4,3))), ("cplx", g(3,1,1,F(-2,3))), ("cplx", g(3,1,1,F(2,3))), ("cplx", g(1,2,2,0))]
def S(reps, i):
    s = reps[i][1]
    for k, r in enumerate(reps):
        if k != i: s *= r[0]
    return s
def D_gut(f):
    d = np.zeros(4)
    for kind, reps in HEAVY:
        c = {"real": F(1,6), "cplx": F(1,3)}[kind]
        for i in range(4):
            d[i] += float(c*S(reps, i))*math.log(f)/(2*PI)
    return d
def solve(content, loops, M_s, y_s, f):
    bsm0, bijsm0 = V.mv(V.CG_SM, V.sm_fields(0,0)); bsm1, bijsm1 = V.mv(V.CG_SM, V.sm_fields(6,2))
    bg, bijg = V.mv(V.CG_G, V.g_fields(content, True))
    yt2 = 0.95**2
    s0 = V.Seg(bsm0, bijsm0, loops=loops, Y=np.array([1.7,1.5,2.0])*yt2*0.6)
    s1 = V.Seg(bsm1, bijsm1, loops=loops, Y=np.array([1.7,1.5,2.0])*yt2*0.6 + 14*y_s**2)
    sg = V.Seg(bg, bijg, loops=loops, Y=np.array([4,4,4,4])*yt2*0.3 + 14*y_s**2)
    t0, ts = math.log(V.MZ), math.log(M_s)
    D = D_gut(f)
    def to_MU(x):
        tv, tu, a2r = x
        a = np.array([V.A1, V.A2, V.A3])
        a,_,_ = V.run(s0, a, t0, ts); a,_,_ = V.run(s1, a, ts, tv)
        gg = np.array([a[2], a[1], a2r, 2.5*(a[0]-0.6*a2r)])
        gg,_,_ = V.run(sg, gg, tv, tu)
        return gg + D
    def resid(x):
        gg = to_MU(x); return np.array([gg[0]-gg[1], gg[2]-gg[1], gg[3]-gg[1]])
    x, info, ier, msg = fsolve(resid, np.array([math.log(2.5e13), math.log(2e16), 46.0]), full_output=True, xtol=1e-12)
    gg = to_MU(x)
    return math.exp(x[0]), math.exp(x[1]), float(gg[1]), ier
out = {}
for M_s in (5e12, 6e12, 7e12, 1e13):
    y_s = M_s/2.9e13
    for f in (0.5, 1.0, 2.0):
        vR, MU, aU, ier = solve("T2", 2, M_s, y_s, f)
        l2 = V.landau(MU, aU, 2, M_phi=1e17, y_s=y_s)["Lambda_over_MPl"]
        l3 = V.landau(MU, aU, 3, M_phi=1e17, y_s=y_s)["Lambda_over_MPl"]
        out[f"T2_Ms{M_s:.0e}_gutx{f}"] = {"v_R": vR, "M_U": MU, "aU": aU, "L2": l2, "L3": l3, "ier": ier}
        print(f"T2 M_s={M_s:.0e} GUT x{f}: v_R={vR:.3e} M_U={MU:.3e} aU={aU:.3f} L2/MPl={l2:.3f} L3/MPl={l3:.3f}")
json.dump(out, open("v_coherent.json","w"), indent=1)
