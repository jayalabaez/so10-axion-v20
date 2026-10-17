"""Independent verification of the K0-contract result, v2 (feasibility/standards lens).  Rebuilt from scratch;
corrects the v1 partial attempt (verify_k0.py) in two places: (i) the f2-decay enumeration now uses SO(10)
tensor-product rules for ALL two-fermion operators (v1 and the researcher both missed F Vec3 H10* S^5 Phi17*),
(ii) the H-H pairing is taken from the configuration in force (kappa = -r0^2/(4 r_S): Im-10 doublet at M_I,
tuned doublet massless at tree level), so no (M_s/m_H)^8 or kappa<S>/m_H^2 suppression applies.
Labels: EXACT (integer/Fraction arithmetic and tensor-product rules), NUM, EST as stated per item.
"""
from __future__ import annotations

import itertools
import json
import math
from fractions import Fraction as Fr
from pathlib import Path

import sympy

HERE = Path(__file__).resolve().parent
MPL = 2.435e18
CHI = 0.0755 ** 4
L16 = 16 * math.pi ** 2
GEV_S = 6.582e-25
out: dict = {}

FERM = [("F", 16, 1, 3), ("TenA", 10, -1, 1), ("TenB", 10, 5, 1), ("Vec1", 16, 0, 1), ("Vec1bar", -16, 4, 1),
        ("Vec2", 16, -3, 1), ("Vec2bar", -16, 7, 1), ("Vec3", 16, -6, 1), ("Vec3bar", -16, 10, 1),
        ("PhiV", 16, -9, 1), ("PhiVbar", -16, -8, 1), ("SingN", 1, -3, 2), ("SingM", 1, -1, 2)]
SCAL = [("Phi210", 210, 0, True), ("Delta126bar", -126, -2, False), ("H10", 10, -2, False), ("S", 1, 4, False),
        ("Phi17", 1, 17, False)]
T_SO10 = {1: Fr(0), 10: Fr(1), 16: Fr(2), 126: Fr(35), 210: Fr(56)}
DIM = {1: 1, 10: 10, 16: 16, 126: 126, 210: 210}
SELF = {1, 10, 45, 54, 120, 210}
def conj(r): return r if abs(r) in SELF else -r
# complete two-factor products needed (convention: 16x16 contains 126, so that 16.16.126bar is invariant)
TP = {(16, 16): [10, 120, 126], (-16, -16): [10, 120, -126], (-16, 16): [1, 45, 210], (10, 10): [1, 45, 54],
      (10, 16): [16, 144], (-16, 10): [-16, -144], (1, 1): [1], (1, 10): [10], (1, 16): [16], (-16, 1): [-16]}
def tp(a, b): return TP[tuple(sorted((a, b)))]

# 1. anomalies, indices, b_X (EXACT) -----------------------------------------------------------------------
a_so10 = sum(Fr(g) * T_SO10[abs(r)] * x for _n, r, x, g in FERM)
a_grav = sum(Fr(g) * DIM[abs(r)] * x for _n, r, x, g in FERM)
a_x3 = sum(Fr(g) * DIM[abs(r)] * x ** 3 for _n, r, x, g in FERM)
t_s = sum(Fr(g) * T_SO10[abs(r)] for n, r, x, g in FERM if n not in ("F", "PhiV", "PhiVbar"))
t_phi = sum(Fr(g) * T_SO10[abs(r)] for n, r, x, g in FERM if n in ("PhiV", "PhiVbar"))
b_x = sum(Fr(2, 3) * g * DIM[abs(r)] * x * x for _n, r, x, g in FERM) + sum(Fr(1, 3) * DIM[abs(r)] * x * x for _n, r, x, real in SCAL if not real)
# SO(10) one-loop b with F17 content: -11/3 C2 + 2/3 sum T_F + 1/3 sum T_S(complex) + 1/6 T_S(real)
b1_so10 = Fr(-11, 3) * 8 + Fr(2, 3) * sum(Fr(g) * T_SO10[abs(r)] for _n, r, _x, g in FERM) + Fr(1, 6) * 56 + Fr(1, 3) * (35 + 1)
out["anomalies"] = {"SO10^2 X": str(a_so10), "grav X": str(a_grav), "X^3": str(a_x3), "all_zero": a_so10 == a_grav == a_x3 == 0,
                    "T_S": str(t_s), "T_Phi": str(t_phi), "b_X_integer_X": str(b_x), "b1_SO10_F17": str(b1_so10),
                    "alpha_X_inv_min_at_M_U(alpha_X(MPl)=1)": 1 + float(b_x) / (2 * math.pi) * math.log(MPL / 2.13e16)}

# 2. renormalizable catalogue (EXACT) --------------------------------------------------------------------------
ins = [("mass", 1, 0)]
for n, r, x, real in SCAL:
    ins.append((n, r, x))
    if not real:
        ins.append(("conj[%s]" % n, conj(r), -x))
found = []
for (fa, ra, xa, _ga), (fb, rb, xb, _gb) in itertools.combinations_with_replacement(FERM, 2):
    for lab, sr, sx in ins:
        if xa + xb + sx == 0 and conj(sr) in tp(ra, rb):
            found.append("%s.%s.%s" % (fa, fb, lab))
DECLARED = {"F.F.H10", "F.F.Delta126bar", "F.Vec2.conj[H10]", "Vec3bar.PhiVbar.H10", "Vec1.Vec1bar.conj[S]",
            "Vec2.Vec2bar.conj[S]", "Vec3.Vec3bar.conj[S]", "PhiV.PhiVbar.Phi17", "TenA.TenB.conj[S]",
            "TenA.SingM.conj[H10]", "TenB.SingN.H10", "SingN.SingM.S"}
out["couplings"] = {"enumerated": sorted(found), "count": len(found), "declared_equals_enumerated": set(found) == DECLARED,
                    "Z17_only_allowed_but_X_forbidden_bare_masses": ["PhiV.PhiVbar (X=-17): forbidden by gauged U(1)_X, allowed by Z17 alone"],
                    "model_file_defect": "v21 LagHC omits kappaH H10.H10.S (present in v20 LagHC); 'scalar rows verbatim' is false"}

# 3. kernel, PQ, N, E/N, N_DW (EXACT) --------------------------------------------------------------------------
fn = [f[0] for f in FERM]; sn = ["H10", "Delta126bar", "S", "Phi17"]
q = {n: sympy.Symbol("q_" + n) for n in fn + sn}
eqs = []
for term in found:
    a, b, s = term.split(".")
    e = q[a] + q[b]
    if s.startswith("conj["):
        e -= q[s[5:-1]]
    elif s not in ("mass", "Phi210"):
        e += q[s]
    eqs.append(e)
h, d, s_, _p = q["H10"], q["Delta126bar"], q["S"], q["Phi17"]
eqs += [2 * h + s_, -h + d, -h - d - s_, 2 * d - 2 * h]
A = sympy.Matrix([[sympy.diff(e, q[n]) for n in fn + sn] for e in eqs])
null = A.nullspace()
TSU3 = {16: Fr(2), 10: Fr(1), 1: Fr(0)}; TRQ2 = {16: Fr(16, 3), 10: Fr(8, 3), 1: Fr(0)}
def n_e(ch):
    return (sum(g * TSU3[abs(r)] * Fr(ch[n]) for n, r, _x, g in FERM), sum(g * TRQ2[abs(r)] * Fr(ch[n]) for n, r, _x, g in FERM))
xvec = {n: x for n, _r, x, _g in FERM}; xvec.update({"H10": -2, "Delta126bar": -2, "S": 4, "Phi17": 17})
g2 = {n: 0 for n in fn + sn}; g2["Phi17"] = 1; g2["PhiV"] = -1
pq = {n: xvec[n] - 17 * g2[n] for n in fn + sn}
N_pq, E_pq = n_e(pq)
M = 68; vac = set()
for a in range(M):
    for b in range(M):
        if (17 * a - 4 * b) % M == 0:
            vac.add(min(((a + 4 * k) % M, (b + 17 * k) % M) for k in range(M)))
out["kernel_pq"] = {"rank": A.rank(), "kernel_dim": len(null), "N": str(N_pq), "E": str(E_pq), "E/N": str(E_pq / N_pq),
                    "N_DW_mod_gauge_bruteforce": len(vac), "N_DW_S_only_strings": 2 * int(N_pq) // 4,
                    "note": "pre-inflationary PQ breaking (FINAL: T_RH << 1e12, theta_i ~ 0.4): N_DW is moot"}

# 4. mod-4 lemma (EXACT) -----------------------------------------------------------------------------------------
Z = {16: 1, -16: 3, 10: 2, -126: 2, 126: 2, 210: 0, 1: 0}
f1 = {"Vec1": 1, "Vec1bar": -1}; f2 = {"Vec3": -1, "Vec3bar": 1, "PhiV": 1, "PhiVbar": -1}
f3 = {"TenA": 1, "SingN": 1, "TenB": -1, "SingM": -1}
viol = [n for n, r, x, _g in FERM if (x - (Z[r] + g2[n] - f1.get(n, 0) + 3 * f2.get(n, 0) + f3.get(n, 0))) % 4]
viol += [n for n, r, x, _real in SCAL if (x - (Z[r] + g2.get(n, 0))) % 4]
out["lemma_violations"] = viol

# 5. decay operators of the f1/f2 sectors: exhaustive two-fermion enumeration with SO(10) rules (EXACT for the
#    class 'two fermions x (<= 1 non-singlet scalar or its conjugate) x S^a S*^b Phi17^c Phi17*^d', dim <= 11) -----
FX = {n: (r, x) for n, r, x, _g in FERM}
SX = {"H10": (10, -2), "H10*": (10, 2), "Delta": (-126, -2), "Delta*": (126, 2), "Phi210": (210, 0), "none": (1, 0)}
def fcharges(n):  # (f1, f2, f3)
    return (f1.get(n, 0), f2.get(n, 0), f3.get(n, 0))
results = {}
for (fa, (ra, xa)), (fb, (rb, xb)) in itertools.combinations_with_replacement(FX.items(), 2):
    for ca, cb in ((False, False), (True, True), (True, False), (False, True)):
        # Lorentz: psi psi (both unconjugated) or psi^dag psi^dag (both conjugated): scalar; mixed needs a derivative (+1)
        deriv = 1 if ca != cb else 0
        Ra = conj(ra) if ca else ra; Rb = conj(rb) if cb else rb
        Xa = -xa if ca else xa; Xb = -xb if cb else xb
        fa_c = tuple((-1 if ca else 1) * v for v in fcharges(fa)); fb_c = tuple((-1 if cb else 1) * v for v in fcharges(fb))
        fch = tuple(u + v for u, v in zip(fa_c, fb_c))
        if fch == (0, 0, 0):
            continue
        prod = tp(Ra, Rb)
        for slab, (sr, sx) in SX.items():
            if conj(sr) not in prod:
                continue
            xs = Xa + Xb + sx
            # S^a Phi17^c with signed powers: 4 a + 17 c = -xs ; minimal |a| + |c|
            best = None
            for c_ in range(-3, 4):
                rem = -xs - 17 * c_
                if rem % 4:
                    continue
                a_ = rem // 4
                dim = 3 + deriv + (0 if slab == "none" else 1) + abs(a_) + abs(c_)
                if best is None or dim < best[0]:
                    best = (dim, a_, c_)
            if best is None:
                continue
            dim, a_, c_ = best
            key = "f=%s" % (fch,)
            lab = "%s%s %s%s %s S^%d Phi17^%d (dim %d%s)" % (fa, "*" if ca else "", fb, "*" if cb else "", slab, a_, c_, dim, ", 1 deriv" if deriv else "")
            if key not in results or dim < results[key][0]:
                results[key] = (dim, [lab])
            elif dim == results[key][0]:
                results[key][1].append(lab)
out["decay_operators_two_fermion_min_dim"] = {k: {"dim": v[0], "operators": v[1]} for k, v in sorted(results.items())}

# Vec3 lifetime through the genuine dim-10 operator F Vec3 H10* S^5 Phi17* / M_Pl^6 (EST): direct two-body
# decay Vec3 -> F + light H (SM doublet massless at tree level in the G3 member in force)
sig, phi = 1e13 / 0.304, 1e17
g_eff = sig ** 5 * phi / MPL ** 6
for M3 in (1e13,):
    Gam = g_eff ** 2 * M3 / (16 * math.pi)
    out["Vec3_lifetime"] = {"operator": "F Vec3 conj[H10] S^5 conj[Phi17] / M_Pl^6 (16.16.10 singlet; X = 1-6+2+20-17 = 0)",
                            "g_eff(c=1)": g_eff, "Gamma_GeV": Gam, "tau_s": GEV_S / Gam, "age_universe_s": 4.35e17,
                            "researcher_named_operator": "F Vec3 Delta* S^5 Phi17*: NOT SO(10) invariant (16.16.126 has no singlet); the dimension 10 and tau ~ 1e15-1e16 s survive via the H10* operator",
                            "note": "decays after recombination (t ~ 3e8 yr): CMB/diffuse-photon bounds on its abundance are far stronger than for a stable relic"}

# 6. configuration kappa (G3 member in force: kappa = -r0^2/(4 r_S) <-> kappa <S> = M_I^2/4, Im-10 doublet at M_I) ---
for MI in (2.5e13, 2.6e13, 3.4e13):
    for S_ in (1e13 / 0.304, 1e13 / 0.374):
        out.setdefault("kappa_configuration", {})["M_I=%.1e,<S>=%.2e" % (MI, S_)] = MI ** 2 / (4 * S_)

# 7. NDA of the variant-E closure at the configuration in force (EST), scan of the planned window ----------------
def dtheta_E(sig, phi, kappa, ms, c=1.0):
    # V ~ c^7 (16pi^2)^-5 (<S>/MPl)^4 (<S><Phi>/MPl^2)^2 (<Phi>^2/MPl^4) (kappa<S>)^3 * (y^8 <S>^8 / ms^8 -> 1 at ms = y<S>)
    return c ** 7 * L16 ** -5 * (sig / MPL) ** 4 * (sig * phi / MPL ** 2) ** 2 * (phi ** 2 / MPL ** 4) * (kappa * sig) ** 3 / CHI
def dtheta_K15(sig, phi, ms, c=1.0):
    # kappa-free two-loop closure: V ~ c^5 (16pi^2)^-2 ms^3 <S>^12 <Phi>^4 / MPl^15
    return c ** 5 * L16 ** -2 * ms ** 3 * sig ** 12 * phi ** 4 / MPL ** 15 / CHI
scan = {}
for ms, ys in ((1e13, 0.304), (1e13, 0.35), (1e13, 0.374), (3e12, 0.091), (3e12, 0.35)):
    sig = ms / ys
    for phi in (1e17, 3e16, 1e16):
        kappa = (2.6e13) ** 2 / (4 * sig)
        scan["M_s=%.0e,y_s=%.3f,<Phi>=%.0e" % (ms, ys, phi)] = {
            "log10_dtheta_E(c=1,config kappa=%.1e)" % kappa: round(math.log10(dtheta_E(sig, phi, kappa, ms)), 2),
            "log10_dtheta_E(c=0.1)": round(math.log10(dtheta_E(sig, phi, kappa, ms, c=0.1)), 2),
            "log10_dtheta_K15_2loop(c=1)": round(math.log10(dtheta_K15(sig, phi, ms)), 2),
            "log10_dtheta_K15_2loop(c=0.3)": round(math.log10(dtheta_K15(sig, phi, ms, c=0.3)), 2),
            "log10_dtheta_declared_dim21": round((math.log10(2) + 4 * math.log10(phi) + 17 * math.log10(sig / MPL) - math.log10(CHI)), 2)}
out["NDA_scan"] = scan
base = dtheta_E(1e13 / 0.304, 1e17, (2.6e13) ** 2 / (4 * 1e13 / 0.304), 1e13)
out["NDA_E_benchmark"] = {"log10_dtheta": math.log10(base), "c_per_operator_for_1e-10 (7 ops)": (1e-10 / base) ** (1 / 7),
                          "kappa_for_1e-10_if_kappa_were_free_GeV": (2.6e13) ** 2 / (4 * 1e13 / 0.304) * (1e-10 / base) ** (1 / 3)}
b15 = dtheta_K15(1e13 / 0.304, 1e17, 1e13)
out["NDA_K15_benchmark"] = {"log10_dtheta": math.log10(b15), "c_per_operator_for_1e-10 (5 ops)": (1e-10 / b15) ** (1 / 5)}

# 8. y_s cap sensitivity to the perturbativity criterion (NUM, pure-Yukawa analytic; gauge terms only widen) ------
caps = {}
for ms in (1e13, 3e12):
    lnr = math.log(MPL / ms)
    for lim, name in ((math.sqrt(4 * math.pi), "sqrt(4pi) [researcher]"), (1.8, "1.8 (a0<=1/2 coupled-channel, sqrt(60) enhancement)"), (1.0, "1.0")):
        caps["M_s=%.0e y(MPl)<=%s" % (ms, name)] = round(1 / math.sqrt(1 / lim ** 2 + 122 / L16 * lnr), 4)
out["ys_cap_pure_yukawa"] = caps

# 9. axion numbers (NUM) ---------------------------------------------------------------------------------------------
def fa_ma(sig, phi=1e17):
    vs, vp = math.sqrt(2) * sig, math.sqrt(2) * phi
    fa = vs * vp / math.sqrt(16 * vs ** 2 + 289 * vp ** 2)
    return fa, 5.70e-6 * 1e12 / fa * 1e6
out["axion"] = {"y_s=0.304": fa_ma(1e13 / 0.304), "y_s=0.374": fa_ma(1e13 / 0.374), "y_s=0.388": fa_ma(1e13 / 0.388), "M_s=3e12,y=0.35": fa_ma(3e12 / 0.35)}

(HERE / "verify_k0_v2.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(json.dumps(out, indent=1, default=str))
