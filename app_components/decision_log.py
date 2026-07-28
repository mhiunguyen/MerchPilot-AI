from __future__ import annotations

import csv
import io
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import pandas as pd


DECISION_COLUMNS = [
    "submission_timestamp",
    "country_code",
    "shop_id",
    "shop_name",
    "item_id",
    "product_name",
    "platform_category",
    "opportunity_score",
    "recommendation_label",
    "recommendation_confidence",
    "ai_benchmark_signal",
    "ai_model_confidence",
    "reviewer_role",
    "reviewer_name",
    "decision_status",
    "selected_action",
    "decision_rationale",
    "success_metric",
    "review_date",
]


def make_decision_row(
    product: Mapping[str, Any], values: Mapping[str, Any]
) -> dict[str, Any]:
    row = {column: "" for column in DECISION_COLUMNS}
    row.update(
        {
            "submission_timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "country_code": product.get("country_code", ""),
            "shop_id": product.get("shop_id", ""),
            "shop_name": product.get("shop_name", ""),
            "item_id": product.get("item_id", ""),
            "product_name": product.get("product_name", ""),
            "platform_category": product.get("platform_category", ""),
            "opportunity_score": product.get("opportunity_score", ""),
            "recommendation_label": product.get("recommendation_label", ""),
            "recommendation_confidence": product.get("confidence_level", ""),
            "ai_benchmark_signal": product.get("ai_benchmark_signal", ""),
            "ai_model_confidence": product.get("ai_model_confidence", ""),
        }
    )
    for column in DECISION_COLUMNS:
        if column in values:
            row[column] = values[column]
    return row


def validate_decision(row: Mapping[str, Any]) -> list[str]:
    required = [
        "reviewer_role",
        "decision_status",
        "selected_action",
        "decision_rationale",
        "success_metric",
        "review_date",
    ]
    return [column for column in required if not str(row.get(column, "")).strip()]


def append_decision(row: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists() and path.stat().st_size > 0
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=DECISION_COLUMNS)
        if not exists:
            writer.writeheader()
        writer.writerow({column: row.get(column, "") for column in DECISION_COLUMNS})


def decision_csv_bytes(rows: list[Mapping[str, Any]]) -> bytes:
    frame = pd.DataFrame(rows, columns=DECISION_COLUMNS)
    stream = io.StringIO()
    frame.to_csv(stream, index=False)
    return stream.getvalue().encode("utf-8-sig")
