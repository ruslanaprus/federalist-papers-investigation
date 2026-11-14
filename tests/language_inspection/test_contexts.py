import csv
import io
import json
import math
from pathlib import Path
import tempfile
import unittest

from src.interpretation.__main__ import (
    build_outputs, concordances, example_rows, quotation_decision,
    rank_contributions, word_spans,
)
from src.word_features import load_specification


ROOT = Path(__file__).resolve().parents[2]


class ContributionRankingTests(unittest.TestCase):
    def test_absolute_ranking_preserves_sign_and_breaks_ties_alphabetically(self):
        profile = {
            "training_model": {"features": ["z", "a", "m", "b"]},
            "result": {"hamilton_contributions": [3, 0, 1, 2],
                       "madison_contributions": [1, 2, 1, 1]},
        }
        ranked = rank_contributions(profile)
        self.assertEqual([r["word"] for r in ranked], ["a", "z", "b", "m"])
        self.assertEqual([r["favored_profile"] for r in ranked],
                         ["hamilton", "madison", "madison", "neither"])
        self.assertEqual(ranked[0]["signed_difference"], -2)
        self.assertEqual(ranked[0]["contribution_to_mean_gap"], -.5)

    def test_mismatched_or_nonfinite_contributions_are_rejected(self):
        for h, m in (([1], []), ([float("nan")], [1]), ([-1], [1])):
            with self.subTest(h=h), self.assertRaises(ValueError):
                rank_contributions({"training_model": {"features": ["on"]},
                                    "result": {"hamilton_contributions": h,
                                               "madison_contributions": m}})


class ConcordanceLocationTests(unittest.TestCase):
    def setUp(self):
        self.specification = load_specification(ROOT)

    def test_offsets_retain_case_curly_apostrophes_and_whole_word_rules(self):
        text = "ON inborn isn\u2019t in; these-they're at home."
        tokens = word_spans(text, self.specification)
        self.assertEqual([t.word for t in tokens],
                         ["on", "inborn", "isn't", "in", "these", "they're", "at", "home"])
        self.assertEqual(text[tokens[0].start:tokens[0].end], "ON")
        self.assertEqual(text[tokens[2].start:tokens[2].end], "isn\u2019t")

    def test_length_changing_normalization_cannot_silently_corrupt_offsets(self):
        with self.assertRaises(ValueError):
            word_spans("\u0130n a place", self.specification)

    def test_context_edges_and_quotation_decisions_preserve_readable_text(self):
        text = 'ON "these" grounds,\nwe agree in principle.'
        tokens = word_spans(text, self.specification)
        annotations = [{"start_offset": 3, "end_offset": 10, "decision": "retain"}]
        source = {"essay_number": 49, "role": "questioned", "text_path": "invented.txt", "url": "invented"}
        rows = concordances(text, tokens, ("on", "in", "these"), source, annotations)
        self.assertEqual(rows[0]["left_context"], "")
        self.assertEqual(rows[0]["matched_text"], "ON")
        self.assertEqual(rows[1]["quotation_decision"], "retain")
        self.assertEqual(rows[2]["line_number"], 2)
        self.assertEqual(rows[2]["right_context"], " principle")
        self.assertEqual(quotation_decision(tokens[0], annotations), "outside")

    def test_a_curated_example_must_resolve_to_a_unique_counted_hit(self):
        with tempfile.TemporaryDirectory(prefix="federalist-contexts-") as folder:
            root = Path(folder)
            (root / "metadata").mkdir()
            (root / "metadata/concordance_examples.csv").write_text(
                "word,essay_number,start_offset,construction,observation,selection_reason\n"
                "on,49,999,preposition,Invented note,Invented selection\n"
            )
            with self.assertRaises(ValueError):
                example_rows(root, [{"word": "on", "essay_number": 49, "start_offset": 0}])


class CorpusInspectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build_outputs(ROOT)

    def rows(self, name):
        return list(csv.DictReader(io.StringIO(self.outputs[name].decode("utf-8"))))

    def test_concordances_recover_every_count_and_point_to_exact_source_words(self):
        hits = self.rows("results/concordances.csv")
        by_group = {}
        texts = {}
        for row in hits:
            texts.setdefault(row["text_path"], (ROOT / row["text_path"]).read_text())
            self.assertEqual(texts[row["text_path"]][int(row["start_offset"]):int(row["end_offset"])],
                             row["matched_text"])
            key = (row["word"], row["essay_number"])
            by_group[key] = by_group.get(key, 0) + 1
        distribution = self.rows("results/feature_distribution.csv")
        self.assertEqual(len(distribution), 68)
        for row in distribution:
            self.assertEqual(by_group.get((row["word"], row["essay_number"]), 0), int(row["count"]))
            self.assertEqual(int(row["quotation_check_count"]),
                             int(row["count"]) - int(row["removed_quotation_count"]))

    def test_all_twenty_four_signed_components_reconstruct_the_saved_gap(self):
        rows = self.rows("results/feature_contributions.csv")
        self.assertEqual(len(rows), 24)
        gap = json.loads((ROOT / "results/questioned_profiles.json").read_text())["result"]["signed_gap"]
        self.assertTrue(math.isclose(math.fsum(float(r["contribution_to_mean_gap"]) for r in rows),
                                     gap, abs_tol=1e-14))
        self.assertEqual(sum(r["selected_for_context"] == "Yes" for r in rows), 4)

    def test_notes_cover_all_questioned_hits_and_all_reference_essays(self):
        examples = self.rows("results/concordance_examples.csv")
        hits = self.rows("results/concordances.csv")
        key = lambda row: (row["word"], row["essay_number"], row["start_offset"])
        self.assertEqual({key(r) for r in hits if r["essay_number"] == "49"},
                         {key(r) for r in examples if r["essay_number"] == "49"})
        self.assertEqual({r["essay_number"] for r in examples}, {r["essay_number"] for r in hits})


if __name__ == "__main__":
    unittest.main()
