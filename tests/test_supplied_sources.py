"""Verify supplied texts are attributable and immutable without normalizing them."""

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from src.assemble_corpus import supplied_source


class SuppliedSourceTests(unittest.TestCase):
    def test_original_breaks_and_final_newline_state_are_preserved(self):
        payload = (
            'Federalist No. 21\nTitle\nAuthor: Alexander Hamilton\n'
            'To the People of the State of New York:\n"four\n\n."\nPUBLIUS.'
        ).encode()
        with tempfile.TemporaryDirectory(prefix="federalist-supplied-") as directory:
            root = Path(directory)
            (root / "metadata").mkdir()
            (root / "raw.txt").write_bytes(payload)
            entry = {"essay_number": 21, "raw_path": "raw.txt", "sha256": hashlib.sha256(payload).hexdigest()}
            (root / "metadata/supplied_sources.json").write_text(json.dumps({"sources": [entry]}))
            _, actual = supplied_source(root, 21, "Author: Alexander Hamilton")
            self.assertEqual(actual, payload)
            (root / "raw.txt").write_bytes(payload + b"\n")
            with self.assertRaises(ValueError):
                supplied_source(root, 21, "Author: Alexander Hamilton")

    def test_wrong_essay_or_author_cannot_fill_a_missing_reference(self):
        with tempfile.TemporaryDirectory(prefix="federalist-supplied-") as directory:
            root = Path(directory)
            (root / "metadata").mkdir()
            for title, author in (("Federalist No. 26", "Alexander Hamilton"), ("Federalist No. 21", "James Madison")):
                with self.subTest(title=title, author=author):
                    payload = f"{title}\nAuthor: {author}\nTo the People of the State of New York:\nBody.\nPUBLIUS.".encode()
                    (root / "raw.txt").write_bytes(payload)
                    entry = {"essay_number": 21, "raw_path": "raw.txt", "sha256": hashlib.sha256(payload).hexdigest()}
                    (root / "metadata/supplied_sources.json").write_text(json.dumps({"sources": [entry]}))
                    with self.assertRaises(ValueError):
                        supplied_source(root, 21, "Author: Alexander Hamilton")
