# V49 retained boundary-action completeness

Status: `V49_RETAINED_ACTION_CENSUS_COMPLETE_IN_DECLARED_FIXED_ORDER_SECTOR__23_EXACT_PURE_SOURCE_QUARTIC_DIRECTIONS__MU_H_AND_ALL_HC_PROFILE_COORDINATES_RETAINED__IBP_EOM_FIELD_REDEFINITION_NORMAL_FORM_DEFINED__STRONG_WALL_HC_SUPPRESSION_REJECTED__COMPONENT_MATCHING_AND_G2_OPEN`

## Verdict

The declared fixed-order action census is now complete at the abstract
invariant-tensor level.  It contains the allowed `mu_H H H` term, all 19 PS
spinor cubics, exact pure-source quartics, both direct and complementary
source-collar spinor portals, odd-profile `Hc H`, even-profile `Hc Hc`, all
quadratic mixed Kähler sectors, and a deterministic normal-derivative normal
form.

**G2 remains open.**  The full collar transfer and Wilson calculation has not
yet been rerun with every new `A,Xi,C` tensor, normalized SO(10)-to-PS
component arrays remain unpublished, and the finite Wilson-line smearing is a
bilocal Wilsonian regulator rather than a point-local 5D microscopic action.

## Exact pure-source quartics

The independent D5 character census and constructive Susyno plethysm agree
sector by sector.  With `S`, `ThetaPlus` and `ThetaMinus` singlets, the degree
four source action has 12 nonempty monomial sectors and
**23 independent complex invariant directions**:

| Monomial sector | Exact multiplicity |
|---|---:|
| `S^4` | 1 |
| `S^2 ThetaPlus ThetaMinus` | 1 |
| `S^2 Phi^2` | 1 |
| `S^2 Sigma barSigma` | 1 |
| `S Phi^3` | 1 |
| `S Phi Sigma barSigma` | 1 |
| `ThetaPlus^2 ThetaMinus^2` | 1 |
| `ThetaPlus ThetaMinus Phi^2` | 1 |
| `ThetaPlus ThetaMinus Sigma barSigma` | 1 |
| `Phi^4` | 4 |
| `Phi^2 Sigma barSigma` | 6 |
| `Sigma^2 barSigma^2` | 4 |

One independent coefficient is retained for every orthonormal Hom-space
direction.  This satisfies fixed-order C1 enumeration without pretending to
publish the Cartesian Clebsch arrays needed for C7.

## Two-bulk and mixed-Kähler census

The holomorphic portal basis starts from every charge-neutral candidate and
then keeps every direction in its exact finite Spin(10) Haar-projector image.
Candidate counts at degrees 2/3/4 are respectively **2/10/30 for `HH`**,
**2/10/30 for `HcHc`**, and **4/20/60 for ordered `HcH`**.  Empty projector
images add no coefficient; multiplicity greater than one adds one coefficient
per orthonormal image direction.  Thus the familiar 12 degree-four `HH` and
12 degree-four `HcHc` expressions are witnesses, not an exhaustiveness
assumption.

The same construction is used for Kähler response.  All
**16** charge-neutral
zero-insertion candidates and
**80** one-source
candidates are represented before Haar projection; the displayed 8 and 32
terms are known nonempty witnesses.  Hermiticity and positivity are imposed
on the assembled metric, not by deleting uncomputed sectors.

Both constant source-wall gauge kinetic terms, all
**3** allowed one-source gauge
kinetic functions, and the independent source-wall `xiF_L` FI coordinate are
also retained.  Their coefficients and the PS-wall `xiF_0` datum are
renormalized inputs at the declared matching scale.

## Strong-wall correction

In the `A/epsilon` collar, the exact zero-energy profile is

`H(s)=H0`, `Hc(s)=-(s/epsilon) A H0`.

Therefore

`<Hc^T Xi Hc> = H0^T A^T Xi A H0/3`,

`<rho_o H^T C Hc> = -H0^T C A H0/3`.

Both are order one as `epsilon -> 0`.  The earlier fixed-derivative estimate
`HcHc=O(epsilon^2)` does not apply to the strong wall.  `Xi=C=0` is consequently
a matching choice, not a controlled remainder or a symmetry theorem.

The fundamental collar action is

`W_col=Hc^T D5 H + rho_e(H^T A H+Hc^T Xi Hc)/2 + rho_o Hc^T C H`.

For symmetric `A,Xi`, its general generator is Hamiltonian.  The executable
path-ordered transfer has symplectic residual
`1.221e-15`.

## Normal-derivative normal form

For every invariant channel begin with `O7=Hc D5H`,
`O8=(D5Hc)H`, and the derivative-profile coordinate `M_o`.  Exact collar IBP
gives `O7+O8+M_o=0`; retain `O_minus=O8-O7` and `M_o`.  Leading-EOM descendants
with `D5^2` or `barD^2` are removed, but neither retained boundary coordinate
is set to zero.  Positive Kähler matrices are canonically normalized by
Cholesky transformations, with all induced mass, derivative, current, and
Yukawa shifts carried along.

## Gauge-covariant smearing

Every bulk field is transported to `y=L` by the shortest normal chiral Wilson
line in its own representation before contraction with a source tensor.  This
is gauge covariant and becomes `U=I` in collar axial gauge.  It is still
bilocal over the finite width `epsilon`, so no point-local microscopic UV
completion is claimed.

## Remaining G2 blockers

- insert the full A,Xi,C tensor families into the same-action spectral/Wilson pencil
- publish normalized SO10-to-PS Cartesian tensors for C7 rather than abstract Hom labels
- perform a second-profile counterterm rematch and loop-level subtraction audit
- decide whether finite Wilson-line bilocality is accepted as the G2 regulator contract

Core SHA-256: `ed0b77f66a4f800abbf1dca9a199433d549c13a1f92903748c0013ffef6e90ad`
