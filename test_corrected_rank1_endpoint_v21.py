#!/usr/bin/env python3
"""Central fail-closed tests for the audited corrected endpoint publication."""
from __future__ import annotations

import copy
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import corrected_rank1_endpoint_v21 as corrected


class CorrectedRank1EndpointV21Tests(unittest.TestCase):
    def test_exact_central_view_preserves_narrow_claim_boundary(self) -> None:
        publication = corrected.load_validated_publication()
        self.assertTrue(corrected.corrected_fixed_endpoint_theorem_exact(publication))
        view = corrected.central_view(publication)
        self.assertEqual(view["map_shape"], [6_585, 19_594])
        self.assertEqual(view["map_common_denominator"], 256)
        self.assertEqual(view["map_nnz"], 138_550)
        self.assertEqual(
            view["map_numerator_csr_sha256"], corrected.EXPECTED_MAP_SHA256
        )
        self.assertEqual(view["target_common_denominator"], 576_000)
        self.assertEqual(view["target_nonzero_count"], 512)
        self.assertEqual(
            view["target_numerator_sha256"], corrected.EXPECTED_TARGET_SHA256
        )
        self.assertEqual(view["exact_coefficient_equalities"], 6_585)
        self.assertEqual(view["strict_positive_Gram_blocks"], 22)
        self.assertEqual(view["strict_positive_LDL_pivots"], 824)
        self.assertTrue(view["arbitrary_real_Phi_at_fixed_endpoint"])
        self.assertTrue(view["strict_positive_off_homogeneous_origin"])
        self.assertTrue(view["A_greater_than_3_over_200_at_t1"])
        self.assertTrue(view["p_zero_set_at_t1_empty"])
        for name in (
            "legacy_v20_physical_target_valid",
            "legacy_v20_primal_valid",
            "global_Sigma_proved",
            "general_H_proved",
            "full_H_proved",
            "full_Hessian_proved",
            "G3_closed",
        ):
            self.assertIs(view[name], False, name)

    def test_semantic_updated_echo_mutations_fail_closed(self) -> None:
        publication = corrected.load_validated_publication()
        attacks = []
        changed = copy.deepcopy(publication)
        changed["theorem"]["claim_boundary"]["G3_closed"] = True
        attacks.append(changed)
        changed = copy.deepcopy(publication)
        changed["source"]["map"]["numerator_csr_sha256"] = "0" * 64
        changed["theorem"]["exact_evidence"]["map_numerator_csr_sha256"] = "0" * 64
        changed["manifest"]["logical_pins"]["map_numerator_csr_sha256"] = "0" * 64
        attacks.append(changed)
        changed = copy.deepcopy(publication)
        changed["source"]["physical_RHS"]["numerator_sha256"] = "1" * 64
        changed["theorem"]["exact_evidence"]["target_numerator_sha256"] = "1" * 64
        changed["manifest"]["logical_pins"]["target_numerator_sha256"] = "1" * 64
        attacks.append(changed)
        changed = copy.deepcopy(publication)
        changed["verify"]["exact_coefficient_equalities_verified"] = 6_584
        changed["theorem"]["exact_evidence"]["coefficient_equalities"] = 6_584
        attacks.append(changed)
        for path, value in (
            (("manifest", "schema"), "evil"),
            (("manifest", "status"), "evil"),
            (("manifest", "inventory_count"), 17),
            (("theorem", "theorem", "polynomial"), "evil"),
            (
                (
                    "source",
                    "carrier_exhaustion",
                    "carrier_transform_invertible_exact",
                ),
                False,
            ),
            (("verify", "target_numerator_int64_sha256"), "0" * 64),
            (("live", "claim_boundary", "G3_closed"), True),
            (("overflow", "claim_boundary", "G3_closed"), True),
            (("manifest", "inventory_count"), 18.0),
            (("manifest", "manifest_self_excluded_by_definition"), 1),
            (
                (
                    "source",
                    "carrier_exhaustion",
                    "carrier_transform_invertible_exact",
                ),
                1,
            ),
            (("verify", "exact_coefficient_equalities_verified"), 6585.0),
            (("verify", "exact_rational_coordinates_verified"), 19594.0),
            (("source", "map", "nnz"), 138550.0),
        ):
            changed = copy.deepcopy(publication)
            target = changed
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            attacks.append(changed)
        for attack in attacks:
            with self.subTest(attack=attacks.index(attack)):
                self.assertFalse(
                    corrected.corrected_fixed_endpoint_theorem_exact(attack)
                )

    def test_returned_publication_is_a_defensive_copy(self) -> None:
        first = corrected.load_validated_publication()
        first["theorem"]["claim_boundary"]["G3_closed"] = True
        second = corrected.load_validated_publication()
        self.assertIs(second["theorem"]["claim_boundary"]["G3_closed"], False)
        self.assertTrue(corrected.corrected_fixed_endpoint_theorem_exact(second))

    def test_same_process_post_first_load_disk_mutation_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            copied = Path(temporary) / "publication"
            shutil.copytree(corrected.PUBLICATION_ROOT, copied)
            replacements = {
                "PUBLICATION_ROOT": copied,
                "MANIFEST_PATH": copied / corrected.MANIFEST_PATH.name,
                "THEOREM_PATH": copied / corrected.THEOREM_PATH.name,
                "SOURCE_REPORT_PATH": copied / corrected.SOURCE_REPORT_PATH.name,
                "VERIFY_REPORT_PATH": copied / corrected.VERIFY_REPORT_PATH.name,
                "LIVE_REPORT_PATH": copied / corrected.LIVE_REPORT_PATH.name,
                "OVERFLOW_REPORT_PATH": copied / corrected.OVERFLOW_REPORT_PATH.name,
            }
            with patch.multiple(corrected, **replacements):
                first = corrected.load_validated_publication()
                self.assertTrue(
                    corrected.corrected_fixed_endpoint_theorem_exact(first)
                )
                theorem_path = copied / corrected.THEOREM_PATH.name
                theorem_path.write_bytes(theorem_path.read_bytes() + b"\n")
                with self.assertRaisesRegex(
                    ArithmeticError, "publication (?:size|byte hash) mismatch"
                ):
                    corrected.load_validated_publication()

    def test_each_verified_file_is_read_once_and_same_bytes_are_parsed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            copied = Path(temporary) / "publication"
            shutil.copytree(corrected.PUBLICATION_ROOT, copied)
            replacements = {
                "PUBLICATION_ROOT": copied,
                "MANIFEST_PATH": copied / corrected.MANIFEST_PATH.name,
                "THEOREM_PATH": copied / corrected.THEOREM_PATH.name,
                "SOURCE_REPORT_PATH": copied / corrected.SOURCE_REPORT_PATH.name,
                "VERIFY_REPORT_PATH": copied / corrected.VERIFY_REPORT_PATH.name,
                "LIVE_REPORT_PATH": copied / corrected.LIVE_REPORT_PATH.name,
                "OVERFLOW_REPORT_PATH": copied / corrected.OVERFLOW_REPORT_PATH.name,
            }
            original_read_bytes = Path.read_bytes
            counts: dict[str, int] = {}

            def counted_read_bytes(path: Path) -> bytes:
                resolved = path.resolve()
                if resolved.parent == copied.resolve():
                    counts[resolved.name] = counts.get(resolved.name, 0) + 1
                return original_read_bytes(path)

            with patch.multiple(corrected, **replacements), patch.object(
                Path, "read_bytes", counted_read_bytes
            ):
                publication = corrected.load_validated_publication()
            self.assertTrue(corrected.corrected_fixed_endpoint_theorem_exact(publication))
            self.assertEqual(set(counts), {path.name for path in copied.iterdir()})
            self.assertTrue(all(count == 1 for count in counts.values()), counts)


if __name__ == "__main__":
    unittest.main()
