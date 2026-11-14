"""Check project setup and optionally save an environment snapshot.

This command does not collect, prepare, count, or classify essay texts.
"""

import argparse
import csv
import hashlib
import json
import platform
import subprocess
import sys
import tomllib
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIRECTORIES = (
    "config",
    "data/raw/pages",
    "data/raw/texts",
    "data/clean",
    "data/no_quotes",
    "metadata",
    "src",
    "tests",
    "results/feature_check",
    "results/quotation_check",
    "docs",
    "report",
)
INPUT_FILES = (
    ".gitignore",
    ".python-version",
    "AGENTS.md",
    "README.md",
    "pyproject.toml",
    "uv.lock",
    "config/research.toml",
    "docs/research_plan.md",
    "metadata/sources.csv",
    "metadata/preparation.csv",
    "metadata/quotations.csv",
    "src/check_environment.py",
)
METADATA_FILES = (
    "metadata/sources.csv",
    "metadata/preparation.csv",
    "metadata/quotations.csv",
)


def command_output(*arguments):
    """Read the output of a local tool without invoking a shell."""
    return subprocess.run(
        arguments,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    ).stdout.rstrip("\n")


def checksum(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metadata_row_count(path):
    """Check CSV structure without treating a heading as a data record."""
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, strict=True)
        header = next(reader, [])
        if not header or any(not name for name in header):
            raise ValueError(f"Missing CSV headings: {path.relative_to(ROOT)}")
        if len(header) != len(set(header)):
            raise ValueError(f"Duplicate CSV headings: {path.relative_to(ROOT)}")
        count = 0
        for row in reader:
            if len(row) != len(header):
                raise ValueError(
                    f"Incorrect CSV field count: {path.relative_to(ROOT)}, "
                    f"line {reader.line_num}"
                )
            count += 1
        return count


def collect_snapshot():
    """Validate setup and describe the actual environment and settings."""
    pinned_python = (ROOT / ".python-version").read_text(encoding="utf-8").strip()
    if platform.python_version() != pinned_python:
        raise ValueError(
            f"Expected Python {pinned_python}; use uv run --locked python."
        )
    if Path(sys.prefix).resolve() != (ROOT / ".venv").resolve():
        raise ValueError("Use the project .venv interpreter through uv run.")

    for directory in DIRECTORIES:
        if not (ROOT / directory).is_dir():
            raise ValueError(f"Missing project directory: {directory}")
    for filename in INPUT_FILES:
        if not (ROOT / filename).is_file():
            raise ValueError(f"Missing setup file: {filename}")

    settings = tomllib.loads(
        (ROOT / "config/research.toml").read_text(encoding="utf-8")
    )
    plan = settings["research"]
    if checksum(ROOT / plan["plan_path"]) != plan["plan_sha256"]:
        raise ValueError("The original research plan checksum has changed.")

    corpus = settings["corpus"]
    references = corpus["hamilton"] + corpus["madison"]
    if (
        len(corpus["hamilton"]) != 8
        or len(corpus["madison"]) != 8
        or len(set(references)) != 16
        or corpus["questioned"] in references
    ):
        raise ValueError("Invalid or overlapping reference and questioned samples.")
    features = settings["counting"]["features"]
    if len(features) != 24 or len(set(features)) != 24:
        raise ValueError("Expected 24 distinct main-analysis word features.")

    row_counts = {
        filename: metadata_row_count(ROOT / filename)
        for filename in METADATA_FILES
    }
    git_commit = command_output("git", "rev-parse", "HEAD")
    git_status = command_output(
        "git", "status", "--porcelain=v1", "--untracked-files=all"
    )
    return {
        "activity": "environment_setup_check",
        "recorded_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "analysis_performed_by_this_command": False,
        "python": {
            "implementation": platform.python_implementation(),
            "version": platform.python_version(),
            "executable": sys.executable,
        },
        "uv_version": command_output("uv", "--version"),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "macos_version": platform.mac_ver()[0],
        },
        "git": {
            "commit": git_commit,
            "working_tree_dirty": bool(git_status),
            "status_porcelain": git_status.splitlines(),
        },
        "input_sha256": {
            filename: checksum(ROOT / filename) for filename in INPUT_FILES
        },
        "metadata_record_counts": row_counts,
        "settings": settings,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        help="Save a JSON snapshot to a new file; existing files are preserved.",
    )
    arguments = parser.parse_args()
    try:
        snapshot = collect_snapshot()
        if arguments.manifest is not None:
            destination = ROOT / arguments.manifest
            with destination.open("x", encoding="utf-8") as handle:
                json.dump(snapshot, handle, indent=2, ensure_ascii=False)
                handle.write("\n")
            print(f"Environment snapshot saved: {arguments.manifest}")
    except (OSError, ValueError, KeyError, csv.Error, subprocess.SubprocessError) as error:
        parser.exit(1, f"Environment check failed: {error}\n")
    print(f"Environment ready: Python {platform.python_version()}.")
    print("Layout, metadata structure, settings, and original plan checked.")
    print("No essay bodies were read or analyzed.")


if __name__ == "__main__":
    main()
