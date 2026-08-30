# Exact physical-SM vector R_xi vacuum cancellation v20

Status: `EXACT_ALL_37_BROKEN_DIRECTION_RXI_VACUUM_DETERMINANT_CANCELLATION_CLOSED__BACKGROUND_FIELD_POLE_AND_FULL_G6_G7_OPEN`

## Exact result

For one real massive gauge direction, the longitudinal vector, Goldstone, and FP-ghost determinant weights on `D_xi=p^2+xi M^2` are `1/2+1/2-1=0`. The residual `-1/2 log(xi)` is field-independent and is removed by vacuum normalization. The remaining determinant contains exactly the three transverse polarizations.

The exact mass theorem supplies `34` charged and `3` neutral massive real directions, for `37` in total. Thus the unphysical squared determinant is `xi^-37` before and `1` after normalization.

## Scope boundary

- Vacuum quadratic arbitrary-positive-R_xi cancellation: `True`
- General-background heat-kernel matching: `False`
- Vector pole masses: `False`
- Physical G6: `False`
- Physical G7: `False`

## Exact audit

A deterministic exact-rational grid covers cases `0..99`; all 100 satisfy the normalized squared determinant identity exactly.

## Remaining blockers

- Derive a background-covariant vector/Goldstone/FP-ghost operator and heat-kernel replay if an independent derivation of the already frozen Hall/Ellis-Wells coefficient is required.
- Supply renormalized couplings, VEVs, scalar/Yukawa tensors, a tadpole prescription, and the transverse self-energies needed to solve every vector pole equation.
- Derive the scalar Hessian directly from source algebra, remove the 37 eaten directions exactly, and compute all scalar and fermion pole-mass matrices.
- Construct the stationary pre-electroweak SU(3)xSU(2)xU(1) stage and complete the Yukawa/scalar/dimensionful/EFT flow.

Checks: `16`; failures: `0`.

Core SHA256: `ff79272e5f9eea691cae4e05926723d882ced5dcf852154dcfc43f8add44ef93`
