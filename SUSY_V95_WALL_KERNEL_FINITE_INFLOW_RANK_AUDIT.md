# SUSY V95: wall kernel, necessary inflow and original section bounds

Status: V95_UNCHANGED_WALL_EMBEDDING_REJECTED__NECESSARY_INFLOW_TARGETS_AND_RANK_BOUND__NO_ACCEPTED_PARENT

Core SHA256: e8ed3aa98cc23726cd41d0b62bbfb8822253d7a9282f1184ba22a77956cb4729

## Outcome

F95 rules out a specific wall repair, derives exact targets for a different inflow completion, and bounds the original Jacobian's free rank. No common action is accepted. All eight SUSY/C8 gates remain OPEN; canonical V21 physical evidence is unchanged. These are mathematical/model audits, not experimental confirmation.

## The unchanged wall cannot be repaired with internal signs

The inclusion Spin4 x Spin2 into Spin6 has kernel D=(-1,-1). D is already the identity in Spin6 before the R/flavor/gauge quotient, so tensoring an independent internal representation cannot change its action. Eight of V94's 28 Weyl components per C4 fail this identity: five in E*, one in det(E), and two positive-charge singlets. N1 scalar partners fail the same test. This excludes the unchanged embedding, not every new boundary cover or correlated tangential structure.

The formal R assignment r_R=2q_N makes the geometric phase neutral but retains the same eight failures. Its full Cartan anomaly is I_wall(x+2y), not I_wall(x); setting y=-x/2 removes the wall polynomial rather than cancelling the frozen bare normal anomaly. A genuinely different embedding requires recomputing its full bulk and boundary curvature and finite data.

## Exact fractional U(1) inflow target

Set the normal and Spin11 Cartan curvatures to zero. The bare anomaly moments (TrQ,TrQ^3) are (47/2,754) at each C4 and (3,-60) on the physical C2 orbit, the sum of its two cover points. Ordinary integer-charge Weyl polynomials lie in Z(1,1)+Z(2,8), because q^3-q is divisible by6. Each local remainder lies outside this enlarged lattice; no set of ordinary wall Weyls alone can cancel it. The actual frozen gauge-representation lattice is smaller, not larger.

On spin CP3 with f=H and p1=4H^2, the three bare index periods are 487/4,487/4,-21/2. Define J2=I(q=2)=4f^3/3-f*p1/12. The formal transfer (+J2/4,+J2/4,-J2/2) has zero sum and changes these periods to122,122,-11. A common denominator divisible by4 is necessary in this enlarged lattice and this representative attains4. The integrated bulk index remains233, with moments(50,1448); the full visible moments remain(-68,1408). Nothing global has been cancelled by redistributing a zero-sum polynomial.

This specifies a necessary fractional class only. The shifted local polynomials are nonzero; physical representations, source quantization, mixed anomalies and a differential inflow action remain missing. CP3 is an index-integrality witness, not a lens-space defect phase or a test of a nowhere-zero Higgs phase.

## Finite defect phases and the Majorana sign

For the unchanged isolated unit defect, retain three complex channels of physical C8 charge2 and three real channels of charge4. With xi=(eta+h)/2, the gravitationally subtracted phase is exp[-2*pi*i*(3*rho2+(3/2)*rho4)]. The real half is taken before discarding integral spectral data.

On primitive L8^3(1,1), the explicitly fixed spectral orientation gives bare phase+i and required inverse inflow-i for both spin lifts. Reversing the common orientation/chirality conjugates both phases. On flat S1 x odd-spin T2 with primitive holonomy, the bare and inverse phases are both-1 for either S1 spin choice. The torus sign comes from the Majorana kernel term; reducing modulo1 before taking the real half would lose it.

The normal spin root shifts the induced tangent spin structure; the physical charge4 Majoranas cannot be called neutral without retaining the corresponding rank-nine spin-change factor. These admissible isolated-model witnesses refine V94's local curvature match but neither generate the full Gammahat bordism group nor construct its relative trivialization. The common bulk/defect orientation dictionary and purely gravitational completion also remain open.

## Original geometry: a bound and two conditional heights

Keep the original coefficients and write K=C(X)(T), with X transcendental. Extending constants to the algebraic closure of C(X) yields an elliptic K3 with16 finite I1 fibers and I2*/D6 at infinity. Shioda-Tate and the characteristic-zero K3 Picard bound give0<=rank E(K)<=12 by field inclusion, not numerical specialization. V94's trivial torsion theorem remains valid. No original-field nonzero section or exact rank has been found.

Original-field sections can meet only the monodromy-fixed simple components0 or1. Their generic-K3 heights are4+2m or3+2m, respectively, with m=P.O>=0. Under the stated flat crepant threefold assumptions, b(P)=2*Kbar+2*pi_*(P.O)-c(P)*S. If displayed charges equal Shioda charges, the scout target148S+768F requires component0 and pi_*(P.O)=72S+378F. If displayed charges are twice Shioda charges, the section height is37S+192F, requiring component1 and pi_*(P.O)=17S+90F.

The scale-two branch is conditionally compatible with the Spin^c11 parity: singlet/vector charges become even and spinor charges odd. This is a normalization and central-weight check, not a derived global gauge group or an existing section. Neither branch is excluded or proved to exist. V94's anti-invariant cover point still does not descend, and its quadratic twist still changes the required gauge fiber.

## Next step

F96_QUANTIZED_RELATIVE_INFLOW_AND_ORIGINAL_MW_GENERATOR

Construct or exclude a quantized relative inflow action with the pure-U1 fractional source class (+I(q=2)/4,+I(q=2)/4,-I(q=2)/2), all mixed normal/R/nonabelian terms, and inverse isolated-defect phases (-i on the chosen lens convention, -1 on the torus). Specify a valid boundary tangential map and field representations; independent internal signs cannot repair the unchanged V94 module.

Determine the original generic-K3 Picard/Mordell-Weil rank or construct a K-rational non-torsion section. Fix the physical charge normalization before testing its height: the scale-two candidate requires section height37S+192F and near-component intersection, not a primitive height148S+768F by assumption.

## Primary sources

- [Sections3.1 and4 distinguish fractional bare bulk fixed-point contributions, localized Weyl anomalies and bulk Green-Schwarz inflow; integrated cancellation alone is insufficient.](https://arxiv.org/abs/hep-th/0612212)
- [N1 superfield expansion/action and equations44-45 motivate tracking both superspace and matter twists; no source assertion of the new wall candidate.](https://arxiv.org/abs/hep-th/0602155)
- [Index integrality and the distinction between polynomial matching and a differential anomaly theory.](https://arxiv.org/abs/1808.01334)
- [Weyl anomaly as the degree-six Ahat*Chern-character index density; local descent is distinct from global completion.](https://arxiv.org/abs/0802.0634)
- [AppendixC(C.2) finite spectral sum, (C.3)-(C.4) lens polynomials, and (3.13) change of spin lift. Our lens Dirac sign is explicitly the opposite of (C.2); exact sums, not mod-one polynomials, fix the real half.](https://arxiv.org/abs/2504.02934)
- [Section3.1 (3.4) includes the kernel in APS xi, (3.9) subtracts a same-rank trivial bundle, and (3.12)-(3.15) distinguish determinant/Pfaffian phases and the real-twisted even quaternionic index. The explicit negative-exponential phase convention is used here.](https://arxiv.org/abs/2606.18380)
- [Section2.4 and Eq(2.52) derive the fermion Pfaffian anomaly factor, including the real versus complex normalization; not an automatic global completion of the present bulk theory.](https://arxiv.org/abs/1909.08775)
- [Section2 (2.18)-(2.20) identifies useful lens and odd-T2 product tests for cyclic two-dimensional anomalies. Its complex mod-one product result must not be halved after discarding the kernel integer.](https://arxiv.org/abs/2604.19634)
- [Theorem6.8, Corollaries6.11/6.13, section11.8/Table4, and section13.1 supply the canonical/Euler, Shioda-Tate, local height and characteristic-zero K3 Picard bounds.](https://arxiv.org/abs/0907.0298)
- [Sections2.1-2.3 relate inverse-Cartan Shioda coefficients to central quotients and explain the preferred section/charge normalization. Applied only conditionally to this unconstructed section.](https://arxiv.org/abs/1706.08521)
- [AppendixA, equationsA.18-A.30 define the height pushforward, section self-intersections and nonabelian corrections. Bilinearity gives the squared charge-rescaling factor.](https://arxiv.org/abs/1803.07998)
- [Section6.4 identifies the nonsplit I2* monodromy cover; V93 derives its actual P_plus*P_minus square class, recomputed here.](https://arxiv.org/abs/1106.3854)
