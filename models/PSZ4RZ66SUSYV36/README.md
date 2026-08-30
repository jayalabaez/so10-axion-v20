# PSZ4RZ66SUSYV36 source boundary

This directory is the polynomial four-dimensional SUSY Pati--Salam source for
V36.  SARAH contains the gauge and chiral multiplets and the complete
renormalizable superpotential selected by the exact `Z66`.  It does not contain
the gravitational/topological sector, a Kahler potential, soft mediation, a
compactification, or pole matching.

## Exact selector

`Z66` is the CRT combination of the old `Z33` selector and anomalon parity:

`q66 = 2 q33 + 33 p (mod 66)`.

The nonzero charges are:

- `P=2`, `Pbar=64`, `PsiBar=PsiCBar=64`;
- `A2=37`, `A32=31`, `A15=63`, `A17=1`, `A16=65`.

The `P,Pbar` VEVs leave the order-two subgroup unbroken.  All anomalons are odd
and all original fields are even under that remnant.  The dangerous `P A32`
term is therefore forbidden by the same exact selector; no independent global
parity is assumed.

## External topological boundary

The PS-singlet anomalons cancel the pure finite Spin x Z66 class but cannot
change the universal mixed PS-squared selector residue.  V36 therefore defines,
at EFT level, a period-one axion chiral multiplet `T` with shift `4/33` under the
projected Z33 generator (equivalently `8/66` under the chosen Z66 generator),
equal gauge topological levels `(1,1,1)`, and gravitational level
`k_grav=0 mod 11` (the minimal representative is zero).

This is a declared nonuniversal 4D Green--Schwarz boundary condition.  Its
microscopic compactification or Stueckelberg origin is not derived.  Stabilizing
exponentials involving `T` are charged coefficient spurions and can dress lower
powers of `P`; no axion-quality claim may ignore them.

## Vacuum boundary

The two driver rows constrain `Sbar*S` and `P*Pbar` when
`kappaPS*rhoPQ-kappaPQ*rhoPS` is nonzero.  This gives a rank-four local
driver/radial holomorphic Hessian and leaves the expected PQ Goldstone
multiplet.  The Kahler/soft sector must still stabilize the saxion and select
the global vacuum.

## Falsifiability boundary

The source disables soft terms because no mediation model has been derived.
Higher-dimensional gauge-kinetic and Kahler threshold operators are set to zero
only as a falsifiable boundary hypothesis; an alternative analysis must list a
finite Wilson vector and priors.  Independent ad-hoc matching shifts are not
part of V36.
