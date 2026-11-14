"""Inspect the four features selected by the original contribution-ranking rule.

Run with uv run --locked python -m src.interpretation. The command preserves
all earlier artifacts and refuses to replace its own outputs. --verify checks
deterministic reproduction. Context patterns are descriptive, not new features.
"""

import argparse
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import platform
import re
import statistics
import subprocess
import sys

from src.prepare_texts import normalize_for_counting
from src.validate_authors import json_bytes, number_text
from src.word_features import load_specification, tokenize_words


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = "results/interpretation_manifest.json"
WINDOW_WORDS = 8
# Chosen during context inspection; these are not attribution features or tests.
PATTERNS = (
    "on the other hand", "on the side of", "on one side", "on the same side",
    "on this subject", "on which", "on whom", "on its side",
    "in time of peace", "in the hands of", "in the first place", "in the next place",
    "in proportion to", "in favor of", "in order to",
    "at the same time", "at least", "at once", "at large", "at the expense of",
    "these advantages", "these states", "these circumstances", "these considerations",
)


def sha(content):
    return hashlib.sha256(content).hexdigest()


def read_rows(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def table_bytes(rows):
    if not rows:
        raise ValueError("An inspection table cannot be empty.")
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: number_text(value) if isinstance(value, float) else value
                         for key, value in row.items()})
    return buffer.getvalue().encode("utf-8")


@dataclass(frozen=True)
class Token:
    word: str
    start: int
    end: int


def word_spans(text, specification):
    """Use the counting rule and preserve exact readable-text character offsets."""
    normalized = normalize_for_counting(text)
    if len(normalized) != len(text):
        raise ValueError("Length-changing normalization requires an explicit offset map.")
    tokens = tuple(Token(m.group(), m.start(), m.end())
                   for m in re.finditer(specification.token_pattern, normalized))
    if [token.word for token in tokens] != tokenize_words(text, specification):
        raise ValueError("Concordance tokens differ from the fixed counting rule.")
    return tokens


def rank_contributions(profile):
    """Rank absolute signed differences, breaking exact ties alphabetically."""
    model, result = profile["training_model"], profile["result"]
    words = model["features"]
    h, m = result["hamilton_contributions"], result["madison_contributions"]
    if len(words) != len(set(words)) or len(words) != len(h) or len(words) != len(m):
        raise ValueError("Invalid contribution vectors.")
    rows = []
    for word, hc, mc in zip(words, h, m):
        if not all(math.isfinite(value) and value >= 0 for value in (hc, mc)):
            raise ValueError("Contributions must be finite and nonnegative.")
        difference = hc - mc
        rows.append({
            "word": word, "hamilton_contribution": hc, "madison_contribution": mc,
            "signed_difference": difference, "absolute_difference": abs(difference),
            "contribution_to_mean_gap": difference / len(words),
            "favored_profile": "madison" if difference > 0 else "hamilton" if difference < 0 else "neither",
        })
    rows.sort(key=lambda row: (-row["absolute_difference"], row["word"]))
    return [{"rank": i, **row, "selected_for_context": "Yes" if i <= 4 else "No"}
            for i, row in enumerate(rows, start=1)]


def quotation_decision(token, annotations):
    matches = [row for row in annotations
               if int(row["start_offset"]) <= token.start and token.end <= int(row["end_offset"])]
    if len(matches) > 1:
        raise ValueError("Overlapping quotation annotations.")
    return matches[0]["decision"] if matches else "outside"


def concordances(text, tokens, selected, source, annotations):
    rows = []
    ranks = {word: i for i, word in enumerate(selected, start=1)}
    for index, token in enumerate(tokens):
        if token.word not in ranks:
            continue
        first, last = tokens[max(0, index - WINDOW_WORDS)], tokens[min(len(tokens) - 1, index + WINDOW_WORDS)]
        rows.append({
            "feature_rank": ranks[token.word], "word": token.word,
            "essay_number": int(source["essay_number"]), "role": source["role"],
            "text_path": source["text_path"], "text_sha256": sha(text.encode("utf-8")),
            "source_url": source["url"], "token_number": index + 1,
            "line_number": text.count("\n", 0, token.start) + 1,
            "start_offset": token.start, "end_offset": token.end,
            "left_context": text[first.start:token.start],
            "matched_text": text[token.start:token.end],
            "right_context": text[token.end:last.end],
            "quotation_decision": quotation_decision(token, annotations),
        })
    return rows


def descriptive_summary(distribution, selected, profile, quotation_profile):
    main = {row["word"]: row for row in rank_contributions(profile)}
    no_quotes = {row["word"]: row for row in rank_contributions(quotation_profile)}
    summaries = {}
    for word in selected:
        rows = [row for row in distribution if row["word"] == word]
        own = {}
        for author in ("hamilton", "madison"):
            group = [row for row in rows if row["role"] == author]
            frequencies = [row["frequency_per_1000"] for row in group]
            clean = [row["quotation_check_frequency_per_1000"] for row in group]
            own[author] = {
                "essay_count": len(group), "mean": statistics.fmean(frequencies),
                "median": statistics.median(frequencies),
                "minimum": min(frequencies), "maximum": max(frequencies),
                "quotation_check_mean": statistics.fmean(clean),
                "quotation_check_minimum": min(clean), "quotation_check_maximum": max(clean),
                "word_count": sum(row["count"] for row in group),
                "occurrences_in_removed_spans": sum(row["removed_quotation_count"] for row in group),
            }
        query = next(row for row in rows if row["role"] == "questioned")
        summaries[word] = {
            "by_author": own, "questioned": query,
            "all_madison_rates_exceed_all_hamilton_rates": own["madison"]["minimum"] > own["hamilton"]["maximum"],
            "same_separation_after_quotation_removal": own["madison"]["quotation_check_minimum"] > own["hamilton"]["quotation_check_maximum"],
            "main_signed_contribution": main[word]["signed_difference"],
            "quotation_check_signed_contribution": no_quotes[word]["signed_difference"],
        }
    return summaries


def example_rows(root, hits):
    """Resolve curated linguistic notes to exact, already-counted occurrences."""
    examples = read_rows(root / "metadata/concordance_examples.csv")
    index = {(row["word"], row["essay_number"], row["start_offset"]): row for row in hits}
    seen, output = set(), []
    for example in examples:
        key = example["word"], int(example["essay_number"]), int(example["start_offset"])
        if key not in index or key in seen:
            raise ValueError("An example is duplicated or does not identify a concordance hit.")
        if not all(example[field].strip() for field in ("construction", "observation", "selection_reason")):
            raise ValueError("A linguistic example requires a construction, observation, and selection reason.")
        output.append({**index[key], **{field: example[field]
                                      for field in ("construction", "observation", "selection_reason")}})
        seen.add(key)
    for word in {row["word"] for row in hits}:
        if {row["role"] for row in output if row["word"] == word} != {"hamilton", "madison", "questioned"}:
            raise ValueError("Every selected feature needs examples from both authors and No. 49.")
    return output


def build_outputs(root):
    specification = load_specification(root)
    profile = json.loads((root / "results/questioned_profiles.json").read_text("utf-8"))
    quotation_profile = json.loads((root / "results/quotation_check/questioned_profiles.json").read_text("utf-8"))
    ranking = rank_contributions(profile)
    if len(ranking) != 24 or {row["word"] for row in ranking} != set(specification.words):
        raise ValueError("The main comparison must supply the original 24 usable features.")
    selected = tuple(row["word"] for row in ranking[:4])
    sources = sorted(read_rows(root / "metadata/sources.csv"), key=lambda row: int(row["essay_number"]))
    counts = {int(row["essay_number"]): row for row in read_rows(root / "results/counts.csv")}
    rates = {int(row["essay_number"]): row for row in read_rows(root / "results/frequencies.csv")}
    quote_counts = {int(row["essay_number"]): row for row in read_rows(root / "results/quotation_check/counts.csv")}
    annotations = read_rows(root / "metadata/quotations.csv")
    hits, distribution, patterns = [], [], []
    for source in sources:
        number = int(source["essay_number"])
        path = "data/clean/" + Path(source["raw_text_path"]).name
        text = (root / path).read_text("utf-8")
        tokens = word_spans(text, specification)
        if len(tokens) != int(counts[number]["total_words"]):
            raise ValueError(f"Word totals differ for No. {number}.")
        own_annotations = [row for row in annotations if int(row["essay_number"]) == number]
        own_hits = concordances(text, tokens, selected, {**source, "text_path": path}, own_annotations)
        hits.extend(own_hits)
        for word in selected:
            own = [row for row in own_hits if row["word"] == word]
            inventory = Counter(row["quotation_decision"] for row in own)
            count = int(counts[number][word])
            frequency = count / len(tokens) * 1000
            remaining_count = int(quote_counts[number][word])
            remaining_total = int(quote_counts[number]["total_words"])
            if (len(own) != count or frequency != float(rates[number][word])
                    or remaining_count != count - inventory["remove"]):
                raise ValueError(f"Concordance or quotation counts disagree for {word}, No. {number}.")
            distribution.append({
                "word": word, "essay_number": number, "role": source["role"],
                "count": count, "total_words": len(tokens), "frequency_per_1000": frequency,
                "removed_quotation_count": inventory["remove"],
                "retained_quotation_count": inventory["retain"], "outside_marked_spans_count": inventory["outside"],
                "quotation_check_count": remaining_count, "quotation_check_total_words": remaining_total,
                "quotation_check_frequency_per_1000": remaining_count / remaining_total * 1000,
            })
        for phrase in PATTERNS:
            words = phrase.split()
            matches = [i for i in range(len(tokens) - len(words) + 1)
                       if [t.word for t in tokens[i:i + len(words)]] == words]
            decisions = Counter(quotation_decision(tokens[i], own_annotations) for i in matches)
            patterns.append({
                "phrase": phrase, "essay_number": number, "role": source["role"],
                "count": len(matches), "first_word_in_removed_span": decisions["remove"],
                "first_word_in_retained_span": decisions["retain"],
            })
    hits.sort(key=lambda row: (row["feature_rank"], row["essay_number"], row["start_offset"]))
    examples = example_rows(root, hits)
    summary = {
        "stage": "linguistic_context_inspection", "status": "complete",
        "selected_features": selected, "ranking": "descending abs(c_H - c_M); exact ties alphabetical",
        "context_window_words_per_side": WINDOW_WORDS,
        "essay_count": len(sources), "concordance_occurrences": len(hits),
        "curated_examples": len(examples),
        "selected_features_are_not_a_new_attribution_model": True,
        "patterns_selected_during_inspection": True,
        "pattern_counts_are_token_sequences_not_parsed_grammatical_categories": True,
        "main_signed_gap": profile["result"]["signed_gap"],
        "sum_of_all_mean_gap_contributions": math.fsum(r["contribution_to_mean_gap"] for r in ranking),
        "selected_four_net_mean_gap_contribution": math.fsum(r["contribution_to_mean_gap"] for r in ranking[:4]),
        "features": descriptive_summary(distribution, selected, profile, quotation_profile),
    }
    return {
        "results/feature_contributions.csv": table_bytes(ranking),
        "results/concordances.csv": table_bytes(hits),
        "results/concordance_examples.csv": table_bytes(examples),
        "results/feature_distribution.csv": table_bytes(distribution),
        "results/context_patterns.csv": table_bytes(patterns),
        "results/interpretation_summary.json": json_bytes(summary),
    }


def fingerprints(root):
    previous = json.loads((root / "results/robustness_manifest.json").read_text("utf-8"))
    names = {*previous["input_sha256"], *previous["output_sha256"],
             "results/robustness_manifest.json", "metadata/concordance_examples.csv"}
    names.update(str(path.relative_to(root)) for folder in ("src/interpretation", "tests/language_inspection")
                 for path in (root / folder).glob("*.py"))
    return {name: sha((root / name).read_bytes()) for name in sorted(names)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="Recalculate all inspection outputs without writing.")
    arguments = parser.parse_args()
    try:
        subprocess.run([sys.executable, "-m", "src.robustness_checks", "--verify"],
                       cwd=ROOT, check=True, timeout=60)
        before = fingerprints(ROOT)
        outputs = build_outputs(ROOT)
        hashes = {name: sha(content) for name, content in outputs.items()}
        if before != fingerprints(ROOT):
            raise ValueError("Inspection inputs changed during calculation.")
        if arguments.verify:
            manifest = json.loads((ROOT / MANIFEST).read_text("utf-8"))
            if manifest["input_sha256"] != before or manifest["output_sha256"] != hashes:
                raise ValueError("Inspection provenance differs from recalculation.")
            for name, content in outputs.items():
                if (ROOT / name).read_bytes() != content:
                    raise ValueError(f"Saved inspection output differs: {name}")
        else:
            for name in (*outputs, MANIFEST):
                if (ROOT / name).exists():
                    raise ValueError(f"Output exists; use --verify: {name}")
            manifest = {
                "stage": "linguistic_context_inspection", "status": "complete",
                "recorded_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                "runtime": {"python": platform.python_version(), "operating_system": platform.platform(),
                            "uv": subprocess.check_output(["uv", "--version"], text=True).strip()},
                "input_sha256": before, "output_sha256": hashes,
                "main_and_reliability_analyses_preserved": True,
                "offset_convention": "Unicode characters; zero-based start; exclusive end; original readable clean text",
                "token_numbers_and_line_numbers": "one-based",
                "linguistic_annotations_are_descriptive_and_post_result": True,
            }
            for name, content in {**outputs, MANIFEST: json_bytes(manifest)}.items():
                with (ROOT / name).open("xb") as handle:
                    handle.write(content)
        if before != fingerprints(ROOT):
            raise ValueError("Inspection inputs changed during output verification.")
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        parser.exit(1, f"Language inspection failed: {error}\n")
    summary = json.loads(outputs["results/interpretation_summary.json"])
    print("Inspected features: " + ", ".join(summary["selected_features"]) + ".")
    print(f"Saved or verified {summary['concordance_occurrences']} concordance occurrences "
          f"across {summary['essay_count']} essays and {summary['curated_examples']} annotated examples.")


if __name__ == "__main__":
    main()
