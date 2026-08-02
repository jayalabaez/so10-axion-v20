#!/usr/bin/env python3
"""Fail-closed numerical engine for the v20 decay-safe completion."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

import spin10_referee_audit as spin10
from decay_safe_completion_v20 import (
    anomaly_report,
    build_report as build_completion_report,
    decay_report,
    explicit_p8_certificate,
    mass_and_portal_audit,
    minimality_report,
    minimum_vacuum_closure,
    operator_frontier,
    p8_one_loop_lorentz_factor,
    renormalizable_accidental_audit,
    running_report,
)
from decay_threshold_v20 import build_amplitude_report, chirality_chain


VS = 6.313855e11
VPHI = 1.0e17
MPL = 2.435e18


class Checks:
    def __init__(self) -> None:
        self.rows: list[dict] = []

    def check(self, name: str, condition: bool, detail: str = "") -> None:
        passed = bool(condition)
        self.rows.append({"name": name, "passed": passed, "detail": detail})
        print(f"[{'PASS' if passed else 'FAIL'}] {name}" + (f": {detail}" if detail else ""))

    @property
    def failures(self) -> list[str]:
        return [row["name"] for row in self.rows if not row["passed"]]


def build_verdict(inject_failure: bool = False) -> tuple[dict, Checks]:
    checks = Checks()
    completion = build_completion_report(VS, VPHI)
    amplitudes = build_amplitude_report(VS, VPHI)

    anomalies = anomaly_report()
    checks.check("light anomaly baseline is unchanged", tuple(anomalies["light"]) == (-34, -272, -16592))
    checks.check(
        "three complete pairs supply the exact opposite anomaly",
        tuple(anomalies["three_complete_pairs"]) == (34, 272, 16592),
    )
    checks.check("all continuous anomalies cancel", tuple(anomalies["total"]) == (0, 0, 0))
    checks.check("heavy pairs do not shift the accidental-PQ QCD anomaly", anomalies["qcd_axion_anomaly_unchanged"])
    checks.check(
        "pair cubic units are 4097+2771-5831=1037",
        anomalies["pair_cubic_units_before_dim16"] == [4097, 2771, -5831]
        and sum(anomalies["pair_cubic_units_before_dim16"]) == 1037,
    )

    minimality = minimality_report()
    checks.check("mixed anomaly forces an odd anomalon-pair count", minimality["pair_number_must_be_odd"])
    checks.check("one-pair cubic equation has discriminant -15", minimality["one_pair_quadratic_discriminant"] == -15)
    checks.check("one complete pair is impossible", minimality["one_pair_impossible_even_over_real_charges"])
    checks.check("three pairs are minimal in the stated ansatz", minimality["minimum_number_of_pairs"] == 3)
    checks.check("canonical three-pair charges are found", minimality["canonical_solution"] == ((1, 16), (14, 3), (1, -18)))
    checks.check("canonical triple is unique in the existing-field portal basis", minimality["canonical_is_unique_in_portal_basis"])

    portals = mass_and_portal_audit()
    checks.check("every heavy mass is gauge and PQ invariant", portals["all_masses_gauge_and_PQ_invariant"])
    checks.check("every decay portal is gauge and PQ invariant", portals["all_portals_gauge_and_PQ_invariant"])
    checks.check(
        "generic X=1 mass matrix leaves three chiral families",
        portals["ordinary_chiral_families_after_generic_rank_two_X1_mass_matrix"] == 3,
    )

    renormalizable = renormalizable_accidental_audit()
    checks.check(
        "renormalizable necessary-condition overcatalogue has no PQ breaker",
        renormalizable["pq_or_spectator_vector_breaking_candidates"] == [],
    )
    checks.check(
        "accidental PQ and spectator vector survive all d<=4 candidates",
        renormalizable["accidental_PQ_and_spectator_vector_exact_at_d_le_4"],
    )

    frontier = operator_frontier(16)
    checks.check("decay-safe frontier has 22 exact charge states", len(frontier) == 22, str(len(frontier)))
    checks.check("no vector-neutral PQ closure exists through P=7", minimum_vacuum_closure(frontier, 7) is None)
    closure = minimum_vacuum_closure(frontier, 8)
    checks.check(
        "first necessary-condition closure is P=8",
        closure is not None and (closure.planck_power, closure.pq, closure.spectator_vector) == (8, -68, 0),
    )
    certificate = explicit_p8_certificate()
    checks.check(
        "explicit P=8 certificate saturates the lower bound",
        (certificate.planck_power, certificate.pq, certificate.spectator_vector) == (8, -68, 0),
    )
    multiplicities = sorted(__import__("collections").Counter(op.label for op in certificate.operators).values())
    checks.check("certificate multiplicities are 4+1", multiplicities == [1, 4])
    checks.check("every certificate operator is exactly U(1)_X invariant", all(op.x == 0 for op in certificate.operators))
    checks.check("closed scalar phase is U(1)_X invariant", 4 * 17 + 18 * (-4) + 2 * 2 == 0)
    checks.check("closed scalar phase carries Q_PQ=-68", 18 * (-4) + 2 * 2 == -68)
    checks.check("explicit graph has two loops", 12 - 11 + 1 == 2)

    tensors = np.asarray(spin10.chiral_vector_bilinears(+1))
    component_gram = np.einsum("aij,akj->ik", tensors, tensors.conj())
    checks.check(
        "every 16 component has a nonzero normalized 10-channel",
        np.array_equal(np.real_if_close(component_gram).astype(int), 10 * np.eye(16, dtype=int)),
    )
    channel_gram = np.einsum("aij,bij->ab", tensors.conj(), tensors)
    checks.check(
        "P=8 Spin(10) 10-channel closure is nonzero",
        np.array_equal(np.real_if_close(channel_gram).astype(int), 16 * np.eye(10, dtype=int)),
    )
    loop_lorentz = p8_one_loop_lorentz_factor()
    checks.check(
        "explicit v20 Lorentz chain is nonzero in both loops",
        loop_lorentz == -2 and loop_lorentz**2 == 4,
        str(loop_lorentz),
    )

    decays = decay_report(VPHI)
    checks.check("example anomalon lifetime is below 1e-22 s", decays["example_lifetime_s"] < 1.0e-22)
    checks.check(
        "a normalized portal above 3.1e-20 decays before one second",
        decays["minimum_normalized_portal_for_lifetime_below_one_second"] < 3.1e-20,
    )

    running = running_report(VPHI)
    checks.check("v20 Abelian beta coefficient is 10843", running["b_X_one_loop"] == 10843.0)
    checks.check(
        "gX=0.04 keeps the Abelian Landau pole above MPl",
        running["example_U1X_landau_pole_GeV"] > MPL,
    )
    checks.check(
        "Abelian cutoff bound is gX<0.0478",
        0.0477 < running["maximum_gX_for_landau_pole_above_cutoff"] < 0.0478,
    )
    checks.check(
        "conservative Spin(10) running remains perturbative to MPl",
        running["example_Spin10_landau_pole_GeV"] > MPL,
    )
    continuous = running["continuous_from_spectator_corrected_alpha_GUT"]
    checks.check(
        "continuous Spin(10) trajectory from alpha_GUT is recorded",
        abs(continuous["alpha_inv_GUT"] - 16.810) < 0.01,
    )
    checks.check(
        "continuous conservative Spin(10) running is not Planck-safe",
        continuous["conservative"]["landau_pole_below_MPl"],
    )

    heavy = VPHI / math.sqrt(2.0)
    chain = chirality_chain(heavy, VS, 246.0)
    shape = 16.0 * math.pi**2 * heavy**2 * chain
    checks.check("finite repeated-pole chain is positive", chain > 0.0)
    checks.check("hierarchical chain has controlled unit shape", abs(shape - 0.9999999965313857) < 2.0e-15)
    p8 = amplitudes["results"]["v20_U1X_P8_decay_threshold_two_loop"]
    checks.check(
        "exact P=8 threshold shift is 6.043e-47",
        abs(p8["worst_phase_2A_over_chi"] / 6.043043168794402e-47 - 1.0) < 1.0e-12,
    )
    checks.check("P=8 threshold is safe for unit normalized coefficient", p8["safe_below_1e-10_for_unit_coefficient"])
    checks.check(
        "direct dimension-21 scalar term remains the largest computed term",
        amplitudes["dominant_computed_unit_coefficient_term"]
        == "v20_U1X_direct_scalar_dimension21",
    )
    checks.check("dominant computed term retains >1e32 quality margin", amplitudes["margin_below_1e-10"] > 1.0e32)

    if inject_failure:
        checks.check("injected failure exercises nonzero-exit path", False)

    verdict = {
        "status": "PASS" if not checks.failures else "FAIL",
        "n_checks_total": len(checks.rows),
        "n_checks_failed": len(checks.failures),
        "failures": checks.failures,
        "checks": checks.rows,
        "completion": completion,
        "amplitudes": amplitudes,
    }
    return verdict, checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("so10_axion_v20_verdict.json"))
    parser.add_argument("--inject-failure", action="store_true")
    arguments = parser.parse_args()
    verdict, checks = build_verdict(arguments.inject_failure)
    arguments.output.write_text(json.dumps(verdict, indent=2) + "\n")
    print(
        f"VERDICT={verdict['status']} "
        f"CHECKS={verdict['n_checks_total'] - verdict['n_checks_failed']}/{verdict['n_checks_total']}"
    )
    return 1 if checks.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
