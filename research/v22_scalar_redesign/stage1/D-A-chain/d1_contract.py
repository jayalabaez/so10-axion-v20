#!/usr/bin/env python3
"""D1 contract arithmetic (EXACT, Fractions) for the D-A-chain designs.

Fermions (Weyl, B63, unchanged in every D-A-chain variant): rep, X, multiplicity, G2 (accidental, round-1 basis).
Scalars do not enter gauge anomalies; a scalar addition can change the accidental-symmetry kernel / PQ / N_DW only through
new phase-sensitive couplings, which is checked separately (kernel rank) for every variant.
Outputs: [SO(10)]^2 X, X^3, grav-X; N = sum PQ T_SU(3), E = sum PQ Q_em^2 (complete SO(10) multiplets), E/N;
PQ = X - 17 G2; N_DW argument inputs (gcd(4, 17) = 1)."""
import json
from fractions import Fraction as Fr
from math import gcd

# (name, rep, X, mult, G2)
FERM = [("F", "16", 1, 3, 0), ("V1", "16", -35, 2, -1), ("Vb1", "16b", 39, 1, 1), ("V2", "16", -28, 1, 0),
        ("Vb2", "16b", 32, 1, 0), ("V3", "16", 34, 1, 0), ("Vb3", "16b", -30, 1, 0), ("T", "10", 2, 2, 0),
        ("Pb", "16b", 18, 1, 0), ("N1", "1", -63, 1, 0), ("N1b", "1", 59, 1, 0), ("N2", "1", -58, 1, 0),
        ("N2b", "1", 54, 1, 0), ("N3", "1", -57, 1, 0), ("N3b", "1", 61, 1, 0), ("NMm", "1", -2, 2, 0)]
DIM = {"16": 16, "16b": 16, "10": 10, "1": 1}
TIDX = {"16": Fr(2), "16b": Fr(2), "10": Fr(1), "1": Fr(0)}          # SO(10) index, T(10) = 1 (= SU(3) index of the rep)
# sum of Q_em^2 over a complete multiplet: 16 -> 16/3, 10 -> 8/3 (so E/N = 8/3 for complete multiplets)
QEM2 = {"16": Fr(16, 3), "16b": Fr(16, 3), "10": Fr(8, 3), "1": Fr(0)}

out = {}
a_so10x = sum(TIDX[r] * x * m for _, r, x, m, _ in FERM)
a_x3 = sum(DIM[r] * x ** 3 * m for _, r, x, m, _ in FERM)
a_grav = sum(DIM[r] * x * m for _, r, x, m, _ in FERM)
out["anomaly_SO10^2_X"] = str(a_so10x); out["anomaly_X^3"] = str(a_x3); out["anomaly_grav_X"] = str(a_grav)
N_X = sum(TIDX[r] * x * m for _, r, x, m, _ in FERM)
N_G2 = sum(TIDX[r] * g * m for _, r, x, m, g in FERM)
pq = {n: x - 17 * g for n, r, x, m, g in FERM}
N = sum(TIDX[r] * pq[n] * m for n, r, x, m, g in FERM)
E = sum(QEM2[r] * pq[n] * m for n, r, x, m, g in FERM)
out.update({"N(X)": str(N_X), "N(G2)": str(N_G2), "N(PQ=X-17G2)": str(N), "E": str(E), "E/N": str(Fr(E) / N),
            "N_DW_input": "theta_eff = 17 theta_S - 4 theta_Phi17 (X-invariant); gcd(4,17) = %d -> N_DW = 1 mod gauge" % gcd(4, 17)})
net16 = sum(m * (1 if r == "16" else -1 if r == "16b" else 0) for _, r, x, m, _ in FERM)
out["net_16_minus_16bar"] = net16
ok = (a_so10x == 0 and a_x3 == 0 and a_grav == 0 and N == 34 and Fr(E) / N == Fr(8, 3) and net16 == 3)
out["all_ok"] = ok
print(json.dumps(out, indent=1))
json.dump(out, open("d1_contract.json", "w"), indent=1)
