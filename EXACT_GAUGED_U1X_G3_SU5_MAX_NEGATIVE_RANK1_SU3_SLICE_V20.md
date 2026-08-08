# Exact rank-one maximal-negative SU(3)-slice bound

Status: **EXACT_RANK1_SU3_DANGEROUS_SLICE_BOUND_CERTIFIED**

The live explicit decomposable pure-spinor source and the 54/4125 pair-Casimir projectors reconstruct the four-variable anchor polynomial exactly.
A rational 15x15 Gram matrix has fifteen strictly positive exact LDL pivots and proves `anchor >= 3/200`.  The radial patch then gives the restricted global minimum `1/5000` for all nonnegative `u,v`.

This closes only a four-dimensional sub-slice of the full 16-real-dimensional SU(3)-fixed space.  Arbitrary real Phi at this explicit endpoint, the full maximal-negative Sigma-35 family, and G3 remain open.

## Checks

- `rank1_live_residual_source_exact`: **PASS**
- `explicit_endpoint_current_and_self_projectors_exactly`: **PASS**
- `slice_basis_Gram_exact`: **PASS**
- `rank1_common_affine_kernel_rank160_nullity50_exact`: **PASS**
- `angular_projector_Gram_symmetric_exact`: **PASS**
- `angular_projector_int64_overflow_preflight_exact`: **PASS**
- `anchor_polynomial_reconstructed_exactly`: **PASS**
- `rational_SOS_polynomial_identity_exact`: **PASS**
- `rational_SOS_Gram_positive_definite_exact`: **PASS**
- `anchor_at_least_3_over_200_exact`: **PASS**
- `radial_patch_global_minimum_1_over_5000_exact`: **PASS**
- `attaining_slice_witness_evaluated_from_live_arrays_exact`: **PASS**
- `arbitrary_rank1_Phi_proved`: **OPEN**
- `arbitrary_Sigma35_proved`: **OPEN**
- `G3_closed`: **OPEN**
