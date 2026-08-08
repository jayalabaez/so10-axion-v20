# Exact G3 replacement stationary-orbit audit — v20

**Status:** `EXACT_REPLACEMENT_STATIONARY_ORBIT__NUMERIC_STRICT_LOCAL_MINIMUM__GLOBAL_OPEN`

The old Delta_R orbit is not global, but its exact lower-energy counterexample is itself an exact stationary orbit.  Its live well-conditioned Hessian is strictly positive on 445 transverse directions.  However its gauge-orbit rank is 40 rather than the target 37, so it has the wrong unbroken gauge symmetry.  The exact gap-curvature identity separately excludes the fixed P+Delta_R orbit. General Phi=(p,a,omega) branches remain open, so G3 is not closed.

## Exact results

- full 486-gradient: exactly zero from the complete 27-parameter SOS map;
- 126bar identity: `grad W(z)=33 z` in all 252 real coordinates;
- SO(10), gauge, and full-symmetry orbit ranks: `39`, `40`, `41`;
- physical quotient dimension: `445`.
- replacement gauge rank: `40` (target `37`): **wrong symmetry**.

## Numerical Hessian classification

- transverse dimension: `445`;
- minimum eigenvalue: `0.00526094276087988`;
- negative/zero modes at 1e-10: `0` / `0`;
- proof grade: **false** (direct Q(sqrt(22)) LDL remains open).

## G3 consequence

This is an exact lower stationary orbit and a high-confidence numerical strict local minimum, but it has the wrong unbroken gauge symmetry. The exact two-tangent identity excludes the fixed P+Delta_R orbit. General SM-preserving Phi branches remain open, so G3 remains open.
