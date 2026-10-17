from fractions import Fraction as F
import math, json
# PGJ single-group three-loop (table as transcribed in the repo module and the researcher's k1_lib; checked here only
# as arithmetic on the v21 invariants, independent code path)
PGJ = {"c1.CG^3": F(2857,162), "c1.CG^2*TR": F(-1415,162), "c1.CG*TR^2": F(79,162), "c1.CG^2*TS": F(-545,648),
 "c1.CG*TR*TS": F(29,162), "c1.CG*TS^2": F(-1,324), "c1.CG*CS2": F(-1129,216), "c1.TR*CS2": F(25,54),
 "c1.TS*CS2": F(49,216), "c1.CG*CR2": F(-205,54), "c1.TR*CR2": F(11,27), "c1.TS*CR2": F(23,108),
 "c1.CR3": F(1,3), "c1.CS3": F(-29,12)}
def b3(TR, TS, CR2, CS2, CR3, CS3, CG=F(8)):
    v = {"CG":CG,"TR":TR,"TS":TS,"CR2":CR2,"CS2":CS2,"CR3":CR3,"CS3":CS3}
    s = F(0)
    for k, c in PGJ.items():
        expr = k.split(".",1)[1]; val = c
        for tok in expr.split("*"):
            if "^" in tok:
                n,p = tok.split("^"); val *= v[n]**int(p)
            else: val *= v[tok]
        s += val
    return -3*s
C16, C10, C210, C126 = F(45,8), F(9,2), F(12), F(25,2)
T16, T10, T210, T126 = F(2), F(1), F(56), F(35)
# scalars (real count): 210 real (56), 126bar complex (2x35), 10 complex (2x1)
TS = T210 + 2*T126 + 2*T10
CS2 = T210*C210 + 2*T126*C126 + 2*T10*C10
CS3 = T210*C210**2 + 2*T126*C126**2 + 2*T10*C10**2
def ferm(n16, n10):
    TR = n16*T16 + n10*T10
    CR2 = n16*T16*C16 + n10*T10*C10
    CR3 = n16*T16*C16**2 + n10*T10*C10**2
    return TR, CR2, CR3
out = {}
for lab, (n16, n10) in {"v21_lo (9x16,2x10)": (9,2), "v21_hi (11x16,2x10)": (11,2), "v20_noPQR (13x16)": (13,0), "v20_PQR (19x16)": (19,0)}.items():
    TR, CR2, CR3 = ferm(n16, n10)
    out[lab] = str(b3(TR, TS, CR2, CS2, CR3, CS3))
print(json.dumps(out, indent=1))
# proton lifetime (repo normalisation) for the K3-compatible roots from v_chain.json
import json as J
d = J.load(open("v_chain.json"))
def tau(MX, ainv):
    f_pi, m_p, ah, ar, fq = 0.139, 0.9382720813, 0.012, 2.726, 7.6
    hbar, yr = 6.582119569e-25, 365.25*24*3600
    a = 1/ainv
    return (4/math.pi)*(f_pi**2/m_p)*(MX**4/a**2)/(ah**2*ar**2*fq)*hbar/yr
for k, r in d["roots"].items():
    if r.get("ok") and k.endswith("L2"):
        print(f"{k:22s} v_R={r['v_R']:.3e} M_U={r['M_U']:.3e} aU={r['alpha_U_inv']:.2f} tau_p={tau(r['M_U'], r['alpha_U_inv']):.2e} yr  (Super-K 2.4e34)")
