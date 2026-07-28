from __future__ import annotations

from typing import Any

import pandas as pd


ACTIVE_REVIEW_LABELS = {
    "Conversion Opportunity",
    "Promotion Test Candidate",
    "Discount Efficiency Review",
}


def safe_range(series: pd.Series, default: tuple[float, float] = (0.0, 0.0)) -> tuple[float, float]:
    values = pd.to_numeric(series, errors="coerce").dropna()
    if values.empty:
        return default
    return float(values.min()), float(values.max())


def apply_product_filters(frame: pd.DataFrame, filters: dict[str, Any]) -> pd.DataFrame:
    result = frame.copy()
    multi_fields = {
        "country_code": filters.get("countries"),
        "shop_name": filters.get("shops"),
        "platform_category": filters.get("platform_categories"),
        "shop_category": filters.get("shop_categories"),
        "recommendation_label": filters.get("recommendation_labels"),
        "confidence_level": filters.get("confidence_levels"),
    }
    for column, selected in multi_fields.items():
        if selected and column in result:
            result = result[result[column].isin(selected)]

    for column, key in {
        "opportunity_score": "score_range",
        "displayed_discount_pct": "discount_range",
        "liked_count": "likes_range",
        "rating_count": "rating_count_range",
        "price": "price_range",
    }.items():
        bounds = filters.get(key)
        if bounds is not None and column in result:
            values = pd.to_numeric(result[column], errors="coerce")
            result = result[values.between(bounds[0], bounds[1], inclusive="both")]

    for column, key in {
        "is_promoted": "promoted_status",
        "is_official_shop": "official_status",
    }.items():
        status = filters.get(key)
        if status in {"Yes", "No"} and column in result:
            expected = status == "Yes"
            result = result[result[column].fillna(False).astype(bool).eq(expected)]

    return result


SORT_OPTIONS: dict[str, tuple[str, bool]] = {
    "Opportunity score · high to low": ("opportunity_score", False),
    "Opportunity score · low to high": ("opportunity_score", True),
    "Likes · high to low": ("liked_count", False),
    "Rating count · high to low": ("rating_count", False),
    "Discount · high to low": ("displayed_discount_pct", False),
    "Sold-value proxy · high to low": ("monthly_sold_value", False),
    "Product name · A to Z": ("product_name", True),
}


def sort_products(frame: pd.DataFrame, option: str) -> pd.DataFrame:
    column, ascending = SORT_OPTIONS.get(option, SORT_OPTIONS["Opportunity score · high to low"])
    return frame.sort_values(column, ascending=ascending, na_position="last", kind="stable")


def format_local_price(value: Any, country_code: str) -> str:
    if value is None or pd.isna(value):
        return "Not available"
    unit = {"id": "IDR", "vn": "VND"}.get(str(country_code).lower(), "Local units")
    return f"{unit} {float(value):,.0f}"


def active_review_count(frame: pd.DataFrame) -> int:
    return int(frame["recommendation_label"].isin(ACTIVE_REVIEW_LABELS).sum())

