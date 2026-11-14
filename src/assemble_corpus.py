"""Extract the fixed corpus from archived Library of Congress reader snapshots.

Reader snapshots preserve the retrieval tool's responses, not original HTML.
This command performs structural extraction and integrity checks, not analysis.
"""

import argparse
import csv
import hashlib
import io
import json
import platform
import re
import subprocess
import tomllib
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_FIELDS = (
    "essay_number", "role", "source_attribution", "url", "edition",
    "retrieved_date", "raw_page_path", "raw_page_sha256", "raw_text_path",
    "raw_text_sha256", "preparation_notes",
)
ATTRIBUTIONS = {
    "hamilton": ("H", "Hamilton", "Author: Alexander Hamilton"),
    "madison": ("M", "Madison", "Author: James Madison"),
    "questioned": (
        "Q", "Hamilton or Madison", "Author: Alexander Hamilton or James Madison"
    ),
}


class UnavailablePage(ValueError):
    """A required source snapshot could not be retrieved completely."""


def digest(content):
    return hashlib.sha256(content).hexdigest()


def project_lines(snapshot):
    """Recover every numbered line, rejecting gaps and conflicting evidence."""
    total = snapshot["total_lines"]
    if not isinstance(total, int) or total <= 0:
        raise UnavailablePage(f"No complete retrieval: {snapshot['source_url']}")
    lines = {}
    resolved = set()
    for capture in snapshot["responses"]:
        response = capture["response"]
        reported = re.search(r"Total lines: (\d+)", response)
        if reported and int(reported.group(1)) != total:
            raise ValueError("Source line count changed between retrievals.")
        for match in re.finditer(r"^L(\d+): ?(.*)$", response, re.MULTILINE):
            number, text = int(match.group(1)), match.group(2)
            if number not in lines or lines[number] == text:
                lines[number] = text
                continue
            short, long = sorted((lines[number], text), key=len)
            if not short.endswith("...") or not long.startswith(short[:-3]):
                raise ValueError(f"Conflicting source representations at L{number}.")
            lines[number] = long
            resolved.add(number)
    if set(lines) != set(range(total)):
        raise UnavailablePage(f"Missing source lines: {snapshot['source_url']}")
    return [lines[number] for number in range(total)], sorted(resolved)


def index_attributions(lines):
    authors = {}
    for line in lines:
        if re.match(r"^\s*\d+\.\s*\|", line):
            cells = line.split("|")
            number = int(cells[0].strip().rstrip("."))
            if number in authors:
                raise ValueError(f"Duplicate authorship table entry: {number}")
            authors[number] = cells[2].strip()
    if set(authors) != set(range(1, 86)):
        raise ValueError("The source authorship table is incomplete.")
    return authors


def extract_section(lines, number, expected_author):
    headings = {}
    for position, line in enumerate(lines):
        match = re.fullmatch(r"## Federalist No\. (\d+)", line)
        if match:
            essay = int(match.group(1))
            if essay in headings:
                raise ValueError(f"Duplicate essay heading: {essay}")
            headings[essay] = position
    if number not in headings:
        raise ValueError(f"Essay heading missing: {number}")
    start = headings[number]
    following = [position for position in headings.values() if position > start]
    end = min(following) if following else len(lines)
    for position in range(start, end):
        if re.match(r"\s*\*\s+【\d+†(?:<< Previous:|Next:)", lines[position]):
            end = position
            break
    section = lines[start:end]
    author_lines = [line for line in section if line.startswith("Author:")]
    if author_lines != [expected_author]:
        raise ValueError(f"Unexpected source-page attribution for No. {number}.")
    if "To the People of the State of New York:" not in section:
        raise ValueError(f"Essay address missing: {number}")
    while section and not section[-1].strip():
        section.pop()
    return ("\n".join(section) + "\n").encode("utf-8"), start, start + len(section) - 1


def build_corpus(root):
    settings = tomllib.loads((root / "config/research.toml").read_text("utf-8"))
    plan = settings["research"]
    if digest((root / plan["plan_path"]).read_bytes()) != plan["plan_sha256"]:
        raise ValueError("The fixed research plan has changed.")
    index_path = root / "data/raw/pages/loc_index.reader.json"
    index = json.loads(index_path.read_text("utf-8"))
    authors = index_attributions(project_lines(index)[0])
    records, outputs, missing, pages = [], {}, [], {}
    selected = [
        (role, number)
        for role in ("hamilton", "madison", "questioned")
        for number in (
            [settings["corpus"][role]]
            if role == "questioned" else settings["corpus"][role]
        )
    ]
    if len(selected) != 17 or len({number for _, number in selected}) != 17:
        raise ValueError("Expected 17 distinct planned essays.")
    for role, number in selected:
        prefix, expected_table, expected_page = ATTRIBUTIONS[role]
        if authors.get(number) != expected_table:
            raise ValueError(f"Authorship-table conflict for No. {number}.")
        first = ((number - 1) // 10) * 10 + 1
        relative = f"data/raw/pages/loc_text-{first}-{first + 9}.reader.json"
        path = root / relative
        snapshot = json.loads(path.read_text("utf-8"))
        try:
            lines, resolved = project_lines(snapshot)
        except UnavailablePage as error:
            missing.append({"essay_number": number, "role": role, "reason": str(error)})
            continue
        content, start, end = extract_section(lines, number, expected_page)
        text_path = f"data/raw/texts/{prefix}_{number}.txt"
        outputs[text_path] = content
        pages[relative] = {
            "sha256": digest(path.read_bytes()),
            "verified_line_count": len(lines),
            "resolved_shortened_reader_lines": resolved,
        }
        records.append(dict(zip(SOURCE_FIELDS, (
            number, role, authors[number], snapshot["source_url"],
            "Library of Congress online presentation, Project Gutenberg compilation",
            snapshot["retrieved_date"], relative, digest(path.read_bytes()),
            text_path, digest(content),
            f"Reader representation, source lines L{start}-L{end}. "
            f"Source page: {expected_page}. Structural extraction only; headings, "
            "publication details, address, signature if present, quotations, and "
            "footnotes retained. No linguistic normalization. Original HTML "
            "bytes unavailable; exact retrieval responses archived in snapshot.",
        ))))
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=SOURCE_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(records)
    return settings, records, outputs, buffer.getvalue().encode("utf-8"), missing, pages


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="Check saved corpus without writing.")
    parser.add_argument(
        "--manifest", type=Path,
        default=Path("results/corpus_collection_manifest.json"),
        help="Collection record to create or verify; existing records are preserved.",
    )
    parser.add_argument(
        "--allow-incomplete", action="store_true",
        help="Explicitly allow verified available essays while listing missing ones.",
    )
    arguments = parser.parse_args()
    try:
        settings, records, outputs, source_log, missing, pages = build_corpus(ROOT)
        if missing and not arguments.allow_incomplete:
            numbers = ", ".join(str(item["essay_number"]) for item in missing)
            raise ValueError(f"Fixed corpus incomplete; missing Nos. {numbers}.")
        for path, content in outputs.items():
            target = ROOT / path
            if target.exists() and target.read_bytes() != content:
                raise ValueError(f"Existing raw text differs; refusing to replace {path}.")
            if arguments.verify and not target.exists():
                raise ValueError(f"Collected text missing: {path}")
        actual = {path.name for path in (ROOT / "data/raw/texts").glob("*.txt")}
        expected = {Path(path).name for path in outputs}
        if actual - expected:
            raise ValueError("Unexpected essay files found in the raw corpus.")
        log_path = ROOT / "metadata/sources.csv"
        manifest_path = ROOT / arguments.manifest
        if arguments.verify:
            if log_path.read_bytes() != source_log:
                raise ValueError("Source log differs from the archived evidence.")
            recorded = json.loads(manifest_path.read_text("utf-8"))
            if recorded["source_log_sha256"] != digest(source_log):
                raise ValueError("Source log differs from the collection manifest.")
            if recorded["source_records"] != records:
                raise ValueError("Corpus records differ from the collection manifest.")
            if recorded["page_snapshots"] != pages:
                raise ValueError("Source snapshots differ from the collection manifest.")
        else:
            if manifest_path.exists():
                raise ValueError("Collection manifest exists; use --verify to preserve it.")
            uv_version = subprocess.run(
                ["uv", "--version"], check=True, capture_output=True,
                text=True, timeout=30,
            ).stdout.strip()
            for path, content in outputs.items():
                target = ROOT / path
                if not target.exists():
                    with target.open("xb") as handle:
                        handle.write(content)
            log_path.write_bytes(source_log)
            manifest = {
                "stage": "corpus_collection",
                "status": "incomplete" if missing else "complete",
                "recorded_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                "runtime": {
                    "python_version": platform.python_version(),
                    "uv_version": uv_version,
                    "operating_system": platform.platform(),
                },
                "planned_essay_count": 17,
                "collected_essay_count": len(records),
                "missing_essays": missing,
                "retrieval_method": "archived_web_reader_responses",
                "original_html_bytes_preserved": False,
                "linguistic_preparation_performed": False,
                "authorship_analysis_performed": False,
                "research_plan_sha256": settings["research"]["plan_sha256"],
                "script_sha256": digest(Path(__file__).read_bytes()),
                "config_sha256": digest((ROOT / "config/research.toml").read_bytes()),
                "index_sha256": digest((ROOT / "data/raw/pages/loc_index.reader.json").read_bytes()),
                "source_log_sha256": digest(source_log),
                "page_snapshots": pages,
                "source_records": records,
            }
            with manifest_path.open("x", encoding="utf-8") as handle:
                json.dump(manifest, handle, indent=2, ensure_ascii=False)
                handle.write("\n")
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        parser.exit(1, f"Corpus check failed: {error}\n")
    action = "Verified" if arguments.verify else "Saved"
    print(f"{action} {len(records)} of 17 planned essays and their source records.")
    if missing:
        print("INCOMPLETE: missing " + ", ".join(f"No. {item['essay_number']}" for item in missing))
    print("No essay frequencies, validation scores, or authorship distances calculated.")


if __name__ == "__main__":
    main()
