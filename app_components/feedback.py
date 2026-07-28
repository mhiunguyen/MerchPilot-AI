from __future__ import annotations

import csv
import io
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


FEEDBACK_COLUMNS = [
    "submission_timestamp",
    "participant_role",
    "test_scenario",
    "usefulness_rating",
    "explanation_clarity_rating",
    "trust_rating",
    "navigation_rating",
    "would_use",
    "most_useful_feature",
    "confusing_element",
    "improvement_suggestion",
    "participant_name",
    "organization",
    "email",
]


def is_public_mode() -> bool:
    explicit = os.getenv("MERCHPILOT_PUBLIC_MODE", "").strip().lower()
    return explicit in {"1", "true", "yes"} or bool(os.getenv("STREAMLIT_SHARING_MODE"))


def make_feedback_row(values: dict[str, Any]) -> dict[str, Any]:
    row = {column: values.get(column, "") for column in FEEDBACK_COLUMNS}
    row["submission_timestamp"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return row


def validate_feedback(row: dict[str, Any]) -> list[str]:
    required_text = [
        "participant_role",
        "test_scenario",
        "would_use",
        "most_useful_feature",
        "confusing_element",
        "improvement_suggestion",
    ]
    return [field for field in required_text if not str(row.get(field, "")).strip()]


def append_feedback(row: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists() and path.stat().st_size > 0
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FEEDBACK_COLUMNS)
        if not exists:
            writer.writeheader()
        writer.writerow({column: row.get(column, "") for column in FEEDBACK_COLUMNS})


def feedback_csv_bytes(rows: list[dict[str, Any]]) -> bytes:
    frame = pd.DataFrame(rows, columns=FEEDBACK_COLUMNS)
    stream = io.StringIO()
    frame.to_csv(stream, index=False)
    return stream.getvalue().encode("utf-8-sig")

