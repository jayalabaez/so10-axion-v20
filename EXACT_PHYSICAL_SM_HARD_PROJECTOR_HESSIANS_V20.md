# Exact physical-SM hard projector Hessians v20

Status: `EXACT_TEN_HARD_PROJECTOR_HESSIANS__FULL_37_ROW_AGGREGATE_AND_GLOBAL_EQUALITY_OPEN`

The full 486-real target Hessians of all four O27 and all six O44 source rows are derived with exact integer/Gaussian-integer arithmetic and cleared rational projectors. No float tolerance, finite difference, autodiff, or rational recognition accepts a Hessian entry.

- Exact hard rows: `10/10`.
- Exact active witness rows overall: `10/37`.
- Remaining active rows: `27`.
- Ordered exact-row digest: `7f0297fdbb26fb4d9347de6df5500012ad20ca27c217d7dd39f2b1822dad7495`.
- O27 projector sum reconstructs the direct norm-quartic Hessian entrywise over Q.
- O44 six-channel sum reconstructs the direct contraction Hessian entrywise over Q.

This is not the exact 37-row witness aggregate. Exact aggregate stationarity, symmetry kernel, rank/PSD, and the separate full 486-field global equality-orbit classification remain open. Therefore physical G3, G4, and G5 remain false.

## Minimum missing derivation

derive the complete exact value/gradient/Hessian jets of these 27 rows; compose all 37 with the exact rational witness; then prove exact stationarity, the 38-dimensional symmetry kernel, rank 448 and PSD.

classify every full 486-field zero/equality point modulo the declared SO(10) x U(1)_X x PQ symmetry; a local Hessian cannot supply this.
