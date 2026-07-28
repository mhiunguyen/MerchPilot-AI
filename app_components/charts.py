from __future__ import annotations

import pandas as pd
import streamlit as st


MARKET_COLORS = {"Indonesia": "#11b8a5", "Vietnam": "#f28b30"}


def show_image_chart(path, caption: str) -> None:
    st.image(str(path), width="stretch")
    st.caption(caption)


def recommendation_mix(frame: pd.DataFrame) -> pd.DataFrame:
    counts = (
        frame["recommendation_label"]
        .value_counts(dropna=False)
        .rename_axis("Recommendation")
        .reset_index(name="Listings")
    )
    counts["Share"] = counts["Listings"] / max(len(frame), 1)
    return counts


def score_band_summary(frame: pd.DataFrame) -> pd.DataFrame:
    bins = [-0.01, 40, 55, 70, 100]
    labels = ["0–40 · Lower", "40–55 · Monitor", "55–70 · Focused", "70–100 · High"]
    bands = pd.cut(frame["opportunity_score"], bins=bins, labels=labels)
    return (
        bands.value_counts(sort=False)
        .rename_axis("Score band")
        .reset_index(name="Listings")
    )


def contribution_frame(contributions: dict[str, float]) -> pd.DataFrame:
    return pd.DataFrame(
        {"Component": list(contributions.keys()), "Score contribution": list(contributions.values())}
    ).set_index("Component")
