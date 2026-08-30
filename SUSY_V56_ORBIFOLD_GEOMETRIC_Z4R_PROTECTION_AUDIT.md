# V56 6D orbifold Z4R protection audit

Status: `V56_6D_ORBIFOLD_Z4R_PROTECTION__V55_AND_V56_ARCHITECTURE_CORES_BOUND__TWO_WEAK_ZERO_MODES_AND_ZERO_COLORED_ZERO_MODES__NONDERIVATIVE_R0_R0_HIGGS_MASSES_FORBIDDEN_TO_ALL_R0_VEV_ORDERS__YUKAWA_AND_MAJORANA_ALLOWED__SOFT_R_BREAKING_MU_ROUTE_IDENTIFIED__BULK_IRREDUCIBLE_GAUGE_ANOMALY_CANCELS__HIGHER_DIMENSIONAL_ORIGIN_DERIVATIVE_BRANE_LOCALIZED_ANOMALY_GS_THRESHOLD_AND_UV_OBLIGATIONS_OPEN__ZERO_GATE_PROMOTIONS`

Core SHA-256: `09ba35b4e7cc05bf2375818e71610f565d6a330b5e8f0221373c301a58293a55`

## Bounded result

The candidate passes one exact, useful test: **all non-derivative R0-R0 local
Higgs bilinears are forbidden to every order in the declared R-neutral
GUT-VEV ring**.  In conventional 4D N=1 bookkeeping,
`q(theta)=1`, `q(D_perp)=q(Sigma)=0`,
`q(H)=q(H')=0`, and `q(Hc)=q(H'c)=2`, while a superpotential term must have
charge 2.  Consequently `Hc D_perp H` is allowed, direct `H H'` and `Hc Hc`
are forbidden, and H-Hc boundary terms are allowed but remain in the
bipartite block.

That result is conditional.  A higher-dimensional/geometric origin of this
Z4R must exist as an exact discrete gauge symmetry of the full compactification.
H-Hc and normal-derivative fixed-point operators still require a regulator-level
classification.  The artifact does not close a theory gate.

The inputs are bound to V55 core
`52d0044e8d227be29b2cab63c565c1f4335aae9a72c9d51f3c9044fe7289a1f7`
and V56 architecture core
`3f3f662cdb8ba0e1081dc77fa2d579fef7c5421b97ca7b16fdce0760f796af0a`.

## Orbifold kernel

The free translation/reflection projector gives zero modes
`H10:H:h2, H10_prime:H:bar_h2`.  There are exactly
`2` weak-doublet zero modes,
`0` colored zero modes, and
`0` conjugate-hyper zero modes.
At the `O_GG` SU(5)xU(1)X fixed point, both desired doublets and their massive
color partners have support.  Complementary Hc components also have local
support, but q=1 matter couples only to q=0 H fields: the corresponding Hc
Yukawas have charge 0 rather than the superpotential charge 2.

This is a projector certificate, not the infinite interacting KK determinant.

## Exact charge census

Allowed rows: gauge_kinetic, bulk_H, bulk_H_gauge, bulk_Hp, bulk_Hp_gauge, up_Yukawa, down_lepton_Yukawa, right_neutrino_Majorana, rank_breaking_driver, rank_breaking_linear, soft_mu_parent, boundary_Hc_H, boundary_Hc_Hp, boundary_Hpc_H, boundary_Hpc_Hp, soft_Hc_Hpc_parent, R_broken_dimension5_proton_parent, normal_derivative_boundary_loophole.

Forbidden rows: direct_H_Hp_mass, direct_H_H_mass, direct_Hp_Hp_mass, direct_Hc_Hpc_mass, direct_X_Xbar_mass, matter_Higgs_mixing, up_Yukawa_to_Hpc, down_Yukawa_to_Hc, renormalizable_RPV_proxy, dimension5_proton_proxy.

The neutral-VEV exhaust checked
`455` exponent vectors through
total insertion degree `12`.  Every
dressed `H H'` operator has charge 0 rather than 2.  The first fatal spurion is
therefore any charge-2 scalar or effective background with a GUT-scale
expectation.  The driving singlet S has charge 2 and must obey `<S>=0` in the
supersymmetric vacuum.

## Yukawa, Majorana, and mu

On the SU(5)xU(1)X brane the candidate action is

`W = yu 10 10 H5 + yd 10 bar5 H'bar5 + yN 1 1 X +
kappa S(X Xbar-v_X^2) + lambda S H H'`.

Each family is `10_-1+bar5_3+1_-5`, all with R charge 1;
`q(X)=q(Xbar)=0` and `q(S)=2`.  Both Yukawas and `1_-5 1_-5 X_+10` are
allowed.  The supersymmetric solution has `X Xbar=v_X^2` and `S=0`, preserving
Z4R and leaving `mu=0`.  Soft terms may
shift `<S>` to the soft scale and generate `mu=lambda<S>`, breaking Z4R to
matter parity.  That soft minimization, `B_mu`, phases, and the seesaw/flavour
fit have not been calculated.  Minimal SU(5) down/lepton mass relations are an
explicit flavor obligation, not a prediction accepted here.

## Colored exchange and proton operators

The exact finite `4+4`
KK witness has full rank `8` and a zero H-H
inverse block.  Thus two Z4R-selected O_GG matter sources have no colored-Higgsino
dimension-five propagator in the declared bipartite quadratic topology.
Adding an Hc-Hc block produces
`4` nonzero H-H
inverse entries.  A direct Hc-Hc mass is forbidden before R breaking, but
`S Hc H'c` is allowed and generates this block after `<S>` becomes nonzero.

Z4R forbids `10 bar5 bar5` R parity violation and direct
`10 10 10 bar5/M_*` proton operators.  After R breaking,
`S(10 10 10 bar5)/M_*^2` is allowed and must be matched.  Conditional on the
full KK inverse retaining the block hierarchy, colored exchange scales as
`C5 ~ yu yd lambda_c<S>/Mc^2`, not as an unsuppressed `1/Mc` coefficient.
KK gauge exchange and boundary Kähler operators remain as dimension-six
obligations.

## Anomalies

In the normalization `A(10)=1`, the irreducible six-dimensional SO(10)
coefficient is `2-1-1=0`.  The rigid chiral dimension mismatch is nevertheless
`25`,
and reducible, gravitational, fixed-point, and discrete anomalies are open.

For the massless MSSM fields the mixed coefficients are
`A3=3`,
`A2=1`, and
`A1=-3/5`.  Their integerized
residues are universal modulo `eta=2`; this is only a necessary low-energy
check and is not localized six-dimensional anomaly cancellation.

The explicitly localized family sums vanish exactly, family by family:
`A_SU5^3=0`,
`A_SU5^2-X=0`,
`A_X^3=0`, and
`A_grav-X=0`.
The `X_+10+Xbar_-10` pair is vectorlike.  These sums do not include
parity-localized bulk inflow or discrete-R anomalies.

Remaining anomaly work:

- Compute the anomaly polynomial including every bulk hypermultiplet, tensor, and supergravity multiplet.
- Distribute parity-induced anomalies among all four fixed points and add explicit inflow/counterterms.
- Check mixed Z4R-G_local^2 and Z4R-gravity anomalies separately at every fixed point.
- Specify a quantized axion/tensor shift that cancels all universal residues; low-energy congruence is insufficient.
- Recheck the SU(2) Witten anomaly and all global/cobordism anomalies after adding boundary and hidden matter.

## Threshold and UV obligations

- The full two-radius KK determinant and regulator-matched gauge thresholds.
- Nonuniversal fixed-point gauge kinetic terms at SO(10), GG, flipped, and PS branes.
- U(1)X/rank-breaking, X/Xbar, S, flavor-mediator, and supersymmetry-breaking thresholds.
- The relation among M_c, M_*, the six-dimensional gauge coupling, and the observed unified coupling.

## Decisive falsifiers

- No consistent exact higher-dimensional/discrete-gauge realization of the Z4R exists for the full compactification.
- A permitted H-Hc or normal-derivative brane operator lifts the weak zero modes or indirectly creates an Hc-Hc triplet block.
- Any q_R=2 scalar/spurion has a GUT-scale expectation and regenerates a Higgs mass.
- The full bulk plus localized anomaly system cannot be canceled with quantized inflow and physical fields.
- The infinite KK determinant contains a colored zero mode or lacks exactly one Hu/Hd pair before soft breaking.
- Threshold, seesaw/flavor, proton, or soft-spectrum matching fails data.

## Explicit nonclaims

- No regulator-level proof of a higher-dimensional/geometric origin for Z4R or complete fixed-point operator ring.
- No infinite KK determinant with normal-derivative boundary interactions.
- No localized/discrete/gravitational anomaly cancellation or physical GS completion.
- No threshold, flavor, seesaw, proton-lifetime, soft-spectrum, or cosmology fit.
- No G1-G8 gate promotion and no empirical discovery.

## Primary literature

- L.J. Hall, Y. Nomura, T. Okui, D.R. Smith, [SO(10) Unified Theories in Six Dimensions](https://arxiv.org/abs/hep-ph/0108071) (`hep-ph/0108071`).
- H.M. Lee et al., [A unique Z_4^R symmetry for the MSSM](https://arxiv.org/abs/1009.0905) (`1009.0905`).
- W. Buchmuller, L. Covi, D. Emmanuel-Costa, S. Wiesenfeldt, [Flavour structure and proton decay in 6D orbifold GUTs](https://arxiv.org/abs/hep-ph/0407070) (`hep-ph/0407070`).

The Z4R protection layer is a new conditional candidate built on the
published orbifold and low-energy Z4R mechanisms; it is not attributed to those
papers as a completed model.
