#!/usr/bin/env python3
"""Trusted, fail-closed verifier for canonical gauged-X G3."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parent
SCHEMA = "canonical_gauged_u1x_gate_verification_v1"
EVIDENCE_SCHEMA = "canonical_gauged_u1x_gate_evidence_v1"
NAMESPACE = "canonical.gauged_u1x.phenomenology.v21"
MODEL = "gauged_u1x_phi17_v20"
G2_ID = f"{NAMESPACE}.G2.full_component_projection_dim6"
G3_ID = f"{NAMESPACE}.G3.physical_ew_global_vacuum"
EXPECTED_ARTIFACT = "CANONICAL_G3_PHYSICAL_EW_GLOBAL_VACUUM_V21.json"
EXPECTED_PRODUCER = "canonical_g3_physical_ew_global_vacuum_v21.py"
EXPECTED_STATUS = "CANONICAL_G3_PHYSICAL_EW_GLOBAL_VACUUM_EXACTLY_CLOSED"
EXPECTED_CRITERIA = (
    "the physical-EW vacuum is source-exact stationary for the complete accepted potential",
    "the gauge quotient contains exactly 37 broken gauge directions derived as 45+1-8-1",
    "all non-symmetry component Hessian modes are strictly positive with the intended axion direction identified",
    "boundedness and global equality-orbit classification exclude every deeper or disconnected competing extremum",
)
EXPECTED_SOURCE_PATHS = (
    EXPECTED_PRODUCER,
    "canonical_g1_g8_gauged_u1x_v21.py",
    "CANONICAL_G1_SUSYNO_CHANNEL_BASIS_V21.json",
    "CANONICAL_G2_EXACT_CONTRACTION_BASIS_V21.json",
    "CANONICAL_G2_FULL_COMPONENT_PROJECTION_DIM6_V21.json",
    "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_CLOSURE_V20.json",
    "exact_210_pati_salam_global_vacuum_v20.py",
    "exact_gauged_u1x_g3_a_square_recoupling_v20.py",
    "EXACT_GAUGED_U1X_G3_A_SQUARE_RECOUPLING_V20.json",
    "exact_physical_sm_37_row_aggregate_v20.py",
    "exact_physical_sm_hard_projector_hessians_v20.py",
    "exact_physical_sm_easy_21_hessians_v20.py",
    "exact_physical_sm_last_six_hessians_v20.py",
    "physical_sm_vacuum_local_feasibility_v20.py",
    "PHYSICAL_SM_VACUUM_LOCAL_FEASIBILITY_V20.json",
)
EXPECTED_PINS = {
    EXPECTED_PRODUCER: "d9cfab99505ac0fce0e7bdaad336a769dbb50ed29d02c73d9c9afc96dc81f99c",
    "CANONICAL_G1_SUSYNO_CHANNEL_BASIS_V21.json": "066e2ccd746d97ca562ca4f84957816a2d6babed10574112e8f7118ac23cd309",
    "CANONICAL_G2_EXACT_CONTRACTION_BASIS_V21.json": "e88c6ddd02818eebf80b554118a5cad14e8d16581430c95f43501e1a6d4736a2",
    "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_CLOSURE_V20.json": "c2e4692d1e1cf991265ffd5d054f9d6aa99cf1143a7e8e7d6db06284fb1c04ee",
    "exact_210_pati_salam_global_vacuum_v20.py": "54fa1a4433b8a78236f67b40db17bf0ec3087de0ea9e1a7e93eceab4a55a7ac8",
    "exact_gauged_u1x_g3_a_square_recoupling_v20.py": "013e27c9b365883d8d226d0ec61be235a36b3714818cb2333f575a65f1597c9f",
    "EXACT_GAUGED_U1X_G3_A_SQUARE_RECOUPLING_V20.json": "db56b0cf2e6ca72a554ee0d028915318a8d9e7e87cff63372a3b26d7667fdd55",
    "exact_physical_sm_37_row_aggregate_v20.py": "801b456743d9037d4478dcb3c94fef3d745ad312b58c3b262324aeded7567f5c",
    "exact_physical_sm_hard_projector_hessians_v20.py": "2ac49af04f3bbec17a4e616c82898de6a0710ddcfa3462d7ec8d59dad69de27e",
    "exact_physical_sm_easy_21_hessians_v20.py": "e8b6fcf9bc459ee4c05a74d41cae6d9a82680de88683ba5ffcc4ceb30fe73311",
    "exact_physical_sm_last_six_hessians_v20.py": "78d712d3573ec3377a331eb52dbf429452aa1c7ed82aeb7eeb0aa5900b3774ce",
    "physical_sm_vacuum_local_feasibility_v20.py": "629ea8c45f101f82b6b4e963fd1fb19dcc5735fe52a1d8efb1fb0812dbaa565c",
    "PHYSICAL_SM_VACUUM_LOCAL_FEASIBILITY_V20.json": "ac575067550472afeae1d87503c04a47bf27386223a4417cf7c2341ad75af315",
}
EXPECTED_COEFFICIENTS = {
    "O03_B01_singlet_polynomial": "-1",
    "O04_B01_singlet_polynomial": "-1/25",
    "O05_B01_126bar_norm": "99/25",
    "O06_B01_Hdag_H_norm": "-2",
    "O07_B01_Phi_norm": "-2",
    "O14_B01_Phi_Sigma_Sigmadag_cubic": "-4",
    "O20_B01_singlet_polynomial": "1",
    "O23_B01_singlet_polynomial": "1",
    "O27_B01_126bar_self_projectors": "2",
    "O27_B02_126bar_self_projectors": "2",
    "O27_B03_126bar_self_projectors": "1",
    "O27_B04_126bar_self_projectors": "2",
    "O35_B01_H_Sigma_hermitian": "1",
    "O35_B02_H_Sigma_hermitian": "-1",
    "O36_B01_H_self_quartics": "2",
    "O36_B02_H_self_quartics": "1",
    "O44_B01_Phi2_Sigma_projectors": "40",
    "O44_B02_Phi2_Sigma_projectors": "72",
    "O44_B03_Phi2_Sigma_projectors": "28",
    "O44_B04_Phi2_Sigma_projectors": "-8",
    "O44_B05_Phi2_Sigma_projectors": "-12",
    "O44_B06_Phi2_Sigma_projectors": "12",
    "O46_B01_Phi2_HdagH_channels": "3/5",
    "O46_B03_Phi2_HdagH_channels": "-1",
    "O48_B01_Phi_self_quartics": "-21/200",
    "O48_B02_Phi_self_quartics": "2467/28800",
    "O48_B03_Phi_self_quartics": "-77/3200",
    "O48_B04_Phi_self_quartics": "119/115200",
}


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sha(value: Any) -> str:
    return hashlib.sha256((canonical(value) + "\n").encode("ascii")).hexdigest()


def portable(path: Path) -> str:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


def safe_path(path: Path) -> Path | None:
    try:
        relative = path.resolve().relative_to(ROOT.resolve())
    except ValueError:
        return None
    current = ROOT
    for part in relative.parts:
        current = current / part
        if current.is_symlink() or (hasattr(current, "is_junction") and current.is_junction()):
            return None
    return path.resolve() if path.resolve().is_file() else None


def core_valid(value: dict[str, Any]) -> bool:
    body = dict(value)
    claimed = body.pop("core_sha256", None)
    return isinstance(claimed, str) and claimed == sha(body)


def source_manifest_valid(artifact: dict[str, Any]) -> bool:
    rows = artifact.get("source_manifest")
    if not isinstance(rows, list) or [row.get("path") for row in rows if isinstance(row, dict)] != list(EXPECTED_SOURCE_PATHS):
        return False
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"path", "mode", "sha256"} or row["mode"] != "portable-lf":
            return False
        path = safe_path(ROOT / row["path"])
        if path is None:
            return False
        observed = portable(path)
        if observed != row["sha256"]:
            return False
        if row["path"] in EXPECTED_PINS and observed != EXPECTED_PINS[row["path"]]:
            return False
    return True


def acceptance_valid(artifact: dict[str, Any]) -> bool:
    evidence = artifact.get("acceptance_evidence")
    if not isinstance(evidence, dict) or list(evidence) != ["A1", "A2", "A3", "A4"]:
        return False
    manifest = artifact.get("source_manifest")
    for index, criterion in enumerate(EXPECTED_CRITERIA, 1):
        row = evidence.get(f"A{index}")
        if not isinstance(row, dict) or set(row) != {"criterion", "passed", "artifacts"}:
            return False
        if row["criterion"] != criterion or row["passed"] is not True or row["artifacts"] != manifest:
            return False
    return True


def scientific_payload_valid(artifact: dict[str, Any]) -> dict[str, bool]:
    ledger = artifact.get("accepted_potential", {})
    sos = artifact.get("sum_of_squares", {})
    identities = artifact.get("invariant_identities", {})
    orbit = artifact.get("global_orbit", {})
    hessian = artifact.get("stationarity_and_Hessian", {})
    checks = artifact.get("checks", {})
    return {
        "complete_potential": bool(
            ledger.get("canonical_total_real_directions") == 891
            and ledger.get("degree_direction_counts") == {"2": 5, "3": 6, "4": 40, "5": 119, "6": 721}
            and ledger.get("degree_at_most_four_real_directions") == 51
            and ledger.get("zero_dimension_five_directions") == 119
            and ledger.get("zero_dimension_six_directions") == 721
            and ledger.get("nonzero_coefficients") == EXPECTED_COEFFICIENTS
        ),
        "exact_SOS": bool(
            sos.get("potential_identity") == "V=-1+sum_{a=1}^8 R_a with every R_a an exact squared norm"
            and sos.get("expanded_constant") == "3127/2500"
            and sos.get("residual_count") == 8
            and sos.get("coefficient_expansion_matches_exactly") is True
            and sos.get("global_lower_bound") == "V>=-1 on all 486 real fields"
            and all(row.get("nonnegative") is True for row in sos.get("terms", []))
        ),
        "invariant_zero_sets": bool(
            identities.get("Phi_quartic_exact_J_basis") == {"J0": "-21/200", "J2": "2467/28800", "J3": "-77/3200", "J4": "119/115200"}
            and identities.get("A_square_exact_weights") == ["40", "72", "28", "-8", "-12", "12"]
            and identities.get("A_square_exact_residuals") == ["0"] * 6
            and identities.get("Phi_Sigma_residual_Gram_diagonal") == [64, 32, 32, 24]
            and identities.get("H_Sigma_Fierz_identity") == "I1-I45=||i_H Sigma||^2"
        ),
        "exact_stationarity_Hessian": bool(
            hessian.get("field_dimension") == 486
            and hessian.get("nonzero_coefficient_count") == 28
            and hessian.get("exact_field_term_value") == "-5627/2500"
            and hessian.get("exact_constant") == "3127/2500"
            and hessian.get("exact_total_value") == "-1"
            and hessian.get("exact_gradient_nonzero_entries") == 0
            and hessian.get("modular_rank_prime") == 1009
            and hessian.get("modular_rank") == hessian.get("exact_rank") == 448
            and hessian.get("principal_minor_determinant_mod_prime") == 961
            and hessian.get("exact_nullity") == 38
            and hessian.get("gauge_orbit_rank") == 37
            and hessian.get("full_symmetry_orbit_rank") == 38
            and hessian.get("kernel_equals_full_symmetry_tangent_span") is True
            and hessian.get("all_448_non_symmetry_modes_strictly_positive") is True
            and hessian.get("intended_axion_direction_count") == 1
        ),
        "global_orbit": bool(
            orbit.get("exact_stabilizer_is_SU3C_plus_U1em") is True
            and orbit.get("gauge_dimension_identity") == "45+1-8-1=37"
            and orbit.get("broken_gauge_directions") == 37
            and orbit.get("zero_locus_parameter_dimensions", {}).get("total") == 38
            and orbit.get("all_global_minima_one_continuous_symmetry_orbit") is True
            and orbit.get("no_deeper_extremum") is True
            and orbit.get("no_disconnected_equal_minimum") is True
        ),
        "embedded_checks": bool(
            type(artifact.get("n_checks")) is int
            and artifact.get("n_checks") == len(checks) == 11
            and all(value is True for value in checks.values())
        ),
    }


def producer_replay_valid(artifact_core: str) -> bool:
    producer = safe_path(ROOT / EXPECTED_PRODUCER)
    if producer is None:
        return False
    environment = {key: value for key, value in os.environ.items() if key.upper() not in {"PYTHONPATH", "PYTHONHOME"}}
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            "-c",
            (
                "import runpy,sys;"
                "sys.path.insert(0,sys.argv[1]);"
                "sys.argv=[sys.argv[2],'--check'];"
                "runpy.run_path(sys.argv[0],run_name='__main__')"
            ),
            str(ROOT),
            str(producer),
        ],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    return bool(
        completed.returncode == 0
        and completed.stderr == ""
        and completed.stdout.splitlines() == [EXPECTED_STATUS, artifact_core]
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-artifact", required=True)
    parser.add_argument("--definition-sha256", required=True)
    parser.add_argument("--qualified-gate-id", required=True)
    parser.add_argument("--gate-definition-sha256", required=True)
    parser.add_argument("--dependencies-json", required=True)
    parser.add_argument("--acceptance-count", required=True, type=int)
    args = parser.parse_args()
    failures: list[str] = []
    path = safe_path(Path(args.verify_artifact))
    artifact: dict[str, Any] = {}
    if path is None or path.name != EXPECTED_ARTIFACT:
        failures.append("artifact_path_invalid")
    else:
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            artifact = loaded if isinstance(loaded, dict) else {}
        except (OSError, json.JSONDecodeError):
            failures.append("artifact_parse_failed")
    try:
        dependencies = json.loads(args.dependencies_json)
    except json.JSONDecodeError:
        dependencies = None
    shape = bool(
        artifact.get("schema") == EVIDENCE_SCHEMA
        and artifact.get("contract_namespace") == NAMESPACE
        and artifact.get("definition_sha256") == args.definition_sha256
        and artifact.get("model_contract_id") == MODEL
        and artifact.get("qualified_gate_id") == args.qualified_gate_id == G3_ID
        and artifact.get("dependencies") == dependencies == [G2_ID]
        and artifact.get("closure_complete") is True
        and type(artifact.get("n_failed")) is int
        and artifact.get("n_failed") == 0
        and artifact.get("failures") == []
        and artifact.get("producer") == EXPECTED_PRODUCER
        and artifact.get("status") == EXPECTED_STATUS
        and args.acceptance_count == 4
        and core_valid(artifact)
    )
    if not shape:
        failures.append("artifact_shape_or_core_invalid")
    if not source_manifest_valid(artifact):
        failures.append("source_manifest_invalid")
    if not acceptance_valid(artifact):
        failures.append("acceptance_evidence_invalid")
    scientific = scientific_payload_valid(artifact)
    failures.extend(key for key, value in scientific.items() if value is not True)
    artifact_core = artifact.get("core_sha256")
    if not isinstance(artifact_core, str) or not producer_replay_valid(artifact_core):
        failures.append("independent_source_replay_failed")
    results = {
        "A1": not failures and scientific["complete_potential"] and scientific["exact_stationarity_Hessian"],
        "A2": not failures and scientific["exact_stationarity_Hessian"] and scientific["global_orbit"],
        "A3": not failures and scientific["exact_SOS"] and scientific["exact_stationarity_Hessian"],
        "A4": not failures and scientific["exact_SOS"] and scientific["invariant_zero_sets"] and scientific["global_orbit"],
    }
    if not all(value is True for value in results.values()) and not failures:
        failures.append("acceptance_projection_failed")
    verifier_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    output: dict[str, Any] = {
        "schema": SCHEMA,
        "contract_namespace": NAMESPACE,
        "definition_sha256": args.definition_sha256,
        "qualified_gate_id": args.qualified_gate_id,
        "gate_definition_sha256": args.gate_definition_sha256,
        "dependencies": dependencies,
        "artifact_core_sha256": artifact_core,
        "verifier_sha256": verifier_sha,
        "acceptance_results": results,
        "all_acceptance_criteria_verified": not failures and all(value is True for value in results.values()),
        "n_failed": len(failures),
        "failures": failures,
    }
    output["verification_core_sha256"] = sha(output)
    sys.stdout.write(json.dumps(output, separators=(",", ":")))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
