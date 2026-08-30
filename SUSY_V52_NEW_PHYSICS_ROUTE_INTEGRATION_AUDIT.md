# V52 new-physics route integration audit

Status: `V52_NEW_PHYSICS_ROUTE_SELECTION__EXACT_LOW_INDEX_54_45_16_BAR16_SOURCE_SELECTED_FOR_NEXT_BUILD__EXACT_RECOMPUTED_TWO_SITE_HYBRID_LIFTS_ALL24_RELATIVE_CHIRALS_AND_HAS_FULL176_HESSIAN_KERNEL_EQUAL_GAUGE_ORBIT__HYBRID_IS_EFT_ONLY__V51_NEAR_THRESHOLD_LANDAU_KILL_EVADED__EXACT_RANK3_DOUBLE_SEESAW_AND_EXTERNAL_Z2_WITNESS__DT_WITNESS_IS_TUNED__UV_SELECTOR_NATURAL_DT_FLAVOUR_MATCHING_AND_GLOBAL_VACUUM_OPEN__NO_G2_OR_FULL_GATE_PROMOTION`

## Outcome

V52 produces a **real candidate advance**, not a complete theory.  The selected
single-site `54+45+16+bar16` source has an exact supersymmetric witness whose
Spin(10)-sector stabilizer is the SM, with no additional local infinitesimal
source modulus at that witness.  It evades V51's link and near-threshold running
failures by deleting the link sector; this is not a repair of the V51 action.
Separately, a nonlinear two-site theorem lifts a 12-dimensional V51-analog
incidence sector, and the recomputed low-index hybrid lifts all 24 of its own
relative modes with an exact 176-coordinate source+link Hessian.  That hybrid
remains an EFT without an elementary UV completion.

The minimal R1 extension also provides exact existence witnesses for a rank-three
renormalizable double seesaw, a VEV-stable external Z2 ledger, and a triplet-heavy/
one-Higgs-pair tree matrix.  The last result is an unprotected codimension-one
tuning, while the Z2 lacks a UV embedding and permits dangerous even-matter
classes unless further selection rules are supplied.

**No result is combined across action lineages. G2 remains open. The frozen
cumulative ledger retains only prior ordinary-Spin G1; the V52 candidate itself
closes 0/8 complete gates.**

## Selected route: exact conventional low-index source

- Coordinates: `131`.
- Exact ranks: `rank(Q)=33` and
  `rank(H)=98` with
  `nullity(H)=33`.
- Exact Ward/kernel result: `HQ=0` and `ker(H)=im(Q)`.
- Running: source `sum T=24`; with three families
  and one 10H, `b=7` and
  `Lambda_pole/M=1.5575e+09` at `g=0.73`.

This is the strongest foundation because its full GUT-breaking source geometry
is certified in an elementary renormalizable single-site theory.  Its minimal
extension establishes seesaw, external-Z2 and tuned DT rank existence, but does
not establish a UV-safe proton selector, natural DT splitting, a full flavour
fit, thresholds or proton decay.  If an independent V50-style U(1)F is restored,
an additional charged sector is needed to remove the leftover diagonal U(1).

## Recomputed low-index boundary-EFT hybrid

The low-index source stabilizer lies inside the PS host, so its exact endpoint
partition is `12/9/0/24`.  The hybrid alignment has rank
`24`, the gauge incidence rank is
`54`, and their 78-coordinate Goldstone block
has rank `78` with zero nullity.
For the actual 45 link plus 131 source coordinates,
`rank(Q)=54` and
`rank(H)=122` with
`ker(H)=im(Q)`.  This is a genuine recomputation for one action, not a pasted
cross-action inference.  It is a source+link result, not a whole-phenomenological-
action Hessian.  Its pole proxy (`627.619`)
lies above the nonlinear cutoff (`17.2142`),
but the link still has no elementary UV beta function.

## Minimal renormalizable R1 repair module

- Added fields: one `10H` and four Spin(10)-singlet `N` fields.
- Double seesaw: heavy rank `7`, full
  neutral rank `10`, induced-RH rank
  `3`, and light rank
  `3`.
- External Z2: every declared nonzero-VEV field is even, required displayed
  operators are allowed, and the reported gravity/SO(10)/cubic mod-2 ledgers
  vanish.  This is a conservative local ledger, not a continuous-parent or full
  discrete-gauge construction, and it does not forbid even-matter `16F^4`.
- DT matrix: color-triplet rank `6` and
  weak nullity `4`, corresponding to one
  `Hu,Hd` pair.  The condition `mH-3*kH=0`
  is codimension `1` and is not
  symmetry protected.
- Running: `sum T=31`, `b=7`,
  and formal one-loop pole ratio `1.5575e+09`
  at `g=0.73`, before any future naturalizer, messenger or UV-selector fields.

## Original nonlinear alignment lemma

The PS/SU(5) endpoint partition is `12/9/12/12`.  The gauge incidence has rank
`54` and the alignment supplies the orthogonal
rank `12`.  Their combined 66-coordinate
mass block has rank `66` and nullity
`0`.  Thus all and only the 12-dimensional
pre-alignment V51-analog sector of this new action is lifted.  The term is nonlinear and
nonrenormalizable, and retaining the V51 linear source leaves a pole only 3.51
matching scales away.

## Other serious routes

- **Flipped Spin(10) x U(1)X:** generic spinor misalignment can leave the SM. The
  primary analysis reports `b10=1` and `bXhat=67/24`; this audit's one-loop
  extrapolation assuming both normalized couplings equal `0.73` gives pole ratios
  `2.22e+64` and
  `1.12e+23`. It
  changes the gauge group and matter embedding; its 109-coordinate chiral
  Hessian, selector and natural DT mechanism are not complete.
- **Extended missing-VEV repair:** a known simple-representation construction
  supplies renormalizable DT matrices, but raises `b` to 23–24.  Its pole window
  is about 480–628, so it passes a 100x screen but not a 1000x screen and has not
  been joined to the exact V52 Hessian.

## Honest C1-C7 ledger

- `C1` — `source_subsector_pass_only`: The most general declared renormalizable 54+45+16+bar16 source is explicit; the full matter/DT/portal action census is not.
- `C2` — `new_action_locality_only`: The selected source is an ordinary local 4D action, but it is not the frozen V50 boundary regulator/action.
- `C3` — `source_subsector_exact`: The source variational domain, gauge orbit, Ward identity and physical Hessian kernel are exact.
- `C4` — `source_subsector_exact`: With canonical source Kahler metric, H-dagger-H is positive on all 98 physical source directions; the whole-theory metric is absent.
- `C5` — `open`: No V52 one-loop matching, counterterm map or matching-scale cancellation has been computed.
- `C6` — `partial_selector_ledger`: An external Z2 survives the declared VEVs and passes the displayed mod-2 ledgers, but its UV embedding, complete operator census and natural DT protection are absent.
- `C7` — `open`: No V52 component Clebsch basis or contracted physical Wilson array exists.

## Sharp continuation / rejection tests

1. **N1** — Freeze one complete R1-plus-repair field/action/selector census, construct a UV discrete-gauge embedding, and enumerate every allowed operator through dimension five. Kill test: Reject if the external Z2 cannot be UV completed or supplemented to forbid the even-matter proton-decay classes while preserving the required seesaw/Yukawa terms.
2. **N2** — Replace the tuned mH=3*kH relation by a symmetry/vacuum-enforced natural DT mechanism, then recompute the enlarged holomorphic Hessian. Kill test: Require exactly one light Higgs-doublet pair, no light colored triplet/exotic, no unprotected coefficient cancellation and no physical GUT-scale modulus.
3. **N3** — Redo the invariant/Clebsch census and derive the V52 action-to-EFT Wilson array; do not reuse the V51 array by name. Kill test: Reject any route without one action hash shared by the vacuum, regulator/matching and coefficient array.
4. **N4** — Run two-loop unification, one-loop thresholds, dressed proton decay and a rank-three flavour/neutrino fit. Kill test: Reject if perturbative control, experimental proton limits or the withheld flavour prediction fails.

## G1-G8 frozen cumulative ledger

Frozen cumulative frontier: closed flags denote reusable prior-namespace results, not same-action closure for the selected V52 candidate.

- `G1` — `closed`: Frozen V47 ordinary-Spin quotient/anomaly results remain a reusable lemma; this is not a same-action V52 reclosure. Remaining: For an independently gauged V50-style U(1)F, the R1 spinor pair leaves an extra diagonal U(1) unless another charged sector is added; the complete V52 selector/UV quotient is not frozen.
- `G2` — `open`: V52 proves an exact low-index source vacuum/Hessian and a separately frozen, fully recomputed two-site hybrid whose rank-24 alignment lifts every relative chiral and whose 176-coordinate Hessian kernel equals its gauge orbit. Remaining: The hybrid link is a nonlinear sigma-model EFT without an elementary UV completion; neither V52 action is matched to frozen V50, and no complete C1-C7 Wilson action exists.
- `G3` — `open`: The complete 131-coordinate GUT-breaking source has F=D=0, rank(Q)=33, rank(H)=98, HQ=0 and ker(H)=im(Q) at one exact rational witness. Remaining: The electroweak/DT, SUSY-breaking and soft sectors, tunnelling/global vacuum selection and the whole-action scalar Hessian are absent.
- `G4` — `open`: The minimal R1 repair has an exact renormalizable 10H tree matrix with triplet rank 6 and weak nullity 4, i.e. one Hu,Hd pair. Remaining: The result requires the codimension-one tuning mH=3*kH; no symmetry enforces it, and mu/Bmu, SUSY breaking, radiative EWSB and the full scalar vacuum are absent.
- `G5` — `open`: V52 introduces no dark/PQ claim; the four seesaw singlets have zero scalar VEV at the displayed witness and are not silently counted as a relic solution. Remaining: No dark-sector or PQ Lagrangian, reheating history, relic calculation, BBN/CMB test or cosmological likelihood is specified.
- `G6` — `open`: The selected single-site source has sum T=24; with three families and one 10H, b=7 and the one-loop pole ratio at g=0.73 is 1.5575e+09. Remaining: The hybrid's 627.6 pole ratio is only a nonlinear-tangent proxy above its NDA cutoff; a frozen elementary spectrum, two-loop running, one-loop thresholds, unification and proton-decay amplitudes have not been computed.
- `G7` — `open`: V52 identifies a source action with a controlled local quotient on which a new operator/Wilson calculation can be based. Remaining: V51 factor tensors cannot be inherited across the action change; the V52 invariant census, mediator matching, running and B/L rates are absent.
- `G8` — `open`: The minimal extension gives an exact renormalizable 10x10 double-seesaw witness: heavy rank 7, full rank 10, induced-RH rank 3 and light-neutrino rank 3. An external Z2 survives all declared VEVs and passes the displayed mod-2 ledgers. Remaining: The Z2 has no continuous-parent/full UV discrete-gauge construction; the complete operator census, charged-family fit, uncertainty propagation and withheld prediction are absent.

## Primary sources

- [Buccella and Savoy: Intermediate Symmetries in SUSY SO(10)](https://arxiv.org/abs/hep-ph/0202278)
- [Bertolini, Di Luzio and Malinsky: Minimal Flipped SO(10) x U(1) SUSY Higgs Model](https://arxiv.org/abs/1011.1821)
- [Chacko and Mohapatra: New Doublet-Triplet Splitting Mechanism](https://arxiv.org/abs/hep-ph/9810315)
- [Mohapatra and Valle: Neutrino Mass and Baryon-Number Nonconservation in Superstring Models](https://doi.org/10.1103/PhysRevD.34.1642)
- [Banks and Dine: Note on Discrete Gauge Anomalies](https://arxiv.org/abs/hep-th/9109045)
- [Nath and Syed: SO(10) Spinor and Tensor Couplings](https://arxiv.org/abs/hep-th/0109116)
- [Haba, Mimura and Yamada: Proton Decay in Lean SUSY SO(10)](https://arxiv.org/abs/1904.11697)

Core SHA-256: `9ffa78a63afd3ff0a1e948ff2deffc701f229c5b7cae46b354d6cf5ebecb3df8`
