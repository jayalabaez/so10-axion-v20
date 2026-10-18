"""D-B-symmetry, variant V2 ('texture Z_n'): the only abelian-symmetry loophole of the diagnosis lemma 1c-ii.

The lemma (h = d forced) assumes F_i F_j H10 and F_i F_j Delta share at least one (i,j) entry.  A family-dependent Z_n with
NO shared entry allows delta = h - d != 0.  This script enumerates every such Z_n (n = 3..8) exactly and records:
  (1) the Yukawa supports A_H (F F H10) and A_D (F F Delta) and whether M_R (support A_D) and the charged mass matrices
      (support A_H u A_D) are generically non-singular (random complex entries, exact zero pattern);
  (2) whether the textures leave an extra continuous family/H-number U(1) (exact rational rank of the continuous charge
      constraints) - a D1 issue (extra accidental symmetry -> extra Goldstone / axion);
  (3) which phase-sensitive v20 scalar operators survive: O15 Phi H* D, O45 Phi^2 H* D, O28 H* D^2 D*, O31 H*^2 D^2,
      kappaH H H S, O38 Phi H* D* S*  (Phi real: 2q = 0; the S charge sigma is free and chosen to keep kappaH or O38).
EXACT statement checked for every admissible case: O31 forbidden  =>  O15, O45, O28 forbidden  =>  the H10 and Sigma
bidoublets mix only through O38 (~ lambda38 <S> <Phi>) or not at all.
Writes v2_textures.json.
"""
from __future__ import annotations
import itertools, json
from fractions import Fraction as Fr
from pathlib import Path
import numpy as np
import sympy as sp

HERE = Path(__file__).resolve().parent
PAIRS = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]


def generic_det(support, rng):
    M = np.zeros((3, 3), complex)
    for (i, j) in support:
        z = rng.normal() + 1j * rng.normal(); M[i, j] = z; M[j, i] = z
    return abs(np.linalg.det(M))


def cont_kernel_dim(AH, AD):
    # unknowns phi1, phi2, phi3, h, d ; constraints phi_i + phi_j + h = 0 on AH, phi_i + phi_j + d = 0 on AD
    rows = []
    for (i, j) in AH:
        r = [0] * 5; r[i] += 1; r[j] += 1; r[3] = 1; rows.append(r)
    for (i, j) in AD:
        r = [0] * 5; r[i] += 1; r[j] += 1; r[4] = 1; rows.append(r)
    M = sp.Matrix(rows) if rows else sp.zeros(1, 5)
    ns = M.nullspace()
    # does the continuous kernel force h = d ?
    forces_h_eq_d = all(v[3] == v[4] for v in ns)
    return len(ns), forces_h_eq_d


def main():
    rng = np.random.default_rng(5)
    cases = []
    seen = set()
    for n in range(3, 9):
        qs = [0] + ([n // 2] if n % 2 == 0 else [])
        for f in itertools.product(range(n), repeat=3):
            if f[0] != 0:
                continue                      # overall shift f_i -> f_i + k, h,d -> h,d - 2k removes one charge
            for h in range(n):
                for d in range(n):
                    delta = (h - d) % n
                    if (2 * delta) % n == 0:
                        continue              # O31 allowed -> not a solution of the task
                    AH = [p for p in PAIRS if (f[p[0]] + f[p[1]] + h) % n == 0]
                    AD = [p for p in PAIRS if (f[p[0]] + f[p[1]] + d) % n == 0]
                    if not AH or not AD:
                        continue
                    dR = generic_det(AD, rng)
                    dM = generic_det(AH + AD, rng)
                    if dR < 1e-12 or dM < 1e-12:
                        continue              # singular M_R or massless charged fermion
                    key = (tuple(sorted(AH)), tuple(sorted(AD)))
                    # family permutations
                    canon = None
                    for perm in itertools.permutations(range(3)):
                        mp = lambda p: tuple(sorted((perm[p[0]], perm[p[1]])))
                        k2 = (tuple(sorted(mp(p) for p in AH)), tuple(sorted(mp(p) for p in AD)))
                        canon = k2 if canon is None or k2 < canon else canon
                    kdim, heqd = cont_kernel_dim(AH, AD)
                    ops = {}
                    for q in qs:
                        o = {"O15 Phi H* D": (-h + d + q) % n == 0, "O45 Phi^2 H* D": (-h + d) % n == 0,
                             "O28 H* D^2 D*": (-h + d) % n == 0, "O31 H*^2 D^2": (2 * (d - h)) % n == 0}
                        # sigma chosen to allow kappaH (2h + sigma = 0) or O38 (-h - d - sigma + q = 0); both?
                        both = ((-h - d + q) - (-2 * h)) % n == 0
                        o["kappaH and O38 both allowable"] = both
                        ops[f"q={q}"] = o
                    rec = {"n": n, "f": f, "h": h, "d": d, "delta": delta, "A_H": AH, "A_D": AD,
                           "canonical": [list(map(list, canon[0])), list(map(list, canon[1]))],
                           "cont_kernel_dim": kdim, "cont_kernel_forces_h_eq_d": heqd, "ops": ops}
                    cases.append(rec)
                    seen.add(json.dumps(rec["canonical"]))
    # EXACT checks over all cases
    all_O15_forbidden = all(not v["O15 Phi H* D"] for c in cases for v in c["ops"].values())
    all_O28_O45_forbidden = all(not v["O28 H* D^2 D*"] and not v["O45 Phi^2 H* D"] for c in cases for v in c["ops"].values())
    never_both = all(not v["kappaH and O38 both allowable"] for c in cases for v in c["ops"].values())
    extra_u1 = [c for c in cases if not c["cont_kernel_forces_h_eq_d"]]
    out = {"n_cases": len(cases), "n_texture_classes_mod_family_permutations": len(seen),
           "EXACT_O31_forbidden_implies_O15_forbidden": all_O15_forbidden,
           "EXACT_O31_forbidden_implies_O28_O45_forbidden": all_O28_O45_forbidden,
           "EXACT_kappaH_and_O38_never_both": never_both,
           "n_cases_with_extra_continuous_U1_(h!=d_allowed_continuously)": len(extra_u1),
           "texture_classes": sorted(seen),
           "max_entries_AH_plus_AD": max(len(c["A_H"]) + len(c["A_D"]) for c in cases) if cases else 0,
           "examples": cases[:6]}
    (HERE / "v2_textures.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k not in ("examples", "texture_classes")}, indent=1))
    for t in sorted(seen):
        print("  class:", t)


if __name__ == "__main__":
    main()
