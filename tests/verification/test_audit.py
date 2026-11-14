from decimal import Decimal, localcontext
import unittest

from src.verification.__main__ import (
    NumericChecks, check_model, fit_decimal, indexed, scan_words, score_decimal,
)


class IndependentScannerTests(unittest.TestCase):
    def test_apostrophes_and_word_boundaries_match_the_registered_rule(self):
        text = "'THE' theme it\u2019s isn't a''b in/on 49 THE-and"
        tokens = scan_words(text)
        self.assertEqual([t[0] for t in tokens],
                         ["the", "theme", "it's", "isn't", "a", "b", "in", "on", "the", "and"])
        self.assertEqual([text[start:end] for word, start, end in tokens],
                         ["THE", "theme", "it\u2019s", "isn't", "a", "b", "in", "on", "THE", "and"])


class AuditFailureDetectionTests(unittest.TestCase):
    def test_duplicate_and_missing_essay_identities_are_rejected(self):
        for rows in ([{"id": "1"}, {"id": "1"}], [{"id": "1"}]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                indexed(rows, "id", (1, 6))

    def test_nonfinite_and_material_numerical_disagreements_fail(self):
        for actual in ("NaN", "Infinity", ".000001"):
            with self.subTest(actual=actual), self.assertRaises(ValueError):
                NumericChecks().close(actual, Decimal(0), "invented mismatch")

    def test_independent_model_rejects_population_scaling_and_contaminated_ids(self):
        with localcontext() as context:
            context.prec = 50
            rows = [{"number": i, "role": "hamilton" if i <= 2 else "madison",
                     "frequencies": {"the": Decimal(value), "of": Decimal(5)}}
                    for i, value in enumerate((10, 14, 18, 22), start=1)]
            expected = fit_decimal(rows, ("the", "of"))
            saved = {**expected, "sample_standard_deviations": [Decimal(20).sqrt()]}
            with self.assertRaises(ValueError):
                check_model(saved, expected, NumericChecks())
            saved = {**expected, "training_ids": ["1", "2", "3", "49"]}
            with self.assertRaises(ValueError):
                check_model(saved, expected, NumericChecks())
            self.assertEqual(expected["excluded_features"], ["of"])
            self.assertEqual(expected["hamilton_mean"], [Decimal(12)])
            self.assertEqual(expected["madison_mean"], [Decimal(20)])
            self.assertEqual(expected["sample_standard_deviations"], [(Decimal(80) / 3).sqrt()])

    def test_constant_features_and_evaluation_data_cannot_enter_independent_fit(self):
        rows = [{"number": 1, "role": "hamilton", "frequencies": {"of": Decimal(5)}},
                {"number": 6, "role": "madison", "frequencies": {"of": Decimal(5)}}]
        with self.assertRaises(ValueError):
            fit_decimal(rows, ("of",))
        with self.assertRaises(ValueError):
            fit_decimal([rows[0], {**rows[1], "number": 49}], ("of",))

    def test_independent_distance_and_tie_rule_have_invented_known_answers(self):
        model = {"features": ["the"], "training_ids": ["1", "6"],
                 "hamilton_mean": [Decimal(10)], "madison_mean": [Decimal(20)],
                 "sample_standard_deviations": [Decimal(2)]}
        distances, gap, prediction, _ = score_decimal(model, {"number": 49, "frequencies": {"the": Decimal(12)}})
        self.assertEqual(distances, {"hamilton": Decimal(1), "madison": Decimal(4)})
        self.assertEqual(gap, Decimal(-3))
        self.assertEqual(prediction, "hamilton")
        self.assertEqual(score_decimal(model, {"number": 49, "frequencies": {"the": Decimal(15)}})[2], "inconclusive")
        with self.assertRaises(ValueError):
            score_decimal(model, {"number": 1, "frequencies": {"the": Decimal(12)}})


if __name__ == "__main__":
    unittest.main()
