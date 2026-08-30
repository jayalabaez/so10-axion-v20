# V50 PS-intertwiner basis audit

Status: `V50_CARTESIAN_WILSON_FUNCTIONAL_BASIS_COMPLETE__PS_NAMED_COMPONENT_INTERTWINER_NOT_EMITTED__C7_PARTIAL`  
Core SHA-256: `2ee3bc6d972976b83f523a60e753a418d5cd9a3c7dca72f9379bafce681b0cab`

Repeated-weight rotations are basis conventions, not external physical CG data. Transforming the current, kernel and projectors together leaves `-1/2 J† K^-1 J` invariant; the executable residual is `1.53e-16`.

A deterministic intertwiner is constructible by simultaneous Cartan diagonalization, highest-weight nullspaces, ordered Chevalley lowering, positive-first-coordinate phases, and ancestry-ordered Gram–Schmidt. The repository has not yet frozen one PS Chevalley embedding and multiplicity ancestry order tied to every V49 trace label, so the three large unitaries were not emitted.

A complete Cartesian Wilson functional is physically sufficient when currents and parity projectors are also Cartesian. The current mixed Cartesian/PS artifact set does not yet meet that condition. Therefore C7 is **PARTIAL**, not PASS; no external CG measurement is required, only a finite convention-and-implementation bridge.
