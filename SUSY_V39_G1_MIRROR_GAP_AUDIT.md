# SUSY V39 G1 mirror-wall gap audit

- Status: `V39_MIRROR_WALL_TRIVIAL_SUPERPOTENTIAL_GAP_NO_GO__FIRST_BREAKING_MASS_WITNESS_EXPLICIT__R_AND_PS_GLOBAL_ARITHMETIC_AUDITED__FULL_G1_FAIL_CLOSED`
- Core: `f5e9f10f11adf3bc46f47127714e460a80c9f00e535742f2f4f2a16b7a111933`
- Full G1 closed: **no**.

## Mirror-wall result

The V38 inverse packet cannot be removed by a local symmetry-preserving N=1 superpotential.  It contains `3` net opposite Pati--Salam families and has mixed U(1)_X-PS^2 coefficient `[8, 8, 8]`.  Either obstruction alone forbids a full-rank trivial PS x Z66 preserving mass gap.

The first local mass attempt is explicit: `Bminus2*mirror_Q*mirror_PsiBar`.  Its needed field has U(1)_X charge `-2` and Z4R superfield charge `2`, exactly the Pbar-like assignment.  Its VEV leaves only `Z2` of Z66 and `Z170` of Z5610.  It therefore breaks the selector and cannot serve as the ultraviolet mirror gap.

## R and global-form accounting

Using the conventional N=1 local R-anomaly formula, chiral matter plus Pati--Salam gauginos gives doubled mixed rows `[14, 10, 2]`, universal as `2 mod 4`.  The PS-only gravitational count is `21`; with U(1)X and U(1)H zero-mode gauginos it is `23`.  Both are odd modulo two before the unspecified breaking/mirror sector.  One neutral modulino of fermion R lift `-1` repairs only arithmetic parity; it does not give a quantized GS action or a full supergravity completion.

The correct Spin(10)-descended Pati--Salam global form is `(SU4 x SU2L x SU2R)/Z2_diag`; every V37 representation descends and both SU2 Witten doublet counts are even.  The full product bordism with Z4R, Z5610, gauginos, gravitino, and quotient bundles remains uncomputed.

## Decision

V39 rules out the missing conventional mirror-wall superpotential.  A nontrivial anomalous boundary topological order or a microscopic UV completion would be new physical input, not a consequence of V37/V38.  The 5D interval remains an anomaly-EFT scaffold and G1 remains fail-closed.

References: [Witten--Yonekura](https://arxiv.org/abs/1909.08775), [Hsieh](https://arxiv.org/abs/1808.02881), [Cordova--Ohmori](https://arxiv.org/abs/1910.04962), [Byakti--Ghosh--Sharma](https://arxiv.org/abs/1707.03837), and [Kawamura--Raby](https://arxiv.org/abs/2009.04582).
