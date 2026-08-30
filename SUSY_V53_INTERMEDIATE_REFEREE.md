# V53 intermediate referee report

## Decision

**Approve as exact intermediate results, with scope conditions.** I found no arithmetic or modular-logic blocker in either audit. Neither result closes the whole phenomenological action or promotes G2/G3. The selector conclusions must remain no-go statements for their explicitly declared symmetry/action classes.

## Independently reproduced

- The cross-coupled `54+45+45+16+bar16` source has exact Gaussian-rational Hessian rank **143**, orbit rank **33**, and `H Q = 0`; hence its 33-dimensional kernel is exactly the broken gauge orbit. Independent reductions at `(p,i)=(37,6),(41,9),(73,27)` reproduce ranks `(143,33)`.
- The uncoupled control has exact characteristic-zero Hessian rank **137**, `H Q = 0`, nullity 39, and therefore six physical chiral zero modes beyond the 33 gauge directions. This exact rank check closes a proof gap that would exist if one relied on a single modular lower bound alone.
- The declared two-vector DT Hessian is symmetric, has rank **16** and nullity **4**: the color block is full rank while four weak Cartesian modes remain. For the direct source-plus-DT quadratic block, the accounting is rank `143+16=159`, nullity `37=33 gauge+4 Higgs`. This is not a Hessian for the full matter/singlet/filter action.
- The proton-selector congruence is exact: in every ordinary cyclic factor, `H^2` and `FFH` imply `4q_F=0`, so `F^4` is allowed. In a conventional cyclic R factor, simultaneous `E^2` and `E^3` forces the superpotential charge to vanish and leaves only modulus 2, which reduces to the same obstruction. A brute-force independent check through modulus 256 finds no counterexample; the componentwise argument covers finite Abelian products.
- The reported `F^4` flavor multiplicity **6** agrees independently with `dim S_(2,2)(C^3)=6`, the family tensor permitted by the spinor contraction/Fermi symmetry.
- The natural-DT inventory gives `sum T=24+8+2+6=40`. With `C2(SO(10))=8`, the report's convention is the Landau coefficient `b_L=sumT-3C2=+16`; the asymptotic-freedom convention is `b_AF=-16`. At `g=0.73`, the stated one-loop pole proxy is about `1.05e4` times the matching scale.

## Scope conditions and cautions

1. The proton result excludes finite products of ordinary Abelian and conventional R cyclic selectors **for the unchanged required operator set**. It does not exclude non-Abelian selectors, altered actions, spurions, or UV threshold mechanisms. `F^4` being symmetry-allowed is a generic operator-safety failure, not by itself a quantitative proton-lifetime prediction.
2. The natural-DT no-go covers ordinary additive Abelian factors with the displayed source/action assumptions. It does not cover R symmetries, non-Abelian filters, charged mass spurions, anomalous-U(1) constructions, or product-group/flipped completions. Within the displayed ordinary-Abelian source, neutrality of `B` is also enforced by the allowed cross/source terms, rather than being an arbitrary standalone assumption.
3. The four `N` singlets and family fields appear in inventory/perturbativity bookkeeping, but their complete portals, vacuum equations, and full Hessian are not audited here. Accordingly, “candidate action” must be read as source plus declared DT sector, not a complete same-action model.
4. The suggested “three Dirac singlet pairs” escape is a reasonable rank-three seesaw design target, not a proved globally minimal completion over all possible action changes.

Executable reproduction: `susy_v53_intermediate_referee_verification.py`.
