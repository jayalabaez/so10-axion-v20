# Exact normalized SO(10) Yukawa CGCs — v20

Status: `EXACT_NORMALIZED_SO10_REPRESENTATION_YUKAWA_CGCS_CLOSED__FLAVOR_RGE_AND_FULL_G7_OPEN`

Core SHA-256: `c83671cff9c33043b5c7cad19e2f2a744cb5f861a8ea71937c5f3a7308dfffb7`

## Closed representation theorem

The exact Clifford construction gives `16 x 16 x 10 = (C Gamma_a)|_- / 4`. Projection onto the canonical kinetic-normalized physical `-i` Hodge basis gives `16 x 16 x 126bar = sum_I E[r,I](C Gamma_I)|_- / 8`.  Their Gram matrices are identities, both families are symmetric, mutually orthogonal, SO(10)-covariant under all 45 generators, and together form the complete 136-dimensional symmetric square.

The opposite Clifford chirality contracts identically to zero with this physical `126bar`; this exact obstruction fixes the chirality assignment and prevents a guessed CGC.

## Canonical inventory and declared symbols

The source-bound inventory contains 19 Weyl multiplets and 304 Weyl components.  Normalized representation CGCs are closed for:

- `Y10`: F x F through `10`; flavor tensor `symmetric_3x3` remains symbolic.
- `Y126`: F x F through `126bar`; flavor tensor `symmetric_3x3` remains symbolic.
- `yP`: P x Pbar through `singlet`; flavor tensor `scalar` remains symbolic.
- `yQ`: Q x Qbar through `singlet`; flavor tensor `scalar` remains symbolic.
- `yR`: R x Rbar through `singlet`; flavor tensor `scalar` remains symbolic.
- `ys`: SpecS x SpecB through `singlet`; flavor tensor `general_5x5` remains symbolic.
- `lambdaP`: P x F through `10`; flavor tensor `row_1x3` remains symbolic.
- `lambdaR`: R x F through `10`; flavor tensor `row_1x3` remains symbolic.
- `lambdaQB`: Qbar x F through `singlet`; flavor tensor `row_1x3` remains symbolic.
- `lambdaQR`: Q x Rbar through `singlet`; flavor tensor `scalar` remains symbolic.

## Fail-closed boundary

This artifact does not infer SARAH's implicit identical-field normalization, choose flavor boundary values, compute Yukawa/scalar/dimensionful beta functions, or provide physical component thresholds.  Full Yukawa closure and mathematical/release G7 remain false.

## Exact checks

- `authoritative_sources_match_frozen_hashes`: `true`
- `all_ten_declared_yukawa_symbols_found`: `true`
- `canonical_inventory_has_19_weyl_multiplets`: `true`
- `canonical_inventory_has_304_weyl_components`: `true`
- `minus_chirality_has_standard_model_16_weights`: `true`
- `plus_chirality_is_conjugate_16bar`: `true`
- `vector_has_ten_symmetric_matrices`: `true`
- `vector_normalized_gram_is_identity`: `true`
- `physical_126bar_has_126_symmetric_matrices`: `true`
- `physical_126bar_normalized_gram_is_identity`: `true`
- `physical_126bar_complement_shortcut_agrees`: `true`
- `opposite_spinor_chirality_annihilates_physical_126bar`: `true`
- `ten_and_126bar_are_exactly_orthogonal`: `true`
- `ten_plus_126bar_complete_symmetric_square`: `true`
- `singlet_duality_map_is_unitary`: `true`
- `singlet_dual_basis_normalized_gram_is_identity`: `true`
- `all_45_vector_covariance_residuals_zero`: `true`
- `all_45_126bar_covariance_residuals_zero`: `true`
- `all_45_singlet_covariance_residuals_zero`: `true`
- `vector_sparse_count_is_160`: `true`
- `physical_126bar_sparse_count_is_2016`: `true`
- `singlet_sparse_count_is_16`: `true`
- `all_embedded_support_indices_lie_in_304_inventory`: `true`
- `all_declared_representation_cgcs_closed`: `true`
- `flavor_boundary_values_closed`: `false`
- `sarah_symbol_normalization_closed`: `false`
- `full_yukawa_rge_closed`: `false`
- `full_physical_G7_closed`: `false`
