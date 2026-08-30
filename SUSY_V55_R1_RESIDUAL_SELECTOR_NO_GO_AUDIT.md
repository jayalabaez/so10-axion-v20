# V55 R1 residual-selector no-go audit

Status: `V55_R1_ADDITIVE_SELECTOR_NO_GO__SOURCE_TERMS_FORCE_L_EQUALS_A_EQUALS_B_AND_THEREFORE_ALLOW_RENORMALIZABLE_h_A_H2_AND_L_h_H2__BOTH_FILL_WEAK_KERNEL__ANY_RESIDUAL_ORDINARY_OR_R_FACTOR_PRESERVING_THE_VACUUM_FILTER_AND_TWO_DIRECT_YUKAWAS_ALLOWS_MIXED_FAMILY_F4__SAME_FAMILY_FOURTH_POWER_TENSOR_ABSENT__ACTUAL_UNIVERSAL_FAMILIES_HAVE_DEGREE9_S4R_DRESSING__NO_GATE_PROMOTION`

Core SHA-256: `4419949188586eb7ded9551f1cb11c683a672cb30b4ae65d482e6273ba3d7a19`

## Exact theorem

For any additive ordinary or R symmetry factor, the required source terms
`M A^2`, `M A B`, `barC A C`, and `L barC C` force
`r(L)=r(A)=r(B)`.  The required filter term `h B H2` then immediately forces
both `h A H2` and `L h H2` to carry the superpotential charge.  This is
independent of whether the symmetry survives the vacuum.  The exact `A` VEV
has weak coefficient 3, while `L` also has a VEV.  Either filler raises the
weak-filter rank from `12`
to `16` and all four
weak-Higgs zero modes disappear.  Removing `L` alone is therefore insufficient.

No product of additive Abelian selectors can repair this action without
removing a required source/filter term.

## Residual proton theorem

Let `w` be the fixed superpotential charge of any additive residual ordinary or
R symmetry.  If the R1 vacuum is neutral under the residual factor and the
terms `P H1 barh`, `S barh h`, `h B H2`, `T H2^2`, and direct Yukawas for two
distinct families `Fa Fa H1` and `Fb Fb H1` are retained,
their congruences imply

`r(h)=r(barh)=r(H1)=r(H2)`, `2 r(Fa)=2 r(Fb)=r(H2)`, and therefore
`2 r(Fa)+2 r(Fb)=2 r(H2)=w (mod N)`.

The exact tensor census removes a same-family fourth power, but it contains one
genuine `Fa^2 Fb^2` singlet for distinct families.  This mixed operator is
therefore allowed.  The argument applies factorwise, so a product of additive
residual Abelian factors does not repair the universal-family R1 action.

The finite audit checked `254` ordinary/R factors through
`Z_128`, found `382` charge
solutions satisfying all hypotheses, and found zero counterexamples.

## Actual V54 charged-source action

The VEV-charge gcd is `1`, so the
continuous U(1) itself leaves no nontrivial discrete subgroup.  The top-family
mixed-family operator has charge
`44` and the exact `S^4 R`
dressing has charge `-44`.  Hence

`(F1^2 F2^2)_Spin10-singlet S^4 R / Lambda^6`

is allowed at total degree `9`, exactly matching the V54
bounded operator search.

## Decision

R1 is rejected as a symmetry-complete natural-DT action: its two forced
renormalizable fillers remove the Higgs pair.  No gate is promoted.  G7 also
remains open.  Possible exits require a changed source/filter, mediator-generated
top Yukawa, genuinely non-Abelian matter selection, or an explicit
Wilson/lifetime proof for a successor action.

Primary context: https://arxiv.org/abs/1003.2625
