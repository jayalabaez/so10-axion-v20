"""F92 ordinary closed-lens eta/WCS tests of the hash-pinned V91 scout.

This is not a computation of the full physical tangential bordism group, an
orbifold determinant, or a relative fixed-wall trivialization.  Arithmetic is
exact.  In particular, a bare fermion sign is never called a theory rejection.
"""
from __future__ import annotations

from fractions import Fraction as F
from itertools import combinations, product

import susy_v91_spinc_quantization_tensor_cone_finite_torsion_audit as parent


V91_CORE = "4a581af0dd4cfc6fd3f66ef1e3ea2801b9770c67822d984a02deb602865c0322"
MM_URL = "https://arxiv.org/abs/1808.01334"
UTOPIA_URL = "https://arxiv.org/abs/2505.15885"
IIBORDIA_URL = "https://arxiv.org/abs/2302.00007"


def multiplicities(residues, n):
    result = [0] * n
    for r in residues:
        result[r % n] += 1
    return result


def representation_census(counts, vector_charges):
    """Complex halves of full hyper reps; signs of magnitudes do not change eta."""
    if len(counts) != 5 or any(type(x) is not int or x < 0 for x in counts):
        raise ValueError("five nonnegative integer singlet multiplicities required")
    if any(type(q) is not int or q % 2 for q in vector_charges):
        raise ValueError("even integral vector charges required for G8 descent")
    vector_weights = [1, -1] + [0] * 9
    adjoint_weights = [a+b for a, b in combinations(vector_weights, 2)]
    h4, h8 = [0]*4, [0]*8
    for q in vector_charges:
        for w in vector_weights:
            h4[(w+q//2) % 4] += 1
            h8[q % 8] += 1
    for q, count in zip((0, 2, 4, 6, 8), counts):
        h4[(q//2) % 4] += count
        h8[q % 8] += count
    v4 = multiplicities(adjoint_weights + [0], 4)
    v8 = [56] + [0]*7
    return {
        "vector11_section_weights": vector_weights,
        "adjoint55_section_multiplicities": multiplicities(adjoint_weights, 4),
        "section_C4": {"hyper": h4, "vector": v4,
                       "hyper_minus_vector": [x-y for x, y in zip(h4, v4)]},
        "central_C8": {"hyper": h8, "vector": v8,
                       "hyper_minus_vector": [x-y for x, y in zip(h8, v8)]},
    }


def complex_dirac_xi(n, charge):
    """One complex character: one half of MM Eq7.4's quaternionic R_s xi."""
    if n not in (4, 8):
        raise ValueError("this bounded certificate supports n=4 or n=8")
    s = charge % n
    return F(-11+10*n*n+n**4-60*n*s+60*s*s-30*n*n*s*s
             +60*n*s**3-30*s**4, 720*n)


def reduced_dirac_xi(n, charge, spin_shift=0):
    if spin_shift not in (0, n//2):
        raise ValueError("spin lifts are the canonical lift and its central minus sign")
    return complex_dirac_xi(n, charge+spin_shift)-complex_dirac_xi(n, spin_shift)


def fermion_lens_test(census, n, spin_shift):
    weights = [reduced_dirac_xi(n, r, spin_shift) for r in range(n)]
    difference = census["hyper_minus_vector"]
    h_minus_v = sum((F(m)*w for m, w in zip(difference, weights)), F(0))
    # MM uses positive-chirality gauginos and negative-chirality hyperinos.
    mm_bare = -h_minus_v
    return {
        "n": n, "spin_shift": spin_shift,
        "spin_lift": "product_i exp(pi*e_(2i-1)*e_(2i)/n), i=1,...,4"
                     + ("" if spin_shift == 0 else ", multiplied by central -1"),
        "reduced_complex_Dirac_xi_by_charge": [str(x) for x in weights],
        "hyper_minus_vector_xi": str(h_minus_v),
        "MM_bare_fermion_phase_exponent": str(mm_bare),
        "MM_bare_fermion_phase_exponent_mod1": str(mm_bare % 1),
        "bare_fermion_ratio": "+1" if mm_bare % 1 == 0 else
                              "-1" if mm_bare % 1 == F(1, 2) else "nonreal phase",
        "rank_zero_subtraction": "subtract (H-V)=244 trivial complex characters",
        "bare_fermion_ratio_is_total_anomaly": False,
    }


def tangent_lambda(n, spin_shift=0):
    """Integral half-p1 from a Spin(8) torus lift, not division in Z/n."""
    if n not in (4, 8) or spin_shift not in (0, n//2):
        raise ValueError("unsupported lens or spin lift")
    weights = [1, 1, 1, 1]
    if spin_shift:
        weights[0] += n
    return (sum(w*w for w in weights)//2) % n


def u_wcs_relative_action(n, gauge, gravity=(2, 2), linking_sign=1):
    """Delta S for ordinary even-U WCS; GS counterterm has exponent -Delta S.

    MM4.7 and4.15 give q_U(g1 e1+g2 e2)=link(g1,g2).  The mixed
    term uses the characteristic of Y_grav, not a flat-gravity assumption.
    linking_sign explicitly retains either overall lens-orientation convention.
    """
    if n not in (4, 8) or linking_sign not in (-1, 1):
        raise ValueError("unsupported lens/linking convention")
    g1, g2 = gauge
    a1, a2 = gravity
    return (linking_sign*F(g1*g2+a1*g2+a2*g1, n)) % 1


def refinement_tests(b=(2, -1), linking_sign=1,
                     bare_section=F(0), bare_central=F(1, 2)):
    rows = []
    for tau in product(range(4), repeat=2):
        central = [(2*b[i]+4*tau[i]) % 8 for i in range(2)]
        section_action = u_wcs_relative_action(4, tau, linking_sign=linking_sign)
        central_action = u_wcs_relative_action(8, central, linking_sign=linking_sign)
        section_total = (bare_section-section_action) % 1
        central_total = (bare_central-central_action) % 1
        rows.append({
            "tau_mod4": list(tau), "central_gauge_class_mod8": central,
            "section_WCS_action_difference_mod1": str(section_action),
            "central_WCS_action_difference_mod1": str(central_action),
            "section_combined_exponent_mod1": str(section_total),
            "central_combined_exponent_mod1": str(central_total),
            "passes_both_lens_spin_lifts_in_both_embeddings":
                section_total == 0 and central_total == 0,
        })
    return rows


def build_certificate():
    v91 = parent.load_bound(parent.OUT_JSON, V91_CORE)
    scout = v91["quantized_scout"]
    topology = v91["finite_G8_topology"]
    counts = scout["singlet_counts_by_q0_q2_q4_q6_q8"]
    charges = scout["bulk_vector_charge_magnitudes"]
    if counts != [144, 3, 19, 11, 90] or charges != [6, 4, 6]:
        raise RuntimeError("V91 scout data changed")
    if scout["H_V_T"] != [300, 56, 1]:
        raise RuntimeError("V91 H,V,T changed")
    if topology["fixed_connected_coefficient"] != "-b*lambda_c":
        raise RuntimeError("frozen V71 source convention changed")
    tau = topology["new_scout_tau_mod4"]
    if tau != [0, 2] or topology["new_scout_central_C8_image_mod8"] != [4, 6]:
        raise RuntimeError("V91 finite source restriction changed")
    census = representation_census(counts, charges)
    lenses = [fermion_lens_test(census[key], n, spin)
              for key, n in (("section_C4", 4), ("central_C8", 8))
              for spin in (0, n//2)]
    bare_section = {F(row["MM_bare_fermion_phase_exponent_mod1"]) for row in lenses if row["n"] == 4}
    bare_central = {F(row["MM_bare_fermion_phase_exponent_mod1"]) for row in lenses if row["n"] == 8}
    if bare_section != {F(0)} or bare_central != {F(1, 2)}:
        raise RuntimeError("computed bare lens phases disagree with the selected refinement screen")
    refinements = refinement_tests(bare_section=next(iter(bare_section)),
                                   bare_central=next(iter(bare_central)))
    selected = next(r for r in refinements if r["tau_mod4"] == tau)
    return {
        "status": "EXACT_ORDINARY_CLOSED_LENS_ETA_WCS_SCREEN__NO_FULL_TANGENTIAL_OR_RELATIVE_PROMOTION",
        "input_core_hashes": {"v91": V91_CORE},
        "input_scout": {"singlet_counts_q0_q2_q4_q6_q8": counts,
                        "bulk_vector_charge_magnitudes": charges, "H_V_T": [300, 56, 1]},
        "representation_census": census,
        "representation_derivation": [
            "V91 section h=[exp(pi*e1e2/4),k] acts on vector11 as weights(1,-1,0^9) plus q/2 mod4.",
            "The adjoint of SO11 is wedge^2(vector11); its 55 characters are pairwise weight sums.",
            "The extra ordinary U1 vector is neutral; central k acts trivially on both adjoints.",
            "Full charged hyper S is SMW in S+conjugate(S); the 1/2 reality factor cancels the doubling.",
            "Gauginos are SMW Sp1_R doublets; with trivial R holonomy the same factor cancels their doubling.",
            "Conjugating a charge magnitude leaves both lens-spin-lift xi values unchanged.",
        ],
        "ordinary_screen_assumptions": [
            "smooth six-dimensional (1,0) bulk scout before Higgsing or orbifold projection",
            "closed spin lens L7_n=S7/<diag(exp(2*pi*i/n))>, n=4,8",
            "ordinary Spin tangent times G8 bundle, trivial R/flavor backgrounds and no fixed strata",
            "same-manifold holonomy-to-trivial-holonomy ratio; neutral gravity/tensor terms cancel",
            "ordinary differential-cohomology WCS model with even unimodular tensor lattice U",
            "frozen integral source Y_g=-b*lambda_c+tau*x^2, b=(2,-1), a=(2,2)",
        ],
        "lens_fermion_tests": lenses,
        "tangent_characteristic": {
            "stable_tangent": "TL7_n+R=4*(L_charge1)_real",
            "p1_mod_n": {str(n): 4 % n for n in (4, 8)},
            "lambda_p1_over2_mod_n_both_spin_lifts": {
                str(n): [tangent_lambda(n, s) for s in (0, n//2)] for n in (4, 8)},
            "derivation": "Spin torus weights(1,1,1,1) give lambda=2u^2; central-minus lift adds n to one weight, shifting lambda by n+n^2/2=0 mod n.",
            "gravity_Y_characteristic": "(a/2)*lambda_T=(2,2)u^2; even when p1=0 mod4, lambda=2u^2 is nonzero",
        },
        "WCS_derivation": {
            "lens_linking_derivation": "L7_n bounds the disk bundle of O(-n) over CP3. With h in H2(CP3) and Thom class U, hU maps to -n*h^2 and has self-intersection -n. Its boundary discriminant pairing on u^2=h^2|L is therefore +/-1/n; both orientation signs are checked.",
            "null_axis_naturality": "MM4.15: q(z tensor e_i)=q_Z(z)*(e_i,e_i)=0 for both null U basis vectors",
            "polarization": "MM4.7: q_U(x*e1+y*e2)=link(x,y)",
            "Wu_independence": "U is even, gamma=0 in U/2U, so MM4.23 Wu variation vanishes",
            "shift": "MM4.4 nu=d(eta_Z tensor a,0,0); a=(2,2) makes nu/2 integral and trivializable, so MM5.2 changes no closed differential class",
            "gravity_need_not_be_flat": "MM4.7/4.12: Delta S=q(g)+integral(Y_grav cup g); for flat g the cross-term depends on the torsion characteristic of Y_grav",
            "same_manifold_Arf_cancels": "MM4.19 contains S(X)-Arf(q); Arf(q) is independent of the background X",
            "GS_sign": "MM5.3 uses the complex conjugate WCS, hence GS exponent=-Delta S",
            "action_formula": "Delta S=(g1*g2+2*g1+2*g2)/n mod1 for linking(u^2,u^2)=+1/n",
            "opposite_linking_sign_also_checked": True,
            "absolute_eta_to_linking_orientation_dictionary_fixed": False,
            "why_sign_gap_does_not_affect_screen": "bare exponents are 0 or1/2; replacing Delta S by its negative leaves the passing-label set unchanged",
        },
        "torsion_refinement_lens_screen": {
            "bare_phases_derived_from_the_representation_census": True,
            "rows": refinements,
            "passing_tau_mod4": [r["tau_mod4"] for r in refinements
                                 if r["passes_both_lens_spin_lifts_in_both_embeddings"]],
            "initial_ordinary_integral_labels": 16,
            "labels_passing_this_screen": sum(r["passes_both_lens_spin_lifts_in_both_embeddings"] for r in refinements),
            "V91_selected_label": selected,
            "central_C8_bare_minus_one_canceled_on_both_lenses": all(
                r["central_combined_exponent_mod1"] == "0" for r in refinements),
            "passing_labels_are_anomaly_free_theories": False,
        },
        "bordism_scope": {
            "ordinary_OmegaSpin7_BC4_from_literature": "Z/32 direct_sum Z/2",
            "generator_dictionary_note": "2505.15885 Thm13.40 and Prop13.43 give a lens-generator presentation, but its signed combination was not reconciled with the explicit spin-lift eta convention used here; no generator promotion is made.",
            "explicit_Z2_generator_witness_certified": False,
            "full_OmegaSpin7_BC4_character_certified": False,
            "ordinary_OmegaSpin7_BG8_computed": False,
            "full_Gammahat_tangential_bordism_computed": False,
            "relative_fixed_wall_WCS_trivialization_constructed": False,
            "orbifold_fermion_determinant_constructed": False,
            "all_global_anomalies_canceled": False,
            "any_G_gate_closed": False,
        },
        "primary_sources": [
            {"url": MM_URL, "use": "Sec2.1/2.2 SMW normalization and adjoint gauginos; Eq7.4 lens xi; Eq4.4/4.7/4.15/4.19/4.23 and5.2/5.3 WCS ratio"},
            {"url": IIBORDIA_URL, "use": "AppendixC.1 spin-lift shift by n/2 and independent lens eta construction; absolute overall eta sign not identified"},
            {"url": UTOPIA_URL, "use": "Thm13.40 ordinary OmegaSpin7(BC4) presentation; Prop13.43 signed lens generator dictionary left unresolved"},
        ],
    }
