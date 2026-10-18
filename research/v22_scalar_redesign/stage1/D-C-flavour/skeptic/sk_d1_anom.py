"""SKEPTIC D1: own exact anomaly arithmetic for the (unchanged) B63 fermion content + quality-vs-chart-point check.
dtheta_tree = 2 <Phi17>^4 <S>^17 / (M_Pl,red^17 chi) (R2-V 4e normalisation, chi^(1/4) = 75.5 MeV) evaluated at the
plan point and at the LP field points actually used by the designer (s = 0.0016, x = 4 chart units), converted with the
designer's own |Phi| = eps M_Pl,red (eps = 0.0113 chain a, 0.024 chain b)."""
from fractions import Fraction as Fr
import json
from pathlib import Path
SP = [("F",16,1,3),("V1",16,-35,2),("Vb1",16,39,1),("V2",16,-28,1),("Vb2",16,32,1),("V3",16,34,1),("Vb3",16,-30,1),
      ("T",10,2,2),("Pb",16,18,1),("N1",1,-63,1),("N1b",1,59,1),("N2",1,-58,1),("N2b",1,54,1),("N3",1,-57,1),("N3b",1,61,1),("NMm",1,-2,2)]
T = {16: 2, 10: 1, 1: 0}
a2 = sum(T[d]*x*m for _,d,x,m in SP); a3 = sum(d*x**3*m for _,d,x,m in SP); ag = sum(d*x*m for _,d,x,m in SP)
MPL, chi = 2.435e18, 0.0755**4
dth = lambda S, P: 2*(P/MPL)**4*(S/MPL)**13*S**4/chi
out = {"SO10^2_X": a2, "X^3": a3, "grav_X": ag,
       "dtheta_plan(S=3e13,Phi17=1e17)": dth(3e13, 1e17),
       "dtheta(S=3e13, Phi17=x*|Phi| chain b = 4*0.024*MPL)": dth(3e13, 4*0.024*MPL),
       "dtheta_LPpoint_chain_a(S=0.0016*0.0113*MPL, Phi17=4*0.0113*MPL)": dth(0.0016*0.0113*MPL, 4*0.0113*MPL),
       "dtheta_LPpoint_chain_b(S=0.0016*0.024*MPL, Phi17=4*0.024*MPL)": dth(0.0016*0.024*MPL, 4*0.024*MPL),
       "S_LP_GeV_chain_a,b": [0.0016*0.0113*MPL, 0.0016*0.024*MPL], "Phi17_LP_GeV_chain_a,b": [4*0.0113*MPL, 4*0.024*MPL],
       "S_max(Phi17=1e17) for dtheta=1e-10": 3e13*(1e-10/dth(3e13, 1e17))**(1/17),
       "s_chart_max_chain_b": 3e13*(1e-10/dth(3e13, 1e17))**(1/17)/(0.024*MPL)}
print(json.dumps(out, indent=1))
json.dump(out, open(Path(__file__).with_name("sk_d1_anom.json"), "w"), indent=1)
