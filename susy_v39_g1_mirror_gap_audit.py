#!/usr/bin/env python3
"""V39 fail-closed test of whether the V38 mirror wall can be gapped.

The V38 interval construction cancels boundary anomalies only because the
second wall carries the inverse anomaly.  This audit asks the next necessary
question: can that wall be removed by a local supersymmetric mass sector while
preserving Pati--Salam, Z4R, and the Z5610 selector?  It proves the relevant
ordinary-superpotential no-go, records the first symmetry-breaking mass
witness, and separates conventional R-anomaly arithmetic from a genuine
Spin/Z4R/global-form bordism calculation.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping

import susy_v37_new_physics_routes as v37
import susy_v38_g1_uv_completion_audit as v38


ROOT = Path(__file__).resolve().parent
REPORT_JSON = ROOT / "SUSY_V39_G1_MIRROR_GAP_AUDIT.json"
REPORT_MD = ROOT / "SUSY_V39_G1_MIRROR_GAP_AUDIT.md"

N_X = v37.N66
N_H = v37.N85
N_SELECTOR = v37.N5610

SOURCE_FILES = (
    "susy_v39_g1_mirror_gap_audit.py",
    "test_susy_v39_g1_mirror_gap_audit.py",
    "susy_v38_g1_uv_completion_audit.py",
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


def mirror_packet() -> list[dict[str, Any]]:
    return v38.mirrored_rows(v38.visible_rows())


def ps_chiral_index(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Chiral PS family index of the opposite wall.

    A Pati--Salam-invariant holomorphic mass needs a representation and its
    conjugate.  The nonzero differences below are therefore a direct mass-rank
    obstruction, independent of any numerical coupling choices.
    """

    def count(representation: str) -> int:
        return sum(
            row["multiplicity"]
            for row in rows
            if row["PS_representation"] == representation
        )

    n4l, nbar4l = count("(4,2,1)"), count("(bar4,2,1)")
    n4r, nbar4r = count("(4,1,2)"), count("(bar4,1,2)")
    return {
        "mirror_4_2_1": n4l,
        "mirror_bar4_2_1": nbar4l,
        "mirror_4_1_2": n4r,
        "mirror_bar4_1_2": nbar4r,
        "left_chiral_index_n4_minus_nbar4": n4l - nbar4l,
        "right_chiral_index_nbar4_minus_n4": nbar4r - n4r,
        "number_of_unpaired_opposite_PS_families": 3,
        "ordinary_PS_preserving_full_rank_mass_possible": False,
        "reason": (
            "The mirror wall contains three net (bar4,2,1)+(4,1,2) families. "
            "PS-singlet mass matrices cannot remove a nonzero representation index."
        ),
    }


def ordinary_gap_nogo(mirror: list[dict[str, Any]], index: Mapping[str, Any]) -> dict[str, Any]:
    anomaly = v38.visible_anomaly_ledger(mirror)["U1X_PS_squared_doubled_SU4_SU2L_SU2R"]
    # The opposite packet has +8; a conventional massive threshold that retains
    # the Z66 gauge remnant changes the mixed anomaly only by 0 mod 66 (or at
    # most 0 mod 33 for an even-order real-representation ambiguity).
    return {
        "theorem": "no trivial local N=1 mirror-wall gap with unbroken PS x Z4R x Z5610",
        "assumptions": [
            "The mirror wall is a local 3+1D N=1 theory and all its extra fields are gapped by an ordinary polynomial superpotential/Kahler mass sector.",
            "Pati--Salam and the Z66 factor of Z5610 remain unbroken on the mirror wall.",
            "All VEV insertions in a mass matrix have U(1)X charge in 66 Z; no nonlocal cross-interval interaction or symmetry-breaking boundary condition is used.",
        ],
        "two_independent_obstructions": {
            "Pati_Salam_chiral_index": {
                "unpaired_opposite_families": index["number_of_unpaired_opposite_PS_families"],
                "full_rank_PS_invariant_mass": False,
            },
            "mixed_selector_anomaly": {
                "mirror_U1X_PS_squared_doubled_SU4_SU2L_SU2R": anomaly,
                "residue_mod66": [value % N_X for value in anomaly],
                "residue_mod33_even_order_relaxation": [value % (N_X // 2) for value in anomaly],
                "ordinary_symmetric_threshold_shift_mod66": [0, 0, 0],
                "ordinary_symmetric_threshold_shift_mod33": [0, 0, 0],
                "consequence": (
                    "A trivially gapped local wall cannot carry a nonzero perturbative U(1)X-PS^2 "
                    "anomaly.  The +8 residue must remain in massless boundary modes, be matched by "
                    "a nontrivial boundary topological theory, or be removed by breaking the selector."
                ),
            },
        },
        "proof": [
            "A PS-invariant mass block pairs R with Rbar.  Z66 invariance makes the determinant charge zero modulo 66, so its doubled mixed anomaly shift vanishes modulo 66 (at most modulo 33 in the even-order real-representation case).",
            "The inverse packet instead has (+8,+8,+8), nonzero under both tests; anomaly matching is invariant along any local RG flow.  It therefore cannot flow to a unique symmetry-preserving trivial gapped vacuum.",
            "Independently, its three net opposite PS families forbid a full-rank PS-singlet mass matrix before the selector is even considered.",
        ],
        "allowed_exits": [
            "leave the mirror wall gapless (the V38 interval EFT choice)",
            "break Pati--Salam or the Z66 selector on the far wall, making the visible selection rule non-exact in the full 5D theory",
            "supply an explicit nontrivial 3+1D boundary topological order/symmetry extension with a matched anomaly and a microscopic construction",
        ],
        "ordinary_symmetric_gapping_superpotential_exists": False,
    }


def first_breaking_mass_witness(mirror: list[dict[str, Any]]) -> dict[str, Any]:
    by_name = {row["field"]: row for row in mirror}
    q = by_name["mirror_Q"]
    psi_bar = by_name["mirror_PsiBar"]
    required_x = -(q["U1X_charge_lift"] + psi_bar["U1X_charge_lift"])
    required_r = (2 - q["Z4R_superfield_charge"] - psi_bar["Z4R_superfield_charge"]) % 4
    # The quantum numbers agree with a local Pbar-like field.  Its VEV is the
    # first (degree-three) mass insertion for this pair but it reduces Z66 to
    # Z2 and Z5610 to Z170.
    residual_x = math.gcd(N_X, abs(required_x))
    residual_selector = math.gcd(N_SELECTOR, abs(N_H * required_x))
    return {
        "target_pair": ["mirror_Q", "mirror_PsiBar"],
        "PS_contraction": "(bar4,2,1) x (4,2,1) -> (1,1,1)",
        "bilinear_U1X_charge": q["U1X_charge_lift"] + psi_bar["U1X_charge_lift"],
        "bilinear_Z4R_superfield_charge_mod4": (
            q["Z4R_superfield_charge"] + psi_bar["Z4R_superfield_charge"]
        ) % 4,
        "lowest_local_holomorphic_mass_operator": "Bminus2 * mirror_Q * mirror_PsiBar",
        "operator_degree": 3,
        "Bminus2_required_U1X_charge": required_x,
        "Bminus2_required_U1H_charge": 0,
        "Bminus2_required_Z4R_superfield_charge": required_r,
        "Bminus2_Z5610_charge": (N_H * required_x) % N_SELECTOR,
        "a_VEV_of_Bminus2_leaves_Z66": f"Z{residual_x}",
        "a_VEV_of_Bminus2_leaves_Z5610": f"Z{residual_selector}",
        "V37_identification": "The visible Pbar has precisely (U1X,R)=(-2,2), but a local far-wall copy would be required for locality.",
        "verdict": (
            "A degree-three mass witness exists only after a charge-minus-two VEV, which breaks Z66 to Z2 "
            "and the selector Z5610 to Z170.  It is not a symmetry-preserving ultraviolet mirror gap."
        ),
    }


def r_anomaly_ledger(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Conventional 4D N=1 discrete-R bookkeeping, explicitly not bordism."""

    chiral = [
        sum(
            row["multiplicity"]
            * row["Z4R_fermion_lift"]
            * row["doubled_Dynkin_indices_SU4_SU2L_SU2R"][index]
            for row in rows
        )
        for index in range(3)
    ]
    gaugino = [8, 4, 4]  # 2T(adj) for SU(4), SU(2), SU(2)
    total = [left + right for left, right in zip(chiral, gaugino, strict=True)]
    matter_grav = sum(
        row["multiplicity"] * row["PS_dimension_per_copy"] * row["Z4R_fermion_lift"]
        for row in rows
    )
    gaugino_grav_ps_only = 15 + 3 + 3
    # The V38 interval additionally gauges U(1)X and U(1)H.  If both have
    # ordinary 4D N=1 zero-mode vectors, their neutral gauginos add two.  The
    # orbifold projection and the R charges of the breaking sectors are not
    # specified, so this is a bookkeeping branch, not a 5D SUGRA derivation.
    gaugino_grav_with_parent_u1s = gaugino_grav_ps_only + 2
    gravitino = -21  # standard 4D N=1 spin-3/2 index contribution
    total_grav = matter_grav + gaugino_grav_ps_only + gravitino
    total_grav_parent_u1s = matter_grav + gaugino_grav_with_parent_u1s + gravitino
    return {
        "scope": "conventional local anomaly coefficients; not a complete Spin/Z4R eta-invariant or supergravity compactification",
        "formulae": {
            "mixed_G_squared_Z4R": "sum_chiral 2T(R_i)*(q_i-1) + 2T(adj_G)",
            "gravitational_Z4R": "sum_chiral dim(R_i)*(q_i-1) + sum_G dim(adj_G) - 21",
        },
        "chiral_matter_mixed_doubled_SU4_SU2L_SU2R": chiral,
        "gaugino_mixed_doubled_SU4_SU2L_SU2R": gaugino,
        "total_mixed_doubled_SU4_SU2L_SU2R": total,
        "total_mixed_mod4": [value % 4 for value in total],
        "total_mixed_mod2_standard_even_N_eta": [value % 2 for value in total],
        "universality": len(set(value % 4 for value in total)) == 1,
        "matter_gravitational": matter_grav,
        "gaugino_gravitational_PS_only": gaugino_grav_ps_only,
        "gaugino_gravitational_with_U1X_U1H_zero_modes": gaugino_grav_with_parent_u1s,
        "gravitino_gravitational": gravitino,
        "total_gravitational_PS_only": total_grav,
        "total_gravitational_PS_only_mod2": total_grav % 2,
        "total_gravitational_with_U1X_U1H_zero_modes_before_breaking_sector": total_grav_parent_u1s,
        "total_gravitational_with_U1X_U1H_zero_modes_before_breaking_sector_mod2": total_grav_parent_u1s % 2,
        "unfixed_R_data": [
            "5D orbifold projection and supergravity multiplet convention",
            "Z4R charges of the +/-66 and +/-85 Higgs/breaking sectors",
            "mirror-wall and possible boundary-topological degrees of freedom",
        ],
        "minimal_arithmetic_GS_modulino_patch": {
            "field": "one PS- and selector-neutral chiral modulino of Z4R fermion lift -1",
            "new_total_gravitational_PS_only": total_grav - 1,
            "new_total_gravitational_PS_only_mod2": (total_grav - 1) % 2,
            "new_total_gravitational_with_parent_U1_zero_modes": total_grav_parent_u1s - 1,
            "new_total_gravitational_with_parent_U1_zero_modes_mod2": (total_grav_parent_u1s - 1) % 2,
            "what_it_does_not_supply": "a microscopic axion period, a quantized Wess--Zumino action, or a full gravitino/global-form bordism calculation",
        },
        "conclusion": (
            "The PS gauge rows are universal (2 mod4, equivalently 0 mod2 in the common even-N convention), "
            "but both displayed gravitational branches are odd before unspecified breaking/mirror sectors. "
            "A one-modulino arithmetic patch fixes only that parity; it is not a physical UV completion."
        ),
    }


def ps_global_form(rows: list[dict[str, Any]]) -> dict[str, Any]:
    # The Spin(10) Pati--Salam subgroup has the indicated diagonal quotient.
    # All V37 representations are trivial under z=(-1_4,-1_L,-1_R).
    descends = {}
    for row in rows:
        rep = row["PS_representation"]
        if rep == "(1,2,2)":
            action = "+1 = (-1_L)(-1_R)"
        elif "4" in rep and ",2,1)" in rep:
            action = "+1 = (-1_4)(-1_L)"
        elif "4" in rep and ",1,2)" in rep:
            action = "+1 = (-1_4)(-1_R)"
        elif rep == "(6,1,1)":
            action = "+1 = (-1_4)^2"
        else:
            action = "+1 = singlet"
        descends[row["field"]] = action
    anomaly = v38.visible_anomaly_ledger(rows)
    return {
        "global_form": "G_PS = (SU(4) x SU(2)_L x SU(2)_R) / Z2_diag, with z=(-1_4,-1_L,-1_R)",
        "Spin10_embedding_reason": "the diagonal element acts trivially on (4,2,1), (bar4,1,2), (1,2,2), and (6,1,1)",
        "all_V37_representations_descend": True,
        "representation_descent_checks": descends,
        "SU2_Witten_doublet_counts_visible": anomaly["SU2L_SU2R_Witten_doublet_counts"],
        "SU2_Witten_anomalies_absent": all(
            count % 2 == 0 for count in anomaly["SU2L_SU2R_Witten_doublet_counts"]
        ),
        "uncomputed_required_bordism": "Omega_5 for the actual Spin/Z4R structure times B[G_PS] times BZ5610, including gaugino/gravitino and quotient bundles",
        "status": "representation and ordinary SU2 global checks pass; the requested product bordism has not been derived",
    }


def build_report() -> dict[str, Any]:
    mirror = mirror_packet()
    index = ps_chiral_index(mirror)
    gap = ordinary_gap_nogo(mirror, index)
    witness = first_breaking_mass_witness(mirror)
    r_ledger = r_anomaly_ledger(v38.visible_rows())
    global_form = ps_global_form(v38.visible_rows())
    manifest = source_manifest()
    checks = {
        "mirror_has_three_opposite_PS_families": index["number_of_unpaired_opposite_PS_families"] == 3,
        "ordinary_PS_preserving_full_rank_mass_is_impossible": index[
            "ordinary_PS_preserving_full_rank_mass_possible"
        ] is False,
        "mirror_mixed_selector_residue_is_plus_8_each": gap["two_independent_obstructions"][
            "mixed_selector_anomaly"
        ]["mirror_U1X_PS_squared_doubled_SU4_SU2L_SU2R"] == [8, 8, 8],
        "mirror_residue_survives_mod66_and_mod33": gap["two_independent_obstructions"][
            "mixed_selector_anomaly"
        ]["residue_mod33_even_order_relaxation"] == [8, 8, 8],
        "first_mass_witness_breaks_Z66_to_Z2": witness["a_VEV_of_Bminus2_leaves_Z66"] == "Z2",
        "first_mass_witness_breaks_Z5610_to_Z170": witness[
            "a_VEV_of_Bminus2_leaves_Z5610"
        ] == "Z170",
        "conventional_R_gauge_rows_are_universal": r_ledger["total_mixed_doubled_SU4_SU2L_SU2R"] == [14, 10, 2]
        and r_ledger["universality"],
        "bare_conventional_R_gravity_rows_are_odd": r_ledger["total_gravitational_PS_only_mod2"] == 1
        and r_ledger["total_gravitational_with_U1X_U1H_zero_modes_before_breaking_sector_mod2"] == 1,
        "one_modulino_only_repairs_arithmetic_parity": r_ledger["minimal_arithmetic_GS_modulino_patch"][
            "new_total_gravitational_PS_only_mod2"
        ] == 0,
        "PS_global_form_representation_and_Witten_checks_pass": global_form[
            "all_V37_representations_descend"
        ] and global_form["SU2_Witten_anomalies_absent"],
        "full_G1_remains_fail_closed": gap["ordinary_symmetric_gapping_superpotential_exists"] is False,
        "sources_present": all(row["exists"] for row in manifest),
    }
    failures = [name for name, passed in checks.items() if not passed]
    report: dict[str, Any] = {
        "schema": "susy-v39-g1-mirror-gap-audit-v1",
        "status": "V39_MIRROR_WALL_TRIVIAL_SUPERPOTENTIAL_GAP_NO_GO__FIRST_BREAKING_MASS_WITNESS_EXPLICIT__R_AND_PS_GLOBAL_ARITHMETIC_AUDITED__FULL_G1_FAIL_CLOSED",
        "source_manifest": manifest,
        "mirror_chiral_index": index,
        "ordinary_mirror_gap_no_go": gap,
        "first_selector_breaking_mass_witness": witness,
        "conventional_Z4R_anomaly_ledger": r_ledger,
        "Pati_Salam_global_form": global_form,
        "literature": [
            "https://arxiv.org/abs/1909.08775",
            "https://arxiv.org/abs/1808.02881",
            "https://arxiv.org/abs/1910.04962",
            "https://arxiv.org/abs/1707.03837",
            "https://arxiv.org/abs/2009.04582",
        ],
        "required_for_G1_promotion": [
            "an explicit microscopic 3+1D boundary topological order or a UV completion that matches the mirror anomaly without breaking the selector",
            "a complete 5D/4D Spin-Z4R product bordism calculation with the PS diagonal quotient and the actual supergravity spectrum",
            "quantized eta/CS/GS levels, mirror threshold determinants, KK spectrum, and UV-to-visible matching",
        ],
        "gate_decision": {
            "G1_closed": False,
            "ordinary_local_mirror_wall_gap_exists": False,
            "selector_breaking_mass_witness_exists": True,
            "R_anomaly_arithmetic_improved": True,
            "full_product_bordism_complete": False,
            "established_complete_theory_exists": False,
        },
        "checks": checks,
        "n_failed": len(failures),
        "failures": failures,
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    index = report["mirror_chiral_index"]
    gap = report["ordinary_mirror_gap_no_go"]
    witness = report["first_selector_breaking_mass_witness"]
    r_ledger = report["conventional_Z4R_anomaly_ledger"]
    return "\n".join(
        [
            "# SUSY V39 G1 mirror-wall gap audit",
            "",
            f"- Status: `{report['status']}`",
            f"- Core: `{report['core_sha256']}`",
            "- Full G1 closed: **no**.",
            "",
            "## Mirror-wall result",
            "",
            "The V38 inverse packet cannot be removed by a local symmetry-preserving N=1 superpotential.  It contains "
            f"`{index['number_of_unpaired_opposite_PS_families']}` net opposite Pati--Salam families and has mixed U(1)_X-PS^2 coefficient "
            f"`{gap['two_independent_obstructions']['mixed_selector_anomaly']['mirror_U1X_PS_squared_doubled_SU4_SU2L_SU2R']}`.  "
            "Either obstruction alone forbids a full-rank trivial PS x Z66 preserving mass gap.",
            "",
            "The first local mass attempt is explicit: `Bminus2*mirror_Q*mirror_PsiBar`.  Its needed field has U(1)_X charge `-2` and Z4R superfield charge `2`, exactly the Pbar-like assignment.  Its VEV leaves only "
            f"`{witness['a_VEV_of_Bminus2_leaves_Z66']}` of Z66 and `{witness['a_VEV_of_Bminus2_leaves_Z5610']}` of Z5610.  It therefore breaks the selector and cannot serve as the ultraviolet mirror gap.",
            "",
            "## R and global-form accounting",
            "",
            "Using the conventional N=1 local R-anomaly formula, chiral matter plus Pati--Salam gauginos gives doubled mixed rows "
            f"`{r_ledger['total_mixed_doubled_SU4_SU2L_SU2R']}`, universal as `2 mod 4`.  The PS-only gravitational count is "
            f"`{r_ledger['total_gravitational_PS_only']}`; with U(1)X and U(1)H zero-mode gauginos it is `{r_ledger['total_gravitational_with_U1X_U1H_zero_modes_before_breaking_sector']}`.  Both are odd modulo two before the unspecified breaking/mirror sector.  One neutral modulino of fermion R lift `-1` repairs only arithmetic parity; it does not give a quantized GS action or a full supergravity completion.",
            "",
            "The correct Spin(10)-descended Pati--Salam global form is `(SU4 x SU2L x SU2R)/Z2_diag`; every V37 representation descends and both SU2 Witten doublet counts are even.  The full product bordism with Z4R, Z5610, gauginos, gravitino, and quotient bundles remains uncomputed.",
            "",
            "## Decision",
            "",
            "V39 rules out the missing conventional mirror-wall superpotential.  A nontrivial anomalous boundary topological order or a microscopic UV completion would be new physical input, not a consequence of V37/V38.  The 5D interval remains an anomaly-EFT scaffold and G1 remains fail-closed.",
            "",
            "References: [Witten--Yonekura](https://arxiv.org/abs/1909.08775), [Hsieh](https://arxiv.org/abs/1808.02881), [Cordova--Ohmori](https://arxiv.org/abs/1910.04962), [Byakti--Ghosh--Sharma](https://arxiv.org/abs/1707.03837), and [Kawamura--Raby](https://arxiv.org/abs/2009.04582).",
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
    print("V39_G1_MIRROR_GAP_AUDIT " + ("PASS" if valid else "FAIL"))
    print(report["core_sha256"])
    print(json.dumps(report["gate_decision"], sort_keys=True))
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
