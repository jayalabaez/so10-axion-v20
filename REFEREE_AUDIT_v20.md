# Referee audit boundary — v20

## What v20 establishes

1. The displayed three complete `16+16bar` pairs cancel the continuous
   mixed Spin(10), gravitational and cubic `U(1)_X` anomalies exactly.
2. Their accidental-PQ anomaly vanishes, and an over-catalogue of all
   dimension-four-or-lower charge/centre/Lorentz candidates contains no PQ
   or light-spectator-number breaker.
3. One complete pair cannot solve the anomalies in a sector containing only
   complete pairs if its renormalizable mass uses one `Phi` insertion.
   Three pairs are therefore minimal in that no-singlet-anomalon ansatz; the
   displayed triple is unique at three pairs in the stated existing-field
   portal basis.
4. Every pair has a gauge- and PQ-invariant renormalizable portal to
   ordinary matter.  The explicit Clifford representation proves no
   component of a `16` is annihilated by all `10_H` channels.
5. The first necessary-condition, spectator-neutral PQ closure is `P=8`,
   and the manuscript supplies an actual nonzero two-loop graph saturating
   it.
6. The repeated-pole momentum kernel is finite, mass-dependent, evaluated
   at high precision and checked by an independent quadrature.
7. The computed `P=8` term is safe for a unit normalized contraction; the
   direct dimension-21 scalar term remains the largest computed term.

## What v20 does not establish

- It does not prove that nature realizes this model or that an axion has
  been detected.
- Minimality is not claimed over arbitrary Spin(10) representations,
  multiple mass scalars or a string spectrum.
- It does not derive Planck-scale Wilson, flavour or RG contractions.
- The conservative one-loop running check with an `alpha=1/40` reset is
  **not** a continuous single-trajectory analysis; continuous running from
  the spectator-corrected `alpha_GUT` fails weak coupling to `M_Pl`.
- The width estimate is a normalized-channel bound with two-body kinematics;
  it is not a complete broken-phase Clebsch/flavour calculation.
- Manuscript quality formulae must include the hermitian-conjugate factor two.
- It does not stabilize the `vPhi/vS` hierarchy or simulate the gauged
  string network.
- It does not solve the thermal history if the full `U(1)_X` sector is
  restored after inflation.

## Highest-value independent checks

1. Reconstruct the `P=8` graph with explicit Spin(10) indices and
   two-component propagator conventions, including its overall sign and
   group normalization.
2. Fit the full `5 x 2` `X=1` heavy-light mass block and the `16_14` block
   after Spin(10) breaking; verify component lifetimes and induced flavour
   operators.
3. Run two-loop Spin(10)×`U(1)_X` RGEs with realistic GUT thresholds.
4. Evolve the dimension-five and dimension-eight Wilson tensors from
   `M_Pl` through `vPhi`, the GUT thresholds and `vS`.
5. Analyze finite-temperature restoration, entropy injection and the
   `(ell,n)=(13,-3)` string network.

## Machine audit

- v17 regression: 65 checks.
- v19 regression: 59 checks.
- v20 completion/matching: 42 checks (includes continuous-RG soft falsification).
- Full unittest discovery: 102 tests, including independent error-audit and physics-push tests.
- Independent audit: `audit_v20_errors.py` / `V20_ERROR_AUDIT.md` (imports no v20 engine).
- All engines have injected nonzero-exit tests.
- The release gate requires a warning-free, byte-stable 11-page PDF.
