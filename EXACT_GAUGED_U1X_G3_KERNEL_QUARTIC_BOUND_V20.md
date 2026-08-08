# Exact G3 mixed-kernel quartic bound — v20

**Status:** `EXACT_SHARP_KERNEL_BOUND__SIMPLE_WEIGHT_SWAP_NO_GO`

The counterexample quartic value 33/32 is the sharp minimum on the entire 60-real mixed-flat kernel.  The exact SOS certificate leaves no lower direction there for the current weights.  Interchanging the 2772bar and 4125 weights fails as a rescue because a coherent pure-2772bar kernel vector reaches the sharper value 1 and beats Delta_R. More generally, at fixed Phi=P the same-norm value gap is exactly minus one eighth of Delta_R's twofold transverse curvature, proving that the selected orbit can never be both strict-local and global.

## Sharp current-weight theorem

- Exact mixed kernel: `30 complex = 60 real` dimensions, `K=(10,1,3)`.
- Sharp bound: `W >= (33/32)||z||^4`.
- Equality: one PS-and-phase orbit, represented by the exact Gaussian witness.
- The proof is the exact four-term SOS identity recorded in the JSON artifact.

## Weight-swap rescue no-go

- Swapped weights: `(2,2,1,17/16)`.
- Sharp kernel minimum: `1`.
- Delta_R value: `49/48`.
- Exact loss of Delta_R: `1/48`.
- Saturating vector: `product_j (e_(2j)+i e_(2j+1))`, pure 2772bar.

## Fixed-P local/global no-go

- All 49 non-`O27 B03/B04` exact-X directions have zero same-norm value difference.
- `Delta V/r^4=(lambda_4125-lambda_2772)/6`.
- `m_perp^2/r^2=(4/3)(lambda_2772-lambda_4125)` (multiplicity two).
- Hence `Delta V/r^4=-(1/8)m_perp^2/r^2` exactly.
- This rules out the selected `Phi=P, Sigma=Delta_R` orbit, not a general `(p,a,omega)` branch.

## Scope

The selected P+Delta_R orbit cannot close G3, but this does not minimize the complete potential over general Phi=(p,a,omega) and does not exclude the full theory.
