from __future__ import annotations

from typing import Any, Mapping

import pandas as pd


def _percentile(value: Any) -> str:
    if value is None or pd.isna(value):
        return "an unavailable"
    return f"the {float(value):.0%}"


def ai_decision_brief(product: Mapping[str, Any], language: str = "en") -> str:
    """Create a grounded explanation from the cross-validated model benchmark."""
    signal = str(product.get("ai_benchmark_signal", "Benchmark unavailable"))
    confidence = str(product.get("ai_model_confidence", "Unavailable"))
    if language == "vi":
        if signal == "Benchmark unavailable":
            return (
                "Đối chuẩn có AI hỗ trợ không khả dụng cho sản phẩm này vì thiếu biến mục tiêu "
                "của mô hình. Hãy sử dụng điểm cơ hội minh bạch và bằng chứng nhóm tương đồng."
            )
        if signal == "Observed proxy unavailable":
            return (
                "Mô hình có thể ước tính đối chuẩn theo bối cảnh, nhưng thiếu giá trị bán hàng tháng "
                "đại diện nên không thể tính khoảng cách hiệu năng. Hãy sử dụng điểm cơ hội minh bạch "
                "và thu thập kết quả còn thiếu trước khi so sánh."
            )
        engagement_value = product.get("likes_pct_peer")
        price_value = product.get("price_pct_country_category")
        engagement = (
            "không có dữ liệu"
            if engagement_value is None or pd.isna(engagement_value)
            else f"{float(engagement_value):.0%}"
        )
        price = (
            "không có dữ liệu"
            if price_value is None or pd.isna(price_value)
            else f"{float(price_value):.0%}"
        )
        if signal == "Below contextual benchmark":
            core = (
                "Mô hình kiểm định chéo xếp sản phẩm này thấp hơn mức giá trị bán gắn với bối cảnh "
                f"tương đồng. Tương tác ở {engagement} phân vị nhóm và giá ở {price} phân vị nhóm, "
                "vì vậy khoảng cách này là tín hiệu cần xem xét trở ngại chuyển đổi."
            )
        elif signal == "Above contextual benchmark":
            core = (
                "Giá trị bán quan sát được cao hơn đối chuẩn theo bối cảnh của mô hình. Điều này hỗ trợ "
                f"việc bảo vệ cách triển khai hiện tại, đồng thời theo dõi vị trí tương tác {engagement}."
            )
        else:
            core = (
                "Giá trị bán quan sát được gần với đối chuẩn theo bối cảnh của mô hình. Mô hình không "
                "phát hiện khoảng cách hiệu năng lớn, vì vậy điểm minh bạch và bối cảnh kinh doanh nên "
                "dẫn dắt quá trình xem xét."
            )
        if confidence == "Low":
            core += (
                " Độ tin cậy của mô hình Việt Nam thấp, vì vậy tín hiệu này không được ghi đè điểm "
                "minh bạch hoặc phán đoán của con người."
            )
        else:
            core += " Đây là đối chuẩn cắt ngang, không phải dự báo doanh số tương lai."
        return core

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
