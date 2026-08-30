# V43 targeted Z4M repair audit for the V42 G7 witness

Status: `V43_Z4M_TARGETED_G7_WITNESS_SELECTOR_ARITHMETIC_CERTIFIED__NO_DECOUPLING_ONLY_ORDINARY_DISCRETE_GAUGE_COMPLETION__G7_FAIL_CLOSED`

## Outcome

There is a smallest **charge-arithmetic** repair: an extra unbroken ordinary `Z4_M`.  Give `Q`, `Psi`, `PsiCBar`, and the Dirac messenger `F` charge `+1`; give `Qc`, `PsiBar`, `PsiC`, `Fc`, and `NDirac` charge `-1`; keep every displayed PS/PQ/EW/Theta VEV and all drivers neutral.  The full V40 term list plus the V41 messenger remains neutral.  The V42 operator has `Z4_M=2`, so it is forbidden.

The required-term checks are U1F-neutral `True`, Z9-neutral `True`, Z4R-target-two `True`, and Z4M-neutral `True`.

The witness signature is `{'U1F': 0, 'Z9': 0, 'Z4R': 2, 'U1M_lift': -6, 'Z4M': 2, 'allowed_by_preexisting_V40_selectors': True, 'allowed_by_new_Z4M': False}`.  The familiar four-matter and one-PS-VEV controls remain blocked by the union of the old selectors and Z4M, while the required Dirac operator stays allowed: `{'U1F': 0, 'Z9': 0, 'Z4R': 2, 'U1M_lift': 0, 'Z4M': 0, 'allowed_by_preexisting_V40_selectors': True, 'allowed_by_new_Z4M': True}`.

## Exact limitation

This does **not** create an anomaly-complete new gauge symmetry.  The prospective U(1)_M parent has base rows `SU4=0`, `SU2L=12`, `SU2R=-12`, `gravity=-3`, `cubic=-3`.  Three residual-preserving left/right doublet pairs can cancel the mixed PS rows, but leave gravity and cubic rows at `-3`; its displayed U(1)_M-U(1)_F cross rows are nonzero as well.  At the Z4M level the necessary even-order screen has `eta=2` and gravitational residue `1`, so the ordinary no-GS screen fails.

The general primitive-charge scan through N=96 finds ordinary no-GS necessary-screen orders `[2, 3, 6]` and orders that also block the witness `[]`.  The analytic reason is that the three required `NDirac` fields force `A_gravity=-3q`, whereas the witness has charge `-6q`.

## Bounded operator check

Reproducing the V42 stated degree-12 single-epsilon frontier gives `6` rows.  Z4M blocks `4` including the degree-ten witness.  The remaining orientation-neutral rows are intentionally not called safe; a full invariant-ring and component analysis is still required.

A viable escape would have to supply one of the missing UV ingredients explicitly: a quantized GS/inflow or topological sector, an anomaly-carrying light sector with a physical spectrum, or a different nonminimal symmetry realization.  It cannot be inferred from this charge table.  Heavy thresholds and global discrete data matter for that distinction; see [Ibanez](https://arxiv.org/abs/hep-ph/9210211) and [Hsieh](https://arxiv.org/abs/1808.02881).

G7 remains open.

Core SHA-256: `9eac4ca35cdff6ba02a05b5aeb2736644d9c970acf2a80f05f29049e7bd5d4bf`
