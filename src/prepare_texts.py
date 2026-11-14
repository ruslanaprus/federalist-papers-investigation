"""Prepare readable essay bodies while preserving raw sources and an edit log.

Clean copies retain case, spelling, apostrophes, and quotations. The separate
normalization helper implements the fixed rules for later word counting.
"""

import argparse
import csv
from dataclasses import dataclass
import hashlib
import io
import json
import platform
import re
import subprocess
import sys
import tomllib
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADDRESS = "To the People of the State of New York:"
FOOTNOTE_MARKER = re.compile(r"【\d+†\^\{\d+\}】")
LOG_FIELDS = (
    "essay_number", "input_path", "output_path", "operation",
    "source_location", "original_text", "replacement_text", "reason",
)


@dataclass(frozen=True)
class Edit:
    start: int
    end: int
    replacement: str
    operation: str
    reason: str


def digest(content):
    return hashlib.sha256(content).hexdigest()


def normalize_for_counting(text):
    """Apply the fixed counting normalization without counting any words."""
    return text.lower().translate({ord("‘"): "'", ord("’"): "'"})


def apply_edits(text, edits):
    pieces, position = [], 0
    for edit in sorted(edits, key=lambda item: (item.start, item.end)):
        if not position <= edit.start <= edit.end <= len(text):
            raise ValueError("Preparation edits overlap or exceed the raw text.")
        pieces.extend((text[position:edit.start], edit.replacement))
        position = edit.end
    pieces.append(text[position:])
    return "".join(pieces)


def prepare_text(text):
    """Select main prose using structural boundaries, never topic or style."""
    lines = text.splitlines(keepends=True)
    offsets, position = [], 0
    for line in lines:
        offsets.append(position)
        position += len(line)
    addresses = [index for index, line in enumerate(lines) if line.strip() == ADDRESS]
    if len(addresses) != 1:
        raise ValueError("Expected exactly one standalone address to readers.")
    first = addresses[0] + 1
    while first < len(lines) and not lines[first].strip():
        first += 1
    if first == len(lines):
        raise ValueError("No essay body follows the reader address.")
    body_start = offsets[first]
    edits = [Edit(
        0, body_start, "", "remove_header",
        "Remove essay heading, title, publication details, author label, and shared reader address.",
    )]
    signatures = [
        index for index in range(first, len(lines))
        if lines[index].strip() in {"PUBLIUS", "PUBLIUS."}
    ]
    if len(signatures) > 1:
        raise ValueError("Multiple standalone signatures require manual review.")
    end = signatures[0] if signatures else len(lines)
    if signatures:
        signature = signatures[0]
        signature_end = offsets[signature] + len(lines[signature])
        edits.append(Edit(
            offsets[signature], signature_end, "", "remove_signature",
            "Remove the shared standalone closing signature, not occurrences inside prose.",
        ))
        tail = text[signature_end:]
        if tail.strip():
            if not re.match(r"\s*\d+\.\s", tail):
                raise ValueError("Unrecognized material after signature requires manual review.")
            edits.append(Edit(
                signature_end, len(text), "", "exclude_appended_notes",
                "Exclude the separately numbered source notes from the main running prose; "
                "this structural rule does not claim all notes are editorial.",
            ))
        elif tail:
            edits.append(Edit(
                signature_end, len(text), "", "remove_boundary_blank_lines",
                "Remove blank material outside the essay body.",
            ))
    body_limit = offsets[end] if end < len(lines) else len(text)
    while end > first and not lines[end - 1].strip():
        end -= 1
    body_end = offsets[end] if end < len(lines) else len(text)
    if body_end <= body_start:
        raise ValueError("The prepared body would be empty.")
    if body_end < body_limit:
        edits.append(Edit(
            body_end, body_limit, "", "remove_boundary_blank_lines",
            "Remove blank lines between the main prose and closing apparatus.",
        ))
    for match in FOOTNOTE_MARKER.finditer(text, body_start, body_end):
        before = text[match.start() - 1] if match.start() > body_start else ""
        after = text[match.end()] if match.end() < body_end else ""
        replacement = " " if before.isalpha() and after.isalpha() else ""
        edits.append(Edit(
            match.start(), match.end(), replacement, "remove_note_reference",
            "Remove a reader-rendered numeric footnote reference; preserve any word boundary.",
        ))
    if not text[body_start:body_end].endswith("\n"):
        edits.append(Edit(
            body_end, body_end, "\n", "ensure_final_newline",
            "End the UTF-8 prepared file with a newline without changing words.",
        ))
    edits.sort(key=lambda item: (item.start, item.end))
    prepared = apply_edits(text, edits)
    if "【" in prepared or "】" in prepared or "Back to text" in prepared:
        raise ValueError("Unrecognized reader markup remains; manual review required.")
    if re.search(r"</?[A-Za-z][^>]*>", prepared):
        raise ValueError("Unexpected HTML remains in the collected text.")
    return prepared, edits


def raw_checksums(root):
    return {
        path.relative_to(root).as_posix(): digest(path.read_bytes())
        for path in sorted((root / "data/raw").rglob("*")) if path.is_file()
    }


def build_preparation(root):
    settings = tomllib.loads((root / "config/research.toml").read_text("utf-8"))
    plan = settings["research"]
    if digest((root / plan["plan_path"]).read_bytes()) != plan["plan_sha256"]:
        raise ValueError("The original research plan has changed.")
    with (root / "metadata/sources.csv").open(encoding="utf-8", newline="") as handle:
        sources = list(csv.DictReader(handle))
    if not sources or len({row["edition"] for row in sources}) != 1:
        raise ValueError("Expected a nonempty corpus from exactly one recorded edition.")
    base_url = settings["research"]["source_collection"].rsplit("/", 1)[0] + "/text-"
    outputs, records, essay_records = {}, [], []
    for row in sources:
        if not row["url"].startswith(base_url):
            raise ValueError("A collected text is outside the specified Library of Congress edition.")
        source_path = root / row["raw_text_path"]
        original = source_path.read_bytes()
        if digest(original) != row["raw_text_sha256"]:
            raise ValueError(f"Raw text checksum mismatch: {row['raw_text_path']}")
        text = original.decode("utf-8")
        prepared, edits = prepare_text(text)
        output_path = f"data/clean/{source_path.name}"
        outputs[output_path] = prepared.encode("utf-8")
        for edit in edits:
            first_line = text.count("\n", 0, edit.start) + 1
            last_line = text.count("\n", 0, max(edit.start, edit.end - 1)) + 1
            records.append(dict(zip(LOG_FIELDS, (
                row["essay_number"], row["raw_text_path"], output_path, edit.operation,
                f"characters [{edit.start}, {edit.end}); raw lines {first_line}-{last_line}",
                text[edit.start:edit.end], edit.replacement, edit.reason,
            ))))
        essay_records.append({
            "essay_number": int(row["essay_number"]), "role": row["role"],
            "raw_path": row["raw_text_path"], "raw_sha256": digest(original),
            "prepared_path": output_path,
            "prepared_sha256": digest(outputs[output_path]),
            "edit_count": len(edits),
            "contains_double_quote_characters": any(char in prepared for char in '\"“”'),
            "quotation_passages_removed": False,
            "quotation_annotation_status": "not_yet_performed",
            "spelling_corrections": [],
        })
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=LOG_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(records)
    return settings, outputs, buffer.getvalue().encode("utf-8"), essay_records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="Check prepared copies without writing.")
    parser.add_argument(
        "--allow-incomplete", action="store_true",
        help="Prepare only collected essays, explicitly retaining incomplete-corpus status.",
    )
    arguments = parser.parse_args()
    try:
        command = [sys.executable, str(ROOT / "src/assemble_corpus.py"), "--verify"]
        if arguments.allow_incomplete:
            command.append("--allow-incomplete")
        subprocess.run(command, cwd=ROOT, check=True, timeout=30)
        before = raw_checksums(ROOT)
        settings, outputs, log, essays = build_preparation(ROOT)
        manifest_path = ROOT / "results/preparation_manifest.json"
        log_path = ROOT / "metadata/preparation.csv"
        expected = {Path(path).name for path in outputs}
        actual = {path.name for path in (ROOT / "data/clean").glob("*.txt")}
        if actual - expected:
            raise ValueError("Unexpected prepared essay files found.")
        for filename, content in outputs.items():
            path = ROOT / filename
            if path.exists() and path.read_bytes() != content:
                raise ValueError(f"Prepared copy differs; refusing to replace {filename}.")
            if arguments.verify and not path.exists():
                raise ValueError(f"Prepared copy missing: {filename}")
        if arguments.verify:
            manifest = json.loads(manifest_path.read_text("utf-8"))
            if log_path.read_bytes() != log or manifest["preparation_log_sha256"] != digest(log):
                raise ValueError("Preparation log differs from the recorded edits.")
            if manifest["raw_sha256"] != before or manifest["essays"] != essays:
                raise ValueError("Raw evidence or prepared-copy records changed.")
        else:
            if manifest_path.exists():
                raise ValueError("Preparation manifest exists; use --verify to preserve it.")
            with log_path.open(encoding="utf-8", newline="") as handle:
                if len(list(csv.reader(handle))) != 1:
                    raise ValueError("Existing preparation decisions must be preserved.")
            uv_version = subprocess.run(
                ["uv", "--version"], check=True, capture_output=True,
                text=True, timeout=30,
            ).stdout.strip()
            revision = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True,
                capture_output=True, text=True, timeout=30,
            ).stdout.strip()
            manifest = {
                "stage": "text_preparation",
                "status": "complete" if len(essays) == 17 else "incomplete_corpus",
                "recorded_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                "prepared_essay_count": len(essays),
                "missing_essays": json.loads(
                    (ROOT / "results/corpus_collection_manifest.json").read_text("utf-8")
                )["missing_essays"],
                "edition": "Library of Congress online presentation, Project Gutenberg compilation",
                "runtime": {"python": platform.python_version(), "uv": uv_version},
                "git_revision": revision,
                "code_sha256": {
                    path.relative_to(ROOT).as_posix(): digest(path.read_bytes())
                    for folder in ("src", "tests")
                    for path in sorted((ROOT / folder).glob("*.py"))
                },
                "research_plan_sha256": settings["research"]["plan_sha256"],
                "config_sha256": digest((ROOT / "config/research.toml").read_bytes()),
                "sources_log_sha256": digest((ROOT / "metadata/sources.csv").read_bytes()),
                "collection_manifest_sha256": digest(
                    (ROOT / "results/corpus_collection_manifest.json").read_bytes()
                ),
                "raw_sha256": before,
                "preparation_log_sha256": digest(log),
                "prepared_copies_preserve_case_and_apostrophes": True,
                "counting_normalization_applied_to_saved_copies": False,
                "counting_normalization_helper": "src/prepare_texts.py:normalize_for_counting",
                "appended_source_notes": "excluded_from_main_running_prose",
                "quotation_passages_removed": False,
                "spelling_corrections_made": False,
                "word_counts_calculated": False,
                "authorship_analysis_performed": False,
                "essays": essays,
            }
            for filename, content in outputs.items():
                path = ROOT / filename
                if not path.exists():
                    with path.open("xb") as handle:
                        handle.write(content)
            log_path.write_bytes(log)
            with manifest_path.open("x", encoding="utf-8") as handle:
                json.dump(manifest, handle, indent=2, ensure_ascii=False)
                handle.write("\n")
        if raw_checksums(ROOT) != before:
            raise ValueError("Raw evidence changed during preparation.")
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        parser.exit(1, f"Preparation failed: {error}\n")
    action = "Verified" if arguments.verify else "Prepared"
    print(f"{action} {len(essays)} of 17 planned essays; raw evidence unchanged.")
    print("Quotations and original word forms retained; no counts or attribution performed.")


if __name__ == "__main__":
    main()
