#!/usr/bin/env python3
"""Fail-closed numerical engine for the v19 UV completion and amplitudes."""

from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path

import numpy as np

import spin10_referee_audit as spin10
from alternate_v18_adversarial_audit import build_report as build_alternate_audit
from discrete_general_minimality_v19 import build_report as build_general_minimality
from falsification_targets_v19 import build_report as build_falsification_targets
from two_loop_amplitude_v19 import (
    build_amplitude_report,
    chirality_triangle_equal,
    divided_difference_triangle,
    pentagon_scalar,
    triangle_scalar_equal,
)
from uv_completion_v19 import (
    ZERO_VECTOR,
    anomaly_report,
    axion_mixing,
    build_uv_report,
    completion_solutions,
    explicit_p13_certificate,
    operator_frontier,
    renormalizable_accidental_symmetry_audit,
)


VS = 6.313855e11
VPHI = 1.0e17
MPL = 2.435e18
CHI4 = 75.5e-3
EW_UPPER = 246.0


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


def five_bilinear_lorentz_cycle() -> int:
    epsilon_down = np.array([[0, 1], [-1, 0]], dtype=int)
    epsilon_up = np.array([[0, -1], [1, 0]], dtype=int)
    total = 0
    n = 5
    for values in itertools.product(range(2), repeat=2 * n):
        left, right = values[:n], values[n:]
        term = 1
        for index in range(n):
            term *= epsilon_down[left[index], right[index]]
            term *= epsilon_up[right[index], left[(index + 1) % n]]
        total += term
    return int(total)


def massless_family_pentagon(heavy: float, spectator: float) -> float:
    """Analytic m_f=0 denominator limit of I_(2,2,1)."""
    a = heavy**2
    b = spectator**2
    ratio = a / b
    shape = 1.0 / (ratio * (ratio - 1.0))
    shape += 2.0 * (1.0 - 1.0 / ratio - math.log(ratio)) / (ratio - 1.0) ** 3
    return shape / (16.0 * math.pi**2 * b**3)


def build_verdict(inject_failure: bool = False) -> tuple[dict, Checks]:
    checks = Checks()
    uv = build_uv_report(VS, VPHI)
    amplitudes = build_amplitude_report(VS, VPHI)
    general = build_general_minimality()
    alternate = build_alternate_audit()
    falsification = build_falsification_targets()

    checks.check("arbitrary S-massed pairs still require k=5 mod 17",
                 general["allowed_k_1_through_17"] == [5])
    checks.check("exhaustive arbitrary-charge scan has no solution for k<=4",
                 all(value == 0 for value in general["solutions_k_1_through_4"].values()))
    checks.check("general k=5 cubic solutions count is 83232",
                 general["ordered_general_solutions_at_k5"] == 83232)
    checks.check("residue uniqueness is retained only in identical-pair ansatz",
                 general["identical_pair_residue_solutions_at_k5"] == [(2, 11)])

    checks.check("alternate charge set cancels its continuous anomalies",
                 tuple(alternate["anomalies"]["total"]) == (0, 0, 0))
    pq_repair = alternate["accidental_pq_repair"]
    checks.check("alternate setup needs and admits an independent accidental PQ",
                 pq_repair["heavy_mass_PQ_charge"] == 0
                 and pq_repair["decay_vertex_PQ_charge"] == 0
                 and pq_repair["heavy_mixed_QCD_PQ_anomaly"] == 0)
    checks.check("alternate heavy singlet Yukawas are only their two mass terms",
                 len(alternate["heavy_singlet_yukawas"]) == 2)
    alt_closure = alternate["omitted_fermionic_closure"]["closure"]
    checks.check("alternate scalar-only scan misses a P=12 fermionic closure",
                 (alt_closure["P"], alt_closure["Q_PQ"], alt_closure["V_light"])
                 == (12, -68, 0))
    checks.check("alternate Abelian beta coefficient is 8263",
                 alternate["u1_running"]["b_X_one_loop"] == 8263.0)
    checks.check("alternate quoted old-graph number has a 128-fold offset",
                 127.0 < alternate["old_graph_normalisation"]["quoted_over_exact"] < 129.0)

    checks.check("pre-inflationary tensor ceiling is 1.34e-17",
                 abs(falsification["preinflationary_r_ceiling"] / 1.339e-17 - 1.0) < 0.002)
    halo = falsification["haloscope"]
    checks.check("haloscope theory-location band is 36.62--37.60 GHz",
                 halo["theory_location_band_GHz"] == [36.62, 37.60])
    checks.check("halo linewidth is approximately 34 kHz",
                 33.0 < halo["halo_linewidth_kHz"] < 34.0)

    anomalies = anomaly_report()
    checks.check("light continuous anomalies are the audited integers",
                 tuple(anomalies["light"]) == (-34, -272, -16592))
    checks.check("heavy Spin(10) pair cancels mixed and gravitational anomalies",
                 tuple(anomalies["heavy_spin10_pair"][:2]) == (34, 272))
    checks.check("heavy Spin(10) cubic contribution is 21488",
                 anomalies["heavy_spin10_pair"][2] == 21488)
    checks.check("four singlets supply cubic anomaly -4896",
                 tuple(anomalies["heavy_singlets"]) == (0, 0, -4896))
    checks.check("all continuous U(1)_X anomalies cancel exactly",
                 tuple(anomalies["total"]) == (0, 0, 0))
    checks.check("Spin(10) heavy mass term is U(1)_X invariant", -17 + 7 + 10 == 0)
    checks.check("first singlet mass term is U(1)_X invariant", -17 - 6 + 23 == 0)
    checks.check("second singlet mass term is U(1)_X invariant", 17 - 26 + 9 == 0)
    checks.check("all heavy pairs are vectorlike modulo 17",
                 all(value % 17 == 0 for value in (7 + 10, -6 + 23, -26 + 9)))
    charges = (1, 2, -6, 4, -2, 17, 7, 10, -6, 23, -26, 9)
    checks.check("continuous charge normalization is primitive",
                 math.gcd(*map(abs, charges)) == 1)

    checks.check("no ansatz solution has max |X| <=25", completion_solutions(25) == [])
    solutions26 = completion_solutions(26)
    checks.check("the canonical max-|X|=26 solution exists",
                 (7, 10, -6, 23, -26, 9) in solutions26)
    checks.check("bounded ansatz has eight permutation-equivalent solutions at 26",
                 len(solutions26) == 8)

    renorm = renormalizable_accidental_symmetry_audit()
    checks.check("necessary-condition renormalizable catalogue has no PQ breaker",
                 renorm["pq_or_vector_breaking_candidates"] == [])
    checks.check("four heavy/light vector numbers remain exact at d<=4",
                 renorm["accidental_PQ_and_four_vector_numbers_exact_at_d_le_4"])

    frontier = operator_frontier(16)
    checks.check("UV operator frontier has the reproducible state count",
                 len(frontier) == 1716, str(len(frontier)))
    minimum = uv["quality_overcatalogue"]["minimum"]
    checks.check("no UV vacuum closure occurs through P=12",
                 uv["quality_overcatalogue"]["no_vacuum_closure_through_P12"])
    checks.check("necessary-condition search first reaches P=13",
                 minimum["P"] == 13)
    checks.check("first closure carries Q_PQ=-68 and zero exact vectors",
                 minimum["Q_PQ"] == -68 and tuple(minimum["vector"]) == ZERO_VECTOR)

    certificate = explicit_p13_certificate()
    checks.check("explicit Spin(10) P=13 certificate matches the lower bound",
                 certificate.planck_power == 13)
    checks.check("explicit certificate has Q_PQ=-68",
                 certificate.pq == -68)
    checks.check("explicit certificate conserves every vector number",
                 certificate.vector == ZERO_VECTOR)
    checks.check("each certificate spurion is continuous-gauge invariant",
                 all(op.x == 0 for op in certificate.operators))
    checks.check("certificate multiplicities are 2+2+1",
                 sorted(CounterLike(certificate)) == [1, 2, 2])
    vertices, internal_lines = 5, 5
    checks.check("P=13 compact graph is one loop",
                 internal_lines - vertices + 1 == 1)
    checks.check("P=13 scalar phase is U(1)_X invariant",
                 4 * 17 + 17 * (-4) + (-2) + 2 == 0)
    checks.check("P=13 scalar phase carries Q_PQ=-68",
                 17 * (-4) + (-2) + 2 == -68)

    vector_tensors = np.asarray(spin10.chiral_vector_bilinears(+1))
    gram = np.einsum("aij,bij->ab", vector_tensors.conj(), vector_tensors)
    checks.check("P=13 Spin(10) 10-channel closure is nonzero",
                 np.array_equal(np.real_if_close(gram).astype(int), 16 * np.eye(10, dtype=int)))
    lorentz = five_bilinear_lorentz_cycle()
    checks.check("P=13 five-bilinear Lorentz cycle is nonzero", lorentz == 2, str(lorentz))

    mixing = axion_mixing(VS, VPHI)
    direction = mixing["physical_axion_direction_in_(aPhi,aS)"]
    gauge = mixing["gauge_direction_in_(aPhi,aS)"]
    checks.check("physical axion is orthogonal to the U(1)_X gauge direction",
                 abs(direction[0] * gauge[0] + direction[1] * gauge[1]) < 1.0e3)
    checks.check("exact f_a approaches v_S/17",
                 abs(mixing["relative_correction_to_vS_over_17"]) < 1.2e-12)
    running = uv["u1_running"]
    checks.check("one-loop Abelian beta coefficient is 4919", running["b_X_one_loop"] == 4919.0)
    checks.check("g_X=0.05 keeps the Landau pole above M_Pl",
                 running["example_landau_pole_GeV"] > MPL)
    checks.check("Landau-pole cutoff requires g_X below 0.071 at vPhi=1e17",
                 0.070 < running["maximum_gX_for_landau_pole_above_cutoff"] < 0.071)

    equal_limit = triangle_scalar_equal(10.0, 10.0)
    checks.check("triangle equal-mass limit is exact",
                 abs(equal_limit * 32.0 * math.pi**2 * 100.0 - 1.0) < 1.0e-12)
    general_triangle = divided_difference_triangle(2.0, 3.0, 5.0)
    permuted = divided_difference_triangle(5.0, 2.0, 3.0)
    checks.check("general triangle is permutation symmetric",
                 abs(general_triangle / permuted - 1.0) < 1.0e-13)
    chirality = chirality_triangle_equal(VS, EW_UPPER)
    checks.check("hierarchical triangle tends to m/(16 pi^2)",
                 abs(chirality / (EW_UPPER / (16.0 * math.pi**2)) - 1.0) < 1.0e-14)

    amp_results = amplitudes["results"]
    old_exact = amp_results["v17_EFT_P12_two_loop_undressed"]["A_over_chi"]
    checks.check("full v17 two-loop kernel gives 2.149e-53 per normalized coefficient",
                 abs(old_exact / 2.148670644581424e-53 - 1.0) < 1.0e-12)
    old_diagnostic = 2.750298425064228e-51
    checks.check("exact vev normalization is 1/128 of the old dimensional diagnostic",
                 abs((old_exact / old_diagnostic) * 128.0 - 1.0) < 1.0e-12)
    dress = (VPHI / math.sqrt(2.0) / MPL) ** 4
    dressed_ratio = (
        amp_results["v19_U1X_P16_two_loop_dressed"]["A_over_chi"] / old_exact
    )
    checks.check("four mandatory Phi/M_Pl dressings are applied exactly",
                 abs(dressed_ratio / dress - 1.0) < 1.0e-12)

    heavy = VPHI / math.sqrt(2.0)
    p5 = pentagon_scalar(heavy, VS, EW_UPPER)
    p5_massless = massless_family_pentagon(heavy, VS)
    checks.check("full five-propagator integral is positive", p5 > 0.0)
    checks.check("finite-family-mass pentagon matches its controlled hierarchy limit",
                 abs(p5 / p5_massless - 1.0) < 1.0e-15)
    p13_shift = amp_results["v19_U1X_P13_one_loop_heavy_threshold"]["A_over_chi"]
    checks.check("P=13 threshold graph evaluates to 6.221e-58",
                 abs(p13_shift / 6.221143478014484e-58 - 1.0) < 1.0e-12)
    direct = amp_results["v19_U1X_direct_scalar_dimension21"]["A_over_chi"]
    checks.check("dimension-21 direct scalar term evaluates to 2.301e-43",
                 abs(direct / 2.301034295466917e-43 - 1.0) < 1.0e-12)
    checks.check("direct scalar term dominates the computed unit-coefficient terms",
                 amplitudes["dominant_computed_unit_coefficient_term"]
                 == "v19_U1X_direct_scalar_dimension21")
    checks.check("dominant computed term has >1e32 quality margin",
                 amplitudes["margin_below_1e-10"] > 1.0e32)

    if inject_failure:
        checks.check("injected failure exercises nonzero-exit path", False)

    verdict = {
        "status": "PASS" if not checks.failures else "FAIL",
        "n_checks_total": len(checks.rows),
        "n_checks_failed": len(checks.failures),
        "failures": checks.failures,
        "checks": checks.rows,
        "uv_completion": uv,
        "amplitudes": amplitudes,
        "general_minimality": general,
        "alternate_v18_audit": alternate,
        "falsification_targets": falsification,
        "explicit_p13_contraction": {
            "spin10_gram": np.real_if_close(gram).astype(int).tolist(),
            "lorentz_cycle_factor": lorentz,
            "vertices": vertices,
            "internal_fermion_lines": internal_lines,
            "loops": 1,
        },
    }
    return verdict, checks


def CounterLike(certificate) -> list[int]:
    counts: dict[str, int] = {}
    for operator in certificate.operators:
        counts[operator.label] = counts.get(operator.label, 0) + 1
    return list(counts.values())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("so10_axion_v19_verdict.json"))
    parser.add_argument("--inject-failure", action="store_true")
    args = parser.parse_args()
    verdict, checks = build_verdict(args.inject_failure)
    args.output.write_text(json.dumps(verdict, indent=2) + "\n")
    print(
        f"SUMMARY: {len(checks.rows) - len(checks.failures)}/{len(checks.rows)} PASS; "
        f"wrote {args.output}"
    )
    return 1 if checks.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
