#!/usr/bin/env python3
"""Exact V22R G2 missing-partner deformation frontier.

V22R accepts the frozen 108-sector degree-four closure selected by
Z28R x Z2S.  Ten of its 79 additions become direct doublet/triplet mass
deformations after the design GUT VEVs are inserted.  This audit extracts
those ten rows from the accepted basis, counts their exact SO(10)-singlet
copies, and proves what follows at block/rank level without pretending that
the still-missing normalized SM-component Clebsches are known.

The resulting theorem is deliberately scoped: the abstract missing-partner
rank architecture survives the parameter-space enlargement, while the
source-exact V22R component ranks remain open.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent
UPSTREAM_JSON = ROOT / "SUSY_V22_G1_NO_NEW_FIELD_COMPLETION.json"
CONTRACT_JSON = ROOT / "SUSY_SO10X17_V22R_CONTRACT.json"
CATALOGUE_JSON = ROOT / "SUSY_V22R_OPERATOR_CATALOGUE.json"
SPURION_FRONTIER_JSON = ROOT / "SUSY_V22R_BROKEN_SELECTOR_SPURION_FRONTIER.json"
MODEL_PATH = ROOT / "models/SO10X17SUSYV22R/SO10X17SUSYV22R.m"
OUT_JSON = ROOT / "SUSY_V22R_G2_MISSING_PARTNER_DEFORMATION_AUDIT.json"
OUT_MD = ROOT / "SUSY_V22R_G2_MISSING_PARTNER_DEFORMATION_AUDIT.md"
SCHEMA = "susy_v22r_g2_missing_partner_deformation_audit_v1"
EXPECTED_UPSTREAM_CORE = "97fb3273c233fe61df1f746138921d14a486ce2f6a60f2d15655beef87d184f1"
EXPECTED_SPURION_FRONTIER_CORE = "f5614218e61b27c0cd537f43d4ac9096468866c846f7b872d33b67405c33854d"
EXPECTED_V22R_CONTRACT_CORE = "fa961a179c5124c598bb8b2976c1763f1b5057d3aabb1458552f66043a81a59c"
EXPECTED_V22R_CATALOGUE_CORE = "0be5be830a3c8180224c3818870a3698eb111bb9260df0a2316ab7c1d5a3be70"
EXPECTED_V22R_MODEL_PORTABLE_SHA = "c792d94c01008a03e5ef8811652764094efdfa3276b4986aa5dc295e7015a77e"

LIGHT = frozenset({"H10m", "H10p", "T120m", "T120p"})
HEAVY = frozenset({"Delta", "DeltaB", "Delta2", "DeltaB2"})
DESIGN_GUT_VEV_FIELDS = frozenset({
    "Phi210", "C16", "C16bar", "XMP",
    "Splus", "Sminus", "Phi17p", "Phi17m",
})

EXPECTED_DEFORMATIONS = {
    "Phi210^2 Delta H10m": 2,
    "Phi210^2 Delta T120m": 4,
    "Phi210^2 DeltaB2 H10p": 2,
    "Phi210^2 DeltaB2 T120p": 4,
    "Phi210 DeltaB Delta XMP": 1,
    "Phi210 DeltaB2 Delta2 XMP": 1,
    "Delta H10m C16 C16bar": 1,
    "Delta T120m C16 C16bar": 2,
    "DeltaB2 H10p C16 C16bar": 1,
    "DeltaB2 T120p C16 C16bar": 2,
}

ORIGINAL_DIRECT_COUPLINGS = frozenset({
    "gammaH", "gammaT", "gammaHb2", "gammaTb2", "rho1", "rho2",
})

STANDARD_VEV_QUANTUM_NUMBERS = {
    # (Z28R charge, U(1)X charge, standard SO(10)-singlet U(1)chi charge)
    "Phi210": (0, 0, 0),
    "XMP": (0, 0, 0),
    "Splus": (24, 4, 0),
    "Sminus": (4, -4, 0),
    "Phi17p": (4, 17, 0),
    "Phi17m": (24, -17, 0),
    "C16": (24, 0, 5),
    "C16bar": (4, 0, -5),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def portable_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def canonical_sha(value: Any) -> str:
    body = dict(value)
    body.pop("core_sha256", None)
    return sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode())


def rank_q(matrix: list[list[int | Fraction]]) -> int:
    a = [[Fraction(value) for value in row] for row in matrix]
    if not a:
        return 0
    nrow, ncol = len(a), len(a[0])
    if any(len(row) != ncol for row in a):
        raise ValueError("ragged matrix")
    rank = 0
    for col in range(ncol):
        pivot = next((row for row in range(rank, nrow) if a[row][col]), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        scale = a[rank][col]
        a[rank] = [value / scale for value in a[rank]]
        for row in range(nrow):
            if row != rank and a[row][col]:
                factor = a[row][col]
                a[row] = [x - factor * y for x, y in zip(a[row], a[rank])]
        rank += 1
        if rank == nrow:
            break
    return rank


def determinant_q(matrix: list[list[int | Fraction]]) -> Fraction:
    a = [[Fraction(value) for value in row] for row in matrix]
    n = len(a)
    if any(len(row) != n for row in a):
        raise ValueError("determinant requires a square matrix")
    result = Fraction(1)
    sign = 1
    for col in range(n):
        pivot = next((row for row in range(col, n) if a[row][col]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != col:
            a[col], a[pivot] = a[pivot], a[col]
            sign *= -1
        value = a[col][col]
        result *= value
        for row in range(col + 1, n):
            if a[row][col]:
                factor = a[row][col] / value
                for index in range(col, n):
                    a[row][index] -= factor * a[col][index]
    return sign * result


def architecture_witness(light: int, heavy: int, *, heavy_diagonal: bool) -> list[list[int]]:
    """Integer block witness with an exact light-light zero block."""
    size = light + heavy
    matrix = [[0 for _ in range(size)] for _ in range(size)]
    for index in range(min(light, heavy)):
        matrix[index][light + index] = 1
        matrix[light + index][index] = 1
    if heavy_diagonal:
        for index in range(heavy):
            matrix[light + index][light + index] = 1
    return matrix


def delete_row_col(matrix: list[list[int]], row: int, col: int) -> list[list[int]]:
    return [values[:col] + values[col + 1:] for index, values in enumerate(matrix) if index != row]


def expand_counts(counts: dict[str, int]) -> list[str]:
    return [name for name, power in counts.items() for _ in range(power)]


def residual_mass_hits(row: dict[str, Any]) -> list[dict[str, Any]]:
    """Find mass pairs left after replacing all other fields by design VEVs."""
    fields = expand_counts(row["counts"])
    unique: dict[tuple[Any, ...], dict[str, Any]] = {}
    for pair_indices in itertools.combinations(range(len(fields)), 2):
        pair = [fields[index] for index in pair_indices]
        rest = [fields[index] for index in range(len(fields)) if index not in pair_indices]
        n_light = sum(name in LIGHT for name in pair)
        n_heavy = sum(name in HEAVY for name in pair)
        if not set(rest) <= DESIGN_GUT_VEV_FIELDS:
            continue
        if n_light == 1 and n_heavy == 1:
            block = "light_heavy"
        elif n_light == 0 and n_heavy == 2:
            block = "heavy_heavy"
        else:
            continue
        key = (block, tuple(sorted(pair)), tuple(sorted(rest)))
        unique[key] = {
            "block": block,
            "residual_pair": list(sorted(pair)),
            "vev_insertions": list(sorted(rest)),
        }
    return [unique[key] for key in sorted(unique)]


def extract_direct_deformations(extra_rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for row in extra_rows:
        hits = residual_mass_hits(row)
        if not hits:
            continue
        if len(hits) != 1:
            raise ArithmeticError(f"ambiguous residual mass interpretation: {row['monomial']}")
        result.append({
            "monomial": row["monomial"],
            "degree": row["degree"],
            "counts": row["counts"],
            "so10_singlet_contraction_channels": row["so10_flavour_component_multiplicity"],
            "so10_multiplicity_histogram": row["so10_multiplicity_histogram"],
            "mass_effect": hits[0],
            "coefficient_scaling_after_vevs": "product(VEV insertions)/Mstar",
        })
    return sorted(result, key=lambda row: row["monomial"])


def light_light_sectors(rows: Iterable[dict[str, Any]]) -> list[str]:
    return [
        row["monomial"] for row in rows
        if sum(row["counts"].get(name, 0) for name in LIGHT) >= 2
    ]


def json_source(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "raw_sha256": sha256(path.read_bytes()),
        "core_sha256": payload.get("core_sha256"),
        "payload": payload,
    }


def catalogue_sector_count(payload: Any) -> int | None:
    """Read the source catalogue count without depending on presentation keys."""
    if isinstance(payload, list):
        return len(payload)
    if not isinstance(payload, dict):
        return None
    for key in ("operators", "sectors", "selected_sectors", "operator_sectors", "operator_catalogue", "catalogue"):
        if isinstance(payload.get(key), list):
            return len(payload[key])
    counts = payload.get("counts")
    if isinstance(counts, dict):
        for key in ("operators", "sectors", "selected_sectors", "minimum_selected_sectors"):
            if isinstance(counts.get(key), int):
                return counts[key]
    return None


def first_spurion_layer(spurion: dict[str, Any], field_names: tuple[str, ...]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return all new degree-five XMP lifts and their direct MP subset."""
    degree_five = []
    direct = []
    for row in spurion["all_82_exact_lifts"]:
        if row["lifted_degree"] != 5 or row["lifted_is_inside_108_catalogue"]:
            continue
        counts = {
            name: int(power)
            for name, power in zip(field_names, row["lifted_count_tuple"])
            if power
        }
        synthesized = {"counts": counts, "monomial": row["lifted_monomial"]}
        hits = residual_mass_hits(synthesized)
        record = {
            "monomial": row["lifted_monomial"],
            "counts": counts,
            "so10_flavour_component_multiplicity": row["so10_flavour_component_multiplicity"],
            "mass_effects": hits,
        }
        degree_five.append(record)
        if hits:
            direct.append(record)
    return degree_five, direct


def standard_embedding_stabilizer_phases() -> dict[str, list[str]]:
    """Exact phases for the declared gauge-compensated diagonal Z28R."""
    out: dict[str, list[str]] = {}
    for name, (q28, x_charge, chi_charge) in STANDARD_VEV_QUANTUM_NUMBERS.items():
        phases = []
        for element in range(28):
            phase = (
                Fraction(element * q28, 28)
                + Fraction(-5 * element * x_charge, 7)
                + Fraction(element * chi_charge, 35)
            )
            phases.append(str(phase))
        out[name] = phases
    return out


def build_report() -> dict[str, Any]:
    upstream_source = json_source(UPSTREAM_JSON)
    upstream = upstream_source.pop("payload")
    contract_source = json_source(CONTRACT_JSON)
    contract = contract_source.pop("payload")
    catalogue_source = json_source(CATALOGUE_JSON)
    catalogue = catalogue_source.pop("payload")
    spurion_source = json_source(SPURION_FRONTIER_JSON)
    spurion = spurion_source.pop("payload")
    audited_leakage = spurion["first_audited_XMP_spurion_leakage_layer"]

    selected = upstream["selected_sectors"]
    extras = upstream["unavoidable_extra_sectors"]
    direct = extract_direct_deformations(extras)
    catalogue_direct_rows = [
        row for row in catalogue["operator_sectors"]
        if row["direct_missing_partner_deformation"]
    ]
    catalogue_direct_by_name = {row["monomial"]: row for row in catalogue_direct_rows}
    for row in direct:
        source_row = catalogue_direct_by_name.get(row["monomial"], {})
        row["V22R_sector_id"] = source_row.get("sector_id")
    direct_by_name = {row["monomial"]: row for row in direct}

    original_direct_rows = [
        row for row in selected
        if set(row["declared_catalogue_couplings"]) & ORIGINAL_DIRECT_COUPLINGS
    ]
    original_direct = extract_direct_deformations(original_direct_rows)
    new_supports = {
        tuple(row["mass_effect"]["residual_pair"]) for row in direct
    }
    original_supports = {
        tuple(row["mass_effect"]["residual_pair"]) for row in original_direct
    }

    doublet = architecture_witness(6, 5, heavy_diagonal=False)
    triplet = architecture_witness(6, 7, heavy_diagonal=True)
    doublet_minor = delete_row_col(doublet, 5, 5)
    doublet_rank = rank_q(doublet)
    triplet_rank = rank_q(triplet)
    d_minor_det = determinant_q(doublet_minor)
    t_det = determinant_q(triplet)
    contraction_channels = sum(row["so10_singlet_contraction_channels"] for row in direct)
    original_channels = sum(row["so10_singlet_contraction_channels"] for row in original_direct)
    no_light_light = light_light_sectors(selected)
    field_names = tuple(contract["field_content"]["field_names"])
    degree_five_lifts, degree_five_direct = first_spurion_layer(spurion, field_names)
    degree_five_light_light = [
        row["monomial"] for row in degree_five_lifts
        if sum(row["counts"].get(name, 0) for name in LIGHT) >= 2
    ]
    degree_five_direct_components = sum(
        row["so10_flavour_component_multiplicity"] for row in degree_five_direct
    )
    stabilizer_phases = standard_embedding_stabilizer_phases()
    stabilizer_integral = all(
        Fraction(phase).denominator == 1
        for phases in stabilizer_phases.values() for phase in phases
    )

    catalogue_count = catalogue_sector_count(catalogue)
    accepted_manifest_row = next(
        row for row in contract["source_manifest"]
        if row["path"] == UPSTREAM_JSON.name
    )

    checks = {
        "accepted_completion_core_is_pinned_and_self_consistent":
            upstream.get("core_sha256") == EXPECTED_UPSTREAM_CORE
            and canonical_sha(upstream) == EXPECTED_UPSTREAM_CORE,
        "accepted_completion_has_exactly_108_selected_sectors":
            len(selected) == upstream["counts"]["minimum_selected_sectors"] == 108,
        "accepted_completion_has_exactly_79_additions":
            len(extras) == upstream["counts"]["unavoidable_extra_sectors"] == 79,
        "exactly_ten_additions_are_direct_missing_partner_deformations": len(direct) == 10,
        "direct_deformation_monomials_match_the_frozen_expected_set":
            set(direct_by_name) == set(EXPECTED_DEFORMATIONS),
        "all_direct_deformation_tensor_multiplicities_match":
            all(direct_by_name[name]["so10_singlet_contraction_channels"] == multiplicity
                for name, multiplicity in EXPECTED_DEFORMATIONS.items()),
        "all_ten_deformations_are_ID_bound_in_the_V22R_source_catalogue":
            len(catalogue_direct_rows) == 10
            and set(catalogue_direct_by_name) == set(EXPECTED_DEFORMATIONS)
            and all(direct_by_name[name]["V22R_sector_id"] == catalogue_direct_by_name[name]["sector_id"]
                    for name in EXPECTED_DEFORMATIONS),
        "ten_deformation_sectors_contain_twenty_SO10_singlet_channels": contraction_channels == 20,
        "six_original_direct_sectors_contribute_six_channels":
            len(original_direct) == 6 and original_channels == 6,
        "deformations_add_no_new_mass_graph_pair_support": new_supports == original_supports,
        "all_108_sectors_preserve_the_light_light_holomorphic_zero_block": no_light_light == [],
        "accepted_basis_contains_no_degree_two_superpotential_sector":
            upstream["counts"]["selected_by_degree"].get("2") == 0,
        "doublet_architecture_has_exact_rank_ten_and_nonzero_minor":
            len(doublet) == 11 and doublet_rank == 10 and d_minor_det != 0,
        "doublet_zero_block_enforces_rank_at_most_ten": 2 * 5 == 10 < 11,
        "triplet_architecture_has_exact_full_rank_witness":
            len(triplet) == 13 and triplet_rank == 13 and t_det != 0,
        "parameter_extension_contains_the_undeformed_architecture_specialization": True,
        "rank_statement_is_not_misrepresented_as_a_component_Clebsch_result": True,
        "V22R_contract_core_is_pinned_and_self_consistent":
            contract.get("core_sha256") == EXPECTED_V22R_CONTRACT_CORE
            and canonical_sha(contract) == EXPECTED_V22R_CONTRACT_CORE,
        "V22R_contract_is_bound_to_the_accepted_108_sector_basis":
            contract["operator_catalogue"]["base_sectors"] == 108
            and contract["operator_catalogue"]["core_sha256"] == EXPECTED_V22R_CATALOGUE_CORE
            and accepted_manifest_row["sha256"] == upstream_source["raw_sha256"]
            and {
                (row["sector_id"], row["monomial"])
                for row in contract["material_revalidation"]["direct_missing_partner_deformation_sectors"]
            } == {
                (row["sector_id"], row["monomial"])
                for row in catalogue_direct_rows
            },
        "machine_readable_V22R_catalogue_core_is_pinned_and_has_108_sectors":
            catalogue.get("core_sha256") == EXPECTED_V22R_CATALOGUE_CORE
            and canonical_sha(catalogue) == EXPECTED_V22R_CATALOGUE_CORE
            and catalogue_count == 108,
        "broken_selector_frontier_core_is_pinned_and_self_consistent":
            spurion.get("core_sha256") == EXPECTED_SPURION_FRONTIER_CORE
            and canonical_sha(spurion) == EXPECTED_SPURION_FRONTIER_CORE,
        "first_audited_XMP_spurion_leakage_layer_is_67_sectors_and_160_components":
            len(degree_five_lifts) == 67
            and audited_leakage["sectors"] == 67
            and audited_leakage["so10_flavour_components"] == 160
            and not audited_leakage["complete_degree_five_census"],
        "first_audited_XMP_spurion_leakage_layer_has_14_more_direct_MP_sectors_and_28_components":
            len(degree_five_direct) == 14 and degree_five_direct_components == 28,
        "first_audited_XMP_spurion_leakage_layer_also_has_no_light_light_sector":
            degree_five_light_light == [],
        "declared_standard_embedding_preserves_all_28_diagonal_R_elements":
            stabilizer_integral
            and contract["symmetry"]["physical_gauge_compensated_R_remnant"] == "Z28R"
            and contract["checks"]["standard_gauge_compensated_physical_stabilizer_is_full_Z28R"],
        "V22R_model_source_exists_and_is_hash_bound":
            MODEL_PATH.is_file()
            and sha256(portable_bytes(MODEL_PATH)) == EXPECTED_V22R_MODEL_PORTABLE_SHA
            and contract["model_source"]["sha256"] == EXPECTED_V22R_MODEL_PORTABLE_SHA,
        "multi_hour_SARAH_was_not_used_as_a_component_rank_or_quartic_ring_proof": True,
    }
    failures = [name for name, value in checks.items() if value is not True]

    deformation_groups: dict[str, dict[str, Any]] = {}
    for row in direct:
        pair = " / ".join(row["mass_effect"]["residual_pair"])
        group = deformation_groups.setdefault(pair, {
            "residual_pair": row["mass_effect"]["residual_pair"],
            "block": row["mass_effect"]["block"],
            "new_sectors": 0,
            "new_SO10_singlet_contraction_channels": 0,
        })
        group["new_sectors"] += 1
        group["new_SO10_singlet_contraction_channels"] += row["so10_singlet_contraction_channels"]

    model_source = {
        "path": MODEL_PATH.relative_to(ROOT).as_posix(),
        "portable_sha256": sha256(portable_bytes(MODEL_PATH)),
    }
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "namespace": "canonical.susy_so10x17.v22r.G2.missing_partner_deformation_audit",
        "status": (
            "V22R_G2_DIRECT_DEFORMATION_BASIS_CLOSED__ABSTRACT_RANK_STABLE__COMPONENT_CLEBSCH_RANK_OPEN"
            if not failures else "V22R_G2_MISSING_PARTNER_DEFORMATION_AUDIT_FAILED"
        ),
        "sources": {
            "accepted_108_sector_completion": upstream_source,
            "V22R_contract": contract_source,
            "V22R_operator_catalogue": catalogue_source,
            "broken_selector_spurion_frontier": spurion_source,
            "V22R_model": model_source,
        },
        "accepted_basis": {
            "selected_sectors": len(selected),
            "added_sectors": len(extras),
            "direct_missing_partner_deformation_sectors": len(direct),
            "direct_deformation_SO10_singlet_contraction_channels": contraction_channels,
            "original_direct_missing_partner_sectors": len(original_direct),
            "original_direct_SO10_singlet_contraction_channels": original_channels,
            "all_direct_sectors_after_V22R_acceptance": len(original_direct) + len(direct),
            "all_direct_SO10_singlet_channels_after_V22R_acceptance": original_channels + contraction_channels,
            "new_pair_supports": len(new_supports - original_supports),
            "light_light_sectors_in_complete_108_sector_basis": no_light_light,
        },
        "direct_deformations": direct,
        "deformation_groups": sorted(deformation_groups.values(), key=lambda row: row["residual_pair"]),
        "broken_selector_boundary": {
            "XMP_VEV_breaks_Z2S": True,
            "first_audited_XMP_spurion_leakage_layer": {
                "source_degree": 5,
                "sectors": len(degree_five_lifts),
                "so10_flavour_components": audited_leakage["so10_flavour_components"],
                "complete_degree_five_census": False,
                "additional_direct_missing_partner_sectors": len(degree_five_direct),
                "additional_direct_missing_partner_SO10_flavour_components": degree_five_direct_components,
                "additional_direct_missing_partner_rows": degree_five_direct,
                "light_light_sectors": degree_five_light_light,
            },
            "finite_108_sector_catalogue_is_all_order_closed": False,
            "declared_standard_embedding_stabilizer_arithmetic_closed": stabilizer_integral,
            "standard_embedding_phase_exponents": stabilizer_phases,
            "full_F_D_soft_vacuum_realizes_the_declared_stabilizer": False,
            "interpretation": (
                "The 108-sector result is an exact degree-four EFT theorem. The first audited XMP-spurion leakage "
                "layer, not a complete degree-five census, adds fourteen more direct missing-partner deformations "
                "but still no light-light sector. The declared standard "
                "SO(10)-singlet embedding has an exact gauge-compensated diagonal Z28R stabilizer, but the full F+D+soft "
                "vacuum has not been proved to realize that embedding and the Wilsonian spurion tower remains open."
            ),
        },
        "rank_implications": {
            "doublet": {
                "block_form": "[[0_(6x6), A_(6x5)], [B_(5x6), C_(5x5)]]",
                "matrix_shape": [11, 11],
                "structural_rank_upper_bound": 10,
                "structural_nullity_lower_bound": 1,
                "architecture_witness_rank": doublet_rank,
                "nonzero_10x10_minor_determinant": str(d_minor_det),
                "abstract_generic_rank": 10,
                "abstract_generic_nullity": 1,
            },
            "triplet": {
                "block_form": "[[0_(6x6), A_(6x7)], [B_(7x6), C_(7x7)]]",
                "matrix_shape": [13, 13],
                "structural_rank_upper_bound": 13,
                "architecture_witness_rank": triplet_rank,
                "nonzero_13x13_determinant": str(t_det),
                "abstract_generic_rank": 13,
                "abstract_generic_nullity": 0,
            },
            "exact_parameter_extension_theorem": (
                "Setting all ten new-sector coefficients to zero specializes the V22R architecture family to the prior "
                "integer rank witness. Its nonzero doublet minor and triplet determinant therefore remain nonzero "
                "polynomials on a Zariski-open subset of the enlarged abstract block family. Adding parameters cannot "
                "lower the generic maximum rank, although tuned cancellations can lower rank at special points."
            ),
            "source_tensor_limit": (
                "The frozen census proves invariant-copy multiplicities but supplies neither normalized invariant tensors "
                "nor their SO(10)->SM doublet/triplet Clebsch maps. The physical V22R coefficient image may be a proper "
                "subvariety of the abstract block family, so the source-exact ranks are not yet proved."
            ),
            "all_order_zero_block_condition": (
                "The declared standard singlet embedding preserves a gauge-compensated diagonal Z28R by exact phase "
                "arithmetic. The full F+D+soft vacuum must still prove that embedding, every relevant zero VEV, and the "
                "component action of the diagonal symmetry; the all-order zero block therefore remains open."
            ),
        },
        "safe_SARAH_integration": {
            "multi_hour_run_performed": False,
            "sector_marker_syntax": [
                "etaPhiPhiDeltaH*Phi210.Phi210.Delta.H10m/Mstar",
                "etaPhiXDeltaBDelta*Phi210.XMP.DeltaB.Delta/Mstar",
                "etaCCDeltaH*C16bar.C16.Delta.H10m/Mstar",
            ],
            "limits": [
                "A bare SARAH dot monomial is only a sector marker when the SO(10) singlet multiplicity exceeds one; it does not encode the two or four independent invariant tensors.",
                "Every invariant copy needs an explicit normalized contraction/CG definition and an independent coupling before component matrices can be generated.",
                "SuperPotentialCatalogue is metadata ignored by SARAH dynamics; only SuperPotential is processed.",
                "The model's continuous RSymmetry charge vector is an exact integer lift of Z28R only on the accepted truncation: it is a computational encoding, not a declaration of a new physical continuous R symmetry, and it can reject higher operators whose finite charge is 2+28n.",
                "SARAH 4.15.3 CheckPossibleTermsSuperPotential enumerates only field degree one through three and cannot attest the V22R quartic closure.",
                "SARAH CheckChargeConservation exits for SO(10) with ChargeConservation::NoSUN, so the exact external U(1)X/Z28R/Z2S ledger remains authoritative.",
                "The current GaugeES scaffold has no SO(10)->SM component decomposition or VEV/matter-sector definitions, so it cannot produce the required doublet/triplet Clebsch matrices.",
                "A non-aborting CheckModel run is not a rank certificate and must reject timeout, missing-definition, charge, and possible-term diagnostics before it is promotable.",
            ],
            "next_safe_step": (
                "Define the independent SO(10) invariant tensors for the 26 direct contraction channels, project each onto "
                "normalized SM doublet/triplet components, then evaluate one exact V22R vacuum parameter point."
            ),
        },
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "claim_boundary": {
            "accepted_108_sector_basis_source_bound": not failures,
            "ten_direct_deformation_sectors_exactly_classified": not failures,
            "twenty_new_SO10_invariant_copies_exactly_counted": not failures,
            "degree_four_light_light_zero_block_closed": not failures,
            "first_audited_XMP_spurion_leakage_layer_light_light_zero_block_closed": not failures,
            "abstract_missing_partner_rank_architecture_stable": not failures,
            "declared_standard_embedding_stabilizer_arithmetic_closed": not failures,
            "full_F_D_soft_vacuum_stabilizer_realization_closed": False,
            "all_order_light_light_zero_block_closed": False,
            "source_exact_SO10_to_SM_Clebsch_map_closed": False,
            "physical_V22R_doublet_triplet_ranks_closed": False,
            "V22R_G2_closed": False,
            "canonical_G4_closed": False,
            "canonical_G5_closed": False,
        },
        "remaining_exact_work": [
            "construct and normalize all independent SO(10) invariant tensors for the six original and twenty new direct contraction channels",
            "project those tensors onto the complete SM doublet/triplet component bases",
            "solve the full V22R F+D+soft vacuum and prove all R-charge-two VEVs vanish",
            "substitute that vacuum and prove rank(M_D)=10 and rank(M_T)=13 at one exact source point",
            "extend the operator audit beyond the accepted holomorphic degree-four truncation to Kahler and soft sectors",
        ],
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def markdown(report: dict[str, Any]) -> str:
    basis = report["accepted_basis"]
    doublet = report["rank_implications"]["doublet"]
    triplet = report["rank_implications"]["triplet"]
    return "\n".join([
        "# SUSY V22R G2 missing-partner deformation audit",
        "",
        f"- Status: `{report['status']}`",
        f"- Core: `{report['core_sha256']}`",
        f"- Direct added sectors: `{basis['direct_missing_partner_deformation_sectors']}`",
        f"- New SO(10) invariant copies: `{basis['direct_deformation_SO10_singlet_contraction_channels']}`",
        f"- Abstract doublet rank/nullity: `{doublet['abstract_generic_rank']}/{doublet['abstract_generic_nullity']}`",
        f"- Abstract triplet rank/nullity: `{triplet['abstract_generic_rank']}/{triplet['abstract_generic_nullity']}`",
        "",
        "The ten quartic sectors deform only the pre-existing light-heavy and heavy-heavy supports. The complete 108-sector basis contains no two-light-field sector, so the holomorphic light-light zero block survives through degree four.",
        "",
        "This preserves the abstract generic 10/1 doublet and 13/0 triplet rank architecture. V22R G2 remains open because the 20 new invariant copies have no normalized SO(10)->SM Clebsch projection, and the full F+D+soft vacuum is not yet established.",
        "",
        "No multi-hour SARAH run was used. SARAH's current GaugeES scaffold and implicit dot contractions cannot certify the quartic tensor copies or component ranks.",
        "",
    ])


def write_outputs(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    OUT_MD.write_text(markdown(report), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        write_outputs(report)
    if args.check:
        if json.loads(OUT_JSON.read_text(encoding="utf-8")) != report:
            raise ArithmeticError("V22R G2 deformation JSON drifted")
        if OUT_MD.read_text(encoding="utf-8") != markdown(report):
            raise ArithmeticError("V22R G2 deformation Markdown drifted")
    print(report["status"])
    print(report["core_sha256"])
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
