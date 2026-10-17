"""SO(10) gauge-boson masses from a G3221 vacuum of the 210 = Lambda^4(R^10), vevs p (1,1,1) and a (15,1,1), omega = 0.

p  ~ e7^e8^e9^e10 (SO(6) x SO(4) singlet, D-odd),  a ~ (e1234 + e1256 + e3456)/sqrt3 = J^J/|J^J| with J = e12+e34+e56
(the SU(3) x U(1)_{B-L} singlet in the 15 of SO(6)).  Generators L_ij act as derivations on 4-forms.
M^2_{AB} = g^2 (L_A Phi).(L_B Phi) for canonically normalised real components.  Eigenvalues are grouped by
generator type: (6,2,2) = L_{i m}, i in 1..6, m in 7..10;  SU(4)/U(3) coset (3,1,1)+(3bar,1,1) = the so(6) generators
anti-commuting with J;  the G3221 generators must have zero mass.  Reports M_{(3,1,1)}/M_{(6,2,2)} as a function of p/a.
"""
from __future__ import annotations
import itertools, sys, json
import numpy as np

n = 10
basis = list(itertools.combinations(range(n), 4))
index = {b: k for k, b in enumerate(basis)}
D = len(basis)
assert D == 210


def wedge_vec(indices, coeff, vec):
    """add coeff * e_{i1}^e_{i2}^e_{i3}^e_{i4} (indices possibly unsorted / repeated) to vec."""
    if len(set(indices)) < 4:
        return
    perm = np.argsort(indices)
    sign = np.linalg.det(np.eye(4)[perm])
    vec[index[tuple(sorted(indices))]] += coeff * sign


def generator(i, j):
    """Matrix of L_ij on Lambda^4: L_ij e_i = e_j, L_ij e_j = -e_i, derivation."""
    L = np.zeros((D, D))
    for k, b in enumerate(basis):
        col = np.zeros(D)
        for pos, idx in enumerate(b):
            if idx == i:
                new = list(b); new[pos] = j
                wedge_vec(new, 1.0, col)
            elif idx == j:
                new = list(b); new[pos] = i
                wedge_vec(new, -1.0, col)
        L[:, k] = col
    return L


gens = {(i, j): generator(i, j) for i in range(n) for j in range(i + 1, n)}
# vacuum directions (unit vectors)
p_dir = np.zeros(D); wedge_vec((6, 7, 8, 9), 1.0, p_dir)
a_dir = np.zeros(D)
for t in ((0, 1, 2, 3), (0, 1, 4, 5), (2, 3, 4, 5)):
    wedge_vec(t, 1 / np.sqrt(3), a_dir)
# complex structure J on R^6: pairs (0,1),(2,3),(4,5).  so(6) generators commuting with J: L_{2k,2k+1}, L_{2k,2l}+L_{2k+1,2l+1}, L_{2k,2l+1}-L_{2k+1,2l}
# coset (3+3bar): L_{2k,2l}-L_{2k+1,2l+1}, L_{2k,2l+1}+L_{2k+1,2l}
def L(i, j):
    return gens[(i, j)] if i < j else -gens[(j, i)]

coset_su4 = []
u3 = []
for k in range(3):
    u3.append(L(2 * k, 2 * k + 1))
    for l in range(k + 1, 3):
        u3.append((L(2 * k, 2 * l) + L(2 * k + 1, 2 * l + 1)) / np.sqrt(2))
        u3.append((L(2 * k, 2 * l + 1) - L(2 * k + 1, 2 * l)) / np.sqrt(2))
        coset_su4.append((L(2 * k, 2 * l) - L(2 * k + 1, 2 * l + 1)) / np.sqrt(2))
        coset_su4.append((L(2 * k, 2 * l + 1) + L(2 * k + 1, 2 * l)) / np.sqrt(2))
so4 = [L(i, j) for i in range(6, 10) for j in range(i + 1, 10)]
c622 = [L(i, m) for i in range(6) for m in range(6, 10)]
assert len(u3) == 9 and len(coset_su4) == 6 and len(so4) == 6 and len(c622) == 24


def masses(p, a):
    Phi = p * p_dir + a * a_dir
    out = {}
    for name, G in (("G3221 (u3+so4)", u3 + so4), ("(3,1,1)+(3bar,1,1)", coset_su4), ("(6,2,2)", c622)):
        vals = [float((g @ Phi) @ (g @ Phi)) for g in G]
        out[name] = (min(vals), max(vals))
    return out


print("unit checks: |p_dir|=", np.linalg.norm(p_dir), "|a_dir|=", np.linalg.norm(a_dir))
print("p only (a=0):", masses(1.0, 0.0))
print("a only (p=0):", masses(0.0, 1.0))
rows = []
for r in (0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0):
    m = masses(r, 1.0)     # p/a = r
    m311 = m["(3,1,1)+(3bar,1,1)"][0]; m622 = m["(6,2,2)"][0]
    rows.append(dict(p_over_a=r, M2_311=m311, M2_622=m622, ratio_M311_over_M622=np.sqrt(m311 / m622) if m622 > 0 else None, G3221_max=m["G3221 (u3+so4)"][1]))
    print(f"p/a={r:5.2f}: M^2(3,1,1)={m311:.4f}  M^2(6,2,2)={m622:.4f}  M311/M622={rows[-1]['ratio_M311_over_M622']}, G3221 residual {m['G3221 (u3+so4)'][1]:.1e}")
# critical p/a where M311/M622 = 1.37 (ordering flip, from verify_splitting)
with open(sys.argv[1] if len(sys.argv) > 1 else "verify_gauge_masses_210.json", "w", encoding="utf-8") as fh:
    json.dump(rows, fh, indent=1, default=float)
