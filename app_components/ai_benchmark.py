from __future__ import annotations

from typing import Any, Mapping

import pandas as pd


def _percentile(value: Any) -> str:
    if value is None or pd.isna(value):
        return "an unavailable"
    return f"the {float(value):.0%}"


def ai_decision_brief(product: Mapping[str, Any]) -> str:
    """Create a grounded explanation from the cross-validated model benchmark."""
    signal = str(product.get("ai_benchmark_signal", "Benchmark unavailable"))
    confidence = str(product.get("ai_model_confidence", "Unavailable"))
    if signal == "Benchmark unavailable":
        return (
            "The AI-assisted benchmark is unavailable for this listing because the modeling "
            "target is missing. Use the transparent opportunity score and peer evidence."
        )
    if signal == "Observed proxy unavailable":
        return (
            "The model can estimate a contextual benchmark for this listing, but the observed "
            "monthly sold-value proxy is missing, so no performance gap is calculated. Use the "
            "transparent opportunity score and collect the missing outcome before comparison."
        )

    engagement = _percentile(product.get("likes_pct_peer"))
    price = _percentile(product.get("price_pct_country_category"))
    if signal == "Below contextual benchmark":
        core = (
            "The cross-validated model places this listing below the sold-value level associated "
            f"with comparable context. Engagement is at {engagement} peer percentile and price is "
            f"at {price} peer percentile, so the gap is a review signal for possible conversion friction."
        )
    elif signal == "Above contextual benchmark":
        core = (
            "Observed sold-value is above the model's contextual benchmark. This supports protecting "
            f"the listing's current execution while monitoring its {engagement} engagement position."
        )
    else:
        core = (
            "Observed sold-value is close to the model's contextual benchmark. The model does not "
            "identify a large performance gap, so the transparent score and business context should "
            "drive the review."
        )

    if confidence == "Low":
        core += (
            " Vietnam model confidence is low, so this signal must not override the transparent "
            "score or human judgment."
        )
    else:
        core += " This is a cross-sectional benchmark, not a future-sales forecast."
    return core
