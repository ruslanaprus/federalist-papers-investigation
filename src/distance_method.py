"""Define and verify the planned distance method without fitting corpus data.

Run from the repository root: uv run --locked python -m src.distance_method
The mathematical functions are exercised using invented frequencies in tests.
"""

import argparse
from dataclasses import dataclass
import hashlib
import json
import math
import platform
import statistics
import subprocess
import sys
import tomllib
from datetime import datetime
from pathlib import Path
from typing import Mapping, Sequence

from .word_features import load_specification


ROOT = Path(__file__).resolve().parents[1]
RECORD = Path("metadata/distance_method.json")
TIE_TOLERANCE = 1e-12
QUESTIONED_ID = 49
COMPARISON_SETTINGS = {
    "method": "mean_standardized_absolute_distance",
    "profile_weighting": "equal_essay",
    "standard_deviation": "sample_across_training_essays",
    "standard_deviation_ddof": 1,
    "constant_features": "exclude",
    "no_usable_features": "error",
    "tie_absolute_tolerance": TIE_TOLERANCE,
    "tie_label": "inconclusive",
}


@dataclass(frozen=True)
class EssayFrequencies:
    essay_id: int | str
    role: str
    frequencies: Mapping[str, float]


@dataclass(frozen=True)
class FittedProfiles:
    features: tuple[str, ...]
    excluded_features: tuple[str, ...]
    training_ids: tuple[str, ...]
    hamilton_essay_count: int
    madison_essay_count: int
    hamilton_mean: tuple[float, ...]
    madison_mean: tuple[float, ...]
    sample_standard_deviations: tuple[float, ...]


@dataclass(frozen=True)
class DistanceResult:
    hamilton_distance: float
    madison_distance: float
    signed_gap: float
    prediction: str
    hamilton_contributions: tuple[float, ...]
    madison_contributions: tuple[float, ...]


def identifier(value):
    if isinstance(value, bool) or not isinstance(value, (str, int)) or not str(value).strip():
        raise ValueError("Each essay needs a nonempty string or integer identifier.")
    return str(value)


def frequency_vector(essay, features):
    values = []
    for word in features:
        try:
            original = essay.frequencies[word]
            value = float(original)
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(f"Missing or invalid frequency for {word!r} in {essay.essay_id!r}.") from error
        if isinstance(original, bool) or not math.isfinite(value) or not 0 <= value <= 1000:
            raise ValueError("Frequencies must be finite values from zero to 1,000 per word.")
        values.append(value)
    return tuple(values)


def fit_reference_profiles(
    essays: Sequence[EssayFrequencies], features: Sequence[str], *, held_out_essay_id=None,
):
    """Fit means and sample scaling from the supplied training essays only."""
    if isinstance(features, str):
        raise ValueError("Features must be an ordered sequence of distinct word names.")
    features = tuple(features)
    if not features or any(not isinstance(word, str) or not word for word in features):
        raise ValueError("At least one named feature is required.")
    if len(features) != len(set(features)):
        raise ValueError("Features must be distinct.")
    rows = tuple(essays)
    ids = tuple(identifier(essay.essay_id) for essay in rows)
    if len(ids) != len(set(ids)):
        raise ValueError("A reference essay cannot appear more than once.")
    if str(QUESTIONED_ID) in ids or any(essay.role == "questioned" for essay in rows):
        raise ValueError("The questioned essay cannot enter profile fitting or scaling.")
    if held_out_essay_id is not None and identifier(held_out_essay_id) in ids:
        raise ValueError("The held-out essay must be removed before fitting.")
    if any(essay.role not in {"hamilton", "madison"} for essay in rows):
        raise ValueError("Reference roles must be hamilton or madison.")
    groups = {
        author: [index for index, essay in enumerate(rows) if essay.role == author]
        for author in ("hamilton", "madison")
    }
    if any(not positions for positions in groups.values()):
        raise ValueError("Both authors require at least one training essay.")
    vectors = tuple(frequency_vector(essay, features) for essay in rows)
    scales = tuple(
        statistics.stdev(vector[column] for vector in vectors)
        for column in range(len(features))
    )
    usable = tuple(column for column, scale in enumerate(scales) if scale != 0)
    excluded = tuple(word for word, scale in zip(features, scales) if scale == 0)
    if not usable:
        raise ValueError("No usable features remain; all training standard deviations are zero.")
    means = {
        author: tuple(
            statistics.fmean(vectors[index][column] for index in positions)
            for column in usable
        )
        for author, positions in groups.items()
    }
    return FittedProfiles(
        tuple(features[column] for column in usable), excluded, ids,
        len(groups["hamilton"]), len(groups["madison"]),
        means["hamilton"], means["madison"], tuple(scales[column] for column in usable),
    )


def choose_author(hamilton_distance, madison_distance):
    for distance in (hamilton_distance, madison_distance):
        if not math.isfinite(distance) or distance < 0:
            raise ValueError("Distances must be finite and nonnegative.")
    if abs(hamilton_distance - madison_distance) <= TIE_TOLERANCE:
        return "inconclusive"
    return "hamilton" if hamilton_distance < madison_distance else "madison"


def compare_essay(model: FittedProfiles, essay: EssayFrequencies):
    """Apply training-only profiles and scales without refitting any quantity."""
    if identifier(essay.essay_id) in model.training_ids:
        raise ValueError("An essay used for fitting cannot be scored as held out.")
    vector = frequency_vector(essay, model.features)
    contributions = tuple(
        tuple(abs(value - mean) / scale for value, mean, scale in zip(
            vector, profile, model.sample_standard_deviations
        ))
        for profile in (model.hamilton_mean, model.madison_mean)
    )
    if any(not math.isfinite(value) for group in contributions for value in group):
        raise ValueError("A standardized contribution is not finite.")
    distances = tuple(statistics.fmean(group) for group in contributions)
    return DistanceResult(
        distances[0], distances[1], distances[0] - distances[1],
        choose_author(*distances), contributions[0], contributions[1],
    )


def definition(root=ROOT):
    features = load_specification(root)
    settings = tomllib.loads((root / "config/research.toml").read_text("utf-8"))
    if settings["comparison"] != COMPARISON_SETTINGS:
        raise ValueError("Distance settings differ from the fixed method.")
    if settings["corpus"]["questioned"] != QUESTIONED_ID:
        raise ValueError("The questioned essay differs from the fixed plan.")
    return {
        **COMPARISON_SETTINGS,
        "main_features": list(features.words),
        "feature_check_features": features.as_dict()["feature_check_features"],
        "input_unit": "occurrences per 1,000 total word tokens",
        "author_mean": "Arithmetic mean of reference-essay frequencies, equal essay weights",
        "scaling_mean": "Arithmetic mean across all supplied training essays",
        "scaling_variance": "Sum of squared deviations from scaling_mean divided by n - 1",
        "scaling_standard_deviation": "Square root of scaling_variance",
        "contribution": "abs(r_query(word) - author_mean(word)) / training_sample_sd(word)",
        "distance": "Sum of contributions divided by the number of usable features",
        "constant_feature_rule": "Exclude exactly zero training standard deviation; no epsilon cutoff",
        "questioned_essay_id": QUESTIONED_ID,
        "fit_within_each_validation_trial": True,
        "reject_training_essay_as_query": True,
        "refit_on_query": False,
        "signed_gap": "Hamilton distance minus Madison distance; positive favors Madison",
        "probability_of_authorship": False,
    }


def fingerprints():
    return {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        for name in (
            "docs/research_plan.md", "config/research.toml", "metadata/word_features.json",
            ".python-version", "pyproject.toml", "uv.lock", "src/word_features.py",
            "src/distance_method.py", "tests/test_distance_method.py",
        )
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-record", action="store_true", help="Create a new method record once.")
    arguments = parser.parse_args()
    try:
        subprocess.run(
            [sys.executable, "-m", "src.word_features"], cwd=ROOT, check=True, timeout=30,
        )
        method, inputs = definition(), fingerprints()
        path = ROOT / RECORD
        if arguments.write_record:
            uv_version = subprocess.run(
                ["uv", "--version"], check=True, capture_output=True,
                text=True, timeout=30,
            ).stdout.strip()
            record = {
                "stage": "distance_method_definition",
                "recorded_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                "selection_origin": "Original research plan, version 1; method unchanged",
                "definition": method, "input_sha256": inputs,
                "runtime": {"python": platform.python_version(), "uv": uv_version},
                "corpus_frequency_tables_read_by_this_command": False,
                "real_reference_profiles_fitted": False,
                "known_author_validation_performed": False,
                "questioned_essay_compared": False,
            }
            with path.open("x", encoding="utf-8") as handle:
                json.dump(record, handle, indent=2, ensure_ascii=False)
                handle.write("\n")
        else:
            record = json.loads(path.read_text("utf-8"))
            if record["definition"] != method or record["input_sha256"] != inputs:
                raise ValueError("The method record or its implementation inputs changed.")
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        parser.exit(1, f"Distance-method check failed: {error}\n")
    print("Verified equal-essay means, training-only sample scaling, absolute distance, and tie rule.")
    print("No corpus profiles fitted, validation performed, or No. 49 comparison calculated.")


if __name__ == "__main__":
    main()
