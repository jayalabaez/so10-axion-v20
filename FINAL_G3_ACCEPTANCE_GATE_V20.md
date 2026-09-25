# Final G3 acceptance gate — v20

## State

**State:** `PASS` (`G3_closed`: `True`, `n_failed`: `0`)

## Closing track

- closing track: `sm_pati_salam`
- closure routes: `['sm_pati_salam']`; diagnostic tracks: `['chiral_H_SU5_Delta']`
- rule: G3 closes only if the sm_pati_salam track closes (every SM-track integrity, science and release criterion True) and every artifact-integrity check of both tracks passes; the chiral_H_SU5_Delta track is integrity-checked but can never close G3 (decision D1)

## Verdict

G3 is verified on the SM Pati-Salam track, the only closure route of this gate. G3 closed on the SM Pati-Salam benchmark family: the exact SM-preserving global vacuum of the declared exact-X potential's 27-parameter benchmark with the light-doublet deformation eps > 0, unique modulo SO(10) x U(1)_X x accidental U(1)_PQ; tuned DT/M_I relations; G4 OPEN, G6-G8 blocked; caveats routed downstream; internal candidate withheld; whole model neither validated nor excluded. Decisive theorem: For every 486-real field q, V_PS,eps(q)-V_PS,eps(q0)>=0; equality holds exactly on the SO(10)xU(1)_XxPQ orbit of q0. The G3 witness is the light-but-massive doublet member V_PS,eps = V_PS + eps N_H (O06 = 2|kappa| r0 + eps, 0 < eps < 599/50) at r0 = 1/5, x0 = 1, kappa = -r0/4: its exact Hessian at q0 = (p, 0, r0 sigma_std, r0, x0) is PSD with rank 451 and nullity 35 and kernel exactly the symmetry-orbit tangent space; the tuned eps = 0 point (447/39) is not the witness. Proof inputs: 6 cited classical theorems and 6 hand-argued elementary steps, accepted as G3-grade inputs under decision D6 and pinned by an allowlist. Model-level caveats are routed downstream and G3 keeps only disclosures: sub-M_I coloured states and positivity (no EWSB) go to G6; RG-anchor content and the Higgs quartic go to G7; Yukawas and proton-decay mediators go to G8; zero-mode classification and the recomputed ranks (34 gauge -> 452, 35 -> 451) go to G4; the naturalness of the tunings (DT splitting, O05, M_I) lies outside G1-G8. The SU(5)+Delta chiral-H track is an integrity-checked diagnostic that can never close G3: its Delta_R is the T3R=0, Y=-1 member of the 126bar triplet, so it is not a Standard-Model vacuum (g3_sigma_hypercharge_audit_v20); its exact results (the 448/38 Hessian, the fixed-F gap, the pure-Delta gap 1/5000, the corrected fixed-endpoint theorem) remain valid statements about that point.

## Decisive theorem

For every 486-real field q, V_PS,eps(q)-V_PS,eps(q0)>=0; equality holds exactly on the SO(10)xU(1)_XxPQ orbit of q0.

## Closure scope

G3 closed on the SM Pati-Salam benchmark family: the exact SM-preserving global vacuum of the declared exact-X potential's 27-parameter benchmark with the light-doublet deformation eps > 0, unique modulo SO(10) x U(1)_X x accidental U(1)_PQ; tuned DT/M_I relations; G4 OPEN, G6-G8 blocked; caveats routed downstream; internal candidate withheld; whole model neither validated nor excluded.

## Witness

The G3 witness is the light-but-massive doublet member V_PS,eps = V_PS + eps N_H (O06 = 2|kappa| r0 + eps, 0 < eps < 599/50) at r0 = 1/5, x0 = 1, kappa = -r0/4: its exact Hessian at q0 = (p, 0, r0 sigma_std, r0, x0) is PSD with rank 451 and nullity 35 and kernel exactly the symmetry-orbit tangent space; the tuned eps = 0 point (447/39) is not the witness.

- potential: `V_PS,eps = V_PS + eps N_H`
- vacuum: `(Phi, H, Sigma, S, Phi17) = (p, 0, r0 sigma_std, r0, x0)`
- eps window: `{'lower_exclusive': '0', 'upper_exclusive': '599/50', 'meaning': 'O06_eps = 2|kappa| r0 + eps < 12 < 4 pi'}`

## SM-track science criteria

- `G1_G2_exact_scoped_calculations_complete`: `True`
- `sm_target_unbroken_algebra_is_standard_model_exact`: `True`
- `sm_symmetry_orbit_ranks_33_34_35_exact`: `True`
- `sm_eps_witness_couplings_perturbative_exact`: `True`
- `sm_full_homogeneous_quartic_BFB_exact`: `True`
- `sm_eps_witness_exactly_stationary`: `True`
- `sm_eps_witness_global_gap_exact`: `True`
- `sm_eps_witness_equality_set_single_G_orbit_exact`: `True`
- `sm_decisive_theorem_string_bound`: `True`
- `sm_eps_witness_full_Hessian_rank_451_nullity_35_exact`: `True`
- `sm_eps_witness_quotient_strictly_positive_kernel_is_orbit_exact`: `True`
- `sm_raised_O06_control_rank_451_nullity_35_exact`: `True`
- `sm_eps_witness_light_doublet_mass_squared_equals_eps_exact`: `True`

## Release criteria

- `authoritative_external_model_contract_executed`: `True`
- `G1_promoted_closed`: `True`
- `G2_promoted_closed`: `True`
- `G5_BFB_evidence_covers_closing_coupling_vector`: `True`
- `ledger_G3_status_matches_gate_closure`: `True`

## Blockers

- none

## Downstream caveats (decision D5)

- `sub_M_I_coloured_126bar_states` -> `G6` (resolved: `False`)
- `positivity_without_EWSB` -> `G6` (resolved: `False`)
- `phi17_benchmark_scale` -> `G6` (resolved: `False`)
- `rg_anchor_field_content` -> `G7` (resolved: `False`)
- `higgs_quartic_matching` -> `G7` (resolved: `False`)
- `tan_beta_one_light_doublet` -> `G8` (resolved: `False`)
- `realistic_yukawa_sector` -> `G8` (resolved: `False`)
- `proton_decay_mediators` -> `G8` (resolved: `False`)
- `zero_modes_and_ranks_at_witness` -> `G4` (resolved: `False`)
- `naturalness_of_tunings` -> `OUTSIDE_G1_G8` (resolved: `False`)

## Diagnostic track

- `chiral_H_SU5_Delta` (role `DIAGNOSTIC`): `can_close_G3` = `False`
- failed criteria: `target_unbroken_algebra_is_standard_model`, `all_PD_equality_orbits_classified_exactly`, `beta_global_gap_and_unique_equality_exact`
- why not a closure route: its Delta_R is the T3R=0, Y=-1 member of the 126bar triplet, so its (F, Delta_R) pair leaves SU(3)_c x SU(2)_L x U(1)_T3R, not the Standard Model (g3_sigma_hypercharge_audit_v20)
