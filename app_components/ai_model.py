from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def _transform(frame: pd.DataFrame, design: dict[str, Any]) -> np.ndarray:
    numeric_names = design["numeric_names"]
    numeric = frame.reindex(columns=numeric_names).apply(pd.to_numeric, errors="coerce").to_numpy(float)
    medians = np.asarray(design["medians"], dtype=float)
    means = np.asarray(design["means"], dtype=float)
    scales = np.asarray(design["scales"], dtype=float)
    numeric = np.where(np.isfinite(numeric), numeric, medians)
    matrices = [(numeric - means) / scales]
    for column, levels in design["category_levels"].items():
        values = frame.get(column, pd.Series("Unknown", index=frame.index)).fillna("Unknown").astype(str)
        categories = levels[1:]
        if categories:
            matrices.append(
                np.column_stack([(values == category).astype(float) for category in categories])
            )
    return np.column_stack(matrices)


def _friendly_feature(name: str) -> str:
    mapping = {
        "log1p_liked_count": "listing likes",
        "log1p_rating_count": "rating volume",
        "price_pct_country_category": "peer-relative price",
        "price_pct_shop": "shop-relative price",
        "displayed_discount_pct": "displayed discount depth",
        "discount_pct_peer": "peer-relative discount",
        "is_promoted": "current promotion status",
        "promotion_mechanism_count": "promotion mechanism count",
        "log1p_follower_count": "shop followers",
        "rating_star": "shop rating",
        "shop_assortment_size": "shop assortment size",
    }
    return mapping.get(name, name.replace("_", " ").replace("=", ": "))


def predict_contextual_benchmarks(
    frame: pd.DataFrame, artifact: dict[str, Any]
) -> pd.DataFrame:
    """Run the compact model artifact against already-deployed product features."""
    outputs: list[pd.DataFrame] = []
    keys = ["country_code", "shop_id", "item_id"]
    for country, model_artifact in artifact.get("country_models", {}).items():
        country_frame = frame[frame["country_code"].eq(country)].copy()
        if country_frame.empty:
            continue
        design = model_artifact["design"]
        x = _transform(country_frame, design)
        feature_names = design["feature_names"]
        prediction = np.full(len(country_frame), float(model_artifact["model"]["base"]))
        contributions = np.zeros((len(country_frame), len(feature_names)))
        for stump in model_artifact["model"]["stumps"]:
            feature = int(stump["feature"])
            values = np.where(
                x[:, feature] <= float(stump["threshold"]),
                float(stump["left"]),
                float(stump["right"]),
            )
            prediction += values
            contributions[:, feature] += values

        local_drivers: list[str] = []
        for row_contributions in contributions:
            order = np.argsort(-np.abs(row_contributions))[:3]
            explanations = []
            for feature_idx in order:
                contribution = float(row_contributions[feature_idx])
                feature = _friendly_feature(feature_names[feature_idx]).capitalize()
                direction = "raises" if contribution >= 0 else "lowers"
                explanations.append(
                    f"{feature} {direction} the contextual benchmark estimate."
                )
            local_drivers.append(" | ".join(explanations))

        output = country_frame[keys].copy()
        output["ai_predicted_log_sold_proxy"] = prediction
        output["ai_local_drivers"] = local_drivers
        outputs.append(output)
    if not outputs:
        return pd.DataFrame(columns=keys + ["ai_predicted_log_sold_proxy", "ai_local_drivers"])
    return pd.concat(outputs, ignore_index=True)
