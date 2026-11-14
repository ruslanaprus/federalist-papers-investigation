"""Guard against incomplete retrievals and incorrect essay boundaries."""

import unittest

from src.assemble_corpus import UnavailablePage, extract_section, project_lines


class ReaderIntegrityTests(unittest.TestCase):
    def test_shortened_overlap_is_recovered_without_adding_an_ellipsis(self):
        snapshot = {
            "source_url": "https://guides.loc.gov/example",
            "total_lines": 2,
            "responses": [
                {"response": "Total lines: 2\nL0: Original spelling\nL1: The consti..."},
                {"response": "Total lines: 2\nL1: The constitution remains."},
            ],
        }
        lines, resolved = project_lines(snapshot)
        self.assertEqual(lines[-1], "The constitution remains.")
        self.assertEqual(resolved, [1])

    def test_missing_line_is_not_silently_skipped(self):
        snapshot = {
            "source_url": "https://guides.loc.gov/example",
            "total_lines": 3,
            "responses": [{"response": "L0: First\nL2: Third"}],
        }
        with self.assertRaises(UnavailablePage):
            project_lines(snapshot)

    def test_conflicting_wording_is_not_resolved_by_selecting_a_longer_line(self):
        snapshot = {
            "source_url": "https://guides.loc.gov/example",
            "total_lines": 1,
            "responses": [
                {"response": "L0: The union."},
                {"response": "L0: A different union."},
            ],
        }
        with self.assertRaises(ValueError):
            project_lines(snapshot)

    def test_failed_retrieval_cannot_become_an_empty_essay(self):
        snapshot = {"source_url": "https://guides.loc.gov/example", "total_lines": None}
        with self.assertRaises(UnavailablePage):
            project_lines(snapshot)


class SectionBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.lines = [
            "## Federalist No. 1", "Title", "Author: Alexander Hamilton",
            "To the People of the State of New York:",
            "The original body.", "PUBLIUS.", "A source footnote.", "",
            "## Federalist No. 2", "Author: John Jay", "Another essay.",
        ]

    def test_neighboring_essay_is_excluded_while_source_apparatus_is_retained(self):
        content, start, end = extract_section(self.lines, 1, "Author: Alexander Hamilton")
        self.assertIn(b"PUBLIUS.\nA source footnote.", content)
        self.assertNotIn(b"John Jay", content)
        self.assertEqual((start, end), (0, 6))

    def test_wrong_reference_author_is_rejected(self):
        with self.assertRaises(ValueError):
            extract_section(self.lines, 1, "Author: James Madison")

    def test_absent_signature_is_not_invented_and_footer_is_excluded(self):
        lines = self.lines[:5] + ["", "  * 【4†<< Previous: Index】", "Hosted by publisher"]
        content, _, _ = extract_section(lines, 1, "Author: Alexander Hamilton")
        self.assertTrue(content.endswith(b"The original body.\n"))
        self.assertNotIn(b"PUBLIUS", content)
        self.assertNotIn(b"Hosted by", content)


if __name__ == "__main__":
    unittest.main()
