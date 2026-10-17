# Theory confirmation verdict - v20

**Status:** `THEORY_CONFIRMATION_AUDIT_COMPLETE__GATES_OPEN`
**Overall state:** `OPEN`
**Classification:** `AUTHORITATIVE_GATES_OPEN`
**Decision:** `WITHHOLD_APPROVAL`

WITHHOLD APPROVAL. The audit succeeds and the gauged-U(1)_X model contract is attested by bound external SARAH execution evidence. G1, G2, G3 (SM Pati-Salam benchmark family, scoped), G4 (at the G3 witness benchmark, tree level) and G5 are closed, which meets decision D3, but decision D-E holds approval of the internal-candidate tier until G7 is CLOSED, and decision U3 never approves it. By decision U3 the internal candidate is released: certified tree-level vacuum, excluded by G8 flavour at 8.9 sigma (minimum load-bearing pull 8.86 sigma with a 10% theory term, 13.24 sigma on experimental errors alone; witness-branch renormalizable Yukawas, tan-beta-independent tests, 1e9-2e16 GeV), not approved (CKM = 1, m_t = m_b, m_d = m_e; G8_SM_PATI_SALAM_FLAVOUR_NOGO_V20.json). G6 is open and G7-G8 remain blocked (sub-M_I coloured states and positivity beyond tree level, electroweak symmetry breaking, RG-anchor content, the Higgs quartic, Yukawas and proton decay), so no internal, conditional-benchmark, full-phenomenology, empirical, or exclusion claim is approved; the whole model is neither validated nor excluded by a proof-grade certificate. Program verdict (decision U1): NOT VIABLE as a complete description of nature under the declared standards; the no-go is method-limited at G3 x G8.

## Approval levels

- Internal candidate: **False**
- Internal-candidate gate (D3 and D-E): caveats_cleared = False (G4_closed = True; closing-track downstream caveats resolved = False; G7_closed = False; held pending G7 = True; approval disabled by decision U3 = True)
- Internal-candidate release: RELEASED (decision U3): certified tree-level vacuum, excluded by G8 flavour at 8.9 sigma (minimum load-bearing pull 8.86 sigma with a 10% theory term, 13.24 sigma on experimental errors alone; witness-branch renormalizable Yukawas, tan-beta-independent tests, 1e9-2e16 GeV), not approved. The G3 witness vacuum is certified at tree level (G1-G5 CLOSED; G4 at the witness benchmark r0 = 1/5, x0 = 1, kappa = -r0/4); on this witness branch the renormalizable Yukawas give CKM = 1, m_t = m_b and m_d = m_e, and across 1e9-2e16 GeV the minimum load-bearing pulls of the tan-beta-independent tests are 13.24 sigma (experimental errors alone) and 8.86 sigma (with a 10% theory term) (G8_SM_PATI_SALAM_FLAVOUR_NOGO_V20.json, fields data.minimum_load_bearing_pull_raw_sigma and data.minimum_load_bearing_pull_conservative_sigma; the label's 8.9 sigma is the conservative pull rounded to 0.1 sigma). The structural obstruction (g8_sm_pati_salam_structural_obstruction_v20) extends the flavour-dead relations M_e = phase x M_d^T and CKM = 1 (tan beta = 1) to every vacuum of the degree-2-SOS-certified witness family at the dimension-4 level. The internal-candidate tier is not approved (decision U3 keeps internal_candidate_approved False on every path); the release is neither phenomenological validation nor a proof-grade exclusion of the SO(10) x U(1)_X contract.
- Internal-candidate tier: **RELEASED_NOT_APPROVED**
- Conditional benchmark: **False**
- Full phenomenology: **False**
- Empirical realization: **False**
- Whole-model exclusion: **False**

## Tiers

- INTERNAL_CANDIDATE: **RELEASED_NOT_APPROVED** - internal consistency of the attested model contract: G1, G2 and G3 CLOSED, decision D3 satisfied (the closing G3 track's downstream caveats resolved, or G4 CLOSED) and, by decision D-E, G7 CLOSED; not phenomenology; by decision U3 never approved (a candidate that meets D3 may be released, RELEASED_NOT_APPROVED)
- CONDITIONAL_BENCHMARK: **WITHHELD** - a numerically safe benchmark region under extra portal assumptions on the current contract; withheld because the aligned benchmarks were computed under the superseded no-X contract
- FULL_PHENOMENOLOGY: **WITHHELD** - every G1-G8 gate CLOSED and the authoritative full-model gate validated
- EMPIRICAL_REALIZATION: **NOT_ESTABLISHED** - full phenomenology plus a real empirical discovery
- WHOLE_MODEL_EXCLUSION: **NOT_ESTABLISHED** - a proof-grade exclusion by the authoritative full-model gate

## Program verdict (decision U1)

**Code:** `NOT_VIABLE_UNDER_DECLARED_STANDARDS__NO_GO_METHOD_LIMITED_AT_G3_X_G8`

Program verdict (user decision U1): SO10Z17AxionV20 is a certified tree-level vacuum with exact no-go lemmas and numerical no-go evidence, and it is NOT VIABLE as a complete description of nature under the declared standards (exact G3 vacuum certification and the G1-G8 gate criteria of G1_G8_GATE_LEDGER_V20); the no-go is method-limited at G3 x G8. EXACT: every vacuum of the degree-2-SOS-certified witness family is flavour-dead at the dimension-4 level (M_e = phase x M_d^T, CKM = 1 at tan beta = 1; g8_sm_pati_salam_structural_obstruction_v20). EXACT relations, NUM data comparison: on the witness branch the renormalizable Yukawas give CKM = 1, m_t = m_b and m_d = m_e, which the tan-beta-independent tests exclude (G8 Route C; g8_sm_pati_salam_flavour_nogo_v20). Research-recorded, not a committed certificate: no certification method has been demonstrated for the flavour-capable vacuum orientations (degree-2 SOS leaves flat Phi-sector directions at the G3221/G3211 orientations; rescue-study NUM, Phi sector only). NUM: G6 is not closable on the SOS-certified witness family at one loop with tree-level matching (sampled region; only the tree-matching statement is robust; g6_sm_pati_salam_remnant_rg_nogo_v20); on the decoupled-singlet benchmark BM-DA1 (U1 root held fixed; gauge + matter running) a 120_H, a second 126bar and vectorlike pairs (also with a 45_H) fail the reduced-Planck Landau criterion already at two loops, and the other analysed additions (10_F, a real or complex 45_H) pass at two loops and fail at three loops, as does the contract content itself on that root (three-loop verdict convention- and threshold-limited; omitted Yukawa terms not conservative for a fail statement; g7_decoupled_singlet_benchmark_evidence_v20). The attested contract is a truncation (g1_contract_truncation_scope_v20). Gate statuses are unchanged (G1-G5 CLOSED, G6 OPEN, G7 BLOCKED, G8 BLOCKED); this is not a proof-grade exclusion of the SO(10) x U(1)_X contract, and the whole model is neither validated nor excluded by any gate.

## Scientific blockers

- `G6_NOT_CLOSED`
- `G6_SUB_M_I_COLOURED_STATES_AND_POSITIVITY_WITHOUT_EWSB`
- `G7_NOT_CLOSED`
- `G7_RG_ANCHOR_CONTENT_AND_HIGGS_QUARTIC_MATCHING`
- `G8_NOT_CLOSED`
- `G8_YUKAWA_SECTOR_AND_PROTON_DECAY_MEDIATORS`
- `GAUGED_U1X_G6_G7_G8_CLOSURE_REQUIRED`
- `PROTON_READINESS_complete_mass_basis_gauge_flavour_wilson_coefficients`
- `PROTON_READINESS_complete_scalar_triplet_masses_mixings_and_yukawas`
- `PROTON_READINESS_full_component_vacuum_and_competing_extrema`
- `PROTON_READINESS_physical_phases_and_interference`
- `PROTON_READINESS_uncertainties_propagated`
- `PROTON_READINESS_unique_physical_XY_masses`
- `PROTON_READINESS_unique_vev_ratios_from_full_potential`
- `PROTON_READINESS_validated_two_loop_component_threshold_matching`

## Historical scope

The preserved Option-C G1-G3 calculations are non-authoritative
subtheorems of the superseded no-X potential.

## Correct public claim

> The authoritative gauged-U(1)_X model contract is attested by a manifest/log-bound external SARAH 4.15.3 execution, and G1, G2, G3, G4 and G5 are closed. G1 and the model contract attest a truncation: 10 of the 26 renormalizable fermion bilinears allowed by SO(10) x U(1)_X x Z17 are declared (labels in the model file's field basis; no field redefinition removes the truncation), and the 16 omitted ones are not protected by any U(1) or multiplet-diagonal phase symmetry of the declared Lagrangian (g1_contract_truncation_scope_v20). G3 closed on the SM Pati-Salam benchmark family: the exact SM-preserving global vacuum of the declared exact-X potential's 27-parameter benchmark with the light-doublet deformation eps > 0, unique modulo SO(10) x U(1)_X x accidental U(1)_PQ; tuned DT/M_I relations; caveats routed downstream; whole model neither validated nor excluded. G4 is CLOSED at the G3 witness benchmark (r0 = 1/5, x0 = 1, kappa = -r0/4, every 0 < eps < 599/50), tree level (g4_sm_pati_salam_physical_quotient_v20 through g4_sm_closure_binding_v20): SO(10)xU(1)_X rank 34 (gauge quotient 452) and SO(10)xU(1)_XxPQ rank 35 (massive/transverse quotient 451); on the gauge quotient the Hessian is 451/1/0 with the physical axion as its only zero mode, the 35 zero modes of the full Hessian are 34 eaten Goldstones and the axion, and no mode is negative; as eps -> 0 the only extra zero modes are one SM doublet (1,2)_{1/2}, lifted at quartic order by lambda_eff = 127/64. The axion is massless only for the renormalizable PQ-neutral benchmark potential: the QCD anomaly and PQ-violating operators such as Phi17^4 conj(S)^17/M_Pl^17 give it a mass. The internal candidate is RELEASED (decision U3): certified tree-level vacuum, excluded by G8 flavour at 8.9 sigma (minimum load-bearing pull 8.86 sigma with a 10% theory term, 13.24 sigma on experimental errors alone; witness-branch renormalizable Yukawas, tan-beta-independent tests, 1e9-2e16 GeV), not approved. The G3 witness vacuum is certified at tree level (G1-G5 CLOSED; G4 at the witness benchmark r0 = 1/5, x0 = 1, kappa = -r0/4); on this witness branch the renormalizable Yukawas give CKM = 1, m_t = m_b and m_d = m_e, and across 1e9-2e16 GeV the minimum load-bearing pulls of the tan-beta-independent tests are 13.24 sigma (experimental errors alone) and 8.86 sigma (with a 10% theory term) (G8_SM_PATI_SALAM_FLAVOUR_NOGO_V20.json, fields data.minimum_load_bearing_pull_raw_sigma and data.minimum_load_bearing_pull_conservative_sigma; the label's 8.9 sigma is the conservative pull rounded to 0.1 sigma). The structural obstruction (g8_sm_pati_salam_structural_obstruction_v20) extends the flavour-dead relations M_e = phase x M_d^T and CKM = 1 (tan beta = 1) to every vacuum of the degree-2-SOS-certified witness family at the dimension-4 level. The internal-candidate tier is not approved (decision U3 keeps internal_candidate_approved False on every path); the release is neither phenomenological validation nor a proof-grade exclusion of the SO(10) x U(1)_X contract. G6 is open and G7-G8 remain blocked. G1-G8 approval is withheld. Program verdict (decision U1, G1_G8_GATE_LEDGER_V20.json): NOT VIABLE as a complete description of nature under the declared standards; the no-go is method-limited at G3 x G8; this is not a proof-grade exclusion of the SO(10) x U(1)_X contract. Historical Option-C calculations are scoped subtheorems and neither validate nor exclude the gauged model.
