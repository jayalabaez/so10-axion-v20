# V49 G2 frontier integration audit

Status: `V49_G2_RETAINED_ACTION_C1_AND_FIXED_ORDER_POLICY_C6_CLOSED__STRICTLY_4D_SOURCE_REMOVES_SPURIOUS_SOURCE_TOWER__STRONG_COLLAR_HC_COUNTERTERMS_PROVED_UNSUPPRESSED__GENERALIZED_RESTRICTED_KERNEL_AND_64_TRACE_PS_MAP_EXECUTABLE__LOCAL_REGULATOR_COMPLETE_DOMAIN_PROFILE_REMATCH_AND_PHYSICAL_COMPONENT_KERNEL_MISSING__G2_FAIL_CLOSED__ONE_OF_EIGHT_FULL_GATES_CLOSED`

## Scientific verdict

V49 makes two closure-grade advances: the fixed-order retained action is now
complete at the abstract invariant-tensor level (`C1`), and every retained
coefficient has an explicit matching/naturalness policy (`C6`).  It also
removes the spurious source KK tower and expands the Wilson witness to 64 PS
trace coordinates.

**G2 nevertheless remains open.  Full gates closed: 1 / 8 — G1 only.**

The decisive correction is that the exact strong collar has

```text
H(s)=H0,
Hc(s)=-(s/epsilon) A H0.
```

Consequently `Hc Xi Hc` and odd-profile `H C Hc` terms are `O(1)`, not
`O(epsilon^2)` or `O(epsilon)`.  The V48 transfer is exact only at their
zero-finite-part matching point.  A complete G2 calculation must recompute the
path-ordered transfer with all of them present.

This is mathematical EFT progress, not a complete theory, UV completion,
phenomenological fit, or empirical validation.

## What V49 genuinely solved

- **E30 — source-spectrum repair:** The source fields depend only on (x,theta), so their transverse mode count is exactly zero and the V47 4D source Hessian is retained.
- **E31 — non-uniform strong-wall Hc scaling:** At m=0, Hc(s)=-(s/epsilon)A H0.  Even-profile Hc Xi Hc and odd-profile H C Hc therefore remain O(1), so they are leading regulator coordinates.
- **E32 — exact pure-source quartic census:** Twelve neutral monomial sectors contain 23 independent complex invariant directions.
- **E33 — retained boundary-action normal form:** The fixed-order action includes mu_H, all direct/conjugate collar portals, leading Hc-Hc and odd-profile coordinates, mixed Kahler sectors, and the two-coordinate O7/O8/profile IBP quotient per channel.
- **E34 — general strong-collar symplectic transfer:** For symmetric A and Xi the full holomorphic collar generator is Hamiltonian; the representative path-ordered transfer preserves the symplectic form.
- **E35 — restricted generalized Wilson witness:** The executable restricted kernel has a 64-coordinate PS trace map and passes its Hermiticity, pole, residue, Euclidean locality, and decoupling checks.
- **E36 — V49 fail-closed decision:** C1 and C6 pass, while C2 is conditional and C3/C4/C5/C7 remain partial. The seven-clause conjunction is false; G2 is not promoted.

## Frozen C1--C7 decision

`G2_closed iff C1 through C7 all pass for the same retained action`.

| Clause | Requirement | Status | Landed | Remaining blocker |
|---|---|---|---|---|
| C1 | fixed_order_action_completeness | pass | The declared tree O(Lambda^-1) sector now has one coefficient for every abstract invariant direction: 23 exact pure-source quartics in 12 sectors, mu_H, direct and conjugate H/Hc portals, mixed Kahler blocks, FI/gauge coordinates, and an IBP/EOM normal form for one normal derivative. | none for C1 at the abstract invariant-tensor level; Cartesian Clebsches belong to C7 |
| C2 | explicit_regulator | conditional | Strictly 4D source multiplets remove the spurious source KK tower, and fixed profiles plus shortest normal Wilson lines define an explicit gauge-covariant finite-resolution tree prescription. | The Wilson-line source coupling is bilocal over epsilon.  It is not a point-local microscopic 5D wall unless finite-range bilocality is admitted as the regulator class or localized by deconstruction/constrained transport fields. |
| C3 | variational_domain_and_self_adjointness | partial | The general holomorphic A,Xi,C collar generator is Hamiltonian and its transfer is symplectic; passive endpoint pencils have a positive-metric self-adjoint enlargement. | All retained strong-collar, Kahler, O7/O8, brane-bulk, and auxiliary blocks have not been varied together into one complete domain. |
| C4 | positive_full_kinetic_form | partial | Positive direct/auxiliary endpoint metrics and the monotone Hermitian pencil identity are executable; the restricted witnesses have finite positive norms. | Positivity of the same complete strong-collar action after every mixed Kahler, normal-derivative, and source-dependent block is assembled remains unproved. |
| C5 | counterterm_and_matching_scheme | partial | The matching scale, finite even/odd profiles, coefficient coordinates, and renormalization inputs are declared. | No independent second-profile rematch or loop/subtraction calculation shows profile and scale independence through O(Lambda^-1). |
| C6 | selector_and_naturalness_policy | pass | Every retained invariant direction has an independent matching coefficient; the Hc and odd-profile zeros are identified as finite-part choices rather than symmetry claims, and higher sectors have an explicit remainder assignment. | none for the declared fixed-order policy |
| C7 | action_to_full_tower_Wilson_matching | partial | A generalized Hermitian endpoint pencil, exact restricted Schur kernel, 64-trace PS map, and pole/residue/locality/decoupling witnesses are executable. | The kernel uses the zero-Hc-counterterm V48 transfer.  The full A,Xi,C path-ordered collar, normalized SO(10)->PS tensors, derivative-current Clebsches, and complete physical Wilson coefficient array have not been matched together. |

Only `C1` and `C6` pass completely.  The conjunction is false.

## Exact remaining defects

- **D8 — finite_range_bilocal_regulator:** The shortest normal Wilson line makes the smearing gauge covariant but bilocal. Localize it by finite deconstruction/constrained transport, or explicitly adopt cutoff-range bilocality in the G2 regulator contract.
- **D9 — complete_strong_collar_transfer_missing:** All allowed Hc-Hc and odd-profile H-Hc matrices are O(1) in the strong wall and must enter one path-ordered transfer; the current Wilson witness uses their zero point.
- **D10 — complete_domain_and_positive_norm_missing:** The full retained collar, endpoint Kahler, derivative, auxiliary, and counterterm blocks have not been varied and certified positive together.
- **D11 — profile_rematching_missing:** An independent profile calculation has not shown counterterm-rematched agreement through O(Lambda^-1).
- **D12 — physical_component_kernel_missing:** Normalized SO(10)-to-PS Cartesian tensors and derivative-current Clebsches are still abstract, so the complete physical Wilson coefficient array is absent.

## Smallest next closure patch

1. Localize the source coupling with finite deconstruction or constrained covariantly constant transport fields, unless cutoff-range bilocality is explicitly accepted.
2. Insert the complete A,Xi,C and O7/O8 tensor families into one path-ordered strong-collar transfer and vary the full retained action.
3. Assemble and prove positivity of the complete bulk+collar+endpoint generalized norm.
4. Rematch a second smooth profile and show counterterm-adjusted agreement through O(Lambda^-1).
5. Publish normalized SO10-to-PS tensors and the resulting complete physical Wilson coefficient array.

## G1--G8 ledger

| Gate | Status | Advance | Remaining blocker |
|---|---|---|---|
| G1 | closed | V47 exact ordinary-Spin quotient and relative anomaly calculations remain intact. | none within the declared ordinary-Spin model |
| G2 | open | V49 completes the retained action at the abstract invariant-tensor level, proves 23 pure-source quartic directions and the O(1) strong-collar Hc correction, and supplies a 64-trace restricted Wilson witness. | The regulator is cutoff-range bilocal, the full A/Xi/C strong-collar action has not been assembled into one positive self-adjoint kernel, profile rematching is absent, and physical component tensors remain abstract. |
| G3 | open | The exact coupled F/D-flat branch and generic physical-rank theorem remain valid at renormalizable order. | Pure-source higher operators, FI/Kähler/radion/soft terms, global vacuum selection and the controlled 5D branch are unsolved. |
| G4 | open | The missing PS mu_H term is now identified as an allowed input rather than silently forbidden. | The mu/Bmu mechanism, SUSY breaking, radion stabilization, EWSB and complete scalar vacuum are absent. |
| G5 | open | No excluded dark benchmark is reintroduced. | No dark-sector Lagrangian, relic calculation or cosmological history is specified. |
| G6 | open | The regulator map is exact and three representative regulated poles plus one residue replay. | A complete controlled parameter point, every pole, thresholds, NDA cutoff, unification and RG running are absent. |
| G7 | open | The source-dependent restricted Schur kernel supplies the correct structural starting point for full-tower matching. | The 210-completed B/L ring, component Wilson coefficients, dressing/running and proton or multinucleon rates are absent. |
| G8 | open | The PS census now includes complementary Hc Higgs cubics and the allowed family/bulk Kähler mixings. | There is no complete component Clebsch map, neutrino completion, family fit, uncertainty propagation or withheld prediction. |

## Route decision

Continue the neutral-210 route only as an open EFT research program.  Do not promote G2 until one local or explicitly admitted regulator carries the complete retained action, positive domain, profile rematch, and component Wilson kernel together.

## Primary sources

- [Marti--Pomarol: 5D supersymmetry in N=1 superfields](https://arxiv.org/abs/hep-th/0106256)
- [Hebecker: gauge-covariant brane operators](https://arxiv.org/abs/hep-ph/0112230)
- [von Gersdorff et al.: interval boundary action principle](https://arxiv.org/abs/hep-th/0411133)
- [del Aguila et al.: thin-defect EFT and classical renormalization](https://arxiv.org/abs/hep-ph/0601222)
- [Barcelo--Mitra--Moreau: finite-width brane/KK limit ordering](https://arxiv.org/abs/1408.1852)
- [Nath--Syed: SO(10) spinor contraction channels](https://arxiv.org/abs/hep-th/0109116)

Core SHA-256: `ad582070cd5e948c5b999d39aa03353fa2da23c4a41ee55a3ab821457222fb5b`
