"""Calculate separate essay counts and frequencies per 1,000 total words.

Run from the repository root with uv run --locked python -m src.calculate_frequencies.
No author profiles, validation, distances, or predictions are calculated here.
"""

import argparse
from collections import Counter
import csv
import hashlib
import io
import json
import platform
import subprocess
import sys
import tomllib
from datetime import datetime
from pathlib import Path

from .word_features import load_specification, tokenize_words


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATHS = (
    "results/counts.csv",
    "results/frequencies.csv",
    "results/frequency_manifest.json",
)


def sha256(content):
    return hashlib.sha256(content).hexdigest()


def measure_text(text, specification):
    """Use one unchanged token stream for the denominator and all features."""
    tokens = tokenize_words(text, specification)
    total = len(tokens)
    if total == 0:
        raise ValueError("Essay contains no word tokens; a frequency cannot be calculated.")
    inventory = Counter(tokens)
    counts = {word: inventory[word] for word in specification.words}
    frequencies = {
        word: count / total * specification.frequency_unit_words
        for word, count in counts.items()
    }
    return total, counts, frequencies


def serialize_frequency(value):
    """Keep round-trip float precision and omit a leading zero in decimals."""
    if value == 0:
        return "0"
    text = repr(value)
    return text[1:] if text.startswith("0.") else text


def csv_bytes(rows, words):
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        buffer, fieldnames=["essay_number", "role", "total_words", *words],
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def build_tables(root):
    specification = load_specification(root)
    settings = tomllib.loads((root / "config/research.toml").read_text("utf-8"))
    preparation = json.loads((root / "results/preparation_manifest.json").read_text("utf-8"))
    expected_roles = {
        number: role for role in ("hamilton", "madison")
        for number in settings["corpus"][role]
    }
    expected_roles[settings["corpus"]["questioned"]] = "questioned"
    if len(expected_roles) != 17:
        raise ValueError("The configured fixed corpus must contain 17 distinct essays.")
    essays = sorted(preparation["essays"], key=lambda item: item["essay_number"])
    numbers = [item["essay_number"] for item in essays]
    if not numbers or len(numbers) != len(set(numbers)):
        raise ValueError("Prepared essay records are empty or contain duplicates.")
    missing = sorted(set(expected_roles) - set(numbers))
    if missing != sorted(item["essay_number"] for item in preparation["missing_essays"]):
        raise ValueError("Prepared corpus and its missing-essay record disagree.")
    count_rows, frequency_rows, summaries = [], [], []
    for essay in essays:
        number, role = essay["essay_number"], essay["role"]
        if expected_roles.get(number) != role:
            raise ValueError(f"Unexpected corpus role for No. {number}.")
        path = root / essay["prepared_path"]
        content = path.read_bytes()
        if sha256(content) != essay["prepared_sha256"]:
            raise ValueError(f"Prepared text checksum mismatch: {essay['prepared_path']}")
        total, counts, frequencies = measure_text(content.decode("utf-8"), specification)
        identity = {"essay_number": number, "role": role, "total_words": total}
        count_rows.append({**identity, **counts})
        frequency_rows.append({
            **identity,
            **{word: serialize_frequency(value) for word, value in frequencies.items()},
        })
        summaries.append({
            **identity, "prepared_path": essay["prepared_path"],
            "prepared_sha256": sha256(content),
        })
    outputs = {
        "results/counts.csv": csv_bytes(count_rows, specification.words),
        "results/frequencies.csv": csv_bytes(frequency_rows, specification.words),
    }
    return specification, outputs, summaries, missing


def input_fingerprints(root):
    names = (
        "docs/research_plan.md", "config/research.toml", ".python-version",
        "pyproject.toml", "uv.lock", "metadata/sources.csv",
        "metadata/preparation.csv", "metadata/word_features.json",
        "results/corpus_collection_manifest.json", "results/preparation_manifest.json",
    )
    paths = [root / name for name in names]
    paths.extend(sorted((root / "data/clean").glob("*.txt")))
    return {path.relative_to(root).as_posix(): sha256(path.read_bytes()) for path in paths}


def verify_prerequisites(root, allow_incomplete):
    subprocess.run(
        [sys.executable, "-m", "src.word_features"], cwd=root, check=True, timeout=30,
    )
    command = [sys.executable, str(root / "src/prepare_texts.py"), "--verify"]
    if allow_incomplete:
        command.append("--allow-incomplete")
    subprocess.run(command, cwd=root, check=True, timeout=30)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="Recalculate and check saved tables without writing.")
    parser.add_argument(
        "--allow-incomplete", action="store_true",
        help="Explicitly allow descriptive tables for available essays; keep missing texts recorded.",
    )
    arguments = parser.parse_args()
    try:
        verify_prerequisites(ROOT, arguments.allow_incomplete)
        before = input_fingerprints(ROOT)
        specification, outputs, essays, missing = build_tables(ROOT)
        if missing and not arguments.allow_incomplete:
            raise ValueError("The fixed corpus is incomplete.")
        if input_fingerprints(ROOT) != before:
            raise ValueError("Counting inputs changed while tables were calculated.")
        hashes = {name: sha256(content) for name, content in outputs.items()}
        manifest_path = ROOT / OUTPUT_PATHS[-1]
        if arguments.verify:
            manifest = json.loads(manifest_path.read_text("utf-8"))
            if manifest["input_sha256"] != before or manifest["output_sha256"] != hashes:
                raise ValueError("Counting inputs or saved output fingerprints have changed.")
            if manifest["essays"] != essays or manifest["missing_essays"] != missing:
                raise ValueError("Essay records differ from the frequency manifest.")
            for name, expected in outputs.items():
                if (ROOT / name).read_bytes() != expected:
                    raise ValueError(f"Saved table differs from recalculation: {name}")
        else:
            for name in OUTPUT_PATHS:
                if (ROOT / name).exists():
                    raise ValueError(f"Output exists; refusing to replace {name}. Use --verify.")
            uv_version = subprocess.run(
                ["uv", "--version"], check=True, capture_output=True,
                text=True, timeout=30,
            ).stdout.strip()
            revision = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True,
                capture_output=True, text=True, timeout=30,
            ).stdout.strip()
            status = subprocess.run(
                ["git", "status", "--porcelain=v1", "--untracked-files=all"],
                cwd=ROOT, check=True, capture_output=True, text=True, timeout=30,
            ).stdout.rstrip("\n")
            manifest = {
                "stage": "per_essay_counts_and_frequencies",
                "recorded_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                "status": "incomplete_corpus" if missing else "complete",
                "planned_essay_count": 17, "measured_essay_count": len(essays),
                "missing_essays": missing,
                "rows_by_role": dict(Counter(essay["role"] for essay in essays)),
                "formula": "word_count / total_word_tokens * 1000",
                "denominator": "All tokens from the same tokenizer used for feature counts",
                "precision": "Python binary64; repr round-trip decimals without pre-rounding",
                "exact_recalculation": "Integer counts and total_words preserve the exact ratios",
                "specification": specification.as_dict(),
                "runtime": {
                    "python": platform.python_version(), "uv": uv_version,
                    "operating_system": platform.platform(),
                },
                "git": {
                    "revision": revision, "working_tree_dirty": bool(status),
                    "status_porcelain": status.splitlines(),
                },
                "code_sha256": {
                    path.relative_to(ROOT).as_posix(): sha256(path.read_bytes())
                    for folder in ("src", "tests")
                    for path in sorted((ROOT / folder).glob("*.py"))
                },
                "input_sha256": before, "output_sha256": hashes, "essays": essays,
                "author_profiles_calculated": False,
                "known_author_validation_performed": False,
                "authorship_comparison_performed": False,
            }
            for name, content in outputs.items():
                with (ROOT / name).open("xb") as handle:
                    handle.write(content)
            with manifest_path.open("x", encoding="utf-8") as handle:
                json.dump(manifest, handle, indent=2, ensure_ascii=False)
                handle.write("\n")
        if input_fingerprints(ROOT) != before:
            raise ValueError("Counting inputs changed during output verification.")
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        parser.exit(1, f"Frequency calculation failed: {error}\n")
    action = "Verified" if arguments.verify else "Saved"
    print(f"{action} separate counts and frequencies for {len(essays)} of 17 planned essays.")
    if missing:
        print("INCOMPLETE: missing " + ", ".join(f"No. {number}" for number in missing))
    print("Rates are per 1,000 total words; no author profiles or comparisons calculated.")


if __name__ == "__main__":
    main()
