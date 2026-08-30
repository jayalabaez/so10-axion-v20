# Physical SM vacuum local-feasibility rebuild v20

- Status: `PHYSICAL_SM_RECONSTRUCTED_GLOBAL_EFT_CERTIFICATE__DIRECT_SOURCE_ALGEBRA_AND_GLOBAL_EQUALITY_ORBIT_OPEN`
- Core SHA-256: `01f565d3382756bc467bfaa99d187188bc1bfc4060f2c3a472650f5e57537e80`
- Physical-SM G3/G4/G5/G6/G7 closure claims: all `false`.

## Exact results

- Rational target: `20 q` integral, `q.q=102/25`.
- SO(10) orbit rank: `36`.
- Gauged SO(10)xU(1)_X orbit rank: `37`.
- Full gauge+PQ orbit rank: `38`.
- Exact stabilizer: standard `SU(3)_C x U(1)_em`.
- Supersedes the old selected-target stabilizer label: that target is actually `SU(3)_C x U(1)_89`, not standard electromagnetism.
- `W6=kappa R(R-R0)^2`, `kappa>0`, is a nonnegative coercive EFT completion and adds only a PSD radial Hessian at the target.
- `U=a(V+1)^2+b||grad V||^2`, `a,b>0`, is exactly nonnegative and has `H_U=2b H_V^T H_V` at the target.

## Live local scout

- Reconstructed exact stationarity rank/nullity: `15/36`.
- Maximum Q+sqrt(2)Q reconstruction residual: `2.363561e-15`.
- Gradient max norm: `1.998401e-15`.
- Hessian zero modes: `38`.
- Minimum transverse eigenvalue: `0.09999835991`.
- Maximum eigenvalue: `3.288671157`.
- Physical-sector transverse dimension sum: `448`.
- Numerical local-feasibility checks: `true`.
- Exact reconstructed Hessian rank/nullity: `448/38`.
- Reconstructed sparse-Hessian SHA-256: `58e39ea9a982ac71fd696de93d8d8bc51dd1e153399bfa6f7cbcc368fc6b7458`.
- Squared-stationarity EFT target is an exact global minimum; classification of all other zero-action minima remains open.

## Fail-closed boundary

Stationarity and Hessian rank are exact on a rational lattice reconstructed from the live compiler, and the squared-stationarity EFT identity gives exact nonnegativity, globality, and PSD on that lattice. Direct source-algebra derivations of every reconstructed entry and classification of the complete global zero locus remain open, so G3/G4 and physical G6 stay fail-closed.
