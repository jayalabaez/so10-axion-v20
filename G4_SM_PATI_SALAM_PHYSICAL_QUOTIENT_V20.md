# G4 at the G3 witness: gauge quotient, axion and physical Hessian -- v20

**Status:** `G4_SM_PATI_SALAM_PHYSICAL_QUOTIENT_CERTIFIED__G4_NOT_WIRED`

**Theorem claimed:** `True` (69/69 checks)

Exact over Q at the G3 witness (V_PS,eps, 0 < eps < 599/50, r0 = 1/5, x0 = 1, kappa = -r0/4, q0 = (p, 0, r0 sigma_std, r0, x0)): the orbit tangent ranks are SO(10) 33, SO(10)xU(1)_X 34 and SO(10)xU(1)_XxPQ 35 (nonzero integer minors 1, 4, -68 and 12 independent integer null vectors spanning the standard SM algebra, without X or PQ coefficient), so the gauge quotient has dimension 452 and the massive/transverse quotient 451; PQ is global, neither gauged nor eaten.  In the canonical chart metric the PQ tangent's component orthogonal to the gauge tangents, a, spans T35 cap G34^perp; with ker Hess = T35 (PSD) for every eps > 0 the Hessian restricted to the 452-dimensional gauge quotient is PSD with a single zero mode, the physical axion (|a|^2 = 9248/7241; S phase 7225/7241, Phi17 phase 16/7241, Sigma phase 0), and 451 positive modes equal to the positive spectrum of the Hessian; the 35 zero modes of the full Hessian are 34 eaten Goldstones (33 + 1) and the axion, with no negative mode.  At eps = 0 the only extra zero modes are Re H_6..9, one SM doublet (1,2)_{1/2}, lifted at quartic order by lambda_eff = 127/64; for eps > 0 their mass^2 is eps.

Exact over Q at the G3 witness V_PS,eps (0 < eps < 599/50, r0 = 1/5, x0 = 1, kappa = -r0/4): the orbit tangent ranks are 33 (SO(10)), 34 (SO(10) x U(1)_X) and 35 (+ PQ), with nonzero integer minors 1, 4, -68 and 12 independent integer null vectors spanning the standard SM algebra; the gauge quotient has dimension 452 (axion included) and the massive/transverse quotient 451.  PQ is global.  The physical axion is the PQ tangent's component orthogonal to the gauge tangents, |a|^2 = 9248/7241 (S phase 7225/7241, Phi17 phase 16/7241, Sigma phase 0).  On the 452-dimensional gauge quotient the Hessian is PSD with the axion as its only zero mode and 451 positive modes (the positive spectrum of the Hessian, lowest eps with multiplicity 4 for eps < r0^2/96); the 35 zero modes of the full Hessian are 34 eaten Goldstones (33 + 1) and the axion, and no mode is negative.  At eps = 0 the 4 extra zero modes are one SM doublet (1,2)_{1/2}, lifted at quartic order by lambda_eff = 127/64.  The vector-boson Gram matrix has rank 34.  Compiler binding is float64.  G4 is NOT wired: the ledger keeps G4 OPEN (under decision D3 a CLOSED G4 approves the internal candidate, so wiring G4 is the user's decision).

## Gauge quotient (exact rank certificate)

| generators | rank | minor | det M-minor | det D_u M-minor | null vectors (rank) | no X/PQ coefficient |
|---|---|---|---|---|---|---|
| SO10 | `33` | `33x33` | `1` | `1/512000000000` | `12` (`12`) | `True` |
| SO10_x_U1X | `34` | `34x34` | `4` | `1/640000000000` | `12` (`12`) | `True` |
| SO10_x_U1X_x_PQ | `35` | `35x35` | `-68` | `-17/640000000000` | `12` (`12`) | `True` |

- stabilizer = standard SM algebra: `True`;
- U(1)_X/PQ minor on (S.y, Phi17.y): `[[4, 4], [17, 0]]`, det `-68`;
- gauge quotient (axion included): `452`; massive/transverse quotient: `451` (superseded point: `449`/`448`);
- eaten Goldstones: `34` = `33` SO(10)/SM + `1` U(1)_X; PQ gauged: `False`, eaten: `False`;
- live compiler binding (float64, max residual): `0.0`.

## Physical axion

- |a|^2 = `9248/7241` M_GUT^2 (closed form `9248/7241`); |t_PQ|^2 = `8/5`;
- squared-norm composition: H10 `0`, Phi17_phase `16/7241`, Phi210 `0`, S_phase `7225/7241`, Sigma_phase `0`;
- chart components: Phi17.y = `sqrt(2)*(-272/7241)`, S.y = `sqrt(2)*(5780/7241)`;
- projection coefficients: SO10:T[0,1] `-14450/7241`, U1X `16/7241`;
- axion-angle period modulo SO(10) x U(1)_X: `2 pi/68` (explicit gauge element, angles in units of 2 pi: beta_U1X `13/17`, psi_so10 `1/2`, so10_generator `SO10:T[0,1]`, theta_PQ `1/68`); v_a^2 = `2/7241` M_GUT^2 (v_a = F_PQ/68);
- convention: theta_PQ -> exp(i theta Q_PQ) q0 with Q_PQ(Sigma126bar, H10, S, Phi17) = (-2, -2, 4, 0); the physical axion is the canonical-metric component of d/dtheta orthogonal to the gauge orbit, with kinetic term (1/2) F_PQ^2 (d theta)^2, F_PQ^2 = |a|^2.  theta = pi acts trivially on the scalar fields, but modulo the gauge group the axion angle has period 2 pi/68: S and Phi17 are SO(10) singlets, so PQ(theta) q0 = g q0 with g in SO(10) x U(1)_X needs 4 (theta - beta) and 17 beta in 2 pi Z, i.e. theta in (2 pi/68) Z, with 68 = |q_PQ(S) q_X(Phi17) - q_PQ(Phi17) q_X(S)|/gcd(q_X(S), q_X(Phi17)) the PQ charge of the gauge-invariant Phi17^4 conj(S)^17; conversely U(1)_X at beta = 26 pi/17 followed by exp(pi L_01) (L_01 fixes p and rotates the Sigma phase; H = 0) reproduces theta = pi/34.  So a = F_PQ theta has period 2 pi v_a with v_a = F_PQ/68, v_a^2 = 2 r0^2 x0^2/(16 r0^2 + 289 x0^2) = 2/7241 M_GUT^2.  The axion zero mode is exact for the renormalizable PQ-neutral benchmark potential only: PQ-violating non-renormalizable operators such as Phi17^4 conj(S)^17 (PQ charge -68, a potential in cos(a/v_a + delta)) lift it explicitly and are not included.  The conversion to f_a = v_a/N_DW needs the QCD anomaly (domain-wall) coefficient and the fermion PQ charges, which are not computed here.

## Hessian on the gauge quotient

- dimensions: W `452`, W_cap_kernel_eps_positive `1`, W_cap_kernel_tuned `5`, kernel_T35 `35`, kernel_T35_plus_D4_tuned `39`;
- eps > 0: inertia on W `451/1/0`, zero mode: the physical axion a; for 0 < eps < r0^2/96 the positive levels are eps (x`4`), 1/2400 (x`14`) and `433` above (holds: `True`);
- eps = 0: inertia on W `447/5/0` (the axion a and the 4 real doublet directions Re H_6..9 (in W: the gauge tangents vanish on the H block));
- lemma: Let K = ker Hess_q V_eps(q0) with Hess_q PSD and K = T35 (every eps > 0).  Then T35 = G34 (+) span(a) orthogonally (a is orthogonal to G34, lies in T35, and dim T35 = dim G34 + 1), so K^perp = G34^perp cap a^perp and W = G34^perp = span(a) (+) K^perp.  Hess_q is symmetric with kernel K, so K^perp = range(Hess_q) is invariant and Hess_q is positive definite on it.  Hence P_W Hess_q P_W on W is 0 on a and equals Hess_q on K^perp: PSD, with inertia (dim W - 1, 1, 0) and positive spectrum equal to the positive spectrum of Hess_q (Sylvester: identical statements hold for H_u with the metric D_c^2).

| fresh exact member | eps | inertia (+/0/-) | kernel as expected | H_u a = 0 | H_u D4 = 2 eps D4 | smallest nonzero (mult.) |
|---|---|---|---|---|---|---|
| benchmark | `0` | `447/39/0` | `True` | `True` | `True` | `1/2400` (`14`) |
| raised_O06 | `1/2500` | `451/35/0` | `True` | `True` | `True` | `1/2500` (`4`) |
| tiny_eps | `1/25000000` | `451/35/0` | `True` | `True` | `True` | `1/25000000` (`4`) |

## Zero and negative modes

- certified: `True`; unexplained zero or negative modes: `0`;
- eps > 0: `451/35/0`; ker Hess = T35 = G34 (+) span(a) orthogonally (canonical chart metric); eaten 34 (33 + 1), axion 1, negative 0;
- eps = 0: `447/39/0`; 34 eaten + 1 axion + 4 real doublet modes Re H_6..9.

## Light doublet (eps -> 0)

- directions: `H[6].x`, `H[7].x`, `H[8].x`, `H[9].x` (Re H_6..9);
- SM label: `(1,2)_{1/2}: one complex SM doublet realified (equivalently its conjugate (1,2)_{-1/2}); |Y| = 1/2` (SU(2)_L Casimir `3/4`, Y^2 `1/4`, colour singlet `True`);
- mass^2: eps (exact, every eps >= 0; units M_GUT^2); lightest with multiplicity 4 for 0 < eps < r0^2/96 = 1/2400;
- quartic lift at eps = 0: lambda_eff = `127/64` (2 - kappa^2/(4 r0^2) = 127/64 at kappa = -r0/4 (g3_sm_pati_salam_candidate_v20)).

## Vector bosons (tangent Gram matrix, up to couplings)

- rank `34`; characteristic polynomial at unit couplings: `lambda^12 (lambda - 1)^12 (lambda - 27/25)^12 (lambda - 2/25)^8 (125 lambda^2 - 72500 lambda + 28964)/125`;
- neutral block (1,1)_0 (+) X (t = g_X/g): `lambda (125*lambda**2 - (50 + 72450*t**2)*lambda + 28964*t**2)/125`; roots at t = 1: `290 - (4/25)*sqrt(3276105)`, `290 + (4/25)*sqrt(3276105)`;

| sector | real dim | Gamma eigenvalue |
|---|---|---|
| (8,1)_0 | `8` | `0` |
| (1,3)_0 | `3` | `0` |
| (3,2)_-5/6 + conj | `12` | `1` |
| (3,2)_1/6 + conj | `12` | `27/25` |
| (3,1)_2/3 + conj | `6` | `2/25` |
| (1,1)_1 + conj | `2` | `2/25` |
| (1,1)_0 | `2` | `neutral block` |

## Final acceptance test (G4, not wired)

**Required statement:** At the G3 witness q0 of V_PS,eps (0 < eps < 599/50; r0 = 1/5, x0 = 1, kappa = -r0/4) the SO(10)xU(1)_X orbit has rank 34 and the SO(10)xU(1)_XxPQ orbit rank 35 (gauge quotient 452, massive/transverse quotient 451); the Hessian has no negative mode and exactly 35 zero modes, 34 eaten Goldstones (33 SO(10)/SM + 1 U(1)_X) and 1 physical axion; restricted to the 452-dimensional gauge quotient (canonical chart metric) it is PSD with the axion as its only zero mode and 451 strictly positive modes; as eps -> 0 the only extra zero modes are the 4 real modes of one SM doublet (1,2)_{1/2}, of mass^2 eps and lifted at quartic order by lambda_eff = 127/64 > 0.

**Currently passes:** `True`; wired into the gate ledger: `False`; closes G4 by itself: `False`.

Wiring: left to the user: under decision D3 a CLOSED G4 approves the internal candidate, so this report does not wire G4 and the ledger keeps G4 OPEN.

## G4 open-scope coverage

- `True`: carry the exact gauge quotient to the accepted G3 witness (the SM Pati-Salam eps member) and recompute its ranks there: SO(10)xU(1)_X rank 34 (gauge quotient 452, axion included) and SO(10)xU(1)_XxPQ rank 35 (massive/transverse quotient 451), replacing the rank-37/38 (449/448) values of the superseded p+delta point
- `True`: classify all remaining Hessian zero and negative modes at that witness, including the axion/PQ direction and the eps -> 0 tuned light doublet (4 real modes)
- `True`: routed from G3 by decision D5 (zero_modes_and_ranks_at_witness): Zero-mode classification at the witness belongs to G4: the recomputed ranks 34/35 (SO(10) x U(1)_X rank 34, gauge quotient 452 with the axion included; SO(10) x U(1)_X x U(1)_PQ rank 35, massive/transverse quotient 451, i.e. quotients 452/451), the axion/PQ direction and the eps -> 0 tuned light doublet (4 real modes); it is resolved only when G4 is CLOSED.

## Checks

| check | passed |
|---|---|
| `axion__T35_cap_gauge_complement_is_one_dimensional` | `True` |
| `axion__axion_composition_S_7225_Phi17_16_over_7241_Sigma_Phi_H_0` | `True` |
| `axion__axion_is_pure_S_and_Phi17_phase` | `True` |
| `axion__axion_lies_in_orbit_tangent_span_T35` | `True` |
| `axion__axion_nonzero` | `True` |
| `axion__axion_norm_squared_9248_over_7241` | `True` |
| `axion__axion_norm_squared_matches_closed_form` | `True` |
| `axion__axion_not_in_gauge_span` | `True` |
| `axion__axion_orthogonal_to_all_46_gauge_tangents_exact` | `True` |
| `axion__axion_period_modulo_gauge_2pi_over_68` | `True` |
| `axion__gauge_gram_on_34_pivot_tangents_nonsingular` | `True` |
| `binding__float64_restricted_spectrum_and_kinetic_metric_consistent` | `True` |
| `binding__live_compiler_tangents_equal_D_M_float64` | `True` |
| `chart__chart_blocks_use_canonical_conventions` | `True` |
| `chart__metric_is_1_on_Phi_and_2_on_complex_blocks` | `True` |
| `chart__vacuum_norm_squared_1_plus_4r0sq_plus_2x0sq` | `True` |
| `chart__vacuum_orthogonal_to_all_47_orbit_tangents_exact` | `True` |
| `doublet__doublet_SU2L_casimir_3_over_4_exact` | `True` |
| `doublet__doublet_Y_is_complex_structure_commuting_with_SU2L` | `True` |
| `doublet__doublet_colour_singlet_exact` | `True` |
| `doublet__doublet_directions_are_Re_H6_to_H9` | `True` |
| `doublet__doublet_hypercharge_squared_1_over_4_exact` | `True` |
| `doublet__doublet_is_zero_mode_of_tuned_hessian_exact` | `True` |
| `doublet__doublet_label_consistent_with_sigma_audit_weak_block` | `True` |
| `doublet__doublet_mass_squared_eps_committed_and_fresh` | `True` |
| `doublet__doublet_quartic_lift_127_over_64_committed_and_fresh` | `True` |
| `doublet__doublet_span_invariant_under_SM_algebra_exact` | `True` |
| `fresh__fresh_doublet_exact_eigenvectors_mass_squared_eps_at_both_members` | `True` |
| `fresh__fresh_eps_r0sq_over_100_inertia_451_35_0_kernel_T35_annihilates_axion` | `True` |
| `fresh__fresh_eps_r0sq_over_10e6_inertia_451_35_0_kernel_T35_annihilates_axion` | `True` |
| `fresh__fresh_second_level_r0sq_over_96_multiplicity_14_at_r0sq_over_100` | `True` |
| `fresh__fresh_tuned_eps_0_inertia_447_39_0_kernel_T35_plus_doublet` | `True` |
| `gauge__PQ_global_not_gauged_and_not_in_gauge_span` | `True` |
| `gauge__SO10_12_independent_exact_null_vectors` | `True` |
| `gauge__SO10_minor_determinant_1` | `True` |
| `gauge__SO10_rank_33_nonzero_33x33_integer_minor` | `True` |
| `gauge__SO10_x_U1X_12_independent_exact_null_vectors` | `True` |
| `gauge__SO10_x_U1X_minor_determinant_4` | `True` |
| `gauge__SO10_x_U1X_rank_34_nonzero_34x34_integer_minor` | `True` |
| `gauge__SO10_x_U1X_x_PQ_12_independent_exact_null_vectors` | `True` |
| `gauge__SO10_x_U1X_x_PQ_minor_determinant_-68` | `True` |
| `gauge__SO10_x_U1X_x_PQ_rank_35_nonzero_35x35_integer_minor` | `True` |
| `gauge__U1X_PQ_phase_minor_on_S_y_Phi17_y_is_minus_68` | `True` |
| `gauge__gauge_quotient_dimension_452` | `True` |
| `gauge__massive_transverse_quotient_dimension_451` | `True` |
| `gauge__null_vectors_have_no_X_or_PQ_coefficient` | `True` |
| `gauge__phase_columns_rebuilt_from_declared_X_and_PQ_charges` | `True` |
| `gauge__row_scaling_D_invertible_at_witness_r0_x0_positive` | `True` |
| `gauge__so10_stabilizer_equals_standard_SM_algebra` | `True` |
| `gauge__tangent_matrix_equals_equality_module_construction` | `True` |
| `gauge__tangent_matrix_is_486x47_integer` | `True` |
| `gauge__tangents_vanish_on_H_block` | `True` |
| `premise_candidate_report` | `True` |
| `premise_contract_report` | `True` |
| `premise_equality_report` | `True` |
| `premise_hessian_report` | `True` |
| `premise_sigma_audit_report` | `True` |
| `restricted__gauge_complement_W_has_dimension_452` | `True` |
| `restricted__restricted_hessian_inputs_PSD_and_kernel_T35_for_every_eps_positive` | `True` |
| `restricted__restricted_hessian_psd_one_zero_mode_axion_451_positive` | `True` |
| `restricted__restricted_spectrum_is_zero_plus_positive_hessian_spectrum` | `True` |
| `restricted__tuned_limit_W_inertia_447_5_0_axion_plus_doublet` | `True` |
| `vectors__SM_sectors_decompose_so10_with_expected_dimensions` | `True` |
| `vectors__X_couples_only_to_the_neutral_sector` | `True` |
| `vectors__colour_casimir_normalised_on_vector_colour_block` | `True` |
| `vectors__gamma_scalar_on_every_charged_sector_with_expected_value` | `True` |
| `vectors__massless_vectors_are_the_12_SM_gauge_bosons` | `True` |
| `vectors__neutral_block_polynomial_exact` | `True` |
| `vectors__vector_gram_rank_34` | `True` |

## Scope

**proved_exactly**

- the orbit tangent ranks 33/34/35 at q0 (both halves of the rank certificate, for all r0, x0 > 0 since D is invertible), the gauge quotient 452 and the massive/transverse quotient 451
- the physical axion a = t_PQ - proj_G34 t_PQ, |a|^2 = 9248/7241 and its squared-norm composition, and the axion-angle period 2 pi/68 modulo SO(10) x U(1)_X (v_a = F_PQ/68, v_a^2 = 2/7241), at r0 = 1/5, x0 = 1
- the Hessian of V_PS,eps restricted to the gauge quotient: PSD, one zero mode (a), 451 positive modes equal to the positive spectrum of the Hessian, for every eps in the window (inputs: the Hessian report's L2 plus fresh exact certificates at eps = r0^2/100 and r0^2/10^6)
- the zero-mode classification 35 = 34 eaten (33 + 1) + 1 axion, no negative mode; at eps = 0 the 4 extra modes Re H_6..9 form one SM doublet (1,2)_{1/2}
- the vector-boson tangent Gram matrix: rank 34 and its eigenvalues by SM sector

**bound_from_committed_reports**

- G3_SM_PATI_SALAM_EXACT_HESSIAN_V20.json (eps family L1/L2, doublet section, tuned 447/39)
- G3_SM_PATI_SALAM_EQUALITY_SET_V20.json (tangent ranks, charges, PQ status)
- G3_SM_PATI_SALAM_CANDIDATE_V20.json (lambda_eff = 127/64, SM vacuum)
- G3_SIGMA_HYPERCHARGE_AUDIT_V20.json (standard SM pair (p, z1..z5), weak-block |Y| = 1/2)
- GAUGED_U1X_SCALAR_CONTRACT_V20.json (gauge SO(10) x U(1)_X, accidental global U(1)_PQ)

**float64_evidence_only**

- the compiler = exact-operator identity of the Hessian end to end (inherited from the exact Hessian report: per-unit and assembled float64 bindings)
- the entrywise binding of D M to the live chart tangents
- the chart kinetic normalisation residuals and the float64 restricted spectrum

**not_covered**

- the physical hierarchy point (r0 = M_I/M_GUT, canonical Phi17 scale x0 ~ 10.08): only r0 = 1/5, x0 = 1 is certified
- loop corrections (Coleman-Weinberg, running), the axion's QCD anomaly mass and the conversion of v_a to the conventional f_a = v_a/N_DW (fermion PQ charges and the domain-wall number are not computed)
- PQ-violating non-renormalizable operators (e.g. the dimension-21 axion-quality term Phi17^4 conj(S)^17 / M_Pl^17, SO(10) x U(1)_X-invariant with PQ charge -68), which lift the axion explicitly; the axion zero mode is exact for the renormalizable PQ-neutral benchmark potential only
- the G6 positivity/EWSB caveats: H = 0 on the witness, no electroweak breaking, sub-M_I coloured 126bar states; the complete positive spectrum with SM provenance is a G6 task
- gauge coupling values: the vector-boson matrix is given up to g and g_X
- wiring G4 into the gate ledger (under decision D3 a CLOSED G4 approves the internal candidate, so wiring is the user's decision)

Runtime: 12 s.
