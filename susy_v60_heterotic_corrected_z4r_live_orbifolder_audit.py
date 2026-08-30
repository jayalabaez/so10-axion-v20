#!/usr/bin/env python3
"""V60 source-locked corrected-Z4R audit for the Kappl et al. model.

This certificate parses a vendored, hash-locked lossless projection of a live
Orbifolder-1.1 regeneration rather than a hand-copied spectrum.  It computes
the Eq. (3.40) gamma correction for every plane rotation on every one of the
92 massless chiral multiplets.  Reproduction needs no Orbifolder executable or
external temporary directory.

The calculation is deliberately split into two logically distinct claims:

1. a conditional massless-state ledger, for which h_g is derived exactly for
   every published massless constructing element; and
2. the full-CFT symmetry claim, which remains open because the freely acting
   translation tau is not mapped into its own space-group conjugacy class.

The latter prevents this file from promoting G1 even if a four-dimensional
anomaly residue happens to look attractive.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any, Iterable, Sequence


HERE = Path(__file__).resolve().parent
FIXTURE_PATH = HERE / "susy_v60_heterotic_corrected_z4r_live_orbifolder_fixture.json"
EXPECTED_FIXTURE_SHA256 = "79ef2c19fd0b9a563ac36a06a3099e4b240966ef3dd8fe968fe4029d9b237f51"

JSON_PATH = HERE / "susy_v60_heterotic_corrected_z4r_live_orbifolder_audit.json"
MD_PATH = HERE / "susy_v60_heterotic_corrected_z4r_live_orbifolder_audit.md"


EXPECTED_SHA256 = {
    "modelKapplZ2xZ2Free.txt": "cd7d5f7e1bd0efdc5b7aaa952bcf4e8ccb7916ee4559d86872ab314718846e3f",
    "Geometry_Z2xZ2_Blowup_freelyWL.txt": "ea05e8e3e499c66e590638b17e3c5da8cfdf4d8be6e3f61a18e8e26efbc09021",
    "v59_all_fields_internal.txt": "6e2019fa1413c76cbd8edbcf4f39eb8f9eeb6c5b0a5db534cbea92297d218a3a",
    "v59_all_states.txt": "3fb8fabb6fc8776a92f3a14ea9b5f7aa854c53602dbe9acf35c83a2205adb8aa",
    "v59_anomaly_info.txt": "f68d0b45a8c0eb2ec225a9fe7cb56ef7eae5e288685c7668c8dd4453f969d49f",
    "v59_gauge_group.txt": "53a5ec1b582858287a3ee32928f6dd2959f3d65a6453bae48bd6afb7f1a7a7c5",
    "corbifold.cpp": "d0a4f84d145cecc3b0b49c50dc6018a1df4da4ce67400861769f2d024066c217",
    "cstate.cpp": "15460fb359a76293eb80f48c38f104a4249bedf9e353f7ed2ff15d5a3b031f3b",
}


FACTOR_NAMES = (
    "SU3_C",
    "SU2_L",
    "SU3_hidden",
    "SU2_hidden_1",
    "SU2_hidden_2",
)
FACTOR_N = (3, 2, 3, 2, 2)

# Real lattice basis actions inferred exactly from the local geometry file's
# orthogonal real basis and its two complex twist vectors.
IDENTITY = (1, 1, 1, 1, 1, 1)
THETA = (1, 1, -1, -1, -1, -1)
OMEGA = (-1, -1, 1, 1, -1, -1)
THETA_OMEGA = (-1, -1, -1, -1, 1, 1)
RHO2 = (1, 1, -1, -1, 1, 1)
POINT_GROUP = (IDENTITY, THETA, OMEGA, THETA_OMEGA)
TAU = tuple(Fraction(x, 2) for x in (0, 1, 0, 1, 0, 1))


def F(text: str | int | Fraction) -> Fraction:
    if isinstance(text, Fraction):
        return text
    return Fraction(str(text).strip())


def fstr(value: Fraction | int) -> str:
    value = F(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def mod_fraction(value: Fraction, modulus: int) -> Fraction:
    q = value // modulus
    return value - q * modulus


@dataclass(frozen=True)
class Field:
    name: str
    sector: tuple[int, int]
    fixed: tuple[int, ...]
    sg_charges: tuple[int, ...]
    representation: tuple[int, ...]
    qx: Fraction
    j: tuple[Fraction, ...]
    gamma: tuple[Fraction, ...]
    field_no: int


def load_fixture(path: Path = FIXTURE_PATH) -> dict[str, Any]:
    digest = sha256_file(path)
    if digest != EXPECTED_FIXTURE_SHA256:
        raise ValueError(f"vendored fixture digest changed: {digest}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "susy_v60_compact_orbifolder_92_state_fixture_v1":
        raise ValueError("unexpected V60 fixture schema")
    if data.get("source_sha256") != EXPECTED_SHA256:
        raise ValueError("fixture raw-source digest ledger changed")
    regeneration = data.get("provenance", {}).get("regeneration", {})
    if (
        regeneration.get("massless_chiral_field_count") != 92
        or regeneration.get("all_massless_chiral_oscillators_absent") is not True
    ):
        raise ValueError("fixture spectrum-generation checks changed")
    return data


def parse_fields(fixture: dict[str, Any] | None = None) -> list[Field]:
    fixture = load_fixture() if fixture is None else fixture
    expected_columns = [
        "name", "sector", "fixed_n", "space_group_Z2_charges", "representation",
        "qX", "J", "gamma", "orbifolder_field_no",
    ]
    if fixture.get("field_columns") != expected_columns:
        raise ValueError("unexpected V60 compact field schema")
    fields: list[Field] = []
    for compact in fixture.get("fields", []):
        if len(compact) != len(expected_columns):
            raise ValueError("malformed V60 compact field row")
        name, sector, fixed, sg, representation, qx, j, gamma, field_no = compact
        field = Field(
            name=name,
            sector=tuple(int(x) for x in sector),
            fixed=tuple(int(x) for x in fixed),
            sg_charges=tuple(int(x) for x in sg),
            representation=tuple(int(x) for x in representation),
            qx=F(qx),
            j=tuple(F(x) for x in j),
            gamma=tuple(F(x) for x in gamma),
            field_no=int(field_no),
        )
        fields.append(field)

    expected_names = [f"F_{i}" for i in range(1, 93)]
    if [field.name for field in fields] != expected_names:
        raise ValueError("the internal field file is not the exact ordered F_1,...,F_92 spectrum")
    for field in fields:
        if len(field.fixed) != 6 or len(field.sg_charges) != 6:
            raise ValueError(f"{field.name}: bad space-group dimension")
        if len(field.representation) != 5:
            raise ValueError(f"{field.name}: bad gauge data dimension")
        if len(field.j) != 3 or len(field.gamma) != 9:
            raise ValueError(f"{field.name}: bad right-moving/gamma dimension")
    return fields


def componentwise(values: Sequence[Fraction | int], signs: Sequence[int]) -> tuple[Fraction, ...]:
    return tuple(F(value) * sign for value, sign in zip(values, signs, strict=True))


def vector_add(a: Sequence[Fraction | int], b: Sequence[Fraction | int]) -> tuple[Fraction, ...]:
    return tuple(F(x) + F(y) for x, y in zip(a, b, strict=True))


def point_action(sector: tuple[int, int]) -> tuple[int, ...]:
    k, ell = sector
    return tuple((THETA[i] if k else 1) * (OMEGA[i] if ell else 1) for i in range(6))


def derive_h_for_plane(field: Field, plane: int) -> tuple[tuple[Fraction, ...], str]:
    """Return the translation mu in h=(1,mu), proving rho(g)=hgh^-1.

    For a space-group element g=(A,lambda), conjugation by (1,mu) gives
    (A,lambda+(1-A)mu).  The exact target equation is therefore
    (1-A)mu=(rho2-1)lambda.
    """
    if plane not in (0, 1, 2):
        raise ValueError(f"invalid complex plane {plane + 1}")
    lam = tuple(F(x) for x in field.fixed)
    if field.sector == (0, 0):
        mu = tuple(F(0) for _ in range(6))
        return mu, "untwisted_identity_twist_field"
    action = point_action(field.sector)
    first = 2 * plane
    second = first + 1
    rho = tuple(-1 if i in (first, second) else 1 for i in range(6))
    mu_list = [F(0) for _ in range(6)]
    if action[first] == -1 and action[second] == -1:
        mu_list[first] = -lam[first]
        mu_list[second] = -lam[second]
    else:
        if lam[first] != 0 or lam[second] != 0:
            raise ValueError(
                f"{field.name}: plane-{plane + 1} rotation changes translation in an invariant plane"
            )
    mu = tuple(mu_list)
    lhs = tuple((1 - action[i]) * mu[i] for i in range(6))
    rhs = tuple((rho[i] - 1) * lam[i] for i in range(6))
    if lhs != rhs:
        raise ValueError(f"{field.name}: affine h_g equation failed: {lhs} != {rhs}")
    return mu, "rho2(g)=h_g g h_g^-1_exact"


def derive_h(field: Field) -> tuple[tuple[Fraction, ...], str]:
    """Backward-compatible shorthand for the target second-plane rotation."""
    return derive_h_for_plane(field, 1)


def gamma_for_translation(field: Field, mu: Sequence[Fraction]) -> Fraction:
    # gamma_1,2 are theta,omega; gamma_3,...,8 are e1,...,e6;
    # gamma_9 is tau.  The derived massless h_g uses only integral e_i.
    value = sum((F(mu[i]) * field.gamma[i + 2] for i in range(6)), F(0))
    return mod_fraction(value, 1)


def q_x(field: Field) -> Fraction:
    return field.qx


def charge_row(field: Field) -> dict[str, Any]:
    plane_data = []
    for plane in range(3):
        plane_mu, plane_proof = derive_h_for_plane(field, plane)
        plane_gamma = gamma_for_translation(field, plane_mu)
        old_charge = -2 * field.j[plane]
        corrected_charge = old_charge - 4 * plane_gamma
        if old_charge.denominator != 1 or corrected_charge.denominator != 1:
            raise ValueError(f"{field.name}: non-integral plane-{plane + 1} charge")
        plane_data.append(
            {
                "plane": plane + 1,
                "J": fstr(field.j[plane]),
                "h_g_translation_mu": [fstr(x) for x in plane_mu],
                "h_g_proof": plane_proof,
                "gamma_h": fstr(plane_gamma),
                "R_old_raw": int(old_charge),
                "R_old_mod4": int(old_charge) % 4,
                "R_corrected_raw": int(corrected_charge),
                "R_corrected_mod4": int(corrected_charge) % 4,
                "shift_mod4": (int(corrected_charge) - int(old_charge)) % 4,
            }
        )

    target = plane_data[1]
    gamma_h = F(target["gamma_h"])
    j2 = field.j[1]
    r2_old = F(target["R_old_raw"])
    r2_new = F(target["R_corrected_raw"])
    qx = q_x(field)
    n3 = field.fixed[2]
    q_old_raw = qx + r2_old + 2 * n3
    q_new_raw = qx + r2_new + 2 * n3
    for label, value in (("qX", qx), ("R2_old", r2_old), ("R2_new", r2_new), ("q_old", q_old_raw), ("q_new", q_new_raw)):
        if value.denominator != 1:
            raise ValueError(f"{field.name}: non-integral {label}={value}")
    q_old = int(q_old_raw) % 4
    q_new = int(q_new_raw) % 4
    return {
        "field": field.name,
        "orbifolder_field_no": field.field_no,
        "sector": list(field.sector),
        "fixed_n": list(field.fixed),
        "space_group_Z2_charges": list(field.sg_charges),
        "representation": list(field.representation),
        "qX": int(qx),
        "J2": fstr(j2),
        "h_g": {
            "point_part": [0, 0],
            "translation_mu": target["h_g_translation_mu"],
            "proof": target["h_g_proof"],
        },
        "gamma_h": fstr(gamma_h),
        "gamma_basis": [fstr(x) for x in field.gamma],
        "R2_old_raw": int(r2_old),
        "R2_corrected_raw": int(r2_new),
        "corrected_plane_charges": plane_data,
        "R1_corrected_mod4": plane_data[0]["R_corrected_mod4"],
        "R2_corrected_mod4": plane_data[1]["R_corrected_mod4"],
        "R3_corrected_mod4": plane_data[2]["R_corrected_mod4"],
        "n3": n3,
        "qZ4R_old_mod4": q_old,
        "qZ4R_corrected_mod4": q_new,
        "shift_mod4": (q_new - q_old) % 4,
        "changed": q_old != q_new,
    }


def dynkin_index_for_factor(rep: Sequence[int], factor: int) -> Fraction:
    dimension = abs(rep[factor])
    if dimension == 1:
        return F(0)
    if dimension != FACTOR_N[factor]:
        raise ValueError(f"unsupported representation dimension {dimension} for {FACTOR_NAMES[factor]}")
    multiplicity = 1
    for j, other in enumerate(rep):
        if j != factor:
            multiplicity *= abs(other)
    return Fraction(multiplicity, 2)


def anomaly_ledger(rows: Sequence[dict[str, Any]], charge_key: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for factor, name in enumerate(FACTOR_NAMES):
        matter = F(0)
        contributions: list[dict[str, Any]] = []
        for row in rows:
            index = dynkin_index_for_factor(row["representation"], factor)
            if index == 0:
                continue
            fermion_charge = int(row[charge_key]) - 1
            term = fermion_charge * index
            matter += term
            contributions.append(
                {
                    "field": row["field"],
                    "fermion_charge_representative": fermion_charge,
                    "index_with_spectator_multiplicity": fstr(index),
                    "contribution": fstr(term),
                }
            )
        total = F(FACTOR_N[factor]) + matter
        result[name] = {
            "gaugino_C2": FACTOR_N[factor],
            "matter_sum": fstr(matter),
            "A_representative": fstr(total),
            "A_mod_eta_2": fstr(mod_fraction(total, 2)),
            "contributions": contributions,
        }
    return result


def non_r_sg_anomaly_vectors(fields: Sequence[Field]) -> dict[str, Any]:
    # The six charges printed by Orbifolder are exactly the six "new non-R
    # symmetry" entries in the geometry file.  Mixing qZ4 by 2*s_j changes
    # A_G by 2*B_G, B_G=sum s_j*T(R).
    labels = ("k", "ell", "n1", "n3", "n5", "free_half_shift_rule")
    vectors: dict[str, Any] = {}
    for sg_index, label in enumerate(labels):
        B: list[Fraction] = []
        delta: list[Fraction] = []
        for factor in range(5):
            value = sum(
                (
                    F(field.sg_charges[sg_index])
                    * dynkin_index_for_factor(field.representation, factor)
                    for field in fields
                ),
                F(0),
            )
            B.append(value)
            delta.append(2 * value)
        vectors[label] = {
            "B_G": {name: fstr(value) for name, value in zip(FACTOR_NAMES, B, strict=True)},
            "delta_A_for_q_to_q_plus_2s": {
                name: fstr(value) for name, value in zip(FACTOR_NAMES, delta, strict=True)
            },
            "delta_residues_mod2": [fstr(mod_fraction(value, 2)) for value in delta],
        }
    return vectors


def exhaustive_sg_repair(
    corrected: dict[str, Any],
    vectors: dict[str, Any],
) -> dict[str, Any]:
    base = [F(corrected[name]["A_representative"]) for name in FACTOR_NAMES]
    deltas = [
        [F(vectors[label]["delta_A_for_q_to_q_plus_2s"][name]) for name in FACTOR_NAMES]
        for label in vectors
    ]
    universal_solutions: list[list[int]] = []
    all_residues: dict[str, int] = {}
    for bits in product((0, 1), repeat=len(deltas)):
        candidate = [base[j] + sum((bits[i] * deltas[i][j] for i in range(len(bits))), F(0)) for j in range(5)]
        residues = tuple(mod_fraction(value, 2) for value in candidate)
        key = ",".join(fstr(value) for value in residues)
        all_residues[key] = all_residues.get(key, 0) + 1
        if len(set(residues)) == 1:
            universal_solutions.append(list(bits))
    return {
        "mixings_enumerated": 2 ** len(deltas),
        "generator_order": list(vectors),
        "universal_solution_count": len(universal_solutions),
        "universal_solutions": universal_solutions,
        "distinct_residue_vectors": all_residues,
        "repair_exists": bool(universal_solutions),
    }


def corrected_plane_anomaly_audit(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    ledgers = {
        f"R{plane}": anomaly_ledger(rows, f"R{plane}_corrected_mod4")
        for plane in (1, 2, 3)
    }
    residue_vectors = {
        label: [ledger[name]["A_mod_eta_2"] for name in FACTOR_NAMES]
        for label, ledger in ledgers.items()
    }
    expected = {
        "R1": ["0", "0", "0", "1", "1"],
        "R2": ["0", "0", "0", "1", "1"],
        "R3": ["1", "1", "1", "0", "0"],
    }
    if residue_vectors != expected:
        raise ValueError(f"corrected plane anomaly residues changed: {residue_vectors}")

    pattern_counts: dict[str, int] = {}
    coefficient_rows: list[dict[str, Any]] = []
    universal_count = 0
    for coefficients in product(range(4), repeat=3):
        if sum(coefficients) % 2 != 1:
            continue
        combined_rows = []
        for row in rows:
            combined = sum(
                coefficients[i] * int(row[f"R{i + 1}_corrected_mod4"])
                for i in range(3)
            ) % 4
            combined_rows.append({**row, "combined_plane_R_mod4": combined})
        ledger = anomaly_ledger(combined_rows, "combined_plane_R_mod4")
        residues = [ledger[name]["A_mod_eta_2"] for name in FACTOR_NAMES]
        key = ",".join(residues)
        pattern_counts[key] = pattern_counts.get(key, 0) + 1
        universal = len(set(residues)) == 1
        universal_count += int(universal)
        coefficient_rows.append(
            {
                "coefficients_mod4": list(coefficients),
                "sum_odd_superpotential_charge_2": True,
                "residue_vector_mod2": residues,
                "universal": universal,
            }
        )
    if len(coefficient_rows) != 32 or universal_count != 0:
        raise ValueError("unexpected corrected plane-combination scan result")
    return {
        "individual_ledgers": ledgers,
        "individual_residue_vectors_mod2": residue_vectors,
        "coefficient_scan": {
            "coefficients_tested": len(coefficient_rows),
            "domain": "c_i in Z4 with c1+c2+c3 odd, so W has charge 2 mod4",
            "residue_pattern_counts": pattern_counts,
            "universal_case_count": universal_count,
            "universal_case_exists": bool(universal_count),
            "rows": coefficient_rows,
        },
    }


def parse_continuous_u1_anomalies(fixture: dict[str, Any] | None = None) -> dict[str, Any]:
    fixture = load_fixture() if fixture is None else fixture
    matrix = [
        [F(value) for value in row]
        for row in fixture.get("continuous_mixed_anomaly_matrix", [])
    ]
    if len(matrix) != 5 or any(len(row) != 9 for row in matrix):
        raise ValueError("expected a 5x9 vendored continuous mixed-anomaly matrix")
    relative_columns = []
    for u1 in range(9):
        column = [matrix[g][u1] for g in range(5)]
        relative_columns.append(len(set(column)) == 1)
    return {
        "matrix_factor_order": list(FACTOR_NAMES),
        "matrix_U1_columns_1_to_9": [[fstr(x) for x in row] for row in matrix],
        "each_column_is_universal_across_all_non_Abelian_factors": relative_columns,
        "all_U1_mixings_leave_relative_anomalies_invariant": all(relative_columns),
        "stronger_than_integrality_restrictions": (
            "Even allowing arbitrary integer coefficients for every printed U(1), each anomaly column is universal; "
            "therefore no U(1) combination changes any pairwise A_G-A_H difference."
        ),
    }


def plane_rotation_action(coefficients: Sequence[int]) -> tuple[int, ...]:
    if len(coefficients) != 3:
        raise ValueError("expected three plane-rotation coefficients")
    signs: list[int] = []
    for coefficient in coefficients:
        sign = -1 if int(coefficient) % 2 else 1
        signs.extend((sign, sign))
    return tuple(signs)


def tau_conjugacy_obstruction() -> dict[str, Any]:
    orbit = [componentwise(TAU, action) for action in POINT_GROUP]
    # For a pure translation t, (B,mu)(1,t)(B,mu)^-1=(1,Bt); mu drops out.
    rho_tau = componentwise(TAU, RHO2)
    in_orbit = rho_tau in orbit
    if in_orbit:
        raise ValueError("source-locked tau obstruction unexpectedly disappeared")
    scan_rows: list[dict[str, Any]] = []
    class_preserving_count = 0
    for coefficients in product(range(4), repeat=3):
        if sum(coefficients) % 2 != 1:
            continue
        rho = plane_rotation_action(coefficients)
        image = componentwise(TAU, rho)
        preserving = image in orbit
        class_preserving_count += int(preserving)
        scan_rows.append(
            {
                "coefficients_mod4": list(coefficients),
                "odd_plane_flip_count": sum(int(c) % 2 for c in coefficients),
                "rho_tau": [fstr(x) for x in image],
                "in_point_group_conjugacy_orbit": preserving,
            }
        )
    if len(scan_rows) != 32 or class_preserving_count != 0:
        raise ValueError("unexpected full odd-plane-R tau scan result")
    return {
        "tau": [fstr(x) for x in TAU],
        "rho2_tau": [fstr(x) for x in rho_tau],
        "rho2_tau_equals_tau_minus_e4": rho_tau == vector_add(TAU, (0, 0, 0, -1, 0, 0)),
        "point_group_conjugacy_orbit": [[fstr(x) for x in row] for row in orbit],
        "rho2_tau_in_conjugacy_orbit": in_orbit,
        "no_h_tau_in_space_group": not in_orbit,
        "all_odd_sum_plane_R_combinations": {
            "combinations_tested": len(scan_rows),
            "domain": "c_i in Z4 with c1+c2+c3 odd (superpotential charge 2)",
            "point_group_plane_flip_parities": [0, 2, 2, 2],
            "candidate_plane_flip_parity": "odd",
            "class_preserving_count": class_preserving_count,
            "every_candidate_fails_class_preservation": class_preserving_count == 0,
            "rows": scan_rows,
        },
        "parity_theorem": (
            "The Z2xZ2 point group flips an even number of complex planes, whereas each odd-sum "
            "c_i combination flips an odd number. Since tau has a half-component in one real "
            "coordinate of every plane, rho_c(tau) cannot equal B tau for any point-group B."
        ),
        "scope": (
            "For all 32 plane-R candidates with superpotential charge 2, this blocks direct use of the class-preserving Eq. (3.40) derivation as a proof of a diagonal symmetry of the full freely quotiented CFT. "
            "It is not a theorem that no symmetry exists: rho_c may permute winding sectors and require an enlarged treatment."
        ),
    }


def source_lock(fixture: dict[str, Any] | None = None) -> dict[str, Any]:
    fixture = load_fixture() if fixture is None else fixture
    fixture_digest = sha256_file(FIXTURE_PATH)
    rows: dict[str, Any] = {
        FIXTURE_PATH.name: {
            "path": FIXTURE_PATH.name,
            "sha256": fixture_digest,
            "expected_sha256": EXPECTED_FIXTURE_SHA256,
            "matches_expected": fixture_digest == EXPECTED_FIXTURE_SHA256,
            "availability_required": True,
            "role": "vendored lossless projection used by this certificate",
        }
    }
    for label, expected in EXPECTED_SHA256.items():
        pinned = fixture["source_sha256"].get(label)
        rows[label] = {
            "source_filename": label,
            "sha256": pinned,
            "expected_sha256": expected,
            "matches_expected": pinned == expected,
            "availability_required": False,
            "role": "provenance lock for the original model/source or regenerated raw output",
        }
    archive = fixture["provenance"]["download_archive"]
    rows[archive["filename"]] = {
        "source_filename": archive["filename"],
        "size_bytes": archive["size_bytes"],
        "sha256": archive["sha256"],
        "expected_sha256": "f3a1ec863787f79dd78651e62d3060fc7342a17a67acd7592d2386d67752ab92",
        "matches_expected": archive["sha256"] == "f3a1ec863787f79dd78651e62d3060fc7342a17a67acd7592d2386d67752ab92",
        "availability_required": False,
        "dataset_doi": fixture["provenance"]["dataset_doi"],
        "dataset_url": fixture["provenance"]["dataset_url"],
        "role": "provenance lock for the original Mendeley download",
    }
    if not all(row["matches_expected"] for row in rows.values()):
        raise ValueError("a vendored or provenance source digest changed")
    return rows


def geometry_file_checks(fixture: dict[str, Any] | None = None) -> dict[str, Any]:
    fixture = load_fixture() if fixture is None else fixture
    geometry = dict(fixture.get("geometry_checks", {}))
    expected_order = ["theta", "omega", "e1", "e2", "e3", "e4", "e5", "e6", "tau"]
    if (
        geometry.get("twists_present") is not True
        or geometry.get("free_shift_generator_present") is not True
        or geometry.get("new_non_R_symmetry_count") != 6
        or geometry.get("new_R_symmetry_count") != 3
        or geometry.get("gamma_column_order") != expected_order
    ):
        raise ValueError("vendored geometry projection changed")
    return geometry


def build_report() -> dict[str, Any]:
    fixture = load_fixture()
    locks = source_lock(fixture)
    geometry = geometry_file_checks(fixture)
    fields = parse_fields(fixture)
    rows = [charge_row(field) for field in fields]
    changed = [row for row in rows if row["changed"]]
    expected_changed = ["F_41", "F_42", "F_80", "F_81", "F_91", "F_92"]
    if [row["field"] for row in changed] != expected_changed:
        raise ValueError(f"unexpected corrected-charge shifts: {[row['field'] for row in changed]}")

    sector_counts: dict[str, int] = {}
    for field in fields:
        key = f"T_{field.sector[0]}{field.sector[1]}" if field.sector != (0, 0) else "U"
        sector_counts[key] = sector_counts.get(key, 0) + 1

    old_anomalies = anomaly_ledger(rows, "qZ4R_old_mod4")
    corrected_anomalies = anomaly_ledger(rows, "qZ4R_corrected_mod4")
    plane_anomalies = corrected_plane_anomaly_audit(rows)
    sg_vectors = non_r_sg_anomaly_vectors(fields)
    sg_repair = exhaustive_sg_repair(corrected_anomalies, sg_vectors)
    u1 = parse_continuous_u1_anomalies(fixture)
    tau_issue = tau_conjugacy_obstruction()

    corrected_residues = [corrected_anomalies[name]["A_mod_eta_2"] for name in FACTOR_NAMES]
    relative_nonuniversal = len(set(corrected_residues)) != 1
    repair_absent = (not sg_repair["repair_exists"]) and u1["all_U1_mixings_leave_relative_anomalies_invariant"]
    sg_delta_patterns = {
        tuple(row["delta_residues_mod2"])
        for row in sg_vectors.values()
    }
    if not sg_delta_patterns.issubset({("0",) * 5, ("1",) * 5}):
        raise ValueError(f"a printed SG mixing changes relative anomalies: {sg_delta_patterns}")
    full_abelian_no_repair = (
        plane_anomalies["coefficient_scan"]["universal_case_exists"] is False
        and repair_absent
        and sg_delta_patterns.issubset({("0",) * 5, ("1",) * 5})
    )

    report: dict[str, Any] = {
        "artifact": "SUSY_V60_HETEROTIC_CORRECTED_Z4R_LIVE_ORBIFOLDER_AUDIT",
        "status": (
            "V60_LIVE_ORBIFOLDER_92_STATE_RECONSTRUCTION_PASS__SIX_GAMMA_CORRECTIONS_EXACT__"
            "ALL_THREE_CORRECTED_PLANE_R_LEDGERS_EXACT__FULL_4CUBED_ODD_SUM_SCAN_NONUNIVERSAL__"
            "AVAILABLE_U1_AND_SPACE_GROUP_MIXINGS_DO_NOT_REPAIR__"
            "ALL_32_ODD_PLANE_R_FREE_TAU_CLASS_PRESERVATION_FAIL__"
            "LOCAL_THRESHOLD_AXION_LEDGER_UNKNOWN__STRICT_G1_OPEN"
        ),
        "primary_sources": {
            "Kappl_et_al_1012.4574": {
                "url": "https://arxiv.org/abs/1012.4574",
                "uses": ["Eqs. (3.11)-(3.12)", "Eqs. (E.1)-(E.6)", "Table E.2", "Appendix A.2"],
            },
            "Cabo_Bizet_et_al_1308.5669": {
                "url": "https://arxiv.org/abs/1308.5669",
                "uses": ["Eqs. (3.25)-(3.40)", "Eqs. (4.43)-(4.46)"],
            },
            "Schmitz_BONN_IR_2014_12": {
                "url": "https://d-nb.info/1077289065/34",
                "uses": ["Sec. 3.3.6", "Table 3.1", "Z2xZ2-5-1 free-involution warning"],
            },
            "Orbifolder_AELR_v1_0": {
                "url": fixture["provenance"]["dataset_url"],
                "doi": fixture["provenance"]["dataset_doi"],
                "uses": ["Orbifolder v1.1 source archive and exact Kappl-model regeneration provenance"],
            },
            "Ramos_Sanchez_Vaudrevange_JHEP01_2019_055": {
                "url": "https://doi.org/10.1007/JHEP01(2019)055",
                "uses": [
                    "Eqs. (3.47)-(3.51): exact non-R SG-flavor Z4 for Z2xZ2-5-1",
                    "massless strings carry only even values of that Z4 charge",
                ],
            },
        },
        "self_contained_reproduction": {
            "requires_external_orbifolder_tree": False,
            "requires_orbifolder_executable": False,
            "vendored_fixture": FIXTURE_PATH.name,
            "vendored_fixture_sha256": EXPECTED_FIXTURE_SHA256,
            "fixture_projection": list(fixture["field_columns"]),
            "raw_regeneration_hashes_preserved": True,
            "original_Mendeley_archive_hash_preserved": True,
            "provenance": fixture["provenance"],
        },
        "source_lock": locks,
        "geometry_and_conventions": {
            **geometry,
            "theta_real_action": list(THETA),
            "omega_real_action": list(OMEGA),
            "rho2_real_action": list(RHO2),
            "rho2_angles": ["0", "-1/2", "0"],
            "spin_lift_integer_normalization": {
                "M": 4,
                "superpotential_charge": 2,
                "J2": "q_sh^2-N_L^2+Nbar_L^2; all 92 regenerated fields have no oscillators",
                "R2_old": "-2 J2",
                "R2_corrected": "-2 J2 - 4 gamma_hg (mod 4)",
                "qZ4R_corrected": "qX + R2_corrected + 2 n3 (mod 4)",
            },
            "h_g_derivation": {
                "equation": "(1-A_g) mu = (rho2-1) lambda for h_g=(1,mu)",
                "T10_and_T11": "mu=-n3 e3-n4 e4",
                "T01": "mu=0 because every regenerated representative has n3=n4=0",
                "untwisted": "identity twist-field phase",
                "gamma_hg": "-n3 gamma_5-n4 gamma_6 mod 1 for T10/T11; 0 otherwise",
                "all_plane_generalization": (
                    "For plane i, mu=-(n_(2i-1)e_(2i-1)+n_(2i)e_(2i)) when A_g flips that plane; "
                    "when A_g leaves it invariant, every regenerated representative has both corresponding n values zero and mu=0."
                ),
            },
        },
        "spectrum": {
            "field_count": len(fields),
            "sector_counts": sector_counts,
            "all_oscillators_absent": fixture["provenance"]["regeneration"]["all_massless_chiral_oscillators_absent"],
            "all_affine_hg_equations_pass": True,
            "charge_rows": rows,
            "changed_field_count": len(changed),
            "changed_fields": changed,
        },
        "non_Abelian_mixed_Z4R_anomalies": {
            "formula": "A_G=C2(G)+sum_i (q_i-1) T_G(R_i), eta=M/2=2",
            "factor_order": list(FACTOR_NAMES),
            "old_2010_charge_ledger": old_anomalies,
            "corrected_conditional_massless_ledger": corrected_anomalies,
            "corrected_residue_vector_mod2": corrected_residues,
            "corrected_residues_universal": not relative_nonuniversal,
            "all_three_corrected_plane_R_audit": plane_anomalies,
        },
        "mixing_repair_audit": {
            "continuous_U1": u1,
            "space_group_Z2_vectors": sg_vectors,
            "space_group_exhaustive_binary_search": sg_repair,
            "space_group_delta_residue_patterns": [list(row) for row in sorted(sg_delta_patterns)],
            "every_printed_space_group_mixing_shifts_zero_or_all_five_residues": True,
            "relative_nonuniversality_present": relative_nonuniversal,
            "available_U1_and_printed_space_group_mixings_cannot_repair": repair_absent,
            "no_Abelian_combination_in_plane_R_x_U1_9_x_SG_basis_repairs": full_abelian_no_repair,
            "scope_caveat": (
                "The no-repair statement covers the nine continuous U(1) generators and six printed non-R space-group Z2 generators of this exact Orbifolder action. "
                "It does not exclude an enlarged sector-permuting symmetry, extra threshold counterterms, or an additional axion not represented by these charge mixings."
            ),
            "published_SG_Z4_crosscheck": {
                "result": (
                    "JHEP 01 (2019) 055, Eqs. (3.47)-(3.51), derives a non-R SG-flavor Z4 for affine class Z2xZ2-5-1 and states that all massless strings have even Z4 charge."
                ),
                "implication": (
                    "On massless states its faithful action reduces to a Z2, so it does not supply a new order-four R action beyond the non-R SG mixing class already audited."
                ),
                "basis_map_caveat": (
                    "The later original-basis formula Q_top=n_tau+2(n2+n4+n6) mod4 is not independently source-derived in this certificate and is not used as an input to the no-repair proof."
                ),
            },
        },
        "full_CFT_obstruction": tau_issue,
        "unknown_obligations": [
            "derive the action of rho2 on all freely twisted/winding sectors when conjugacy classes are permuted",
            "compute local/fixed-locus anomaly phases and any localized counterterms",
            "compute moduli-dependent threshold corrections for the corrected mixed generator",
            "derive the complete quantized axion coupling and transformation matrix",
            "recheck the corrected generator after the selected singlet VEVs and mass diagonalization",
        ],
        "terminal_decision": {
            "conditional_92_state_charge_reconstruction": "PASS",
            "six_corrected_shifts": "PASS",
            "corrected_non_Abelian_anomaly_universality": "FAIL",
            "all_corrected_plane_R_combinations_with_W_charge_2": "FAIL_UNIVERSALITY",
            "repair_by_available_U1_or_printed_space_group_mixings": "FAIL",
            "full_CFT_class_preserving_rho2_action": "FAIL",
            "all_32_W_charge_2_plane_R_class_preserving_actions": "FAIL",
            "full_GS_local_threshold_completion": "OPEN",
            "physical_symmetry_no_go_proved": False,
            "strict_G1_closed": False,
            "gate_promotion": "NONE",
        },
    }
    report["canonical_core_sha256"] = canonical_sha256(report)
    return report


def render_markdown(report: dict[str, Any]) -> str:
    spectrum = report["spectrum"]
    anomalies = report["non_Abelian_mixed_Z4R_anomalies"]
    plane = anomalies["all_three_corrected_plane_R_audit"]
    old = anomalies["old_2010_charge_ledger"]
    new = anomalies["corrected_conditional_massless_ledger"]
    repair = report["mixing_repair_audit"]
    tau = report["full_CFT_obstruction"]
    changed_lines = []
    for row in spectrum["changed_fields"]:
        changed_lines.append(
            f"| {row['field']} | {row['orbifolder_field_no']} | {row['sector']} | {row['fixed_n']} | "
            f"{row['representation']} | {row['gamma_h']} | {row['qZ4R_old_mod4']} | {row['qZ4R_corrected_mod4']} |"
        )
    anomaly_lines = []
    for name in FACTOR_NAMES:
        anomaly_lines.append(
            f"| {name} | {old[name]['A_representative']} | {old[name]['A_mod_eta_2']} | "
            f"{new[name]['A_representative']} | {new[name]['A_mod_eta_2']} |"
        )
    return "\n".join(
        [
            "# V60 corrected Z4R live-Orbifolder audit",
            "",
            f"- Status: `{report['status']}`",
            f"- Canonical core: `{report['canonical_core_sha256']}`",
            f"- Regenerated chiral fields: `{spectrum['field_count']}`",
            f"- Vendored fixture: `{report['self_contained_reproduction']['vendored_fixture']}` (`{report['self_contained_reproduction']['vendored_fixture_sha256']}`)",
            "- Reproduction requires neither the original temporary tree nor an Orbifolder executable.",
            "- Strict result: **G1 remains open; no gate promotion.**",
            "",
            "## Result",
            "",
            "The live Orbifolder regeneration removes the V59 publication-data ambiguity for the 92 massless chiral multiplets. "
            "For the second-plane rotation, the exact affine equation is",
            "",
            "```text",
            "(1-A_g) mu = (rho2-1) lambda,    h_g=(1,mu),",
            "mu=-n3 e3-n4 e4 in T(1,0) and T(1,1).",
            "```",
            "",
            "Because Orbifolder orders its gamma basis as `(theta,omega,e1,e2,e3,e4,e5,e6,tau)`,",
            "",
            "```text",
            "gamma_hg = -n3 gamma_5 - n4 gamma_6 mod 1,",
            "R2_new  = -2 J2 - 4 gamma_hg mod 4,",
            "qZ4R    = qX + R2_new + 2 n3 mod 4.",
            "```",
            "",
            "Exactly six charges shift:",
            "",
            "| Field | internal no. | sector | n | representation | gamma_h | old | corrected |",
            "|---|---:|---|---|---|---:|---:|---:|",
            *changed_lines,
            "",
            "## Non-Abelian mixed anomalies at the orbifold point",
            "",
            "The representative convention is `q=0,1,2,3`, with `A_G=C2(G)+sum(q-1)T(R)` and `eta=2`.",
            "",
            "| Factor | old A | old mod 2 | corrected A | corrected mod 2 |",
            "|---|---:|---:|---:|---:|",
            *anomaly_lines,
            "",
            f"Corrected residues are `{anomalies['corrected_residue_vector_mod2']}` and are **not universal**.",
            "",
            "The same derivation was performed independently for all three plane rotations. Their residue vectors in factor order "
            "`(SU3_C,SU2_L,SU3_hidden,SU2_hidden_1,SU2_hidden_2)` are:",
            "",
            f"- `R1`: `{plane['individual_residue_vectors_mod2']['R1']}`",
            f"- `R2`: `{plane['individual_residue_vectors_mod2']['R2']}`",
            f"- `R3`: `{plane['individual_residue_vectors_mod2']['R3']}`",
            "",
            f"The exhaustive scan tested all `{plane['coefficient_scan']['coefficients_tested']}` triples `c_i in Z4` with odd `c1+c2+c3`, "
            "which are precisely the combinations whose superpotential charge is 2. "
            f"The residue-pattern counts are `{plane['coefficient_scan']['residue_pattern_counts']}`; universal cases: "
            f"`{plane['coefficient_scan']['universal_case_count']}`.",
            "",
            "## Mixing repair audit",
            "",
            "The exact Orbifolder continuous-anomaly matrix has the same first-column anomaly `15` for all five factors and zero in the other eight columns. "
            "Thus every continuous-U(1) mixing leaves all pairwise anomaly differences unchanged.",
            "",
            f"All `{repair['space_group_exhaustive_binary_search']['mixings_enumerated']}` binary combinations of the six printed non-R space-group generators were checked. "
            f"Universal solutions: `{repair['space_group_exhaustive_binary_search']['universal_solution_count']}`.",
            "Each printed space-group generator shifts either none or all five anomaly residues, so it cannot alter their relative pattern. "
            "Consequently no Abelian combination in the corrected plane-R x U(1)^9 x printed-space-group basis restores universality.",
            "",
            "JHEP 01 (2019) 055 independently derives an exact non-R SG-flavor `Z4` for affine class `Z2xZ2-5-1`, but its massless charges are all even. "
            "Its faithful massless action is therefore only `Z2`; it is not an extra order-four R candidate. The later original-basis charge formula is not used in this certificate because that basis map was not independently source-derived here.",
            "",
            "This no-repair statement is limited to the explicitly regenerated U(1) and space-group charge basis. It does not rule out sector-permuting actions, threshold terms, localized counterterms, or additional axionic structure.",
            "",
            "## Full-CFT fail-closed obstruction",
            "",
            f"The free generator is `tau={tau['tau']}`, while `rho2(tau)={tau['rho2_tau']}=tau-e4`. "
            "For a pure translation, conjugation can only send `tau` to `B tau` for a point-group element `B`. The `Z2 x Z2` point group flips an even number of planes, but every odd-sum plane-R combination flips an odd number. "
            f"Therefore none of the `{tau['all_odd_sum_plane_R_combinations']['combinations_tested']}` candidates with superpotential charge 2 maps `tau` into its point-group conjugacy orbit. "
            "No class-preserving `h_tau` exists for any of them, so the direct Eq. (3.40) hypothesis fails for the full freely quotiented CFT.",
            "",
            "This is not a physical no-go: the rotation may permute winding sectors and require an enlarged treatment. It is decisive against claiming that the 92-state anomaly calculation alone proves a globally gauged Z4R.",
            "",
            "## Sources",
            "",
            "- [Kappl et al., arXiv:1012.4574](https://arxiv.org/abs/1012.4574), Eqs. (3.11)-(3.12), (E.1)-(E.6), Table E.2 and Appendix A.2.",
            "- [Cabo Bizet et al., arXiv:1308.5669](https://arxiv.org/abs/1308.5669), Eqs. (3.25)-(3.40) and (4.43)-(4.46).",
            "- [Schmitz, BONN-IR-2014-12](https://d-nb.info/1077289065/34), Sec. 3.3.6 and Table 3.1.",
            "- [Orbifolder AELR_v1_0 dataset](https://data.mendeley.com/datasets/zrcpg6s3yw/1), DOI `10.17632/zrcpg6s3yw.1`; the original download and every regenerated raw output remain hash-pinned in the fixture.",
            "- [Ramos-Sanchez and Vaudrevange, JHEP 01 (2019) 055](https://doi.org/10.1007/JHEP01(2019)055), Eqs. (3.47)-(3.51).",
            "",
            "## Verdict",
            "",
            "The corrected 92-state calculation is complete and reproducible, but it worsens the result: the five non-Abelian residues are relatively non-universal and the available printed U(1)/space-group mixings do not repair them. "
            "The full free-quotient action, local/threshold anomalies and quantized axion ledger remain unresolved. Strict G1 stays open.",
            "",
        ]
    )


def json_text(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def check_or_write(check: bool) -> int:
    report = build_report()
    expected = {JSON_PATH: json_text(report), MD_PATH: render_markdown(report)}
    if check:
        failures = []
        for path, content in expected.items():
            if not path.exists():
                failures.append(f"missing {path.name}")
            elif path.read_text(encoding="utf-8") != content:
                failures.append(f"stale {path.name}")
        if failures:
            print("\n".join(failures))
            return 1
        print(f"V60 check PASS: {report['canonical_core_sha256']}")
        return 0
    for path, content in expected.items():
        path.write_text(content, encoding="utf-8", newline="\n")
    print(f"wrote {JSON_PATH.name} and {MD_PATH.name}")
    print(f"canonical core: {report['canonical_core_sha256']}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="verify generated artifacts are current")
    args = parser.parse_args()
    return check_or_write(args.check)


if __name__ == "__main__":
    raise SystemExit(main())
