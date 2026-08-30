# SUSY V55 R1 matter and operator audit

Status: `V55_R1_EXACT_FAMILY_CHARGE_SEARCH_FINDS_BOUNDED_FN_SURVIVORS__SPIN10_TENSOR_FILTER_REMOVES_SINGLE_FAMILY_FOURTH_POWERS__BUT_RENORMALIZABLE_L_H_H2_FILLER_KILLS_NATURAL_DT__DIFFERENTIATED_FAMILIES_INVALIDATE_FIXED_GS_REPAIR__NO_GATE_PROMOTION`

Core SHA-256: `895f999b53fcf7c4e513e0f9c6ee3245d166d8db8d3cfceaff3d9d8c2af25330`

## Result

The R1 lattice admits bounded family-charge assignments with full charge-level Yukawa and RH-Majorana support; exact Spin10 tensors remove the spurious single-family F_i^4 class and the strict proxy can delay the first gauge-invariant F^4 dressing to ten insertions. This does not rescue R1. The exact same charge ledger permits the renormalizable L h H2 filler, whose L VEV removes all four weak-Higgs modes, and every differentiated survivor invalidates the fixed V54 GS spectator universality. No gate is promoted.

## Exact Spin(10) filter

The exact D5 character calculation shows that `F_i^4` and `F_i^3 F_j` have no holomorphic
Spin(10) singlet. The six genuine family classes are the three `F_i^2 F_j^2` and three
`F_i^2 F_j F_k` patterns, each with multiplicity one. Both equal- and mixed-family
`F_i F_j H1` operators exist, and `F_i F_j barC^2` has multiplicity two.

## Bounded family search

The exact search scans `820` ordered integer triples with `q3=11` and
`11<=q2<=q1<=50`, enumerating singlet dressings through 20 insertions. It finds
`626` hierarchy-proxy survivors and
`178` strict-monotone survivors.

The lowest-charge member of the best strict class is `[45, 39, 11]`. Its leading Yukawa
insertion matrix is `[[7, 6, 4], [6, 6, 4], [4, 4, 0]]` and its RH-Majorana matrix is
`[[9, 8, 5], [8, 8, 4], [5, 4, 3]]`. Its first valid proton dressing uses
`10` insertions, at total degree
`14`. This is a charge-level proxy, not a flavour fit.

## Decisive Higgs leak

The complete ten-bilinear singlet-spurion census finds `L h_10 H2_10` at total degree
`3` with charge `1-4+3=0`. Since `L` has a nonzero VEV,
this is the direct `h H2` mass in the vacuum. The weak filter rank becomes 16 and its nullity becomes
zero; the full four-vector filter rank becomes 40. The earlier bare-charge screen therefore missed
a renormalizable same-action filler.

## Anomaly boundary

The fixed 134-singlet repair satisfies single-GS universality only when `q1+q2+q3=33`.
In the ordered domain this forces `(11,11,11)`, so no differentiated hierarchy survivor retains
the fixed repair. For the strict example, `A_10=173`
while fixed `TrQ=2168` instead of the required
`4152`.

The result does not exclude a changed Higgs/source action, redesigned GS spectrum, or a complete
flavour construction. Those require new same-action Hessian, anomaly, Wilson, and likelihood audits.
