"""Check that preparation removes apparatus without rewriting essay prose."""

import unittest

from src.prepare_texts import apply_edits, normalize_for_counting, prepare_text


HEADER = (
    "## Federalist No. 1\n\nTitle\nFor the Independent Journal.\n"
    "Author: Alexander Hamilton\nTo the People of the State of New York:\n"
)


class PreparationTests(unittest.TestCase):
    def test_historical_forms_case_and_quotations_are_preserved(self):
        prose = 'WE chuse the draught: "It is the people’s authority."\n'
        prepared, _ = prepare_text(HEADER + prose + "PUBLIUS.\n")
        self.assertEqual(prepared, prose)

    def test_header_words_inside_the_prose_are_retained(self):
        prose = 'The label "Author: Hamilton" and the name "PUBLIUS" are discussed.\n'
        prepared, _ = prepare_text(HEADER + prose + "PUBLIUS.\n")
        self.assertEqual(prepared, prose)

    def test_notes_after_signature_are_excluded_without_removing_body_quotes(self):
        prose = 'The body says "and the union."\n'
        raw = HEADER + prose + 'PUBLIUS.\n\n  1. Note: "another passage." 【9†Back to text】\n'
        prepared, edits = prepare_text(raw)
        self.assertEqual(prepared, prose)
        self.assertIn("exclude_appended_notes", [edit.operation for edit in edits])

    def test_numbered_argument_is_not_mistaken_for_an_appended_note(self):
        prose = 'The next power follows.\n4. "To admit new States into the Union."\n'
        prepared, _ = prepare_text(HEADER + prose + "PUBLIUS.\n")
        self.assertEqual(prepared, prose)

    def test_essay_without_signature_keeps_its_complete_last_paragraph(self):
        prose = "The argument.\nThe complete final paragraph.\n"
        prepared, _ = prepare_text(HEADER + prose)
        self.assertEqual(prepared, prose)

    def test_numeric_reader_reference_cannot_join_adjacent_words(self):
        prepared, _ = prepare_text(HEADER + "and【3†^{1}】or, the【4†^{2}】 union.\nPUBLIUS.\n")
        self.assertEqual(prepared, "and or, the union.\n")

    def test_missing_or_repeated_reader_address_requires_review(self):
        for raw in ("An unstructured text.", HEADER + "Body.\nTo the People of the State of New York:\n"):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                prepare_text(raw)

    def test_prose_after_signature_cannot_be_silently_discarded(self):
        with self.assertRaises(ValueError):
            prepare_text(HEADER + "Body.\nPUBLIUS.\nUnexpected additional argument.\n")

    def test_unknown_reader_markup_is_not_silently_deleted(self):
        with self.assertRaises(ValueError):
            prepare_text(HEADER + "The 【3†quoted wording】 remains.\nPUBLIUS.\n")

    def test_edit_log_reconstructs_the_exact_output(self):
        raw = HEADER + 'The【3†^{1}】 union says "be free."\n\nPUBLIUS.\n  1. A note.\n'
        prepared, edits = prepare_text(raw)
        self.assertEqual(apply_edits(raw, edits), prepared)
        reversed_text = raw
        for edit in reversed(edits):
            reversed_text = reversed_text[:edit.start] + edit.replacement + reversed_text[edit.end:]
        self.assertEqual(reversed_text, prepared)

    def test_final_newline_is_logged_when_absent(self):
        prepared, edits = prepare_text(HEADER + "The body")
        self.assertEqual(prepared, "The body\n")
        self.assertEqual(edits[-1].operation, "ensure_final_newline")

    def test_counting_normalization_is_separate_and_preserves_spelling(self):
        original = "WE chuse; it’s the people‘s draught."
        self.assertEqual(normalize_for_counting(original), "we chuse; it's the people's draught.")
        self.assertEqual(original, "WE chuse; it’s the people‘s draught.")


if __name__ == "__main__":
    unittest.main()
