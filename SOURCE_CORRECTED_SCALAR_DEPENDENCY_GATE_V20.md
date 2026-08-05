# Source-corrected scalar dependency gate — v20

**State:** `BLOCKED`

The corrected symmetric 45 changes the complete scalar-potential dependency graph. Structural tensor, gauge, and reduced neutral-phase results remain useful, but G1-G8 are not closed. PR #98 must remain draft until the source-normalized quartic basis and all downstream vacuum, Hessian, threshold, and proton-decay calculations are rerun.

## Retained structural results

- `direct_210_10_126_portal_tensor_map`
- `canonical_126_kinetic_basis`
- `selected_neutral_phase_gauge_quotient_for_positive_kappa`
- `one_heavy_cp_odd_plus_one_pq_axion_in_reduced_neutral_sector`
- `so10_generator_and_gauge_orbit_constructions`
- `cqit_haloscope_receiver_bridge`

## Reopened scalar dependencies

- `same_field_symmetric_45_quartic_absent`
- `old_sym2_210_residual_dimension_5945`
- `complete_210_quartic_invariant_basis`
- `full_mixed_rep_invariant_ring_G1`
- `full_tensor_projected_potential_G2`
- `complete_bfb_certificate`
- `global_vacuum_selection`
- `complete_component_hessian`
- `physical_threshold_spectrum`
- `two_loop_threshold_chain`
- `unique_proton_lifetime`

## Superseded artifacts

- `OPEN_210_CHANNEL_1050_IRREDUCIBLE_BLOCKER_V20.json`
- `SO10_210_TO_45_PROJECTOR_V20.json (same-field quartic interpretation only)`
- `FULL_MIXED_REP_INVARIANT_RING_V20.json completeness interpretation`
- `SCALAR_THEORY_CLOSURE_LEDGER_V20.json downstream scalar statuses`

## Required execution order

1. Normalize and verify the source 45, 54, 210 and 1050 invariant identities in one Cartesian convention — the one-field 210 quartic sub-basis only
2. Complete mixed-representation invariant multiplicities and component CG maps — G1 and G2
3. Rebuild stationarity, BFB, competing extrema and gauge-projected full Hessian — G3-G5 prerequisites
4. Regenerate physical scalar/triplet thresholds and two-loop matching — G6-G7 prerequisites
5. Recompute gauge plus scalar proton decay with one physical flavour solution — G8
