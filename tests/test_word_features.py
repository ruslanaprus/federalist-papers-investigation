"""Test feature preservation, word boundaries, and rejection of method drift."""

from pathlib import Path
import tempfile
import unittest

from src.word_features import ROOT, load_specification, tokenize_words


class WordRuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.specification = load_specification()

    def test_invented_planning_example_uses_the_fixed_word_rule(self):
        self.assertEqual(
            tokenize_words("The theme is clear; it's clear.", self.specification),
            ["the", "theme", "is", "clear", "it's", "clear"],
        )

    def test_features_are_not_substrings_of_longer_tokens(self):
        tokens = tokenize_words("theme order within being and the or in be", self.specification)
        selected = [word for word in tokens if word in self.specification.words]
        self.assertEqual(selected, ["and", "the", "or", "in", "be"])

    def test_contractions_do_not_create_unwritten_feature_words(self):
        self.assertEqual(
            tokenize_words("It’s isn't THAT‘S", self.specification),
            ["it's", "isn't", "that's"],
        )

    def test_quotation_delimiters_do_not_hide_a_whole_word(self):
        self.assertEqual(tokenize_words("'the' “and”", self.specification), ["the", "and"])

    def test_hyphens_numbers_and_punctuation_follow_the_planned_rule(self):
        self.assertEqual(
            tokenize_words("the-and, in/on; 1787 49", self.specification),
            ["the", "and", "in", "on"],
        )

    def test_common_words_and_nonfeatures_both_remain_in_the_token_stream(self):
        self.assertEqual(
            tokenize_words("The constitution and liberty.", self.specification),
            ["the", "constitution", "and", "liberty"],
        )

    def test_historical_forms_are_not_modernized_or_grouped(self):
        self.assertEqual(
            tokenize_words("CHUSE draught is be being", self.specification),
            ["chuse", "draught", "is", "be", "being"],
        )

    def test_grammatical_role_does_not_change_a_spelling_feature(self):
        tokens = tokenize_words("That book shows that it is useful.", self.specification)
        self.assertEqual([word for word in tokens if word == "that"], ["that", "that"])


class FeatureDriftTests(unittest.TestCase):
    def test_reordering_or_changing_counting_rules_is_rejected(self):
        original = (ROOT / "config/research.toml").read_text("utf-8")
        changes = (
            ('"the", "a", "an"', '"a", "the", "an"'),
            ("remove_stopwords = false", "remove_stopwords = true"),
            ("expand_contractions = false", "expand_contractions = true"),
            ("lowercase = true", "lowercase = false"),
            ('token_pattern = "[a-z]+(?:\'[a-z]+)*"', 'token_pattern = "[a-z]+"'),
        )
        with tempfile.TemporaryDirectory(prefix="federalist-features-") as folder:
            root = Path(folder)
            (root / "config").mkdir()
            (root / "docs").mkdir()
            (root / "docs/research_plan.md").write_bytes((ROOT / "docs/research_plan.md").read_bytes())
            for before, after in changes:
                with self.subTest(setting=before):
                    changed = original.replace(before, after, 1)
                    self.assertNotEqual(changed, original)
                    (root / "config/research.toml").write_text(changed, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        load_specification(root)


if __name__ == "__main__":
    unittest.main()
