# Next executable calculation: physical E/F/J/X Clebsch normalization

## Goal

Compute the exact coefficient `c_norm` in

`gamma_eff = c_norm * lambda4`

for the non-supersymmetric invariant `Phi(210) H(10) Sigmabar(126bar) S`,
then re-evaluate the E/F/J/X spectrum on the physical `h=174 GeV` branch.

## Inputs that must be supplied

1. Exact antisymmetric-index definitions for 210 and 126bar.
2. The 126bar self-duality sign and epsilon convention.
3. Canonically normalized Pati-Salam or SU(5) component states for the four fields.
4. Normalized 210 singlet directions `(p,a,omega)`.
5. The singlet-S convention and VEV normalization.
6. The physical non-supersymmetric vacuum values, including `hEW=174 GeV`.

## Executable sequence

1. **Symbolic contraction generator**
   - Encode the exact invariant with rational/factorial prefactors.
   - Generate component coefficients using exact arithmetic.
2. **State normalization test**
   - Check every basis state has unit kinetic norm.
   - Check orthogonality within repeated SM irreps.
3. **E/F/J/X reconstruction**
   - Reconstruct each gamma-dependent matrix slot independently.
   - Compare slot by slot with the response matrices emitted by
     `efjx_cgc_physical_normalization_gate_v20.py`.
4. **Convention map**
   - Solve for `gamma_eff_over_lambda4`, including its phase/sign.
   - Populate `EFJX_CGC_NORMALIZATION_INPUT_V20.json` with evidence.
5. **Physical branch insertion**
   - Insert the derived coefficient into the complete component potential.
   - Re-solve stationarity with `hEW=174 GeV` rather than `H10=M_I`.
6. **Falsification gate**
   - If any non-Goldstone eigenvalue is negative, reject the branch.
   - If E/F/J/X remain below the declared threshold, reject that rescue route.
   - Otherwise pass the result forward to physical thresholds and two-loop RG.

## Acceptance rule

No numerical ratio from the reduced radial proxy is accepted as a Clebsch
coefficient. Closure requires direct tensor contraction, independent matrix
reconstruction, canonical normalization, and physical-EW re-minimization.
