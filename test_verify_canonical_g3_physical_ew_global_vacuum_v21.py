from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import canonical_g1_g8_gauged_u1x_v21 as contract
import verify_canonical_g3_physical_ew_global_vacuum_v21 as verifier


ROOT = Path(__file__).resolve().parent
ARTIFACT = ROOT / verifier.EXPECTED_ARTIFACT


def gate():
    return next(row for row in contract.GATES if row["qualified_gate_id"] == contract.G3_ID)


def invoke(path: Path):
    row = gate()
    return subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            str(ROOT / "verify_canonical_g3_physical_ew_global_vacuum_v21.py"),
            "--verify-artifact",
            str(path),
            "--definition-sha256",
            contract.DEFINITION_SHA256,
            "--qualified-gate-id",
            contract.G3_ID,
            "--gate-definition-sha256",
            contract._sha(row),
            "--dependencies-json",
            json.dumps(row["dependencies"], separators=(",", ":")),
            "--acceptance-count",
            str(len(row["acceptance"])),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=240,
        check=False,
    )


def canonical_sha(value):
    return hashlib.sha256(
        (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
    ).hexdigest()


def mutated_artifact(change):
    value = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    change(value)
    body = dict(value)
    body.pop("core_sha256", None)
    value["core_sha256"] = canonical_sha(body)
    directory = tempfile.TemporaryDirectory(dir=ROOT)
    path = Path(directory.name) / verifier.EXPECTED_ARTIFACT
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")
    return directory, path


def test_trusted_verifier_accepts_exact_live_artifact():
    completed = invoke(ARTIFACT)
    assert completed.returncode == 0, completed.stderr + completed.stdout
    assert completed.stderr == ""
    result = json.loads(completed.stdout)
    assert result["n_failed"] == 0
    assert result["all_acceptance_criteria_verified"] is True
    assert result["acceptance_results"] == {"A1": True, "A2": True, "A3": True, "A4": True}
    assert result["verifier_sha256"] == hashlib.sha256((ROOT / verifier.__file__).read_bytes()).hexdigest()


def test_forged_coefficient_is_rejected_even_with_recomputed_core():
    directory, path = mutated_artifact(
        lambda value: value["accepted_potential"]["nonzero_coefficients"].__setitem__(
            "O44_B04_Phi2_Sigma_projectors", "-7"
        )
    )
    try:
        completed = invoke(path)
        assert completed.returncode != 0
        assert "complete_potential" in json.loads(completed.stdout)["failures"]
    finally:
        directory.cleanup()


def test_forged_rank_is_rejected_even_with_recomputed_core():
    directory, path = mutated_artifact(
        lambda value: value["stationarity_and_Hessian"].__setitem__("exact_rank", 447)
    )
    try:
        completed = invoke(path)
        assert completed.returncode != 0
        assert "exact_stationarity_Hessian" in json.loads(completed.stdout)["failures"]
    finally:
        directory.cleanup()


def test_source_hash_mutation_is_rejected():
    directory, path = mutated_artifact(
        lambda value: value["source_manifest"][0].__setitem__("sha256", "0" * 64)
    )
    try:
        completed = invoke(path)
        assert completed.returncode != 0
        assert "source_manifest_invalid" in json.loads(completed.stdout)["failures"]
    finally:
        directory.cleanup()


def test_boolean_integer_alias_is_rejected():
    directory, path = mutated_artifact(lambda value: value.__setitem__("n_failed", False))
    try:
        completed = invoke(path)
        assert completed.returncode != 0
        assert "artifact_shape_or_core_invalid" in json.loads(completed.stdout)["failures"]
    finally:
        directory.cleanup()
