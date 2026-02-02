"""Background tasks for parsing, synchronising and AI enrichment.

These functions are enqueued by the scheduler and executed by the RQ worker.
Each task should be idempotent and resilient: if a task fails it can be retried.
"""

import os
import json
import time
import logging
from typing import Any

import requests

API_URL = os.getenv("API_URL", "http://api:8000")
GIGACHAT_TOKEN = os.getenv("GIGACHAT_TOKEN", "")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _post_event(event_type: str, source: str, payload: dict[str, Any], company_id: int | None = None) -> None:
    """Helper to post an event to the API."""
    try:
        resp = requests.post(
            f"{API_URL}/events",
            json={
                "type": event_type,
                "source": source,
                "payload": json.dumps(payload, ensure_ascii=False),
                "company_id": company_id,
            },
            timeout=10,
        )
        resp.raise_for_status()
        logger.info("Posted %s event", event_type)
    except Exception as exc:
        logger.error("Failed to post event: %s", exc)


def media_parser() -> str:
    """Dummy media parser. Replace with real implementation.

    Fetches media references for companies and enqueues events.
    """
    # Simulate delay
    time.sleep(2)
    # Example payload
    payload = {
        "title": "Статья о компании",
        "url": "https://example.com/news/123",
        "summary": "Краткое описание новости о компании.",
    }
    _post_event("media", "parser", payload)
    return "media_parser completed"


def tender_parser() -> str:
    """Dummy tender parser. Replace with real implementation."""
    time.sleep(2)
    payload = {
        "tender": "Тендер на закупку оборудования",
        "deadline": "2026-03-01",
        "value": 5000000,
    }
    _post_event("tender", "parser", payload)
    return "tender_parser completed"


def minute_sync() -> str:
    """Synchronise external system into events.

    This function should load only incremental changes since the last run. Here we just emit a dummy event.
    """
    payload = {"message": "incremental sync completed"}
    _post_event("sync", "scheduler", payload)
    return "minute_sync completed"


def gigachat_enrich(text: str) -> str:
    """Call GigaChat AI service to enrich text.

    Currently a stub that simply echoes the text back. In production
    you would call the GigaChat API with the provided token.
    """
    if not GIGACHAT_TOKEN:
        logger.warning("GIGACHAT_TOKEN is not set, skipping AI enrich")
        return text
    # Replace with real call to AI service
    time.sleep(1)
    enriched = f"GigaChat enrichment: {text}"
    return enriched
