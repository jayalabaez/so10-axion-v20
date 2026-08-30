# SUSY V37 G5 residual-relic and cosmology audit

## Exact result

The `P,Pbar` VEV leaves `Z170 ~= Z2 x Z85`.  Every core field except
`A2,A32,A15,A17,A16` is neutral under it.  Their inverse-charge classes are
`{'A2_A32': [19, 151], 'A15_A17': [49, 121], 'A16': [85, 85]}`; there are therefore three inequivalent
anomalon charge classes.  A nonzero-charge state cannot decay only to the rest
of the V37 core.  This proves an extension-free stable-relic obstruction, but
does not assert that every anomalon is separately stable for every mass order.

## Conditional extension

The six-field `D2,Db2,D17,Db17,D16,Db16` construction reuses the existing `X`
driver to give a decay route for each class.  All listed terms pass the exact `Z66`, `Z85`, `Z4R`, and
optimized-PQ checks; the full finite Hsieh/Dai--Freed audit remains true.  The
all-chiral lattice first breaks PQ at W degree
`33` and
Kahler degree `32`.
The P/M-suppressed decay benchmark has lifetime
`1.525e-12` s for a
1-TeV parent and unit coefficient, far before BBN.

## Fail-closed boundary

This is not a G5 closure.  The candidate leaves stable dark carriers and needs
a spectrum, soft mediation, global vacuum calculation, and a numerical
Boltzmann/reheating history.  A standard thermal relic much heavier than
`3.4e+05` GeV cannot be rescued by ordinary
elementary-particle freeze-out alone.  The observed target used for a future
calculation is `Omega_c h^2=0.12`.

Sources: [Griest--Kamionkowski thermal-relic unitarity bound](https://ntrs.nasa.gov/citations/19900004848);
[Planck 2018 cosmological parameters](https://arxiv.org/abs/1807.06209).

Core SHA-256: `5b7424ef3436c298037bba0853edb484d127a987ba53ff88181a5d07c9744ce2`
