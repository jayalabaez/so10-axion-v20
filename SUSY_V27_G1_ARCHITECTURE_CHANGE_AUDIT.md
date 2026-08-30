# SUSY V27 G1 architecture-change audit

- Status: `V27_G1_ARCHITECTURE_CHANGE_AUDIT_COMPLETE__NO_SINGLE_UV_CANDIDATE_PASSES__V26_DYNAMICAL_GS_EFT_RETAINED__FULL_G1_OPEN`
- Core: `d97af356e9f2e2d7d0d2001a2a3b60027e6845cf4266d6f8c7b36b539281a58e`
- Full G1 closed: **no**.
- New-physics routes tested: **6**; complete routes: **0**.

## Outcome

New physics was allowed without preserving the V24 architecture. Six independent full-G1 requirements were applied to every candidate. No single theory supplies all six, and partial results from unrelated theories cannot be combined without an explicit UV-to-EFT derivation.

V26 remains the strongest executable continuation: it has a dynamical anomaly-matched GS racetrack, an exact local supersymmetric Minkowski modulus point, and preserved residual matter parity. It is still a bottom-up supergravity EFT whose levels, condensate thresholds, complete branch quotient, and all-order coefficients are inputs.

## Route-by-route result

- `V26_BOTTOM_UP_GS_RACETRACK`: 1/6 requirements pass; failed: R1, R2, R3, R4, R5.
- `RIGID_DBRANE_PS_2026`: 1/6 requirements pass; failed: R2, R3, R4, R5, R6.
- `TYPE_IIA_PS_FLUX_2006`: 1/6 requirements pass; failed: R2, R3, R4, R5, R6.
- `HETEROTIC_PS_GGSO_2010`: 1/6 requirements pass; failed: R2, R3, R4, R5, R6.
- `D6_PS_HIDDEN_RACETRACK_2004`: 1/6 requirements pass; failed: R2, R3, R4, R5, R6.
- `ANOMALY_FREE_SELECTOR_REPLACEMENT`: 0/6 requirements pass; failed: R1, R2, R3, R4, R5, R6.

## Strongest microscopic alternative

The 2026 rigid D-brane Pati--Salam models are genuine string constructions with full perturbative spectra and string consistency checks. They still do not close this gate. Their Kähler moduli remain unfixed at the constructed stage, and the paper explicitly leaves Yukawa couplings, soft terms, and twisted-sector Yukawa rules for future work. Their spectrum and selection rules also do not match `PSZ4RZ11SUSYV24`.

Primary source: [Three-family supersymmetric Pati--Salam flux models from rigid D-branes](https://arxiv.org/pdf/2512.21141). The relevant limitations are stated in its conclusion on pages 51--52.

Older string routes do not fill the gap: the 2006 Type-IIA construction says detailed moduli stabilization and exotic masses are deferred; the heterotic GGSO work classifies exact spectra but does not supply the stabilized operator-matched vacuum; and the 2004 D6 models contain extra exotics and only partial moduli stabilization.

## Exact stopping rule

Full G1 can be promoted only when one candidate passes all of: microscopic source; complete selector/level/anomaly derivation; normalized all-order operator and coefficient matching; stabilization of every modulus and physical branch quotient; hidden-threshold and residual-`Z2` audit; and executable component matching.

The generated `SUSY_V27_G1_UV_COMPLETION_INPUT_SCHEMA.json` makes those required inputs machine-readable. It prevents another EFT ansatz or literature scaffold from being mislabeled as a completed UV theory.

## Decision

Do not replace V24 with an unmatched string model and do not mark G1 closed. The scientifically valid enhancement is the V26 dynamical GS EFT plus this V27 UV acceptance audit. Actual closure now requires new external microscopic data, not another unconstrained local operator or invented coefficient.

Other primary sources: [Type IIA Pati--Salam flux vacua](https://arxiv.org/abs/hep-th/0601064), [heterotic Pati--Salam classification](https://arxiv.org/abs/1007.2268), and [intersecting D6-brane Pati--Salam models](https://arxiv.org/abs/hep-th/0403061).
