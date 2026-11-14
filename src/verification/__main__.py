"""Verify implementation, evidence integrity, and repeatability without replacement.

Use uv run --locked python -m src.verification. Use --verify to rerun checks
against the saved verification record. Independent calculations use an ASCII
word scanner and Decimal arithmetic rather than the production tokenizer or
distance implementation. Production functions are used only in leakage probes.
"""

import argparse
from collections import Counter
import csv
from dataclasses import asdict, replace
from datetime import datetime
from decimal import Decimal, localcontext
import hashlib
import io
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[2]
DESTINATION = "results/verification"
MANIFEST = DESTINATION + "/manifest.json"
PRECISION = 50
AUDIT_TOLERANCE = Decimal("1e-12")
METHOD_TIE_TOLERANCE = Decimal("1e-12")
FEATURES = tuple("the a an and or but of to in on at by for from with as that which this these it is be not".split())
HAMILTON = (1, 6, 21, 26, 31, 59, 70, 78)
MADISON = (10, 14, 37, 39, 41, 43, 46, 48)
ROLES = {**dict.fromkeys(HAMILTON, "hamilton"), **dict.fromkeys(MADISON, "madison"), 49: "questioned"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(content):
    return hashlib.sha256(content).hexdigest()


def json_bytes(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def decimal_text(value):
    text = str(value)
    if text.startswith("0."):
        return text[1:]
    return "-" + text[2:] if text.startswith("-0.") else text


def table_bytes(rows):
    require(bool(rows), "An audit table cannot be empty.")
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def read_rows(root, path):
    with (root / path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(root, path):
    return json.loads((root / path).read_text("utf-8"))


def indexed(rows, key, expected):
    result = {}
    for row in rows:
        number = int(row[key])
        require(number not in result, f"Duplicate {key}: {number}")
        result[number] = row
    require(set(result) == set(expected), f"Unexpected or missing identities in {key}.")
    return result


def scan_words(text):
    """Implement the registered ASCII word rule independently of regular expressions."""
    normalized = text.lower().replace("‘", "'").replace("’", "'")
    require(len(normalized) == len(text), "An offset map is required for length-changing normalization.")
    tokens, position = [], 0
    while position < len(normalized):
        if not "a" <= normalized[position] <= "z":
            position += 1
            continue
        start = position
        while position < len(normalized):
            if "a" <= normalized[position] <= "z":
                position += 1
            elif (normalized[position] == "'" and position + 1 < len(normalized)
                  and "a" <= normalized[position + 1] <= "z"):
                position += 1
            else:
                break
        tokens.append((normalized[start:position], start, position))
    return tokens


class NumericChecks:
    def __init__(self):
        self.checked = 0
        self.maximum_error = Decimal(0)

    def close(self, saved, expected, label):
        actual = Decimal(str(saved))
        require(actual.is_finite() and expected.is_finite(), f"Nonfinite quantity: {label}")
        error = abs(actual - expected)
        require(error <= AUDIT_TOLERANCE, f"Numerical mismatch: {label}; error {error}")
        self.checked += 1
        self.maximum_error = max(self.maximum_error, error)
        return error


def fit_decimal(training, features):
    """Fit equal-essay means and sample scaling with 50-digit decimal arithmetic."""
    require(len(training) >= 2, "Sample scaling needs at least 2 training essays.")
    require(all(row["number"] != 49 and row["role"] in {"hamilton", "madison"} for row in training),
            "Evaluation data entered the independent training sample.")
    means = {author: [] for author in ("hamilton", "madison")}
    usable, excluded, scales = [], [], []
    for word in features:
        values = [row["frequencies"][word] for row in training]
        overall = sum(values) / len(values)
        scale = (sum((value - overall) ** 2 for value in values) / (len(values) - 1)).sqrt()
        if scale == 0:
            excluded.append(word)
            continue
        usable.append(word)
        scales.append(scale)
        for author in means:
            own = [row["frequencies"][word] for row in training if row["role"] == author]
            require(bool(own), "Both reference authors are required.")
            means[author].append(sum(own) / len(own))
    require(bool(usable), "All independent training features are constant.")
    return {"features": usable, "excluded_features": excluded,
            "training_ids": [str(row["number"]) for row in training],
            "hamilton_essay_count": sum(row["role"] == "hamilton" for row in training),
            "madison_essay_count": sum(row["role"] == "madison" for row in training),
            "hamilton_mean": means["hamilton"], "madison_mean": means["madison"],
            "sample_standard_deviations": scales}


def score_decimal(model, query):
    require(str(query["number"]) not in model["training_ids"], "Query entered its own fitted profiles.")
    contributions = {}
    distances = {}
    for author in ("hamilton", "madison"):
        contributions[author] = [abs(query["frequencies"][word] - mean) / scale
                                 for word, mean, scale in zip(model["features"], model[author + "_mean"],
                                                              model["sample_standard_deviations"])]
        distances[author] = sum(contributions[author]) / len(model["features"])
    gap = distances["hamilton"] - distances["madison"]
    prediction = "inconclusive" if abs(gap) <= METHOD_TIE_TOLERANCE else min(distances, key=distances.get)
    return distances, gap, prediction, contributions


def check_model(saved, expected, numbers):
    for key in ("features", "excluded_features", "hamilton_essay_count", "madison_essay_count"):
        require(saved[key] == expected[key], f"Fitted model differs: {key}")
    require(len(saved["training_ids"]) == len(set(saved["training_ids"]))
            and set(saved["training_ids"]) == set(expected["training_ids"]), "Training identifiers differ.")
    for key in ("hamilton_mean", "madison_mean", "sample_standard_deviations"):
        require(len(saved[key]) == len(expected[key]), f"Fitted vector length differs: {key}")
        for word, actual, independent in zip(expected["features"], saved[key], expected[key]):
            numbers.close(actual, independent, key + ":" + word)


def audit_integrity(root):
    settings = tomllib.loads((root / "config/research.toml").read_text("utf-8"))
    require(settings["corpus"] == {"hamilton": list(HAMILTON), "madison": list(MADISON), "questioned": 49},
            "The registered corpus differs from the fixed selection.")
    require(tuple(settings["counting"]["features"]) == FEATURES, "The original 24 features changed.")
    require(digest((root / "docs/research_plan.md").read_bytes()) == settings["research"]["plan_sha256"],
            "The original plan checksum changed.")
    sources = indexed(read_rows(root, "metadata/sources.csv"), "essay_number", ROLES)
    for number, source in sources.items():
        require(all(value.strip() for value in source.values()), f"Empty source metadata: No. {number}")
        require(source["role"] == ROLES[number], f"Incorrect reference role: No. {number}")
        require(source["source_attribution"] == {"hamilton": "Hamilton", "madison": "Madison",
                                                 "questioned": "Hamilton or Madison"}[ROLES[number]],
                f"Incorrect source attribution label: No. {number}")
        for prefix in ("raw_page", "raw_text"):
            require(digest((root / source[prefix + "_path"]).read_bytes()) == source[prefix + "_sha256"],
                    f"Source artifact checksum changed: No. {number}")
    preparation = read_json(root, "results/preparation_manifest.json")
    raw = {str(path.relative_to(root)): digest(path.read_bytes())
           for path in sorted((root / "data/raw").rglob("*")) if path.is_file()}
    require(raw == preparation["raw_sha256"], "Raw evidence inventory or checksums changed.")
    essays = indexed(preparation["essays"], "essay_number", ROLES)
    for number, essay in essays.items():
        require(essay["role"] == ROLES[number], "Preparation role differs.")
        require(digest((root / essay["prepared_path"]).read_bytes()) == essay["prepared_sha256"],
                f"Prepared copy checksum changed: No. {number}")
    for folder in ("data/clean", "data/no_quotes", "data/raw/texts"):
        expected = {Path(source["raw_text_path"]).name for source in sources.values()}
        require({path.name for path in (root / folder).glob("*.txt")} == expected,
                f"Unexpected or missing essay files: {folder}")
    history = "results/history/partial_corpus_14_november_2026"
    archived = read_json(root, history + "/archive_manifest.json")["original_path_sha256"]
    for name, expected in archived.items():
        require(digest((root / history / name).read_bytes()) == expected, f"Historical artifact changed: {name}")
    references = 0
    for name in ("metadata/word_features.json", "metadata/distance_method.json",
                 "results/frequency_manifest.json", "results/validation_manifest.json",
                 "results/questioned_manifest.json", "results/robustness_manifest.json",
                 "results/interpretation_manifest.json"):
        record = read_json(root, name)
        for section in ("input_sha256", "output_sha256", "code_sha256"):
            for path, expected in record.get(section, {}).items():
                require(digest((root / path).read_bytes()) == expected, f"Recorded fingerprint changed: {name}: {path}")
                references += 1
    return sources, {"reference_essays": 16, "questioned_essays": 1,
                     "raw_files_including_layout_markers": len(raw), "source_records": len(sources),
                     "historical_artifacts": len(archived), "provenance_hash_references": references}


def rebuild_texts(root, sources):
    annotations = read_rows(root, "metadata/quotations.csv")
    texts, stripped, inventories = {}, {}, {}
    for number, source in sources.items():
        name = Path(source["raw_text_path"]).name
        text = (root / "data/clean" / name).read_text("utf-8")
        own = sorted((row for row in annotations if int(row["essay_number"]) == number),
                     key=lambda row: int(row["start_offset"]))
        previous_end, accounted = 0, set()
        for row in own:
            start, end = int(row["start_offset"]), int(row["end_offset"])
            require(previous_end <= start < end <= len(text) and text[start:end] == row["quoted_text"],
                    f"Invalid quotation annotation: No. {number}")
            require(row["decision"] in {"remove", "retain"} and bool(row["reason"].strip()),
                    "A quotation decision or reason is missing.")
            accounted.update(i for i in range(start, end) if text[i] in '\"“”')
            previous_end = end
        require(accounted == {i for i, char in enumerate(text) if char in '\"“”'},
                f"Unreviewed quotation marks: No. {number}")
        no_quotes = text
        for row in reversed(own):
            if row["decision"] == "remove":
                no_quotes = no_quotes[:int(row["start_offset"])] + " " + no_quotes[int(row["end_offset"]):]
        require(no_quotes == (root / "data/no_quotes" / name).read_text("utf-8"),
                f"Quotation-removal copy differs: No. {number}")
        texts[number], stripped[number], inventories[number] = text, no_quotes, own
    return texts, stripped, inventories


def build_dataset(root, name, prefix, features, texts, numbers):
    counts = indexed(read_rows(root, prefix + "counts.csv"), "essay_number", ROLES)
    rates = indexed(read_rows(root, prefix + "frequencies.csv"), "essay_number", ROLES)
    dataset = []
    for number in sorted(ROLES):
        require(list(counts[number]) == ["essay_number", "role", "total_words", *features]
                and list(rates[number]) == list(counts[number]), f"Unexpected table columns: {name}")
        tokens = scan_words(texts[number])
        inventory = Counter(token[0] for token in tokens)
        require(bool(tokens), f"Empty essay: {name}, No. {number}")
        for row in (counts[number], rates[number]):
            require(row["role"] == ROLES[number] and int(row["total_words"]) == len(tokens),
                    f"Role or denominator differs: {name}, No. {number}")
        frequencies = {}
        for word in features:
            require(int(counts[number][word]) == inventory[word], f"Word count differs: {name}, No. {number}, {word}")
            frequencies[word] = Decimal(inventory[word]) / len(tokens) * 1000
            numbers.close(rates[number][word], frequencies[word], f"{name}:frequency:{number}:{word}")
        dataset.append({"number": number, "role": ROLES[number], "total_words": len(tokens),
                        "counts": inventory, "frequencies": frequencies,
                        "production_frequencies": {word: float(rates[number][word]) for word in features}})
    return dataset


def audit_comparisons(root, name, prefix, features, dataset, numbers):
    references = [row for row in dataset if row["number"] != 49]
    trials = indexed(read_rows(root, prefix + "validation.csv"), "held_out_essay", [row["number"] for row in references])
    fits = indexed(read_json(root, prefix + "validation_fits.json"), "held_out_essay", trials)
    comparisons, correct, errors, inconclusive = [], Counter(), [], []
    for query in [*references, next(row for row in dataset if row["number"] == 49)]:
        number = query["number"]
        training = [row for row in references if row["number"] != number]
        model = fit_decimal(training, features)
        distances, gap, prediction, contributions = score_decimal(model, query)
        if number == 49:
            saved_rows = read_rows(root, prefix + "questioned.csv")
            require(len(saved_rows) == 1 and saved_rows[0]["essay_number"] == "49"
                    and saved_rows[0]["role"] == "questioned", f"Invalid questioned result: {name}")
            saved = saved_rows[0]
            profile = read_json(root, prefix + "questioned_profiles.json")
            check_model(profile["training_model"], model, numbers)
            for author in ("hamilton", "madison"):
                original = profile["result"][author + "_contributions"]
                require(len(original) == len(contributions[author]), "Contribution vector length differs.")
                for actual, expected in zip(original, contributions[author]):
                    numbers.close(actual, expected, f"{name}:questioned:{author}:contribution")
        else:
            saved = trials[number]
            check_model(fits[number]["training_model"], model, numbers)
            require(saved["reference_author"] == query["role"], "Held-out reference label differs.")
            require(int(saved["training_hamilton_count"]) == model["hamilton_essay_count"]
                    and int(saved["training_madison_count"]) == model["madison_essay_count"], "Training counts differ.")
            success = prediction == query["role"]
            require(saved["correct"] == ("Yes" if success else "No"), "Trial correctness differs.")
            correct[query["role"]] += int(success)
            if prediction == "inconclusive":
                inconclusive.append(number)
            elif not success:
                errors.append(number)
        require(int(saved["usable_feature_count"]) == len(model["features"])
                and saved["excluded_features"] == ";".join(model["excluded_features"]), "Feature exclusions differ.")
        require(saved["predicted_author"] == prediction, f"Prediction differs: {name}, No. {number}")
        errors_by_author = {a: numbers.close(saved[a + "_distance"], distances[a], f"{name}:{number}:{a}")
                            for a in ("hamilton", "madison")}
        numbers.close(saved["signed_gap"], gap, f"{name}:{number}:signed_gap")
        numbers.close(saved["absolute_gap"], abs(gap), f"{name}:{number}:absolute_gap")
        comparisons.append({
            "version": name, "evaluated_essay": number, "role": query["role"],
            "training_essays": len(training), "usable_features": len(model["features"]),
            "independent_hamilton_distance": decimal_text(distances["hamilton"]),
            "saved_hamilton_distance": saved["hamilton_distance"],
            "absolute_hamilton_error": decimal_text(errors_by_author["hamilton"]),
            "independent_madison_distance": decimal_text(distances["madison"]),
            "saved_madison_distance": saved["madison_distance"],
            "absolute_madison_error": decimal_text(errors_by_author["madison"]),
            "independent_prediction": prediction, "saved_prediction": saved["predicted_author"],
        })
    summary = read_json(root, prefix + "validation_summary.json")
    require(summary["total_trials"] == 16 and summary["correct_assignments"] == sum(correct.values()),
            "Validation summary totals differ.")
    for author in ("hamilton", "madison"):
        require(summary["by_author"][author] == {"correct": correct[author], "total": 8},
                "Per-author validation summary differs.")
    require(sorted(summary["misclassified_essays"]) == errors
            and sorted(summary["inconclusive_essays"]) == inconclusive
            and summary["baseline"]["correct"] == 8 and summary["baseline"]["total"] == 16,
            "Errors, inconclusive trials, or baseline differ.")
    return comparisons


def audit_contexts(root, texts, stripped, annotations, numbers):
    main = read_json(root, "results/questioned_profiles.json")
    words = main["training_model"]["features"]
    expected = sorted([(abs(Decimal(str(h)) - Decimal(str(m))), word, Decimal(str(h)) - Decimal(str(m)))
                       for word, h, m in zip(words, main["result"]["hamilton_contributions"],
                                             main["result"]["madison_contributions"])], key=lambda row: (-row[0], row[1]))
    ranked = read_rows(root, "results/feature_contributions.csv")
    require(len(ranked) == 24 and [r["word"] for r in ranked] == [r[1] for r in expected], "Feature ranks differ.")
    for rank, (row, (_, word, difference)) in enumerate(zip(ranked, expected), start=1):
        require(int(row["rank"]) == rank and row["selected_for_context"] == ("Yes" if rank <= 4 else "No"),
                "Feature selection differs.")
        numbers.close(row["signed_difference"], difference, word + ":signed_contribution")
        numbers.close(row["contribution_to_mean_gap"], difference / 24, word + ":mean_gap_contribution")
    selected = [row[1] for row in expected[:4]]
    hits = read_rows(root, "results/concordances.csv")
    by_location = {}
    tokens = {number: scan_words(text) for number, text in texts.items()}
    for row in hits:
        number, start, end = int(row["essay_number"]), int(row["start_offset"]), int(row["end_offset"])
        key = number, start
        require(key not in by_location and row["word"] in selected, "Duplicate or unexpected concordance hit.")
        by_location[key] = row
        text, ts, index = texts[number], tokens[number], int(row["token_number"]) - 1
        require(0 <= index < len(ts) and ts[index] == (row["word"], start, end), "Incorrect concordance token or offset.")
        require(row["matched_text"] == text[start:end]
                and row["left_context"] == text[ts[max(0, index - 8)][1]:start]
                and row["right_context"] == text[end:ts[min(len(ts) - 1, index + 8)][2]], "Incorrect context window.")
        require(int(row["line_number"]) == text.count("\n", 0, start) + 1
                and row["text_sha256"] == digest(text.encode()), "Incorrect concordance line or checksum.")
        own = [a for a in annotations[number] if int(a["start_offset"]) <= start and end <= int(a["end_offset"])]
        require(row["quotation_decision"] == (own[0]["decision"] if own else "outside"), "Incorrect quotation membership.")
    expected_locations = {(number, start) for number, ts in tokens.items() for word, start, end in ts if word in selected}
    require(set(by_location) == expected_locations, "Incomplete concordances.")
    distributions = read_rows(root, "results/feature_distribution.csv")
    require(len(distributions) == 68
            and len({(r["word"], r["essay_number"]) for r in distributions}) == 68, "Incomplete feature distributions.")
    for row in distributions:
        number, word = int(row["essay_number"]), row["word"]
        require(word in selected, "Unexpected distribution word.")
        inventory = Counter(t[0] for t in tokens[number])
        remaining = scan_words(stripped[number])
        require(int(row["count"]) == inventory[word] and int(row["total_words"]) == len(tokens[number]), "Distribution counts differ.")
        numbers.close(row["frequency_per_1000"], Decimal(inventory[word]) / len(tokens[number]) * 1000, "distribution rate")
        numbers.close(row["quotation_check_frequency_per_1000"], Decimal(sum(t[0] == word for t in remaining)) / len(remaining) * 1000,
                      "quotation distribution rate")
    notes = read_rows(root, "metadata/concordance_examples.csv")
    examples = read_rows(root, "results/concordance_examples.csv")
    require(len(notes) == len(examples), "Annotated examples are incomplete.")
    for note, example in zip(notes, examples):
        hit = by_location[(int(note["essay_number"]), int(note["start_offset"]))]
        require(all(example[key] == value for key, value in hit.items())
                and all(example[key] == value for key, value in note.items()), "An annotated example differs from its source.")
    return {"ranked_features": len(ranked), "concordance_occurrences": len(hits),
            "distribution_rows": len(distributions), "annotated_examples": len(examples)}


def independent_audit(root):
    with localcontext() as context:
        context.prec = PRECISION
        numbers = NumericChecks()
        sources, integrity = audit_integrity(root)
        texts, stripped, annotations = rebuild_texts(root, sources)
        versions = (("main", "results/", FEATURES, texts),
                    ("feature_check", "results/feature_check/", tuple(w for w in FEATURES if w not in {"the", "a", "of", "and"}), texts),
                    ("quotation_check", "results/quotation_check/", FEATURES, stripped))
        comparisons, datasets = [], {}
        for name, prefix, features, copies in versions:
            dataset = build_dataset(root, name, prefix, features, copies, numbers)
            comparisons.extend(audit_comparisons(root, name, prefix, features, dataset, numbers))
            datasets[name] = features, dataset
        contexts = audit_contexts(root, texts, stripped, annotations, numbers)
        cells = sum(len(features) * len(dataset) for features, dataset in datasets.values())
        summary = {"status": "passed", "corpus_integrity": integrity, "versions": len(datasets),
                   "count_cells_checked": cells, "frequency_cells_checked": cells,
                   "validation_trials_checked": sum(row["evaluated_essay"] != 49 for row in comparisons),
                   "questioned_comparisons_checked": sum(row["evaluated_essay"] == 49 for row in comparisons),
                   "distance_values_checked": len(comparisons) * 2, "fitted_models_checked": len(comparisons),
                   "decimal_precision": PRECISION, "absolute_audit_tolerance": str(AUDIT_TOLERANCE),
                   "audit_tolerance_is_not_an_evidence_threshold": True,
                   "numeric_quantities_checked": numbers.checked,
                   "maximum_observed_absolute_error": str(numbers.maximum_error),
                   "contexts": contexts}
        return summary, comparisons, datasets


def leakage_probes(datasets):
    # Deliberately exercise the production workflow on perturbed in-memory inputs.
    from src.compare_questioned import compare_questioned
    from src.distance_method import EssayFrequencies
    from src.validate_authors import run_leave_one_out

    roles = {str(n): role for n, role in ROLES.items() if n != 49}
    probes = []
    for name, (features, dataset) in datasets.items():
        references = tuple(EssayFrequencies(row["number"], row["role"], row["production_frequencies"])
                           for row in dataset if row["number"] != 49)
        baseline = {trial.essay_id: trial for trial in run_leave_one_out(references, features, roles)}
        for held_out in references:
            perturbed = tuple(replace(row, frequencies={w: 900 for w in features})
                              if row.essay_id == held_out.essay_id else row for row in references)
            modified = next(t for t in run_leave_one_out(perturbed, features, roles) if t.essay_id == held_out.essay_id)
            original = baseline[held_out.essay_id]
            require(original.model == modified.model, f"Held-out values changed their training fit: {name}, No. {held_out.essay_id}")
            probes.append({"version": name, "evaluated_essay": held_out.essay_id,
                           "probe": "held_out_frequency_replacement", "replacement_per_1000": 900,
                           "training_model_before_sha256": digest(json_bytes(asdict(original.model))),
                           "training_model_after_sha256": digest(json_bytes(asdict(modified.model))),
                           "training_quantities_unchanged": True})
        query = next(row for row in dataset if row["number"] == 49)
        query = EssayFrequencies(49, "questioned", query["production_frequencies"])
        first_model, _ = compare_questioned(references, query, features, roles)
        second_model, _ = compare_questioned(references, replace(query, frequencies={w: 900 for w in features}), features, roles)
        require(first_model == second_model, f"No. 49 values changed the reference fit: {name}")
        probes.append({"version": name, "evaluated_essay": 49, "probe": "questioned_frequency_replacement",
                       "replacement_per_1000": 900,
                       "training_model_before_sha256": digest(json_bytes(asdict(first_model))),
                       "training_model_after_sha256": digest(json_bytes(asdict(second_model))),
                       "training_quantities_unchanged": True})
    return probes


def input_snapshot(root):
    paths = {root / name for name in ("AGENTS.md", "docs/research_plan.md", "docs/research_amendments.md",
                                     "config/research.toml", ".python-version", "pyproject.toml", "uv.lock")}
    for folder in ("metadata", "data", "src", "tests", "results"):
        for path in (root / folder).rglob("*"):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            if path.is_relative_to(root / DESTINATION):
                continue
            if folder in {"src", "tests"} and path.suffix != ".py":
                continue
            paths.add(path)
    return {str(path.relative_to(root)): digest(path.read_bytes()) for path in sorted(paths)}


def run_checks(root):
    commands = (
        ("unit_tests", ["-m", "unittest", "discover", "-s", "tests", "-v"]),
        ("environment", ["src/check_environment.py"]),
        ("corpus", ["src/assemble_corpus.py", "--verify"]),
        ("frequencies_and_preparation", ["-m", "src.calculate_frequencies", "--verify"]),
        ("analysis_and_interpretation_first_pass", ["-m", "src.interpretation", "--verify"]),
    )
    records, logs = [], {}
    for name, arguments in commands:
        result = subprocess.run([sys.executable, *arguments], cwd=root, capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr
        require(result.returncode == 0, f"Verification command failed: {name}\n{output}")
        logs[f"{DESTINATION}/{name}.log"] = output.encode("utf-8")
        records.append({"name": name, "command": "uv run --locked python " + " ".join(arguments),
                        "exit_code": result.returncode, "status": "passed"})
    test_output = logs[f"{DESTINATION}/unit_tests.log"].decode()
    match = re.search(r"Ran (\d+) tests? in", test_output)
    require(match is not None and test_output.rstrip().endswith("OK"), "Tests did not report complete success.")
    return records, logs, int(match.group(1))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="Rerun verification without replacing saved records.")
    arguments = parser.parse_args()
    try:
        if not arguments.verify:
            require(not (ROOT / DESTINATION).exists(), "Verification records exist; use --verify.")
        before = input_snapshot(ROOT)
        commands, logs, test_count = run_checks(ROOT)
        audit, comparisons, datasets = independent_audit(ROOT)
        probes = leakage_probes(datasets)
        deterministic = {
            f"{DESTINATION}/independent_audit.json": json_bytes(audit),
            f"{DESTINATION}/independent_comparisons.csv": table_bytes(comparisons),
            f"{DESTINATION}/leakage_probes.json": json_bytes(probes),
        }
        # A second deterministic calculation and complete production verification
        # are required by the research plan; the unit suite runs only once.
        second_audit, second_comparisons, _ = independent_audit(ROOT)
        require(json_bytes(second_audit) == deterministic[f"{DESTINATION}/independent_audit.json"]
                and table_bytes(second_comparisons) == deterministic[f"{DESTINATION}/independent_comparisons.csv"],
                "Independent calculations are not repeatable.")
        repeated = subprocess.run([sys.executable, "-m", "src.interpretation", "--verify"],
                                  cwd=ROOT, capture_output=True, text=True, timeout=60)
        require(repeated.returncode == 0, "Second complete production verification failed: " + repeated.stderr)
        logs[f"{DESTINATION}/analysis_and_interpretation_second_pass.log"] = (repeated.stdout + repeated.stderr).encode()
        commands.append({"name": "analysis_and_interpretation_second_pass",
                         "command": "uv run --locked python -m src.interpretation --verify",
                         "exit_code": repeated.returncode, "status": "passed"})
        unchanged = input_snapshot(ROOT)
        require(before == unchanged, "Input evidence, prior results, or code changed during verification.")
        summary = {"stage": "implementation_verification", "status": "passed", "unit_tests_passed": test_count,
                   "unit_test_failures": 0, "unit_test_errors": 0, "unit_test_skips": 0,
                   "commands": commands, "independent_audit": audit,
                   "held_out_leakage_probes_passed": sum(p["evaluated_essay"] != 49 for p in probes),
                   "questioned_leakage_probes_passed": sum(p["evaluated_essay"] == 49 for p in probes),
                   "production_numeric_reproduction_passes": 2,
                   "independent_decimal_reproduction_passes": 2,
                   "independent_repeated_comparison_bytes_identical": True,
                   "all_input_bytes_unchanged": True,
                   "scope": "Implementation correctness and evidence integrity; not historical authorship or general accuracy",
                   "limitations": ["Nos. 21 and 26 remain supplied transcriptions without independent live-wording verification.",
                                   "Quotation and linguistic annotations include interpretive judgments and were not blinded.",
                                   "Passing these checks does not prove an absence of all defects or establish performance on unseen texts."]}
        deterministic[f"{DESTINATION}/summary.json"] = json_bytes(summary)
        hashes = {name: digest(content) for name, content in deterministic.items()}
        if arguments.verify:
            recorded = read_json(ROOT, MANIFEST)
            require(recorded["input_sha256"] == before, "Verification inputs differ from the saved run.")
            for name, content in deterministic.items():
                require((ROOT / name).read_bytes() == content and recorded["output_sha256"][name] == hashes[name],
                        f"Verification output differs: {name}")
            for name, expected in recorded["output_sha256"].items():
                require(digest((ROOT / name).read_bytes()) == expected, f"Saved verification evidence changed: {name}")
        else:
            outputs = {**deterministic, **logs}
            manifest = {"stage": "implementation_verification", "status": "passed",
                        "recorded_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                        "runtime": {"python": platform.python_version(), "uv": subprocess.check_output(["uv", "--version"], text=True).strip(),
                                    "operating_system": platform.platform()},
                        "git_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                        "input_sha256": before, "output_sha256": {name: digest(content) for name, content in outputs.items()},
                        "unittest_timings_are_not_compared_between_runs": True}
            (ROOT / DESTINATION).mkdir()
            for name, content in {**outputs, MANIFEST: json_bytes(manifest)}.items():
                with (ROOT / name).open("xb") as handle:
                    handle.write(content)
        require(before == input_snapshot(ROOT), "Verification altered its source evidence.")
    except (OSError, ValueError, KeyError, ArithmeticError, subprocess.SubprocessError) as error:
        parser.exit(1, f"Implementation verification failed: {error}\n")
    print(f"Verification passed: {test_count} tests; 48 validation trials; 3 questioned comparisons; "
          f"{len(probes)} data-leakage probes.")
    print("Saved results reproduced; raw evidence and all earlier artifacts remain unchanged.")


if __name__ == "__main__":
    main()
