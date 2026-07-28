from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import streamlit as st


@dataclass(frozen=True)
class DeliveryResult:
    delivered: bool
    configured: bool
    message: str


def google_sheets_config() -> tuple[str, str]:
    """Return webhook URL and shared token without exposing either in the UI."""
    env_url = os.getenv("MERCHPILOT_GOOGLE_SHEETS_WEBHOOK_URL", "").strip()
    env_token = os.getenv("MERCHPILOT_GOOGLE_SHEETS_WEBHOOK_TOKEN", "").strip()
    if env_url:
        return env_url, env_token
    try:
        section = st.secrets.get("google_sheets", {})
        return str(section.get("webhook_url", "")).strip(), str(
            section.get("webhook_token", "")
        ).strip()
    except Exception:
        return "", ""


def deliver_record(
    record_type: str,
    row: dict[str, Any],
    *,
    webhook_url: str | None = None,
    webhook_token: str | None = None,
    timeout_seconds: float = 10,
) -> DeliveryResult:
    """Send a feedback or decision record to the configured Google Apps Script."""
    if webhook_url is None or webhook_token is None:
        configured_url, configured_token = google_sheets_config()
        webhook_url = configured_url if webhook_url is None else webhook_url
        webhook_token = configured_token if webhook_token is None else webhook_token
    webhook_url = str(webhook_url or "").strip()
    webhook_token = str(webhook_token or "").strip()
    if not webhook_url:
        return DeliveryResult(False, False, "Google Sheets persistence is not configured.")

    payload = json.dumps(
        {
            "record_type": record_type,
            "token": webhook_token,
            "record": row,
        },
        ensure_ascii=False,
        default=str,
    ).encode("utf-8")
    request = Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            body = response.read().decode("utf-8", errors="replace")
            if not 200 <= response.status < 300:
                return DeliveryResult(False, True, f"Google Sheets returned HTTP {response.status}.")
            try:
                parsed = json.loads(body)
            except json.JSONDecodeError:
                parsed = {}
            if parsed and not parsed.get("ok", False):
                return DeliveryResult(
                    False,
                    True,
                    str(parsed.get("error", "Google Sheets rejected the submission.")),
                )
            return DeliveryResult(True, True, "Submission delivered to Team YOUNGHTT.")
    except HTTPError as exc:
        return DeliveryResult(False, True, f"Google Sheets returned HTTP {exc.code}.")
    except (URLError, TimeoutError, OSError) as exc:
        return DeliveryResult(False, True, f"Could not reach Google Sheets: {exc}")
