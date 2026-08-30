# SUSY V66 Spin(11) GM-overlap and unification repair audit

Status: V66_SPIN11_GM_OVERLAP_UNIFICATION_REPAIR__V65_ARTIFACTS_VALID__V65_ACTION_UPGRADE_RETRACTED__GM_ALLOWED_NOT_CONSTRUCTED__V64_NULL_MODE_NORMALIZATION_SUPPRESSES_GM_AND_PORTALS__ONE_LOOP_THRESHOLD_SOLVE_EXACT__GAUGE_ONLY_TWO_LOOP_DIAGNOSTICS__FULL_SU5_TEN_COMPENSATOR_CANDIDATE_EXHIBITED__BARYON_SAFETY_NOT_INHERITED__CURRENT_ACTION_REJECTED__TWO_CONDITIONAL_EXTENSIONS__NO_WZ__G1_TO_G8_OPEN

Canonical core: 07593002755158c96647701da7453b1942114424a5d3aff5318ebb891a2964ae

## Decision

The current V65 action is REJECTED. Its immutable files and cores remain valid, but the upgrade to conditionally viable is retracted: Z4R permits a Giudice-Masiero bilinear, yet the bound action does not construct its coefficient or hidden-sector F terms. V64's normalizable orphan mode and the no-WZ correction are preserved. G1-G8 remain OPEN.

Two research branches survive only as conditional extensions: a high-scale orphan-only branch and a low-scale full-10 compensator.

## Regression-scope correction

The current complete V59-V65 selection contains 16 files and 208 tests. The 199-test run omitted test_susy_v59_heterotic_corrected_z4r_data_sufficiency_audit.py, which contains 9 tests.

## GM overlap: allowed is not constructed

mu_Q = [m_3/2 Z_Q - Fbar^I partial_bar_I Z_Q]/sqrt(Y_Q Y_Qbar)

the bound action specifies neither Z_Q, its hidden-sector derivative, nor the SUSY-breaking F terms; symmetry permission does not prove a nonzero numerator.

The V64 null-mode normalization gives:

- alpha^2 = g5^2 v^2 L
- 1 + alpha^2
- Z_eff = c_K/(1+alpha^2)
- portal amplitude: 1/sqrt(1+alpha^2)

## Exact one-loop threshold solution

The conventional beta-function order is (b1,b2,b3). The orphan pair has Delta b = (1/5,3,2). For c=MQ/MS:

- MS = 2.25084e11 GeV * c^(-21/32)
- MQ = 2.25084e11 GeV * c^(11/32)
- MG = 4.54981e15 GeV * c^(3/64)
- alphaU^-1 = 34.16816 - [121/(128*pi)] ln(c)

At c=1 the direct solve gives MS=MQ=2.250826151e+11 GeV, MG=4.549789822e+15 GeV and alphaU^-1=34.16815951.
At MS=1 TeV it instead requires MQ=5.337995621e+15 GeV and MG=1.797161841e+16 GeV.

## Martin-Vaughn exact gauge coefficients

MSSM B = [['199/25', '27/5', '88/5'], ['9/5', '25', '24'], ['11/5', '9', '14']]

Orphan Delta B_Q = [['1/75', '3/5', '16/15'], ['1/5', '21', '16'], ['2/15', '6', '68/3']]

Companion Delta b = ['14/5', '0', '1'].
 Together with Q this gives a complete 10+10bar with Delta b = ['3', '3', '3'].

## Gauge-only two-loop diagnostics

Raw orphan-only: MS=MQ=4.760378229e+11 GeV, MG=2.266291459e+15 GeV, alphaU=0.02859797.
With only the universal MSbar-to-DRbar shift: MS=MQ=4.991969753e+11 GeV, MG=2.367079474e+15 GeV, alphaU^-1=34.940560.
Full 10+10bar raw diagnostic: MS=M10=1.383905252e+04 GeV, MG=1.216381692e+16 GeV, alphaU=0.07873997.

These are diagnostics only. Finite decoupling, Yukawas, soft splittings, KK thresholds and brane kinetic terms are absent.

## Why the full-10 candidate is not accepted

Its local Spin(11)/Spin(10) embedding, localized anomaly/GS closure and Kahler/soft sector are absent. Moreover the full 10_X 5bar 5bar portal contains Uc_X dc dc and Ec_X L L. The orphan-only V65 baryon-safety assignment therefore does not extend to this completion.

## Fail-closed acceptance criteria

- A1 [OPEN]: full pole and running spectrum with every superpartner and exotic threshold
- A2 [OPEN]: tan(beta) and all relevant Yukawa boundary conditions
- A3 [OPEN]: two-loop running plus complete one-loop decoupling and scheme matching
- A4 [OPEN]: Mc, M*, the KK tower and brane-kinetic threshold corrections
- A5 [OPEN]: physical threshold ordering, perturbativity and vacuum stability
- A6 [OPEN]: three-coupling residual smaller than a quantified truncation uncertainty
- A7 [OPEN]: explicit hidden/Kahler/soft sector producing nonzero mu_Q and acceptable B terms
- A8 [OPEN]: for T66, local Spin(11)/Spin(10) embedding, anomaly/GS closure and baryon safety

## Gate ledger

- G1 [OPEN]: OPEN: the current action is rejected; H66 and T66 are conditional extensions without complete microscopic actions
- G2 [OPEN]: OPEN: no complete flavor/KK determinant fit
- G3 [OPEN]: OPEN: no full vacuum and SUSY-breaking stabilization
- G4 [OPEN]: OPEN: no Dai-Freed/global anomaly computation for either extension
- G5 [OPEN]: OPEN: no controlled proton and baryon analysis for the full completion
- G6 [OPEN]: OPEN: only gauge-only unification diagnostics exist
- G7 [OPEN]: OPEN: no pole spectrum, lifetimes, relic or collider calculation
- G8 [OPEN]: OPEN: no UV regulator or quantified predictivity score

No gate is promoted. No Wess-Zumino term is forced.
