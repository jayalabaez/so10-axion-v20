# Referee audit of the v17 Spin(10) × Z17 quality claim

## Verdict

The v16 claim that the first attainable vacuum-sensitive spurion set occurs
at `P = 12` survives explicit hostile testing. The result has two logically
separate halves:

1. A necessary-condition over-catalogue, independently reimplemented, finds
   no `V = 0`, nonzero `Q_PQ = 0 mod 68` target through `P = 11`.
2. A concrete `4 O6 + O8` construction at `P = 12` has nonzero Spin(10),
   Lorentz and Grassmann contractions and closes as a connected two-loop
   vacuum graph.

Together these establish `P_min = 12` under the EFT field content and
selection rules stated in the manuscript.

## Explicit contraction certificate

The audit constructs ten Euclidean gamma matrices satisfying
`{Γ^a, Γ^b} = 2 δ^{ab}` exactly in a `32 × 32` representation. With
`C = Γ^2 Γ^4 Γ^6 Γ^8 Γ^10`, restriction of `C Γ^a` to either chiral
16-dimensional subspace gives ten symmetric matrices `T^a`. This is the
required Fermi-statistics symmetry for the `10_s` in
`16 ⊗ 16 = 10_s ⊕ 120_a ⊕ 126_s`.

Computed exact diagnostics:

| Diagnostic | Result |
|---|---:|
| Clifford and charge-conjugation maximum error | 0 |
| Chiral dimensions | 16 + 16 |
| `T^a` Gram matrix | `16 I_10` |
| Nonzero O6 Grassmann monomials | 32 |
| Nonzero O8 Grassmann monomials | 240 |
| Nonzero O10 Grassmann monomials | 2560 |
| Nonzero O12 Grassmann monomials | 960 |
| Nonzero entries of `K_ijkl = Σ_a T^a_ij T^a_kl` | 640 |
| `Σ_ijkl |K_ijkl|²` | 2560 |
| Unit-`10_H` graph contraction | 256 |
| Displayed Lorentz contraction | 4 |

The compact `4 O6 + O8` graph has five Planck vertices and six internal
fermion lines, hence `L = E − V + 1 = 2`. Four lines are spectator `s-b`
same-chirality propagators and two are ordinary-family `10_H`-channel
chirality flips. Four different spectator copies can be used, although the
stronger same-species local Grassmann check is already nonzero.

The associated scalar phase is

\[
(S^\dagger)^{18}(10_H^\dagger\!\cdot10_H^\dagger),
\qquad Q_{\rm PQ}=-68.
\]

The tensor norm 2560 proves the central four-spinor tensor is nonzero; the
separate value 256 proves the actual closure with two `10_H`-channel mass
tensors is nonzero. These numbers depend on tensor normalization and are
absorbed into `C_eff` when quoting the NDA estimate.

## Independent lower-bound check

`test_referee_audit_v17.py` does not import the main quality enumerator. It
enumerates raw weak compositions of all six fermion/conjugate species and
four charged scalar/conjugate species, imposes only even Weyl number,
Spin(10)-centre neutrality and Z17 invariance, and keeps the least dimension
for every `(Q_PQ/17, V)` class. Its unbounded positive-cost reachability
search finds:

- exactly the expected 20 classes with individual cost `P ≤ 11`;
- no vacuum target through total `P = 11`;
- both target classes `(-4, 0)` and `(+4, 0)` at `P = 12`.

Because this is an over-catalogue that permits some nonexistent contractions,
absence in it is a conservative lower bound. The explicit graph supplies the
matching upper bound.

## Numerical interpretation

The rigorous, deliberately loose result remains

\[
|\Delta\bar\theta|/|C_{\rm eff}| \lesssim 4.52\times10^{-28}.
\]

For the constructed graph itself,

\[
(16\pi^2)^{-2}(246\,{\rm GeV}/M_s)^2
\times 4.52\times10^{-28}
=2.75\times10^{-51},
\]

before additional flavour suppression. A special VEV alignment that makes
`10_H^dagger · 10_H^dagger` vanish removes this diagram and therefore only
strengthens the bound.

## What remains unproved

- a UV gauge/string origin of Z17;
- exhaustive matching across arbitrary heavy PQ-breaking thresholds;
- the nonstandard gauged-string cosmology;
- phenomenological viability beyond the benchmark inputs;
- novelty acceptance by independent domain experts.

These limits are consistent with the anomaly-framework caveats in
[Hsieh (2018)](https://arxiv.org/abs/1808.02881), the standard Spin(10)
representation products used in
[Djouadi et al. (2022)](https://arxiv.org/abs/2212.11315), and the warning
that heavy thresholds can change naive quality power counting in
[Bonnefoy (2022)](https://arxiv.org/abs/2212.00102).
