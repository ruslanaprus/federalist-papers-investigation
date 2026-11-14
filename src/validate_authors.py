"""Run the fixed 16-trial validation before any comparison of No. 49.

Incomplete reference samples stop before fitting. There is no partial-sample
override. Tests exercise the workflow with invented frequencies.
"""

import argparse
from collections import Counter
import csv
from dataclasses import asdict, dataclass
import hashlib
import io
import json
import math
import platform
import statistics
import subprocess
import sys
import tomllib
from datetime import datetime
from pathlib import Path

from .distance_method import (
    DistanceResult, EssayFrequencies, FittedProfiles, QUESTIONED_ID,
    compare_essay, fit_reference_profiles, identifier,
)
from .word_features import load_specification


ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = "results/validation_preflight.json"
OUTPUT_PATHS = (
    "results/validation.csv", "results/validation_summary.json",
    "results/validation_fits.json", "results/validation_manifest.json",
)


@dataclass(frozen=True)
class ValidationTrial:
    essay_id: int | str
    reference_author: str
    score: DistanceResult
    model: FittedProfiles


def expected_roles(root):
    settings = tomllib.loads((root / "config/research.toml").read_text("utf-8"))
    if settings["validation"] != {
        "method": "leave_one_essay_out",
        "fit_scaling_within_each_trial": True,
        "count_inconclusive_as_correct": False,
        "run_before_questioned_comparison": True,
    }:
        raise ValueError("Validation settings differ from the fixed plan.")
    return {
        identifier(number): author
        for author in ("hamilton", "madison") for number in settings["corpus"][author]
    }


def check_reference_set(references, roles):
    """Validate identities and labels, returning the missing reference IDs."""
    roles = {identifier(key): value for key, value in roles.items()}
    if len(roles) != 16 or Counter(roles.values()) != {"hamilton": 8, "madison": 8}:
        raise ValueError("The fixed evaluation requires 8 references per author.")
    if str(QUESTIONED_ID) in roles:
        raise ValueError("No. 49 cannot be a reference essay.")
    seen = set()
    for essay in references:
        key = identifier(essay.essay_id)
        if key in seen:
            raise ValueError(f"Duplicate reference essay: {key}")
        if key not in roles or essay.role != roles[key]:
            raise ValueError(f"Unexpected reference identity or author: {key}")
        seen.add(key)
    return tuple(sorted(set(roles) - seen, key=int))


def load_references(root, features, roles):
    """Read reference frequencies only; never parse No. 49's feature values."""
    references, seen = [], set()
    with (root / "results/frequencies.csv").open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["essay_number", "role", "total_words", *features]:
            raise ValueError("Frequency table columns differ from the fixed feature order.")
        for row in reader:
            number = int(row["essay_number"])
            if number in seen:
                raise ValueError(f"Duplicate frequency-table essay: {number}")
            seen.add(number)
            if number == QUESTIONED_ID:
                if row["role"] != "questioned":
                    raise ValueError("No. 49 must retain its questioned role.")
                continue
            if roles.get(str(number)) != row["role"]:
                raise ValueError(f"Unexpected reference row: {number}")
            if int(row["total_words"]) <= 0:
                raise ValueError(f"Invalid total word count for No. {number}.")
            values = {word: float(row[word]) for word in features}
            if any(not math.isfinite(value) or not 0 <= value <= 1000 for value in values.values()):
                raise ValueError(f"Invalid frequencies for No. {number}.")
            references.append(EssayFrequencies(number, row["role"], values))
    return tuple(sorted(references, key=lambda row: int(row.essay_id)))


def run_leave_one_out(references, features, roles):
    references = tuple(references)
    missing = check_reference_set(references, roles)
    if missing:
        raise ValueError("Missing planned references: " + ", ".join(missing))
    trials = []
    for held_out in references:
        held_id = identifier(held_out.essay_id)
        training = tuple(row for row in references if identifier(row.essay_id) != held_id)
        model = fit_reference_profiles(training, features, held_out_essay_id=held_out.essay_id)
        score = compare_essay(model, held_out)
        trials.append(ValidationTrial(held_out.essay_id, held_out.role, score, model))
    return tuple(trials)


def summarize_trials(trials):
    if len(trials) != 16 or len({identifier(trial.essay_id) for trial in trials}) != 16:
        raise ValueError("A validation summary requires 16 distinct completed trials.")
    by_author = {}
    for author in ("hamilton", "madison"):
        own = [trial for trial in trials if trial.reference_author == author]
        if len(own) != 8:
            raise ValueError("The completed trials must include 8 essays per author.")
        by_author[author] = {
            "correct": sum(trial.score.prediction == author for trial in own), "total": 8,
        }
    correct = sum(item["correct"] for item in by_author.values())
    gaps = [abs(trial.score.signed_gap) for trial in trials]
    return {
        "status": "complete", "correct_assignments": correct, "total_trials": 16,
        "by_author": by_author,
        "misclassified_essays": [
            trial.essay_id for trial in trials
            if trial.score.prediction not in {trial.reference_author, "inconclusive"}
        ],
        "inconclusive_essays": [
            trial.essay_id for trial in trials if trial.score.prediction == "inconclusive"
        ],
        "inconclusive_counted_as_correct": False,
        "baseline": {"correct": 8, "total": 16, "rule": "Always choose one author"},
        "correct_assignments_above_baseline": correct > 8,
        "absolute_gap_summary": {
            "minimum": min(gaps), "median": statistics.median(gaps), "maximum": max(gaps),
        },
        "substantive_close_gap_threshold": None,
        "universal_accuracy_threshold": None,
        "trials_are_independent": False,
        "questioned_essay_compared": False,
    }


def number_text(value):
    if value == 0:
        return "0"
    text = repr(value)
    if text.startswith("0."):
        return text[1:]
    return "-" + text[2:] if text.startswith("-0.") else text


def validation_csv(trials):
    fields = (
        "held_out_essay", "reference_author", "predicted_author", "correct",
        "hamilton_distance", "madison_distance", "signed_gap", "absolute_gap",
        "usable_feature_count", "excluded_features", "training_hamilton_count",
        "training_madison_count",
    )
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for trial in trials:
        model, score = trial.model, trial.score
        writer.writerow({
            "held_out_essay": trial.essay_id, "reference_author": trial.reference_author,
            "predicted_author": score.prediction,
            "correct": "Yes" if score.prediction == trial.reference_author else "No",
            "hamilton_distance": number_text(score.hamilton_distance),
            "madison_distance": number_text(score.madison_distance),
            "signed_gap": number_text(score.signed_gap),
            "absolute_gap": number_text(abs(score.signed_gap)),
            "usable_feature_count": len(model.features),
            "excluded_features": ";".join(model.excluded_features),
            "training_hamilton_count": model.hamilton_essay_count,
            "training_madison_count": model.madison_essay_count,
        })
    return buffer.getvalue().encode("utf-8")


def json_bytes(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprints(root):
    return {
        name: digest(root / name)
        for name in (
            "docs/research_plan.md", "config/research.toml", "metadata/word_features.json",
            "metadata/distance_method.json", "results/frequency_manifest.json",
            "results/frequencies.csv", "src/validate_authors.py", "tests/test_validation.py",
        )
    }


def verify_prerequisites(root):
    subprocess.run(
        [sys.executable, "-m", "src.distance_method"], cwd=root, check=True, timeout=30,
    )
    recorded = json.loads((root / "results/frequency_manifest.json").read_text("utf-8"))
    for section in ("input_sha256", "output_sha256", "code_sha256"):
        for name, expected in recorded[section].items():
            if digest(root / name) != expected:
                raise ValueError(f"Frequency provenance check failed: {name}")


def blocked_record(root, references, roles, missing, inputs):
    record = {
        "stage": "known_author_validation_preflight",
        "recorded_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "runtime": {"python": platform.python_version()},
        "status": "blocked_missing_reference_essays",
        "expected_reference_count": 16, "available_reference_count": len(references),
        "by_author": {
            author: {"expected": 8, "available": sum(row.role == author for row in references)}
            for author in ("hamilton", "madison")
        },
        "missing_essays": [int(key) for key in missing],
        "missing_source_urls": sorted({
            "https://guides.loc.gov/federalist-papers/text-"
            f"{((int(key) - 1) // 10) * 10 + 1}-{((int(key) - 1) // 10) * 10 + 10}"
            for key in missing
        }),
        "completed_validation_trials": 0, "correct_assignments": None,
        "accuracy": None, "corpus_profiles_fitted": False,
        "questioned_essay_compared": False,
        "input_sha256": inputs,
        "planned_baseline": {"correct": 8, "total": 16, "is_observed_result": False},
        "resolution": "Collect, prepare, and count the missing planned reference essays before validation.",
    }
    path = root / STATUS_PATH
    if path.exists():
        previous = json.loads(path.read_text("utf-8"))
        comparable = {key: value for key, value in record.items() if key != "recorded_at"}
        if comparable != {key: value for key, value in previous.items() if key != "recorded_at"}:
            raise ValueError("An existing preflight record differs; preserve it before recording a new state.")
    else:
        with path.open("xb") as handle:
            handle.write(json_bytes(record))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check prerequisites without fitting any profiles.")
    parser.add_argument("--verify", action="store_true", help="Recalculate and check completed validation artifacts.")
    arguments = parser.parse_args()
    try:
        if arguments.check and arguments.verify:
            raise ValueError("Choose either --check or --verify.")
        verify_prerequisites(ROOT)
        before = fingerprints(ROOT)
        specification, roles = load_specification(), expected_roles(ROOT)
        references = load_references(ROOT, specification.words, roles)
        missing = check_reference_set(references, roles)
        if missing:
            blocked_record(ROOT, references, roles, missing, before)
            parser.exit(
                2, "Validation cannot run: missing planned reference essays "
                + ", ".join(missing) + ". No validation scores or No. 49 comparison calculated.\n",
            )
        if arguments.check:
            print("Ready: all 16 planned references are available; no profiles fitted.")
            return
        trials = run_leave_one_out(references, specification.words, roles)
        summary = summarize_trials(trials)
        fits = [
            {"held_out_essay": trial.essay_id, "training_model": asdict(trial.model)}
            for trial in trials
        ]
        outputs = {
            OUTPUT_PATHS[0]: validation_csv(trials),
            OUTPUT_PATHS[1]: json_bytes(summary), OUTPUT_PATHS[2]: json_bytes(fits),
        }
        if fingerprints(ROOT) != before:
            raise ValueError("Validation inputs changed during the trials.")
        hashes = {name: hashlib.sha256(content).hexdigest() for name, content in outputs.items()}
        manifest_path = ROOT / OUTPUT_PATHS[-1]
        if arguments.verify:
            recorded = json.loads(manifest_path.read_text("utf-8"))
            if recorded["input_sha256"] != before or recorded["output_sha256"] != hashes:
                raise ValueError("Completed validation fingerprints have changed.")
            for name, content in outputs.items():
                if (ROOT / name).read_bytes() != content:
                    raise ValueError(f"Completed validation output differs: {name}")
        else:
            for name in OUTPUT_PATHS:
                if (ROOT / name).exists():
                    raise ValueError(f"Validation output exists; use --verify: {name}")
            manifest = {
                "stage": "known_author_validation", "status": "complete",
                "recorded_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                "runtime": {"python": platform.python_version()},
                "feature_order": list(specification.words),
                "input_sha256": before, "output_sha256": hashes,
                "trial_count": 16, "training_essays_per_trial": 15,
                "questioned_essay_excluded": QUESTIONED_ID,
                "questioned_essay_compared": False,
            }
            for name, content in outputs.items():
                with (ROOT / name).open("xb") as handle:
                    handle.write(content)
            with manifest_path.open("xb") as handle:
                handle.write(json_bytes(manifest))
        if fingerprints(ROOT) != before:
            raise ValueError("Validation inputs changed during output verification.")
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        parser.exit(1, f"Validation failed: {error}\n")
    print(f"Validation: {summary['correct_assignments']} correct out of 16; baseline 8 out of 16.")
    print("No. 49 was excluded from all trials and has not been compared.")


if __name__ == "__main__":
    main()
