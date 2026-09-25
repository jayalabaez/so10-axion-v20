# G3 SM Pati-Salam candidate -- v20

**Status:** `SM_PATI_SALAM_G3_CANDIDATE__EXACT_GLOBAL_MINIMUM_OF_BENCHMARK_POTENTIAL__SM_UNBROKEN__G3_OPEN`

The 27-parameter member of the declared exact-X potential obtained from the historical p-branch map by swapping the 2772bar/4125 self-projector weights, setting O05 = (1/8)(4 - 2 r0^2) and adding kappa_H = -r0/4 with O06 = 2|kappa| r0 has the vacuum (p, r0 sigma_std, 0, r0, x0), sigma_std = z1^z2^z3^z4^z5, whose unbroken algebra is exactly SU(3)_c x SU(2)_L x U(1)_Y (SO(10) -> Pati-Salam at M_GUT -> SM at r0 M_GUT). An adapted exact SOS identity gives V >= -1 - r0^4/8 - r0^4 - x0^4/32 on the whole field space and the vacuum attains it, so it is an exact global minimum of this benchmark potential, exactly stationary with PSD Hessian, for every r0 > 0 (checked on the live compiler at r0 = 1/5, 1/100, 1/1000 and M_I/M_GUT with x0 = 1: symmetry rank 35, kernel = symmetry tangents plus the 4 modes of one tuned light doublet, lightest massive mode r0^2/96). Physics caveats: one 10_H doublet is light (exactly massless at tree level) only because O46_1 = -(3/5) O46_54 and O06 = 2|kappa| r0 are tuned, while the 10_H colour triplets are at M_GUT for generic O46 couplings (doublet-triplet splitting is tuned, not automatic); the intermediate scale is itself a cancellation of O(1) couplings to ~(M_I/M_GUT)^2; 126bar colour triplets and sextets and a doubly charged singlet lie below M_I; only the breaking route matches the manuscript's Pati-Salam RG anchor, not its field content (no light (15,2,2), 1HDM instead of 2HDM), so the GeV masses at r0 = M_I/M_GUT are illustrative; and the light doublet's tree-level quartic is 127/64 at the benchmark (m_h ~ 195 GeV under conditional SM running), too large; the certified family kappa^2 < 8 r0^2 reaches lambda_eff -> 0+, near the measured Higgs mass, but tree-level global minimality forbids the slightly negative SM value at M_t = 173.34 GeV. Uniqueness of the minimum modulo symmetry, electroweak breaking and a realistic Yukawa sector remain open; G3 is not closed and the model is neither validated nor excluded.

## Candidate

Vacuum `(Phi, Sigma, H, S, Phi17) = (p, r0 sigma_std, 0, r0, x0)`, `sigma_std = z1^z2^z3^z4^z5` (Y = 0).

| parameter | historical (h=0) | candidate |
|---|---|---|
| `lambda::O05_B01_126bar_norm` | 47/96 | 49/100 |
| `lambda::O06_B01_Hdag_H_norm` | 0 | 1/50 |
| `lambda::O27_B03_126bar_self_projectors` | 17/128 | 1/8 |
| `lambda::O27_B04_126bar_self_projectors` | 1/8 | 17/128 |
| `re::O12_B01_Hdag_Hdag_pair` | 0 | -1/20 |

- nonzero parameters: `27` of 51; H-linear portals zero: `True`
- unbroken algebra: SU(3)xSU(2)xU(1)_Y: standard SM embedding (dim 12, centre ~ ['Y_standard']); Phi = p alone: dim 21 (Pati-Salam)

## Exact certificate

- identity: V = [-2|Phi|^2 + Q(Phi)] + (1/8)[||(M_Phi - 2)Sigma||^2 + ||C_Phi Sigma||^2 + W'(Sigma) - 2 r0^2 N_Sigma] + [2 N_H^2 + 2|k| r0 N_H + 2k Re(conj(H.H) conj(S)) + (|S|^2 - r0^2)^2 - r0^4] + ||H wedge Phi||^2 + (1/32)(|Phi17|^2 - x0^2)^2 - x0^4/32,  W' = 2 I54 + 2 I1050bar + I2772bar + (17/16) I4125
- sigma_std projector fractions: `{'1050bar': '0', '2772bar': '1', '4125': '0', '54': '0'}`; (M_p - 2) sigma = 0: `True`; C_p sigma = 0: `True`
- lower bound V0 = -1 - r0^4/8 - r0^4 - x0^4/32 (= `-20661/20000` at r0 = 1/5, x0 = 1), attained at the vacuum
- BFB: `True`; global minimum: `True`; exact stationarity: `True`; quartic part >= |q|^4/167

## Compiler (float64)

| r0 | max abs grad | V - V0 | sym. rank | n_neg | n_zero | min massive / r0^2 | abs. dev. from r0^2/96 | all-massive n_zero |
|---|---|---|---|---|---|---|---|---|
| 1/5 | 4.92e-14 | -3.11e-15 | 35 | 0 | 4 | 0.01041666667 | 6.16e-14 | 0 |
| 1/100 | 1.89e-15 | -8.88e-16 | 35 | 0 | 4 | 0.01041666606 | 6.04e-14 | 0 |
| 1/1000 | 1.77e-15 | -4.44e-16 | 35 | 0 | 4 | 0.01041660493 | 6.17e-14 | 0 |
| M_I/M_GUT | 1.78e-15 | -8.88e-16 | 35 | 0 | 4 | 0.01040178039 | 6.03e-14 | 0 |

n_zero counts the 4 real modes of the tuned light doublet: the Hessian kernel is the 35 symmetry tangents plus that doublet, and exactly the symmetry tangents only when O06 is raised (last column). All benchmarks use x0 = 1.

### Spectrum at r0 = 1/5 (lightest clusters)

The m^2/r0^2 column is a scaling only for the r0-dependent states (m^2 < 5 r0^2 below). The Phi17 radial mode (0.125 = x0^2/8) and every state from m^2 ~ 0.45 up are GUT-scale and do not scale with r0.

| m^2 | m^2/r0^2 | real dim | SM content | fields |
|---|---|---|---|---|
| 2.7157437e-16 | 6.7893593e-15 | 4 | (1,2)_\|Y\|=1/2: 4 | H10 1.00 |
| 0.00041666667 | 0.010416667 | 14 | (1,1)_\|Y\|=2: 2, (6,1)_\|Y\|=4/3: 12 | Sigma126bar 1.00 |
| 0.002358027 | 0.058950676 | 6 | (3,1)_\|Y\|=1/3: 6 | Phi210 0.00, Sigma126bar 1.00 |
| 0.0025694444 | 0.064236111 | 18 | (3,1)_\|Y\|=4/3: 6, (6,1)_\|Y\|=1/3: 12 | Sigma126bar 1.00 |
| 0.004202381 | 0.10505952 | 12 | (6,1)_\|Y\|=2/3: 12 | Sigma126bar 1.00 |
| 0.02 | 0.5 | 1 | (1,1)_\|Y\|=0: 1 | Sigma126bar 1.00 |
| 0.04 | 1 | 4 | (1,2)_\|Y\|=1/2: 4 | H10 1.00 |
| 0.125 | 3.125 | 1 | (1,1)_\|Y\|=0: 1 | Phi17 1.00 |
| 0.16 | 4 | 1 | (1,1)_\|Y\|=0: 1 | S 1.00 |
| 0.45238298 | 11.309575 | 4 | (1,2)_\|Y\|=1/2: 4 | Phi210 0.04, Sigma126bar 0.96 |
| 0.5 | 12.5 | 12 | (3,2)_\|Y\|=1/6: 12 | Phi210 0.11, Sigma126bar 0.89 |
| 0.50041667 | 12.510417 | 44 | (3,2)_\|Y\|=7/6: 12, (8,2)_\|Y\|=1/2: 32 | Sigma126bar 1.00 |
| 0.50256944 | 12.564236 | 48 | (1,2)_\|Y\|=1/2: 4, (3,2)_\|Y\|=7/6: 12, (8,2)_\|Y\|=1/2: 32 | Sigma126bar 1.00 |
| 0.50420238 | 12.60506 | 12 | (3,2)_\|Y\|=1/6: 12 | Sigma126bar 1.00 |
| 0.59956326 | 14.989082 | 6 | (3,1)_\|Y\|=1/3: 6 | Phi210 0.06, Sigma126bar 0.94 |
| 0.62756944 | 15.689236 | 6 | (3,1)_\|Y\|=1/3: 6 | Sigma126bar 1.00 |
| 0.88888889 | 22.222222 | 75 | (1,3)_\|Y\|=0: 3, (3,1)_\|Y\|=5/3: 6, (3,3)_\|Y\|=2/3: 18, (8,1)_\|Y\|=0: 8, (8,1)_\|Y\|=1: 16, (8,3)_\|Y\|=0: 24 | Phi210 1.00 |
| 0.96671687 | 24.167922 | 6 | (3,1)_\|Y\|=2/3: 6 | Phi210 1.00 |
| 1 | 25 | 6 | (3,1)_\|Y\|=1/3: 6 | H10 1.00 |
| 1.0088889 | 25.222222 | 2 | (1,1)_\|Y\|=1: 2 | Phi210 1.00 |
| 1.04 | 26 | 6 | (3,1)_\|Y\|=1/3: 6 | H10 1.00 |
| 1.0457176 | 26.14294 | 6 | (3,1)_\|Y\|=1/3: 6 | Phi210 0.94, Sigma126bar 0.06 |
| 1.1073417 | 27.683544 | 1 | (1,1)_\|Y\|=0: 1 | Phi210 1.00 |
| 1.5 | 37.5 | 64 | (1,2)_\|Y\|=3/2: 4, (3,2)_\|Y\|=5/6: 12, (6,2)_\|Y\|=1/6: 24, (6,2)_\|Y\|=5/6: 24 | Phi210 1.00 |

### Light states at r0 = M_I/M_GUT (illustrative GeV)

Labelled by SM-isotypic component (exact-integer Casimirs), then diagonalised. GeV values use the anchor's M_I, which this content does not reproduce (see RG-anchor consistency).

| SM content | m^2/r0^2 | m/M_I | m [GeV] | fields |
|---|---|---|---|---|
| (1,2)_\|Y\|=1/2: 4 | -1.7593e-16 | 0 | 0 | H10 1.00 |
| (1,1)_\|Y\|=2: 2 | 0.0104019 | 0.102 | 6.439e+10 | Sigma126bar 1.00 |
| (6,1)_\|Y\|=4/3: 12 | 0.0104019 | 0.102 | 6.439e+10 | Sigma126bar 1.00 |
| (3,1)_\|Y\|=1/3: 6 | 0.059013 | 0.2429 | 1.534e+11 | Sigma126bar 1.00 |
| (3,1)_\|Y\|=4/3: 6 | 0.0642213 | 0.2534 | 1.6e+11 | Sigma126bar 1.00 |
| (6,1)_\|Y\|=1/3: 12 | 0.0642214 | 0.2534 | 1.6e+11 | Sigma126bar 1.00 |
| (6,1)_\|Y\|=2/3: 12 | 0.105045 | 0.3241 | 2.046e+11 | Sigma126bar 1.00 |
| (1,1)_\|Y\|=0: 1 | 0.499985 | 0.7071 | 4.465e+11 | Sigma126bar 1.00 |
| (1,2)_\|Y\|=1/2: 4 | 1 | 1 | 6.314e+11 | H10 1.00 |
| (1,1)_\|Y\|=0: 1 | 4 | 2 | 1.263e+12 | S 1.00 |

### 10_H at r0 = 1/5

- real-block eigenvalues: `{'colour_x': [1.0], 'colour_y': [1.04], 'weak_x': [-3.46944695195e-18], 'weak_y': [0.04]}`
- doublet-triplet splitting (10_H only; tuned): At the tuned ratio O46_1 : O46_54 = 3/5 : -1 the Phi-H quartics combine into ||H wedge Phi||^2 = H^dag diag(1_6, 0_4) H, which gives the 10_H colour triplets M_GUT^2 and the doublets no Phi-induced mass; the remaining doublet mass O06 - 2|kappa| r0 is tuned to zero. Neither relation is enforced by a symmetry: adding eps > 0 to O46_1 adds eps |Phi|^2 N_H >= 0, keeps V >= V0 with the same global minimum, and gives the doublets eps M_GUT^2. Doublet-triplet splitting is therefore tuned, not automatic.
- Phi-induced doublet m^2 = (O46_1 + (3/5) O46_54) |Phi|^2 = `0`; triplet m^2 = (O46_1 - (2/5) O46_54) |Phi|^2 = `1`
- tuned relations: O46_1 = -(3/5) O46_54 (doublet Phi-induced mass zero; precision ~ (m_h/M_GUT)^2); O06 = 2|kappa| r0 (doublet B-term cancelled; precision ~ (m_h/M_I)^2); O05 = (1/8)(4 - 2 r0^2) against the Phi-induced O14/O44 masses on the (10bar,1,3) (1/2 - 1 + 1/2 - r0^2/4 at |Phi| = 1): the intermediate scale itself is a cancellation of O(1) couplings to precision ~ (M_I/M_GUT)^2 ~ 4e-9
- light doublet weight in the 5 (span z4, z5): `0.5` (equal 5/5bar mixture, tan beta = 1 structure)

## Illustrative hierarchy and RG-anchor consistency

- ILLUSTRATIVE: M_GUT and M_I are the anchor's (gauged_u1x_g2_derivative_audit_v20), and this candidate's field content does not reproduce the anchor (rg_anchor_consistency); the GeV numbers are not predictions
- units: chart unit |Phi| = 1 identified with the RG M_GUT and r0 = |Sigma|/|Phi| with M_I/M_GUT (a vev ratio), without gauge-coupling or group-theory factors
- Phi17: Every compiler benchmark, including 'M_I/M_GUT', keeps x0 = 1 (Phi17 at M_GUT), not the canonical physical_hierarchy_state value Phi17 = 1e17 GeV (x0 ~ 10.08). The exact identity contains Phi17 only in (1/32)(|Phi17|^2 - x0^2)^2 and the compiler Phi17 block is decoupled (Phi17_block), so x0 changes only the Phi17 radial mass x0^2/8 M_GUT^2 and V0; the exact certificate holds for every x0 > 0.
- anchor content: below M_I SM gauge + 3 families + 2 Higgs doublets (2HDM); M_I to M_GUT PS gauge + 3 families + complex (1,2,2) + complex (10bar,1,3) + complex (15,2,2)
- candidate content: below M_I SM gauge + 3 families + ONE light doublet (1HDM; the partner is at exactly M_I) + six gauge-charged complex (10bar,1,3) remnants between 0.10 M_I and 0.33 M_I (sub_M_I_thresholds) and the neutral Sigma radial mode at M_I/sqrt(2); M_I to M_GUT PS gauge + 3 families + complex (1,2,2) (10_H doublets) + complex (10bar,1,3); the 126bar (15,2,2) sits at m^2 = 0.45-0.50 M_GUT^2 at r0 = 1/5 and 0.5 M_GUT^2 as r0 -> 0 (~0.7 M_GUT), forced by (1/8)||(M_Phi - 2)Sigma||^2 with M_p = 0 on it
- betas (U(1)_Y, SU(2)_L, SU(3)_c) below M_I: anchor `['21/5', '-3', '-7']`, candidate `['41/10', '-19/6', '-7']`; (SU(4), SU(2)_L, SU(2)_R) above M_I: anchor `['-7/3', '2', '26/3']`, candidate `['-23/3', '-3', '11/3']`

| one-loop chain | M_I [GeV] | M_GUT [GeV] | alpha_GUT^-1 | M_I/M_GUT |
|---|---|---|---|---|
| anchor_content_local_chain | 6.314e+11 | 9.918e+15 | 37.31 | 6.366e-05 |
| anchor_repository_two_loop_thresholds_v20 | 6.314e+11 | 9.918e+15 | 37.31 | 6.366e-05 |
| candidate_PS_content_with_1HDM_below_M_I | 5.791e+11 | 1.1e+16 | 45.65 | 5.264e-05 |
| candidate_PS_content_with_2HDM_below_M_I | 1.056e+12 | 5.353e+15 | 44.71 | 0.0001972 |
| candidate_content_with_1HDM_and_sub_M_I_remnants | 7.775e+10 | 1.994e+16 | 45.88 | 3.898e-06 |

- Indicative: one loop, tree-level threshold masses at their physical-benchmark ratios m/M_I (r0-independent at leading order), no matching corrections or two-loop shifts, and the chart unit |Phi| = 1 identified with M_GUT and r0 with M_I/M_GUT without gauge-coupling factors.
- Only the breaking route matches the anchor. Its beta coefficients assume a light (15,2,2) above M_I and a 2HDM below M_I; this candidate provides neither and adds sub-M_I coloured scalars, so the anchor's M_I and M_GUT (and r0 = M_I/M_GUT) are borrowed, not reproduced.

## Light-doublet quartic (tree level)

- exact: lambda_eff = 2 - kappa^2/(4 r0^2) = `127/64`; compiler at r0 = 1/5: lambda_direct `2`, lambda_eff `1.984375`
- V >= V0 with the doublet exactly massless implies V_eff(h) = V0 + lambda_eff (h^dag h)^2 + ... >= V0, so lambda_eff >= 0 at tree level for every member of this family
- conditional two-loop SM running from M_I = `6.314e+11` GeV: lambda(M_I) = 127/64 -> m_h `195` GeV; SM needs lambda(M_I) = `-0.008539`. Conditional: assumes pure SM running below M_I and the anchor's M_I. The candidate has sub-M_I coloured scalars, a tan beta = 1 light doublet, and a field content that does not reproduce the anchor's M_I.

## Numerical global search

- fast SOS evaluator vs compiler: max relative value difference `6.36e-14`
- lowest gap V - V0 found by any method: `-2.89e-15`

| competitor (r0 = 1/5) | compiler gap | exact gap | local min. from it: final gap | on SM orbit |
|---|---|---|---|---|
| F\|Sigma=0 | 0.253931 | - | 7.84e-14 | True |
| F\|delta_R | 0.253867 | - | 3.04e-14 | True |
| F\|flipped | 0.253931 | - | 1.73e-13 | True |
| F\|sigma_std | 0.253931 | - | 2.94e-13 | True |
| a\|sigma_std | 0.129232 | - | 4.95e-14 | True |
| omega\|sigma_std | 0.24601 | - | 1.29e-13 | True |
| p\|Sigma=0 | 0.0002 | 1/5000 | 3.82e-12 | True |
| p\|delta_R | 4.08163e-06 | 1/245000 | 4.91e-14 | True |
| p\|flipped | -2.88658e-15 | 0 | 6.22e-15 | True |
| p\|historical_global_witness | 6.06061e-06 | - | 3.6e-14 | True |

- random starts (r0=1/20): 3; lowest final gap `1.75e-13`; all on SM vacuum orbit: `True`
- random starts (r0=1/5): 10; lowest final gap `1.53e-14`; all on SM vacuum orbit: `True`
- quartic part on the unit sphere: lowest `0.00599059` >= exact bound 1/167: `True`
- equality set at Phi = p: ker(M_p - 2) n ker(C_p) has complex dimension `30` (contains sigma_std and delta_R); pure-spinor minima in it all SM-type: `True`
- V_Phi minimizations all at -1 with a 21-dimensional (Pati-Salam) stabilizer: `True`

## Flags

- bfb_certified: `True`
- breaking_route_matches_rg_anchor: `True`
- candidate_is_sm_vacuum: `True`
- coloured_scalars_only_at_M_GUT: `False`
- doublet_triplet_splitting_natural: `False`
- electroweak_symmetry_breaking_realized: `False`
- equality_set_unique_modulo_symmetry_certified: `False`
- exactly_stationary: `True`
- g3_closed: `False`
- global_minimum_certified: `True`
- hessian_kernel_count_is_float64: `True`
- hessian_kernel_is_symmetry_when_O06_raised: `True`
- hessian_psd_exact: `True`
- hessian_psd_kernel_is_symmetry: `False`
- hessian_psd_kernel_is_symmetry_plus_tuned_light_doublet: `True`
- higgs_mass_compatible: `False`
- physical_benchmark_uses_canonical_phi17_scale: `False`
- realistic_yukawa_sector: `False`
- rg_anchor_field_content_reproduced: `False`
- target_unbroken_algebra_is_standard_model: `True`
- whole_model_excluded: `False`
- whole_model_validated: `False`

Flag notes:

- breaking_route_matches_rg_anchor: chain topology SO(10) -> PS -> SM only; not the anchor's field content
- coloured_scalars_only_at_M_GUT: False: only the 10_H triplets are at M_GUT; 126bar (10bar,1,3) remnants (6,1)_4/3, (3,1)_1/3, (3,1)_4/3, (6,1)_1/3, (6,1)_2/3 lie below M_I
- doublet_triplet_splitting_natural: False: the 10_H splitting needs O46_1 = -(3/5) O46_54 (to ~ (m_h/M_GUT)^2) and O06 = 2|kappa| r0 (to ~ (m_h/M_I)^2); no symmetry enforces either
- exactly_stationary: follows from global minimality; the exact slice gradient also vanishes identically
- global_minimum_certified: exact: adapted SOS27 lower bound attained at the vacuum (repository source-bound recouplings plus new exact sigma_std pieces); uniqueness of the minimum modulo symmetry is not certified
- hessian_psd_kernel_is_symmetry: False by its literal meaning: at every benchmark the PSD Hessian's kernel is the 35 symmetry tangents (SO(10)/SM + U(1)_X + PQ) PLUS the 4 real modes of the deliberately tuned light doublet (O06 = 2|kappa| r0); see hessian_psd_kernel_is_symmetry_plus_tuned_light_doublet. Raising O06 by r0^2/100 leaves exactly the 35 symmetry tangents (hessian_kernel_is_symmetry_when_O06_raised). Kernel counts are float64.
- higgs_mass_compatible: False at the benchmark (a benchmark-only flag): tree-level lambda_eff = 127/64 at kappa = -r0/4 (m_h ~ 195 GeV under conditional SM running). The certified family kappa^2 < 8 r0^2 spans lambda_eff in (0, 2], and lambda_eff -> 0+ gives m_h within a few GeV of the measured value (lambda(M_I) = 0: m_h ~ 126.2 GeV tree, 127.7 GeV Buttazzo-scaled, vs 125.20 GeV). The remaining tension is lambda_eff >= 0 (tree-level global minimality) versus the SM-required lambda(M_I) = -0.0085 at M_t = 173.34 GeV, whose sign is M_t-dependent at about 2 sigma
- physical_benchmark_uses_canonical_phi17_scale: False: x0 = 1 at every benchmark (canonical x0 ~ 10.08)
- rg_anchor_field_content_reproduced: False: anchor betas assume a light (15,2,2) above M_I and a 2HDM below; the candidate has neither and has sub-M_I coloured scalars (rg_anchor_consistency)
- target_unbroken_algebra_is_standard_model: exact integer stabilizer of (p, sigma_std); gated by the audit passing (fail-closed), like every other positive flag

## Open

- uniqueness of the equality set {V = V0} modulo symmetry (numerical evidence only)
- exact (non-float) Hessian kernel/rank certificate
- electroweak symmetry breaking: H = 0 here, one doublet is tuned massless at tree level
- doublet-triplet splitting is tuned, not automatic: O46_1 = -(3/5) O46_54 (precision ~ (m_h/M_GUT)^2 ~ 2e-28) and O06 = 2|kappa| r0 (precision ~ (m_h/M_I)^2 ~ 4e-20); their radiative stability is not addressed
- light 126bar coloured states below M_I: (3,1)_1/3 at ~0.24 M_I (proton-decay mediator quantum numbers, coupled to 16.16 by the 126bar Yukawa that Majorana nu_R masses need), (6,1)_4/3 and (1,1)_2 at M_I/sqrt(96), (3,1)_4/3 + (6,1)_1/3 at ~0.25 M_I, (6,1)_2/3 at ~0.32 M_I; their proton-decay and RG/unification consequences are not analysed
- RG consistency: the anchor's M_I, M_GUT assume a light (15,2,2) above M_I and a 2HDM below; this candidate has the (15,2,2) at ~0.7 M_GUT and a 1HDM, and re-solving the one-loop chain with its content moves M_I and M_GUT (rg_anchor_consistency)
- Higgs mass: the benchmark's tree-level lambda_eff = 127/64 at M_I is too large (m_h ~ 195 GeV under conditional SM running); the certified family kappa^2 < 8 r0^2 reaches lambda_eff -> 0+, near the measured Higgs mass (m_h ~ 126 GeV at lambda(M_I) = 0), but tree-level global minimality forbids the slightly negative SM value lambda(M_I) = -0.0085 at M_t = 173.34 GeV (sign M_t-dependent at ~2 sigma)
- intermediate scale: O05 = (1/8)(4 - 2 r0^2) cancels the Phi-induced O14/O44 (10bar,1,3) mass to precision ~ (M_I/M_GUT)^2 ~ 4e-9 at the anchor; its radiative stability is not addressed
- light doublet is an equal 5/5bar mixture (tan beta = 1 structure): with 10_H-only Yukawas m_t = m_b at matching
- realistic Yukawa sector: the H-linear portals O15, O38, O45, O28 vanish
- radiative stability of the M_I/M_GUT hierarchy
