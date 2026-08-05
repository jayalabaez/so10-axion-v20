# Next executable calculation: full non-SUSY scalar potential and Hessian

## Source correction

The former E/F/J/X Clebsch-normalization plan is retired.

Aulakh Appendix E/F/J/X are mixed chiral-gauge fermion/gaugino matrices. Their `g` is the SO(10) gauge coupling, not the superpotential `gamma` coupling. They cannot be used to define a non-supersymmetric scalar `lambda4` normalization or threshold.

The obsolete targets are forbidden:

- no E/F/J/X slot matching for scalar closure;
- no `gamma_eff/lambda4` extraction from E/F/J/X;
- no resurrection of the withdrawn `8.8e29` bound;
- no `EFJX_CGC_NORMALIZATION_INPUT_V20.json` closure artifact.

## Completed direct tensor work

The direct scalar invariant

`lambda4 S H_i Phi_jklm Sigmabar_ijklm / 4! + h.c.`

has been implemented as a canonically normalized `10 x 126` tensor map using the complete `(P,A,W)` singlet basis.

Its analytic singular branches are:

1. `sqrt((P+A/sqrt(3))^2+4 W^2/3)`, multiplicity 3;
2. `abs(P-A/sqrt(3))`, multiplicity 3;
3. `abs(A+W/sqrt(2))`, multiplicity 2;
4. `abs(A-W/sqrt(2))`, multiplicity 2.

The independent Aulakh VEV dictionary is

`P=p`, `A=sqrt(3)a`, `W=sqrt(6)omega`,

and the direct spectrum matches the genuine `gamma`-dependent chiral triplet/doublet Clebsch magnitudes.

## Completed scoped portal M² insertion

Repository Aulakh-style VEVs are traced into the canonical `(P,A,W)` dictionary and the portal block

`M^2_{H–Σ̄} = lambda4 v_S T_Phi`

is inserted into a scoped non-SUSY `10 x 126` mass-squared sector (`direct_phi_h_sigmabar_portal_m2_block_v20.py`).

This closes the VEV-dictionary trace and the *scoped* portal bilinear insertion only. It does **not** close the complete invariant ring, full component projection, global Hessian, or issue #86.

## Completed exact portal Schur gate

The holomorphic block `B = lambda4 vS T_Phi` is embedded in the exact 272-real-mode Hessian for `(Re H, Im H, Re Σ̄, Im Σ̄)` with positivity criterion

`sigma_max(A^{-1/2} B C^{-1/2}) < 1`.

Diagonal `A = M²_H` and `C = M²_Σ̄` remain open inputs.

## Completed diagonal-channel inventory scaffold

Classic Kronecker channels that can source those diagonals are inventoried and PQ/X/Z17-filtered in

`diagonal_h10_sigmabar_m2_channel_inventory_v20.py`:

- `210×210`: 45, 54, 210, 1050 (+ cubics);
- `210×126`: 10, 120, 320, 126;
- `126` quartics: 54, 1050, 4125;
- `10_H` via isotropic and 54 projections.

Cartesian second-derivative slots are recorded as `OPEN_AWAITING_CG`. Index CG tensors are **not** invented.

## Completed isotropic + 54 partial Schur A/C fill

`diagonal_h10_sigmabar_m2_isotropic_54_slots_v20.py` fills inventory slots that
already have repository support:

- isotropic H10 / Σ̄ soft-norm seeds;
- 210-norm portals into H10 and Σ̄.

The former isotropic `54-locking` mass seed that used `H10_eff=M_I` is
**withdrawn** (PR #97): `10_H` has no PS/SM singlet, and
`P_54(Delta_R,Delta_R)=0` on the selected vacuum. Selected-vacuum `lambda4`
radial/phase amplitudes are likewise null (`T_Phi Delta_R=0`). Partial
positive diagonals therefore come only from soft/norm and 210-norm seeds.
Channels 120/320/1050/4125 remain open.

## Completed selected-vacuum phase-Hessian revalidation

Root `A_54=0` and κ-only multi-operator phase Hessian consumers have been
rewritten against the exact nulls.

## Corrected: the "extra flat phase" was a gauge Goldstone

The unquotiented reduced Hessian on `(φ_Δ,φ_10,φ_S)` has rank one and two
nulls when `A_κ>0`. One null is the eaten Pati–Salam `Z'_R/B-L` orbit
`q=(1,0,0)`. After that gauge quotient the physical sector `(φ_10,φ_S)` has

- one massive CP-odd eigenvalue `5 A_κ`;
- exactly one physical null `(1,-2)`, the PQ axion;
- **no** additional physical non-axion flat phase.

All-orders: B−L neutrality forces `d=0` and PQ/Z17 then forces every nonzero
selected-vacuum polynomial phase vector parallel to `κ`. Finite dim-6/7/8
zeros corroborate this identity; they are not required to prove physical
phase closure of the reduced sector.

Core pre-quotient consumers (`multi_operator_phase_hessian`,
`gauge_fixing_goldstone_eating`, `phase_operator_independence_audit`) and
UV/CP descendants (`uv_cp_phases_from_potential`, `component_lift_210_126_10`,
`uv_delta_i_cp_reality_principle`) are source-rewritten against the Z' quotient.

## Completed physical 54-channel Hessian at hEW=174 GeV

`physical_54_component_hessian_at_hew_v20.py` differentiates the charge-allowed
54-locking operator on the physical electroweak background:

- `P54(hEW,hEW)` is nonzero;
- selected-vacuum amplitude `⟨P54(hEW,hEW), P54(Δ_R,Δ_R)⟩ = 0`;
- `OPEN_H10_54` remains exact zero from `P54(Δ_R,Δ_R)=0`;
- `OPEN_126_54_LOCKING` is a holomorphic `ΣΣ` kernel on the Δ_R eigenspace,
  suppressed by `(hEW/M_I)^2`, and is **not** a positive Hermitian Schur C seed.

## Completed OPEN_MIXED_126 PS-singlet Sigmabar M² fill

`diagonal_sigmabar_m2_mixed_126_ps_singlet_v20.py` fills inventory slot
`OPEN_MIXED_126` (`210_H 126bar† 126bar`) from the guaranteed PS-singlet
reduction `eff_210_for_126 = |ω+a|+|p|`, giving a positive Hermitian Schur C
seed. Full Cartesian CG, second multiplicity, and channels 120/320/1050/4125
remain OPEN.

## Completed Goldstone nullspace projector (orbit embedding)

`so10_goldstone_nullspace_projector_v20.py` builds exact projectors
`P_G` (trace 33) and `P_phys` (trace 681) on the orbit-certificate embedding
`(210_PS ⊕ 126bar)`, and validates Hessian projection on synthetic spectra.
Full dynamical component Hessian remains OPEN.

## Completed hEW-extended gauge orbit (36 Goldstones)

`so10_gauge_orbit_with_hew_v20.py` stacks the physical electroweak VEV
`⟨H⟩=hEW·ê` (direction index 6) into the differential-form tangent with
`(210_PS, Δ_R)`. Orbit rank rises from 33 to **36**, residual stabilizer
dimension **9** (`SU(3)_c×U(1)_EM`). Extended projectors are validated on
synthetic Hessians in the 724-dim embedding
`(210 ⊕ 126bar_ℂ ⊕ H10)`. Spectators `S`, `Φ₁₇` remain outside the orbit.

## Completed partial dynamical Hessian + hEW Goldstone gate

`partial_dynamical_hessian_hew_goldstone_gate_v20.py` builds a form-basis
positive-diagonal M² skeleton from the isotropic/norm A/C seeds (including
`OPEN_MIXED_126`) on the 724 embedding, applies the exact 36-Goldstone
`P_phys`, and proves the projected spectrum has 36 zeros / 688 positive /
0 negative modes. The Aulakh Schur 272 portal Hessian is recorded upstream
but **not** identified with the form basis (Cartesian portal basis map OPEN).

## Completed Hodge 126bar C-embedding and portal lift

`hodge_126bar_c_embedding_portal_lift_v20.py` places physical diagonal
`C₁₂₆` into ambient ℝ⁵⁰⁴ via the canonical anti-self-dual (`*Σ=−iΣ`) frame
shared with the Schur portal tensor, proves `Δ_R` lies in that subspace
(projector residual 0), and lifts holomorphic `B=λ₄ v_S T_Φ` to
H10_real↔504 mixing. The upgraded partial dynamical Hessian gate now uses
Hodge-placed C + lifted B under the 36-Goldstone projector. Im H remains
outside the 724 orbit embedding.

## Completed Im H + S/Φ₁₇ extended form-basis Hessian

`extended_form_basis_hessian_imh_spectators_v20.py` upgrades the embedding to
dim **738** (`210 ⊕ 504 ⊕ ℂ¹⁰ ⊕ ℂ_S ⊕ ℂ_Φ₁₇`), pads the hEW tangent so the
Goldstone rank stays **36**, inserts the full holomorphic portal on
`(Re H, Im H)`, and places reduced-radial soft masses for S and Φ₁₇.
Projected spectrum: 36 zeros / 702 positive / 0 negative. PQ axion quotient
remains OPEN.

## Completed PQ-axion quotient on the extended Hessian

`extended_hessian_pq_axion_quotient_v20.py` injects the κ phase Hessian into
`(Im H[hEW], Im S)`, realizes the exact PQ null `(φ_10,φ_S)∥(1,-2)`, and
removes it together with the 36 SO(10) Goldstones. Combined projected
spectrum: **37 zeros / 701 positive / 0 negative**. UV value of `κ` and full
component Hessian remain OPEN.

## Completed OPEN_MIXED_10 portal absorption + closure ledger

`diagonal_mixed_10_portal_absorption_v20.py` proves the charge-allowed cubic
`210·126†·10` opens H–Σ mixing through the same `T_Φ` as portal
`B=λ₄ v_S T_Φ` (absorbed; not a new diagonal). 
`filled_mass_ps_sm_irrep_spectrum_v20.py` assigns PS multiplicities to the
isotropic A/C seeds. `scalar_theory_closure_ledger_v20.py` scores G1–G8.

## Completed OPEN_210_RADIAL/CUBIC PS-singlet fill + scoped BFB

`diagonal_210_radial_cubic_ps_singlet_v20.py` fills the form-basis 210 mass
from the reduced `P_210` curvature (radial + Aulakh cubics) at `hEW=174`.
`scoped_bfb_boundedness_gate_v20.py` aggregates reduced-quartic BFB, Schur
PD, and the Goldstone+axion-projected skeleton. Closure ledger:
**0 CLOSED / 5 PARTIAL (G2–G6) / 3 OPEN**. Theory remains **BLOCKED**.
(Historical note at PS-singlet fill time was 4 PARTIAL / 4 OPEN; G6 later
advanced via the published threshold bundle.)

## Completed (210⊗210)→54 and →45 combinatorial projectors

`so10_210_to_54_projector_v20.py` builds the exact SO(10) bilinear
`(210⊗210)→54` by triple-contracting two four-forms and applying
`P_54=Sym_0`. On the selected `(p,a,ω)` vacuum this yields a nonzero
`||(ΦΦ)_54||` and a PS-singlet curvature seed
`ΔM² ≈ λ̃ ||Q||_F² / ||Φ||²` for `OPEN_210_CHANNEL_54` (off-singlet CG OPEN).

`so10_210_to_45_projector_v20.py` uses the same kernel with
`P_45=(M−Mᵀ)/2`. Swap identity proves `P_45(M(Φ,Φ))=0` for every Φ.
Stronger: the full Aulakh PS-singlet span `{p,a,ω}` has vanishing
**antisymmetric** 45 bilinears among itself. That does **not** close the
source-correct **Sym²(210)→45** quartic (`so10_210_symmetric_45_source_projector_v20`,
gr-qc/9507053 Eq. 2.8): same-field / selected-singlet span are nontrivial
there. `OPEN_210_CHANNEL_45` is therefore
`PARTIAL_ANTISYM_VANISHES__SYMMETRIC_SOURCE_REOPENED`. Antisym mixed
singlet⊗off-singlet remains nontrivial and OPEN.

`source_corrected_scalar_dependency_gate_v20.py` supersedes the old
“residual = 770+1050+4125” 1050-blocker as incomplete (true Sym² residual
after 1/45/54/210 includes 1050+1050bar+4125+8910+5940+770). Downstream
scalar ledger / BFB / Hessian statuses require revalidation after the
source-normalized 45 enters the potential. Do not invent 120/320/1050/4125.

These dual-channel maps are wired into `diagonal_210_radial_cubic_ps_singlet_v20`
and absorbed in the isotropic inventory.

## Completed (210⊗210)→210 self-map + Goldstone SM root catalog

`so10_210_to_210_self_map_v20.py` builds the double-contracted Alt₄ bilinear
`Ξ(Φ,Ψ)∈∧⁴≅210`. On the selected vacuum `Ξ∥Φ` (overlap ≈0.997, mostly radial)
with seed `ΔM²≈λ̃‖Ξ‖²/‖Φ‖²`. Notably `Ξ(p,p)=0` while `a` and `ω` self-maps
are nontrivial. Seed is diagnostic only (not double-counted into isotropic
`m²_210`).

`so10_goldstone_sm_root_catalog_v20.py` SVD-catalogues the 45 adjoint planes
on `(210,Δ,hEW)`: rank **36** Goldstones, stabilizer **9**. Stabilizer L2
weights split as **8 (so6_color) + 1 (so4_weak)** = `SU(3)_c×U(1)_EM`, with
unbroken generators as linear combinations (only `M_89` has a vanishing
column alone). Cartans `T3_L/R` recorded. Dynamical masses remain OPEN.

## Completed effective PQ axion potential + co-positivity BFB

`effective_pq_axion_potential_v20.py` integrates the heavy CP-odd mode of
`V_κ=(5 A_κ/2) h²` at tree level, proving `V_eff(a)=0` in the κ truncation,
records `f_a=√(hEW²+4 v_S²)`, and applies the all-orders selection rule to
show radial 210/126 integration cannot lift the axion without new PQ
breaking. UV `κ` remains OPEN.

`reduced_quartic_copositivity_bfb_v20.py` certifies spectral PD and
co-positivity of the reduced five-amplitude quartic Λ (pairwise + Monte-Carlo
on the simplex) together with the Schur portal margin. Wired into
`scoped_bfb_boundedness_gate_v20`. Full-ring BFB remains OPEN.

## Completed reduced competing-extrema census + UV κ constraint

`reduced_polynomial_competing_extrema_v20.py` censuses nine amplitude points
on the reduced polynomial: selected `hEW=174`, `λ₄=0` is locally PD;
historical `λ₄` is tachyonic. V_total ranking among fixed probes is
diagnostic only (not free extrema). Full-ring extrema remain OPEN.

`uv_kappa_stationarity_constraint_v20.py` evaluates physical
`A_κ = |κ| M_I hEW² v_S` from the finite-κ stationarity window, withdraws the
`M_I`-equal proxy, and records that κ is constrained but **not** UV-unique.

## Completed physical A_κ wiring + 1050 irreducible blocker

`extended_hessian_pq_axion_quotient_v20.py` now injects **physical** `A_κ`
(from `uv_kappa_stationarity_constraint_v20`) instead of diagnostic
`min(A,C)/5`. Spectrum gate remains 37 zeros / 701 positive / 0 negative.
`effective_pq_axion_potential_v20` uses the same physical `A_κ`.

`open_210_channel_1050_irreducible_blocker_v20.py` proved residual after
1/54/210 mixes ≥770⊕1050⊕4125 (`OPEN_AWAITING_YOUNG_CG`). That residual
census is **incomplete** once Sym²→45 is restored: see
`so10_210_symmetric_product_source_audit_v20` / dependency gate
(true residual after 1/45/54/210 includes 1050+1050bar+4125+8910+5940+770).
No CG invented; 1050 remains OPEN.

## Completed off-singlet mixed-45 census + free extrema + unique-κ probes

`open_210_channel_45_off_singlet_census_v20.py` censuses vacuum⊗off-singlet
`(Φ⊗δΦ)_45` on the 207-dim PS complement (all modes source nonzero bilinears;
diagnostic seed only; mode-by-mode SM irrep CG OPEN). Wired into
`diagonal_210_radial_cubic_ps_singlet_v20` / isotropic inventory as PARTIAL.

`reduced_amplitude_free_extrema_v20.py` freely minimizes `V₄+V_int` on
`(P,Δ,S,Φ)` at fixed `hEW=174`, `λ₄=0`: with stationarity-restoring soft δm²
the selected vacuum is recovered; without soft amplitudes can drift to bounds.
Full-ring extrema remain OPEN.

`unique_kappa_principle_probe_v20.py` compares soft-norm, portal-matching, and
finite-κ-window κ values; they disagree, so `uv_kappa_uniquely_determined=false`.

## Completed off-singlet-45 SM Cartan quantum numbers

`open_210_channel_45_off_singlet_sm_quantum_numbers_v20.py` labels all 207
`(Φ⊗δΦ)_45` images by so6/so4/cross dominance and `Q=T3_L+T3_R=-i M_67`
adjoint activity (Cartan only — no Young CG). Empirically all modes are
Q-charged under the activity cut; most are cross-sector dominant. Status
`PARTIAL_SM_QUANTUM_NUMBERS_READY`; CG coefficients remain OPEN.

## Completed Schur↔form portal ID + ring scaffold + partial G6

`schur_form_basis_portal_identification_v20.py` proves Schur 272 portal
blocks equal form-738 pullback/2 (`EᵀE=2I`); 724 omits Im H; spectators
outside Schur support. Cartesian portal basis map CLOSED for shared B.

`charge_allowed_invariant_ring_scaffold_v20.py` emits
`FULL_MIXED_REP_INVARIANT_RING_V20.json` (scaffold; independence OPEN;
cg_ready READY/PARTIAL/MISSING; no invented CG).

`partial_g6_threshold_spectrum_certificate_v20.py` bundles isotropic PS
multiplicities + Aulakh Table-1/R + Susyno gauge UV. Ledger G6 → PARTIAL.
Closure scoreboard: **0 CLOSED / 5 PARTIAL (G2–G6) / 3 OPEN**.

## Completed ring independence + off-singlet-54 census + hierarchy soft matching

`charge_allowed_ring_linear_independence_certificate_v20.py` certifies
PARTIAL independence on charge×dim subspaces via grading + monomial
exponent SVD rank (full ring with CG still OPEN).

`open_210_channel_54_off_singlet_census_v20.py` censuses vacuum⊗off-singlet
`(Φ⊗δΦ)_54` on the 207-dim complement (published `P_54` only).

`technically_natural_hierarchy_soft_matching_v20.py` quantifies
`hEW/M_I`, `|δm²|/M_I²`, and matched `M_{1/2}` vs `|κ|M_I` at physical
hEW (full stationarity / unique κ remain OPEN).

## Correct next goal

**Immediate:** insert the source-normalized pure-210 Sym²→45 / 54 / 210 / 1050
densities (from `so10_210_source_quartic_basis_v20`, scored on the selected
vacuum by `source_210_quartic_norm_identity_v20`) into the reduced/mixed
potential → BFB / Hessian revalidation. Pure-210 identity is CLOSED; full
mixed G1 remains OPEN. Do **not** claim whole-model validation.

Theory completion still requires transcribed CG for 120/320/1050/4125 and
off-singlet mixed-45 **CG coefficients** (G1), mode-by-mode diagonals (G2),
complete stationarity/hierarchy (G3), the full dynamical Hessian artifact
(G4), full-ring BFB (G5), complete thresholds from full M² (G6), then
two-loop RGE and unique τ_p (G7–G8).
Do not invent missing CG and do not reopen a reduced-sector phase hunt.

## Executable sequence

1. **Complete invariant ring**
   - Enumerate every charge-allowed independent scalar operator through the declared engineering dimension.
   - Prove linear independence and record Hermitian-conjugation conventions.
   - Transcribe missing CG tensors (especially 120, 320, 1050, 4125) into the Cartesian basis.
   - Prefer operators with nonzero tensor projection on the actual `(Delta_R,hEW,S,Phi)` vacuum for phase locking.
   - Next without invented tables: `FULL_TENSOR_PROJECTED_POTENTIAL_V20.json`
     scaffold; off-singlet-210 vacuum census with published self-map;
     READY-subspace BFB only.

2. **Full component projection**
   - Project every invariant into canonical Pati-Salam and Standard Model component fields.
   - The direct `lambda4 vS T_Phi` off-diagonal block is already available as a scoped insertion; extend it to the full projected potential.
   - Fill diagonal `H10` and `Sigmabar126` mass-squared matrices from charge-allowed channels.
   - Do not import SUSY fermion/gaugino matrices as scalar masses.

3. **Stationarity and hierarchy**
   - Solve all stationarity equations with `hEW=174 GeV`.
   - Trace every numerical VEV and coupling to the canonical `(P,A,W)` convention.
   - Demonstrate a technically stable hierarchy mechanism.

4. **Gauge-projected component Hessian**
   - Construct the complete real scalar `M^2` matrix.
   - Remove exactly 36 gauge Goldstones (SO(10)→U(1)_EM; SM-only was 33).
   - Require every remaining eigenvalue to be positive.
   - Partial form-basis gate with Hodge-placed C, full (Re/Im H) portal B,
     S/Φ₁₇ soft blocks, κ phase block, and combined 36 Goldstone + 1 PQ-axion
     projector is in place on dim 738 (37 removed / 701 physical).

5. **Global vacuum and boundedness**
   - Check all enumerated competing extrema.
   - Prove the target vacuum is lower.
   - Apply a boundedness certificate to the complete potential.

6. **Physical thresholds and downstream predictions**
   - Emit physical triplet, doublet and singlet masses with multiplicities and SM quantum numbers.
   - Only then run full two-loop threshold evolution and calculate proton decay.

## Required closure artifacts

- `FULL_MIXED_REP_INVARIANT_RING_V20.json`
- `FULL_TENSOR_PROJECTED_POTENTIAL_V20.json`
- `FULL_NONSUSY_VACUUM_HESSIAN_V20.json`

The direct tensor, scoped portal block, exact Schur gate, classic diagonal-channel inventory, corrected isotropic/norm A/C seeds, and selected-vacuum A54/λ₄ null revalidation of the reduced phase Hessian are in place. Missing CG transcription and the complete scalar theory remain open.
