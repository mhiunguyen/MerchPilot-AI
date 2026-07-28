from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st

from app_components.ai_model import predict_contextual_benchmarks


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = ROOT / "outputs"
CHARTS_DIR = OUTPUTS_DIR / "charts"

FILES = {
    "recommendations": OUTPUTS_DIR / "product_recommendations.csv",
    "processed": OUTPUTS_DIR / "processed_latest_products.csv",
    "model_metrics": OUTPUTS_DIR / "model_metrics.csv",
    "feature_importance": OUTPUTS_DIR / "feature_importance.csv",
    "top_opportunities": OUTPUTS_DIR / "top_opportunities_by_country.csv",
    "score_sensitivity": OUTPUTS_DIR / "score_sensitivity.csv",
    "ai_model_artifact": OUTPUTS_DIR / "ai_model_artifact.json",
    "data_audit": OUTPUTS_DIR / "data_audit.json",
}

CHART_FILES = {
    "score_distribution": CHARTS_DIR / "01_opportunity_score_distribution.png",
    "recommendation_distribution": CHARTS_DIR / "02_recommendation_label_distribution.png",
    "top_opportunities": CHARTS_DIR / "03_top_10_opportunities.png",
    "engagement_gap": CHARTS_DIR / "04_engagement_vs_sold_conversion_gap.png",
    "discount_response": CHARTS_DIR / "05_discount_vs_peer_response.png",
    "feature_importance": CHARTS_DIR / "06_global_feature_importance.png",
    "model_baseline": CHARTS_DIR / "07_model_baseline_comparison.png",
    "score_sensitivity": CHARTS_DIR / "08_score_weight_sensitivity.png",
}

ALIASES: dict[str, tuple[str, ...]] = {
    "country_code": ("country", "market", "country_id"),
    "shop_id": ("seller_id",),
    "shop_name": ("seller_name", "shop"),
    "item_id": ("product_id", "listing_id"),
    "product_name": ("item_name", "name", "title"),
    "platform_category": ("category", "platform_cat"),
    "shop_category": ("seller_category",),
    "price": ("current_price", "item_price"),
    "original_price": ("price_original", "price_before_discount"),
    "displayed_discount_pct": ("discount_percent", "discount_pct"),
    "liked_count": ("likes", "like_count"),
    "rating_star": ("product_rating", "rating_score"),
    "rating_count": ("ratings", "review_count"),
    "monthly_sold_value": ("monthly_sold_value_proxy", "sold_value"),
    "shop_rating": ("rating", "seller_rating"),
    "shop_follower_count": ("follower_count", "followers"),
    "is_official_shop": ("official_shop", "is_official"),
    "is_promoted": ("promoted", "promotion_status"),
}

REQUIRED_COLUMNS = {
    "country_code",
    "shop_id",
    "shop_name",
    "item_id",
    "product_name",
    "platform_category",
    "price",
    "displayed_discount_pct",
    "liked_count",
    "rating_count",
    "monthly_sold_value",
    "opportunity_score",
    "recommendation_label",
    "confidence_level",
    "reason_1",
    "reason_2",
    "reason_3",
}

ENRICHMENT_COLUMNS = [
    "original_price",
    "rating_star",
    "shop_rating",
    "shop_follower_count",
    "is_official_shop",
    "is_promoted",
    "shop_category",
    "engagement_strength",
    "sold_pct_peer",
    "price_competitiveness",
    "promotion_efficiency",
    "shop_credibility",
    "conversion_gap",
    "likes_pct_peer",
    "price_pct_country_category",
    "discount_pct_peer",
]


class DataValidationError(RuntimeError):
    """Raised when an input cannot safely support the application."""


def _rename_aliases(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    for canonical, alternatives in ALIASES.items():
        if canonical in result.columns:
            continue
        match = next((name for name in alternatives if name in result.columns), None)
        if match:
            result = result.rename(columns={match: canonical})
    return result


def _read_csv(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path, low_memory=False)
    except Exception as exc:
        logging.exception("Unable to load %s", path)
        raise DataValidationError(f"Could not read {path.name}.") from exc


def _coalesce_column(frame: pd.DataFrame, column: str, candidates: tuple[str, ...]) -> None:
    if column in frame.columns:
        return
    for candidate in candidates:
        if candidate in frame.columns:
            frame[column] = frame[candidate]
            return


def _build_product_view(
    recommendations: pd.DataFrame,
    processed: pd.DataFrame,
    ai_benchmarks: pd.DataFrame,
) -> pd.DataFrame:
    recommendations = _rename_aliases(recommendations)
    processed = _rename_aliases(processed)
    processed = processed.reset_index(drop=True)
    missing = sorted(REQUIRED_COLUMNS - set(recommendations.columns))
    if missing:
        raise DataValidationError(
            "The recommendation export is missing required fields: " + ", ".join(missing)
        )

    for target, candidates in {
        "original_price": ("price_original",),
        "shop_rating": ("rating",),
        "shop_follower_count": ("follower_count",),
    }.items():
        _coalesce_column(processed, target, candidates)

    keys = ["country_code", "shop_id", "item_id"]
    available = [column for column in ENRICHMENT_COLUMNS if column in processed.columns]
    detail = processed[keys + available].drop_duplicates(keys, keep="last")
    overlap = [column for column in available if column in recommendations.columns]
    detail = detail.drop(columns=overlap)
    result = recommendations.merge(detail, on=keys, how="left", validate="one_to_one")

    result["country_code"] = (
        result["country_code"].astype("string").str.lower().replace({"indonesia": "id", "vietnam": "vn"})
    )
    result["country_name"] = result["country_code"].map({"id": "Indonesia", "vn": "Vietnam"})
    result["market_currency"] = result["country_code"].map({"id": "IDR", "vn": "VND"})
    result["product_key"] = (
        result["country_code"].astype(str)
        + " · "
        + result["shop_id"].astype(str)
        + " · "
        + result["item_id"].astype(str)
    )

    numeric_columns = [
        "price",
        "original_price",
        "displayed_discount_pct",
        "liked_count",
        "rating_star",
        "rating_count",
        "monthly_sold_value",
        "shop_rating",
        "shop_follower_count",
        "opportunity_score",
        "engagement_strength",
        "sold_pct_peer",
        "price_competitiveness",
        "promotion_efficiency",
        "shop_credibility",
        "conversion_gap",
        "likes_pct_peer",
        "price_pct_country_category",
        "discount_pct_peer",
    ]
    for column in numeric_columns:
        if column in result:
            result[column] = pd.to_numeric(result[column], errors="coerce")

    benchmark_columns = [
        "country_code",
        "shop_id",
        "item_id",
        "ai_predicted_log_sold_proxy",
        "ai_local_drivers",
    ]
    benchmarks = ai_benchmarks[
        [column for column in benchmark_columns if column in ai_benchmarks.columns]
    ].copy()
    result = result.merge(
        benchmarks,
        on=["country_code", "shop_id", "item_id"],
        how="left",
        validate="one_to_one",
    )
    result["ai_contextual_sold_benchmark"] = np.expm1(
        result["ai_predicted_log_sold_proxy"].clip(lower=0, upper=15)
    )
    expected = result["ai_contextual_sold_benchmark"].clip(lower=1)
    result["ai_observed_to_benchmark_ratio"] = result["monthly_sold_value"] / expected
    result["ai_benchmark_gap_pct"] = (
        result["monthly_sold_value"] - result["ai_contextual_sold_benchmark"]
    ) / expected
    result["ai_model_confidence"] = result["country_code"].map({"id": "High", "vn": "Low"})
    result.loc[result["ai_contextual_sold_benchmark"].isna(), "ai_model_confidence"] = "Unavailable"
    result["ai_benchmark_signal"] = "Near contextual benchmark"
    result.loc[
        result["ai_observed_to_benchmark_ratio"].lt(0.60),
        "ai_benchmark_signal",
    ] = "Below contextual benchmark"
    result.loc[
        result["ai_observed_to_benchmark_ratio"].gt(1.50),
        "ai_benchmark_signal",
    ] = "Above contextual benchmark"
    result.loc[
        result["ai_contextual_sold_benchmark"].isna(),
        "ai_benchmark_signal",
    ] = "Benchmark unavailable"
    result.loc[
        result["monthly_sold_value"].isna(),
        "ai_benchmark_signal",
    ] = "Observed proxy unavailable"

    if "ai_local_drivers" not in result:
        result["ai_local_drivers"] = pd.NA

    if result.duplicated(keys).any():
        raise DataValidationError("The recommendation export contains duplicate product keys.")
    return result


def validate_assets() -> list[str]:
    problems: list[str] = []
    required_files = [
        "recommendations",
        "processed",
        "model_metrics",
        "feature_importance",
        "top_opportunities",
        "score_sensitivity",
        "ai_model_artifact",
    ]
    for name in required_files:
        if not FILES[name].is_file():
            problems.append(f"Missing required file: {FILES[name].name}")
    for name, path in CHART_FILES.items():
        if not path.is_file():
            problems.append(f"Missing chart asset: {name}")
    return problems


@st.cache_data(show_spinner="Loading precomputed decision outputs…")
def load_app_data() -> dict[str, Any]:
    problems = validate_assets()
    if problems:
        raise DataValidationError(" ".join(problems))

    recommendations = _read_csv(FILES["recommendations"])
    processed = _read_csv(FILES["processed"])
    try:
        ai_model_artifact = json.loads(FILES["ai_model_artifact"].read_text(encoding="utf-8"))
    except Exception as exc:
        logging.exception("Unable to load %s", FILES["ai_model_artifact"])
        raise DataValidationError("Could not read ai_model_artifact.json.") from exc
    ai_benchmarks = predict_contextual_benchmarks(processed, ai_model_artifact)
    products = _build_product_view(
        recommendations,
        processed,
        ai_benchmarks,
    )
    return {
        "products": products,
        "model_metrics": _read_csv(FILES["model_metrics"]),
        "feature_importance": _read_csv(FILES["feature_importance"]),
        "top_opportunities": _read_csv(FILES["top_opportunities"]),
        "score_sensitivity": _read_csv(FILES["score_sensitivity"]),
        "charts": CHART_FILES,
    }


def display_value(value: Any, *, digits: int = 1) -> str:
    if value is None or pd.isna(value):
        return "Not available"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, (int, float)):
        return f"{value:,.{digits}f}"
    return str(value)
