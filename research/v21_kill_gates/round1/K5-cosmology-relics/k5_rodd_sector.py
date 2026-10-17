"""K5 part (1a): the R-odd (tensor-fermion) sector of v21-F17-G3221.

Exact (rational) bookkeeping, no numerics:
  * SO(10) x U(1)_X charge table of the F17 fermions and v20 scalars;
  * every X-allowed renormalizable Yukawa coupling (SO(10) product rules + X sum = 0);
  * the exact parity R = z^2 (-1)^{2s} (z^2 = centre element of Spin(10): -1 on spinors, +1 on tensors);
  * anomalies [SO(10)]^2 X, grav-X, X^3 (sanity reproduction of FINAL J1a);
  * the accidental PQ: general U(1) solution of all Yukawa + scalar-potential phase constraints,
    QCD anomaly N on the solution space, the gauge-invariant axion phase theta = 17 th_S - 4 th_Phi,
    f_a = v_S/17 (v_Phi -> infinity), N_DW = 1;
  * G3221 and SM decomposition of the 10_F (what the stable state can be).
Writes k5_rodd_sector.json.
"""
from __future__ import annotations
import json, itertools
from fractions import Fraction as Fr
import sympy as sp

OUT = r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\wfV21\K5-cosmology-relics\k5_rodd_sector.json"

# ---------------- SO(10) data (Dynkin index T with T(fund SU(3)) = 1/2 convention for the QCD anomaly) ----------
# dim, SU(3) index of the SO(10) rep (QCD anomaly weight), spinorial?
REP = {
    "1":     dict(dim=1,   T3=Fr(0), spinor=False),
    "10":    dict(dim=10,  T3=Fr(1), spinor=False),   # 10 -> 3 + 3bar + 4x1 : T3 = 1/2+1/2
    "16":    dict(dim=16,  T3=Fr(2), spinor=True),    # 16 -> 2x3 + 3bar + 3bar + 4x1 : T3 = 4 x 1/2
    "16bar": dict(dim=16,  T3=Fr(2), spinor=True),
    "126bar":dict(dim=126, T3=None,  spinor=False),
    "210":   dict(dim=210, T3=None,  spinor=False),
}
CONJ = {"1": "1", "10": "10", "16": "16bar", "16bar": "16", "126bar": "126", "126": "126bar", "210": "210"}

# singlets in products of two fermion reps with one scalar rep: does (R1 x R2 x R3) contain a singlet?
# R1 x R2 decompositions (only the pieces that can meet a scalar of the model):
PROD = {
    ("1", "1"):      {"1"},
    ("1", "10"):     {"10"},
    ("1", "16"):     {"16"},
    ("1", "16bar"):  {"16bar"},
    ("10", "10"):    {"1", "45", "54"},
    ("10", "16"):    {"16bar", "144bar"},
    ("10", "16bar"): {"16", "144"},
    ("16", "16"):    {"10", "120", "126"},
    ("16bar", "16bar"): {"10", "120", "126bar"},
    ("16", "16bar"): {"1", "45", "210"},
}
def prod(r1, r2):
    key = (r1, r2) if (r1, r2) in PROD else (r2, r1)
    return PROD[key]

# ---------------- fields ----------------
# Weyl fermions (left-handed), name -> (SO(10) rep, X)
FERMIONS = {
    "F1": ("16", 1), "F2": ("16", 1), "F3": ("16", 1),          # SM families
    "T1": ("10", -1), "T2": ("10", 5),                          # tensor pair (S-sector)
    "A": ("16", 0), "Abar": ("16bar", 4),
    "B": ("16", -3), "Bbar": ("16bar", 7),
    "C": ("16", -6), "Cbar": ("16bar", 10),
    "N3a": ("1", -3), "N1a": ("1", -1), "N3b": ("1", -3), "N1b": ("1", -1),   # 2 x [1(-3)+1(-1)]
    "P": ("16", -9), "Pbar": ("16bar", -8),                      # Phi-sector pair
}
# scalars: name -> (rep, X, real?)
SCALARS = {
    "Phi210": ("210", 0, True),
    "Delta": ("126bar", -2, False),
    "H": ("10", -2, False),
    "S": ("1", 4, False),
    "Phi17": ("1", 17, False),
}

def scalar_forms():
    """Each scalar as itself and (if complex) its conjugate: (label, rep, X)."""
    out = []
    for n, (r, x, real) in SCALARS.items():
        out.append((n, r, x))
        if not real:
            out.append((n + "*", CONJ[r], -x))
    return out

# ---------------- 1. allowed renormalizable Yukawa couplings ----------------
couplings = []
names = list(FERMIONS)
for i, j in itertools.combinations_with_replacement(range(len(names)), 2):
    f1, f2 = names[i], names[j]
    r1, x1 = FERMIONS[f1]; r2, x2 = FERMIONS[f2]
    for (sl, sr, sx) in scalar_forms():
        if x1 + x2 + sx != 0:
            continue
        # singlet in r1 x r2 x sr  <=>  conj(sr) in r1 x r2
        if CONJ.get(sr, None) in prod(r1, r2) or (sr == "1" and "1" in prod(r1, r2)):
            # symmetric-product subtlety: 10 x 10 -> 1 is symmetric, 16 x 16 -> 10,126 symmetric, 120 antisym.
            # For f1 == f2 with a 10 or 126bar scalar: 16.16.H and 16.16.Delta symmetric -> allowed; fine.
            couplings.append((f1, f2, sl))
# group: identical-family copies (F1,F2,F3) and (N3a,N3b),(N1a,N1b) are flavour matrices; list distinct structures
def canon(f):
    return {"F1": "F", "F2": "F", "F3": "F", "N3a": "N3", "N3b": "N3", "N1a": "N1", "N1b": "N1"}.get(f, f)
structures = sorted({(canon(a), canon(b), s) for a, b, s in couplings})

# ---------------- 2. R-parity ----------------
def R_parity(rep, is_fermion):
    z2 = -1 if REP[rep]["spinor"] else +1
    return z2 * (-1 if is_fermion else +1)
R = {f: R_parity(r, True) for f, (r, x) in FERMIONS.items()}
R_s = {s: R_parity(r, False) for s, (r, x, _) in SCALARS.items()}
r_odd = sorted(f for f in R if R[f] == -1)
# every allowed coupling must be R-even (check):
r_check = all(R[a] * R[b] * R_s[s.rstrip("*")] == +1 for a, b, s in couplings)

# ---------------- 3. gauge anomalies ----------------
def dimT(rep):
    return REP[rep]["dim"], REP[rep]["T3"]
A_SO10_X = sum(FERMIONS[f][1] * REP[FERMIONS[f][0]]["T3"] for f in FERMIONS)     # [SU(3)]^2 X  (SO(10)^2 X up to normalisation)
A_grav_X = sum(FERMIONS[f][1] * REP[FERMIONS[f][0]]["dim"] for f in FERMIONS)
A_X3 = sum(FERMIONS[f][1] ** 3 * REP[FERMIONS[f][0]]["dim"] for f in FERMIONS)
T_S = sum(REP[FERMIONS[f][0]]["T3"] for f in ("T1", "T2", "A", "Abar", "B", "Bbar", "C", "Cbar"))
T_Phi = sum(REP[FERMIONS[f][0]]["T3"] for f in ("P", "Pbar"))

# ---------------- 4. accidental PQ, anomaly N, f_a, N_DW ----------------
# unknown phase charges q_f for fermions, q_s for scalars (Phi210 real -> 0).
qf = {f: sp.Symbol("q_" + f) for f in FERMIONS}
qs = {s: sp.Symbol("q_" + s) for s in SCALARS}
eqs = [qs["Phi210"]]
# scalar potential phase constraints (renormalizable, X-neutral, SO(10)-invariant monomials involving phases):
#   S H H          (10x10 -> 1; X: 4-2-2 = 0)      -> q_S + 2 q_H = 0
#   H Delta^* Phi210  (10 x 126 x 210 -> 1; X: -2+2+0) -> q_H - q_Delta = 0
#   H H Delta^* Delta^* (X: -4+4) same constraint; Delta Delta^* etc neutral
eqs += [qs["S"] + 2 * qs["H"], qs["H"] - qs["Delta"]]
# Yukawa constraints
def scharge(label):
    base = label.rstrip("*")
    return -qs[base] if label.endswith("*") else qs[base]
for a, b, s in couplings:
    eqs.append(qf[a] + qf[b] + scharge(s))
# normalisation: PQ defined as the rotation of S by 1 with Phi17 fixed (the gauge-invariant choice modulo X)
unknowns = list(qf.values()) + list(qs.values())
sol = sp.solve(eqs + [qs["S"] - 1, qs["Phi17"]], unknowns, dict=True)
assert len(sol) == 1
sol = sol[0]
free = sorted({s for v in sol.values() for s in v.free_symbols} | {u for u in unknowns if u not in sol}, key=str)
N_expr = sp.expand(sum(sol.get(qf[f], qf[f]) * REP[FERMIONS[f][0]]["T3"] for f in FERMIONS))
# QCD anomaly of the free (fermion-only) directions:
N_free = {str(s): sp.diff(N_expr, s) for s in free}
N_S = N_expr.subs({s: 0 for s in free})
# also the rotation of Phi17 alone (Phi-sector fermions compensating):
N_Phi_rot = sum(sp.Rational(-1, 2) * REP[FERMIONS[f][0]]["T3"] for f in ("P", "Pbar"))
# theta_QCD shift per unit rotation gamma of S (Fujikawa: 2 N gamma) versus the shift of the gauge-invariant phase
# vartheta = 17 th_S - 4 th_Phi (17 gamma): ratio = 2 N_S / 17.
ratio = sp.nsimplify(2 * N_S / 17)
# E/N: electromagnetic anomaly E = sum q * dim * Q^2 over SM content of the 16 and tensor reps.
# SM content of 16: Q(3,2,1/6): Q^2 sum = 3*(4/9+1/9) = 5/3 ; u^c: 3*4/9 = 4/3 ; d^c: 3*1/9 = 1/3 ; L: 1 ; e^c: 1 ; nu^c: 0
Q2_16 = Fr(5, 3) + Fr(4, 3) + Fr(1, 3) + 1 + 1
Q2_10 = 2 * Fr(1, 9) * 3 + 2 * 1      # 10: (3,1,-1/3)+(3bar,1,1/3): 6 x 1/9 ; (1,2,1/2)+(1,2,-1/2): 2 charged
Q2 = {"16": Q2_16, "16bar": Q2_16, "10": Q2_10, "1": Fr(0)}
E_expr = sp.expand(sum(sol.get(qf[f], qf[f]) * Q2[FERMIONS[f][0]] for f in FERMIONS))
E_S = E_expr.subs({s: 0 for s in free})
E_over_N = sp.nsimplify(E_S / N_S)

# ---------------- 5. decomposition of the 10 under G3221 and the SM ----------------
decomp_10 = {
    "G3221 (SU3,SU2L,SU2R)_{B-L}": ["(1,2,2)_0", "(3,1,1)_{-2/3}", "(3bar,1,1)_{+2/3}"],
    "SM (SU3,SU2)_Y, Y = T3R + (B-L)/2": ["(1,2)_{+1/2}", "(1,2)_{-1/2}", "(3,1)_{-1/3}", "(3bar,1)_{+1/3}"],
    "electric charges": {"(1,2)_{+1/2}": ["+1", "0"], "(1,2)_{-1/2}": ["0", "-1"], "(3,1)_{-1/3}": ["-1/3 (colour triplet)"], "(3bar,1)_{+1/3}": ["+1/3 (colour antitriplet)"]},
    "Dirac pairing": "T1 = 10(-1) and T2 = 10(5) pair into 10 Dirac fermions with the common mass M_10 = y_10 <S> from T1.T2.S*",
}

out = dict(
    fermions=FERMIONS, scalars=SCALARS,
    allowed_renormalizable_yukawa_structures=[f"{a}.{b}.{s}" for a, b, s in structures],
    n_structures=len(structures),
    R_parity_fermions=R, R_parity_scalars=R_s, R_odd_fermions=r_odd,
    all_couplings_R_even=r_check,
    anomalies=dict(SU3sq_X=str(A_SO10_X), grav_X=str(A_grav_X), X3=str(A_X3), T_S=str(T_S), T_Phi=str(T_Phi)),
    PQ=dict(
        normalisation="S -> e^{i gamma} S, Phi17 fixed, Phi210 fixed; scalar charges q_H = q_Delta = -1/2 from S.H.H and H.Delta*.Phi210",
        free_fermion_only_directions=[str(s) for s in free],
        QCD_anomaly_of_free_directions={k: str(v) for k, v in N_free.items()},
        N_S_charge1=str(N_S), N_for_S_charge_4=str(4 * N_S), N_Phi_rotation=str(N_Phi_rot),
        theta_shift_over_vartheta_shift=str(ratio),
        gauge_invariant_phase="vartheta = 17 theta_S - 4 theta_Phi17 (invariant under X: 4*17 - 17*4 = 0); theta_QCD = +-vartheta + const",
        f_a="v_S/17 x [1 + O((4 v_S/17 v_Phi)^2)] with v_S = sqrt2 <S>; exact: v_S v_Phi/sqrt((4v_S)^2+(17v_Phi)^2)",
        N_DW=1 if ratio in (1, -1) else str(ratio),
        E_over_N=str(E_over_N),
    ),
    decomposition_10=decomp_10,
    scalar_charges_solution={k: str(sol.get(v, v)) for k, v in qs.items()},
    fermion_charges_solution={k: str(sol.get(v, v)) for k, v in qf.items()},
)
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=1, default=str)
print(json.dumps({k: out[k] for k in ("allowed_renormalizable_yukawa_structures", "n_structures", "R_odd_fermions", "all_couplings_R_even", "anomalies", "PQ")}, indent=1, default=str))
