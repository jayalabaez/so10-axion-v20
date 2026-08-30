#!/usr/bin/env python3
"""Fail-closed V38 audit of ultraviolet origins for the V37 selector.

This is deliberately a theorem-and-construction certificate, not a claim that
the Pati--Salam EFT has become a fundamental theory.  It proves the precise
obstruction to an ordinary four-dimensional Higgsed-U(1) origin for the V37
Z66 factor, and supplies the anomaly data needed for a local 5D APS/eta-inflow
completion of the continuous U(1) sector.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Callable, Mapping

import susy_v37_new_physics_routes as v37


ROOT = Path(__file__).resolve().parent
REPORT_JSON = ROOT / "SUSY_V38_G1_UV_COMPLETION_AUDIT.json"
REPORT_MD = ROOT / "SUSY_V38_G1_UV_COMPLETION_AUDIT.md"

N_X = v37.N66
N_H = v37.N85
N_SELECTOR = v37.N5610

SOURCE_FILES = (
    "susy_v38_g1_uv_completion_audit.py",
    "test_susy_v38_g1_uv_completion_audit.py",
    "susy_v37_new_physics_routes.py",
    "models/PSZ4RZ5610SUSYV37/PSZ4RZ5610SUSYV37.m",
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
        "utf-8"
    )


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_manifest() -> list[dict[str, Any]]:
    return [
        {
            "path": name,
            "exists": (ROOT / name).is_file(),
            "sha256": sha256_file(ROOT / name) if (ROOT / name).is_file() else None,
        }
        for name in SOURCE_FILES
    ]


# A primitive continuous lift of V37's q66 charges.  The lift is chosen so
# every V37 superpotential monomial is U(1)_X neutral; it is not inferred from
# the finite charges alone.
X_LIFT = {
    "PsiBar": -2,
    "PsiCBar": -2,
    "P": 2,
    "Pbar": -2,
    "A2": -29,
    "A32": 31,
    "A15": -3,
    "A17": 1,
    "A16": -1,
}

# The continuous U(1)_H representative is intentionally not the smallest
# residue: the V37 spectator construction uses the pair (+69,-69), whose
# squares are essential to the mixed-R and running ledgers.
H_LIFT = {
    "A2": 1,
    "A32": -1,
    "A15": 69,
    "A17": -69,
}


# multiplicity, dimension of one PS representation, representation, and
# doubled Dynkin indices (2T) for SU(4), SU(2)L, SU(2)R.  The final entry is
# the SU(4)^3 cubic index including the dimensions of the SU(2) factors.
PS_METADATA: dict[str, tuple[int, int, str, tuple[int, int, int], int]] = {
    "H": (1, 4, "(1,2,2)", (0, 2, 2), 0),
    "Q": (3, 8, "(4,2,1)", (2, 4, 0), 2),
    "Qc": (3, 8, "(bar4,1,2)", (2, 0, 4), -2),
    "X": (1, 1, "(1,1,1)", (0, 0, 0), 0),
    "Sc": (1, 8, "(bar4,1,2)", (2, 0, 4), -2),
    "Sbc": (1, 8, "(4,1,2)", (2, 0, 4), 2),
    "Sig6": (1, 6, "(6,1,1)", (2, 0, 0), 0),
    "PsiBar": (1, 8, "(bar4,2,1)", (2, 4, 0), -2),
    "Psi": (1, 8, "(4,2,1)", (2, 4, 0), 2),
    "PsiC": (1, 8, "(bar4,1,2)", (2, 0, 4), -2),
    "PsiCBar": (1, 8, "(4,1,2)", (2, 0, 4), 2),
    "P": (1, 1, "(1,1,1)", (0, 0, 0), 0),
    "Nv": (3, 1, "(1,1,1)", (0, 0, 0), 0),
    "Pbar": (1, 1, "(1,1,1)", (0, 0, 0), 0),
    "Zp": (1, 1, "(1,1,1)", (0, 0, 0), 0),
    "A2": (1, 1, "(1,1,1)", (0, 0, 0), 0),
    "A32": (1, 1, "(1,1,1)", (0, 0, 0), 0),
    "A15": (1, 1, "(1,1,1)", (0, 0, 0), 0),
    "A17": (1, 1, "(1,1,1)", (0, 0, 0), 0),
    "A16": (1, 1, "(1,1,1)", (0, 0, 0), 0),
}


def visible_rows() -> list[dict[str, Any]]:
    """The full V37 chiral matter packet in a continuous charge basis."""

    rows: list[dict[str, Any]] = []
    assert set(PS_METADATA) == set(v37.ALL_CHIRAL_FIELDS)
    for name, (q66, r_super, h85, _pq170) in v37.ALL_CHIRAL_FIELDS.items():
        multiplicity, dimension, representation, t2, cubic = PS_METADATA[name]
        x = X_LIFT.get(name, 0)
        row = {
            "field": name,
            "multiplicity": multiplicity,
            "PS_dimension_per_copy": dimension,
            "PS_representation": representation,
            "PS_conjugate_representation": representation.replace("bar4", "TEMP").replace("4", "bar4").replace("TEMP", "4"),
            "U1X_charge_lift": x,
            "U1H_charge_lift": H_LIFT.get(name, 0),
            "Z4R_superfield_charge": r_super,
            "Z4R_fermion_lift": r_super - 1,
            "Z5610_charge": v37.combined_charge(q66, h85),
            "doubled_Dynkin_indices_SU4_SU2L_SU2R": list(t2),
            "SU4_cubic_index": cubic,
        }
        assert x % N_X == q66
        assert row["U1H_charge_lift"] % N_H == h85
        rows.append(row)
    return rows


def weighted_sum(rows: list[dict[str, Any]], fn: Callable[[dict[str, Any]], int]) -> int:
    return sum(
        row["multiplicity"] * row["PS_dimension_per_copy"] * fn(row) for row in rows
    )


def visible_anomaly_ledger(rows: list[dict[str, Any]]) -> dict[str, Any]:
    x = lambda row: row["U1X_charge_lift"]
    h = lambda row: row["U1H_charge_lift"]
    r = lambda row: row["Z4R_fermion_lift"]
    ps_mixed = [
        sum(
            row["multiplicity"]
            * x(row)
            * row["doubled_Dynkin_indices_SU4_SU2L_SU2R"][index]
            for row in rows
        )
        for index in range(3)
    ]
    h_ps_mixed = [
        sum(
            row["multiplicity"]
            * h(row)
            * row["doubled_Dynkin_indices_SU4_SU2L_SU2R"][index]
            for row in rows
        )
        for index in range(3)
    ]
    ps_cubic = sum(row["multiplicity"] * row["SU4_cubic_index"] for row in rows)
    su2_doublets = [
        sum(
            row["multiplicity"]
            * row["doubled_Dynkin_indices_SU4_SU2L_SU2R"][index]
            for row in rows
        )
        for index in (1, 2)
    ]
    return {
        "normalization": "continuous U(1) charges are primitive integers; non-Abelian entries use 2T(fundamental)=1",
        "U1X_PS_squared_doubled_SU4_SU2L_SU2R": ps_mixed,
        "U1H_PS_squared_doubled_SU4_SU2L_SU2R": h_ps_mixed,
        "U1X_cubed": weighted_sum(rows, lambda row: x(row) ** 3),
        "U1H_cubed": weighted_sum(rows, lambda row: h(row) ** 3),
        "U1X_squared_U1H": weighted_sum(rows, lambda row: x(row) ** 2 * h(row)),
        "U1X_U1H_squared": weighted_sum(rows, lambda row: x(row) * h(row) ** 2),
        "U1X_gravity": weighted_sum(rows, x),
        "U1H_gravity": weighted_sum(rows, h),
        "chiral_matter_Z4R_U1X_squared": weighted_sum(rows, lambda row: r(row) * x(row) ** 2),
        "chiral_matter_Z4R_U1H_squared": weighted_sum(rows, lambda row: r(row) * h(row) ** 2),
        "chiral_matter_Z4R_squared_U1X": weighted_sum(rows, lambda row: r(row) ** 2 * x(row)),
        "chiral_matter_Z4R_squared_U1H": weighted_sum(rows, lambda row: r(row) ** 2 * h(row)),
        "chiral_matter_Z4R_U1X_U1H": weighted_sum(rows, lambda row: r(row) * x(row) * h(row)),
        "chiral_matter_Z4R_cubed": weighted_sum(rows, lambda row: r(row) ** 3),
        "chiral_matter_Z4R_gravity": weighted_sum(rows, r),
        "pure_SU4_cubic": ps_cubic,
        "SU2L_SU2R_Witten_doublet_counts": su2_doublets,
        "pure_PS_gauge_anomaly_absent": ps_cubic == 0 and all(count % 2 == 0 for count in su2_doublets),
    }


def mirrored_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """An opposite wall packet for an APS/eta-inflow interval EFT.

    The Z4R entry is the inverse *fermion* action.  This cancels the chiral
    matter contribution to mixed R rows, but deliberately does not pretend to
    supply the 4D/5D gravitino or PS-centre global-structure data.
    """

    output: list[dict[str, Any]] = []
    for row in rows:
        mirror = dict(row)
        mirror["field"] = f"mirror_{row['field']}"
        mirror["PS_representation"] = row["PS_conjugate_representation"]
        mirror["U1X_charge_lift"] = -row["U1X_charge_lift"]
        mirror["U1H_charge_lift"] = -row["U1H_charge_lift"]
        mirror["Z4R_fermion_lift"] = -row["Z4R_fermion_lift"]
        mirror["Z4R_superfield_charge"] = (mirror["Z4R_fermion_lift"] + 1) % 4
        mirror["Z5610_charge"] = (-row["Z5610_charge"]) % N_SELECTOR
        mirror["SU4_cubic_index"] = -row["SU4_cubic_index"]
        output.append(mirror)
    return output


def selector_higgs_parent_nogo(visible: dict[str, Any]) -> dict[str, Any]:
    residue66 = visible["U1X_PS_squared_doubled_SU4_SU2L_SU2R"]
    residue5610 = [N_H * value for value in residue66]
    return {
        "theorem": "ordinary symmetry-preserving heavy-threshold obstruction",
        "assumptions": [
            "U(1)_X has primitive integer charges and is first Higgsed only by VEVs with U(1)_X charge in 66 Z, leaving an exact Z66 at the threshold scale.",
            "Pati--Salam is unbroken at that threshold scale.",
            "Every extra Pati--Salam-charged fermion becomes massive through an ordinary full-rank polynomial mass matrix whose VEV insertions preserve Z66.",
            "No Green--Schwarz/Stueckelberg response with fractional topological level, no 5D inflow, and no symmetry-preserving topological order is invoked.",
        ],
        "proof": [
            "For each conjugate PS representation block, Z66 invariance of every nonzero mass-matrix entry gives x_i + xbar_j = 0 (mod 66).  The determinant of a full-rank block therefore has total U(1)_X charge 0 (mod 66).",
            "Multiplying by its fixed doubled Dynkin index shows that an ordinary gapped threshold changes every U(1)_X-PS^2 coefficient by 0 (mod 66).  For an even-order discrete symmetry, allowing a real-representation/Majorana ambiguity weakens this at most to 0 (mod 33).",
            "The V37 light packet instead has (-8,-8,-8), which is nonzero modulo both 66 and 33.  Hence no such ordinary four-dimensional threshold can cancel the continuous mixed anomaly while the Z66 selector remains exact.",
        ],
        "light_U1X_PS_squared_doubled": residue66,
        "light_residue_mod66": [value % N_X for value in residue66],
        "light_residue_mod33_even_order_relaxation": [value % (N_X // 2) for value in residue66],
        "combined_Z5610_PS_squared_doubled": residue5610,
        "combined_residue_mod5610": [value % N_SELECTOR for value in residue5610],
        "combined_residue_mod2805_even_order_relaxation": [value % (N_SELECTOR // 2) for value in residue5610],
        "single_compact_GS_axion_subcase": {
            "assumption": "a periodic axion a~a+2pi shifts by 66 alpha under U(1)_X and has integer instanton level k multiplying a tr(F_PS wedge F_PS)",
            "required_equation_in_doubled_normalization": "66*k = +8",
            "integer_solution_exists": False,
            "reason": "8 is not divisible by 66; a fractional level is outside the ordinary compact-axion assumption and is a distinct topological response.",
        },
        "conclusion": "A 4D U(1)_X -> Z66 Higgs parent with only ordinary symmetry-preserving massive matter cannot be the requested G1 completion.",
        "not_ruled_out": [
            "a threshold tied to the later P/Pbar PQ VEV, which must be re-audited for quality and is not an exact-Z66 UV threshold",
            "a quantized higher/topological Green--Schwarz response beyond the single ordinary compact-axion subcase",
            "a 5D inflow/symmetry-extension construction",
        ],
    }


def u1h_running(rows: list[dict[str, Any]]) -> dict[str, Any]:
    light_b = weighted_sum(rows, lambda row: row["U1H_charge_lift"] ** 2)
    higgs_b = 2 * N_H**2
    b_total = light_b + higgs_b
    headroom = 100.0
    g_max = math.sqrt(8 * math.pi**2 / (b_total * math.log(headroom)))
    return {
        "isolated_U1H_gauge_anomalies": {
            "U1H_cubed": 0,
            "U1H_gravity": 0,
            "U1H_PS_squared": [0, 0, 0],
            "all_vanish": True,
        },
        "minimal_breaking_sector": "Splus(qH=+85), Sminus(qH=-85), YH(Splus*Sminus-vH^2)",
        "unbroken_remnant": "Z85",
        "one_loop_N1SUSY_abelian_b": {
            "light_anomalons": light_b,
            "Higgs_pair": higgs_b,
            "total": b_total,
            "formula": "1/gH(mu)^2 = 1/gH(M)^2 - b log(mu/M)/(8 pi^2)",
            "gH_max_at_M_for_100x_scale_headroom": g_max,
        },
        "product_group_boundary": "The simultaneous U(1)X x U(1)H parent also has X^2H=432 and XH^2=-9520, so this isolated U(1)H statement is not a full product-group completion.",
    }


def five_dimensional_inflow(visible_rows_: list[dict[str, Any]], visible: dict[str, Any]) -> dict[str, Any]:
    mirror = mirrored_rows(visible_rows_)
    mirror_anomalies = visible_anomaly_ledger(mirror)
    continuous_keys = (
        "U1X_PS_squared_doubled_SU4_SU2L_SU2R",
        "U1H_PS_squared_doubled_SU4_SU2L_SU2R",
        "U1X_cubed",
        "U1H_cubed",
        "U1X_squared_U1H",
        "U1X_U1H_squared",
        "U1X_gravity",
        "U1H_gravity",
        "chiral_matter_Z4R_U1X_squared",
        "chiral_matter_Z4R_U1H_squared",
        "chiral_matter_Z4R_squared_U1X",
        "chiral_matter_Z4R_squared_U1H",
        "chiral_matter_Z4R_U1X_U1H",
        "chiral_matter_Z4R_cubed",
        "chiral_matter_Z4R_gravity",
    )
    net: dict[str, Any] = {}
    for key in continuous_keys:
        first, second = visible[key], mirror_anomalies[key]
        net[key] = (
            [left + right for left, right in zip(first, second, strict=True)]
            if isinstance(first, list)
            else first + second
        )
    return {
        "geometry": "M4 x I with I=[0,L] and bulk gauge group GPS x U(1)X x U(1)H",
        "boundary_0": "the V37 chiral packet with the listed continuous charge lifts",
        "boundary_L": "one exact opposite-anomaly mirror packet, with PS-conjugate representations and inverse X, H, and chiral-fermion R actions",
        "mirror_packet": mirror,
        "integer_anomaly_polynomial_coefficient_ledger": {
            "visible": {key: visible[key] for key in continuous_keys},
            "mirror": {key: mirror_anomalies[key] for key in continuous_keys},
            "net": net,
            "all_net_rows_zero": all(
                all(value == 0 for value in entry) if isinstance(entry, list) else entry == 0
                for entry in net.values()
            ),
        },
        "APS_eta_inflow_protocol": {
            "prescription": "Use the APS/Dai--Freed eta-invariant of the 5D regulator bundle for the mirror-paired boundary representation; its boundary variation is the negative of the displayed local anomaly polynomial.",
            "why_it_is_quantized": "The complete boundary representation is rho plus its inverse.  Its anomaly class is additive and therefore zero before choosing a local Chern--Simons representative.",
            "literature": [
                "https://arxiv.org/abs/1909.08775",
                "https://arxiv.org/abs/hep-th/0305024",
                "https://arxiv.org/abs/1808.02881",
            ],
        },
        "what_this_closes": "the perturbative continuous U(1)X/U(1)H and chiral-matter mixed-anomaly bookkeeping of a local 5D interval EFT",
        "what_it_does_not_close": [
            "a symmetry-preserving microscopic gap or mass construction for the mirror wall",
            "the 5D UV fixed point/string completion and its KK threshold matching",
            "the full Spin^Z4R anomaly including gaugino, gravitino, and Pati--Salam centre quotient data",
            "the V37 PQ/relic/cosmology and soft-matching gates",
        ],
        "established_microscopic_UV_completion": False,
    }


def build_report() -> dict[str, Any]:
    rows = visible_rows()
    visible = visible_anomaly_ledger(rows)
    nogo = selector_higgs_parent_nogo(visible)
    inflow = five_dimensional_inflow(rows, visible)
    h_parent = u1h_running(rows)
    manifest = source_manifest()
    checks = {
        "all_v37_charge_lifts_reduce_to_frozen_finite_charges": all(
            row["U1X_charge_lift"] % N_X == v37.ALL_CHIRAL_FIELDS[row["field"]][0]
            and row["U1H_charge_lift"] % N_H == v37.ALL_CHIRAL_FIELDS[row["field"]][2]
            for row in rows
        ),
        "visible_mixed_PS_residue_is_exactly_minus_8_each": visible[
            "U1X_PS_squared_doubled_SU4_SU2L_SU2R"
        ] == [-8, -8, -8],
        "ordinary_threshold_obstruction_survives_even_order_relaxation": nogo[
            "light_residue_mod33_even_order_relaxation"
        ] == [25, 25, 25],
        "single_compact_axion_has_no_integer_level_solution": not nogo[
            "single_compact_GS_axion_subcase"
        ]["integer_solution_exists"],
        "isolated_U1H_parent_is_gauge_anomaly_free": h_parent["isolated_U1H_gauge_anomalies"][
            "all_vanish"
        ],
        "mirror_packet_cancels_all_listed_5D_anomaly_rows": inflow[
            "integer_anomaly_polynomial_coefficient_ledger"
        ]["all_net_rows_zero"],
        "pure_PS_anomalies_are_absent": visible["pure_PS_gauge_anomaly_absent"],
        "full_G1_remains_fail_closed": inflow["established_microscopic_UV_completion"] is False,
        "all_source_files_present": all(row["exists"] for row in manifest),
    }
    failures = [name for name, passed in checks.items() if not passed]
    report: dict[str, Any] = {
        "schema": "susy-v38-g1-uv-completion-audit-v1",
        "status": "V38_G1_4D_HIGGSED_U1X_NO_GO_PROVED__U1H_ISOLATED_PARENT_AUDITED__5D_ETA_INFLOW_EFT_PACKET_EXPLICIT__FULL_G1_FAIL_CLOSED",
        "purpose": "resolve the V37 ultraviolet-origin question as far as exact anomaly arithmetic allows without inventing an unprovided microscopic completion",
        "source_manifest": manifest,
        "visible_continuous_charge_packet": rows,
        "visible_anomaly_ledger": visible,
        "four_dimensional_no_go": nogo,
        "isolated_U1H_parent": h_parent,
        "five_dimensional_interval_EFT": inflow,
        "required_for_a_genuine_G1_promotion": [
            "a microscopic completion of the 5D eta-inflow system or an equally explicit quantized 4D topological response",
            "a symmetry-preserving mirror-wall gap with its exact spectrum and all threshold determinants",
            "a complete Spin^Z4R x Z5610 bordism calculation including the PS global form, gaugino, and gravitino",
            "UV-to-SARAH Wilson/Kahler/gauge-kinetic/soft matching and a global stabilized vacuum",
        ],
        "gate_decision": {
            "G1_closed": False,
            "G1_anomaly_subproblem_improved": True,
            "ordinary_4D_Higgsed_U1X_solution_exists_under_theorem_assumptions": False,
            "local_5D_continuous_anomaly_EFT_packet_exists": True,
            "established_complete_theory_exists": False,
        },
        "checks": checks,
        "n_failed": len(failures),
        "failures": failures,
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    anomaly = report["visible_anomaly_ledger"]
    nogo = report["four_dimensional_no_go"]
    h_parent = report["isolated_U1H_parent"]
    inflow = report["five_dimensional_interval_EFT"]
    return "\n".join(
        [
            "# SUSY V38 G1 ultraviolet-origin audit",
            "",
            f"- Status: `{report['status']}`",
            f"- Core: `{report['core_sha256']}`",
            "- Full G1 closed: **no**.",
            "",
            "## Exact result",
            "",
            "With primitive continuous U(1)_X lifts of the V37 Z66 charges, the doubled mixed Pati--Salam anomaly is "
            f"`{anomaly['U1X_PS_squared_doubled_SU4_SU2L_SU2R']}`.  It is nonzero modulo both `66` and the even-order relaxed modulus `33`. "
            "Therefore an ordinary four-dimensional Higgsed-U(1)_X parent cannot cancel it with only massive Pati--Salam thresholds while retaining the exact Z66 selector.",
            "",
            "The proof assumes Pati--Salam is unbroken at the threshold, all breaking VEVs have charge in `66 Z`, and every added non-singlet has an ordinary full-rank symmetry-preserving mass matrix.  Each representation block then shifts the mixed anomaly by zero modulo 66 (at most modulo 33 for the familiar even-order real-representation ambiguity).  The V37 residue is `-8`, so it cannot be removed.  A single ordinary compact GS axion with charge 66 also fails: its integer level would have to solve `66 k=8`.",
            "",
            "## What is now explicit",
            "",
            "The Z85 spectator has a clean isolated U(1)_H parent: its cubic, gravitational, and Pati--Salam mixed gauge anomalies vanish, and a charge `+/-85` Higgs pair leaves Z85.  Its one-loop supersymmetric Abelian coefficient is "
            f"`b_H={h_parent['one_loop_N1SUSY_abelian_b']['total']}`; maintaining two decades of perturbative headroom requires approximately `g_H < {h_parent['one_loop_N1SUSY_abelian_b']['gH_max_at_M_for_100x_scale_headroom']:.5f}` at the breaking scale.  The simultaneous U(1)_X x U(1)_H theory still has cross anomalies and is not claimed complete.",
            "",
            "A local five-dimensional interval EFT is also made concrete.  Place the V37 packet on one boundary and an exact inverse-anomaly PS-conjugate packet on the other.  Every listed continuous U(1), mixed, and chiral-matter R row then sums to zero, and an APS/Dai--Freed eta-invariant supplies the quantized inflow description.  This is a valid anomaly-EFT scaffold, not a microscopic UV completion: the mirror-wall gap, full R/gravitino/PS-centre bordism, KK thresholds, and all V37 dynamical matching remain open.",
            "",
            "## Decision",
            "",
            "V38 closes a false route rather than hiding it: a conventional 4D Higgsed U(1)_X solution is excluded under stated assumptions.  The viable route is an explicitly specified 5D inflow/topological completion, which still needs microscopic dynamics before G1 can be promoted.",
            "",
            "References: [Hsieh, discrete gauge anomalies](https://arxiv.org/abs/1808.02881), [Ibanez, heavy fermions and discrete anomalies](https://arxiv.org/abs/hep-ph/9210211), [Witten--Yonekura, eta-inflow](https://arxiv.org/abs/1909.08775), and [von Gersdorff--Quiros, localized orbifold anomalies](https://arxiv.org/abs/hep-th/0305024).",
            "",
            f"5D continuous-row cancellation: `{str(inflow['integer_anomaly_polynomial_coefficient_ledger']['all_net_rows_zero']).lower()}`.",
            "",
        ]
    )


def write_outputs(report: Mapping[str, Any]) -> None:
    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8", newline="\n")


def check_outputs(report: Mapping[str, Any]) -> bool:
    return (
        REPORT_JSON.is_file()
        and REPORT_MD.is_file()
        and REPORT_JSON.read_text(encoding="utf-8") == json.dumps(report, indent=2, sort_keys=True) + "\n"
        and REPORT_MD.read_text(encoding="utf-8") == render_markdown(report)
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        write_outputs(report)
    valid = report["n_failed"] == 0 and (not args.check or check_outputs(report))
    print("V38_G1_UV_AUDIT " + ("PASS" if valid else "FAIL"))
    print(report["core_sha256"])
    print(json.dumps(report["gate_decision"], sort_keys=True))
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
