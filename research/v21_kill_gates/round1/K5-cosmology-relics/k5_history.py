"""K5 assembly: consistent cosmological history of v21-F17-G3221 and the (H_I, T_RH, theta_i) windows.

Reads k5_rodd_sector.json, k5_splitting.json, k5_axion.json, k5_relic_reheating.json.
Adds exact homotopy checks (monopoles/strings of the two breaking steps), the inflaton-branching bound for direct
R-odd production, and the leptogenesis compatibility windows.  Writes k5_history.json.
"""
from __future__ import annotations
import json, itertools
from fractions import Fraction as Fr
import numpy as np

D = r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\wfV21\K5-cosmology-relics\\"
J = lambda n: json.load(open(D + n, encoding="utf-8"))
rodd, split, axion, relic = J("k5_rodd_sector.json"), J("k5_splitting.json"), J("k5_axion.json"), J("k5_relic_reheating.json")
MP = 2.435e18

# ---------------- exact homotopy bookkeeping (G3221 -> SM step) ----------------
# fields of the model under G3221 with (T3R values, B-L):  check (a) minimal period of the U(1)_Y loop,
# (b) its winding in U(1)_{B-L} (degree d), (c) whether z^2 = (-1)^{3(B-L)} lies in the connected SM subgroup.
G3221_fields = {  # name: (SU3 rep, SU2L dim, SU2R dim, B-L)
    "Q": ("3", 2, 1, Fr(1, 3)), "Qc": ("3bar", 1, 2, Fr(-1, 3)), "L": ("1", 2, 1, Fr(-1)), "Lc": ("1", 1, 2, Fr(1)),
    "10:(1,2,2)": ("1", 2, 2, Fr(0)), "10:(3,1,1)": ("3", 1, 1, Fr(-2, 3)), "10:(3bar,1,1)": ("3bar", 1, 1, Fr(2, 3)),
    "DeltaR:(1,1,3)": ("1", 1, 3, Fr(2)), "DeltaR:(3bar,1,3)": ("3bar", 1, 3, Fr(2, 3)), "DeltaR:(6bar,1,3)": ("6bar", 1, 3, Fr(-2, 3)),
    "45:(6,2,2)": ("3", 2, 2, Fr(-2, 3)),
}
def t3_values(dim):
    return [Fr(dim - 1, 2) - i for i in range(dim)]
# (a) minimal phi with exp(i phi Y) = 1 on all states: Y = T3R + (B-L)/2 ; phi = 2 pi m, need m*Y integer for all
Ys = set()
for name, (c, dL, dR, bl) in G3221_fields.items():
    for t3 in t3_values(dR):
        Ys.add(t3 + bl / 2)
m_Y = 1
while not all((m_Y * y).denominator == 1 for y in Ys):
    m_Y += 1
# (b) minimal period of U(1)_{B-L}: exp(i psi (B-L)) = 1 ; psi = 2 pi m_BL
BLs = {bl for (_, _, _, bl) in G3221_fields.values()}
m_BL = 1
while not all((m_BL * b).denominator == 1 for b in BLs):
    m_BL += 1
# the Y-loop phi in [0, 2 pi m_Y] projects to psi = phi/2 in [0, pi m_Y] -> winding d = (pi m_Y)/(2 pi m_BL) = m_Y/(2 m_BL)
d = Fr(m_Y, 2 * m_BL)
# (c) z^2 = (-1)^{3(B-L)} acts as -1 on the 16 and +1 on the 10: is it in SU(3)xSU(2)_LxU(1)_Y ?
# elements: c3 = e^{2 pi i k/3} (centre), c2 = (-1)^l, e^{2 pi i m Y} (m integer, since Y-phases must be a loop ... but
# general U(1)_Y elements e^{i phi Y} with any phi are allowed): require c3^{n3} c2^{n2} e^{i phi Y} = z^2 on all SM reps.
SM_reps = {  # (triality, SU2L doublet?, Y, z2)
    "Q": (1, 1, Fr(1, 6), -1), "uc": (-1, 0, Fr(-2, 3), -1), "dc": (-1, 0, Fr(1, 3), -1), "L": (0, 1, Fr(-1, 2), -1), "ec": (0, 0, Fr(1), -1), "nuc": (0, 0, Fr(0), -1),
    "10:D": (0, 1, Fr(1, 2), 1), "10:Dbar": (0, 1, Fr(-1, 2), 1), "10:T": (1, 0, Fr(-1, 3), 1), "10:Tbar": (-1, 0, Fr(1, 3), 1),
}
z2_in_SM = False
for k3 in range(3):
    for l2 in range(2):
        # phases: e^{i phi Y} with phi/(2 pi) = x rational candidate: need 2 pi k3 n/3 + pi l2 doublet + phi Y = pi (1 - z2)/2 mod 2 pi
        # solve for phi from nuc (Y=0): requires z2=+1 on nuc -> fails since z2(nuc) = -1 and nuc is a singlet: no phase can act.
        ok = True
        for name, (tri, dbl, Y, z2) in SM_reps.items():
            if Y == 0 and tri == 0 and dbl == 0 and z2 == -1:
                ok = False
        if ok:
            z2_in_SM = True
homotopy = dict(
    SO10_to_G3221="pi_2(SO(10)/G3221) = pi_1(G3221) = Z (one U(1)): GUT monopoles, mass ~ M_U/alpha_U ~ 1e18 GeV; must be inflated away",
    Y_loop_minimal_period_in_2pi=m_Y, BL_loop_minimal_period_in_2pi=m_BL, degree_of_Y_loop_in_BL=str(d),
    G3221_to_SM_monopoles="pi_2(G3221/H) = ker(pi_1(H)->pi_1(G3221)) = ker(Z -> Z, degree %s) = 0 : NO monopoles at v_R" % d,
    z2_in_connected_SM_subgroup=z2_in_SM,
    G3221_to_SM_strings="H = G_SM x Z_2 with Z_2 = z^2 = (-1)^{3(B-L)} (not in the connected G_SM: it acts as -1 on the SM-singlet nu^c); pi_0(H) = Z_2 -> Z_2 (Kibble-Lazarides-Shafi) strings at v_R; formed only if the transition happens after inflation",
    U1X_breaking="Phi17 (X=17) breaks U(1)_X -> Z_17 (gauge): local strings, pi_1(U(1)/Z_17) = Z; no walls (Z_17 is gauged). S (X=4, gcd(4,17)=1) breaks Z_17 and U(1)_PQ: axion; pure gauge string winding (n_S,n_Phi) = (4,17) carries no axion winding; S-only (1,0) string carries axion winding 17 (17 walls); (1,4) string carries axion winding 1 (one wall, N_DW=1). All irrelevant if the vevs are never restored after inflation.",
)

# ---------------- windows ----------------
th = relic["thresholds"]
def get(M, HI, crit):
    for r in th:
        if r["M"] == M and r["HI"] == HI and r["criterion"] == crit:
            return r["TRH_max"]
    return None
windows = []
for M in (3e12, 1e13):
    for HI in (1e5, 1e6, 1e7, 3e7, 1e9, 1e11, 1e13):
        t_dm = get(M, HI, "Omega_X = Omega_DM")
        t_neg = get(M, HI, "Omega_X = 1e-3 Omega_DM")
        t_iso = get(M, HI, "n_X/n_B = 1e-10")
        windows.append(dict(M=M, HI=HI, TRH_max_Omega_DM=t_dm, TRH_max_1em3_DM=t_neg, TRH_max_nX_nB_1em10=t_iso,
                            isocurvature_ok=(HI <= 3.2e7), isocurvature_ok_conservative=(HI <= 1.6e7),
                            thermal_leptogenesis_1e9_ok=(t_dm is not None and t_dm >= 1e9),
                            thermal_leptogenesis_1e10_ok=(t_dm is not None and t_dm >= 1e10),
                            HI_above_H_TRH=(HI >= np.sqrt(np.pi**2*106.75/90) * (t_dm or 0) ** 2 / MP)))

# ---------------- inflaton direct decay bound ----------------
# Y_X = 2 Br (3/4) T_RH / m_phi  (two X per decay, instant conversion); require Omega_X h^2 < 0.12
inflaton = {}
for M in (3e12, 1e13):
    Ymax = 0.12 / (2.74e8 * M)
    inflaton[f"M={M:.0e}"] = dict(Y_max=Ymax, Br_times_TRH_over_mphi_max=Ymax / 1.5,
                                  comment="kinematically closed if m_phi < 2 M; with H_I <= 3e7 that needs m_phi/H_I < %.0e" % (2 * M / 3e7))

# ---------------- gravitational production (exponential suppression) ----------------
grav = dict(M_over_HI_min=3e12 / 3.5e7, comment="M_X/H_I >= 8.6e4 >> 1: inflationary gravitational production is exponentially suppressed (CCKR hep-ph/0104100 regime M_X < H_I does not apply); graviton-mediated thermal production needs T_max >~ M (not the case in the allowed window)")

out = dict(homotopy=homotopy, windows=windows, inflaton_direct_decay=inflaton, gravitational=grav,
           axion_points=axion["points"], splitting=split["T2+DeltaR_min"]["rows"][0], coloured_decay=split["coloured_component_decay"],
           instant_reheating_cross_check=relic["cross_check"], robustness_k=[r for r in th if "k=" in r["criterion"]])
with open(D + "k5_history.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=1, default=str)
print(json.dumps(homotopy, indent=1))
for w in windows:
    print(w)
print(json.dumps(inflaton, indent=1))
print("robustness:", [ (r["criterion"], r["M"], r["TRH_max"]) for r in th if "k=" in r["criterion"]])
