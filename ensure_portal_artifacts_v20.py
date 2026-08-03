#!/usr/bin/env python3
"""Ensure portal / orientation verdict artifacts exist before dependent audits.

CI historically failed when ``unittest discover`` ran ``test_close_open_gaps``
before any step had written
``PORTAL_FULL_COMPLEX_ORIENTATION_SPHERE_V20_VERDICT.json``.  This helper
materializes the required upstream verdicts in a fixed order so audits and
tests are order-independent.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent

# Writers must be ordered so dependents can read previously written files.
_WRITERS: list[tuple[str, str]] = [
    ("channel_fcnc_rates_v20", "CHANNEL_FCNC_RATES_V20_VERDICT.json"),
    ("na62_pointwise_limit_v20", "NA62_POINTWISE_LIMIT_V20_VERDICT.json"),
    ("twist_massless_limit_v20", "TWIST_MASSLESS_LIMIT_V20_VERDICT.json"),
    ("portal_constraint_ray_v20", "PORTAL_CONSTRAINT_RAY_V20_VERDICT.json"),
    ("portal_boundary_heavy_spectrum_v20", "PORTAL_BOUNDARY_HEAVY_SPECTRUM_V20_VERDICT.json"),
    ("portal_family_orientation_map_v20", "PORTAL_FAMILY_ORIENTATION_MAP_V20_VERDICT.json"),
    ("portal_full_complex_orientation_sphere_v20", "PORTAL_FULL_COMPLEX_ORIENTATION_SPHERE_V20_VERDICT.json"),
]


def _import_builder(module_name: str) -> Callable[[], dict[str, Any]]:
    module = __import__(module_name)
    return module.build_report


def ensure_portal_artifacts(*, force: bool = False, root: Path = ROOT) -> dict[str, Any]:
    """Write missing (or all, if force) portal verdict JSON artifacts."""
    written: list[str] = []
    skipped: list[str] = []
    for module_name, filename in _WRITERS:
        path = root / filename
        if path.exists() and not force:
            skipped.append(filename)
            continue
        report = _import_builder(module_name)()
        path.write_text(
            json.dumps(report, indent=2, default=str) + "\n",
            encoding="utf-8",
        )
        written.append(filename)
    sphere = root / "PORTAL_FULL_COMPLEX_ORIENTATION_SPHERE_V20_VERDICT.json"
    return {
        "status": "PORTAL_ARTIFACTS_ENSURED",
        "n_written": len(written),
        "n_skipped": len(skipped),
        "written": written,
        "skipped": skipped,
        "sphere_present": sphere.exists(),
        "sphere_path": str(sphere),
    }


def main() -> int:
    report = ensure_portal_artifacts(force=False)
    print(json.dumps(report, indent=2))
    return 0 if report["sphere_present"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
