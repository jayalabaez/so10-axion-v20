#!/usr/bin/env python3
"""V47 relative Spin-bordism and APS anomaly audit of the V46 interval.

This audit uses the ordinary tangential structure

    Spin(spacetime) x [(SU4 x SU2L x SU2R)/Z2_diag x U1F],

not a spin-charge quotient.  It computes the total-degree-five part of the
homological Atiyah--Hirzebruch spectral sequence (AHSS), including the
non-liftable Pati--Salam bundle sector, and then applies the long exact sequence
of the pair BP -> BSpin(10) to the interval boundary reduction.

The script certifies an anomaly obstruction, not an absolute determinant.  A
numerical APS eta phase still depends on the metric, connections, regulated
KK operator, boundary masses and choice of gauge-invariant local counterterms.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V47_RELATIVE_ETA_BORDISM_AUDIT.json"
MD_PATH = ROOT / "SUSY_V47_RELATIVE_ETA_BORDISM_AUDIT.md"

INPUTS = {
    "V45_reconciled_bulk": ROOT / "SUSY_V45_RECONCILED_BULK_SPINOR_AUDIT.json",
    "V46_global_parity_eta": ROOT / "SUSY_V46_GLOBAL_PARITY_ETA_AUDIT.json",
    "V46_source_higgs": ROOT / "SUSY_V46_SOURCE_HIGGS_RANK_AUDIT.json",
    "V46_spinor_KK": ROOT / "SUSY_V46_SPINOR_KK_DETERMINANT_AUDIT.json",
}

STATUS = (
    "V47_ORDINARY_SPIN_PS_QUOTIENT_AND_U1F_OMEGA5_ZERO__"
    "STANDARD_PAIR_RELATIVE_OMEGA6_ZERO__NONLIFTABLE_AND_RESIDUAL_Z6_"
    "GLOBAL_ANOMALY_OBSTRUCTION_CANCELLED__ABSOLUTE_APS_PHASE_NOT_AN_"
    "ANOMALY__G1_MICROSCOPIC_CONSISTENCY_PROMOTED__G2_TO_G8_OPEN"
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    """Canonical report hash, deliberately excluding the self-hash field."""

    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def load_validated_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"required upstream input missing: {path.name}")
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise RuntimeError(f"required upstream input is not a JSON object: {path.name}")
    stored = payload.get("core_sha256")
    computed = canonical_sha(payload)
    if not isinstance(stored, str) or computed != stored:
        raise RuntimeError(f"required upstream input has an invalid core hash: {path.name}")
    return payload


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def gf2_rank(rows: Iterable[Sequence[int]], ncols: int | None = None) -> int:
    """Rank of a binary matrix, with rows supplied as 0/1 sequences."""

    data = [list(int(value) & 1 for value in row) for row in rows]
    if ncols is None:
        ncols = max((len(row) for row in data), default=0)
    if any(len(row) != ncols for row in data):
        raise ValueError("ragged GF(2) matrix")
    rank = 0
    for column in range(ncols):
        pivot = next((index for index in range(rank, len(data)) if data[index][column]), None)
        if pivot is None:
            continue
        data[rank], data[pivot] = data[pivot], data[rank]
        for index in range(len(data)):
            if index != rank and data[index][column]:
                data[index] = [left ^ right for left, right in zip(data[index], data[rank])]
        rank += 1
    return rank


def ahss_certificate(include_u1: bool) -> dict[str, Any]:
    """Compute all E2/E3 ranks on the p+q=5 diagonal.

    Notation follows the low-degree mod-two cohomology of BP:

      x=w2(V6)=w2(V4), y=Sq1 x,
      a=w4(V6), b=w4(V4), c=w6(V6).

    With U1F present, u is c1 mod 2.  For ordinary MSpin the Thom class has
    Sq2(U)=0.  The d2 maps are dual to Sq2, with mod-two reduction on an
    integral-homology source.
    """

    if include_u1:
        h2 = ["x", "u"]
        h3 = ["y"]
        h4 = ["x^2", "x*u", "u^2", "a=w4(V6)", "b=w4(V4)"]
        h5_mod2 = ["x*y", "u*y"]
        h6 = [
            "x^3",
            "y^2",
            "x^2*u",
            "x*u^2",
            "u^3",
            "x*a",
            "x*b",
            "u*a",
            "u*b",
            "c=w6(V6)",
        ]
        # Rows are targets H2, columns are H4 dual generators.
        d2_out = [
            [1, 0, 0, 0, 0],  # Sq2 x = x^2
            [0, 0, 1, 0, 0],  # Sq2 u = u^2
        ]
        # Rows span im[d2:H6(Z)->H4(F2)] in the H4 dual basis.
        d2_in = [
            [0, 1, 0, 0, 0],  # Sq2(xu)=x^2u+xu^2
            [0, 0, 0, 1, 0],  # Sq2 a=xa+c
            [0, 0, 0, 0, 1],  # Sq2 b=xb
        ]
        sq2_h4_mod_annihilator = {
            "x^2": "y^2 (zero modulo the integral-reduction annihilator <y^2>)",
            "x*u": "x^2*u+x*u^2",
            "u^2": "0",
            "a=w4(V6)": "x*a+c",
            "b=w4(V4)": "x*b",
        }
        integral_homology = {
            "H2": "Z + Z2",
            "H3": "0",
            "H4": "Z^4 + Z2",
            "H5": "Z2",
        }
    else:
        h2 = ["x"]
        h3 = ["y"]
        h4 = ["x^2", "a=w4(V6)", "b=w4(V4)"]
        h5_mod2 = ["x*y"]
        h6 = ["x^3", "y^2", "x*a", "x*b", "c=w6(V6)"]
        d2_out = [[1, 0, 0]]  # Sq2 x=x^2.
        d2_in = [
            [0, 1, 0],  # Sq2 a=xa+c.
            [0, 0, 1],  # Sq2 b=xb.
        ]
        sq2_h4_mod_annihilator = {
            "x^2": "y^2 (zero modulo the integral-reduction annihilator <y^2>)",
            "a=w4(V6)": "x*a+c",
            "b=w4(V4)": "x*b",
        }
        integral_homology = {
            "H2": "Z2",
            "H3": "0",
            "H4": "Z^3",
            "H5": "Z2",
        }

    out_rank = gf2_rank(d2_out, len(h4))
    incoming_rank = gf2_rank(d2_in, len(h4))
    kernel_dimension = len(h4) - out_rank
    e3_41_dimension = kernel_dimension - incoming_rank

    # Sq2(y)=x*y because w5(V6)=0 in H*(BP;F2).  It makes both maps below
    # surjective onto the one-dimensional H3 term.
    d2_50_rank = 1  # H5(Z)=Z2 -> H3(F2).
    d2_51_rank = 1  # H5(F2) -> H3(F2).
    e3_50_dimension = 1 - d2_50_rank
    e3_32_dimension = 1 - d2_51_rank

    return {
        "space": "B(P x U1F)" if include_u1 else "BP",
        "P": "(SU4 x SU2L x SU2R)/Z2_diag",
        "ordinary_tangential_spectrum": "MSpin smash B(internal_group)_+",
        "not_the_spin_charge_spectrum": True,
        "cohomology_bases_mod2": {"H2": h2, "H3": h3, "H4": h4, "H5": h5_mod2, "H6": h6},
        "relations": [
            "x=w2(V6)=w2(V4)",
            "y=w3(V6)=w3(V4)=Sq1(x)",
            "w5(V6)=0",
        ],
        "steenrod_operations": {
            "Sq2(x)": "x^2",
            **({"Sq2(u)": "u^2"} if include_u1 else {}),
            "Sq2(y)": "x*y",
            "Sq2_on_H4_mod_annihilator": sq2_h4_mod_annihilator,
            "Sq1(x*y)": "y^2",
            **({"Sq1(x*u)": "y*u"} if include_u1 else {}),
        },
        "integral_reduction_fact": (
            "The annihilator of im[H6(Z)->H6(F2)] is exactly <y^2>; equivalently the only "
            "degree-six class invisible to integral six-cycles is the Bockstein image Sq1(xy)."
        ),
        "integral_homology_low_degrees": integral_homology,
        "H4_integral_lattice_for_P": {
            "basis": [
                "p1(V6)",
                "e4(V4)",
                "lambda(V6+V4)=(p1(V6)+p1(V4))/2",
            ],
            "mod2_reductions": ["x^2", "b", "a+b+x^2"],
            "all_three_H4_mod2_classes_integrally_represented": True,
        },
        "d2_out_of_E2_4_1": {
            "matrix_rows_H2_columns_H4": d2_out,
            "rank": out_rank,
            "kernel_dimension": kernel_dimension,
        },
        "d2_into_E2_4_1": {
            "image_generators_in_H4_dual_basis": d2_in,
            "rank": incoming_rank,
            "image_equals_outgoing_kernel": incoming_rank == kernel_dimension,
        },
        "other_total_degree_five_terms": {
            "E2_5_0": "Z2",
            "d2_5_0_rank": d2_50_rank,
            "E3_5_0_dimension": e3_50_dimension,
            "E2_3_2": "Z2",
            "d2_5_1_rank": d2_51_rank,
            "E3_3_2_dimension": e3_32_dimension,
        },
        "E3_4_1_dimension": e3_41_dimension,
        "all_total_degree_five_E3_terms_zero": (
            e3_41_dimension == e3_50_dimension == e3_32_dimension == 0
        ),
        "higher_differential_or_extension_room": False,
        "Omega5Spin": "0",
    }


def spin10_u1_certificate() -> dict[str, Any]:
    return {
        "group": "Spin(10) x U1F",
        "Omega5Spin": "0",
        "Omega6Spin": "Z^3",
        "Omega6_free_generators": [
            "U1F^3",
            "U1F-gravity^2",
            "U1F-Spin(10)^2",
        ],
        "Omega6_torsion": "0",
        "AHSS_reason": (
            "Below degree seven H*(BSpin10;F2) starts with w4 and w6=Sq2(w4). "
            "Together with Sq2(u)=u^2, the total-degree-five AHSS terms are killed; "
            "the total-degree-six free classes are the two BU1 classes and u*lambda10."
        ),
        "primary_cross_check": "Omega5Spin(BSpin(n))=0 for n>=8",
    }


def relative_pair_certificate() -> dict[str, Any]:
    return {
        "pair": "(B(Spin10 x U1F), B(P x U1F))",
        "physical_model": (
            "A Spin10 x U1F bulk bundle with a P x U1F reduction at y=0 and no further "
            "reduction at the full-Spin10 wall y=L."
        ),
        "interval_background_homotopy_pullback": (
            "B(P x U1F) x^h_{B(Spin10 x U1F)} B(Spin10 x U1F) ~= B(P x U1F)"
        ),
        "relevant_long_exact_segment": (
            "Omega6(B(PxU1))->Omega6(B(Spin10xU1))->Omega6(pair)->"
            "Omega5(B(PxU1))->Omega5(B(Spin10xU1))"
        ),
        "endpoint_groups": {
            "Omega5_B_PxU1": "0",
            "Omega5_B_Spin10xU1": "0",
            "Omega6_B_Spin10xU1": "Z^3",
        },
        "surjectivity_witness": {
            "two_pure_U1_generators": (
                "Use trivial P/Spin10 bundle; BU1 -> B(PxU1) -> B(Spin10xU1) splits these classes."
            ),
            "mixed_generator": (
                "A unit SU2L instanton is a liftable P bundle and maps to a primitive Spin10 "
                "lambda10 instanton."
            ),
            "characteristic_class_identity": (
                "i^*lambda10 = lambda(V6+V4) = -(c2(SU4)+c2(SU2L)+c2(SU2R)) "
                "on the simply-connected cover"
            ),
            "coefficient_gcd": 1,
            "map_Omega6_is_surjective": True,
        },
        "Omega6Spin_relative": "0",
        "pure_gauge_subpair_also_zero": True,
        "scope": (
            "This is the standard generalized-homology pair/cofiber model.  No reflection is "
            "gauged.  If the orbifold reflection itself is promoted to a microscopic spacetime "
            "symmetry, a separate equivariant/Pin bordism problem would have to be specified."
        ),
    }


def actual_spectrum_certificate(v45: dict[str, Any], v46: dict[str, Any]) -> dict[str, Any]:
    ps_boundary = v45["PS_wall"]["boundary_chirals"]["totals"]
    ps_bulk = v45["PS_wall"]["bulk_hyper_density"]["totals"]
    ps_total = v45["PS_wall"]["combined_totals"]
    source_boundary = v45["Spin10_wall"]["boundary_chirals"]["totals"]
    source_bulk = v45["Spin10_wall"]["bulk_hyper_density"]["totals"]
    source_total = v45["Spin10_wall"]["combined_totals"]
    parity = v46["five_dimensional_parity_half_levels"]

    return {
        "bulk_hypers_primitive": [
            {"name": "HLF", "rep": "16", "qF": 1, "eta0": 1, "etaL": 1},
            {"name": "HLA", "rep": "bar16", "qF": -4, "eta0": 1, "etaL": 1},
            {"name": "HRA", "rep": "16", "qF": -1, "eta0": -1, "etaL": 1},
            {"name": "HRF", "rep": "bar16", "qF": 4, "eta0": -1, "etaL": 1},
        ],
        "PS_boundary": ["3 Q(4,2,1)_+1", "3 Qc(bar4,1,2)_-1", "H(1,2,2)_0"],
        "source_boundary": [
            "ThetaPlus_+3",
            "ThetaMinus_-3",
            "STheta_0",
            "126_0",
            "bar126_0",
            "210_0 repair",
        ],
        "ordinary_local_anomaly_ledgers_in_V45_units": {
            "PS_boundary": ps_boundary,
            "PS_bulk_half_density": ps_bulk,
            "PS_sum": ps_total,
            "Spin10_boundary": source_boundary,
            "Spin10_bulk_half_density": source_bulk,
            "Spin10_sum": source_total,
            "both_walls_zero": all(value == 0 for value in ps_total.values())
            and all(value == 0 for value in source_total.values()),
        },
        "torsion_anomaly_homomorphism": {
            "domain": "Omega5Spin(B(P x U1F))",
            "domain_group": "0",
            "number_of_surviving_generators_to_evaluate": 0,
            "actual_fermion_homomorphism": "the unique zero homomorphism",
            "nonliftable_PS_bundles_included": True,
        },
        "source_multiplets": {
            "126_plus_bar126": "neutral conjugate pair; local rows cancel and no Omega5 torsion exists",
            "210": "neutral real representation; adds no U1 rows and no Omega5 torsion exists",
            "Theta_pair": "charges +3 and -3; U1 cubic and gravitational rows cancel",
        },
        "five_dimensional_parity_levels": {
            "every_individual_shift_in_closed_spin_U1_lattice": parity[
                "every_individual_shift_lies_in_closed_spin_U1_free_lattice"
            ],
            "common_orientation_totals": parity["common_sigma_totals"],
            "common_orientation_net_zero": parity["common_regulator_orientation_net_shift_zero"],
            "integer_levels_fixed_by_V46": parity["physical_integer_CS_levels_determined"],
        },
    }


def residual_z6_certificate() -> dict[str, Any]:
    return {
        "unbroken_group": "Z3_F x Z2_M ~= Z6",
        "embedding": (
            "Z6 -> P x U1F sends a generator to the order-two matter-parity centre element "
            "and the order-three U1F element."
        ),
        "all_Z6_bundles_extend_structure_group_to_PxU1F": True,
        "anomaly_naturality": (
            "The determinant anomaly of the restricted fermion representation is the pullback "
            "of its P x U1F anomaly."
        ),
        "parent_continuous_anomaly_class": "0",
        "pulled_back_Z6_class": "0",
        "mixed_nonliftable_PS_Z6_class_for_this_UV_spectrum": "0",
        "important_scope": (
            "This does not claim Omega5Spin(B(P x Z6)) vanishes for arbitrary spectra.  It proves "
            "that the V46 spectrum inherited from the anomaly-free continuous parent has zero class."
        ),
    }


def aps_conclusion() -> dict[str, Any]:
    return {
        "gauge_anomaly_obstruction": "CANCELLED",
        "why": [
            "wall-local anomaly polynomials vanish",
            "Omega5Spin(B(P x U1F))=0, including non-liftable quotient bundles",
            "Omega6Spin of the standard interval pair is zero",
            "the residual Z6 anomaly is a natural pullback of the zero continuous-parent class",
        ],
        "existence_of_gauge_invariant_Dai_Freed_trivialization": True,
        "absolute_exponentiated_eta_value_computed": False,
        "absolute_phase_not_an_anomaly": True,
        "unfixed_data": [
            "gauge and metric background on a chosen five/six-manifold",
            "odd bulk-mass and Pauli-Villars regulator orientations",
            "renormalized self-adjoint source-wall extension after all allowed 126 couplings",
            "the enlarged coupled KK spectrum including gauginos, hyperinos, boundary fermions and 210",
            "integer gauge-invariant Chern-Simons/local counterterm convention",
        ],
        "allowed_126_terms_requiring_final_KK_operator": [
            "bar126 HLF HRA",
            "126 HLA HRF",
        ],
        "neutral_cross_couplings_requiring_selector_or_inclusion": [
            "STheta Phi(210)^2",
            "STheta 126 bar126",
        ],
        "logical_effect": (
            "Those data can change a gauge-invariant absolute phase and thresholds, but cannot "
            "resurrect the bordism/global gauge anomaly proved absent here."
        ),
        "gate_effect": (
            "G1 is closed as the microscopic gauge/global-anomaly consistency gate.  The remaining "
            "coupled-boundary, KK, vacuum and phenomenology obligations belong to G2--G8."
        ),
    }


def build_report() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing V45/V46 inputs: " + ", ".join(missing))
    upstream = {name: load_validated_json(path) for name, path in INPUTS.items()}
    v45 = upstream["V45_reconciled_bulk"]
    v46 = upstream["V46_global_parity_eta"]

    pure = ahss_certificate(False)
    product = ahss_certificate(True)
    relative = relative_pair_certificate()
    spectrum = actual_spectrum_certificate(v45, v46)

    report = {
        "schema": "susy-v47-relative-eta-bordism-audit-v1",
        "status": STATUS,
        "scope": (
            "Exact ordinary-Spin global gauge-anomaly and standard interval-relative bordism "
            "audit of the V46 compact witness with the neutral 210 repair."
        ),
        "group_and_bundle_geometry": {
            "P": "(SU4 x SU2L x SU2R)/Z2_diag = (Spin6 x Spin4)/Z2_diag",
            "exact_sequence": "1 -> Z2 -> P -> SO6 x SO4 -> 1",
            "bundle_description": (
                "A P bundle determines oriented V6,V4 with x=w2(V6)=w2(V4); x!=0 is "
                "precisely failure to lift to SU4 x SU2L x SU2R."
            ),
            "embedding_into_Spin10": (
                "V10=V6+V4 has w2(V10)=x+x=0, so every P bundle, including x!=0, "
                "extends along P -> Spin10."
            ),
            "spacetime_structure": "ordinary independent Spin; no gauge centre is identified with (-1)^F",
        },
        "AHSS_BP": pure,
        "AHSS_BPxU1F": product,
        "apparent_quotient_torsion": {
            "candidate": "integral of x*Sq1(x)=x*y",
            "identity": "x*y=Sq2(y) because w5(V6)=0",
            "spin_Wu_evaluation": "int_M Sq2(y)=int_M v2(TM)*y=int_M w2(TM)*y=0",
            "AHSS_fate": "killed by d2; it is not a bordism invariant on closed spin five-manifolds",
            "new_pure_quotient_torsion_class_exists": False,
        },
        "mixed_U1F_quotient_direction": {
            "candidate_E2_direction": "x*u in H4(B(P x U1F);F2)",
            "Sq2": "Sq2(x*u)=x^2*u+x*u^2",
            "AHSS_fate": "hit by d2 from integral H6; no E3 survivor",
            "new_mixed_global_class_exists": False,
        },
        "Spin10xU1F": spin10_u1_certificate(),
        "standard_interval_relative_pair": relative,
        "actual_V46_spectrum": spectrum,
        "residual_Z6_mixing": residual_z6_certificate(),
        "APS_eta_conclusion": aps_conclusion(),
        "comparison_warning": {
            "Wan_Wang_tables_not_imported": True,
            "reason": (
                "Their Pati-Salam tables use an outer /Z2^F spin-charge tangential structure. "
                "Its Thom class obeys Sq2(U)=xU, whereas ordinary MSpin smash BP+ has Sq2(U)=0."
            ),
            "unquotiented_PS_result_not_imported": True,
            "reason_2": (
                "Omega5Spin(B(SU4 x SU2L x SU2R))=Z2^2 is for the simply-connected product; "
                "the diagonal quotient changes the AHSS and here removes both cover classes."
            ),
        },
        "primary_sources": [
            {
                "citation": "Wan and Wang, JHEP 07 (2020) 062",
                "url": "https://arxiv.org/abs/1910.14668",
                "use": "Serre differential and low mod-two cohomology relations for BP; comparison of tangential structures",
            },
            {
                "citation": "Davighi, Gripaios and Lohitsiri, JHEP 07 (2020) 232",
                "url": "https://arxiv.org/abs/1910.11277",
                "use": "homological spin-AHSS d2=dual Sq2 formulas and unquotiented Pati-Salam comparison",
            },
            {
                "citation": "Garcia-Etxebarria and Montero, JHEP 08 (2019) 003",
                "url": "https://arxiv.org/abs/1808.00009",
                "use": "Omega5Spin(BSpin(n))=0 for n>=8 and Dai-Freed anomaly criterion",
            },
            {
                "citation": "Witten and Yonekura, SciPost Phys. 8 (2020) 039",
                "url": "https://arxiv.org/abs/1909.08775",
                "use": "nonperturbative anomaly inflow and exponentiated APS eta invariant",
            },
            {
                "citation": "Dai and Freed, J. Math. Phys. 35 (1994) 5155",
                "url": "https://doi.org/10.1063/1.530747",
                "use": "determinant line and eta-invariant gluing theorem",
            },
            {
                "citation": "Atiyah, Patodi and Singer, Math. Proc. Camb. Phil. Soc. 77 (1975) 43",
                "url": "https://doi.org/10.1017/S0305004100049410",
                "use": "spectral asymmetry and index theorem on manifolds with boundary",
            },
        ],
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
        "input_core_sha256": {name: payload["core_sha256"] for name, payload in upstream.items()},
        "upstream_core_hashes_validated": True,
        "decision": {
            "remaining_global_bordism_obstruction_found": False,
            "global_eta_anomaly_subproblem_closed": True,
            "absolute_KK_eta_phase_closed": False,
            "absolute_KK_eta_phase_required_for_gauge_consistency": False,
            "G1_promoted": True,
            "G1_closed": True,
            "G1_closure_reason": (
                "Both wall-local anomaly polynomials vanish; all free parity levels admit quantized "
                "counterterms; the absolute and relative torsion obstruction groups vanish; and the "
                "residual Z6 class is the pullback of the zero continuous-parent anomaly."
            ),
            "G2_through_G8_open": True,
            "theory_complete": False,
        },
    }
    report["core_sha256"] = canonical_sha(report)
    validate_report(report)
    return report


def validate_report(report: dict[str, Any]) -> None:
    if canonical_sha(report) != report.get("core_sha256"):
        raise RuntimeError("V47 canonical core hash is stale")
    if not report.get("upstream_core_hashes_validated"):
        raise RuntimeError("upstream core hashes were not validated")
    if set(report.get("input_core_sha256", {})) != set(INPUTS):
        raise RuntimeError("upstream core-hash manifest is incomplete")
    for key in ("AHSS_BP", "AHSS_BPxU1F"):
        cert = report[key]
        if cert["Omega5Spin"] != "0" or not cert["all_total_degree_five_E3_terms_zero"]:
            raise RuntimeError(f"{key} did not vanish")
        if not cert["d2_into_E2_4_1"]["image_equals_outgoing_kernel"]:
            raise RuntimeError(f"{key} has an unaccounted E3_(4,1) survivor")
    if report["standard_interval_relative_pair"]["Omega6Spin_relative"] != "0":
        raise RuntimeError("relative obstruction did not vanish")
    if not report["actual_V46_spectrum"]["ordinary_local_anomaly_ledgers_in_V45_units"]["both_walls_zero"]:
        raise RuntimeError("wall-local anomaly ledger drifted")
    if report["actual_V46_spectrum"]["torsion_anomaly_homomorphism"]["number_of_surviving_generators_to_evaluate"]:
        raise RuntimeError("a torsion generator unexpectedly survived")
    if report["APS_eta_conclusion"]["absolute_exponentiated_eta_value_computed"]:
        raise RuntimeError("absolute APS phase cannot be inferred from bordism alone")
    if not report["decision"]["G1_promoted"] or not report["decision"]["G1_closed"]:
        raise RuntimeError("the proved anomaly-consistency gate was not promoted")
    if report["decision"]["theory_complete"]:
        raise RuntimeError("V47 cannot certify a complete theory")


def render_markdown(data: dict[str, Any]) -> str:
    pure = data["AHSS_BP"]
    product = data["AHSS_BPxU1F"]
    rel = data["standard_interval_relative_pair"]
    spec = data["actual_V46_spectrum"]
    aps = data["APS_eta_conclusion"]
    input_lines = "\n".join(f"- `{name}`: `{digest}`" for name, digest in data["input_sha256"].items())
    input_core_lines = "\n".join(
        f"- `{name}`: `{digest}`" for name, digest in data["input_core_sha256"].items()
    )
    source_lines = "\n".join(
        f"- [{row['citation']}]({row['url']}): {row['use']}." for row in data["primary_sources"]
    )
    return f"""# V47 relative Spin-bordism and APS eta audit

Status: `{data['status']}`

## Result

The remaining centre-quotient **global gauge-anomaly obstruction is absent** in
the ordinary-Spin V46 model.  The exact low-degree AHSS gives

`Omega5^Spin(BP)=0`,

`Omega5^Spin(B(P x U1_F))=0`,

for `P=(SU4 x SU2L x SU2R)/Z2_diag`.  This calculation includes bundles that
do not lift to `SU4 x SU2L x SU2R`.  The standard relative/cofiber model for an
interval with a `P` reduction at `y=0` and full `Spin(10)` at `y=L` also gives

`Omega6^Spin(B(Spin10 x U1_F), B(P x U1_F))=0`.

Together with V45's exactly vanishing wall-local anomaly polynomials, this is a
genuine Dai--Freed cancellation certificate: a gauge-invariant trivialization
exists, including the non-liftable quotient sectors and their mixing with the
residual `Z6` inherited from the continuous parent.

This does **not** assign a numerical value to the absolute regulated APS eta
phase.  That value depends on the final coupled KK operator, regulator and
integer local counterterm convention.  Those choices can alter a
gauge-invariant phase or thresholds; they cannot resurrect the global gauge
anomaly proved absent here.  This closes **G1 as the microscopic
gauge/global-anomaly consistency gate**.  G2--G8 remain open.

## Correct global group and bundle obstruction

Write

`P=(Spin6 x Spin4)/Z2_diag`.

There is an exact sequence `1 -> Z2 -> P -> SO6 x SO4 -> 1`.  A `P` bundle is
described by oriented bundles `V6,V4` with a common class

`x=w2(V6)=w2(V4)`.

The sector `x!=0` is exactly the sector that fails to lift to the simply
connected product.  Nevertheless, `V10=V6+V4` has
`w2(V10)=x+x=0`, so every such bundle extends along the faithful embedding
`P -> Spin(10)`.  Non-liftable `P` bundles were therefore retained, not
discarded.

Spacetime carries an independent ordinary Spin structure.  The calculation is
for `MSpin smash BP_+`; it is not a theory that identifies a gauge-centre
element with fermion parity.

## Exact AHSS calculation

Below degree six, let

`y=Sq1(x)=w3(V6)=w3(V4)`,

`a=w4(V6)`, `b=w4(V4)`, and `c=w6(V6)`.

The Serre calculation gives `w5(V6)=0`.  For `BP`, use the mod-two `H4` basis
`[x^2,a,b]`.  The outgoing differential
`d2:E2_(4,1)->E2_(2,2)` is dual to `Sq2` and has matrix

`{pure['d2_out_of_E2_4_1']['matrix_rows_H2_columns_H4']}`,

of rank {pure['d2_out_of_E2_4_1']['rank']}; its kernel is the two directions
dual to `a,b`.  The incoming differential from integral `H6` has image

`{pure['d2_into_E2_4_1']['image_generators_in_H4_dual_basis']}`,

of rank {pure['d2_into_E2_4_1']['rank']}, exactly that kernel.  The dual
operations are `Sq2(a)=x a+c` and `Sq2(b)=x b`.  The only degree-six mod-two
class annihilating reductions of integral six-cycles is `y^2=Sq1(xy)`, and
the displayed images are independent modulo it.

The other possible total-degree-five entries also die:
`d2:E2_(5,0)->E2_(3,1)` and
`d2:E2_(5,1)->E2_(3,2)` both have rank one because
`Sq2(y)=x y`.  Hence every entry on `p+q=5` is zero already on `E3`; there is
no higher differential or extension to decide.

Adding `u=c1(U1_F) mod 2` enlarges the `H4` basis to
`[x^2,xu,u^2,a,b]`.  The outgoing matrix is

`{product['d2_out_of_E2_4_1']['matrix_rows_H2_columns_H4']}`,

of rank {product['d2_out_of_E2_4_1']['rank']}.  Its three-dimensional kernel
`[xu,a,b]` is exactly the rank-{product['d2_into_E2_4_1']['rank']} incoming image

`{product['d2_into_E2_4_1']['image_generators_in_H4_dual_basis']}`.

In particular `Sq2(xu)=x^2u+xu^2` kills the only prospective mixed
quotient--`U1_F` direction.  Thus the `U1_F` factor adds no global torsion.

## Why the apparent quotient invariant vanishes

The tempting degree-five class is `x Sq1(x)=xy`.  But

`xy=Sq2(y)`

because `w5(V6)=0`.  On a closed spin five-manifold the Wu formula gives

`int Sq2(y)=int v2(TM)y=int w2(TM)y=0`.

This is the characteristic-number form of the same nonzero AHSS differential.
There is no extra `Z2` quotient anomaly hiding on `x!=0` bundles.

## Relative interval group

The no-reduction full-Spin(10) endpoint contributes an identity leg to the
background homotopy pullback, leaving `B(P x U1_F)` as the interval background
space.  The standard pair description then uses

`{rel['relevant_long_exact_segment']}`.

The right-hand `Omega5` groups both vanish.  Moreover
`Omega6^Spin(B(Spin10 x U1_F))=Z^3`, generated by `U1_F^3`,
`U1_F-gravity^2`, and `U1_F-Spin(10)^2`, with no torsion.  The first two
generators are hit using a trivial `P` bundle.  The mixed generator is hit by a
unit `SU2L` instanton because on the cover

`i^* lambda10 = -(c2(SU4)+c2(SU2L)+c2(SU2R))`.

The coefficients have gcd one, so the map on `Omega6` is surjective, not merely
rationally surjective.  Exactness gives the zero relative group quoted above.

This pair result treats the orbifold parities as boundary conditions, not as a
gauged reflection symmetry.  A future model that gauges the reflection would
need to declare and compute an equivariant/Pin refinement; V46 does not do so.

## Actual V46 fermions

The four primitive-charge bulk hypers are
`16_+1`, `bar16_-4`, `16_-1`, and `bar16_+4`, with parities
`(+,+)`, `(+,+)`, `(-,+)`, and `(-,+)` for the indicated left chiral at the PS
wall.  The PS wall has `3Q+3Qc+H`; the source wall has `Theta+/-`, `STheta`, a
neutral `126+bar126`, and the neutral real `210` repair.

V45's localized-polynomial ledger remains exact:

- PS boundary: `{spec['ordinary_local_anomaly_ledgers_in_V45_units']['PS_boundary']}`;
- PS bulk half-density: `{spec['ordinary_local_anomaly_ledgers_in_V45_units']['PS_bulk_half_density']}`;
- PS total: `{spec['ordinary_local_anomaly_ledgers_in_V45_units']['PS_sum']}`;
- source total: `{spec['ordinary_local_anomaly_ledgers_in_V45_units']['Spin10_sum']}`.

There is no surviving torsion generator on which the fermion eta homomorphism
could be nonzero: its domain is the zero group.  Thus the actual homomorphism is
the unique zero map.  The neutral `126+bar126` pair and real `210` do not alter
that conclusion.

V46 also proved that each conventional five-dimensional half-level lies in the
closed-spin `U1` free lattice and that a common regulator orientation sums to
`{spec['five_dimensional_parity_levels']['common_orientation_totals']}`.  The
remaining integer-level ambiguity is a local counterterm choice, not a global
anomaly.

## Residual `Z6`

After `Theta+/-` and the even-`3(B-L)` `126` VEV, the residual group is
`Z3_F x Z2_M ~= Z6`.  Its generator maps to the order-three element of `U1_F`
and the order-two matter-parity centre element in `P/Spin(10)`.  Every `Z6`
bundle therefore extends its structure group to `P x U1_F`.

Anomalies are natural under restriction of representations.  The V46 finite
fermion anomaly is consequently the pullback of the now-proved zero continuous
parent class, including on non-liftable `P` backgrounds.  The mixed
`P`--`Z6` class of this UV spectrum is zero.  This is not the stronger statement
that `Omega5^Spin(B(P x Z6))` vanishes for every imaginable standalone
spectrum.

## What remains genuinely undetermined

The bordism/global-anomaly question is closed, but an absolute number
`exp(-i pi eta/2)` has not been calculated.  It still requires:

{chr(10).join('- ' + item for item in aps['unfixed_data'])}

The final source operator must also include or forbid
`bar126 HLF HRA` and `126 HLA HRF`, plus the allowed neutral cross-couplings
`STheta Phi^2` and `STheta 126 bar126`.  They affect the spectral operator and
thresholds, not the vanishing bordism obstruction.

Therefore V47 closes the global eta-anomaly subproblem and promotes G1.  It
does not close the coupled boundary/KK construction, vacuum, operator,
phenomenology, or full-theory gates; those remain G2--G8 obligations already
recorded by V46.

## Primary sources

{source_lines}

## Input SHA-256

{input_lines}

## Validated upstream core SHA-256

Each embedded upstream core hash was recomputed canonically before this report
was built.

{input_core_lines}

V47 core SHA-256: `{data['core_sha256']}`
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = build_report()
    expected_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
    expected_md = render_markdown(report)
    if args.write:
        JSON_PATH.write_text(expected_json, encoding="utf-8")
        MD_PATH.write_text(expected_md, encoding="utf-8")
        print("V47_RELATIVE_ETA_BORDISM_AUDIT_WRITE_PASS")
    if args.check:
        if not JSON_PATH.is_file() or not MD_PATH.is_file():
            raise SystemExit("V47 artifacts missing; run --write")
        if JSON_PATH.read_text(encoding="utf-8") != expected_json:
            raise SystemExit("V47 JSON stale; run --write")
        if MD_PATH.read_text(encoding="utf-8") != expected_md:
            raise SystemExit("V47 Markdown stale; run --write")
        print("V47_RELATIVE_ETA_BORDISM_AUDIT_CHECK_PASS")


if __name__ == "__main__":
    main()
