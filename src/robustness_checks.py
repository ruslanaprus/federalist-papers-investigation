"""Run both predefined variants without changing main-analysis artifacts.

Run with uv run --locked python -m src.robustness_checks; use --verify to
recompute every output without writing. Quotation decisions must exist first.
"""

import argparse
import csv
from dataclasses import asdict
from datetime import datetime
import hashlib
import io
import json
from pathlib import Path
import platform
import subprocess
import sys

from .calculate_frequencies import csv_bytes, measure_text, serialize_frequency
from .compare_questioned import compare_questioned, questioned_csv
from .distance_method import EssayFrequencies
from .validate_authors import (
    expected_roles, json_bytes, run_leave_one_out, summarize_trials, validation_csv,
)
from .word_features import load_specification


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "results/robustness_manifest.json"
MARKS = frozenset('\"“”')
ANNOTATION_FIELDS = [
    "essay_number", "text_path", "start_offset", "end_offset", "quoted_text",
    "decision", "reason", "source_url",
]


def sha(content):
    return hashlib.sha256(content).hexdigest()


def remove_annotated_spans(text, annotations):
    """Validate all annotated boundaries; replace only remove spans by spaces.

    Every double quotation mark must be accounted for exactly once. Retained
    annotations are also checked. Apostrophes do not determine boundaries.
    """
    previous_end, accounted, parts, cursor = 0, set(), [], 0
    for row in sorted(annotations, key=lambda item: int(item["start_offset"])):
        start, end = int(row["start_offset"]), int(row["end_offset"])
        if not 0 <= start < end <= len(text) or start < previous_end:
            raise ValueError("Invalid, overlapping, or duplicate quotation offsets.")
        if text[start:end] != row["quoted_text"]:
            raise ValueError("Quotation annotation differs from the exact prepared text.")
        if text[start] not in MARKS or text[end - 1] not in MARKS:
            raise ValueError("Quotation boundaries must include their enclosing marks.")
        if row["decision"] not in {"remove", "retain"} or not row["reason"].strip():
            raise ValueError("Every quotation needs a valid decision and reason.")
        accounted.update(i for i in range(start, end) if text[i] in MARKS)
        if row["decision"] == "remove":
            parts.extend((text[cursor:start], " "))
            cursor = end
        previous_end = end
    if accounted != {i for i, char in enumerate(text) if char in MARKS}:
        raise ValueError("Quotation review leaves unannotated double quotation marks.")
    parts.append(text[cursor:])
    return "".join(parts)


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def load_annotations(root, sources):
    review = json.loads((root / "metadata/quotation_review.json").read_text("utf-8"))
    annotation_bytes = (root / "metadata/quotations.csv").read_bytes()
    if sha(annotation_bytes) != review["annotation_sha256"]:
        raise ValueError("Quotation decisions differ from their completed review record.")
    fields, rows = read_csv(root / "metadata/quotations.csv")
    if fields != ANNOTATION_FIELDS:
        raise ValueError("Unexpected quotation-log columns.")
    by_number = {int(source["essay_number"]): [] for source in sources}
    for row in rows:
        number = int(row["essay_number"])
        if number not in by_number:
            raise ValueError("Quotation log contains an essay outside the fixed corpus.")
        by_number[number].append(row)
    reviews = review["essays"]
    if len(reviews) != 17 or {r["essay_number"] for r in reviews} != set(by_number):
        raise ValueError("All 17 essays must have an individual quotation review.")
    reviews = {r["essay_number"]: r for r in reviews}
    prepared = {}
    for source in sources:
        number = int(source["essay_number"])
        path = "data/clean/" + Path(source["raw_text_path"]).name
        content = (root / path).read_bytes()
        text, item, annotations = content.decode("utf-8"), reviews[number], by_number[number]
        if item["text_path"] != path or item["sha256"] != sha(content):
            raise ValueError(f"Reviewed text changed: {path}")
        if item["status"] != "reviewed" or item["reviewed_spans"] != len(annotations):
            raise ValueError(f"Incomplete review for No. {number}.")
        if (item["quotation_mark_count"] != sum(c in MARKS for c in text)
                or item["remove_spans"] != sum(r["decision"] == "remove" for r in annotations)
                or item["retain_spans"] != sum(r["decision"] == "retain" for r in annotations)):
            raise ValueError(f"Quotation-review totals disagree for No. {number}.")
        if any(r["text_path"] != path or r["source_url"] != source["url"] for r in annotations):
            raise ValueError(f"Quotation provenance differs for No. {number}.")
        prepared[number] = (path, text, remove_annotated_spans(text, annotations))
    return prepared, reviews


def evaluate_rows(rows, features, roles):
    """Validate the entire known-author sample before comparing the question."""
    if len(rows) != 17 or {int(row["essay_number"]) for row in rows} != {
        *map(int, roles), 49,
    }:
        raise ValueError("Each variant needs exactly the 17 fixed essays.")
    essays = tuple(EssayFrequencies(int(row["essay_number"]), row["role"], {
        word: float(row[word]) for word in features
    }) for row in rows)
    references = tuple(essay for essay in essays if essay.essay_id != 49)
    questioned = next(essay for essay in essays if essay.essay_id == 49)
    trials = run_leave_one_out(references, features, roles)
    summary = summarize_trials(trials)
    model, result = compare_questioned(references, questioned, features, roles)
    return trials, summary, model, result


def variant_outputs(name, counts, frequencies, features, roles, specification):
    trials, summary, model, result = evaluate_rows(frequencies, features, roles)
    prefix = f"results/{name}/"
    outputs = {
        prefix + "counts.csv": csv_bytes(counts, features),
        prefix + "frequencies.csv": csv_bytes(frequencies, features),
        prefix + "validation.csv": validation_csv(trials),
        prefix + "validation_summary.json": json_bytes(summary),
        prefix + "validation_fits.json": json_bytes([
            {"held_out_essay": t.essay_id, "training_model": asdict(t.model)} for t in trials
        ]),
        prefix + "questioned.csv": questioned_csv(model, result, summary),
        prefix + "questioned_profiles.json": json_bytes({
            "training_model": asdict(model), "questioned_essay": 49, "result": asdict(result),
            "validation_correct": summary["correct_assignments"],
        }),
    }
    outputs[prefix + "manifest.json"] = json_bytes({
        "stage": name, "status": "complete", "features": features,
        "token_pattern": specification.token_pattern, "frequency_per_words": 1000,
        "denominator": "original all-word total" if name == "feature_check" else "all words remaining after annotated removals",
        "quotations_removed": name == "quotation_check",
        "trial_count": 16, "training_essays_per_trial": 15,
        "full_comparison_training_essays": 16, "questioned_essay_used_for_fitting": False,
        "validation_completed_before_questioned_comparison": True,
        "provenance_manifest": MANIFEST,
        "output_sha256": {path: sha(content) for path, content in outputs.items()},
    })
    return outputs, {
        "feature_count": len(features), "usable_feature_count": len(model.features),
        "excluded_features": list(model.excluded_features),
        "validation": summary,
        "questioned": {key: value for key, value in asdict(result).items()
                       if not key.endswith("contributions")},
    }


def build_outputs(root):
    specification, roles = load_specification(root), expected_roles(root)
    _, sources = read_csv(root / "metadata/sources.csv")
    sources.sort(key=lambda row: int(row["essay_number"]))
    if (len(sources) != 17 or {int(r["essay_number"]) for r in sources} != {*map(int, roles), 49}
            or any(r["role"] != roles.get(r["essay_number"], "questioned") for r in sources)):
        raise ValueError("The source registry must match the fixed corpus.")
    prepared, reviews = load_annotations(root, sources)
    counts_header, original_counts = read_csv(root / "results/counts.csv")
    rates_header, original_rates = read_csv(root / "results/frequencies.csv")
    expected = ["essay_number", "role", "total_words", *specification.words]
    if counts_header != expected or rates_header != expected:
        raise ValueError("Main tables differ from the fixed feature specification.")
    features = tuple(w for w in specification.words if w not in specification.feature_check_remove)
    fields = ["essay_number", "role", "total_words", *features]
    counts = [{k: row[k] for k in fields} for row in original_counts]
    frequencies = [{k: row[k] for k in fields} for row in original_rates]
    outputs, feature_summary = variant_outputs(
        "feature_check", counts, frequencies, features, roles, specification,
    )
    counts, frequencies, removals = [], [], []
    for source in sources:
        number = int(source["essay_number"])
        path, original, cleaned = prepared[number]
        total, measured_counts, rates = measure_text(cleaned, specification)
        identity = {"essay_number": number, "role": source["role"], "total_words": total}
        counts.append({**identity, **measured_counts})
        frequencies.append({**identity, **{w: serialize_frequency(v) for w, v in rates.items()}})
        outputs["data/no_quotes/" + Path(path).name] = cleaned.encode("utf-8")
        original_total = measure_text(original, specification)[0]
        removals.append({
            "essay_number": number, "role": source["role"], "original_words": original_total,
            "remaining_words": total, "removed_words": original_total - total,
            "removed_spans": reviews[number]["remove_spans"],
            "retained_spans": reviews[number]["retain_spans"],
        })
    quotation_outputs, quotation_summary = variant_outputs(
        "quotation_check", counts, frequencies, specification.words, roles, specification,
    )
    outputs.update(quotation_outputs)
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(removals[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(removals)
    outputs["results/quotation_check/removal_summary.csv"] = buffer.getvalue().encode("utf-8")
    main_profiles = json.loads((root / "results/questioned_profiles.json").read_text("utf-8"))
    baseline = {
        "feature_count": 24, "usable_feature_count": len(main_profiles["training_model"]["features"]),
        "excluded_features": main_profiles["training_model"]["excluded_features"],
        "validation": json.loads((root / "results/validation_summary.json").read_text("utf-8")),
        "questioned": {k: v for k, v in main_profiles["result"].items() if not k.endswith("contributions")},
    }
    outputs["results/robustness_summary.json"] = json_bytes({
        "stage": "predefined_robustness_checks", "status": "complete",
        "baseline": baseline, "feature_check": feature_summary, "quotation_check": quotation_summary,
        "quotation_removals": removals, "annotation_was_blinded": False,
        "cross_variant_distances_are_calibrated_strength_measures": False,
        "combined_variant_run": False,
    })
    return outputs


def fingerprints(root):
    names = [
        "docs/research_plan.md", "docs/research_amendments.md", "config/research.toml",
        "metadata/sources.csv", "metadata/word_features.json", "metadata/distance_method.json",
        "metadata/quotations.csv", "metadata/quotation_review.json",
        "results/counts.csv", "results/frequencies.csv", "results/frequency_manifest.json",
        "results/validation.csv", "results/validation_summary.json", "results/validation_fits.json",
        "results/validation_manifest.json", "results/questioned.csv",
        "results/questioned_profiles.json", "results/questioned_manifest.json",
        ".python-version", "pyproject.toml", "uv.lock",
    ]
    paths = [root / name for name in names]
    for folder in ("data/clean", "src", "tests"):
        paths.extend(sorted((root / folder).glob("*.txt" if folder == "data/clean" else "*.py")))
    return {p.relative_to(root).as_posix(): sha(p.read_bytes()) for p in paths}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="Recalculate saved variants without writing.")
    arguments = parser.parse_args()
    try:
        subprocess.run([sys.executable, "-m", "src.compare_questioned", "--verify"],
                       cwd=ROOT, check=True, timeout=60)
        before = fingerprints(ROOT)
        outputs = build_outputs(ROOT)
        hashes = {path: sha(content) for path, content in outputs.items()}
        if before != fingerprints(ROOT):
            raise ValueError("Research inputs changed during calculation.")
        manifest_path = ROOT / MANIFEST
        if arguments.verify:
            manifest = json.loads(manifest_path.read_text("utf-8"))
            if manifest["input_sha256"] != before or manifest["output_sha256"] != hashes:
                raise ValueError("Robustness provenance differs from recalculation.")
            for path, content in outputs.items():
                if (ROOT / path).read_bytes() != content:
                    raise ValueError(f"Saved robustness output differs: {path}")
        else:
            for path in (*outputs, MANIFEST):
                if (ROOT / path).exists():
                    raise ValueError(f"Output exists; use --verify: {path}")
            manifest = {
                "stage": "predefined_robustness_checks", "status": "complete",
                "recorded_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                "runtime": {"python": platform.python_version(), "operating_system": platform.platform(),
                            "uv": subprocess.check_output(["uv", "--version"], text=True).strip()},
                "input_sha256": before, "output_sha256": hashes,
                "main_analysis_preserved": True, "annotation_was_blinded": False,
                "validation_trials_per_variant": 16,
                "validation_completed_before_each_questioned_comparison": True,
            }
            for path, content in {**outputs, MANIFEST: json_bytes(manifest)}.items():
                (ROOT / path).parent.mkdir(parents=True, exist_ok=True)
                with (ROOT / path).open("xb") as handle:
                    handle.write(content)
        if before != fingerprints(ROOT):
            raise ValueError("Research inputs changed during output verification.")
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        parser.exit(1, f"Robustness checks failed: {error}\n")
    summary = json.loads(outputs["results/robustness_summary.json"])
    for name in ("feature_check", "quotation_check"):
        item = summary[name]
        print(f"{name}: {item['validation']['correct_assignments']}/16 correct; "
              f"No. 49 closer to {item['questioned']['prediction']}.")


if __name__ == "__main__":
    main()
