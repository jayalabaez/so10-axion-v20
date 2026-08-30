# Exact physical-SM heavy-vector masses — v20

Status: `EXACT_PARAMETERIZED_PHYSICAL_SM_HEAVY_VECTOR_MASS_THEOREM_CLOSED__LOOP_MATCHING_AND_FULL_G6_G7_OPEN`

Core SHA-256: `86c3e0dfda09366b1cf06c8c3a8dcb3dfdf3bfe1555a41214d380ed4db329894`

## Exact tree theorem

With the source-bound `T(10)=1` normalization, the 45 SO(10) plane generators carry `g10/sqrt(2)` and the declared U(1)_X charge generator carries `gX`.  The complete mass matrix is

`M^2 = v^2 D A^T A D / 400`,

where `A=20(T_a q*)` is the exact 486x46 integer tangent matrix.

Its exact rank/nullity is 37/9. The kernel is precisely `su(3)_C + u(1)_em`; its image is the 37-dimensional eaten tangent space. The accidental PQ tangent supplies one additional uneaten direction.

## Massive sectors

- `T_Q1over3_A`: SU(3) `3`, |Q|=1/3, `m^2/(g10^2 v^2)=1`, real dimension 6.
- `T_Q1over3_B`: SU(3) `3`, |Q|=1/3, `m^2/(g10^2 v^2)=51/50`, real dimension 6.
- `T_Q2over3_A`: SU(3) `3`, |Q|=2/3, `m^2/(g10^2 v^2)=1/50`, real dimension 6.
- `T_Q2over3_B`: SU(3) `3`, |Q|=2/3, `m^2/(g10^2 v^2)=13/25`, real dimension 6.
- `T_Q4over3`: SU(3) `3`, |Q|=4/3, `m^2/(g10^2 v^2)=1/2`, real dimension 6.
- `W_Q1_A`: SU(3) `1`, |Q|=1, `m^2/(g10^2 v^2)=1/2`, real dimension 2.
- `W_Q1_B`: SU(3) `1`, |Q|=1, `m^2/(g10^2 v^2)=13/25`, real dimension 2.

Three additional neutral masses are the positive roots of the exact coupling-dependent cubic recorded in the JSON artifact.

## Threshold boundary

The production interface returns SU(3) and QED representation-index-weighted `log(M/mu)` inputs.  It does not insert a vector/Goldstone/ghost matching coefficient or finite scheme constants.  Since the full target is electroweak broken, an SM-symmetric `g1,g2,g3` threshold step is also still required.

Absolute scales, pole masses, the source-exact scalar spectrum, complete loop matching, physical G6 and physical G7 remain false.

## Checks

- `all_dependencies_match_frozen_hashes`: `true`
- `target_denominator_is_20`: `true`
- `canonical_chart_kinetic_is_identity`: `true`
- `SO10_generator_rescaling_matches_T10_one`: `true`
- `tangent_matrix_is_486_by_46`: `true`
- `exact_tangent_matches_live_chart_without_residual`: `true`
- `gram_matrix_is_exact_symmetric_integer`: `true`
- `five_field_block_grams_sum_exactly`: `true`
- `sparse_upper_triangle_reconstructs_all_nonzero_entries`: `true`
- `exact_massive_rank_is_37`: `true`
- `exact_unbroken_nullity_is_9`: `true`
- `standard_su3C_u1em_basis_is_complete_kernel`: `true`
- `Goldstone_image_dimension_is_37`: `true`
- `one_accidental_PQ_direction_is_uneaten`: `true`
- `mass_gram_commutes_with_color`: `true`
- `mass_gram_commutes_with_Q3_squared`: `true`
- `joint_sector_projectors_are_complete`: `true`
- `all_non_neutral_sector_polynomials_exact`: `true`
- `all_non_neutral_multiplicities_exact`: `true`
- `non_neutral_massive_real_dimension_is_34`: `true`
- `three_neutral_massive_roots_complete_rank_37`: `true`
- `one_loop_SU3_index_sum_is_5_over_2`: `true`
- `one_loop_QED_index_sum_is_32_over_3`: `true`
- `physical_scale_and_coupling_boundaries_fixed`: `false`
- `pole_masses_fixed`: `false`
- `vector_Goldstone_ghost_matching_closed`: `false`
- `finite_scheme_constants_closed`: `false`
- `SM_symmetric_pre_EW_threshold_closed`: `false`
- `physical_G6_closed`: `false`
- `physical_G7_closed`: `false`
