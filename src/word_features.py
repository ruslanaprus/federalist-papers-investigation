"""Verify the fixed word features without reading or counting corpus texts.

Run from the repository root with: uv run --locked python -m src.word_features
"""

import argparse
from dataclasses import dataclass
import hashlib
import json
import platform
import re
import subprocess
import tomllib
from datetime import datetime
from pathlib import Path

from .prepare_texts import normalize_for_counting


ROOT = Path(__file__).resolve().parents[1]
RECORD = Path("metadata/word_features.json")


@dataclass(frozen=True)
class FeatureSpecification:
    words: tuple[str, ...]
    token_pattern: str
    feature_check_remove: tuple[str, ...]
    frequency_unit_words: int

    def as_dict(self):
        return {
            "main_features": list(self.words),
            "token_pattern": self.token_pattern,
            "encoding": "utf-8",
            "lowercase_for_counting": True,
            "normalize_curly_apostrophes": True,
            "remove_stopwords": False,
            "expand_contractions": False,
            "group_word_forms": False,
            "retain_body_quotations": True,
            "feature_check_remove": list(self.feature_check_remove),
            "feature_check_features": [
                word for word in self.words if word not in self.feature_check_remove
            ],
            "quotation_check_features": list(self.words),
            "planned_frequency_unit_words": self.frequency_unit_words,
        }


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_specification(root=ROOT):
    """Check configured features and word rules against the original plan."""
    settings = tomllib.loads((root / "config/research.toml").read_text("utf-8"))
    plan_path = root / settings["research"]["plan_path"]
    if digest(plan_path) != settings["research"]["plan_sha256"]:
        raise ValueError("The original research plan checksum has changed.")
    plan = plan_path.read_text("utf-8")
    lists = re.findall(r"^> ([a-z]+(?:, [a-z]+){23})$", plan, re.MULTILINE)
    if len(lists) != 1:
        raise ValueError("Cannot identify the fixed feature list in the plan.")
    counting = settings["counting"]
    words = tuple(counting["features"])
    if words != tuple(lists[0].split(", ")) or len(set(words)) != 24:
        raise ValueError("Configured words or their order differ from the fixed plan.")
    pattern = counting["token_pattern"]
    if f"\n{pattern}\n" not in plan:
        raise ValueError("The tokenizer differs from the planned word rule.")
    for name, expected in (
        ("lowercase", True), ("normalize_curly_apostrophes", True),
        ("expand_contractions", False), ("remove_stopwords", False),
        ("retain_quotations", True),
    ):
        if counting[name] is not expected:
            raise ValueError(f"Counting setting differs from the plan: {name}")
    if counting["encoding"] != "utf-8" or counting["frequency_per_words"] != 1000:
        raise ValueError("Encoding or planned frequency unit differs from the plan.")
    check = re.search(r"^\| Feature check \|([^\n]+)$", plan, re.MULTILINE)
    if check is None:
        raise ValueError("The predefined feature check is missing from the plan.")
    removed = tuple(settings["robustness"]["feature_check"]["remove_features"])
    if removed != tuple(re.findall(r"`([a-z]+)`", check.group(1))):
        raise ValueError("The robustness feature selection differs from the plan.")
    return FeatureSpecification(words, pattern, removed, counting["frequency_per_words"])


def tokenize_words(text, specification):
    """Return all word tokens, including words outside the selected features."""
    return re.findall(specification.token_pattern, normalize_for_counting(text))


def input_fingerprints():
    return {
        name: digest(ROOT / name)
        for name in (
            "docs/research_plan.md", "config/research.toml", ".python-version",
            "pyproject.toml", "uv.lock", "src/word_features.py", "src/prepare_texts.py",
        )
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-record", action="store_true",
        help="Create the feature record once; never replace an existing record.",
    )
    arguments = parser.parse_args()
    try:
        specification = load_specification()
        fingerprints = input_fingerprints()
        path = ROOT / RECORD
        if arguments.write_record:
            uv_version = subprocess.run(
                ["uv", "--version"], check=True, capture_output=True,
                text=True, timeout=30,
            ).stdout.strip()
            record = {
                "stage": "fixed_word_features",
                "recorded_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                "selection_origin": "Original research plan, version 1; selection unchanged",
                "specification": specification.as_dict(),
                "runtime": {
                    "python": platform.python_version(), "uv": uv_version,
                    "operating_system": platform.platform(),
                },
                "input_sha256": fingerprints,
                "corpus_texts_read_by_this_command": False,
                "essay_word_counts_calculated": False,
                "authorship_analysis_performed": False,
            }
            with path.open("x", encoding="utf-8") as handle:
                json.dump(record, handle, indent=2, ensure_ascii=False)
                handle.write("\n")
        else:
            record = json.loads(path.read_text("utf-8"))
            if record["specification"] != specification.as_dict():
                raise ValueError("The saved feature specification has changed.")
            if record["input_sha256"] != fingerprints:
                raise ValueError("Feature rules or implementation inputs changed since recording.")
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        parser.exit(1, f"Feature check failed: {error}\n")
    print("Verified 24 main features and the predefined 20-feature check.")
    print("Features: " + ", ".join(specification.words))
    print("No corpus texts read; no essay word counts or attribution calculated.")


if __name__ == "__main__":
    main()
