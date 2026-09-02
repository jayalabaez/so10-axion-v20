# SUSY V97: equivariant index, relative inflow and section descent

Status: V97_CONDITIONAL_GAPPED_DIRAC_COMPLETION_AND_COMMON_ORDER4_GLUE__SU2_FLAT_REFINEMENT_AND_CUBIC_BRANCH_EXCLUSION__NO_ACCEPTED_PARENT

Core SHA256: 161eb53a3e453c80b3887d365e31c32c6846d1c6f8d45b474b849f07a3de2020

## Outcome

V97 solves several precisely stated subproblems without accepting a common theory: the projected index and a small-mass gap for an explicit quadratic Dirac model; an exact integer-response decomposition leaving one common order-four class; a nonabelian normal/R repair with its necessary flat refinement; and exclusion of another entire original-section branch. All eight SUSY/C8 gates remain OPEN. No experimental confirmation is claimed.

## What the mass zeros actually imply

Add an explicit kinetic completion to the frozen mass witness: D_mu=[[2*dbar,lambda*mu],[lambda*conj(mu),2*d]], on a flat square cover torus of side L with periodic spin structure, the frozen effective translation and rotation lifts, and no transverse gauge/flavor connection. The charge+2 block has mu=conj(m), domain phases (i,-i), and codomain phases (-1,-1); the conjugate block reverses charge and four-dimensional chirality. Kinetic and mass covariance are checked together.

The compact C4-equivariant index of the charge+2 block is chi1+chi3-2*chi2, with character values (0,2,-4,2). Its invariant multiplicity is exactly zero at every finite mass by elliptic homotopy invariance. The isolated linear-core equations are also solved by Gaussian modes: two C4 cores have odd C4 character, and the C2 pair is induced from the odd C2 character. None of these protected core modes survives projection. This is not a calculation of all accidental paired zero modes of the compact nonlinear profile.

More strongly, all invariant sections have no constant Fourier component, so the zero-mass singular gap is 2*pi/L. The exact bound |m|<=1/2 gives gap >=2*pi/L-|lambda|/2. Thus both projected kernels vanish whenever |lambda|*L<4*pi, even though the mass vanishes at all four cover fixed points. Forced mass zeros do not alone imply physical massless particles. The result assumes the displayed kinetic operator, metric, connections and smooth domain; a full SMW/Gammahat/supersymmetric action is not supplied by it.

## One common mixed-gauge obstruction, with quantized integer pieces

On the preimage of U5 in the gauge Spin^c11 group, write D=det(E)*L_aux^2 and d=c1(D)=t+2*ell. The line L_aux is genuine on this subgroup, not a new odd-charge Spin11-singlet. With I(z)=z^3/6-z*p1/24 and K=I(D*M)-I(D)-I(M), each V96 remainder decomposes exactly as R_C4=Z_C4+P/4 and R_physical_C2=Z_C2-P/2, where P=d^2*(d+u). Z_C4 and Z_C2 have explicit integer eta-index plus integral differential-character responses. Their local negative responses are quantized on the specified product backgrounds.

P itself is the integer index I(D^2*M)-2*I(D*M)+I(M). The CP3 quotient test realizes its period 1, proving that the remaining quarter-class has exact order four modulo quantized curvatures. The old periods 61/4,61/4,-1/2 are retained, not retracted. On a common background the fractions sum to zero; independent filling changes cancel only when n0+n1-2*n2=0 mod4. The exact period correlation is necessary data for a relative construction, not a constructed relative action.

The virtual bundle M*(D-1)^2 has rank zero, first Chern character zero and index P, so a formal application of the old shifted-character difference has the desired quarter/half profile with no extra normal term. But the actual normal root M has C4 phase zeta. Including it changes both frozen H fourth powers from -I to +I. The resulting raw degree-six trace is zero but the candidate is inadmissible under the frozen closure. Ordinary C4 characters cannot fix this. A displayed compensating matrix F=diag(zeta^-1,zeta), F^4=-I, restores the phases algebraically; its full Gammahat representation, flavor curvature, physical multiplicities and quantum gluing remain unproved.

The new virtual P carrier is not the old charge-two Dirac model. Its formal success cannot borrow that model's gap or spectrum. Nor does the common determinant line identify the wall normal bundle with the separate Phi-vortex normal bundle, or glue the five-dimensional responses to the inherited three-dimensional spin-CS/ABK inverse.

## A nonabelian R repair must retain its Witten sign

As a separate product-category scout, replace the old two equal R Cartan weights by a genuine SU2_R doublet with common normal-root weight -3. Its anomaly polynomial is -9*u^3+3*u*c2(R)+u*p1/4. The integral degree-six character -u*c2(E)+10*u^3-3*u*c2(R) gives precisely the same normal repair target as V96 and cancels the added sector's R-curvature terms without requiring the R bundle to split into lines. The known central kernel acts trivially on this representation. Its orbifold placement and complete supermultiplet are still not constructed.

A single Weyl doublet nevertheless has the Witten sign -1 on a unit SU2 instanton times a periodic spin circle, while the displayed bosonic CS response is trivial there. This cannot be avoided just by changing complete SU2 multiplets within the flavor-trivial, odd-normal-weight, no-gravitational-CS ansatz: sum(d_R*k)=-6 forces the total instanton-index parity to be odd.

The ordinary-spin product bordism group with U1_M, SU2_R and U5_E is computed by explicit Sq2 matrices to be Z2. The flat ratio of the new doublet/CS response to the R-trivial reference is therefore exactly nu_R=(-1)^(ind2 D5_Rfund), fixed by its generator value. Multiplying by nu_R restores that reference on all backgrounds of this restricted category; it does not trivialize the reference anomaly, identify the original bare R anomaly, or supply a microscopic inflow sector. The broader tangential/normal half-period obstruction and full Gammahat descent remain open.

## Original section search: an exact exclusion and a smaller system

An exact coordinate change x_section=9*s-6*c, y_section=27*w rewrites the unchanged Jacobian as w^2=s*(s-c)^2-4*a*e*s+b^2*e. In the surviving leading-minus-24 cubic-x branch, split by the leading quartic-y coefficient b4. For b4=0, the h=0 subcase has a necessary equation nonzero at X=1. For h!=0, recursion gives necessary polynomials in h^2; their degrees are preserved at X=1 and modulo 101, where the first pair has resultant 37. This proves the generic resultant nonzero and excludes this leading-minus-24 b4=0 branch even over the algebraic closure of C(X). The statement does not exclude the separate leading-plus-12 branch after a field extension. It is not a rank-specialization argument.

Every remaining cubic candidate must therefore have y degree exactly four. Set b4=108*r, z=r^2!=0 and y=108*r*(T^4+H*T^3+K*T^2+L*T+M). Exact elimination reduces the branch to four saved polynomial equations in z,H,K. The only variable denominator is a power of z, and the excluded z=0 case was handled separately. An original-field point additionally requires z to be a square in C(X); a nonsquare gives only a quadratic-cover point whose y changes sign. The reduced system remains unsolved. Torsion stays trivial and the rank bound remains 0<=rank<=11.

## Next step

F98_GAMMAHAT_TRANSPORT_LIFT_AND_ORIGINAL_SQUARE_SECTION

Construct or exclude a full Gammahat-compatible order-eight compensating lift for the actual-normal-root carrier M*(D-1)^2, retaining its R/flavor curvatures, SMW reality and positive physical field content. If a lift exists, build the order-four relative determinant/gluing for P=d^2*(d+u), including the required normal/SU2 flat refinement and the inherited defect response. A common filling-period constraint is not a substitute for this action.

Solve or rigorously exclude the surviving original-Jacobian four-equation system in z,H,K over C(X), with z nonzero and a square in C(X). Preserve the original coefficient member and charge-normalized height; higher-degree and denominator-bearing sections require separate arguments.

## Primary sources

- [Sections3-4 define integral differential-character holonomy and distinguish it from a full equivariant lift; used for the new SU2-invariant degree-six character.](https://arxiv.org/abs/2011.05768)
- [Section2.7 and Section3 define integral differential cup-product CS holonomy, including nonbounding manifolds and higher-degree products. Used for the integer cup polynomials, not for an unconstructed fourth-root orbifold action.](https://arxiv.org/abs/1207.5449)
- [Sections2.2-2.3 give the periodic-circle instanton test and SU2 representation parity formula; section2.7 distinguishes ordinary spin from spin-SU2 anomalies.](https://arxiv.org/abs/1810.00844)
- [Section2.2.3 and the SU(n) computation in Section3.4 supply ordinary-spin AHSS d2 as dual Sq2 and Sq2(c2)=c1*c2+c3. The product-group calculation is performed here.](https://arxiv.org/abs/1808.00009)
- [Exponentiated eta invariants, determinant lines and gluing; a curvature-zero ratio is treated as a restricted flat anomaly character, not as a full parent cancellation.](https://arxiv.org/abs/hep-th/9405012)
- [Equations2.12-2.22 distinguish 4D, normal and 6D chirality and show that an ordinary 6D mass couples opposite 6D chiralities. The selected torus operator and lifts here are derived explicitly, not taken from that paper's rectangle boundary conditions.](https://arxiv.org/abs/1609.01413)
- [Weinberg's first-order fermion-vortex index problem relates Higgs topology to an operator index. It does not by itself specify the present compact orbifold action or physical field count.](https://journals.aps.org/prd/abstract/10.1103/PhysRevD.24.2669)
- [Equations2.13-2.17 exhibit chiral transverse derivative/Yukawa equations and angular mode constraints. Our simple-core Gaussian and oscillator identities are independently computed for the stated operator, not inferred from a Majorana zero-mode count in a different model.](https://arxiv.org/abs/2303.03425)
- [Equivariant elliptic indices are integer representation multiplicities; finite-group projectors and Fredholm domains. The present character is computed directly from periodic Fourier zero modes.](https://arxiv.org/abs/1908.05165)
- [Orbifold index from equivariant data includes nonidentity stabilizers; supports the distinction from dividing a cover contribution alone by four.](https://arxiv.org/abs/math/0701768)
- [Dai, Section2.3 Eq(3.5)-(3.6): canonical U(n)->Spin-c(2n) lift has vector g_real and determinant det(g). The subgroup map and D=det(E)*L^2 relation are derived explicitly here.](https://web.math.ucsb.edu/~dai/book.pdf)
- [Sections1-2: kernel-inclusive reduced eta modulo integers and CS transgression on odd-dimensional spin manifolds. APS supplies the integer-level line-index refinements; no fractional eta power is declared canonical.](https://arxiv.org/abs/math/0307120)
- [Localized orbifold fermion anomalies retain finite shifted characters and normal Lorentz data. The exact SMW kernel and H^4 condition are frozen through V96 and evaluated with the actual normal-root isotropy here.](https://arxiv.org/abs/hep-th/0612212)
- [APS eta and relative determinant-line anomaly inflow: a curvature decomposition or shared filling-period check alone does not construct the full relative anomaly theory or microscopic action.](https://arxiv.org/abs/1909.08775)
- [Examples1B.4 and2.43 and Section3.E model BCn by infinite lens spaces and compute cyclic cohomology. Equivalently the circle Gysin sequence with Euler class n*c gives H*(BCn;Z)=Z[v]/(n*v). Only the degree-six characteristic-class restriction is used.](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf)
- [Sylvester determinant and common-factor criterion over residue fields; the certificate separately verifies degree preservation and an exact modular nonvanishing witness.](https://stacks.math.columbia.edu/tag/00UA)
- [Section4.1 defines the resultant as a polynomial determinant in the coefficients and states its common-root criterion. No specialization rank theorem is used.](https://www.math.columbia.edu/~dejong/courses/algebraic_curves/AlgCLN6-1.pdf)
- [The inherited elliptic-surface and Mordell-Weil context. This audit preserves the previously proved generic K3 rank bound rather than promoting a low-degree section search to an exact rank.](https://arxiv.org/abs/0907.0298)
