# Referee audit — v19

## Decision

The proposed `U(1)_X -> Z17` construction is internally consistent as a
four-dimensional effective gauge theory up to the Planck cutoff under its
declared perturbativity and hierarchy assumptions. The continuous mixed,
gravitational and cubic anomalies cancel exactly; the heavy sector has
gauge-invariant masses; and a conservative renormalizable over-catalogue
finds no accidental-PQ or exact-vector-number breaker.

This does **not** establish a fundamental UV completion in quantum gravity.
It establishes a concrete anomaly-free gauge embedding that removes the
previously unspecified origin of the discrete symmetry.

It also does **not** establish a relic-safe anomalon cosmology. The
renormalizable audit deliberately finds four exact heavy/light pair
numbers; the heavy fields have masses but no renormalizable portal to
ordinary matter. A low reheating temperature or a separately audited decay
sector is required.

## Merge verdict on the supplied alternate v18

The alternate package passes its own 27 checks and 13 tests, and its exact
anomaly arithmetic is correct. Those tests do not cover its decisive weak
points:

- Its arbitrary-charge cubic code uses `80*sum_i(...)`; the correct
  multiplicity is `16*sum_i(...)`. The factor 80 is valid only after five
  identical pairs have already been imposed. The corrected cyclic
  convolution happens to retain the same numerical count, 83,232.
- A gauged generator is not itself the physical global PQ. An independent
  accidental assignment can be supplied, but it must be stated and its
  gauge-orthogonal axion projected.
- Its scalar-only dimension-21 scan omits the allowed operator
  `(Sdag)^2 (16bar_16 16bar_s)_10 10_H / M_Pl^2`. Four copies plus the
  known dimension-8 `s^4` spurion form a `P=12`, `Q_PQ=-68` closure
  candidate once the advertised anomalon-decay vertex removes anomalon
  number as an exact obstruction. A complete Grassmann evaluation of that
  alternate topology is still required.
- The four heavy singlets have only their two `Phi` mass Yukawas; no
  renormalizable light-matter decay portal exists in the listed field
  content.
- Its `2.37e-62` old-graph number retains the previous dimensional
  envelope. The exact factorized, vev-normalised kernel at the same inputs
  is `1.85e-64`, a factor of about 128 smaller. The omitted alternate
  `P=12` graph, rather than this old graph, would need to be calculated.
- Its large-charge running is `b_X=8263`, implying `g_X<0.0417` at
  `vPhi=M_GUT` for a one-loop Landau pole above `M_Pl`.

Accordingly, v19 merges the genuinely stronger arbitrary-charge
five-pair proof and branch-scoped falsification numbers, but not the
alternate anomalon completion or its amplitude claim.

## New result that changed the earlier interpretation

The discrete-EFT `P=12` graph cannot be copied unchanged into the
continuous theory. Its four portals each have `X=-17` and require a
`Phi/M_Pl` factor. It is a `P=16` graph after matching.

The complete heavy-field search instead finds a different first closure at
`P=13`. A nonzero certificate uses two dimension-6 heavy-light portals,
two dimension-7 dressed light portals and one dimension-7 heavy Majorana
spurion. Five fermion lines close as a one-loop polygon. The final phase is
`Phi^4 (S†)^17 (10_H 10_H†)` with `Q_PQ=-68`.

This is exactly the sort of threshold effect that the heavy-field axion
quality literature warns must be checked. Here it does not endanger
quality, but it invalidates the simpler statement that the old `P=12`
graph remains leading after continuous embedding.

## Amplitude boundary

For the v17 graph the two independent loop momenta give a product of
finite zero-momentum triangle integrals. All propagator masses are retained:

```text
I3(M,M,m) = [1-r+r log r] / [16 pi^2 M^2 (1-r)^2]
r = m^2/M^2
J(M,m) = M^2 m I3(M,M,m)
A_2loop = C_2loop s0^14 J(M,m1) J(M,m2) / M_Pl^12
```

The general unequal-mass kernel is implemented as the symmetric divided
difference of `x log x`. The `P=13` polygon uses a finite five-propagator
integral evaluated with 90-digit partial fractions; a separate SciPy radial
quadrature regression agrees.

The coefficient `C` is deliberately not set equal to a bare product of
un-normalized tensors. It represents the unknown Planck Wilson tensors,
flavour contraction, the explicitly nonzero Spin(10)/Lorentz factor and RG
matching. A paper claiming a unique coefficient-free number would be
overstating what the EFT contains.

## Strongest checks

- Exact anomaly totals: `(0,0,0)`.
- No solution with `max |X| <=25` in the declared completion ansatz.
- No dimension-four-or-lower candidate breaks accidental PQ or the four
  vector numbers, even in the necessary-condition over-catalogue.
- No heavy-inclusive vacuum closure through `P=12`; first target `P=13`.
- Explicit `P=13` Spin(10) Gram matrix `16 I_10`; Lorentz cycle `2`.
- Exact axion projection orthogonal to the gauge direction.
- Abelian Landau-pole bound evaluated rather than omitted.
- Exact triangle checked against Feynman-parameter quadrature.
- Exact five-propagator integral checked against independent radial
  quadrature.
- Both success and injected-failure engine exit codes tested.

## What an external referee should attack next

1. Reconstruct every allowed renormalizable Spin(10) contraction, including
   scalar-potential invariants, without relying on the centre over-catalogue.
2. Re-derive the `P=13` diagram with explicit two-component propagator and
   operator-normalization conventions, including symmetry signs.
3. Specify the Wilson-tensor flavour basis and run the operators from
   `M_Pl` through `vPhi`, `M_GUT`, `vS`, and the electroweak scale.
4. Assess radiative stability of `vPhi >> vS` and the required scalar portal.
5. Supply a heavy-anomalon decay mechanism, or a quantitatively consistent
   low-reheat cosmology, and rerun the operator catalogue with it included.
6. Check the large-charge Abelian theory beyond one loop and seek a
   non-Abelian or gravitational UV origin.
7. Simulate the two-stage local-string/axion-string network.

Until those independent checks exist, v19 is a falsifiable model-building
construction and a reproducible calculation—not proof that nature realizes
the model.
