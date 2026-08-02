#!/usr/bin/env python3
"""Deterministic numerical and operator-audit engine for Spin(10) x Z17.

Computes every internally derived numerical claim of the v17 manuscript,
writes a machine-readable verdict and exits nonzero on any failed check.

Sections:
  1. Anomaly theorem (brute force + modular derivation)
  2. Rephasing matrix ranks and null vector
  3. One-loop gauge unification (solved, not quoted)
  4. Spectator correction
  5. Axion observables with uncertainty
  6. Cosmology (anharmonic misalignment + isocurvature)
  7. Proton-decay Monte Carlo (seeded, priors printed)
  8. Domain-wall/string topology
  9. Axion quality: over-complete local-operator enumeration, exact
     spectator-vector selection, multi-spurion vacuum closure and NDA bound
 10. Referee audit: explicit Clifford algebra, Grassmann invariants,
     independent lower-bound regression and the P=12 vacuum graph

Writes: so10_axion_v17_verdict.json next to this file unless --output is set.
Requires: numpy, scipy and the supplied v17 audit modules.
Usage: python so10_axion_v17_engine.py [--trials 100000] [--output FILE]
"""
import argparse, json, math, sys, pathlib
import numpy as np
from scipy.optimize import brentq
from so10_quality_v17 import (
    EXPLICIT_OPERATORS,
    build_quality_report,
    combined_z51_anomalies,
    enumerate_overcomplete_catalog,
    explicit_p12_certificate,
    minimum_local_pq_dimension,
    minimum_q0_vector_breaking_dimension,
    minimum_vacuum_closure,
    nda_vacuum_bound,
    one_sided_mass_invariants,
    renormalizable_vector_breakers,
    scalar_quality_numbers,
)
from spin10_referee_audit import build_referee_report

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--trials', type=int, default=100_000,
                    help='seeded proton-decay Monte Carlo trials (>=1000)')
parser.add_argument('--output', type=pathlib.Path,
                    help='machine-readable verdict path')
parser.add_argument('--inject-failure', action='store_true',
                    help=argparse.SUPPRESS)
ARGS = parser.parse_args()
if ARGS.trials < 1_000:
    parser.error('--trials must be at least 1000')

PI = math.pi
FAILURES = []
CHECK_COUNT = 0

def check(name, cond, detail=''):
    global CHECK_COUNT
    CHECK_COUNT += 1
    tag = 'PASS' if cond else 'FAIL'
    print(f'  [{tag}] {name}' + (f'  ({detail})' if detail else ''))
    if not cond:
        FAILURES.append(name)
    return cond

V = {}   # verdict dictionary

print('=' * 76)
print('S1. ANOMALY THEOREM (computed)')
print('=' * 76)
# mass condition
apb = (-4) % 17
# brute force k
ks = [k for k in range(1, 120) if (6 + 2 * k * apb) % 17 == 0]
check('mixed anomaly solutions k = 5 + 17m', ks[:4] == [5, 22, 39, 56],
      f'k = {ks[:4]}')
k_min = ks[0]
# gravitational automatic
grav_ok = all((48 + 16 * k * apb) % 17 == 0 for k in ks[:4])
check('gravitational class vanishes on the same set', grav_ok)
# cubic -> residues
roots = [x for x in range(17) if (x * x - 13 * x + 5) % 17 == 0]
check('cubic residues unique {2,11}', roots == [2, 11], f'roots = {roots}')
a_res, b_res = 2, -6           # integer lift of (2, 11)
cubic_int = 48 + 80 * (a_res ** 3 + b_res ** 3)
check('integer-lift cubic sum divisible by 17', cubic_int % 17 == 0,
      f'{cubic_int} = {cubic_int // 17} x 17')
mixed_int = 6 + 2 * k_min * (a_res + b_res)
grav_int = 48 + 16 * k_min * (a_res + b_res)
check('integer mixed/grav sums divisible by 17',
      mixed_int % 17 == 0 and grav_int % 17 == 0,
      f'{mixed_int}, {grav_int}')
V['theorem'] = {'k_min': k_min, 'residues': [2, 11], 'lift': [2, -6],
                'sums': [mixed_int, grav_int, cubic_int]}

print('=' * 76)
print('S2. REPHASING MATRIX (computed)')
print('=' * 76)
M = np.array([
    [0, 2, 1, 0, 0, 0], [0, 2, 0, 1, 0, 0], [1, 0, 0, 0, 1, 1],
    [2, 0, 2, 2, 0, 0], [-3, 1, 0, 0, 0, 1], [4, 1, 1, 0, 1, 0],
    [-2, 1, 0, 0, 1, 2], [-2, 0, 0, 0, 4, 0]], float)
r6 = np.linalg.matrix_rank(M)
Mno = np.delete(M, 3, axis=0)
r5 = np.linalg.matrix_rank(Mno)
null = np.linalg.svd(Mno)[2][-1]
null = null / null[0] * 4
check('rank(M) = 6', r6 == 6)
check('rank without lock = 5', r5 == 5)
check('null vector = (4,18,-36,-36,2,-6)',
      np.allclose(null, [4, 18, -36, -36, 2, -6], atol=1e-9))
res = (M @ np.array([4, 18, -36, -36, 2, -6.0])).astype(int)
check('lift residual = -136 in lock row only',
      res[3] == -136 and np.count_nonzero(res) == 1, f'{res.tolist()}')
V['rephasing'] = {'rank_full': int(r6), 'rank_no_lock': int(r5),
                  'null_vector': null.round(6).tolist()}

print('=' * 76)
print('S3. ONE-LOOP UNIFICATION (solved)')
print('=' * 76)
MZ = 91.1876
A1, A2, A3 = 59.02, 29.57, 1 / 0.1179
B_LOW = (21 / 5, -3.0, -7.0)          # 2HDM
B_PS = (-7 / 3, 2.0, 26 / 3)          # (1,2,2)+(10bar,1,3)+(15,2,2)

def chain(logMI, dthr=0.0):
    MI = 10 ** logMI
    L = math.log(MI / MZ) / (2 * PI)
    i1, i2, i3 = A1 - B_LOW[0] * L, A2 - B_LOW[1] * L, A3 - B_LOW[2] * L
    i4, iL = i3 + dthr, i2
    iR = (5 * i1 - 2 * i4) / 3
    lnMU = 2 * PI * (i4 - iL) / (B_PS[0] - B_PS[1])
    MU = MI * math.exp(lnMU)
    i4U = i4 - B_PS[0] * lnMU / (2 * PI)
    iRU = iR - B_PS[2] * lnMU / (2 * PI)
    return i4U - iRU, MU, i4U

logMI = brentq(lambda x: chain(x)[0], 4, 15.9, xtol=1e-12)
_, MG, IU = chain(logMI)
MI = 10 ** logMI
check('M_I = 6.314e11 GeV', abs(MI - 6.3139e11) / 6.3139e11 < 2e-3,
      f'{MI:.4e}')
check('M_GUT = 9.918e15 GeV', abs(MG - 9.9176e15) / 9.9176e15 < 2e-3,
      f'{MG:.4e}')
check('1/alpha_GUT = 37.313', abs(IU - 37.313) < 0.02, f'{IU:.3f}')
V['unification'] = {'M_I': MI, 'M_GUT': MG, 'inv_alpha': IU}

print('=' * 76)
print('S4. SPECTATOR CORRECTION (computed)')
print('=' * 76)
ys = math.sqrt(2)
Ms = ys * MI / math.sqrt(2)
dinv = -(40 / 3) / (2 * PI) * math.log(MG / Ms)
check('Delta(1/alpha) = -20.503 at y_s = sqrt(2)',
      abs(dinv + 20.503) < 0.02, f'{dinv:.3f}')
IU_spec = IU + dinv
V['spectator'] = {'y_s': ys, 'M_s': Ms, 'delta_inv_alpha': dinv,
                  'inv_alpha_after': IU_spec}

print('=' * 76)
print('S5. AXION OBSERVABLES (with uncertainty)')
print('=' * 76)
# chi^{1/4} = 75.5(5) MeV, Grilli di Cortona et al. 1511.02867
CHI4, CHI4_ERR = 75.5e-3, 0.5e-3       # GeV
CAGG, CAGG_ERR = 1.92, 0.04            # QCD photon coefficient (same ref)
ALPHA_EM = 1 / 137.036
H_EVS = 4.135667696e-15
N2 = 2 * (6 + 5 * 2 * (a_res + b_res))
NDW_cover = abs(N2) // 4
FA = MI / NDW_cover
MA = CHI4 ** 2 / FA * 1e9 * 1e6        # ueV
MA_ERR = MA * 2 * CHI4_ERR / CHI4
NU = MA * 1e-6 / H_EVS / 1e9
NU_ERR = NU * 2 * CHI4_ERR / CHI4
G = ALPHA_EM / (2 * PI * FA) * abs(8 / 3 - CAGG)
G_ERR = ALPHA_EM / (2 * PI * FA) * CAGG_ERR
check('2N = -68, N_DW^cover = 17', N2 == -68 and NDW_cover == 17)
check('f_a = 3.714e10 GeV', abs(FA - 3.7140e10) / 3.714e10 < 2e-3,
      f'{FA:.4e}')
check('m_a = 153.5 +/- 2.0 ueV', abs(MA - 153.5) < 0.3,
      f'{MA:.2f} +/- {MA_ERR:.2f}')
check('nu = 37.11 +/- 0.49 GHz',
      abs(NU - 37.11) < 0.05 and abs(NU_ERR - 0.49) < 0.02,
      f'{NU:.2f} +/- {NU_ERR:.2f}')
check('g = (2.335 +/- 0.125)e-14 GeV^-1',
      abs(G - 2.335e-14) / 2.335e-14 < 0.01
      and abs(G_ERR - 0.125e-14) / 0.125e-14 < 0.05,
      f'{G:.3e} +/- {G_ERR:.3e}')
V['axion'] = {'f_a': FA, 'm_a_ueV': MA, 'm_a_err_ueV': MA_ERR,
              'nu_GHz': NU, 'nu_err_GHz': NU_ERR,
              'g': G, 'g_err': G_ERR}

print('=' * 76)
print('S6. COSMOLOGY (computed)')
print('=' * 76)
def F_anh(t):
    x = min(t * t / PI ** 2, 1 - 1e-12)
    return (math.log(math.e / (1 - x))) ** 1.184

def omega(f_a, t):
    return 0.195 * t * t * F_anh(t) * (f_a / 1e12) ** 1.184

th = brentq(lambda t: omega(FA, t) - 0.120, 0.05, 3.1415)
dln = (math.log(omega(FA, th + 1e-6))
       - math.log(omega(FA, th - 1e-6))) / 2e-6
S_max = math.sqrt(0.038 / 0.962 * 2.1e-9)
H_max = S_max * 2 * PI * FA / dln
check('theta_i = 2.91', abs(th - 2.91) < 0.02, f'{th:.3f}')
check('H_I < 9.1e5 GeV', abs(H_max - 9.07e5) / 9.07e5 < 0.02,
      f'{H_max:.2e}')
V['cosmology'] = {'theta_i': th, 'H_I_max': H_max,
                  'dlnOmega_dtheta': dln}

print('=' * 76)
print('S7. PROTON-DECAY MONTE CARLO (seeded, computed)')
print('=' * 76)
M_P, M_PI, V_UD = 0.9383, 0.1350, 0.9737
HBAR_GEV_S, S_PER_YR = 6.582119569e-25, 3.156e7

def tau_p(M_X, aG, A_R, W):
    """Gamma(p->e+ pi0) = m_p/32pi (1-(mpi/mp)^2)^2 (4pi aG/M_X^2)^2
       A_R^2 W^2 [1+(1+Vud^2)^2];   tau = hbar/Gamma."""
    kin = (1 - (M_PI / M_P) ** 2) ** 2
    C = 4 * PI * aG / M_X ** 2
    flav = 1 + (1 + V_UD ** 2) ** 2
    Gam = M_P / (32 * PI) * kin * C ** 2 * A_R ** 2 * W ** 2 * flav
    return HBAR_GEV_S / Gam / S_PER_YR

rng = np.random.default_rng(20260801)
taus = []
for _ in range(ARGS.trials):
    a3 = rng.normal(0.1179, 0.0009)
    a1i, a2i = rng.normal(59.02, 0.02), rng.normal(29.57, 0.02)
    d = rng.uniform(-1, 1)
    try:
        A1t, A2t, A3t = a1i, a2i, 1 / a3
        # local solve with these inputs
        def ch(logmi):
            mi = 10 ** logmi
            L = math.log(mi / MZ) / (2 * PI)
            i1, i2, i3 = (A1t - B_LOW[0] * L, A2t - B_LOW[1] * L,
                          A3t - B_LOW[2] * L)
            i4, iL = i3 + d, i2
            iR = (5 * i1 - 2 * i4) / 3
            lnMU = 2 * PI * (i4 - iL) / (B_PS[0] - B_PS[1])
            MU_ = mi * math.exp(lnMU)
            return (i4 - B_PS[0] * lnMU / (2 * PI)
                    - (iR - B_PS[2] * lnMU / (2 * PI))), MU_, \
                   i4 - B_PS[0] * lnMU / (2 * PI)
        lmi = brentq(lambda x: ch(x)[0], 4, 15.9)
        _, MU_t, iU_t = ch(lmi)
        iU_s = iU_t - (40 / 3) / (2 * PI) * math.log(MU_t / 10 ** lmi)
    except Exception:
        continue
    xi = 10 ** rng.uniform(math.log10(0.5), math.log10(2.0))
    taus.append(tau_p(xi * MU_t, 1 / iU_s, rng.uniform(2.0, 3.2),
                      rng.normal(0.1095, 0.011)))
taus = np.array(taus)
med = float(np.median(taus))
f_sk = float((taus < 2.4e34).mean() * 100)
f_hk = float(((taus >= 2.4e34) & (taus < 1e35)).mean() * 100)
check(f'{ARGS.trials} proton trials accepted', len(taus) == ARGS.trials,
      f'{len(taus)} accepted')
check('median tau_p ~ 1.04e35 yr', 0.9e35 < med < 1.2e35, f'{med:.3e}')
check('SK-excluded fraction ~ 35.3%', 34 < f_sk < 37, f'{f_sk:.2f}%')
check('additional Hyper-K fraction ~ 14.4%', 13 < f_hk < 16,
      f'{f_hk:.2f}%')
V['proton'] = {'median_yr': med, 'SK_excluded_pct': round(f_sk, 2),
               'HK_new_pct': round(f_hk, 2), 'seed': 20260801,
               'priors': 'printed in manuscript Table 1'}

print('=' * 76)
print('S8. TOPOLOGY (computed)')
print('=' * 76)
check('gauge orbit: 4*13 = 1 mod 17', (4 * 13) % 17 == 1)
winding = 4 * 13 / 17 - 3
check('string sector (l,n)=(13,-3): S-winding = 2pi/17',
      abs(winding - 1 / 17) < 1e-12, f'{winding:.6f} x 2pi')
V['topology'] = {'N_DW_physical': 1, 'string_sector': [13, -3],
                 'S_winding_over_2pi': winding}

print('=' * 76)
print('S9. AXION QUALITY: LOCAL OPERATORS VS VACUUM CLOSURES (computed)')
print('=' * 76)
MPL = 2.435e18                          # reduced Planck mass, GeV
CHI = CHI4 ** 4                         # GeV^4
VS, VSR = MI, MI / math.sqrt(2)         # v_S and v_S/sqrt(2)
# The scalar theorem is analytic: tensor indices contract in pairs, hence
# scalar-invariant PQ charge is 0 mod 4.  Together with Z17 this means
# |Q_PQ| >= lcm(4,17)=68, saturated by S^17 at d=17.
scalar = scalar_quality_numbers(VS, CHI4, MPL)
check('scalar PQ charge is a multiple of 4; lcm(4,17) = 68',
      math.lcm(4, 17) == 68)
check('leading scalar breaker is S^17/M_Pl^13 at dimension 17',
      scalar['leading_dimension'] == 17)
check('direct scalar Delta theta_bar = 3.2e-37 per unit coefficient',
      abs(scalar['delta_theta_scalar'] / 3.24e-37 - 1) < 0.05,
      f"{scalar['delta_theta_scalar']:.2e}")
check('single-scalar-spurion protective dimension d_min = 14',
      scalar['minimum_safe_dimension'] == 14,
      f"d_min = {scalar['minimum_safe_dimension']}")
check('single-spurion quality ceiling v_S = 2.3e13 GeV',
      2.0e13 < scalar['v_s_quality_ceiling_GeV'] < 2.6e13,
      f"{scalar['v_s_quality_ceiling_GeV']:.2e}")

# Explicit local-operator regressions.  b denotes 16bar_s, Sd=S dagger,
# Hm/Hp a charge -2/+2 SO(10) tensor scalar.
O6 = EXPLICIT_OPERATORS['O6_portal']
O8 = EXPLICIT_OPERATORS['O8_vector_breaker']
O9 = EXPLICIT_OPERATORS['O9_one_sided']
O10 = EXPLICIT_OPERATORS['O10_six_fermion']
O12 = EXPLICIT_OPERATORS['O12_mixed']
check('d=6 portal: Q=-17, V=-1, centre neutral',
      (O6.dimension, O6.pq, O6.vector, O6.centre) == (6, -17, -1, 0))
check('d=8 PQ-conserving vector breaker: Q=0, V=+4',
      (O8.dimension, O8.pq, O8.vector, O8.centre) == (8, 0, 4, 0))
check('d=9 one-sided Majorana operator is local but has V=-2',
      (O9.dimension, O9.pq, O9.vector) == (9, -34, -2))
check('regression O10: six-fermion d=10 operator survives optional Z3',
      (O10.dimension, O10.pq, O10.vector, O10.triality) == (10, -34, -6, 0))
check('regression O12: mixed d=12 operator survives optional Z3',
      (O12.dimension, O12.pq, O12.vector, O12.triality) == (12, -17, 3, 0))

# Necessary-condition over-catalogue: allowing nonexistent contractions can
# only make the inferred minimum smaller, so a lower bound from it is safe.
catalog = enumerate_overcomplete_catalog(max_dimension=20)
check('over-catalogue local PQ-breaking minimum is dimension 6',
      minimum_local_pq_dimension(catalog) == 6)
check('lowest Q=0 spectator-vector breaker is dimension 8',
      minimum_q0_vector_breaking_dimension(catalog) == 8)
check('renormalizable Lagrangian preserves spectator vector U(1)_V',
      renormalizable_vector_breakers(catalog) == [])
no_low_closure = minimum_vacuum_closure(catalog, max_planck_power=11)
closure = minimum_vacuum_closure(catalog, max_planck_power=16)
check('no vacuum-sensitive closure exists through P = 11',
      no_low_closure is None)
check('first over-catalogue vacuum closure is P = 12',
      closure is not None and closure.planck_power == 12,
      'P = sum_i(d_i-4)')
check('first closure carries Q=-68 and exact spectator V=0',
      closure is not None and closure.pq == -68 and closure.vector == 0)
certificate = explicit_p12_certificate()
check('SO(10) saturation certificate is 4 O6 + O8 at P=12',
      certificate.planck_power == 12 and certificate.pq == -68
      and certificate.vector == 0 and len(certificate.operators) == 5)

# Wilsonian NDA: loops and small vevs are deliberately omitted, giving an
# upper bound per effective product C_eff of Wilson coefficients.
DTH_NDA = nda_vacuum_bound(Ms, certificate.planck_power, CHI4, MPL)
check('conservative multi-spurion |Delta theta_bar|/C_eff = 4.52e-28',
      abs(DTH_NDA / 4.5179e-28 - 1) < 0.01, f'{DTH_NDA:.3e}')
check('quality bound tolerates C_eff < 2.2e17',
      2.0e17 < 1e-10 / DTH_NDA < 2.4e17,
      f'C_eff < {1e-10 / DTH_NDA:.2e}')

# v15's claimed d=9 one-insertion loop was proportional to delta*M_s^3.
# It vanishes: tr(M^dagger M) and det(M^dagger M), hence the singular values,
# are phase independent for [[0,M_s],[M_s,delta exp(i phi)]].
phases = np.linspace(0.0, 2 * PI, 101)
invariants = one_sided_mass_invariants(Ms, 0.031 * Ms, phases)
check('one-sided mass-matrix invariants are phase independent',
      all(pair == invariants[0] for pair in invariants))
spectra = []
for phi in phases:
    mass = np.array([[0.0, Ms],
                     [Ms, 0.031 * Ms * np.exp(1j * phi)]], complex)
    spectra.append(np.linalg.eigvalsh(mass.conj().T @ mass))
check('numeric singular-value regression: no linear phase-dependent loop',
      np.allclose(spectra, spectra[0], rtol=2e-13, atol=0.0))

# Optional Z3 is audited but no longer imposed.  It is unnecessary, does not
# remove the d=10 six-fermion operator and would stabilize its lightest
# charged spectator state.  Its combined Z51 anomaly arithmetic is retained
# only as a regression.
catalog_z3 = enumerate_overcomplete_catalog(max_dimension=20,
                                             require_triality=True)
closure_z3 = minimum_vacuum_closure(catalog_z3, max_planck_power=16)
check('optional Z3 local minimum is d=10, not d>=19',
      minimum_local_pq_dimension(catalog_z3) == 10)
check('optional Z3 overall vacuum minimum is scalar P=13',
      closure_z3 is not None and closure_z3.planck_power == 13)
z51 = combined_z51_anomalies()
check('optional CRT Z51 anomaly sums are (408,3264,935136)=0 mod 51',
      z51['all_divisible_by_51']
      and [z51['mixed'], z51['gravitational'], z51['cubic']]
      == [408, 3264, 935136])

V['quality'] = build_quality_report(VS, Ms)
V['quality']['catalogue_sizes'] = {
    'Z17': len(catalog), 'Z17_with_optional_Z3': len(catalog_z3)}

print('=' * 76)
print('S10. EXPLICIT SPIN(10) REFEREE AUDIT (computed)')
print('=' * 76)
referee = build_referee_report()
clifford = referee['clifford']
anomalies = referee['anomalies']
invariants = referee['invariants']
graph = referee['vacuum_graph']
check('32x32 Euclidean Clifford algebra is exact',
      clifford['clifford_max_error'] == 0.0)
check('charge-conjugation identities are exact',
      clifford['charge_conjugation_max_error'] == 0.0
      and clifford['C_is_antisymmetric']
      and clifford['C_anticommutes_with_chirality'])
check('Spin(10) chirality spaces have dimensions 16 + 16',
      (clifford['chirality_plus'], clifford['chirality_minus']) == (16, 16))
check('10-channel bilinears obey Fermi statistics in 16 and 16bar',
      clifford['vector_bilinears_symmetric']
      and clifford['conjugate_vector_bilinears_symmetric'])
check('10-channel tensor Gram matrix is 16 times identity',
      clifford['vector_bilinear_gram'] == (16 * np.eye(10, dtype=int)).tolist())
check('odd-Z17 linear, cubic and Spin(10)^2 anomaly residues vanish',
      (anomalies['linear_mod17'], anomalies['cubic_mod17'],
       anomalies['mixed_mod17']) == (0, 0, 0)
      and (anomalies['linear'], anomalies['cubic'],
           anomalies['mixed_spin10']) == (1088, 107168, 136))
for key, label in (
    ('O6_singlet', 'O6 singlet'),
    ('O8', 'O8 four-spinor'),
    ('O10', 'O10 six-spinor'),
    ('O12', 'O12 mixed-spinor'),
):
    check(f'explicit Grassmann {label} invariant is nonzero',
          invariants[key]['nonzero'],
          f"{invariants[key]['grassmann_monomials']} monomials")
check('P=12 Spin(10) closure tensor is nonzero',
      invariants['closure_tensor_nonzero_entries'] == 640
      and invariants['closure_group_factor'] == 2560)
check('actual P=12 graph contraction is nonzero in a unit 10_H direction',
      invariants['graph_group_contraction_unit_10H'] == 256
      and invariants['graph_10H_contraction_gram']
      == (256 * np.eye(10, dtype=int)).tolist())
check('P=12 Lorentz closure factor is nonzero',
      invariants['closure_lorentz_factor'] == 4)
check('P=12 compact graph has two loops and the required charges',
      (graph['P'], graph['Q_PQ'], graph['spectator_vector'], graph['loops'])
      == (12, -68, 0, 2)
      and graph['same_chirality_propagators']
      == {'spectator_s_b': 4, 'family_10H_channel': 2})
check('explicit graph phase and refined suppression are consistent',
      graph['resulting_scalar_Q_PQ'] == -68
      and graph['resulting_scalar_phase'] == '(S_dagger)^18 (10_H_dagger)^2'
      and abs(graph['diagrammatic_estimate_per_Ceff'] / 2.750298425064228e-51 - 1)
      < 1e-12,
      f"{graph['diagrammatic_estimate_per_Ceff']:.3e} per C_eff")
V['referee_audit'] = referee

# ---------------------------------------------------------------- verdict
if ARGS.inject_failure:
    check('injected failure exercises nonzero-exit path', False)

out = (ARGS.output if ARGS.output else
       pathlib.Path(__file__).resolve().parent / 'so10_axion_v17_verdict.json')
out = out.resolve()
out.parent.mkdir(parents=True, exist_ok=True)
V['failures'] = FAILURES
V['n_checks_failed'] = len(FAILURES)
V['n_checks_total'] = CHECK_COUNT
with open(out, 'w') as f:
    json.dump(V, f, indent=2)
print('=' * 76)
print(f'VERDICT: {"ALL CHECKS PASS" if not FAILURES else FAILURES}')
print(f'machine-readable verdict: {out.name}')
print('=' * 76)
sys.exit(0 if not FAILURES else 1)
