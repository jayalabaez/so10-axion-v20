# SUSY V37 new-physics routes

## Outcome

V37 implements one real improvement, not a complete theory.  The V36 selector
is enlarged by an anomaly-paired `Z85` spectator and represented faithfully as
`Z5610`.  Two redundant anomalon terms are removed while the mass determinant
remains `a^2*b^2*c`.

The exact combined finite anomaly test passes.  The complete PS-singlet
chiral superpotential ring first violates the optimized accidental PQ symmetry at
degree `33`.  A
conservative search including conjugate fields first finds a Kahler invariant
at degree `32`.  This is a
large improvement over V36's degree-10 heavy-anomalon frontier.

As a stronger cross-check, a charge-lattice search over all 20 chiral species,
performed before imposing Pati--Salam index contractions, finds the same first
degrees.  Therefore no omitted gauge contraction can generate a lower-degree
polynomial operator; the displayed singlet witnesses show that the bounds are
attained.

The spectator charges are
`h85(A2,A32,A15,A17,A16)=(1,-1,69,-69,0)`.  Pairwise linear and cubic sums
vanish, `69^2=1 mod85`, and the tested mixed `Z4R-Z85^2` residue vanishes.
The full `Spin^Z4R x Z5610` bordism, however, is not inferred from these
pairwise checks.

## Important rejected loophole

A PQ-neutral anomaly-Higgs plus one complete `16+16bar` really does cancel the
three mixed selector anomalies with only `Delta b=(4,4,4)`.  It nevertheless
fails quality: the exact symmetries allow
`Pbar^2 Bbar 16 16bar/M^2`.  The conservative soft-loop estimate gives
`log10|theta|=20.323`
at the frozen V36 benchmark, roughly thirty orders above the limit.  The route
is rejected unless another exact sequestering mechanism is supplied.

## Other routes retained

- A nonprimitive cyclic `Z132` consolidates `Z4R` and `Z33` and reaches
  degree 11, but its universal mixed residue is nonzero.
- A five-dimensional `U(1)_X -> Z66` interval with a mirror wall and APS/eta
  inflow is a concrete UV scaffold.  It still needs the second wall, global PS
  form, `Z4R`, KK thresholds, and quality spurions made explicit.
- A four-dimensional gauged `U(1)_H -> Z85` candidate with charge-`+/-85`
  Higgs fields would produce the spectator remnant.  Its continuous mixed R
  anomaly and unusually large Abelian charge running make the parent theory
  incomplete until a heavy UV sector is supplied.
- The recent composite Pati--Salam axion is a serious radical fork, but is not
  the present elementary N=1 SUSY theory and cannot be spliced in without a new
  dynamical model.

## Validation boundary

Live SARAH initialized `PSZ4RZ5610SUSYV37` and the two-loop calculation status is `True`.

The `P,Pbar` vacuum leaves `Z170 ~= Z2 x Z85` unbroken.  Consequently the
lightest spectator-charged anomalon is stable in the current field content;
reheating below its mass or a symmetry-preserving decay/dark-sector completion
is mandatory before cosmological promotion.

Strict gate count remains `0/8`.  G5's polynomial subproblem is materially
stronger, while G1 has sharper ultraviolet options; neither gate is promoted.

Core SHA-256: `6ce083a0f943b944a9c5927ac71e121b52f74e18f7f9b58c564e09d780d62f68`
