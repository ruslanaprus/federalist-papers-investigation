"""Test the comparison workflow with invented frequencies, not corpus scores."""

import csv
from dataclasses import replace
import io
import json
from pathlib import Path
import tempfile
from unittest.mock import patch
import unittest

from src.compare_questioned import compare_questioned, questioned_csv, record_block, require_completed_validation
from src.distance_method import EssayFrequencies, fit_reference_profiles
from src.validate_authors import ROOT, expected_roles


def invented_data():
    roles = expected_roles(ROOT)
    references = tuple(
        EssayFrequencies(int(number), author, {
            "the": (10 if author == "hamilton" else 30) + index / 10,
            "and": (20 if author == "hamilton" else 40) + index / 10,
            "of": 5,
        })
        for index, (number, author) in enumerate(roles.items())
    )
    return references, EssayFrequencies(49, "questioned", {"the": 11, "and": 21, "of": 8}), roles


def completed_validation(correct=0):
    return {
        "status": "complete", "total_trials": 16, "correct_assignments": correct,
        "by_author": {"hamilton": {"total": 8, "correct": correct // 2},
                      "madison": {"total": 8, "correct": correct - correct // 2}},
    }, {
        "status": "complete", "trial_count": 16, "training_essays_per_trial": 15,
        "questioned_essay_excluded": 49, "questioned_essay_compared": False,
    }


class QuestionedComparisonTests(unittest.TestCase):
    def test_final_fit_uses_sixteen_references_and_excludes_the_query(self):
        references, query, roles = invented_data()
        with patch("src.compare_questioned.fit_reference_profiles", wraps=fit_reference_profiles) as fit:
            model, _ = compare_questioned(references, query, ("the", "and"), roles)
        self.assertEqual(len(fit.call_args.args[0]), 16)
        self.assertNotIn("49", model.training_ids)
        self.assertEqual((model.hamilton_essay_count, model.madison_essay_count), (8, 8))

    def test_query_cannot_change_profiles_or_shared_scaling(self):
        references, query, roles = invented_data()
        first_model, first = compare_questioned(references, query, ("the", "and"), roles)
        second_model, second = compare_questioned(
            references, replace(query, frequencies={"the": 900, "and": 800}), ("the", "and"), roles,
        )
        self.assertEqual(first_model, second_model)
        self.assertNotEqual(first, second)

    def test_incomplete_reference_sample_cannot_reach_fitting(self):
        references, query, roles = invented_data()
        with patch("src.compare_questioned.fit_reference_profiles") as fit:
            with self.assertRaises(ValueError):
                compare_questioned(references[1:], query, ("the", "and"), roles)
            fit.assert_not_called()

    def test_wrong_or_invalid_query_is_rejected_before_fitting(self):
        references, query, roles = invented_data()
        for invalid in (
            replace(query, essay_id=48), replace(query, role="madison"),
            replace(query, frequencies={"the": float("nan"), "and": 10}),
        ):
            with self.subTest(query=invalid), patch("src.compare_questioned.fit_reference_profiles") as fit:
                with self.assertRaises(ValueError):
                    compare_questioned(references, invalid, ("the", "and"), roles)
                fit.assert_not_called()

    def test_completed_but_poor_validation_does_not_change_the_method(self):
        summary, manifest = completed_validation(0)
        require_completed_validation(summary, manifest)

    def test_missing_partial_or_query_contaminated_validation_is_rejected(self):
        summary, manifest = completed_validation(8)
        for invalid_summary, invalid_manifest in (
            ({}, manifest), ({**summary, "total_trials": 14}, manifest),
            (summary, {**manifest, "questioned_essay_excluded": None}),
            (summary, {**manifest, "questioned_essay_compared": True}),
        ):
            with self.subTest(summary=invalid_summary, manifest=invalid_manifest), self.assertRaises(ValueError):
                require_completed_validation(invalid_summary, invalid_manifest)

    def test_result_records_both_distances_signed_gap_exclusions_and_validation(self):
        references, query, roles = invented_data()
        model, score = compare_questioned(references, query, ("the", "and", "of"), roles)
        summary, _ = completed_validation(8)
        rows = list(csv.DictReader(io.StringIO(questioned_csv(model, score, summary).decode("utf-8"))))
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["essay_number"], "49")
        self.assertEqual(row["excluded_features"], "of")
        self.assertEqual(row["usable_feature_count"], "2")
        self.assertEqual(float(row["signed_gap"]), score.hamilton_distance - score.madison_distance)
        self.assertEqual((row["validation_correct"], row["validation_total"]), ("8", "16"))
        self.assertNotIn("probability", row)

    def test_readiness_uses_current_references_instead_of_a_stale_block_record(self):
        references, _, roles = invented_data()
        with tempfile.TemporaryDirectory(prefix="federalist-questioned-") as folder:
            root = Path(folder)
            (root / "results").mkdir()
            (root / "results/validation_preflight.json").write_text(json.dumps({
                "missing_essays": [21, 26], "available_reference_count": 14,
            }), encoding="utf-8")
            with (
                patch("src.compare_questioned.load_specification"),
                patch("src.compare_questioned.expected_roles", return_value=roles),
                patch("src.compare_questioned.load_references", return_value=references),
                patch("src.compare_questioned.preflight_inputs", return_value={}),
            ):
                record_block(root, "Validation must run first.")
            record = json.loads((root / "results/questioned_preflight.json").read_text())
        self.assertEqual(record["available_reference_count"], 16)
        self.assertEqual(record["missing_reference_essays"], [])
        self.assertEqual(record["completed_validation_trials"], 0)
        self.assertNotIn("validation_preflight_sha256", record)


if __name__ == "__main__":
    unittest.main()
