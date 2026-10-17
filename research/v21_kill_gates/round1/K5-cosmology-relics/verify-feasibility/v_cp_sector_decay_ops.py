"""Verifier check: lowest-dimension X-allowed, SO(10)-allowed operators that let the C = 16(-6)+16bar(10) and
P = 16(-9)+16bar(-8) sectors decay into R-even states (F(1), A(0), Abar(4), B(-3), Bbar(7)).
At the renormalizable level the couplings C.Cbar.S*, Cbar.Pbar.H, P.Pbar.Phi17 leave an accidental vectorlike
'CP-number' U(1) (one of K5's three free fermion-only directions): C:+1, Cbar:-1, P:-1, Pbar:+1, all else 0.
We enumerate scalar multisets (n <= 12 fields) with total X = -X(bilinear) and the right SO(10) tensor content,
and estimate the induced mixing mass m_mix = prod <phi> / M_P^(n-1) and a decay lifetime via mixing with a light
SM fermion, Gamma ~ theta^2 M^3/(8 pi v^2), theta = m_mix/M.
"""
import itertools, json
from fractions import Fraction as Fr

MP = 2.435e18
VEV = {"H": 174.0, "H*": 174.0, "D": 3e13, "D*": 3e13, "P210": 2.5e16, "S": 3e13, "S*": 3e13, "F17": 1e17, "F17*": 1e17}
X = {"H": -2, "H*": 2, "D": -2, "D*": 2, "P210": 0, "S": 4, "S*": -4, "F17": 17, "F17*": -17}
# tensor type needed: '16x16' needs a 10 (H,H*) or 126bar (D); '16bx16b' needs 10 or 126 (D*); '16x16b' needs none (P210 allowed)
TENS = {"H": {"16x16", "16bx16b"}, "H*": {"16x16", "16bx16b"}, "D": {"16x16"}, "D*": {"16bx16b"}, "P210": set(), "S": set(), "S*": set(), "F17": set(), "F17*": set()}
heavy = {"C": ("16", -6), "Cbar": ("16bar", 10), "P": ("16", -9), "Pbar": ("16bar", -8)}
light = {"F": ("16", 1), "A": ("16", 0), "Abar": ("16bar", 4), "B": ("16", -3), "Bbar": ("16bar", 7)}
MASS = {"C": 1e13, "Cbar": 1e13, "P": 1e17, "Pbar": 1e17}
OUT = r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\wfV21\K5-cosmology-relics\verify-feasibility\v_cp_sector_decay_ops.json"


def kind(r1, r2):
    if r1 == r2 == "16":
        return "16x16"
    if r1 == r2 == "16bar":
        return "16bx16b"
    return "16x16b"


results = []
names = list(VEV)
for h, (rh, xh) in heavy.items():
    for l, (rl, xl) in light.items():
        need = -(xh + xl)
        k = kind(rh, rl)
        best = None
        for n in range(0, 13):
            for combo in itertools.combinations_with_replacement(names, n):
                if sum(X[c] for c in combo) != need:
                    continue
                if k != "16x16b" and not any(k in TENS[c] for c in combo):
                    continue
                if k == "16x16b" and any(c in ("H", "H*", "D", "D*") for c in combo):
                    continue  # a lone 10/126 cannot couple 16 x 16bar; keep to singlets/210 (lowest order)
                mix = 1.0
                for c in combo:
                    mix *= VEV[c]
                mix /= MP ** max(n - 1, 0)
                if best is None or mix > best[1]:
                    best = (combo, mix, n)
            if best is not None:
                break
        if best is None:
            results.append(dict(bilinear=f"{h}.{l}", X_needed=need, note="no operator with <= 12 scalars"))
            continue
        combo, mix, n = best
        M = MASS[h]
        theta = mix / M
        Gam = theta ** 2 * M ** 3 / (8 * 3.14159 * 174.0 ** 2)
        tau = 6.582e-25 / Gam if Gam > 0 else float("inf")
        results.append(dict(bilinear=f"{h}.{l}", X_needed=need, operator=list(combo), n_scalars=n, dim=3 + n,
                            mixing_mass_GeV=mix, theta=theta, tau_s_via_SM_mixing=tau))
for r in results:
    print(json.dumps(r))
# the renormalizable couplings of the sector, for the record
print("renormalizable: C.Cbar.S* (X -6+10-4=0), Cbar.Pbar.H (10-8-2=0), P.Pbar.Phi17 (-9-8+17=0); accidental CP-number: C+1, Cbar-1, P-1, Pbar+1")
json.dump(results, open(OUT, "w"), indent=1)
