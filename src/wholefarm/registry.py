"""Read and validate the master variable and equation registry."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REQUIRED_COLUMNS = (
    "variable_id", "name", "kind", "unit", "data_type", "spatial_scale",
    "temporal_scale", "requirement", "default", "constraints", "equation",
    "module", "method_origin", "evidence_class", "source_id", "source_locator",
    "status", "notes",
)
ALLOWED_KINDS = {"input", "derived", "output", "parameter", "state"}
ALLOWED_REQUIREMENTS = {"required", "conditional", "optional"}
ALLOWED_STATUSES = {"provisional", "verified", "deprecated"}
ALLOWED_EVIDENCE = {
    "field_measurement", "laboratory_measurement", "survey", "remote_sensing",
    "mapped_covariate", "model_parameter", "model_output", "accounting_rule",
    "calculated", "configuration",
}


@dataclass(frozen=True)
class RegistryIssue:
    row: int
    field: str
    message: str

    def __str__(self) -> str:
        location = f"row {self.row}" if self.row else "header"
        return f"{location}, {self.field}: {self.message}"


def read_registry(path: str | Path) -> tuple[list[str], list[dict[str, str]]]:
    """Return the CSV headers and normalized registry rows."""
    with Path(path).open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        headers = reader.fieldnames or []
        rows = [
            {key: (value or "").strip() for key, value in row.items() if key is not None}
            for row in reader
        ]
    return headers, rows


def validate_registry(headers: Iterable[str], rows: list[dict[str, str]]) -> list[RegistryIssue]:
    """Validate structure, controlled vocabularies and stable identifiers."""
    header_set = set(headers)
    issues = [
        RegistryIssue(0, column, "required column is missing")
        for column in REQUIRED_COLUMNS if column not in header_set
    ]
    if issues:
        return issues

    seen: dict[str, int] = {}
    for line_number, row in enumerate(rows, start=2):
        variable_id = row["variable_id"]
        for field in ("variable_id", "name", "kind", "unit", "data_type", "module", "status"):
            if not row[field]:
                issues.append(RegistryIssue(line_number, field, "value is required"))
        if variable_id in seen:
            issues.append(RegistryIssue(line_number, "variable_id", f"duplicate of row {seen[variable_id]}"))
        elif variable_id:
            seen[variable_id] = line_number
        if variable_id and (variable_id.lower() != variable_id or " " in variable_id):
            issues.append(RegistryIssue(line_number, "variable_id", "must be lowercase and contain no spaces"))
        if row["kind"] not in ALLOWED_KINDS:
            issues.append(RegistryIssue(line_number, "kind", "unknown controlled value"))
        if row["requirement"] not in ALLOWED_REQUIREMENTS:
            issues.append(RegistryIssue(line_number, "requirement", "unknown controlled value"))
        if row["status"] not in ALLOWED_STATUSES:
            issues.append(RegistryIssue(line_number, "status", "unknown controlled value"))
        if row["evidence_class"] not in ALLOWED_EVIDENCE:
            issues.append(RegistryIssue(line_number, "evidence_class", "unknown controlled value"))
        if row["status"] == "verified" and (not row["source_id"] or not row["source_locator"]):
            issues.append(RegistryIssue(line_number, "source_locator", "verified rows require source and locator"))
        if row["requirement"] == "required" and row["default"]:
            issues.append(RegistryIssue(line_number, "default", "required inputs must not silently default"))
    if not rows:
        issues.append(RegistryIssue(0, "rows", "registry is empty"))
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate",))
    parser.add_argument("path", type=Path)
    args = parser.parse_args(argv)
    headers, rows = read_registry(args.path)
    issues = validate_registry(headers, rows)
    if issues:
        for issue in issues:
            print(issue)
        return 1
    print(f"Registry valid: {len(rows)} entries in {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

