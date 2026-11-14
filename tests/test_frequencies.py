"""Test denominators, comparable rates, exact count retention, and CSV precision."""

import csv
import io
import unittest

from src.calculate_frequencies import csv_bytes, measure_text, serialize_frequency
from src.word_features import load_specification


class FrequencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.specification = load_specification()

    def test_invented_planning_example_is_20_in_2000_giving_10_per_1000(self):
        text = "the " * 20 + "liberty " * 1980
        total, counts, frequencies = measure_text(text, self.specification)
        self.assertEqual(total, 2000)
        self.assertEqual(counts["the"], 20)
        self.assertEqual(frequencies["the"], 10)

    def test_nonfeature_words_remain_in_the_denominator(self):
        total, counts, frequencies = measure_text("The constitution and liberty.", self.specification)
        self.assertEqual(total, 4)
        self.assertEqual(counts["the"], 1)
        self.assertEqual(frequencies["the"], 250)
        self.assertEqual(frequencies["and"], 250)

    def test_different_length_texts_with_the_same_proportions_have_the_same_rates(self):
        short = measure_text("the liberty ", self.specification)
        long = measure_text("the liberty " * 4, self.specification)
        self.assertNotEqual(short[1]["the"], long[1]["the"])
        self.assertEqual(short[2], long[2])

    def test_missing_features_are_zero_counts_in_the_original_order(self):
        _, counts, frequencies = measure_text("liberty", self.specification)
        self.assertEqual(tuple(counts), self.specification.words)
        self.assertEqual(tuple(frequencies), self.specification.words)
        self.assertTrue(all(value == 0 for value in counts.values()))
        self.assertTrue(all(value == 0 for value in frequencies.values()))

    def test_no_word_tokens_rejects_the_essay_instead_of_dividing_by_zero(self):
        for text in ("", " \n\t", "1787, 49!"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                measure_text(text, self.specification)

    def test_counting_uses_the_frozen_normalization_and_whole_words(self):
        total, counts, frequencies = measure_text("THE the theme it’s is", self.specification)
        self.assertEqual(total, 5)
        self.assertEqual((counts["the"], counts["it"], counts["is"]), (2, 0, 1))
        self.assertEqual(frequencies["the"], 400)

    def test_repeating_decimal_is_not_rounded_before_export(self):
        _, _, frequencies = measure_text("the liberty constitution", self.specification)
        expected = 1 / 3 * 1000
        self.assertEqual(float(serialize_frequency(frequencies["the"])), expected)
        self.assertNotEqual(frequencies["the"], round(expected, 3))

    def test_decimal_format_preserves_values_without_a_leading_zero(self):
        self.assertEqual(serialize_frequency(.5), ".5")
        self.assertEqual(serialize_frequency(0.0), "0")
        for value in (.12345678901234567, 10.0, 1 / 3 * 1000):
            self.assertEqual(float(serialize_frequency(value)), value)

    def test_csv_keeps_essay_rows_separate_and_all_feature_columns(self):
        rows = []
        for number, text in ((1, "the liberty"), (6, "and liberty freedom")):
            total, counts, _ = measure_text(text, self.specification)
            rows.append({"essay_number": number, "role": "hamilton", "total_words": total, **counts})
        content = csv_bytes(rows, self.specification.words).decode("utf-8")
        reader = csv.DictReader(io.StringIO(content))
        actual = list(reader)
        self.assertEqual(len(actual), 2)
        self.assertEqual([row["total_words"] for row in actual], ["2", "3"])
        self.assertEqual([row["the"] for row in actual], ["1", "0"])
        self.assertEqual(reader.fieldnames[3:], list(self.specification.words))


if __name__ == "__main__":
    unittest.main()
