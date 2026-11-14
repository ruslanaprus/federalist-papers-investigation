"""Check the distance definition with invented frequencies, never corpus scores."""

from dataclasses import replace
import math
from pathlib import Path
import tempfile
import unittest

from src.distance_method import (
    ROOT, TIE_TOLERANCE, EssayFrequencies, choose_author, compare_essay,
    definition, fit_reference_profiles,
)


def invented_references():
    return (
        EssayFrequencies("H-A", "hamilton", {"the": 10, "and": 20, "of": 5}),
        EssayFrequencies("H-B", "hamilton", {"the": 14, "and": 24, "of": 5}),
        EssayFrequencies("M-A", "madison", {"the": 18, "and": 28, "of": 5}),
        EssayFrequencies("M-B", "madison", {"the": 22, "and": 32, "of": 5}),
    )


class DistanceArithmeticTests(unittest.TestCase):
    def test_author_profiles_are_equal_weight_essay_means(self):
        model = fit_reference_profiles(invented_references(), ("the", "and"))
        self.assertEqual(model.hamilton_mean, (12, 22))
        self.assertEqual(model.madison_mean, (20, 30))
        self.assertEqual((model.hamilton_essay_count, model.madison_essay_count), (2, 2))

    def test_scaling_uses_sample_variation_across_both_authors(self):
        model = fit_reference_profiles(invented_references(), ("the", "and"))
        expected = math.sqrt(80 / 3)
        for scale in model.sample_standard_deviations:
            self.assertAlmostEqual(scale, expected)
            self.assertNotAlmostEqual(scale, math.sqrt(80 / 4))
            self.assertNotAlmostEqual(scale, math.sqrt(8))

    def test_distance_averages_absolute_standardized_differences(self):
        model = fit_reference_profiles(invented_references(), ("the", "and"))
        query = EssayFrequencies("invented-query", "questioned", {"the": 13, "and": 23})
        score = compare_essay(model, query)
        scale = math.sqrt(80 / 3)
        self.assertAlmostEqual(score.hamilton_distance, 1 / scale)
        self.assertAlmostEqual(score.madison_distance, 7 / scale)
        self.assertAlmostEqual(score.signed_gap, -6 / scale)
        self.assertEqual(score.prediction, "hamilton")

    def test_opposite_signed_differences_do_not_cancel(self):
        model = fit_reference_profiles(invented_references(), ("the", "and"))
        score = compare_essay(model, EssayFrequencies("query", "questioned", {"the": 13, "and": 21}))
        self.assertAlmostEqual(score.hamilton_distance, 1 / math.sqrt(80 / 3))
        self.assertGreater(score.hamilton_distance, 0)

    def test_constant_feature_is_excluded_from_scaling_and_the_divisor(self):
        model = fit_reference_profiles(invented_references(), ("of", "the", "and"))
        self.assertEqual(model.features, ("the", "and"))
        self.assertEqual(model.excluded_features, ("of",))
        query = EssayFrequencies("query", "questioned", {"of": 999, "the": 13, "and": 23})
        score = compare_essay(model, query)
        self.assertAlmostEqual(score.hamilton_distance, 1 / math.sqrt(80 / 3))
        self.assertEqual(len(score.hamilton_contributions), 2)

    def test_all_constant_features_stop_instead_of_producing_a_zero_distance(self):
        with self.assertRaises(ValueError):
            fit_reference_profiles(invented_references(), ("of",))

    def test_small_positive_variation_is_retained_without_epsilon_clipping(self):
        rows = tuple(
            EssayFrequencies(index + 1, "hamilton" if index < 2 else "madison", {"the": index * 1e-14})
            for index in range(4)
        )
        model = fit_reference_profiles(rows, ("the",))
        self.assertEqual(model.features, ("the",))
        self.assertTrue(0 < model.sample_standard_deviations[0] < TIE_TOLERANCE)

    def test_numerical_tie_tolerance_is_inclusive(self):
        self.assertEqual(choose_author(0, TIE_TOLERANCE), "inconclusive")
        self.assertEqual(choose_author(0, 2 * TIE_TOLERANCE), "hamilton")
        self.assertEqual(choose_author(2 * TIE_TOLERANCE, 0), "madison")


class TrainingSeparationTests(unittest.TestCase):
    def test_questioned_row_is_rejected_even_with_other_known_references(self):
        for row in (
            EssayFrequencies(49, "hamilton", {"the": 10}),
            EssayFrequencies("49", "madison", {"the": 10}),
            EssayFrequencies("query", "questioned", {"the": 10}),
        ):
            with self.subTest(row=row), self.assertRaises(ValueError):
                fit_reference_profiles((*invented_references(), row), ("the",))

    def test_explicitly_held_out_essay_cannot_be_in_training(self):
        with self.assertRaises(ValueError):
            fit_reference_profiles(invented_references(), ("the",), held_out_essay_id="H-A")

    def test_training_essay_cannot_be_scored_as_unknown(self):
        rows = invented_references()
        model = fit_reference_profiles(rows, ("the",))
        with self.assertRaises(ValueError):
            compare_essay(model, rows[0])

    def test_query_values_and_label_do_not_refit_or_change_training_quantities(self):
        rows = invented_references()
        training = rows[1:]
        model = fit_reference_profiles(training, ("the", "and"), held_out_essay_id="H-A")
        self.assertEqual(model.hamilton_mean, (14, 24))
        self.assertAlmostEqual(model.sample_standard_deviations[0], 4)
        before = model
        first = compare_essay(model, rows[0])
        relabelled = compare_essay(model, replace(rows[0], role="madison"))
        self.assertEqual(first, relabelled)
        compare_essay(model, replace(rows[0], frequencies={"the": 900, "and": 800}))
        self.assertEqual(model, before)
        self.assertEqual(model, fit_reference_profiles(training, ("the", "and"), held_out_essay_id="H-A"))

    def test_duplicate_references_and_missing_author_group_are_rejected(self):
        rows = invented_references()
        for training in ((*rows, rows[0]), rows[:2]):
            with self.subTest(training=training), self.assertRaises(ValueError):
                fit_reference_profiles(training, ("the",))

    def test_nonfinite_negative_and_missing_values_are_rejected(self):
        rows = invented_references()
        for values in ({"the": float("nan")}, {"the": float("inf")}, {"the": -1}, {}, {"the": 1001}):
            with self.subTest(values=values), self.assertRaises(ValueError):
                fit_reference_profiles((replace(rows[0], frequencies=values), *rows[1:]), ("the",))
        model = fit_reference_profiles(rows, ("the",))
        with self.assertRaises(ValueError):
            compare_essay(model, EssayFrequencies("query", "questioned", {"the": float("nan")}))


class DefinitionTests(unittest.TestCase):
    def test_unplanned_distance_settings_are_rejected(self):
        original = (ROOT / "config/research.toml").read_text("utf-8")
        changes = (
            ("standard_deviation_ddof = 1", "standard_deviation_ddof = 0"),
            ('profile_weighting = "equal_essay"', 'profile_weighting = "word_count"'),
            ("tie_absolute_tolerance = 1e-12", "tie_absolute_tolerance = 1e-6"),
            ('constant_features = "exclude"', 'constant_features = "epsilon_clip"'),
        )
        with tempfile.TemporaryDirectory(prefix="federalist-distance-") as folder:
            root = Path(folder)
            (root / "config").mkdir()
            (root / "docs").mkdir()
            (root / "docs/research_plan.md").write_bytes((ROOT / "docs/research_plan.md").read_bytes())
            for before, after in changes:
                with self.subTest(setting=before):
                    modified = original.replace(before, after, 1)
                    self.assertNotEqual(modified, original)
                    (root / "config/research.toml").write_text(modified, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        definition(root)


if __name__ == "__main__":
    unittest.main()
