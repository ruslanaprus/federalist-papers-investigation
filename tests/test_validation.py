"""Exercise the full validation workflow using invented reference frequencies."""

import csv
from dataclasses import replace
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from src.distance_method import EssayFrequencies, fit_reference_profiles
from src.validate_authors import (
    ROOT, check_reference_set, expected_roles, load_references,
    run_leave_one_out, summarize_trials, validation_csv,
)


def invented_corpus():
    roles = expected_roles(ROOT)
    rows = []
    for index, (number, role) in enumerate(roles.items()):
        center = 10 if role == "hamilton" else 30
        value = center + index / 10
        rows.append(EssayFrequencies(int(number), role, {
            "the": value, "and": value + 5, "of": 5,
            "an": 1 if index == 0 else 0,
        }))
    return tuple(rows), roles


class ValidationWorkflowTests(unittest.TestCase):
    def test_sixteen_trials_each_fit_fifteen_rows_without_the_evaluated_essay(self):
        rows, roles = invented_corpus()
        with patch("src.validate_authors.fit_reference_profiles", wraps=fit_reference_profiles) as fit:
            trials = run_leave_one_out(rows, ("the", "and"), roles)
        self.assertEqual(len(trials), 16)
        self.assertEqual(fit.call_count, 16)
        for trial, call in zip(trials, fit.call_args_list):
            training = call.args[0]
            self.assertEqual(len(training), 15)
            self.assertNotIn(trial.essay_id, [row.essay_id for row in training])
            self.assertNotIn(49, [row.essay_id for row in training])
            self.assertEqual(call.kwargs["held_out_essay_id"], trial.essay_id)
            self.assertEqual(sorted((trial.model.hamilton_essay_count, trial.model.madison_essay_count)), [7, 8])

    def test_incomplete_sample_stops_before_any_fit(self):
        rows, roles = invented_corpus()
        partial = tuple(row for row in rows if row.essay_id not in {21, 26})
        self.assertEqual(check_reference_set(partial, roles), ("21", "26"))
        with patch("src.validate_authors.fit_reference_profiles") as fit:
            with self.assertRaises(ValueError):
                run_leave_one_out(partial, ("the", "and"), roles)
            fit.assert_not_called()

    def test_constant_feature_exclusions_are_recalculated_within_each_trial(self):
        rows, roles = invented_corpus()
        trials = run_leave_one_out(rows, ("the", "an"), roles)
        self.assertEqual(trials[0].model.excluded_features, ("an",))
        self.assertEqual(trials[0].model.features, ("the",))
        self.assertTrue(all("an" in trial.model.features for trial in trials[1:]))

    def test_held_out_values_cannot_influence_their_own_profiles_or_scaling(self):
        rows, roles = invented_corpus()
        original = run_leave_one_out(rows, ("the", "and"), roles)
        changed = (replace(rows[0], frequencies={"the": 900, "and": 800}), *rows[1:])
        repeated = run_leave_one_out(changed, ("the", "and"), roles)
        self.assertEqual(original[0].model, repeated[0].model)
        self.assertNotEqual(original[0].score, repeated[0].score)

    def test_questioned_and_duplicate_reference_rows_are_rejected(self):
        rows, roles = invented_corpus()
        extra = EssayFrequencies(49, "questioned", {"the": 999})
        for invalid in ((*rows, extra), (*rows, rows[0])):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                run_leave_one_out(invalid, ("the",), roles)

    def test_inconclusive_trial_counts_as_unsuccessful_and_is_listed_separately(self):
        rows, roles = invented_corpus()
        trials = run_leave_one_out(rows, ("the", "and"), roles)
        first = trials[0]
        tied = replace(first, score=replace(
            first.score, prediction="inconclusive", signed_gap=0,
            hamilton_distance=1, madison_distance=1,
        ))
        summary = summarize_trials((tied, *trials[1:]))
        self.assertEqual(summary["correct_assignments"], 15)
        self.assertEqual(summary["by_author"]["hamilton"], {"correct": 7, "total": 8})
        self.assertEqual(summary["inconclusive_essays"], [first.essay_id])
        self.assertEqual(summary["misclassified_essays"], [])
        self.assertEqual(summary["baseline"], {"correct": 8, "total": 16, "rule": "Always choose one author"})

    def test_poor_performance_is_reportable_without_an_accuracy_gate(self):
        rows, roles = invented_corpus()
        trials = run_leave_one_out(rows, ("the", "and"), roles)
        wrong = tuple(replace(trial, score=replace(
            trial.score, prediction="madison" if trial.reference_author == "hamilton" else "hamilton",
        )) for trial in trials)
        summary = summarize_trials(wrong)
        self.assertEqual(summary["status"], "complete")
        self.assertEqual(summary["correct_assignments"], 0)
        self.assertEqual(len(summary["misclassified_essays"]), 16)
        self.assertIsNone(summary["universal_accuracy_threshold"])

    def test_csv_retains_all_sixteen_trials_distances_and_exclusions(self):
        rows, roles = invented_corpus()
        trials = run_leave_one_out(rows, ("the", "and", "of"), roles)
        records = list(csv.DictReader(io.StringIO(validation_csv(trials).decode("utf-8"))))
        self.assertEqual(len(records), 16)
        self.assertEqual(len({row["held_out_essay"] for row in records}), 16)
        self.assertTrue(all(row["excluded_features"] == "of" for row in records))
        self.assertTrue(all(row["usable_feature_count"] == "2" for row in records))
        self.assertTrue(all(float(row["absolute_gap"]) >= 0 for row in records))


class ReferenceLoadingTests(unittest.TestCase):
    def test_questioned_feature_values_are_never_parsed_or_used(self):
        rows, roles = invented_corpus()
        features = ("the", "and")
        with tempfile.TemporaryDirectory(prefix="federalist-validation-") as folder:
            root = Path(folder)
            (root / "results").mkdir()
            with (root / "results/frequencies.csv").open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["essay_number", "role", "total_words", *features])
                writer.writeheader()
                for row in rows:
                    writer.writerow({"essay_number": row.essay_id, "role": row.role, "total_words": 2000,
                                     **{word: row.frequencies[word] for word in features}})
                writer.writerow({"essay_number": 49, "role": "questioned", "total_words": "unused",
                                 "the": "not-a-frequency", "and": "also-unused"})
            loaded = load_references(root, features, roles)
        self.assertEqual(len(loaded), 16)
        self.assertNotIn(49, [row.essay_id for row in loaded])
        self.assertEqual(check_reference_set(loaded, roles), ())


if __name__ == "__main__":
    unittest.main()
