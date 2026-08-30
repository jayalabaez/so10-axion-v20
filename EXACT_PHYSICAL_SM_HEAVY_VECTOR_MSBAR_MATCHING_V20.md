# Exact physical-SM heavy-vector MS-bar matching — v20

Status: `EXACT_COMBINED_HEAVY_VECTOR_GHOST_GOLDSTONE_MSBAR_MATCHING_CLOSED__ARBITRARY_RXI_POLE_PRE_EW_AND_FULL_G7_OPEN`

Core SHA-256: `9f7a269bcc24909b8f543a3ae38c10ea3e5acd5435798a2e74c3223322d1f575`

## Closed theorem

For each charged complex massive-vector multiplet, with tree running mass `M` and low-group index `T`, the source-bound non-supersymmetric MS-bar result is

`Delta alpha^{-1} = -T/(6 pi) + 7 T log(M/mu)/(2 pi)`.

The Hall/Ellis-Wells form and the separately evaluated Appendix-B vector-plus-FP-ghost and would-be-Goldstone terms agree row by row.

## Exact group factors

- complex indices `(SU3,QED)=(5/2,32/3)`
- real broken-generator indices `(SU3,QED)=(5,64/3)`
- finite coefficients over `pi`: `(SU3,QED)=(-5/12,-16/9)`
- total log coefficients over `pi`: `(SU3,QED)=(35/4,112/3)`
- tree inverse-coupling map: `alpha3^-1=alpha10^-1`, `alphaEM^-1=(8/3)alpha10^-1`; U(1)_X has coefficient zero.

All 37 eaten directions must be excluded from a later scalar threshold; the one accidental-PQ direction is not eaten.

## Deliberate boundary

The combined MS-bar result is closed, but this artifact does not invent an arbitrary-`xi` split. Explicit gauge-parameter input is rejected. Pole-mass conversion, a pre-EW `SU(3)xSU(2)xU(1)` stage, complete matter thresholds, physical G6, and physical G7 remain false.

## Primary equations

- S. A. R. Ellis and J. D. Wells, Phys. Rev. D 91 (2015) 075016, `10.1103/PhysRevD.91.075016`: (2), (3).
- K. Jarkovska, M. Malinsky and V. Susic, Phys. Rev. D 108 (2023) 055003, `10.1103/PhysRevD.108.055003`: (B14), (B15).
- L. J. Hall, Nucl. Phys. B 178 (1981) 75-124, `10.1016/0550-3213(81)90498-3`: original derivation.

## Checks

- `all_dependencies_match_frozen_hashes`: `true`
- `primary_equations_identified_by_DOI_and_number`: `true`
- `scheme_is_nonsupersymmetric_MSbar`: `true`
- `tree_running_masses_declared`: `true`
- `seven_charged_complex_multiplets_complete`: `true`
- `charged_real_vector_dimension_is_34`: `true`
- `neutral_massive_vector_dimension_is_3`: `true`
- `total_massive_and_Goldstone_dimensions_are_37`: `true`
- `complex_SU3_index_is_5_over_2`: `true`
- `complex_QED_index_is_32_over_3`: `true`
- `real_SU3_broken_index_is_5`: `true`
- `real_QED_broken_index_is_64_over_3`: `true`
- `QED_embedding_index_is_8_over_3`: `true`
- `U1X_has_zero_tree_embedding_in_SU3_and_QED`: `true`
- `SU3_finite_constant_is_minus_5_over_12pi`: `true`
- `QED_finite_constant_is_minus_16_over_9pi`: `true`
- `SU3_log_coefficient_is_35_over_4pi`: `true`
- `QED_log_coefficient_is_112_over_3pi`: `true`
- `Hall_and_B15_implementations_agree`: `true`
- `mass_theorem_weighted_log_interface_agrees`: `true`
- `combined_vector_FPghost_Goldstone_MSbar_kernel_closed`: `true`
- `finite_MSbar_vector_constant_closed`: `true`
- `Goldstone_double_count_guard_active`: `true`
- `arbitrary_Rxi_determinant_cancellation_rederived`: `false`
- `pole_mass_conversion_closed`: `false`
- `SM_symmetric_pre_EW_matching_closed`: `false`
- `complete_scalar_fermion_threshold_matching_closed`: `false`
- `physical_G6_closed`: `false`
- `physical_G7_closed`: `false`
