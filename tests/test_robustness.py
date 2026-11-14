"""Check quotation integrity, denominators, and evaluation boundaries."""

import csv
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from src.robustness_checks import build_outputs, evaluate_rows, remove_annotated_spans
from src.validate_authors import expected_roles
from src.word_features import load_specification, tokenize_words


ROOT = Path(__file__).resolve().parents[1]


def annotation(text, passage, decision="remove"):
    start = text.index(passage)
    return {"start_offset": start, "end_offset": start + len(passage),
            "quoted_text": passage, "decision": decision, "reason": "Invented test passage"}


class QuotationBoundaryTests(unittest.TestCase):
    def test_replacement_prevents_adjacent_word_merging(self):
        text = 'alpha"borrowed words"omega'
        cleaned = remove_annotated_spans(text, [annotation(text, '"borrowed words"')])
        self.assertEqual(tokenize_words(cleaned, load_specification(ROOT)), ["alpha", "omega"])

    def test_retained_title_and_apostrophes_survive_multiline_removal(self):
        text = 'The "Book Title" says: "it\nis borrowed". It\u2019s the author\u2019s reply.'
        rows = [annotation(text, '"Book Title"', "retain"), annotation(text, '"it\nis borrowed"')]
        self.assertEqual(remove_annotated_spans(text, rows),
                         'The "Book Title" says:  . It\u2019s the author\u2019s reply.')

    def test_invalid_or_stale_offsets_are_rejected(self):
        text = 'A "quotation" follows.'
        row = annotation(text, '"quotation"')
        for invalid in ({**row, "end_offset": 100}, {**row, "start_offset": -1},
                        {**row, "quoted_text": '"different"'}, {**row, "decision": "guess"}):
            with self.subTest(row=invalid), self.assertRaises(ValueError):
                remove_annotated_spans(text, [invalid])

    def test_duplicate_or_unreviewed_passages_are_rejected(self):
        text = 'A "first" and "second" quotation.'
        row = annotation(text, '"first"')
        for rows in ([row], [row, row, annotation(text, '"second"')]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                remove_annotated_spans(text, rows)


class RobustnessWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build_outputs(ROOT)

    def rows(self, path):
        return list(csv.DictReader(io.StringIO(self.outputs[path].decode("utf-8"))))

    def test_feature_check_preserves_original_counts_and_all_word_denominators(self):
        with (ROOT / "results/counts.csv").open(newline="") as handle:
            original = {r["essay_number"]: r for r in csv.DictReader(handle)}
        rows = self.rows("results/feature_check/counts.csv")
        self.assertEqual(len(rows), 17)
        self.assertEqual(set(rows[0]) - {"essay_number", "role", "total_words"},
                         set(load_specification(ROOT).words) - {"the", "a", "of", "and"})
        for row in rows:
            self.assertEqual(row, {key: original[row["essay_number"]][key] for key in row})

    def test_quotation_rates_use_every_remaining_word(self):
        specification = load_specification(ROOT)
        counts = self.rows("results/quotation_check/counts.csv")
        rates = {r["essay_number"]: r for r in self.rows("results/quotation_check/frequencies.csv")}
        removals = {r["essay_number"]: r for r in self.rows("results/quotation_check/removal_summary.csv")}
        for row in counts:
            prefix = {"hamilton": "H", "madison": "M", "questioned": "Q"}[row["role"]]
            text = self.outputs[f"data/no_quotes/{prefix}_{row['essay_number']}.txt"].decode()
            tokens = tokenize_words(text, specification)
            self.assertEqual(len(tokens), int(row["total_words"]))
            self.assertGreater(len(tokens), sum(int(row[w]) for w in specification.words))
            for word in specification.words:
                self.assertEqual(int(row[word]), tokens.count(word))
                self.assertEqual(float(rates[row["essay_number"]][word]),
                                 tokens.count(word) / len(tokens) * 1000)
            self.assertEqual(int(removals[row["essay_number"]]["remaining_words"]), len(tokens))

    def test_each_variant_has_sixteen_uncontaminated_validation_trials(self):
        for variant in ("feature_check", "quotation_check"):
            fits = json.loads(self.outputs[f"results/{variant}/validation_fits.json"])
            self.assertEqual(len(fits), 16)
            for fit in fits:
                training = fit["training_model"]["training_ids"]
                self.assertEqual(len(training), 15)
                self.assertNotIn(str(fit["held_out_essay"]), training)
                self.assertNotIn("49", training)
            profile = json.loads(self.outputs[f"results/{variant}/questioned_profiles.json"])
            self.assertEqual(len(profile["training_model"]["training_ids"]), 16)
            self.assertNotIn("49", profile["training_model"]["training_ids"])

    def test_altered_questioned_frequencies_cannot_change_validation_or_profiles(self):
        roles = expected_roles(ROOT)
        rows = [{"essay_number": int(number), "role": author,
                 "the": 10 + i if author == "hamilton" else 40 + i}
                for i, (number, author) in enumerate(roles.items())]
        rows.append({"essay_number": 49, "role": "questioned", "the": 12})
        first = evaluate_rows(rows, ("the",), roles)
        second = evaluate_rows([*rows[:-1], {**rows[-1], "the": 900}], ("the",), roles)
        self.assertEqual(first[:3], second[:3])
        self.assertNotEqual(first[3], second[3])

    def test_missing_reference_blocks_validation_and_comparison(self):
        rows = self.rows("results/feature_check/frequencies.csv")[1:]
        with patch("src.robustness_checks.compare_questioned") as compare:
            with self.assertRaises(ValueError):
                evaluate_rows(rows, ("it",), expected_roles(ROOT))
            compare.assert_not_called()


if __name__ == "__main__":
    unittest.main()
