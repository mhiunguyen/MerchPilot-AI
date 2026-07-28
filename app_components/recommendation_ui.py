from __future__ import annotations

from collections.abc import Mapping


SCORE_WEIGHTS = {
    "engagement_strength": 0.25,
    "sold_value_strength": 0.20,
    "price_competitiveness": 0.10,
    "promotion_efficiency": 0.15,
    "shop_credibility": 0.10,
    "conversion_gap_opportunity": 0.20,
}

COMPONENT_LABELS = {
    "engagement_strength": "Engagement strength",
    "sold_value_strength": "Sold-value strength",
    "price_competitiveness": "Price competitiveness",
    "promotion_efficiency": "Promotion efficiency",
    "shop_credibility": "Shop credibility",
    "conversion_gap_opportunity": "Conversion-gap opportunity",
}

SCORE_PRESETS = {
    "Balanced product": {
        "engagement_strength": 50,
        "sold_value_strength": 50,
        "price_competitiveness": 50,
        "promotion_efficiency": 50,
        "shop_credibility": 50,
        "conversion_gap_opportunity": 50,
    },
    "Growth opportunity": {
        "engagement_strength": 82,
        "sold_value_strength": 32,
        "price_competitiveness": 62,
        "promotion_efficiency": 58,
        "shop_credibility": 68,
        "conversion_gap_opportunity": 90,
    },
    "Hero protection": {
        "engagement_strength": 92,
        "sold_value_strength": 91,
        "price_competitiveness": 65,
        "promotion_efficiency": 72,
        "shop_credibility": 88,
        "conversion_gap_opportunity": 24,
    },
}

GUIDANCE = {
    "Protect Hero SKU": [
        "Protect availability and preserve listing visibility.",
        "Monitor execution and peer position.",
        "Avoid unnecessary disruption to the current treatment.",
    ],
    "Conversion Opportunity": [
        "Inspect possible conversion friction.",
        "Review price, content, trust, and availability signals.",
        "Consider a controlled test with success metrics defined in advance.",
    ],
    "Promotion Test Candidate": [
        "Consider limited, controlled promotion testing.",
        "Define the target audience, duration, and success metrics before launch.",
    ],
    "Discount Efficiency Review": [
        "Do not automatically increase the discount.",
        "Review targeting, placement, product fit, and historical response.",
    ],
    "Maintain and Monitor": [
        "Continue the current treatment.",
        "Monitor signal changes and peer position.",
    ],
    "Low Priority": [
        "Deprioritize immediate action.",
        "Reassess if engagement or market context changes.",
    ],
}


def calculate_what_if_score(components: Mapping[str, float]) -> float:
    score = 0.0
    for name, weight in SCORE_WEIGHTS.items():
        value = max(0.0, min(100.0, float(components.get(name, 0.0))))
        score += value * weight
    return max(0.0, min(100.0, score))


def score_contributions(components: Mapping[str, float]) -> dict[str, float]:
    return {
        COMPONENT_LABELS[name]: max(0.0, min(100.0, float(components.get(name, 0.0)))) * weight
        for name, weight in SCORE_WEIGHTS.items()
    }


def illustrative_tier(score: float) -> str:
    if score >= 70:
        return "High-priority review"
    if score >= 55:
        return "Focused review"
    if score >= 40:
        return "Monitor"
    return "Lower immediate priority"

