"""Exact F92 singlet-hyper projector witnesses; not a quantum completion.

The 267 six-dimensional hypermultiplets are represented by a compressed direct
sum of explicit one- and four-dimensional flavor blocks.  Each block includes
both conjugate symplectic components; those are not two independent hypers.
The four-dimensional constant-mode kernel is computed, never inferred from the
six-dimensional count.  Only the ordinary flat square-orbifold smooth-sector
lift is constructed.  Localized matter, the regulator and relative WCS remain
outside this certificate.
"""
from __future__ import annotations

import copy
import hashlib
import itertools
import json
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parent
PARENTS = {
    "v70": ("SUSY_V70_SPIN11_LOCALIZED_PARENT_SPIN_FLAVOR_COMPLETION_AUDIT.json",
             "3e7b8e53916fbbc05bdcdf9632bcf4359aa4888b037df775c37d8d7d2551b228"),
    "v71": ("SUSY_V71_SPIN11_NORMAL_BUNDLE_EQUIVARIANT_GS_AUDIT.json",
             "0162828ebd2b1e28d4fcbcf4ea1e6c61178d305cec79abd6d36a55719bb0f1ea"),
    "v88": ("SUSY_V88_B_NEUTRAL_GAMMAHAT_CARTAN_ANOMALY_CORRECTION_AUDIT.json",
             "d8172ac25c3336ae622b250cf29b8a48089be4f15455c0163562a86a49b55033"),
    "v89": ("SUSY_V89_C8_LOCALIZED_BV_COMPACT_GLOBALIZATION_AUDIT.json",
             "afece33b67225eb97b4813a643914fe979a744cea5d233e4886c80be59fbf3e7"),
    "v90": ("SUSY_V90_EXTERNAL_C8_QUOTIENT_DAIFREED_REES_EQUIVARIANCE_AUDIT.json",
             "ec095daa641345934d285a56a1916bf701352ee5cb113018296487ade36b966f"),
    "v91": ("SUSY_V91_SPINC_QUANTIZATION_TENSOR_CONE_FINITE_TORSION_AUDIT.json",
             "4a581af0dd4cfc6fd3f66ef1e3ea2801b9770c67822d984a02deb602865c0322"),
}


def canonical_sha(value):
    value = copy.deepcopy(value)
    value.pop("core_sha256", None)
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_parents():
    reports = {}
    for name, (filename, core) in PARENTS.items():
        value = json.loads((ROOT / filename).read_text(encoding="utf-8"))
        if value.get("core_sha256") != core or canonical_sha(value) != core:
            raise RuntimeError("changed or noncanonical projector parent: " + name)
        reports[name] = value
    return reports


def clean(matrix):
    return sp.Matrix(matrix).applyfunc(sp.simplify)


def matrix_json(matrix):
    return [[str(x) for x in row] for row in clean(matrix).tolist()]


def zero(matrix):
    return clean(matrix) == sp.zeros(matrix.rows, matrix.cols)


def symplectic_form(d):
    return sp.BlockMatrix([[sp.zeros(d), sp.eye(d)], [-sp.eye(d), sp.zeros(d)]]).as_explicit()


def symplectic_embed(unitary):
    return sp.diag(unitary, sp.conjugate(unitary))


def cyclic_projector(matrix, order, exponent=0):
    """Project onto eigenvalue exp(2*pi*i*exponent/order), exactly."""
    root = sp.I if order == 4 else sp.Integer(-1)
    return clean(sum((root**(-exponent*k) * matrix**k for k in range(order)),
                     sp.zeros(matrix.rows)) / order)


def constant_projector(a, u, v):
    d = a.rows
    kernel = (a-sp.eye(d)).col_join(u-sp.eye(d)).col_join(v-sp.eye(d)).nullspace()
    if not kernel:
        return sp.zeros(d)
    n = sp.Matrix.hstack(*kernel)
    return clean(n * (n.conjugate().T*n).inv() * n.conjugate().T)


def assert_square_relations(a, u, v):
    d = a.rows
    checks = {
        "A4": zero(a**4-sp.eye(d)),
        "UV_commute": zero(u*v-v*u),
        "AUAinverse_equals_V": zero(a*u*a.inv()-v),
        "AVAinverse_equals_Uinverse": zero(a*v*a.inv()-u.inv()),
        "unitarity": all(zero(x.conjugate().T*x-sp.eye(d)) for x in (a,u,v)),
    }
    if not all(checks.values()):
        raise RuntimeError("square-space-group relation failed")
    return checks


def source_contract(p):
    n1 = p["v70"]["lorentz_SU2R_and_N1_superfield_lift"]
    if n1["N1_superfield_rules"]["full_hyper_constraint"] != "Z_plus Z_minus i = I, Z_plus^4=Z_minus^4=I":
        raise RuntimeError("V70 hyper partner convention changed")
    old = p["v71"]["neutral_266_phase_classification"]
    orbit = old["explicit_266_dimensional_witness"]["sixty_four_length4_blocks"]
    if orbit["A"] != "A e_k=e_(k+1 mod 4)":
        raise RuntimeError("V71 cyclic shift changed")
    phases = {"1":sp.Integer(1), "-1":sp.Integer(-1), "i":sp.I, "-i":-sp.I}
    u4 = sp.diag(*(phases[x] for x in orbit["U_diagonal"]))
    v4 = sp.diag(*(phases[x] for x in orbit["V_diagonal"]))
    a4 = sp.zeros(4)
    for k in range(4):
        a4[(k+1)%4,k] = 1
    assert_square_relations(a4,u4,v4)
    signs = p["v71"]["spin_half_equivariant_index"]["phase_signs_m0123"]
    if signs != [-1,1,1,-1]:
        raise RuntimeError("V71 normal-channel signs changed")
    lift = p["v88"]["B_neutral_Gammahat_lift"]
    if lift["cover"]["K_F_generators"] != {
        "krot":[1,1,1,1,1,0], "kspin":[0,1,0,0,0,1]
    }:
        raise RuntimeError("V88 kernel changed")
    c8 = p["v89"]["C8_space_group_lift_enumeration"] if "C8_space_group_lift_enumeration" in p["v89"] else None
    if c8 is None:
        c8 = next(value for value in p["v89"].values()
                  if isinstance(value,dict) and "selected_representative_alpha_u_v" in value)
    if c8["selected_representative_alpha_u_v"] != [0,2,2]:
        raise RuntimeError("V89 C8 translation lift changed")
    normal = p["v90"]["localized_isotropy_characters"]["normal_characters"]
    if any(row["complex_normal_weight"] != 1 for row in normal.values()):
        raise RuntimeError("V90 normal weight changed")
    count = p["v91"]["quantized_scout"]["singlet_counts_by_q0_q2_q4_q6_q8"]
    if count != [144,3,19,11,90]:
        raise RuntimeError("V91 singlet counts changed")
    return {"A4":a4,"U4":u4,"V4":v4,"signs":signs,"counts":count,
            "kernel":lift["cover"]["K_F_generators"],"normal":normal}


def effective_matrices(kind, m, eta, contract):
    if kind == "four_orbit":
        return contract["A4"], contract["U4"], contract["V4"]
    if kind != "line" or m not in range(4) or eta not in (-1,1):
        raise ValueError("unknown singlet block")
    return sp.Matrix([[sp.I**m]]),sp.Matrix([[eta]]),sp.Matrix([[eta]])


def block_certificate(q, kind, m, eta, contract):
    if q not in (0,2,4,6,8):
        raise ValueError("charge outside frozen V91 alphabet")
    a,u,v = effective_matrices(kind,m,eta,contract)
    d = a.rows
    plus = {"A":a,"U":u,"V":v}
    # Both N1 fields are columns here.  The row-field inverse is transposed.
    am,um,vm = clean(-sp.I*a.inv().T),clean(u.inv().T),clean(v.inv().T)
    minus = {"A":am,"U":um,"V":vm}
    plus_checks = assert_square_relations(a,u,v)
    minus_checks = assert_square_relations(am,um,vm)
    if not zero(am.T*a+sp.I*sp.eye(d)):
        raise RuntimeError("full-hyper superpotential pairing changed")
    zeta = (1+sp.I)/sp.sqrt(2)
    chi = sp.Integer(-1)**(q//2)
    af = symplectic_embed(zeta*a)
    uf,vf = symplectic_embed(chi*u),symplectic_embed(chi*v)
    k = clean(sp.diag(*( [zeta**q]*d + [zeta**(-q)]*d )))
    charge = sp.diag(*([q]*d+[-q]*d))
    jf = symplectic_form(d)
    smw_checks = {
        "flavor_A_fourth_minus_identity":zero(af**4+sp.eye(2*d)),
        "flavor_symplectic":all(zero(x.T*jf*x-jf) for x in (af,uf,vf,k)),
        "flavor_unitary":all(zero(x.conjugate().T*x-sp.eye(2*d)) for x in (af,uf,vf,k)),
        "quaternionic_reality":all(zero(jf*sp.conjugate(x)-x*jf) for x in (af,uf,vf,k)),
        "quaternionic_reality_square_minus_one":zero(jf*sp.conjugate(jf)+sp.eye(2*d)),
        "continuous_charge_symplectic":zero(charge.T*jf+jf*charge),
        "all_twists_commute_with_continuous_charge":all(zero(x*charge-charge*x) for x in (af,uf,vf,k)),
        "external_k4_identity_on_center_even_singlets":zero(k**4-sp.eye(2*d)),
        "translation_compensation_U":zero(uf*k**2-symplectic_embed(u)),
        "translation_compensation_V":zero(vf*k**2-symplectic_embed(v)),
    }
    scalar_a = clean(zeta**(-1)*af)
    if not zero(scalar_a-sp.diag(a,am)):
        raise RuntimeError("R-times-flavor scalar lift does not match N1 pair")
    # Source hyperino flavor is the dual.  J supplies the equivalence to the
    # fundamental, so this does not introduce another independent hyper.
    lorentz = sp.diag(zeta,zeta**(-1))
    ha = clean(sp.kronecker_product(lorentz,af.inv().T))
    hu = clean(sp.kronecker_product(sp.eye(2),(uf*k**2).inv().T))
    hv = clean(sp.kronecker_product(sp.eye(2),(vf*k**2).inv().T))
    reality = sp.kronecker_product(symplectic_form(1),jf)
    hyperino_checks = assert_square_relations(ha,hu,hv)
    hyperino_checks.update({
        "combined_SMW_reality_square_plus_one":zero(reality*sp.conjugate(reality)-sp.eye(4*d)),
        "combined_twists_preserve_SMW_reality":all(zero(reality*sp.conjugate(x)-x*reality) for x in (ha,hu,hv)),
        "dual_flavor_equivalent_via_J":zero(af.inv().T-jf*af*jf.inv()),
    })
    if not all(smw_checks.values()) or not all(hyperino_checks.values()):
        raise RuntimeError("SMW/charge/half-angle checks failed")
    strata = {}
    for point,word,order in (("z00","A",4),("z11","UA",4),("z10","UA2",2),("z01","VA2",2)):
        matrices = []
        for aa,uu,vv in ((a,u,v),(am,um,vm),(ha,hu,hv)):
            matrices.append({"A":aa,"UA":uu*aa,"UA2":uu*aa**2,"VA2":vv*aa**2}[word])
        projectors = [cyclic_projector(x,order) for x in matrices]
        if any(not zero(x*x-x) or not zero(x.conjugate().T-x) for x in projectors):
            raise RuntimeError("non-orthogonal local projector")
        strata[point] = {
            "stabilizer":word,"order":order,"normal_weight":1,
            "plus_matrix":matrix_json(matrices[0]),"minus_matrix":matrix_json(matrices[1]),
            "hyperino_matrix":matrix_json(matrices[2]),
            "plus_projector":matrix_json(projectors[0]),"minus_projector":matrix_json(projectors[1]),
            "hyperino_projector":matrix_json(projectors[2]),
            "ranks_plus_minus_complex_hyperino":[int(x.rank()) for x in projectors],
        }
        if order == 4:
            counts = [int(cyclic_projector(matrices[0],4,k).rank()) for k in range(4)]
            strata[point]["plus_eigenphase_multiplicities_m0123"] = counts
            strata[point]["normal_Delta"] = sum(n*s for n,s in zip(counts,contract["signs"]))
    pp,pm,ph = constant_projector(a,u,v),constant_projector(am,um,vm),constant_projector(ha,hu,hv)
    np,nm,nh = (int(x.rank()) for x in (pp,pm,ph))
    if nh != 2*(np+nm):
        raise RuntimeError("SMW constant-mode counting disagrees with N1 scalars")
    parities = {"hyperscalars":[0,0,1,0,1,q%2],"hyperinos":[1,0,0,0,1,q%2]}
    kernel = {field:{name:sum(x*y for x,y in zip(row,bits))%2
                     for name,bits in contract["kernel"].items()} for field,row in parities.items()}
    if any(x for row in kernel.values() for x in row.values()):
        raise RuntimeError("singlet block fails Gammahat kernel descent")
    return {
        "kind":kind,"q_magnitude":q,"m":m if kind=="line" else None,
        "effective_translation_eta":eta if kind=="line" else None,"hyper_count":d,
        "continuous_symplectic_charge_diagonal":[q]*d+[-q]*d,
        "finite_q8_symplectic_pair":[q%8,(-q)%8],
        "C8_translation_phase":int(chi),"compensating_flavor_translation_factor":int(chi),
        "effective_plus":{k:matrix_json(x) for k,x in plus.items()},
        "effective_minus_column":{k:matrix_json(x) for k,x in minus.items()},
        "underlying_flavor":{"A":matrix_json(af),"U":matrix_json(uf),"V":matrix_json(vf),
                             "external_k":matrix_json(k),"symplectic_J":matrix_json(jf)},
        "square_relations":{"plus":plus_checks,"minus":minus_checks},
        "SMW_flavor_checks":smw_checks,"hyperino_checks":hyperino_checks,
        "Gammahat_kernel_parities":parities,"Gammahat_kernel_action_exponents_mod2":kernel,
        "strata":strata,
        "constant_projectors":{"plus":matrix_json(pp),"minus":matrix_json(pm),"complex_hyperino":matrix_json(ph)},
        "constant_modes":{"plus":np,"minus":nm,"complex_hyperino":nh,"SMW_independent_Weyl":nh//2,
                          "N1_chiral_charges":[q]*np+[-q]*nm},
        "constant_mode_scope":"flat zero-flux free bulk kinetic operator; interactions and VEV-induced masses unconstructed",
    }


def witness(specification, contract):
    blocks=[]
    counts={q:0 for q in (0,2,4,6,8)}
    charges=[]
    totals={point:[0,0,0] for point in ("z00","z11","z10","z01")}
    delta={"z00":0,"z11":0}
    for q,kind,m,eta,copies in specification:
        if copies <= 0:
            continue
        block=block_certificate(q,kind,m,eta,contract)
        blocks.append({"copies":copies,"certificate":block})
        counts[q]+=copies*block["hyper_count"]
        charges+=copies*block["constant_modes"]["N1_chiral_charges"]
        for point in totals:
            totals[point]=[a+copies*b for a,b in zip(totals[point],block["strata"][point]["ranks_plus_minus_complex_hyperino"])]
        for point in delta:
            delta[point]+=copies*block["strata"][point]["normal_Delta"]
    if list(counts.values()) != contract["counts"]:
        raise RuntimeError("block direct sum changed V91 hyper counts")
    return {"direct_sum_blocks":blocks,"hyper_counts_by_q":[[q,n] for q,n in counts.items()],
            "total_6D_hypers":sum(counts.values()),"complex_symplectic_dimension":2*sum(counts.values()),
            "local_invariant_ranks_plus_minus_complex_hyperino":totals,"normal_Delta_by_corner":delta,
            "constant_N1_chiral_count":len(charges),"constant_N1_signed_continuous_charges":sorted(charges),
            "constant_N1_finite_q8_residues":sorted(q%8 for q in charges),
            "constant_uncharged_N1_chiral_count":charges.count(0),
            "constant_chiral_charge_moments":{"TrQ":sum(charges),"TrQ3":sum(q**3 for q in charges)},
            "local_invariant_ranks_are_not_constant_mode_counts":True}


def certificate_content():
    p=load_parents()
    contract=source_contract(p)
    # This first witness minimizes the number of zero modes after stipulating
    # one +8 and one -8 Phi mode.  It does NOT satisfy the normal-channel target.
    two_spec=[(q,"line",1,1,n-(2 if q==8 else 0))
              for q,n in zip((0,2,4,6,8),contract["counts"])]
    two_spec += [(8,"line",0,1,1),(8,"line",3,1,1)]
    two=witness(two_spec,contract)
    # The second witness extends the pinned 10+64*4 V71 construction.  The
    # extra ordinary untwisted U1 gaugino is a NEW explicit lift choice.
    aligned_spec=[(q,"four_orbit",0,1,n//4)
                  for q,n in zip((0,2,4,6,8),contract["counts"])]
    aligned_spec += [(2,"line",0,1,3),(4,"line",0,1,3),(6,"line",0,1,3),
                     (8,"line",0,1,1),(8,"line",3,1,1)]
    aligned=witness(aligned_spec,contract)
    previous=p["v71"]["neutral_266_phase_classification"]["component_ledger_over_192"]["before_266_neutrals"]
    if previous != [86,-14]:
        raise RuntimeError("V71 inherited normal-channel base changed")
    # The adjoint of U1 has one neutral gaugino: opposite hyperino chirality,
    # ordinary N1-preserving m=0 twist.  This is the negative of s_0*(11,1).
    vector_add=[-contract["signs"][0]*x for x in (11,1)]
    base=[a+b for a,b in zip(previous,vector_add)]
    target=(base[1]-base[0])//10
    normal_rows={}
    for name,row in (("two_mode_unaligned",two),("eleven_mode_normal_aligned",aligned)):
        normal_rows[name]={}
        for point,delta in row["normal_Delta_by_corner"].items():
            coefficients=[base[0]+11*delta,base[1]+delta]
            normal_rows[name][point]={"Delta":delta,"coefficients_x3_xp_over192":coefficients,
                                      "aligned_with_x_p1_T6":coefficients[0]==coefficients[1]}
    signs=[]
    for choices in itertools.product((-1,1),repeat=9):
        ch=[q*s for q,s in zip([2]*3+[4]*3+[6]*3,choices)]+[8,-8]
        if sum(ch)==0 and sum(q**3 for q in ch)==0:
            signs.append(choices)
    if two["constant_N1_chiral_count"]!=2 or aligned["constant_N1_chiral_count"]!=11 or target!=-11:
        raise RuntimeError("projector witness count changed")
    return {
        "schema":"v92_singlet_projector_certificate_v1",
        "input_core_hashes":{key:core for key,(_,core) in PARENTS.items()},
        "scope":"new smooth-sector flat Gammahat representation witnesses at the symmetric hypermultiplet target origin; no full localized quantum action",
        "source_derived_four_orbit_matrices":{key:matrix_json(contract[key]) for key in ("A4","U4","V4")},
        "new_flavor_sector":{
            "replacement":"Sp(266) -> Sp(267) in the neutral/Spin11-singlet factor of the kernel",
            "candidate_symmetric_QK_target":"Sp(267,1)/(Sp(267) x Sp(1)) at its fixed origin",
            "charge_centralizer":"Sp(144) x U(3) x U(19) x U(11) x U(90)",
            "all_block_twists_commute_with_the_gauged_continuous_U1":True,
            "kernel_coordinates":["T","Spin11","R","H3","H267","k4"],
            "kernel_generators":contract["kernel"],
            "selected_external_C8_exponents_A_U_V":[0,2,2],
            "primitive_external_k_is_an_independent_internal_generator":True,
            "q8_is_q_mod8_not_the_continuous_charge":True,
            "q4_pair_has_same_residue_but_opposite_continuous_charges":True,
            "q8_pair_is_finitely_neutral_but_continuously_charged":True,
            "independent_4D_Z4R_charges_of_new_singlets_frozen":False,
            "orbifold_rotation_m_is_the_independent_4D_Z4R_charge":False,
            "global_gauged_QK_action_away_from_origin_constructed":False,
        },
        "parameterized_line_family":{
            "parameters":"for each charge q choose n_(q,m,eta)>=0, m=0..3, eta=+/-1, with sum_(m,eta)n=N_q",
            "effective_A":"i^m", "effective_U_V":"eta",
            "flavor_A_pair":"diag(zeta*i^m,zeta^-1*i^-m)",
            "flavor_U_V_pair":"(-1)^(q/2)*eta times I2",
            "plus_constant_criterion":"m=0 and eta=+1", "minus_constant_criterion":"m=3 and eta=+1",
            "N_zero":"sum_q[n_(q,0,+)+n_(q,3,+)]",
            "Delta00":"sum_(q,m,eta) n_(q,m,eta)*s_m; s=(-1,+1,+1,-1)",
            "Delta11":"sum_(q,m,eta) n_(q,m,eta)*eta*s_m",
            "unique_projector_assignment_forced_by_V91":False,
        },
        "two_mode_unaligned_witness":two,
        "eleven_mode_normal_aligned_witness":aligned,
        "conditional_normal_channel":{
            "new_U1_gaugino_lift_choice":"ordinary untwisted adjoint U1, N1-preserving V70 Lorentz/R lift; no extra isotropy or tensor twist",
            "this_U1_lift_was_previously_frozen":False,
            "inherited_gravity_tensor_and_Spin11_charged_base_over192":previous,
            "new_U1_gaugino_addition_over192":vector_add,
            "new_base_over192":base,
            "restricted_channel":"set gauge curvatures to zero; retain x^3 and x*p1(T4) only; no localized normal-charge additions",
            "target_for_alignment_with_x_p1_T6":target,
            "witness_coefficients":normal_rows,
            "minimum_constant_chiral_modes_under_two_equal_corner_target":11,
            "lower_bound_scope":"the V71 unitary square-space-group translation-character argument with target Delta=-11 and the stated normal-channel assumptions",
            "nine_additional_modes_beyond_two_Phi_under_this_target":9,
            "selected_minimal_four_orbit_family_extra_charges":[2,2,2,4,4,4,6,6,6],
            "charge_sign_choice":"all nine residual q2,q4,q6 lines have m=0 and positive continuous charge; this is new action data, not forced by the six-dimensional magnitudes",
            "extra_modes_must_be_charged_in_every_possible_assignment":False,
            "selected_extra_modes_have_mass_terms_or_stabilization_constructed":False,
            "sign_choices_for_nine_selected_extra_modes":2**9,
            "sign_choices_cancel_both_4D_U1_linear_and_cubic_moments_without_other_sectors":len(signs),
            "nonzero_4D_singlet_cubic_moment_is_a_full_anomaly_no_go":False,
            "normal_alignment_is_full_fixed_wall_anomaly_cancellation":False,
        },
        "open_data":[
            "actual localized family/rank/compensator representations of each complete wall group",
            "local U1 gauge and mixed normal-gauge anomaly tensors after these singlet choices",
            "gravity, tensor, ghost, antifield and common regulator projectors in the same tangential group",
            "global gauged quaternionic-Kahler sigma model, composite R connection and nonzero-VEV background",
            "mass/stabilization/decay terms for the nine additional constant modes in the aligned witness",
            "relative differential WCS, Pfaffian orientation, KK eta and Dai-Freed trivialization",
        ],
        "terminal_decision":{"smooth_singlet_matrix_projector_witnesses_constructed":True,
                             "constant_mode_counts_derived_from_joint_kernels":True,
                             "unique_projector_assignment_selected":False,
                             "full_orbibundle_or_quantum_action_accepted":False,
                             "full_fixed_wall_anomaly_cancelled":False,"closed_gates":[]},
        "primary_sources":[
            {"url":"https://arxiv.org/abs/hep-th/0602155","use":"N1 hyper partner orbifold constraint; equations 44-45, via the bound V70 convention"},
            {"url":"https://arxiv.org/abs/hep-th/0612212","use":"normal fixed-locus spin-half density; via the bound V71 normal-channel calculation"},
        ],
    }


def build_certificate():
    report=certificate_content()
    report["core_sha256"]=canonical_sha(report)
    return report


def validate_certificate(report):
    if report.get("core_sha256")!=canonical_sha(report) or report!=build_certificate():
        raise RuntimeError("singlet projector certificate changed")


if __name__ == "__main__":
    print(json.dumps(build_certificate(),indent=2,sort_keys=True))
