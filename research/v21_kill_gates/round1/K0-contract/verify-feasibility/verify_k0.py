"""Independent verification of the K0-contract researcher result (feasibility/standards lens).
Everything here is rebuilt from scratch (no import of the researcher's scripts).
Labels: EXACT (integer/Fraction arithmetic, tensor-product rules), NUM, EST, as stated per item.
"""
from __future__ import annotations

import itertools
import json
import math
from fractions import Fraction as Fr
from math import gcd
from pathlib import Path

import sympy

HERE = Path(__file__).resolve().parent
MPL = 2.435e18          # reduced Planck mass (user decision in force)
CHI = 0.0755 ** 4        # GeV^4 (chi^(1/4) = 75.5 MeV)
L16 = 16 * math.pi ** 2
out: dict = {}

# ---------------------------------------------------------------------------------------------------
# 1. field content (left-handed Weyl), SO(10) signed dims, X charges, generations
# ---------------------------------------------------------------------------------------------------
FERM = [("F", 16, 1, 3), ("TenA", 10, -1, 1), ("TenB", 10, 5, 1), ("Vec1", 16, 0, 1), ("Vec1bar", -16, 4, 1),
        ("Vec2", 16, -3, 1), ("Vec2bar", -16, 7, 1), ("Vec3", 16, -6, 1), ("Vec3bar", -16, 10, 1),
        ("PhiV", 16, -9, 1), ("PhiVbar", -16, -8, 1), ("SingN", 1, -3, 2), ("SingM", 1, -1, 2)]
SCAL = [("Phi210", 210, 0, True), ("Delta126bar", -126, -2, False), ("H10", 10, -2, False), ("S", 1, 4, False),
        ("Phi17", 1, 17, False)]
T_SO10 = {1: Fr(0), 10: Fr(1), 16: Fr(2), 126: Fr(35), 210: Fr(56)}
DIM = {1: 1, 10: 10, 16: 16, 126: 126, 210: 210}

# ---- anomalies (EXACT) -----------------------------------------------------------------------------
a_so10 = sum(Fr(g) * T_SO10[abs(r)] * x for _n, r, x, g in FERM)
a_grav = sum(Fr(g) * DIM[abs(r)] * x for _n, r, x, g in FERM)
a_x3 = sum(Fr(g) * DIM[abs(r)] * x ** 3 for _n, r, x, g in FERM)
t_s = sum(Fr(g) * T_SO10[abs(r)] for n, r, x, g in FERM if n not in ("F", "PhiV", "PhiVbar"))
t_phi = sum(Fr(g) * T_SO10[abs(r)] for n, r, x, g in FERM if n in ("PhiV", "PhiVbar"))
# U(1)_X one-loop coefficient (integer-X normalisation): (2/3) sum_Weyl dim X^2 + (1/3) sum_cplx scalars dim X^2
b_x = sum(Fr(2, 3) * g * DIM[abs(r)] * x * x for _n, r, x, g in FERM) + sum(
    Fr(1, 3) * DIM[abs(r)] * x * x for _n, r, x, real in SCAL if not real)
out["anomalies"] = {"SO10^2 X": str(a_so10), "grav X": str(a_grav), "X^3": str(a_x3), "T_S": str(t_s),
                    "T_Phi": str(t_phi), "b_X": str(b_x), "all_zero": a_so10 == 0 and a_grav == 0 and a_x3 == 0}
# U(1)_X Landau pole: alpha_X^-1(mu) = alpha_X^-1(MPl) + b_X/(2 pi) ln(MPl/mu); require alpha_X^-1(MPl) >= 1
for name, mu in (("M_U=2.13e16", 2.13e16), ("<Phi17>=1e17", 1.0e17)):
    ainv = 1.0 + float(b_x) / (2 * math.pi) * math.log(MPL / mu)
    out["anomalies"]["alpha_X_inv_min_at_" + name] = ainv
    out["anomalies"]["g_X_max_at_" + name] = math.sqrt(4 * math.pi / ainv)

# ---- renormalizable coupling enumeration (EXACT, independent implementation) ------------------------
SELF = {1, 10, 45, 54, 120, 210}
def conj(r): return r if abs(r) in SELF else -r
TP = {(16, 16): [10, 120, 126], (-16, -16): [10, 120, -126], (-16, 16): [1, 45, 210], (10, 10): [1, 45, 54],
      (10, 16): [16, 144], (-16, 10): [-16, -144], (1, 1): [1], (1, 10): [10], (1, 16): [16], (-16, 1): [-16]}
def tp(a, b): return TP[tuple(sorted((a, b)))]
ins = [("mass", 1, 0)]
for n, r, x, real in SCAL:
    ins.append((n, r, x))
    if not real:
        ins.append(("conj[%s]" % n, conj(r), -x))
found = []
for (fa, ra, xa, ga), (fb, rb, xb, gb) in itertools.combinations_with_replacement(FERM, 2):
    prod = tp(ra, rb)
    for lab, sr, sx in ins:
        if xa + xb + sx == 0 and conj(sr) in prod:
            found.append("%s.%s.%s" % (fa, fb, lab))
DECLARED = {"F.F.H10", "F.F.Delta126bar", "F.Vec2.conj[H10]", "Vec3bar.PhiVbar.H10", "Vec1.Vec1bar.conj[S]",
            "Vec2.Vec2bar.conj[S]", "Vec3.Vec3bar.conj[S]", "PhiV.PhiVbar.Phi17", "TenA.TenB.conj[S]",
            "TenA.SingM.conj[H10]", "TenB.SingN.H10", "SingN.SingM.S"}
out["couplings"] = {"enumerated": sorted(found), "count": len(found),
                    "declared_equals_enumerated": set(found) == DECLARED,
                    "missing_in_draft_LagHC_vs_v20": "kappaH H10.H10.S (scalar cubic, census orbit O12) - present in v20 LagHC, absent in v21 draft"}

# ---- global U(1) kernel, PQ, N, E/N (EXACT) ------------------------------------------------------------
fn = [f[0] for f in FERM]
sn = ["H10", "Delta126bar", "S", "Phi17"]
q = {n: sympy.Symbol("q_" + n) for n in fn + sn}
eqs = []
for term in found:
    parts = term.split(".")
    e = q[parts[0]] + q[parts[1]]
    s = parts[2]
    if s.startswith("conj["):
        e -= q[s[5:-1]]
    elif s not in ("mass", "Phi210"):
        e += q[s]
    eqs.append(e)
h, d, s_, p_ = q["H10"], q["Delta126bar"], q["S"], q["Phi17"]
eqs += [2 * h + s_, -h + d, -h - d - s_, 2 * d - 2 * h]   # kappa HHS, Phi210 H* Delta, O38, Delta^2 H*^2
A = sympy.Matrix([[sympy.diff(e, q[n]) for n in fn + sn] for e in eqs])
null = A.nullspace()
# QCD / EM anomaly of a charge vector
TSU3 = {16: Fr(2), 10: Fr(1), 1: Fr(0)}
TRQ2 = {16: Fr(16, 3), 10: Fr(8, 3), 1: Fr(0)}
def n_e(ch):
    N = sum(g * TSU3[abs(r)] * Fr(ch[n]) for n, r, _x, g in FERM)
    E = sum(g * TRQ2[abs(r)] * Fr(ch[n]) for n, r, _x, g in FERM)
    return N, E
xvec = {n: x for n, _r, x, _g in FERM}; xvec.update({"H10": -2, "Delta126bar": -2, "S": 4, "Phi17": 17})
g2 = {n: 0 for n in fn + sn}; g2["Phi17"] = 1; g2["PhiV"] = -1
pq = {n: xvec[n] - 17 * g2[n] for n in fn + sn}
N_pq, E_pq = n_e(pq)
kernel_anoms = []
for v in null:
    ch = {n: int(v[i]) if v[i].is_integer else v[i] for i, n in enumerate(fn + sn)}
    # scale to integers
    den = sympy.ilcm(*[sympy.nsimplify(c).q for c in v])
    chi = {n: int(sympy.nsimplify(v[i]) * den) for i, n in enumerate(fn + sn)}
    N, E = n_e(chi)
    kernel_anoms.append({"vector": chi, "N_QCD": str(N)})
out["kernel_pq"] = {"rank": A.rank(), "kernel_dim": len(null), "kernel_vectors_with_N_QCD": kernel_anoms,
                    "PQ=X-17G2": pq, "N": str(N_pq), "2N": str(2 * N_pq), "E": str(E_pq), "E/N": str(E_pq / N_pq)}
# N_DW: theta_eff = A theta_S + B theta_Phi with X-invariance 4A + 17B = 0 and PQ shift 4A = 2N -> A = 17, B = -4.
# Physical axion circle = T^2/(gauge line of slope (4,17)); theta_eff: T^2/U(1) -> S^1 has degree gcd(17,4) = 1
# -> exactly one minimum of -chi cos(theta_eff) per physical period: N_DW = 1 modulo gauge (EXACT).
# Brute force: enumerate lattice points (theta_S, theta_Phi) in (2pi/M) Z^2 modulo the gauge orbit, count distinct
# theta_eff values that are zeros mod 2pi.
M = 68
vac = set()
for a in range(M):
    for b in range(M):
        if (17 * a - 4 * b) % M == 0:   # theta_eff = 0 mod 2pi
            # reduce modulo gauge (a,b) -> (a+4k, b+17k)
            best = min(((a + 4 * k) % M, (b + 17 * k) % M) for k in range(M))
            vac.add(best)
out["kernel_pq"]["N_DW_mod_gauge_bruteforce"] = len(vac)
out["kernel_pq"]["N_DW_S_only_strings"] = 2 * int(N_pq) // 4

# ---- lemma X = z + G2 - f1 + 3 f2 + f3 (mod 4) (EXACT) ---------------------------------------------------
Z = {16: 1, -16: 3, 10: 2, -126: 2, 126: 2, 210: 0, 1: 0}
f1 = {"Vec1": 1, "Vec1bar": -1}; f2 = {"Vec3": -1, "Vec3bar": 1, "PhiV": 1, "PhiVbar": -1}
f3 = {"TenA": 1, "SingN": 1, "TenB": -1, "SingM": -1}
viol = []
for n, r, x, _g in FERM:
    if (x - (Z[r] + g2[n] - f1.get(n, 0) + 3 * f2.get(n, 0) + f3.get(n, 0))) % 4:
        viol.append(n)
for n, r, x, _real in SCAL:
    if (x - (Z[r] + g2.get(n, 0))) % 4:
        viol.append(n)
out["lemma_violations"] = viol

# ---- variant-E closure: exact structure check -------------------------------------------------------------
# operators: fields with '*' = conjugate (daggered) field.  Rep of a conjugated field = conj(rep).
REPF = {n: r for n, r, _x, _g in FERM}; REPF.update({"H10": 10, "Delta": -126, "S": 1, "Phi17": 1})
XF = dict(xvec); XF["Delta"] = -2
OPS_E = [("Vec1* Vec3* H10 S*", 2), ("Vec1bar* Vec2bar* H10 S* Phi17", 2), ("Vec2* Vec2* H10 S*", 2),
         ("Vec2bar* Vec2bar* Vec3bar* Vec3bar* Phi17 Phi17", 1)]
YUK_E = {"y1 (S* Vec1 Vec1bar)": 2, "y2 (S* Vec2 Vec2bar)": 4, "y3 (S* Vec3 Vec3bar)": 2}
def parse(op):
    fields = []
    for tok in op.split():
        c = tok.endswith("*")
        fields.append((tok.rstrip("*"), c))
    return fields
def so10_singlet_exists(fields):
    """Count singlets in the product of the SO(10) reps, using the known decompositions only for the
    patterns that occur (two spinors + 10; four spinors with identical-pair symmetrisation)."""
    reps = []
    for n, c in fields:
        r = REPF[n]
        if c:
            r = conj(r)
        if r != 1:
            reps.append(r)
    reps.sort()
    if len(reps) == 3 and reps.count(10) == 1:
        sp = [r for r in reps if abs(r) == 16]
        return 10 in tp(sp[0], sp[1])
    if len(reps) == 4 and all(abs(r) == 16 for r in reps):
        # identical-fermion pairs in the Lorentz-scalar channel are SYMMETRIC in gauge indices: 16x16|_sym = 10+126
        # (Vec2bar*)^2 -> (10 + 126), (Vec3bar*)^2 -> (10 + 126); singlet only from 10 x 10 -> exactly 1 structure
        return True
    raise ValueError(reps)
chir = {n: 0 for n in fn}
xsum = {}
snet = {"H10": 0, "S": 0, "Phi17": 0, "Delta": 0}
K = 0
singlet_ok = True
for op, mult in OPS_E:
    fl = parse(op)
    xs = sum((-1 if c else 1) * XF[n] for n, c in fl)
    xsum[op] = xs
    dim = sum(Fr(3, 2) if n in REPF and n in fn else 1 for n, _c in fl)
    K += mult * (dim - 4)
    singlet_ok &= so10_singlet_exists(fl)
    for n, c in fl:
        if n in chir:
            chir[n] += mult * (-1 if c else 1)
        else:
            snet[n] += mult * (-1 if c else 1)
for yk, mult in YUK_E.items():
    inside = yk[yk.index("(") + 1: -1].split()
    for tok in inside:
        c = tok.endswith("*"); n = tok.rstrip("*")
        if n in chir:
            chir[n] += mult * (-1 if c else 1)
        else:
            snet[n] += mult * (-1 if c else 1)
n_kappa = snet["H10"] // 2
snet_final = dict(snet); snet_final["S"] -= n_kappa; snet_final["H10"] = 0   # kappa* H* H* S* absorbs pairs
vev_X = sum(snet_final[k] * XF[k] for k in snet_final)
vev_PQ = sum(snet_final[k] * (pq[k if k != "Delta" else "Delta126bar"]) for k in snet_final)
out["variant_E"] = {"operators": OPS_E, "yukawa_mass_insertions": YUK_E, "X_of_each_operator": xsum,
                    "chirality_balance_per_species": chir, "all_balanced": all(v == 0 for v in chir.values()),
                    "K_planck_power": int(K), "scalar_net_before_kappa": snet, "kappa_vertices": n_kappa,
                    "vev_monomial": snet_final, "vev_X": vev_X, "vev_PQ": vev_PQ,
                    "so10_singlet_structures_exist": singlet_ok,
                    "fermion_fields": 32, "fermion_propagators_mass_basis": 8, "H_propagators": 3,
                    "vertices_mass_basis": 7, "loops": 8 + 3 - 7 + 1}

# ---- NDA magnitude (EST), rebuilt: V = c^7 (16 pi^2)^-5 eps1^4 eps2^2 G (m_pair^2)^3 (M_s/M_loop)^8 --------------
def dtheta(sig, phi, kappa, m_pair2=None, ms=1.0e13, mloop=None, c=1.0, loops=5):
    eps1 = sig / MPL                 # Vec1*Vec3*H S* and Vec2*^2 H S*  (dim 5) with <S*>
    eps2 = sig * phi / MPL ** 2      # Vec1bar* Vec2bar* H S* Phi17 (dim 6)
    G = phi ** 2 / MPL ** 4          # Vec2bar*^2 Vec3bar*^2 Phi17^2 (dim 8)
    pair2 = kappa * sig if m_pair2 is None else m_pair2   # H-H pairing mass^2 (kappa<S> or lambda v_R^2)
    mloop = ms if mloop is None else mloop
    V = c ** 7 * (L16) ** (-loops) * eps1 ** 4 * eps2 ** 2 * G * pair2 ** 3 * (ms / mloop) ** 8
    return V / CHI
base = dtheta(3.3e13, 1e17, 5e12)
out["NDA"] = {"formula": "dtheta = c^7 (16pi^2)^-5 (<S>/MPl)^4 (<S><Phi>/MPl^2)^2 (<Phi>^2/MPl^4) (m_pair^2)^3 (M_s/M_loop)^8 / chi, "
                         "m_pair^2 = kappa<S> (or lambda_{DDHH} v_R^2); the y^8 M_s^8 of the 8 mass insertions cancels the "
                         "M_s^-8 loop integral when M_loop = M_s",
              "baseline(<S>=3.3e13,<Phi>=1e17,kappa=5e12,M_s=1e13)": base, "log10": math.log10(base),
              "researcher_value_log10": 1.12,
              "per_operator_coefficient_needed_for_1e-10 (7 operators)": (1e-10 / base) ** (1 / 7),
              "kappa_needed_for_1e-10_at_planned_scales_GeV": 5e12 * (1e-10 / base) ** (1 / 3),
              "Im10_doublet_mass_at_that_kappa_GeV": math.sqrt(4 * 5e12 * (1e-10 / base) ** (1 / 3) * 3.3e13),
              "alternative_pairing_lambda_DDHH_vR2(lambda=0.1,vR=2.6e13)": dtheta(3.3e13, 1e17, 0, m_pair2=0.1 * (2.6e13) ** 2),
              "heavy_H_only(M_loop=M_U=2.1e16, m_pair^2=M_U^2)": dtheta(3.3e13, 1e17, 0, m_pair2=(2.1e16) ** 2, mloop=2.1e16),
              "scan": {}}
for sig in (3.3e13, 2.6e13, 8.6e12):
    for phi in (1e17, 3e16, 1e16):
        for kappa in (5e12, 5e10, 1e9):
            out["NDA"]["scan"]["<S>=%.1e,<Phi>=%.0e,kappa=%.0e" % (sig, phi, kappa)] = dtheta(sig, phi, kappa, ms=0.35 * sig)
# certificate bound on kappa: kappa^2 < 8 rS^2 -> |kappa| < 2 sqrt2 <S>; Im-10 doublet m^2 = 4|kappa|<S>
out["NDA"]["kappa_max_from_HS_certificate_GeV"] = 2 * math.sqrt(2) * 3.3e13
out["NDA"]["Im10_doublet_mass_max_GeV"] = math.sqrt(4 * 2 * math.sqrt(2) * 3.3e13 * 3.3e13)
out["NDA"]["Im10_doublet_mass_at_kappa=5e12_GeV"] = math.sqrt(4 * 5e12 * 3.3e13)

# ---- f2 (Vec3 pair) decay: genuine SO(10)-singlet operators ------------------------------------------------
# researcher's "F Vec3 Delta* S^5 Phi17*": Delta* = 126; F Vec3 = 16x16 = 10+120+126 contains 126, not 126bar,
# so 16x16x126 has NO singlet (Susyno test t2 in the researcher's own file: '16 16 126 -> 0').  Not an operator.
# genuine dim-10: F* PhiVbar* S*^6 Phi17 (16bar x 16 -> 1), X = -1+8-24+17 = 0: mixes F with PhiVbar (M_Phi ~ 1e17)
# genuine dim-11 without heavy lines: F Vec3 Delta S^6 Phi17* (16x16x126bar -> 1; X = 1-6-2+24-17 = 0) with <Delta_R>=v_R,
#                                     F* Vec3* H* S*^6 Phi17 (16bar x 16bar x 10 -> 1; X = -1+6+2-24+17 = 0) with <H>=v_EW
sig, phi, vR, MPhi, M3, lam3P = 3.3e13, 1e17, 2.6e13, 1e17, 1e13, 1.0
GEV_S = 6.582e-25
mix10 = sig ** 6 * phi / MPL ** 6                     # F-PhiVbar mixing mass
theta10 = mix10 / MPhi
Gamma10 = lam3P ** 2 * theta10 ** 2 * M3 / (16 * math.pi)   # Vec3bar -> F + H via PhiVbar
mix11 = vR * sig ** 6 * phi / MPL ** 7                # nu^c_F - nu^c_Vec3 mixing mass (dim 11)
theta11 = mix11 / M3                                  # worst case (non-degenerate)
Gamma11 = theta11 ** 2 * M3 / (8 * math.pi)           # Y ~ 1 decay of the mixed heavy state
out["Vec3_pair_decay"] = {
    "researcher_dim10_F_Vec3_Delta*_S^5_Phi17*_is_SO10_singlet": False,
    "reason": "16x16 contains 126 (so F.F.Delta126bar is invariant); F Vec3 Delta* = 16.16.126 has no singlet",
    "genuine_dim10": "F* PhiVbar* S*^6 Phi17 / MPl^6 (F-PhiVbar mixing)",
    "mixing_mass_dim10_GeV": mix10, "angle_via_PhiVbar": theta10, "Gamma_GeV_dim10_route": Gamma10,
    "tau_s_dim10_route": GEV_S / Gamma10,
    "genuine_dim11_no_heavy_line": "F Vec3 Delta S^6 Phi17* / MPl^7 (nu^c channel, <Delta_R>=v_R)",
    "mixing_mass_dim11_GeV": mix11, "angle_dim11_nondegenerate": theta11, "tau_s_dim11_route": GEV_S / Gamma11,
    "age_of_universe_s": 4.35e17,
    "conclusion": "tau >> age of the universe: effectively a second STABLE superheavy relic (EST), not 1e15-1e16 s",
}

# ---- y_s cap (NUM, pure-Yukawa analytic + the researcher's gauge shift) -------------------------------------------
# 16 pi^2 dy/dt = 61 y^3 (sum d_i = 60 plus 1) -> 1/y(Ms)^2 = 1/y(L)^2 + 122/(16 pi^2) ln(L/Ms)
caps = {}
for ms in (1e13, 3e12):
    lnr = math.log(MPL / ms)
    for lim, name in ((math.sqrt(4 * math.pi), "sqrt(4pi)"), (1.0, "1"), (0.65, "0.65 (coupled-channel a0<=1/2, N-scaling)"),
                      (1.27, "1.27 (coupled-channel a0<=1/2, sqrtN-scaling)")):
        caps["M_s=%.0e y(MPl)<=%s" % (ms, name)] = 1 / math.sqrt(1 / lim ** 2 + 122 / L16 * lnr)
out["ys_cap_pure_yukawa"] = caps
out["ys_cap_note"] = ("gauge terms widen the cap by ~0.05 (researcher: 0.322 -> 0.374 least-gauged at M_s=1e13); "
                      "the cap moves by < 0.02 between y(MPl) <= sqrt(4 pi) and y(MPl) <= 1 (log-dominated)")

# ---- f_a and m_a (NUM) ---------------------------------------------------------------------------------------------
def fa_ma(sig, phi=1e17):
    vs, vp = math.sqrt(2) * sig, math.sqrt(2) * phi
    fa = vs * vp / math.sqrt(16 * vs ** 2 + 289 * vp ** 2)
    return fa, 5.70e-6 * 1e12 / fa * 1e6
out["axion"] = {"y_s=0.304 (<S>=3.29e13)": fa_ma(1e13 / 0.304), "y_s=0.374": fa_ma(1e13 / 0.374),
                "y_s=0.388": fa_ma(1e13 / 0.388), "M_s=3e12,y=0.35": fa_ma(3e12 / 0.35)}

(HERE / "verify_k0.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(json.dumps(out, indent=1, default=str))
