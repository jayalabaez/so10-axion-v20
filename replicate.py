#!/usr/bin/env python3
"""One-command pristine replication of the v20 package.

Runs: golden-anchor checks → independent error audit → v20 engine →
unit tests → external next-step packages (flavour / thresholds / haloscope
forecast).  Exits nonzero on any failure.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
GOLDEN = ROOT / "golden" / "expected_anchors_v20.json"


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def check_golden_anchors() -> None:
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    # Live anomaly arithmetic (no package import of engines)
    light = (
        3 * 2 + 5 * 2 * (2 - 6),
        3 * 16 + 5 * 16 * (2 - 6),
        3 * 16 + 5 * 16 * (2**3 + (-6) ** 3),
    )
    charges = [tuple(x) for x in golden["minimality"]["canonical_charges"]]
    heavy = (
        2 * sum(x + y for x, y in charges),
        16 * sum(x + y for x, y in charges),
        16 * sum(x**3 + y**3 for x, y in charges),
    )
    total = tuple(a + b for a, b in zip(light, heavy))
    assert list(light) == golden["anomalies"]["light"], light
    assert list(heavy) == golden["anomalies"]["heavy"], heavy
    assert list(total) == golden["anomalies"]["total"], total
    assert 17**2 - 4 * 76 == golden["minimality"]["one_pair_discriminant"]
    print("[PASS] golden anomaly / minimality anchors", flush=True)


def main() -> int:
    print("=== v20 pristine replication ===", flush=True)
    check_golden_anchors()
    run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    run([sys.executable, "audit_v20_errors.py"])
    run([sys.executable, "so10_axion_v20_engine.py", "--output", "so10_axion_v20_verdict.json"])
    run([sys.executable, "-m", "unittest", "discover", "-v"])
    run([sys.executable, "falsify_v20.py"])
    run([sys.executable, "run_v20_external_next_steps.py"])
    run([sys.executable, "run_v20_referee_next.py"])
    run([sys.executable, "extensive_confirm_falsify_v20.py"])
    run([sys.executable, "next_physics_analysis_v20.py"])
    run([sys.executable, "literature_sweep_150uev_v20.py"])
    run([sys.executable, "home_public_37ghz_search_v20.py"])
    run([sys.executable, "gravitas_axion_v20_37ghz.py"])
    run([sys.executable, "public_data_indirect_audit_v20.py"])
    run([sys.executable, "full_fermion_matching_v20.py"])
    run([sys.executable, "tan_beta_profile_v20.py"])
    run([sys.executable, "reanalysis_portal_beta_v20.py"])
    print("=== REPLICATION PASS ===", flush=True)
    print(
        "Remember: passing tests means internal consistency of the candidate "
        "model, not experimental discovery of dark matter.",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
