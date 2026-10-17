"""Second-pass verifier checks (independent re-derivations):
 (B) one-loop G3221 b-coefficients from my own content table (exact Fractions) and the 10_F triplet/bidoublet
     mass-ratio integral; sign check; also the size of the (unknown) two-loop and finite-threshold terms.
 (C) axion: analytic misalignment estimate (standard fit) vs the ODE theta_i; isocurvature H_I,max formula;
     T_max coefficient derivation check.
 (D) the singlet-LRP gap: if y_1 << y_10 the Dirac singlet N (mass y_1 v_S) is the LRP; production through the
     declared T1.N1.H* / T2.N3.H Yukawas (y_h) via 10_F exchange (dim-5 h h N N / M_10 after integrating out the 10_F)
     is NOT Boltzmann suppressed once M_N < T_max: estimate the (y_1, y_h) region K5's window needs.
"""
from fractions import Fraction as Fr
import json, numpy as np

OUT = r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\wfV21\K5-cosmology-relics\verify-feasibility\vf2_splitting_axion_singlet.json"
res = {}

# ---------------- (B) b-coefficients, G3221 = SU(3) x SU(2)_L x SU(2)_R x U(1)_{B-L} (GUT-normalised: T_BL = sqrt(3/8)(B-L)) ----
# Weyl fermion: +2/3 T(R) per rep ; complex scalar: +1/3 T ; real scalar: +1/6 T ; gauge: -11/3 C_2(G)
T3 = {1: Fr(0), 3: Fr(1, 2), 6: Fr(5, 2), 8: Fr(3)}
T2 = {1: Fr(0), 2: Fr(1, 2), 3: Fr(2)}
D3 = {1: 1, 3: 3, 6: 6, 8: 8}


def b_rep(d3, dL, dR, bl, kind):
    f = {"weyl": Fr(2, 3), "cplx": Fr(1, 3), "real": Fr(1, 6)}[kind]
    n = D3[d3] * dL * dR
    return [f * T3[d3] * dL * dR, f * T2[dL] * D3[d3] * dR, f * T2[dR] * D3[d3] * dL, f * Fr(3, 8) * Fr(bl) ** 2 * n]


def add(*rows):
    return [sum(r[i] for r in rows) for i in range(4)]


gauge = [Fr(-11), Fr(-22, 3), Fr(-22, 3), Fr(0)]
# one 16 (Weyl): Q(3,2,1)_{1/3} + Q^c(3bar,1,2)_{-1/3} + L(1,2,1)_{-1} + L^c(1,1,2)_{1}
one16 = add(b_rep(3, 2, 1, Fr(1, 3), "weyl"), b_rep(3, 1, 2, Fr(-1, 3), "weyl"), b_rep(1, 2, 1, -1, "weyl"), b_rep(1, 1, 2, 1, "weyl"))
# one 10 (Weyl): (1,2,2)_0 + (3,1,1)_{-2/3} + (3bar,1,1)_{2/3}
one10 = add(b_rep(1, 2, 2, 0, "weyl"), b_rep(3, 1, 1, Fr(-2, 3), "weyl"), b_rep(3, 1, 1, Fr(2, 3), "weyl"))
families = [3 * v for v in one16]
S_sector = add(*([one10] * 2 + [one16] * 6))         # 2 x 10_F + 3 x (16 + 16bar)
T2_scal = add(b_rep(1, 2, 2, 0, "cplx"), b_rep(8, 2, 2, 0, "cplx"), b_rep(8, 3, 1, 0, "real"), b_rep(1, 3, 1, 0, "real"))
DR_min = b_rep(1, 1, 3, 2, "cplx")
DR_full = add(DR_min, b_rep(3, 1, 3, Fr(2, 3), "cplx"), b_rep(6, 1, 3, Fr(2, 3), "cplx"))
b_T2min = add(gauge, families, S_sector, T2_scal, DR_min)
b_T2full = add(gauge, families, S_sector, T2_scal, DR_full)
res["b_one16"] = [str(v) for v in one16]
res["b_one10"] = [str(v) for v in one10]
res["b_T2_DRmin"] = [str(v) for v in b_T2min]
res["b_T2_DRfull"] = [str(v) for v in b_T2full]
print("one16:", one16, " one10:", one10, " (complete-multiplet check: all four equal)")
print("b(T2+DRmin) =", b_T2min, "  b(T2+DRfull) =", b_T2full)
print("researcher: (47/6, 12, 29/3, 89/6) and (65/6, 12, 47/3, 49/3)")

# Casimirs of the 10_F components
C_trip = [Fr(4, 3), Fr(0), Fr(0), Fr(3, 8) * Fr(2, 3) ** 2]
C_bid = [Fr(0), Fr(3, 4), Fr(3, 4), Fr(0)]
print("sum C triplet =", sum(C_trip), " bidoublet =", sum(C_bid))


def mass_ratio(b, M10, MU, aUinv, loops_note=""):
    """ln(M_trip/M_bid) at M10 from one-loop gauge running of the Dirac mass: d ln m/d ln mu = -(6/16pi^2) sum_i C_i g_i^2."""
    bb = np.array([float(v) for v in b])
    t = np.log(MU / M10)
    xs = np.linspace(0, t, 4001)
    ainv = aUinv + np.outer(xs, bb) / (2 * np.pi)
    g2 = 4 * np.pi / ainv
    ct = np.array([float(v) for v in C_trip]); cb = np.array([float(v) for v in C_bid])
    diff = g2 @ ct - g2 @ cb
    return (6 / (16 * np.pi ** 2)) * np.trapezoid(diff, xs), (1 / ainv[-1]).tolist()


rows = []
for lab, b in (("T2+DRmin", b_T2min), ("T2+DRfull", b_T2full)):
    for (M10, MU, aUinv) in ((1e13, 2.5e16, 36.0), (3e12, 2.5e16, 36.0), (1e13, 2.1e16, 30.0), (1e13, 3.1e16, 42.0)):
        dln, aM = mass_ratio(b, M10, MU, aUinv)
        rows.append(dict(content=lab, M10=M10, MU=MU, aUinv=aUinv, dlnM_trip_minus_bid=dln, alpha_at_M10=aM))
        print(f"{lab} M10={M10:.0e} MU={MU:.1e} aU^-1={aUinv}: ln(M_trip/M_bid) = {dln:+.3e}; alpha_i(M10) = {np.round(aM,4)}")
res["splitting_rows"] = rows
# size of competing effects: two-loop gauge terms ~ (alpha/4pi) x one-loop; finite threshold ~ (6/16pi^2) * C * g_U^2 * ln(M_X/M_U) per unit log
gU2 = 4 * np.pi / 36
res["threshold_coefficient_per_unit_log"] = (6 / (16 * np.pi ** 2)) * gU2 * 1.0   # x (sum over X bosons of C differences) ~ O(1)
print("one-loop threshold coefficient (6/16pi^2) g_U^2 per unit C per unit ln(M_X/M_U):", res["threshold_coefficient_per_unit_log"])

# ---------------- (C) axion ----------------
# standard analytic misalignment (Borsanyi et al. 2016 / Marsh 2016 style fit, pre-inflation, no anharmonic corr.):
# Omega_a h^2 ~ 0.12 (f_a / 9.2e11 GeV)^1.165 theta_i^2   (fit quoted e.g. in 1610.08297 eq. for n ~ 8 chi(T))
def theta_analytic(fa, target=0.12, f0=9.2e11, p=1.165):
    return np.sqrt(target / (0.12 * (fa / f0) ** p))
# anharmonic correction F(theta) ~ [ln(e/(1-theta^2/pi^2))]^{7/6} (Visinelli-Gondolo 0903.4377)
def theta_anharmonic(fa, target=0.12):
    th = theta_analytic(fa, target)
    for _ in range(50):
        F = (np.log(np.e / (1 - th ** 2 / np.pi ** 2))) ** (7 / 6)
        th = np.sqrt(target / (0.12 * (fa / 9.2e11) ** 1.165 * F))
    return th
axion = []
for (Ms, ys) in ((1e13, 0.305), (1e13, 0.35), (1e13, 0.389), (3e12, 0.31), (3e12, 0.39)):
    vS = np.sqrt(2) * Ms / ys
    fa = vS / 17
    ma = 5.70e-6 * 1e12 / fa
    th = theta_anharmonic(fa)
    # isocurvature: P_iso = (H_I/(pi f_a theta))^2 ; beta = P_iso/(P_iso+P_zeta) < beta_max
    for beta in (0.038, 0.035):
        Pz = 2.1e-9
        HImax = np.pi * fa * th * np.sqrt(beta / (1 - beta) * Pz)
        axion.append(dict(M_s=Ms, y_s=ys, f_a=fa, m_a_ueV=ma * 1e6, theta_i_analytic=th, beta_iso=beta, H_I_max=HImax))
        print(f"M_s={Ms:.0e} y_s={ys}: f_a={fa:.3e} m_a={ma*1e6:.2f} ueV theta_i(analytic fit)={th:.3f} beta={beta}: H_I,max={HImax:.3e}")
res["axion"] = axion
# T_max coefficient from the analytic reheating solution: rho_R,max = 0.139 Gamma rho_I/H_I with rho_I = 3 M_P^2 H_I^2
x = (3 / 8) ** 0.4
fmax = x ** 1.5 - x ** 4
coef = (0.4 * fmax * 3 * np.sqrt(np.pi ** 2 / 90) * 30 / np.pi ** 2) ** 0.25   # x g_*^{-1/8}
res["Tmax_coefficient_times_gstar_1_8"] = coef
print(f"T_max = {coef:.3f} g_*^(-1/8) (T_RH^2 H_I M_P)^(1/4) -> {coef*106.75**(-1/8):.3f} at g_*=106.75 (researcher 0.45)")

# ---------------- (D) singlet-LRP gap ----------------
# LRP = Dirac singlet N, mass M_N = y_1 v_S, v_S = 4e13.  Production: h h -> N N via 10_F exchange with Yukawa y_h
# (T1.N1.H*: 10_F . N . H10^dag; the light Higgs is the H10-admixture of the bidoublet, take fraction ~ 1).
# Integrating out the 10_F (mass M_10 = y_10 v_S): L_eff = (y_h^2/M_10) (H^dag H) N N  (dim-5, no derivative)
# -> sigma(h h -> N N) ~ y_h^4 /(8 pi M_10^2) for s >> M_N^2.  Freeze-in during radiation era after reheating:
# Y_N ~ (135 sqrt(10)/(4 pi^3 g_*^{3/2}) ... ) use the standard UV-freeze-in dim-5 result: Y ~ 0.2 * M_P T_RH * <sv>/(1) in the
# convention dY/dT = -<sv> n_eq^2/(s H T): with n_eq = (zeta3/pi^2) T^3 per dof x 4 (real h dof) and s = 0.44 g_* T^3, H = 0.33 sqrt(g_*) T^2/M_P
def Y_singlet_freezein(y_h, M_10, T_RH, gs=106.75):
    sv = y_h ** 4 / (8 * np.pi * M_10 ** 2)
    n_h = 4 * 1.202 / np.pi ** 2          # x T^3
    s = 2 * np.pi ** 2 / 45 * gs            # x T^3
    Hc = np.sqrt(np.pi ** 2 * gs / 90) / 2.435e18   # x T^2
    # Y = int_0^{T_RH} sv n_h^2 T^6 /(s T^3 Hc T^2 T) dT = sv n_h^2/(s Hc) * T_RH
    return sv * n_h ** 2 / (s * Hc) * T_RH
gap = []
vS = 4e13
for y10 in (0.3,):
    M10 = y10 * vS
    for y1 in (1e-1, 3e-2, 1e-2, 1e-3):
        MN = y1 * vS
        for TRH in (1e11, 1e10):
            # if M_N > ~20 T_max the exponential suppression applies (K5's regime); here flag only the unsuppressed case
            Tmax = 0.45 * (TRH ** 2 * 3e7 * 2.435e18) ** 0.25
            unsuppressed = MN < 3 * Tmax
            # y_h needed for Omega_N h^2 <= 0.12 (radiation-era freeze-in only; reheating-era production adds)
            Ymax = 0.12 / (2.74e8 * MN)
            # solve y_h: Y ~ y_h^4 * const
            Y1 = Y_singlet_freezein(1.0, M10, TRH)
            yh_max = (Ymax / Y1) ** 0.25
            gap.append(dict(y_10=y10, y_1=y1, M_N=MN, T_RH=TRH, T_max=Tmax, Boltzmann_unsuppressed=bool(unsuppressed), y_h_max_for_Omega_DM=yh_max))
            print(f"y_1={y1:.0e} (M_N={MN:.1e}) T_RH={TRH:.0e} T_max={Tmax:.1e} unsuppressed={unsuppressed}: y_h <= {yh_max:.2e} for Omega_N <= Omega_DM")
res["singlet_LRP_gap"] = gap
json.dump(res, open(OUT, "w"), indent=1, default=str)
