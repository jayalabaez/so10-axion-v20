# V49 generalized restricted-action boundary pencil audit

Status: `V49_GENERALIZED_POSITIVE_BOUNDARY_PENCIL_AND_RESTRICTED_ACTION_KERNEL_DERIVED__FULL_64_TRACE_PS_CLEBSCH_CURRENT_MAP_EXECUTABLE__POLE_RESIDUE_LOCALITY_AND_DECOUPLING_IDENTITIES_PASS__STRONG_COLLAR_HC_GENERATOR_AND_SOURCE_QUARTIC_SO10_TENSORS_REMAIN_ABSTRACT__G2_FAIL_CLOSED`

## Verdict

V49 supplies a generalized boundary pencil capable of carrying every named
endpoint Kähler, derivative, counterterm and portal block through the
restricted finite-collar calculation.  It also replaces the V48
eight-coordinate witness by an executable 64-coordinate PS trace map with all
four H/Hc Higgs vertices and the six one-bulk family currents.

This is a substantial C3/C4/C7 advance, but **G2 remains open**.  The full
SO(10) quartic invariant multiplicities and normalized component tensors, the
normal-derivative superspace variation, the generic strong-collar Hc
generator, and a second-profile counterterm rematch are still absent.  A
universal matrix slot is neither a normalized physical Clebsch coefficient
nor a replacement for an interaction inside the collar.

## Restricted-action pencil

At each wall retain a passive Hermitian pencil

`P(m)=M-m Z-C^dagger(H-m W)^-1 C`,

with `Z>=0`, `W>0`, and Hermitian `M,H`.  It obeys

`-dP/dm=Z+C^dagger(H-mW)^-1 W(H-mW)^-1 C>=0`

between auxiliary poles.  The auxiliary states are part of the enlarged
positive Hilbert space; their determinant factors are never divided away.
Normal-derivative relations `A_rel b+B_rel a=0` enter this graph chart when
`A_rel` is invertible and `A_rel^-1 B_rel` is Hermitian.

For the V48 collar,

`Cf=C+P_L D`, `Cg=D+P_L U`,

`K=Cf R+Cg Q`, `N=Cf P+Cg T`.

With the PS relation `b=J0+P0 a`, the exact restricted-action heavy and Wilson
kernels are

`Gamma_HH=K+N P0`, `G00=Gamma_HH^-1 N`,

and the complete light Schur complement is

`Gamma_eff=Gamma_LL-Gamma_LH Gamma_HH^-1 Gamma_HL`.

The executable positive witness finds signed roots
`[0.3903576482050121, 0.9211400410681962, 1.4462836771160366]`.  Its first-pole
residue error is `1.222e-06`;
the Euclidean norm ratio between `p=8` and `p=4` is
`0.00879382`.  Scaling the positive
auxiliary Hamiltonian from eight to sixteen reduces its Schur correction by a
factor `0.496218`.

## Full PS component map

The boundary vector has 64 coordinates: sixteen V47
internal components times `(HLF,HLA,HRA,HRF)`.  In a declared epsilon-tensor
convention the bidoublet map is four repeated 2x2 blocks.  The four vertices
are `A_L-C_R`, `B_L-D_R`, `HRAc_L-HLFc_R`, and
`HRFc_L-HLAc_R`.

The executable map has 64 independent
nonzero entries, exactly its expected count.  Its Clebsch norm completeness
identity and Hermiticity pass.  The physical family current has
16 nonzero component entries, and three
deterministic positive-metric 64x64 counterterm trials give finite kernels.

The action contract now explicitly admits `mu_H H H`, O7/O8 graph
coefficients, `Q nabla5(HLFc)`, `Qc nabla5(HRAc)`, four conjugate Hc source
portals, mixed source Kähler blocks, both FI coordinates, all boundary gauge
terms, and the abstract full pure-source quartic invariant space.  Vacuum
selection from those quartics remains G3; their presence in the action is G2.
However, the executable transfer sets the Hc-Hc and odd-profile mixed finite
parts to zero.  In the strong `Lambda/epsilon` collar they are generically
`O(1)` and must be inserted into the path-ordered generator, so the contract
and executable kernel are not yet the same complete action.

## Clause decision

| Clause | V49 result |
|---|---|
| C1 | FAIL: mu_H, Hc portals and derivative coordinates are named and pure-source quartics are parameterized abstractly, but independent multiplicities/tensors and the complete strong-collar action are not enumerated |
| C2 | CONDITIONAL: the square H/Hc transfer is explicit at a restricted point, but its source coupling is a finite-range Wilson-line bilocal rather than a point-local microscopic 5D regulator |
| C3 | PARTIAL: the passive endpoint pencils give a positive-metric self-adjoint enlargement, but the allowed O(1) Hc-Hc and odd-profile terms have not been varied into one complete collar generator |
| C4 | PARTIAL: direct and auxiliary endpoint metrics and -dP/dm are positive in executable witnesses, but positivity of the complete strong-collar action with all allowed Hc blocks is unproved |
| C5 | PARTIAL: all counterterm types fit named pencil coordinates at mu=Lambda, but a second-profile rematching and loop subtraction calculation are absent |
| C6 | PARTIAL: the fixed-order policy is explicit, but zero Hc-Hc and odd-profile finite parts define a matching point rather than symmetry-protected omissions and must be rematched |
| C7 | PARTIAL: the 64 PS trace/Higgs/current map is executable for the restricted collar and universal admissible tensors are tested, but the O(1) Hc collar blocks, normalized SO10 tensors and derivative-current Clebsches remain absent |

## Exact remaining G2 work

1. enumerate multiplicities and normalized projectors for B4_source=Hom_G(1,Sym4 R_source)
2. supply normalized SO10-to-PS component tensors for all degree-four source portals and H/Hc derivative currents
3. derive the named O7/O8 and brane-bulk derivative graph blocks by varying one explicit superspace action
4. insert every allowed Hc-Hc and odd-profile H-Hc block into the path-ordered strong-collar generator and recompute its transfer
5. perform one independent collar-profile rematch, including local counterterms, and show agreement through O(Lambda^-1)
6. publish the complete same-action Wilson coefficient array rather than universal placeholder tensor inputs

The formal pencil is therefore not used to overrule the missing physical
tensors or strong-collar blocks.  G1 remains the only closed gate, so the
total is **1/8**.

Primary references: [Marti--Pomarol](https://arxiv.org/abs/hep-th/0106256),
[Hebecker](https://arxiv.org/abs/hep-ph/0112230),
[von Gersdorff et al.](https://arxiv.org/abs/hep-th/0411133),
[del Aguila--Perez-Victoria--Santiago](https://arxiv.org/abs/hep-ph/0601222),
[Nath--Syed](https://arxiv.org/abs/hep-th/0109116), and
[Barcelo--Mitra--Moreau](https://arxiv.org/abs/1408.1852).

Core SHA-256: `173aad00eb3ce89748a402b89d3587574f186b1b01166fe145f297b71956a08c`
