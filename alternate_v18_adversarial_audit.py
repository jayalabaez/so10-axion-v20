#!/usr/bin/env python3
"""Adversarial audit of the alternate v18 files supplied for merging.

The anomaly arithmetic and general five-pair lower bound are retained.
The proposed gauged-``U(1)_PQ`` anomalon completion is not used in v19,
because its scalar-only quality scan misses a lower-cost fermionic closure,
its singlet anomalons have no listed renormalizable decay portal, and its
quoted old-graph amplitude retains the earlier 128-fold vev-normalisation
envelope instead of the exact factorised kernel.
"""

from __future__ import annotations

import itertools
import json
import math

from two_loop_amplitude_v19 import uv_dressed_two_loop_amplitude


MPL = 2.435e18
VS = 6.3139e11
VPHI_ALT = 9.9176e15
MS = VS
CHI = (75.5e-3) ** 4
MF_ALT = 0.50 * 246.0 / math.sqrt(2.0)


def anomaly_report() -> dict:
    light = (-34, -272, -16592)
    spin = (2 * (1 + 16), 16 * (1 + 16), 16 * (1**3 + 16**3))
    singlets = (
        0,
        sum((33, -16, 31, -48)),
        sum(q**3 for q in (33, -16, 31, -48)),
    )
    total = tuple(sum(row[index] for row in (light, spin, singlets)) for index in range(3))
    return {"light": light, "spin_pair": spin, "singlets": singlets, "total": total}


def repaired_accidental_pq_assignment() -> dict:
    """One explicit global-PQ assignment independent of the gauge charge."""
    pq = {"Phi": 0, "A_16": 1, "B_16bar": -1, "F": 1, "H": -2}
    return {
        "charges": pq,
        "heavy_mass_PQ_charge": pq["Phi"] + pq["A_16"] + pq["B_16bar"],
        "decay_vertex_PQ_charge": pq["A_16"] + pq["F"] + pq["H"],
        "heavy_mixed_QCD_PQ_anomaly": 2 * (pq["A_16"] + pq["B_16bar"]),
        "note": (
            "The physical global PQ must be stated separately from the gauged U(1); "
            "otherwise the named PQ Goldstone is gauge-eaten."
        ),
    }


def renormalizable_singlet_yukawas() -> list[tuple[str, str, str]]:
    """All gauge-invariant Yukawas made only from listed heavy singlets and singlet scalars."""
    fermions = {"n33": 33, "n-16": -16, "n31": 31, "n-48": -48}
    scalars = {"S": 4, "Sdag": -4, "Phi": 17, "Phidag": -17}
    allowed = []
    for (left, q_left), (right, q_right) in itertools.combinations_with_replacement(
        fermions.items(), 2
    ):
        for scalar, q_scalar in scalars.items():
            if q_left + q_right + q_scalar == 0:
                allowed.append((left, right, scalar))
    return sorted(allowed)


def fermionic_p12_certificate() -> dict:
    """A gauge-invariant lower-cost closure omitted by the scalar-only scan.

    Let B be the charge-16 heavy 16bar with accidental PQ charge -1.
    Both displayed operators are actual Spin(10) 10-channel invariants.
    Four O6 insertions plus O8 have P=12, Q_PQ=-68 and zero light-spectator
    number.  B-number is broken by the proposed renormalizable A-F-H decay
    vertex, so it cannot be imposed as an exact closure obstruction.  This
    is a nonzero-local-invariant and topology certificate; an end-to-end
    Grassmann evaluation of the alternate graph remains an external check.
    """
    o6 = {
        "operator": "(Sdag)^2 (B_16bar b_16bar)_10 10_H / M_Pl^2",
        "dimension": 6,
        "P": 2,
        "X": 2 * (-4) + 16 - 6 - 2,
        "Q_PQ": 2 * (-4) - 1 - 6 - 2,
        "V_light": -1,
    }
    o8 = {
        "operator": "(Sdag)^2 [(s_16 s_16)_10]^2 / M_Pl^4",
        "dimension": 8,
        "P": 4,
        "X": 2 * (-4) + 4 * 2,
        "Q_PQ": 2 * (-4) + 4 * 2,
        "V_light": 4,
    }
    closure = {
        "multiplicities": [4, 1],
        "P": 4 * o6["P"] + o8["P"],
        "Q_PQ": 4 * o6["Q_PQ"] + o8["Q_PQ"],
        "V_light": 4 * o6["V_light"] + o8["V_light"],
        "candidate_fermion_closure": (
            "four s-b mass propagators; four B-A mass propagators; four A-F-H "
            "vertices; four F legs paired by two F-F-H vertices"
        ),
        "loop_count": 2,
    }
    return {"O6": o6, "O8": o8, "closure": closure}


def abelian_running() -> dict:
    light_fermion_q2 = 3248
    heavy_spin_q2 = 16 * (1**2 + 16**2)
    singlet_q2 = sum(q**2 for q in (33, -16, 31, -48))
    scalar_q2 = 16 + 10 * 4 + 126 * 4 + 17**2
    fermion_q2 = light_fermion_q2 + heavy_spin_q2 + singlet_q2
    beta = (2.0 / 3.0) * fermion_q2 + (1.0 / 3.0) * scalar_q2
    g_max = math.sqrt(8.0 * math.pi**2 / (beta * math.log(MPL / VPHI_ALT)))
    return {
        "sum_Weyl_dimR_X2": fermion_q2,
        "sum_complex_scalar_dimR_X2": scalar_q2,
        "b_X_one_loop": beta,
        "gX_max_for_Landau_pole_above_MPl": g_max,
    }


def old_graph_normalisation() -> dict:
    exact = uv_dressed_two_loop_amplitude(VS, VPHI_ALT, MS, MF_ALT, MF_ALT) / CHI
    quoted = 2.37e-62
    return {
        "exact_factorised_A_over_chi": exact,
        "alternate_quoted_A_over_chi": quoted,
        "quoted_over_exact": quoted / exact,
        "diagnosis": (
            "the quoted result is the older dimensional envelope; the exact vev-normalised "
            "factorised graph is smaller by approximately 128"
        ),
    }


def build_report() -> dict:
    masses_only = renormalizable_singlet_yukawas()
    return {
        "decision": "partial merge only",
        "accepted": [
            "exact continuous anomaly arithmetic for the alternate charge set",
            "charge-independent k=5 lower bound",
            "search band and conditional falsification framing, with programme status softened",
        ],
        "not_accepted": [
            "the scalar-only dimension-21 quality theorem",
            "the claim that every anomalon has a renormalizable decay",
            "the quoted quantity as the full two-loop amplitude",
        ],
        "anomalies": anomaly_report(),
        "accidental_pq_repair": repaired_accidental_pq_assignment(),
        "heavy_singlet_yukawas": masses_only,
        "heavy_singlet_result": (
            "only the two Phi mass terms occur; no renormalizable portal to light matter exists "
            "in the listed field content"
        ),
        "omitted_fermionic_closure": fermionic_p12_certificate(),
        "u1_running": abelian_running(),
        "old_graph_normalisation": old_graph_normalisation(),
    }


if __name__ == "__main__":
    print(json.dumps(build_report(), indent=2))
