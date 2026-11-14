"""Compare No. 49 only after verified validation on all planned references.

Missing prerequisites produce a dated preflight record, never placeholder
distances or an assignment. Run with python -m src.compare_questioned.
"""

import argparse
import csv
from dataclasses import asdict
import hashlib
import io
import json
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from .distance_method import (
    QUESTIONED_ID, EssayFrequencies, compare_essay, fit_reference_profiles,
    frequency_vector, identifier,
)
from .validate_authors import (
    check_reference_set, expected_roles, json_bytes, load_references, number_text,
)
from .word_features import load_specification


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT_PATH = "results/questioned_preflight.json"
VALIDATION_FILES = (
    "results/validation.csv", "results/validation_summary.json",
    "results/validation_fits.json", "results/validation_manifest.json",
)
OUTPUT_PATHS = (
    "results/questioned.csv", "results/questioned_profiles.json",
    "results/questioned_manifest.json",
)


class PrerequisitesMissing(ValueError):
    pass


def compare_questioned(references, questioned, features, roles):
    """Fit the full reference sample without including the questioned text."""
    missing = check_reference_set(references, roles)
    if missing:
        raise ValueError("Missing planned references: " + ", ".join(missing))
    if identifier(questioned.essay_id) != str(QUESTIONED_ID) or questioned.role != "questioned":
        raise ValueError("The comparison target must be questioned No. 49.")
    frequency_vector(questioned, features)
    model = fit_reference_profiles(references, features, held_out_essay_id=QUESTIONED_ID)
    return model, compare_essay(model, questioned)


def require_completed_validation(summary, manifest):
    """Require completion, not a favorable accuracy threshold."""
    if (
        summary.get("status") != "complete" or summary.get("total_trials") != 16
        or manifest.get("status") != "complete" or manifest.get("trial_count") != 16
        or manifest.get("training_essays_per_trial") != 15
        or manifest.get("questioned_essay_excluded") != QUESTIONED_ID
        or manifest.get("questioned_essay_compared") is not False
    ):
        raise ValueError("Completed 16-trial validation excluding No. 49 is required.")
    own = [summary.get("by_author", {}).get(author, {}) for author in ("hamilton", "madison")]
    if any(item.get("total") != 8 for item in own):
        raise ValueError("Validation must cover 8 essays per author.")
    correct = summary.get("correct_assignments")
    if not isinstance(correct, int) or not 0 <= correct <= 16:
        raise ValueError("Validation correctness is missing or invalid.")
    if any(not isinstance(item.get("correct"), int) or not 0 <= item["correct"] <= 8 for item in own):
        raise ValueError("Per-author validation correctness is invalid.")
    if sum(item["correct"] for item in own) != correct:
        raise ValueError("Validation correctness totals disagree.")


def load_questioned(root, features):
    with (root / "results/frequencies.csv").open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["essay_number", "role", "total_words", *features]:
            raise ValueError("Frequency-table columns differ from the fixed features.")
        matches = [row for row in reader if int(row["essay_number"]) == QUESTIONED_ID]
    if len(matches) != 1 or matches[0]["role"] != "questioned":
        raise ValueError("Exactly one questioned No. 49 frequency row is required.")
    if int(matches[0]["total_words"]) <= 0:
        raise ValueError("No. 49 has an invalid total word count.")
    return EssayFrequencies(QUESTIONED_ID, "questioned", {
        word: float(matches[0][word]) for word in features
    })


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def preflight_inputs(root):
    names = (
        "docs/research_plan.md", "config/research.toml", "metadata/word_features.json",
        "metadata/distance_method.json", "results/frequency_manifest.json",
        "results/frequencies.csv", "src/compare_questioned.py", "tests/test_questioned.py",
    )
    return {name: digest(root / name) for name in names}


def record_block(root, reason):
    validation_path = root / "results/validation_preflight.json"
    validation = json.loads(validation_path.read_text("utf-8")) if validation_path.exists() else {}
    specification, roles = load_specification(root), expected_roles(root)
    references = load_references(root, specification.words, roles)
    missing = [int(key) for key in check_reference_set(references, roles)]
    record = {
        "stage": "questioned_essay_comparison_preflight",
        "recorded_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "blocked_validation_incomplete", "questioned_essay": QUESTIONED_ID,
        "reason": reason,
        "missing_reference_essays": missing,
        "available_reference_count": len(references),
        "required_reference_count": 16,
        "completed_validation_trials": 0,
        "hamilton_distance": None, "madison_distance": None,
        "signed_gap": None, "predicted_author": None,
        "corpus_profiles_fitted_by_this_command": False,
        "questioned_essay_compared": False,
        "input_sha256": preflight_inputs(root),
    }
    if (validation_path.exists() and validation.get("missing_essays") == missing
            and validation.get("available_reference_count") == len(references)):
        record["validation_preflight_sha256"] = digest(validation_path)
    path = root / PREFLIGHT_PATH
    if path.exists():
        previous = json.loads(path.read_text("utf-8"))
        comparable = lambda item: {key: value for key, value in item.items() if key != "recorded_at"}
        if comparable(previous) != comparable(record):
            raise ValueError("Existing comparison preflight differs; preserve it before recording a new state.")
    else:
        with path.open("xb") as handle:
            handle.write(json_bytes(record))


def verify_validation(root, check_only):
    command = [sys.executable, "-m", "src.validate_authors"]
    readiness = subprocess.run(
        [*command, "--check"], cwd=root, capture_output=True, text=True, timeout=30,
    )
    if readiness.returncode == 2:
        raise PrerequisitesMissing("Planned references are missing; the 16-trial validation has not run.")
    if readiness.returncode != 0:
        raise ValueError("Validation prerequisite check failed: " + readiness.stderr.strip())
    present = [(root / name).exists() for name in VALIDATION_FILES]
    if not any(present):
        if check_only:
            raise PrerequisitesMissing("Reference data are ready, but the 16-trial validation must run first.")
        subprocess.run(command, cwd=root, check=True, timeout=60)
    elif not all(present):
        raise ValueError("Validation artifacts are incomplete; preserve and investigate the existing records.")
    subprocess.run([*command, "--verify"], cwd=root, check=True, timeout=60)
    summary = json.loads((root / VALIDATION_FILES[1]).read_text("utf-8"))
    manifest = json.loads((root / VALIDATION_FILES[3]).read_text("utf-8"))
    require_completed_validation(summary, manifest)
    return summary


def questioned_csv(model, result, validation):
    row = {
        "essay_number": QUESTIONED_ID, "role": "questioned",
        "hamilton_distance": number_text(result.hamilton_distance),
        "madison_distance": number_text(result.madison_distance),
        "signed_gap": number_text(result.signed_gap),
        "absolute_gap": number_text(abs(result.signed_gap)),
        "predicted_author": result.prediction, "usable_feature_count": len(model.features),
        "excluded_features": ";".join(model.excluded_features),
        "validation_correct": validation["correct_assignments"], "validation_total": 16,
    }
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(row), lineterminator="\n")
    writer.writeheader()
    writer.writerow(row)
    return buffer.getvalue().encode("utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check prerequisites without comparing No. 49.")
    parser.add_argument("--verify", action="store_true", help="Recalculate and verify saved comparison outputs.")
    arguments = parser.parse_args()
    try:
        if arguments.check and arguments.verify:
            raise ValueError("Choose either --check or --verify.")
        try:
            validation = verify_validation(ROOT, arguments.check or arguments.verify)
        except PrerequisitesMissing as error:
            record_block(ROOT, str(error))
            parser.exit(2, f"Comparison cannot run: {error} No. 49 remains unassigned.\n")
        if arguments.check:
            print("Ready: completed validation verified; No. 49 has not been compared by this command.")
            return
        before = preflight_inputs(ROOT)
        before.update({name: digest(ROOT / name) for name in VALIDATION_FILES})
        specification, roles = load_specification(), expected_roles(ROOT)
        references = load_references(ROOT, specification.words, roles)
        questioned = load_questioned(ROOT, specification.words)
        model, result = compare_questioned(references, questioned, specification.words, roles)
        outputs = {
            OUTPUT_PATHS[0]: questioned_csv(model, result, validation),
            OUTPUT_PATHS[1]: json_bytes({
                "training_model": asdict(model), "questioned_essay": QUESTIONED_ID,
                "result": asdict(result), "validation_correct": validation["correct_assignments"],
            }),
        }
        current = preflight_inputs(ROOT)
        current.update({name: digest(ROOT / name) for name in VALIDATION_FILES})
        if current != before:
            raise ValueError("Comparison inputs changed during calculation.")
        output_hashes = {name: hashlib.sha256(content).hexdigest() for name, content in outputs.items()}
        manifest_path = ROOT / OUTPUT_PATHS[-1]
        if arguments.verify:
            recorded = json.loads(manifest_path.read_text("utf-8"))
            if recorded["input_sha256"] != before or recorded["output_sha256"] != output_hashes:
                raise ValueError("Saved comparison provenance differs from recalculation.")
            for name, content in outputs.items():
                if (ROOT / name).read_bytes() != content:
                    raise ValueError(f"Saved comparison output differs: {name}")
        else:
            for name in OUTPUT_PATHS:
                if (ROOT / name).exists():
                    raise ValueError(f"Comparison output exists; use --verify: {name}")
            manifest = {
                "stage": "questioned_essay_comparison", "status": "complete",
                "recorded_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                "runtime": {"python": platform.python_version()},
                "input_sha256": before, "output_sha256": output_hashes,
                "reference_essay_count": 16, "questioned_essay": QUESTIONED_ID,
                "validation_completed_before_comparison": True,
                "questioned_essay_used_for_fitting": False,
                "authorship_probability_calculated": False,
                "validation_correct": validation["correct_assignments"], "validation_total": 16,
            }
            for name, content in outputs.items():
                with (ROOT / name).open("xb") as handle:
                    handle.write(content)
            with manifest_path.open("xb") as handle:
                handle.write(json_bytes(manifest))
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        parser.exit(1, f"Questioned-text comparison failed: {error}\n")
    print(f"No. 49: Hamilton distance {number_text(result.hamilton_distance)}, "
          f"Madison distance {number_text(result.madison_distance)}; {result.prediction}.")
    print(f"Known-author validation: {validation['correct_assignments']} correct out of 16.")
    print("Distances describe resemblance under the fixed method, not an authorship probability.")


if __name__ == "__main__":
    main()
