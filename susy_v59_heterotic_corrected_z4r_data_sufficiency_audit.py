#!/usr/bin/env python3
"""V59 source-locked audit of the corrected heterotic mixed-Z4R calculation.

This certificate asks a narrower question than V58: do the published state
tables for the Kappl et al. freely acting E8 x E8 Z2 x Z2 model contain the
microscopic data required by the corrected heterotic R-charge formula of Cabo
Bizet et al.?  Exact rational arithmetic recovers every anomaly statement that
is actually fixed by the published low-energy charge pattern and proves a
sharp information-loss obstruction for the missing corrected calculation.

The result is fail closed.  Table E.2 is a complete representation/Abelian
charge census, but it is not a complete vertex-operator census: it omits the
per-state shifted momenta, oscillators, physical twist-field eigenvectors and
gamma phases that enter the corrected charge.  Thus the corrected full-state
mixed-Z4R and Green--Schwarz rows are not identifiable from the published
table without a new worldsheet/Orbifolder calculation.  This is a data-
sufficiency no-go, not a physical no-go for the string vacuum or its Z4R.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "susy_v59_heterotic_corrected_z4r_data_sufficiency_audit.json"
MD_PATH = ROOT / "susy_v59_heterotic_corrected_z4r_data_sufficiency_audit.md"
TEST_PATH = ROOT / "test_susy_v59_heterotic_corrected_z4r_data_sufficiency_audit.py"
V58_PATH = ROOT / "SUSY_V58_HETEROTIC_G1_MICROSCOPIC_COMPLETION_AUDIT.json"
EXPECTED_V58_CORE = "c31d5fe65fc5bd96279bb739f5284854a624b2ee1586004c9b84998225d382c6"

F = Fraction

SOURCES = {
    "model": {
        "title": "String-derived MSSM vacua with residual R symmetries",
        "authors": (
            "R. Kappl, B. Petersen, S. Raby, M. Ratz, R. Schieren, "
            "P. K. S. Vaudrevange"
        ),
        "arxiv": "1012.4574",
        "url": "https://arxiv.org/abs/1012.4574",
        "locations": [
            "equations (3.2), (3.11)--(3.12)",
            "Appendix A",
            "Appendix E, equations (E.1)--(E.6), Tables E.1--E.2",
        ],
    },
    "corrected_charges": {
        "title": "Discrete R-symmetries and Anomaly Universality in Heterotic Orbifolds",
        "authors": (
            "N. G. Cabo Bizet, T. Kobayashi, D. K. Mayorga Pena, "
            "S. L. Parameswaran, M. Schmitz, I. Zavala"
        ),
        "arxiv": "1308.5669",
        "url": "https://arxiv.org/abs/1308.5669",
        "locations": [
            "vertex operator (2.7)",
            "gamma phase (2.16)",
            "corrected R charge (3.24)",
            "anomaly equations (4.3)--(4.6)",
        ],
    },
    "geometry_warning": {
        "title": "R-Symmetries from the Orbifolded Heterotic String",
        "author": "Matthias Schmitz",
        "report": "BONN-IR-2014-12",
        "url": "https://d-nb.info/1077289065/34",
        "locations": ["pages 62--63", "pages 78--79"],
    },
    "green_schwarz": {
        "title": "Discrete R symmetries for the MSSM and its singlet extensions",
        "authors": (
            "H. M. Lee, S. Raby, M. Ratz, G. G. Ross, R. Schieren, "
            "K. Schmidt-Hoberg, P. K. S. Vaudrevange"
        ),
        "arxiv": "1102.3595",
        "url": "https://arxiv.org/abs/1102.3595",
        "locations": ["equations (A.22)--(A.23)"],
    },
}

STATUS = (
    "V59_CORRECTED_HETEROTIC_Z4R_ROUTE_A__PUBLISHED_TABLE_E2_IS_COMPLETE_"
    "MACRO_SPECTRUM_BUT_INCOMPLETE_VERTEX_OPERATOR_LEDGER__CORRECTED_GAMMA_"
    "PHASES_NOT_IDENTIFIABLE_SOURCE_ONLY__OLD_VISIBLE_ANOMALIES_REPRODUCED_"
    "EXACTLY__FULL_VISIBLE_HIDDEN_U1_GRAVITY_AND_GS_ROWS_UNDERDETERMINED__"
    "NEW_CFT_REGENERATION_REQUIRED__STRICT_G1_OPEN__NO_GATE_PROMOTION"
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def load_v58() -> dict[str, Any]:
    if not V58_PATH.is_file():
        raise RuntimeError(f"missing V58 frontier: {V58_PATH.name}")
    value = json.loads(V58_PATH.read_text(encoding="utf-8"))
    actual = canonical_sha(value)
    if value.get("core_sha256") != actual:
        raise RuntimeError("V58 canonical core is stale")
    if actual != EXPECTED_V58_CORE:
        raise RuntimeError("unexpected V58 canonical core")
    return value


def fstr(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def frac_mod(value: Fraction, modulus: int | Fraction) -> Fraction:
    modulus = F(modulus)
    if modulus <= 0:
        raise ValueError("modulus must be positive")
    return value - modulus * (value // modulus)


def corrected_geometric_r_charge(
    *,
    M: int,
    xi: Sequence[Fraction],
    q_sh_minus_oscillators: Sequence[Fraction],
    gamma: Fraction,
) -> Fraction:
    """Equation (3.24) of arXiv:1308.5669, reduced modulo M."""
    if len(xi) != 3 or len(q_sh_minus_oscillators) != 3:
        raise ValueError("the internal charge vectors must have three components")
    raw = sum(
        (F(M) * rotation * state_charge)
        for rotation, state_charge in zip(xi, q_sh_minus_oscillators)
    ) - F(M) * gamma
    return frac_mod(raw, M)


def corrected_mixed_z4r_charge(
    *,
    q_x: Fraction,
    n3: int,
    q_sh_minus_oscillators: Sequence[Fraction],
    gamma: Fraction,
) -> Fraction:
    """Corrected candidate qX + R2 + 2 n3 for the second Z2 plane."""
    r2 = corrected_geometric_r_charge(
        M=4,
        xi=(F(0), F(1, 2), F(0)),
        q_sh_minus_oscillators=q_sh_minus_oscillators,
        gamma=gamma,
    )
    return frac_mod(F(q_x) + r2 + 2 * n3, 4)


def gamma_from_microstate(
    *, p_sh_dot_V_h: Fraction, v_h_dot_q_sh_minus_osc: Fraction, vacuum_phase: Fraction
) -> Fraction:
    """Equation (2.16) of arXiv:1308.5669, reduced modulo one."""
    return frac_mod(
        -F(p_sh_dot_V_h) + F(v_h_dot_q_sh_minus_osc) - F(vacuum_phase),
        1,
    )


def nonabelian_r_anomaly(
    *, c2_adjoint: Fraction, superpotential_charge: int, rows: Sequence[Mapping[str, Any]]
) -> Fraction:
    """Equation (4.3), with rows containing r and Dynkin index T."""
    theta_charge = F(superpotential_charge, 2)
    return F(c2_adjoint) * theta_charge + sum(
        (F(row["r"]) - theta_charge) * F(row["T"]) for row in rows
    )


MSSM_FIELDS = [
    {"name": "Q", "families": 3, "d3": 3, "d2": 2, "Y": F(1, 6), "r": 1},
    {"name": "Ubar", "families": 3, "d3": 3, "d2": 1, "Y": F(-2, 3), "r": 1},
    {"name": "Dbar", "families": 3, "d3": 3, "d2": 1, "Y": F(1, 3), "r": 1},
    {"name": "L", "families": 3, "d3": 1, "d2": 2, "Y": F(-1, 2), "r": 1},
    {"name": "Ebar", "families": 3, "d3": 1, "d2": 1, "Y": F(1), "r": 1},
    {"name": "Hu", "families": 1, "d3": 1, "d2": 2, "Y": F(1, 2), "r": 0},
    {"name": "Hd", "families": 1, "d3": 1, "d2": 2, "Y": F(-1, 2), "r": 0},
]


def published_old_ledger_derivations() -> dict[str, Any]:
    # In signed representatives the two Higgsino doublets have charge -1.
    a3 = nonabelian_r_anomaly(c2_adjoint=F(3), superpotential_charge=2, rows=[])
    a2_signed = nonabelian_r_anomaly(
        c2_adjoint=F(2),
        superpotential_charge=2,
        rows=[{"r": 0, "T": F(1, 2)}, {"r": 0, "T": F(1, 2)}],
    )
    # Kappl et al. use the non-negative fermion representative -1 == 3 mod 4.
    a2_paper_rep = F(2) + 2 * F(3) * F(1, 2)
    a1_gut = sum(
        F(row["families"])
        * F(row["d3"])
        * F(row["d2"])
        * (F(row["r"]) - 1)
        * F(3, 5)
        * F(row["Y"]) ** 2
        for row in MSSM_FIELDS
    )
    gauge_adjoint_dimension = 8 + 3 + 1
    grav_constant = -21 - 1 - 3 - 3 + gauge_adjoint_dimension
    grav_chiral = sum(
        row["families"] * row["d3"] * row["d2"] * (row["r"] - 1)
        for row in MSSM_FIELDS
    )
    a_grav_truncated = F(grav_constant + grav_chiral)
    eta = 2
    return {
        "scope": (
            "2010 MSSM charge pattern only; not the corrected full Table E.2 spectrum"
        ),
        "superpotential_charge_R": 2,
        "theta_charge": 1,
        "eta_for_Z4R": eta,
        "A_SU3_signed": fstr(a3),
        "A_SU2_signed": fstr(a2_signed),
        "A_SU2_paper_nonnegative_representative": fstr(a2_paper_rep),
        "nonabelian_residues_mod_eta": [
            fstr(frac_mod(a3, eta)),
            fstr(frac_mod(a2_signed, eta)),
        ],
        "visible_nonabelian_universal_mod_eta": frac_mod(a3, eta)
        == frac_mod(a2_signed, eta),
        "formal_A_U1Y2_GUT_normalized": fstr(a1_gut),
        "A_gravity_truncated_visible_plus_S_TU": fstr(a_grav_truncated),
        "gravity_scope_warning": (
            "Includes the gravitino, dilatino, three T modulini, three U modulini, "
            "GSM gauginos and MSSM chirals only. Hidden and residual light singlet "
            "states are absent, so this is not the model anomaly."
        ),
        "published_anomaly_mixing": {
            "A_U1_anom": 15,
            "B_Z2_n3": "1/2",
            "B_plus_nA_residue_mod_1": "1/2 for every integer n",
            "can_rotate_Z2_n3_entirely_into_U1_anom": False,
        },
    }


def published_state_data_matrix() -> list[dict[str, Any]]:
    return [
        {
            "datum": "twists_shifts_Wilson_lines_and_free_shift",
            "required_for": "regenerate the CFT spectrum",
            "publication_status": "PRESENT",
            "location": "1012.4574, equations (E.1)--(E.4)",
            "sufficient": True,
        },
        {
            "datum": "four_dimensional_nonAbelian_representations",
            "required_for": "Dynkin indices and representation dimensions",
            "publication_status": "PRESENT",
            "location": "1012.4574, Tables E.1--E.2",
            "sufficient": True,
        },
        {
            "datum": "qY_qX_q1_through_q6_and_old_qZ4R",
            "required_for": "old Abelian and residual-charge ledger",
            "publication_status": "PRESENT",
            "location": "1012.4574, Table E.2",
            "sufficient": True,
        },
        {
            "datum": "constructing_element_g_for_each_physical_state",
            "required_for": "conjugacy class and free-quotient orbit",
            "publication_status": "PARTIAL_SECTOR_PATTERNS_ONLY",
            "location": "Table E.2 sector column uses stars and paired labels",
            "sufficient": False,
        },
        {
            "datum": "shifted_gauge_momentum_p_sh_for_each_state",
            "required_for": "gamma_h through equation (2.16)",
            "publication_status": "ABSENT",
            "location": "not a Table E.2 column",
            "sufficient": False,
        },
        {
            "datum": "shifted_right_moving_H_momentum_q_sh_for_each_state",
            "required_for": "corrected charge (3.24) and gamma_h",
            "publication_status": "ABSENT_PER_STATE",
            "location": "only sector-level old plane charges are stated",
            "sufficient": False,
        },
        {
            "datum": "left_oscillators_NL_and_NbarL_in_each_plane",
            "required_for": "corrected charge (3.24) and gamma_h",
            "publication_status": "ABSENT",
            "location": "not a Table E.2 column",
            "sufficient": False,
        },
        {
            "datum": "physical_twist_field_eigenvector_and_gamma_h",
            "required_for": "the -M gamma_h term in corrected charge (3.24)",
            "publication_status": "ABSENT",
            "location": "not published for the Table E.2 states",
            "sufficient": False,
        },
        {
            "datum": "isometry_rho_and_statewise_h_g_for_the_free_quotient",
            "required_for": "rho(g)=h_g g h_g^-1 and gamma evaluation",
            "publication_status": "ABSENT_FOR_EXACT_MODEL",
            "location": "the later paper does not apply its construction to this model",
            "sufficient": False,
        },
        {
            "datum": "complete_post_VEV_massless_eigenbasis",
            "required_for": "infrared hidden and gravitational anomaly sums",
            "publication_status": "ABSENT_AT_COEFFICIENT_LEVEL",
            "location": "generic mass-matrix ranks are published, not every eigenstate",
            "sufficient": False,
        },
        {
            "datum": "all_U1_generator_vectors_and_Kac_Moody_metric",
            "required_for": "normalized U1 anomaly rows and universality",
            "publication_status": "PARTIAL",
            "location": "hypercharge normalization and t_X are given; the full basis metric is not",
            "sufficient": False,
        },
        {
            "datum": "local_anomaly_distribution_thresholds_and_axion_coupling_matrix",
            "required_for": "model-specific localized/threshold Green--Schwarz proof",
            "publication_status": "ABSENT",
            "location": "not evaluated in the cited model paper",
            "sufficient": False,
        },
    ]


def ambiguity_witness() -> dict[str, Any]:
    common = {
        "q_x": F(0),
        "n3": 0,
        "q_sh_minus_oscillators": (F(0), F(0), F(0)),
        "representation": "SU(2) fundamental",
        "Dynkin_index": F(1, 2),
    }
    charge_gamma_0 = corrected_mixed_z4r_charge(
        q_x=common["q_x"],
        n3=common["n3"],
        q_sh_minus_oscillators=common["q_sh_minus_oscillators"],
        gamma=F(0),
    )
    charge_gamma_half = corrected_mixed_z4r_charge(
        q_x=common["q_x"],
        n3=common["n3"],
        q_sh_minus_oscillators=common["q_sh_minus_oscillators"],
        gamma=F(1, 2),
    )
    anomaly_shift = (charge_gamma_half - charge_gamma_0) * common["Dynkin_index"]
    return {
        "purpose": (
            "information-loss witness only; it does not assert that both gamma assignments "
            "solve the exact model's GSO projections"
        ),
        "same_published_macro_columns": ["q_X", "n3", "sector", "representation"],
        "gamma_not_in_published_columns": True,
        "completion_A_gamma": "0",
        "completion_B_gamma": "1/2",
        "corrected_charge_A_mod_4": fstr(charge_gamma_0),
        "corrected_charge_B_mod_4": fstr(charge_gamma_half),
        "charge_difference": fstr(charge_gamma_half - charge_gamma_0),
        "SU2_mixed_anomaly_difference": fstr(anomaly_shift),
        "SU2_discrete_modulus": "2",
        "anomaly_residue_can_change": frac_mod(anomaly_shift, 2) != 0,
    }


def data_sufficiency_theorem(matrix: Sequence[Mapping[str, Any]], witness: Mapping[str, Any]) -> dict[str, Any]:
    missing = [row["datum"] for row in matrix if not row["sufficient"]]
    return {
        "name": "corrected_charge_projection_nonidentifiability",
        "premise": (
            "The published macrostate projection retains representations, Abelian charges "
            "and old R charges but discards gamma_h and the microdata needed to derive it."
        ),
        "equation": (
            "r_alpha = sum_i M xi_i (q_sh^i-N_L^i+Nbar_L^i) - M gamma_hg mod M"
        ),
        "proof": (
            "Holding every published macro column fixed while changing an omitted gamma_h "
            "by 1/2 changes a Z4 charge by 2. For an SU(2) fundamental this shifts the "
            "mixed anomaly by one, nonzero modulo two. Therefore neither corrected charges "
            "nor their anomaly residues factor through the published Table E.2 projection."
        ),
        "witness_verified": bool(witness["anomaly_residue_can_change"]),
        "missing_required_data": missing,
        "published_table_alone_determines_corrected_charges": False,
        "published_table_alone_determines_full_anomaly_rows": False,
        "scope_boundary": (
            "This proves non-identifiability from the published state ledger. The complete "
            "worldsheet action may determine the missing data in principle after a new CFT "
            "spectrum/eigenphase calculation."
        ),
        "physical_no_go_for_Z4R": False,
    }


def anomaly_completion_matrix() -> list[dict[str, Any]]:
    return [
        {
            "row": "SU3C^2-Z4R",
            "old_result": "A3=3 == 1 mod 2",
            "corrected_full_state_status": "NOT_IDENTIFIABLE",
            "blocker": "corrected charges of all surviving colored states",
        },
        {
            "row": "SU2L^2-Z4R",
            "old_result": "A2=1 signed (5 in the paper representative) == 1 mod 2",
            "corrected_full_state_status": "NOT_IDENTIFIABLE",
            "blocker": "corrected charges of all surviving doublets",
        },
        {
            "row": "U1Y^2-Z4R",
            "old_result": "formal light-MSSM coefficient -3/5",
            "corrected_full_state_status": "NOT_IDENTIFIABLE",
            "blocker": "corrected charges, massive-state ambiguity and normalized U1 ledger",
        },
        {
            "row": "SU2_hidden^2-Z4R",
            "old_result": None,
            "corrected_full_state_status": "NOT_IDENTIFIABLE",
            "blocker": "post-VEV hidden eigenbasis and corrected charges",
        },
        {
            "row": "other_or_broken_U1_rows",
            "old_result": "A_U1anom=15 and B_n3=1/2 only",
            "corrected_full_state_status": "NOT_IDENTIFIABLE",
            "blocker": "full U1 generator metric and corrected state ledger",
        },
        {
            "row": "gravity^2-Z4R",
            "old_result": "truncated visible+S+TU numerator -20 only",
            "corrected_full_state_status": "NOT_IDENTIFIABLE",
            "blocker": "all corrected light charges and complete post-VEV massless spectrum",
        },
        {
            "row": "fixed_locus_and_global_partition_function_phase",
            "old_result": None,
            "corrected_full_state_status": "NOT_PUBLISHED",
            "blocker": "free-quotient eigenphases, local distribution, inflow and thresholds",
        },
        {
            "row": "universal_Green_Schwarz_trivialization",
            "old_result": "dilaton shifts under U1anom and the independent n3 Z2",
            "corrected_full_state_status": "UNDERDETERMINED",
            "blocker": "universal corrected residue and quantized axion/threshold coupling",
        },
    ]


def green_schwarz_data() -> dict[str, Any]:
    return {
        "general_condition": (
            "S -> S + i Delta_GS/2; pi M Delta_GS == A_grav/24 == A_G mod eta"
        ),
        "source": "1102.3595, equations (A.22)--(A.23)",
        "M": 4,
        "eta": 2,
        "same_action_axion_present": True,
        "corrected_A_G_rows_known": False,
        "corrected_A_grav_known": False,
        "threshold_or_local_counterterm_matrix_known": False,
        "Delta_GS_model_specific_value_determined": False,
        "GS_cancellation_certified": False,
    }


def minimum_completion_payload() -> list[str]:
    return [
        "For every physical state: constructing element representative and full free-quotient orbit.",
        "For every physical state: p or p_sh, q_sh, and all N_L^i and Nbar_L^i.",
        "Physical twist-field eigenvectors and gamma_h for all relevant centralizer elements.",
        "The exact second-plane isometry rho and a statewise h_g solving rho(g)=h_g g h_g^-1.",
        "A corrected charge attached one-to-one to every Table E.2 state/component.",
        "The coefficient-level post-VEV massless eigenbasis, including hidden and singlet states.",
        "Normalized U(1) generator vectors/Kac--Moody metric and all mixed anomaly rows.",
        "The axion periodicity, threshold corrections, local anomaly distribution and inflow map.",
    ]


def gate_ledger() -> list[dict[str, Any]]:
    return [
        {
            "gate": f"G{i}",
            "status": "OPEN",
            "V59_promoted": False,
            "reason": (
                "V59 is a source-data sufficiency certificate; it does not supply the "
                "missing corrected CFT state/eigenphase and GS calculation."
            ),
        }
        for i in range(1, 9)
    ]


def source_manifest() -> list[dict[str, Any]]:
    return [
        {"path": path.name, "exists": path.is_file(), "sha256": sha256_file(path)}
        for path in (Path(__file__), TEST_PATH, V58_PATH)
    ]


def build_report() -> dict[str, Any]:
    v58 = load_v58()
    old = published_old_ledger_derivations()
    matrix = published_state_data_matrix()
    witness = ambiguity_witness()
    theorem = data_sufficiency_theorem(matrix, witness)
    anomaly_rows = anomaly_completion_matrix()
    gs = green_schwarz_data()
    gates = gate_ledger()
    integrity = {
        "V58_core_is_canonical_and_expected": canonical_sha(v58) == EXPECTED_V58_CORE,
        "corrected_formula_has_exact_gamma_dependence": witness["corrected_charge_A_mod_4"]
        != witness["corrected_charge_B_mod_4"],
        "omitted_gamma_can_change_anomaly_residue": witness["anomaly_residue_can_change"],
        "published_state_ledger_is_not_microstate_complete": any(
            not row["sufficient"] for row in matrix
        ),
        "nonidentifiability_theorem_is_fail_closed": not theorem[
            "published_table_alone_determines_full_anomaly_rows"
        ],
        "old_visible_nonabelian_arithmetic_reproduced": old[
            "visible_nonabelian_universal_mod_eta"
        ]
        and old["A_SU3_signed"] == "3"
        and old["A_SU2_paper_nonnegative_representative"] == "5",
        "all_corrected_completion_rows_remain_open": all(
            row["corrected_full_state_status"]
            in {"NOT_IDENTIFIABLE", "NOT_PUBLISHED", "UNDERDETERMINED"}
            for row in anomaly_rows
        ),
        "GS_is_not_overclaimed": not gs["GS_cancellation_certified"],
        "zero_gates_promoted": not any(row["V59_promoted"] for row in gates),
        "physical_no_go_not_overclaimed": not theorem["physical_no_go_for_Z4R"],
        "complete_theory_not_claimed": True,
    }
    report: dict[str, Any] = {
        "schema": "susy_v59_heterotic_corrected_z4r_data_sufficiency_audit/v1",
        "status": STATUS,
        "lineage": {
            "bound_frontier": V58_PATH.name,
            "bound_frontier_core": EXPECTED_V58_CORE,
            "V58_result": "microscopic near-match; corrected mixed-Z4R/GS ledger open",
            "V59_relation": (
                "distinct route-A source-sufficiency calculation; V58 files are not modified"
            ),
        },
        "primary_sources": SOURCES,
        "corrected_charge_equations": {
            "vertex_microdata": (
                "V_-a contains p_sh, q_sh, N_L, Nbar_L and the physical twist field sigma"
            ),
            "gamma": (
                "gamma_h = -p_sh.V_h + v_h.(q_sh-N_L+Nbar_L) - Phi(g,h) mod 1"
            ),
            "charge": (
                "r_alpha = sum_i M xi_i(q_sh^i-N_L^i+Nbar_L^i) - M gamma_hg mod M"
            ),
            "mixed_candidate": (
                "q_corrected = q_X + r_2(corrected) + 2 n3 mod 4"
            ),
            "anomaly_nonAbelian": (
                "A_G = C2(G) R/2 + sum_alpha (r_alpha-R/2) T(R_alpha)"
            ),
            "anomaly_gravity": (
                "A_grav = (-21-1-N_T-N_U+sum dim adj G)R/2 "
                "+ sum_alpha(r_alpha-R/2)dim(R_alpha)"
            ),
        },
        "published_state_data_matrix": matrix,
        "exact_ambiguity_witness": witness,
        "data_sufficiency_theorem": theorem,
        "exact_published_scope_derivations": old,
        "corrected_anomaly_completion_matrix": anomaly_rows,
        "green_schwarz_completion": gs,
        "geometry_specific_warning": {
            "geometry": "Z2 x Z2-5-1 with tau=(e2+e4+e6)/2",
            "scan_size_per_affine_class": 10000,
            "published_result": (
                "plane-R anomalies are non-universal in this exceptional freely quotiented class"
            ),
            "repair_of_mixed_Z4R": "explicitly open",
            "model_specific_no_go": False,
        },
        "minimum_new_calculation_payload": minimum_completion_payload(),
        "terminal_decision": {
            "published_state_data_sufficient_for_corrected_charge_reconstruction": False,
            "published_state_data_sufficient_for_every_anomaly_row": False,
            "corrected_full_state_mixed_Z4R_computed": False,
            "model_specific_GS_cancellation_closed": False,
            "sharp_result": (
                "source-locked non-identifiability: gamma-sensitive corrected charges and "
                "anomalies do not factor through the published Table E.2 columns"
            ),
            "requires_new_worldsheet_or_Orbifolder_calculation": True,
            "physical_Z4R_ruled_out": False,
            "V59_G1_closed": False,
            "closed_gates": [],
            "complete_theory": False,
        },
        "claim_boundary": {
            "new_certificate_not_new_action": True,
            "no_V58_file_modified": True,
            "old_charge_ledger_not_relabeled_as_corrected": True,
            "missing_gamma_not_guessed": True,
            "absence_of_published_data_not_called_physical_inconsistency": True,
            "G1_to_G8_not_promoted": True,
        },
        "gate_ledger": gates,
        "integrity_checks": integrity,
        "n_integrity_checks": len(integrity),
        "n_failed_integrity_checks": sum(not value for value in integrity.values()),
        "source_manifest": source_manifest(),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("V59 canonical core mismatch")
    if report.get("n_failed_integrity_checks") != 0:
        failed = [name for name, passed in report["integrity_checks"].items() if not passed]
        raise RuntimeError(f"V59 integrity failure: {failed}")
    decision = report["terminal_decision"]
    if decision["corrected_full_state_mixed_Z4R_computed"]:
        raise RuntimeError("V59 overclaimed the missing corrected state calculation")
    if decision["model_specific_GS_cancellation_closed"]:
        raise RuntimeError("V59 overclaimed Green--Schwarz closure")
    if decision["physical_Z4R_ruled_out"]:
        raise RuntimeError("V59 promoted a data obstruction to a physical no-go")
    if decision["V59_G1_closed"] or decision["complete_theory"]:
        raise RuntimeError("V59 overclaimed gate or theory closure")


def render_markdown(report: Mapping[str, Any]) -> str:
    old = report["exact_published_scope_derivations"]
    theorem = report["data_sufficiency_theorem"]
    witness = report["exact_ambiguity_witness"]
    lines = [
        "# SUSY V59 heterotic corrected-Z4R data-sufficiency audit",
        "",
        f"**Status:** `{report['status']}`",
        "",
        "## Result",
        "",
        "The published model data do **not** determine the corrected full-state mixed `Z4R` or its complete Green--Schwarz ledger without a new worldsheet/Orbifolder calculation. This is a source-data non-identifiability result, not evidence that the symmetry is physically impossible.",
        "",
        "The model source is [Kappl et al., arXiv:1012.4574](https://arxiv.org/abs/1012.4574). The corrected formula is from [Cabo Bizet et al., arXiv:1308.5669](https://arxiv.org/abs/1308.5669). The geometry-specific warning is in [Schmitz, BONN-IR-2014-12](https://d-nb.info/1077289065/34), and the general discrete GS equations are in [Lee et al., arXiv:1102.3595](https://arxiv.org/abs/1102.3595).",
        "",
        "## Exact corrected equations",
        "",
        "For an orbifold isometry with order `M`,",
        "",
        "```text",
        "gamma_h = -p_sh.V_h + v_h.(q_sh-N_L+Nbar_L) - Phi(g,h)  mod 1",
        "r_alpha = sum_i M xi_i(q_sh^i-N_L^i+Nbar_L^i) - M gamma_hg  mod M",
        "q_corrected = q_X + r_2(corrected) + 2 n3  mod 4.",
        "```",
        "",
        "Table E.2 publishes representations, `qY`, `qX`, six additional Abelian charges and the old `qZ4R`. It does not publish the per-state `p_sh`, `q_sh`, oscillator numbers, physical twist-field eigenvectors, `gamma_h`, or the statewise `h_g` map for the free quotient.",
        "",
        "## Sharp non-identifiability certificate",
        "",
        theorem["proof"],
        "",
        f"The exact witness holds all macro columns fixed but uses `gamma=0` and `gamma=1/2`. The corrected charges are `{witness['corrected_charge_A_mod_4']}` and `{witness['corrected_charge_B_mod_4']}`. For an SU(2) fundamental the mixed anomaly changes by `{witness['SU2_mixed_anomaly_difference']}`, nonzero modulo `{witness['SU2_discrete_modulus']}`.",
        "",
        "This witness proves that corrected anomaly residues cannot be functions of the published macro columns alone. It does not assert that both illustrative gamma completions satisfy the exact model's GSO conditions.",
        "",
        "## Exact scope that can be recovered",
        "",
        f"For the old MSSM pattern, signed representatives give `A3={old['A_SU3_signed']}` and `A2={old['A_SU2_signed']}`; Kappl et al.'s non-negative representative gives `A2={old['A_SU2_paper_nonnegative_representative']}`. Both non-Abelian residues are `{old['nonabelian_residues_mod_eta'][0]}` modulo two. The formal GUT-normalized light-MSSM hypercharge coefficient is `{old['formal_A_U1Y2_GUT_normalized']}`.",
        "",
        f"The gravity numerator `{old['A_gravity_truncated_visible_plus_S_TU']}` is only the visible MSSM plus the gravitino, dilatino, three T and three U modulini. It is not the complete model coefficient.",
        "",
        "The published anomaly-mixing result is also exact: `A_U1anom=15`, `B_n3=1/2`, so `B+nA` always has residue `1/2 mod 1` and the space-group anomaly cannot be rotated entirely into `U(1)anom`.",
        "",
        "## Corrected completion rows",
        "",
        "| Row | Published/old result | Corrected status |",
        "|---|---|---|",
    ]
    for row in report["corrected_anomaly_completion_matrix"]:
        lines.append(
            f"| `{row['row']}` | {row['old_result'] or 'none'} | **{row['corrected_full_state_status']}**: {row['blocker']} |"
        )
    lines.extend(
        [
            "",
            "## Minimum new calculation",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["minimum_new_calculation_payload"])
    lines.extend(
        [
            "",
            "## Gate decision",
            "",
            "Strict G1 remains **OPEN**. No G1--G8 gate is promoted. A complete corrected state dump and free-quotient eigenphase calculation must precede any model-specific universality or Green--Schwarz claim.",
            "",
            f"Canonical core SHA-256: `{report['core_sha256']}`",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate without writing outputs")
    args = parser.parse_args()
    report = build_report()
    validate(report)
    if not args.check:
        write_outputs(report)
    print(report["status"])
    print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
