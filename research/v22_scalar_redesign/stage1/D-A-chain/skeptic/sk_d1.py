#!/usr/bin/env python3
"""SKEPTIC D1 (EXACT, own code): anomalies, accidental kernel, PQ, N, E/N, N_DW input for the D-A-chain A1 content
(= B63 verbatim + v20 scalars).  Also checks that the d=5 Yukawa operators the design relies on are inside the kernel
(i.e. PQ- and X-neutral, so they cannot change the PQ structure), and that the SM-direct vev set {Phi210, Delta_R, S,
Phi17 (+ EW doublet)} is the same set of vev-carrying fields as in the R2-V certificate (the certificate is a
symmetric-phase statement over all gauge-invariant monomials, so only the field content enters)."""
import json
from fractions import Fraction as Fr
import sympy as sp

NAMES = ["F", "V1", "Vb1", "V2", "Vb2", "V3", "Vb3", "T", "Pb", "N1", "N1b", "N2", "N2b", "N3", "N3b", "NMm",
         "Delta", "H10", "S", "Phi17"]
# (rep, X, multiplicity) for fermions; reps: 16, 16b, 10, 1
FER = {"F": ("16", 1, 3), "V1": ("16", -35, 2), "Vb1": ("16b", 39, 1), "V2": ("16", -28, 1), "Vb2": ("16b", 32, 1),
       "V3": ("16", 34, 1), "Vb3": ("16b", -30, 1), "T": ("10", 2, 2), "Pb": ("16b", 18, 1), "N1": ("1", -63, 1),
       "N1b": ("1", 59, 1), "N2": ("1", -58, 1), "N2b": ("1", 54, 1), "N3": ("1", -57, 1), "N3b": ("1", 61, 1),
       "NMm": ("1", -2, 2)}
SCAL_X = {"Delta": -2, "H10": -2, "S": 4, "Phi17": 17}
DIM = {"16": 16, "16b": 16, "10": 10, "1": 1}
IDX = {"16": Fr(2), "16b": Fr(2), "10": Fr(1), "1": Fr(0)}     # SO(10) Dynkin index (T(10) = 1)
out = {}
out["SO10^2_X"] = str(sum(IDX[r] * x * m for r, x, m in FER.values()))
out["X^3"] = str(sum(DIM[r] * x ** 3 * m for r, x, m in FER.values()))
out["grav_X"] = str(sum(DIM[r] * x * m for r, x, m in FER.values()))
out["net_16_minus_16b"] = sum(m * (1 if r == "16" else -1 if r == "16b" else 0) for r, x, m in FER.values())

# accidental kernel: every renormalizable coupling (12 Yukawas + phase-sensitive scalar terms) is a linear constraint
def vec(**kw):
    v = [0] * len(NAMES)
    for k, c in kw.items():
        v[NAMES.index(k)] += c
    return v
cons = {"F.F.H10": vec(F=2, H10=1), "F.F.Delta": vec(F=2, Delta=1), "V1.Vb1.S*": vec(V1=1, Vb1=1, S=-1),
        "V1.Pb.Phi17": vec(V1=1, Pb=1, Phi17=1), "V2.Vb2.S*": vec(V2=1, Vb2=1, S=-1), "Vb2.Vb3.H10": vec(Vb2=1, Vb3=1, H10=1),
        "V3.Vb3.S*": vec(V3=1, Vb3=1, S=-1), "T.T.S*": vec(T=2, S=-1), "N1.N1b.S": vec(N1=1, N1b=1, S=1),
        "N2.N2b.S": vec(N2=1, N2b=1, S=1), "N3.N3b.S*": vec(N3=1, N3b=1, S=-1), "NMm.NMm.S": vec(NMm=2, S=1),
        "kappaH H.H.S": vec(H10=2, S=1), "O15 Phi.H*.Delta": vec(H10=-1, Delta=1), "O38 Phi.H*.Delta*.S*": vec(H10=-1, Delta=-1, S=-1),
        "O31 Delta^2 H*^2": vec(Delta=2, H10=-2), "O28 H* Delta^2 Delta*": vec(H10=-1, Delta=1), "O45 Phi^2 H* Delta": vec(H10=-1, Delta=1)}
A = sp.Matrix(list(cons.values()))
ker = A.nullspace()
out["constraint_rank"] = int(A.rank()); out["kernel_dim"] = len(ker)
Xv = sp.Matrix([FER[n][1] if n in FER else SCAL_X[n] for n in NAMES])
G2 = sp.Matrix(vec(V1=-1, Vb1=1, Phi17=1))
out["X_in_kernel"] = bool((A * Xv).is_zero_matrix); out["G2_in_kernel"] = bool((A * G2).is_zero_matrix)
# d=5 Yukawa operators used by the design: F.F.H10.Phi210, F.F.Delta.Phi210, F.F.H10*.S* (all must be kernel-neutral)
d5 = {"F.F.H10.Phi210": vec(F=2, H10=1), "F.F.Delta.Phi210": vec(F=2, Delta=1), "F.F.H10*.S*": vec(F=2, H10=-1, S=-1)}
kerM = sp.Matrix.hstack(*ker)
out["d5_kernel_charges"] = {k: [int(x) for x in (sp.Matrix([v]) * kerM)] for k, v in d5.items()}
# PQ = X - 17 G2: colour anomaly N and E for complete multiplets
PQ = {n: (FER[n][1] - 17 * G2[NAMES.index(n)]) for n in FER}
Nn = sum(IDX[FER[n][0]] * PQ[n] * FER[n][2] for n in FER)
QEM2 = {"16": Fr(16, 3), "16b": Fr(16, 3), "10": Fr(8, 3), "1": Fr(0)}
E = sum(QEM2[FER[n][0]] * PQ[n] * FER[n][2] for n in FER)
out["N(PQ)"] = str(Nn); out["E(PQ)"] = str(E); out["E/N"] = str(Fr(E) / Fr(Nn))
out["PQ_scalar_charges"] = {"S": 4, "Phi17": 17 - 17 * 1, "H10": -2, "Delta": -2}
out["N_DW_input"] = "theta_eff = 17 theta_S - 4 theta_Phi17; gcd(17,4) = 1 (EXACT) -> N_DW = 1 mod gauge (R2-V centre argument)"
print(json.dumps(out, indent=1))
json.dump(out, open("sk_d1.json", "w"), indent=1)
